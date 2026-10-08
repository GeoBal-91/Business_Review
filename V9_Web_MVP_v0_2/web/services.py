"""Upload boundaries and process isolation. No scoring or classification logic."""
from datetime import date
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import warnings
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile
from PIL import Image, ImageOps, UnidentifiedImageError
from web.version import PRESENTATION_VERSION

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend' / 'V9_Beta2'
MAX_EXPORT = 20 * 1024 * 1024
MAX_LOGO = 5 * 1024 * 1024


class WebError(ValueError):
    """An actionable message safe to display to the user."""


def validate_workbook(payload):
    if not payload or len(payload) > MAX_EXPORT:
        raise WebError('Upload a non-empty XLSX export up to 20 MB.')
    try:
        with ZipFile(BytesIO(payload)) as archive:
            if sum(i.file_size for i in archive.infolist()) > 150 * 1024 * 1024:
                raise WebError('The expanded workbook is too large. Export a smaller reporting window.')
            if 'xl/workbook.xml' not in archive.namelist():
                raise WebError('This is not an XLSX workbook. Export Excel (.xlsx) from Looker.')
    except BadZipFile as exc:
        raise WebError('The workbook is damaged or is not XLSX. Export it again from Looker.') from exc


def normalize_logo(payload):
    if not payload or len(payload) > MAX_LOGO:
        raise WebError('Upload a PNG or JPEG logo up to 5 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(payload)) as im:
                if im.format not in ('PNG', 'JPEG'):
                    raise WebError('The logo must be a PNG or JPEG image.')
                if im.width * im.height > 16_000_000:
                    raise WebError('The logo is too large. Use an image under 16 megapixels.')
                im.load()
                im = ImageOps.exif_transpose(im).convert('RGBA')
                output = BytesIO()
                im.save(output, format='PNG')
                return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise WebError('The logo cannot be read. Upload a valid PNG or JPEG image.') from exc


def baseline_fingerprint():
    digest = hashlib.sha256()
    for path in sorted(BACKEND.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            digest.update(str(path.relative_to(BACKEND)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def normalize_partner_name(value):
    if not isinstance(value, str) or not value.strip():
        raise WebError('Enter the Partner Name before generating the review.')
    return value.strip()


def input_key(partner, logo, sbu, baseline, partner_name=''):
    digest = hashlib.sha256()
    # Presentation builds invalidate an already-generated session result even
    # when the uploaded data, logo and frozen analytical baseline are identical.
    for value in (partner or b'', logo or b'', sbu.encode(), baseline.encode(),
                  PRESENTATION_VERSION.encode(), partner_name.strip().encode(), date.today().isoformat().encode()):
        digest.update(len(value).to_bytes(8, 'big'))
        digest.update(value)
    return digest.hexdigest()


def invoke(mode, partner=None, logo=None, sbu='', *, partner_name='', timeout=300, temp_parent=None):
    if mode not in {'catalog', 'validate', 'generate'}:
        raise WebError('Unknown review operation.')
    if mode != 'catalog':
        validate_workbook(partner)
    display_name = normalize_partner_name(partner_name) if mode == 'generate' else None
    logo_png = normalize_logo(logo) if mode == 'generate' else None
    with TemporaryDirectory(prefix='v9-web-', dir=temp_parent) as temporary:
        folder = Path(temporary)
        (folder / 'request.json').write_text(json.dumps(dict(mode=mode, sbu=sbu, partner_name=display_name)), encoding='utf-8')
        if partner is not None:
            (folder / 'partner.xlsx').write_bytes(partner)
        if logo_png:
            (folder / 'partner_logo.png').write_bytes(logo_png)
        env = dict(os.environ, MPLBACKEND='Agg', MPLCONFIGDIR=str(folder / 'mpl'),
                   TMPDIR=str(folder), TEMP=str(folder), TMP=str(folder), PYTHONDONTWRITEBYTECODE='1')
        try:
            process = subprocess.run([sys.executable, str(ROOT / 'web' / 'worker.py'), str(folder)],
                                     cwd=folder, env=env, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise WebError('Processing timed out. Try a smaller export and generate again.') from exc
        except OSError as exc:
            raise WebError('The review worker could not start. Check the Python installation.') from exc
        try:
            if process.returncode != 0:
                raise ValueError('Worker failed')
            response = json.loads((folder / 'response.json').read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise WebError('Processing failed. Check your export and Python dependencies, then try again.') from exc
        if mode == 'generate' and response['ok']:
            try:
                response['pptx'] = (folder / 'review.pptx').read_bytes()
                with ZipFile(BytesIO(response['pptx'])) as deck:
                    if 'ppt/presentation.xml' not in deck.namelist() or deck.testzip():
                        raise ValueError('Invalid deck')
                output = BytesIO()
                with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
                    for path in sorted((folder / 'audit').iterdir()):
                        if path.is_file():
                            archive.write(path, path.name)
                response['audit'] = output.getvalue()
            except (OSError, ValueError, BadZipFile) as exc:
                raise WebError('The engine did not produce complete downloads. Please try again.') from exc
        return response  # Only bytes/metadata escape; all request files are removed.
