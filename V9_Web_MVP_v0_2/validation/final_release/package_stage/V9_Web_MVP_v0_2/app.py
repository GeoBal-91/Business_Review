"""Glovo Partner Insights v0.2. UI only; Beta2 remains the analytical source."""
import base64
import os
import re
import tomllib
from pathlib import Path
from html import escape
from urllib.parse import urlparse
import streamlit as st
from web.services import WebError, baseline_fingerprint, input_key, invoke, normalize_logo
from web.components import html, icon, section_heading, notice, journey, review_overview, readiness, validation_intro, format_sbu
from web.version import WEB_VERSION, PRESENTATION_VERSION

ROOT = Path(__file__).parent
st.set_page_config(page_title='Partner Review · Glovo Insights', page_icon='🟡', layout='wide', initial_sidebar_state='expanded')
glopi_pattern = base64.b64encode((ROOT/'web/assets/glopi-silhouettes.svg').read_bytes()).decode()
html('<style>:root{--glopi-pattern:url("data:image/svg+xml;base64,' + glopi_pattern + '");}'
     + (ROOT/'web_style.css').read_text() + '</style>')


def clear_session():
    for key in ('validation', 'validation_key', 'result', 'input_key', 'generation_error', 'selected_sbu', 'partner_name'):
        st.session_state.pop(key, None)
    st.session_state['upload_epoch'] = st.session_state.get('upload_epoch', 0) + 1


def download_name(metadata, suffix, display_name=''):
    name = display_name or metadata.get('partner', '')
    if name in ('', 'Not included in export', 'Multiple partners'):
        name = 'Partner'
    stem = re.sub(r'[^\w-]+', '_', f"{name}_{metadata.get('period', '')}", flags=re.UNICODE).strip('_')[:100]
    return f'{stem}_{suffix}'


with st.sidebar:
    logo_src = base64.b64encode((ROOT/'web/assets/glovo_logo.png').read_bytes()).decode()
    sidebar_glopi_src = base64.b64encode((ROOT/'web/assets/glopi-laptop.png').read_bytes()).decode()
    html(f'<div class="brand"><img src="data:image/png;base64,{logo_src}" alt="Glovo"><span>PARTNER INSIGHTS</span></div>')
    nav_items = [('review-top','Create a review','file','01'),('validation-summary','Data checks','shield','02'),('review-downloads','Your presentation','download','03'),('review-help','Help & guidance','help','04')]
    html('<div class="nav-label">WORKSPACE</div><nav class="side-nav" aria-label="Workspace navigation">'+''.join(f'<a href="#{anchor}" target="_self">{icon(ico)}<span>{label}</span><b>{number}</b></a>' for anchor,label,ico,number in nav_items)+'</nav>')
    html(f'<div class="sidebar-glopi" aria-hidden="true"><img src="data:image/png;base64,{sidebar_glopi_src}" alt=""></div>')
    st.button('Clear uploads and results', on_click=clear_session, width='stretch', icon=':material/restart_alt:', help='Start a fresh review. Uploaded data, logo, selected SBU and results are cleared from this session. Downloaded files stay on your Mac.')
    html(f'<div class="sidebar-footer"><span class="status-dot"></span> Running on your Mac<small>Web v{WEB_VERSION} · Slides {PRESENTATION_VERSION}</small></div>')

html('<div class="topbar"><span>Workspace <b>/</b> <strong>Partner review</strong></span><a href="#review-help" target="_self">'+icon('help')+' How it works</a></div>')
html('<div id="review-top" class="anchor"></div>')
stepper = st.empty()
summary_banner = st.empty()

with st.container(key='workspace_grid'):
    setup, action = st.columns([1.85, 1], gap='large')
    with setup:
        with st.container(border=True, key='prepare_card'):
            html('<div id="prepare-review" class="anchor"></div>')
            section_heading('Prepare your review', 'A partner export, a logo and the right business unit.', '01', 'file')
            st.markdown('##### Partner data')
            st.caption('Open your saved Looker report, enter the partner name, then export Excel.')
            try:
                config_path = ROOT/'web_config.toml'
                config = tomllib.loads(config_path.read_text()) if config_path.exists() else {}
                looker_url = os.environ.get('V9_LOOKER_EXPORT_URL', config.get('looker_export_url', '')).strip()
                if urlparse(looker_url).scheme in ('https', 'http') and urlparse(looker_url).netloc:
                    st.link_button('Open Looker Export ↗', looker_url, help='Opens the saved Looker report in a new tab. Run it for a single partner and download Excel (.xlsx).')
                else:
                    st.caption('The saved Looker link is unavailable. You can still upload an export.')
            except (OSError, ValueError, TypeError):
                st.caption('The Looker link could not be loaded. You can still upload an export.')
            epoch = st.session_state.get('upload_epoch', 0)
            with st.container(key='partner_upload'):
                html('<div class="upload-instruction">Drag your Excel file here, or use Upload.</div>')
                partner_file = st.file_uploader('Upload Partner export', type=['xlsx'], key=f'partner_{epoch}', label_visibility='collapsed', help='One partner, complete months. Excel (.xlsx), up to 20 MB. The first sheet is read.')
            data_feedback = st.empty()
            st.caption('Excel .xlsx · Up to 20 MB · One partner · Complete months')
            st.divider()
            logo_col, sbu_col = st.columns([1, 1], gap='large')
            with logo_col:
                st.markdown('##### Partner logo')
                st.caption('Add their identity to the presentation.')
                with st.container(key='logo_upload'):
                    logo_file = st.file_uploader('Upload Partner logo', type=['png', 'jpg', 'jpeg'], max_upload_size=5, key=f'logo_{epoch}', label_visibility='collapsed', help='Required for generation. PNG or JPEG, up to 5 MB.')
                logo_preview = st.empty()
                logo_feedback = st.empty()
                st.caption('PNG or JPEG · Up to 5 MB')
            with sbu_col:
                partner_name = st.text_input('Partner Name', key='partner_name', placeholder='e.g. PetFood', help='Required. This name appears in the presentation; it does not change your data or analysis.').strip()
                st.markdown('##### Business unit')
                st.caption('Choose the relevant benchmark group.')
                try:
                    baseline = baseline_fingerprint()
                    if st.session_state.get('catalog_key') != baseline:
                        catalog = invoke('catalog', timeout=60)
                        if not catalog['ok']:
                            raise WebError('Business units could not be loaded. Restore the original benchmark and try again.')
                        st.session_state['sbus'] = catalog['sbus']
                        st.session_state['catalog_key'] = baseline
                    sbu = st.selectbox('Select SBU', st.session_state['sbus'], index=None, key='selected_sbu', placeholder='Search business units', format_func=format_sbu, label_visibility='collapsed')
                except (WebError, OSError) as exc:
                    st.error(str(exc))
                    st.button('Generate Review', disabled=True)
                    st.stop()
                sbu_feedback = st.empty()
                st.caption(f"{len(st.session_state['sbus'])} business units available")

partner = partner_file.getvalue() if partner_file is not None else None
logo = logo_file.getvalue() if logo_file is not None else None
run_key = input_key(partner, logo, sbu or '', baseline, partner_name)
validation_key = input_key(partner, None, sbu or '', baseline)
if st.session_state.get('input_key') != run_key:
    for item in ('result', 'generation_error'):
        st.session_state.pop(item, None)
    st.session_state['input_key'] = run_key
if st.session_state.get('validation_key') != validation_key:
    st.session_state.pop('validation', None)
    st.session_state['validation_key'] = validation_key
logo_ok = False
logo_error = ''
if logo is not None:
    try:
        preview = normalize_logo(logo)
        logo_ok = True
        preview_src = base64.b64encode(preview).decode()
        logo_preview.markdown(f'<div class="logo-preview"><img src="data:image/png;base64,{preview_src}" alt="Uploaded partner logo"><span>{icon("check")} Logo ready</span></div>', unsafe_allow_html=True)
    except WebError as exc:
        logo_error = str(exc)
        logo_feedback.error(logo_error)
if sbu:
    sbu_feedback.markdown(f'<div class="sbu-selected">{icon("layers")}<span>{escape(format_sbu(sbu))}</span></div>', unsafe_allow_html=True)

with setup:
    with st.container(border=True, key='validation_card'):
        html('<div id="validation-summary" class="anchor"></div>')
        section_heading('Check the details', 'Your export and benchmark are checked automatically.', '02', 'shield')
        if partner is not None and sbu:
            if 'validation' not in st.session_state:
                with st.spinner('Checking file structure, reporting period and benchmarks…'):
                    try:
                        st.session_state['validation'] = invoke('validate', partner, sbu=sbu, timeout=120)
                    except WebError as exc:
                        st.session_state['validation'] = dict(ok=False, metadata={}, issues=[dict(level='error', message=str(exc))])
            validation = st.session_state['validation']
            metadata = validation.get('metadata', {})
            warnings = [i for i in validation['issues'] if i['level'] == 'warning']
            errors = [i for i in validation['issues'] if i['level'] == 'error']
            if validation['ok']:
                notice('Checks passed · review notes' if warnings else 'Your data checks have passed', f'{len(warnings)} warning'+('s' if len(warnings) != 1 else '')+' to review before presenting.' if warnings else 'Required same-month benchmarks are available.', 'warning' if warnings else 'success')
            else:
                notice('This review needs attention', 'Check the details below. Your uploads are kept here while you resolve the issue.', 'error')
            if metadata:
                review_overview(metadata, sbu)
                if metadata['partner'] == 'Not included in export':
                    notice('Partner name is missing from the export', 'Confirm the file contains one partner. The Partner Name entered above is used in the presentation only.', 'info')
            for issue in errors:
                st.error(issue['message'])
            notes = [i for i in validation['issues'] if i['level'] != 'error']
            if notes:
                with st.expander(f'Validation notes ({len(notes)})', expanded=False):
                    for issue in notes:
                        context = ' · '.join(str(issue.get(k, '')) for k in ('source', 'store_id', 'period') if issue.get(k))
                        message = f"{context}: {issue['message']}" if context else issue['message']
                        (st.warning if issue['level'] == 'warning' else st.info)(message)
            if not validation['ok'] and st.button('Retry validation', icon=':material/refresh:'):
                st.session_state.pop('validation', None)
                st.rerun()
        else:
            validation_intro(bool(partner), bool(sbu))

validation = st.session_state.get('validation', {})
metadata = validation.get('metadata', {})
validated = bool(validation.get('ok'))
errors = [i for i in validation.get('issues', []) if i['level'] == 'error']
ready = bool(validated and logo_ok and partner is not None and sbu and partner_name)
if partner is not None:
    if errors:
        data_feedback.markdown('<a class="field-link attention" href="#validation-summary" target="_self">'+icon('help')+' File uploaded · check the validation issues below '+icon('arrow')+'</a>', unsafe_allow_html=True)
    else:
        data_feedback.markdown('<div class="field-status">'+icon('check')+(' Export validated' if validated else ' File received · select an SBU to validate')+'</div>', unsafe_allow_html=True)

with action:
    with st.container(border=True, key='action_card'):
        html('<div id="review-downloads" class="anchor"></div>')
        has_result = bool(st.session_state.get('result'))
        label = 'Review ready' if has_result else 'Ready to generate' if ready else 'Needs attention' if errors or logo_error else 'Setting up'
        label_class = 'success' if has_result or ready else 'warning' if errors or logo_error else 'neutral'
        html(f'<div class="action-topline"><span>YOUR REVIEW</span><b class="state-badge {label_class}"><i></i>{label}</b></div>')
        if not has_result:
            if not ready:
                next_text, next_anchor = ('Upload your partner export', 'prepare-review') if partner is None else ('Add a valid partner logo', 'prepare-review') if not logo_ok else ('Enter the Partner Name', 'prepare-review') if not partner_name else ('Choose a business unit', 'prepare-review') if not sbu else ('Review the validation issues', 'validation-summary')
                html(f'<a class="next-action" href="#{next_anchor}" target="_self"><span><small>NEXT STEP</small>{next_text}</span>{icon("arrow")}</a>')
        if st.button('Generate Review', type='secondary' if has_result else 'primary', disabled=not ready, width='stretch', icon=':material/auto_awesome:'):
            st.session_state.pop('result', None)
            st.session_state.pop('generation_error', None)
            with st.status('Creating your review…', expanded=True) as processing:
                st.write('Generating the presentation and supporting audit. Keep this page open.')
                try:
                    generated = invoke('generate', partner, logo, sbu, partner_name=partner_name)
                    if generated['ok']:
                        st.session_state['result'] = generated
                        processing.update(label='Your review is ready', state='complete')
                    else:
                        st.session_state['validation'] = generated
                        st.session_state['generation_error'] = '\n'.join(i['message'] for i in generated['issues'] if i['level'] == 'error')
                        processing.update(label='Review needs attention', state='error')
                except WebError as exc:
                    st.session_state['generation_error'] = str(exc)
                    processing.update(label='Could not finish the review', state='error')
            st.rerun()
        if st.session_state.get('generation_error'):
            st.error(st.session_state['generation_error'])
        if st.session_state.get('result'):
            result = st.session_state['result']
            notice('Ready for your next conversation', 'Download both files before starting a new review.', 'success')
            result_metadata = result.get('metadata', {})
            st.download_button('Download PPTX', result['pptx'], download_name(result_metadata, 'Review.pptx', result['presentation_display_name']), 'application/vnd.openxmlformats-officedocument.presentationml.presentation', on_click='ignore', width='stretch', icon=':material/slideshow:')
            st.caption(f"PowerPoint presentation · {len(result['pptx']) / 1048576:.1f} MB")
            st.download_button('Download Audit ZIP', result['audit'], download_name(result_metadata, 'Audit.zip'), 'application/zip', on_click='ignore', width='stretch', icon=':material/folder_zip:')
            st.caption(f"Supporting data & rule traces · {len(result['audit']) / 1048576:.1f} MB")
        else:
            readiness([('Partner export', bool(partner)), ('Partner logo', logo_ok), ('Partner Name', bool(partner_name)), ('Business unit', bool(sbu)), ('Data & benchmark checks', validated)])
            html('<div class="action-footnote">'+icon('shield')+' Your files are processed locally.</div>')
    with st.expander('What’s inside the review?', expanded=False):
        st.markdown('- Partner performance & conversion evolution\n- Performance analysis against the SBU\n- Store-level diagnostics\n- Priority opportunities and actions\n- Action plan\n- Supporting audit files')
    html('<div class="aside-signoff"><span>Made for local impact.</span><i></i></div>')

with setup:
    with st.container(border=True, key='help_card'):
        html('<div id="review-help" class="anchor"></div>')
        html('<div class="help-heading">'+icon('help')+'<div><h3>A little help, when you need it.</h3><p>From the first export to your next presentation.</p></div></div>')
        with st.expander('How do I prepare a Looker export?'):
            st.write('Open Looker Export, enter the partner name and run the saved report. Download Excel (.xlsx) for one partner and complete months. Upload it here and choose the matching SBU. CSV and legacy .xls are not supported in this version.')
        with st.expander('Why is generation unavailable?'):
            st.write('The checklist shows what is missing. Add a partner export, a valid logo, a Partner Name and an SBU. The export must pass data checks, and the required benchmarks must exist for the same reporting month. Open Validation notes for details. Missing benchmarks need a corrected benchmark source; uploading the same partner file again will not fill them.')
        with st.expander('What happens to my files?'):
            st.write('Processing happens locally on your Mac. Temporary processing files are removed after each operation. Uploads and results stay in this session until cleared or replaced. Download your presentation and audit before starting another review. Clear uploads and results also resets the Partner Name and selected SBU. Downloaded files stay on your Mac.')

has_result = bool(st.session_state.get('result'))
stepper.markdown(journey(bool(partner) and logo_ok and bool(partner_name) and bool(sbu), validated, has_result, bool(errors or logo_error)), unsafe_allow_html=True)
if errors or logo_error:
    summary_banner.markdown('<a class="error-summary" href="#'+('prepare-review' if logo_error else 'validation-summary')+'" target="_self">'+icon('help')+'<span><strong>Something needs your attention.</strong> '+('Check the partner logo.' if logo_error else 'Review the data checks before generating.')+'</span>'+icon('arrow')+'</a>', unsafe_allow_html=True)
html('<footer class="page-footer"><span>Glovo <b>Partner Insights</b></span><span>Local impact. Global ambition.</span></footer>')
