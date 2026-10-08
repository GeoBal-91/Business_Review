"""Small, escaped presentation components. No analytical calculations."""
from html import escape
import streamlit as st

PATHS = {
    'file': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    'image': '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8" cy="8" r="1"/><path d="m21 15-5-5L5 21"/>',
    'layers': '<path d="m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 17l10 5 10-5"/>',
    'check': '<path d="m5 12 4 4L19 6"/>',
    'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    'download': '<path d="M12 3v12m-5-5 5 5 5-5M4 16v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4"/>',
    'shield': '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
    'help': '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 4m0 3h.01"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
}

def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{PATHS[name]}</svg>'


def html(value):
    st.markdown(value, unsafe_allow_html=True)

def format_sbu(value):
    """Display text only. The selection passed to Beta2 is unchanged."""
    if not value:
        return ''
    return ' '.join(word if word in ('OTC', 'RX', 'DIY') else word.capitalize() for word in value.split('_'))


def section_heading(title, subtitle, number, glyph):
    html(f'<div class="section-heading"><span class="section-number">{number}</span><div><h2>{escape(title)}</h2><p>{escape(subtitle)}</p></div><span class="section-glyph">{icon(glyph)}</span></div>')


def notice(title, text, kind='info'):
    html(f'<div class="notice {kind}" role="{"alert" if kind=="error" else "status"}"><span>{icon("check" if kind=="success" else "help")}</span><div><strong>{escape(title)}</strong><p>{escape(text)}</p></div></div>')


def journey(prepared, validated, generated, blocked):
    stages = [('Prepare', 'Upload files & select SBU', 'prepare-review'), ('Validate', 'Check data & benchmark', 'validation-summary'), ('Generate & download', 'Your presentation + audit', 'review-downloads')]
    completed = [prepared, validated, generated]
    active = 0 if not prepared else 1 if not validated else 2
    entries=[]
    for i, (name,detail,anchor) in enumerate(stages):
        state='done' if completed[i] else 'current' if i==active else 'pending'
        if blocked and i==active:
            state='attention'
        entries.append(f'<a class="journey-step {state}" href="#{anchor}" target="_self" {"aria-current=step" if i==active else ""}><b>{icon("check") if completed[i] else str(i+1).zfill(2)}</b><span><strong>{name}</strong><small>{detail}</small></span>{icon("arrow") if i<2 else ""}</a>')
    return '<nav class="journey" aria-label="Review steps">'+''.join(entries)+'</nav>'


def review_overview(metadata, sbu):
    name = metadata['partner']
    html('<div class="validated-overview"><div class="overview-label">DETECTED FROM YOUR EXPORT</div><h3>'+escape(str(name))+'</h3><div class="overview-grid">'+''.join(f'<div><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>' for label,value in [('Reporting period',metadata['period']),('Stores detected',metadata['store_count']),('Selected SBU',format_sbu(sbu)),('Benchmark period',metadata.get('benchmark_period') or 'Unavailable')])+'</div><div class="coverage-note">'+icon('help')+f'{metadata["current_store_count"]} stores have rows in the latest period.</div></div>')


def readiness(items):
    done=sum(bool(v) for _,v in items)
    html(f'<div class="readiness-title"><strong>Before you generate</strong><span>{done} of {len(items)} ready</span></div><div class="readiness">'+''.join(f'<div class="{"complete" if ok else "incomplete"}"><b>{icon("check") if ok else ""}</b><span>{escape(label)}</span><small>{"Ready" if ok else "Needed"}</small></div>' for label,ok in items)+'</div>')


def validation_intro(has_file, has_sbu):
    title = 'Choose a business unit to check your export.' if has_file else 'Your data checks will appear here.'
    text = 'We’ll use its same-month benchmarks to validate this review.' if has_file else 'Add a partner export and select an SBU. We’ll take care of the checks.'
    html(f'<div class="validation-empty"><span class="empty-icon">{icon("shield")}</span><div><h3>{title}</h3><p>{text}</p></div></div><div class="check-tags"><span>{icon("file")} File structure</span><span>{icon("clock")} Reporting period</span><span>{icon("layers")} Benchmark coverage</span></div>')
