"""One isolated Beta2 invocation. Never imported by the Streamlit process."""
import contextlib
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend' / 'V9_Beta2'))
from config import Settings
from data_pipeline import DataValidationError, load_data, present
from main import clean


def inspect_data(settings):
    data = load_data(settings)  # Schema, grain, rates, counts, periods: Beta2 only.
    issues = [asdict(i) for i in data.issues]
    if data.benchmark_row is None:
        issues.append(dict(level='error', code='web_benchmark_required', source='SBU',
                           message='A same-month benchmark is required to generate a web review.'))
    else:
        missing = [k for k in ('% CVR', '% PNA Orders', '% Cancels DTP')
                   if not present(data.benchmark_row.get(k))]
        if missing:
            issues.append(dict(level='error', code='web_benchmark_incomplete', source='SBU',
                               message='Benchmark metrics unavailable: ' + ', '.join(missing)))
    frame = data.partner_raw
    # Display metadata only; these values never feed scoring/classification.
    name = 'Not included in export'
    for column in ('Partner Name', 'Partner', 'Store Partner Name', 'Store Name'):
        if column not in frame:
            continue
        names = sorted({str(v).strip() for v in frame[column].dropna() if str(v).strip()})
        if len(names) == 1:
            name = names[0]
            break
        if len(names) > 1 and column != 'Store Name':
            issues.append(dict(level='error', code='web_multiple_partners', source='partner',
                               message=f'{column} contains multiple partners. Export one partner at a time.'))
            name = 'Multiple partners'
            break
    period = data.reporting_period
    metadata = dict(partner=name, period=period.strftime('%B %Y'),
                    store_count=int(frame['Store ID'].nunique()),
                    current_store_count=int(frame.loc[frame.Period == period, 'Store ID'].nunique()),
                    benchmark_period=data.benchmark_period.strftime('%B %Y') if data.benchmark_period is not None else None)
    return dict(ok=not any(i['level'] == 'error' for i in issues), issues=issues, metadata=metadata)


def execute(request, folder):
    if request['mode'] == 'catalog':
        from sbu_catalog import supported_sbus
        return dict(ok=True, sbus=list(supported_sbus()))
    display_name = None
    if request['mode'] == 'generate':
        sys.path.insert(1, str(ROOT))
        from web.services import normalize_partner_name, WebError
        try:
            display_name = normalize_partner_name(request.get('partner_name'))
        except WebError as exc:
            return dict(ok=False, metadata={}, issues=[dict(level='error', code='web_partner_name_required', source='web', message=str(exc))])
    settings = Settings(input_file=folder / 'partner.xlsx', partner_sbu=request['sbu'],
                        output_file=folder / 'review.pptx')
    response = inspect_data(settings)
    if request['mode'] == 'validate' or not response['ok']:
        return response
    from analysis import run_analysis
    from business_classification import classify
    from triage_exports import export_triage
    result = run_analysis(settings)
    triage = classify(result)
    export_triage(triage, folder / 'audit')
    # Rendering configuration only, in this private child process. Source files untouched.
    import theme
    theme.PARTNER_LOGO_FILE = folder / 'partner_logo.png'
    # Web presentation changes sit outside the byte-for-byte frozen backend.
    sys.path.insert(1, str(ROOT))
    from web.presentation_update import render, VERSION as presentation_version
    render(triage, settings.output_file, partner_name=display_name)
    provenance = dict(web_version='0.1', backend='V9_Beta2', presentation_version=presentation_version,
                      logo_sha256=hashlib.sha256(theme.PARTNER_LOGO_FILE.read_bytes()).hexdigest(),
                      metadata=response['metadata'], validation=response['issues'])
    (folder / 'audit' / 'web_run.json').write_text(json.dumps(clean(provenance), indent=2), encoding='utf-8')
    response['presentation_display_name'] = display_name
    return response


def main():
    folder = Path(sys.argv[1]).resolve()
    try:
        with (folder / 'worker.log').open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            try:
                response = execute(json.loads((folder / 'request.json').read_text()), folder)
            except DataValidationError as exc:
                response = dict(ok=False, issues=[asdict(i) for i in exc.issues], metadata={})
            except Exception:
                traceback.print_exc()
                response = dict(ok=False, issues=[dict(level='error', code='engine_failure', source='engine',
                    message='The review engine could not process this file. Check the export and try again.')], metadata={})
        (folder / 'response.json').write_text(json.dumps(clean(response), ensure_ascii=False, allow_nan=False), encoding='utf-8')
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
