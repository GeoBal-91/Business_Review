"""Beta 1.0 presentation views. Read AnalysisResult; never rescore or rerank it."""
import textwrap
from pptx.dml.color import RGBColor
from diagnostics import box, BORDER, AMBER
from data_pipeline import G, U
from formatting import format_currency, format_percent, format_score
from ppt_core import add_title, add_text, add_footer, add_picture_contain
from presentation_hardening import recommendation_pages, action_focus, _next_review
from theme import ASSETS_DIR, GREEN, GREY, WHITE, DARK

VERSION = 'V9_Beta2'
METHOD_TITLE = 'How We Prioritize Opportunities'
ACTION_TITLE = 'Priority Opportunities & Actions'
CREAM = RGBColor(255, 251, 237)


def plural(count, noun='store'):
    return f'{count} {noun}' + ('' if count == 1 else 's')


def page(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(slide, title, subtitle)
    add_footer(slide)
    return slide


def build_methodology(prs, result):
    slide = page(prs, METHOD_TITLE, f"{result.summary['reporting_period']} · Higher Priority = stronger case for action")
    cards = [
        ('SEVERITY — 0–100', 'How large is the KPI problem?', 'sbu_pharmacy_otc.png',
         'Compared with the relevant SBU benchmark or operating target.\n\n'
         'Evidence volume and confidence are considered. Larger reliable negative gaps create higher Severity.\n\n'
         'Dominant-KPI protection keeps a major problem from being hidden by healthy KPIs.'),
        ('IMPACT — 0–100', 'How much business exposure\nsits behind the problem?', 'storeLocationPin.png',
         'Order-related exposure behind the KPI gap. Higher-volume problems generally create higher Impact.\n\n'
         'Not euros. Not guaranteed recovered orders. Not a financial forecast.'),
        ('PRIORITY — 0–100', 'Where should we act first?', 'goldStarCelebration.png',
         'Metric Priority =\nKPI Severity × KPI Impact / 100\n\n'
         'Store Priority combines eligible KPI-level priorities, with dominant-KPI protection so one major issue cannot be diluted.'),
    ]
    if result.settings.priority_model == 'simple_product':
        cards[2] = (cards[2][0], cards[2][1], cards[2][2],
                    'EXPERIMENTAL / CHALLENGER MODEL\n\nStore Severity × Store Impact / 100\n\n'
                    'Research comparison only. The production model combines paired KPI-level priorities with dominant-KPI protection.')
    for i, (title, question, icon, body) in enumerate(cards):
        x = .65 + i * 4.08
        box(slide, x, 1.52, 3.86, 3.28, CREAM if i == 2 else WHITE, BORDER)
        add_picture_contain(slide, ASSETS_DIR / icon, x + .18, 1.68, .47, .47)
        add_text(slide, title, x + .76, 1.77, 2.92, .3, size=13, bold=True, color=GREEN)
        add_text(slide, question, x + .20, 2.28, 3.46, .54, size=13, bold=True)
        add_text(slide, body, x + .20, 2.99, 3.46, 1.63, size=11)
    box(slide, .65, 4.97, 5.95, 1.05, WHITE, BORDER)
    add_text(slide, 'PRIMARY ACTION KPI', .85, 5.12, 5.53, .24, size=12, bold=True, color=GREEN)
    add_text(slide, 'The KPI with the strongest paired business case for action at that store.',
             .85, 5.51, 5.53, .37, size=12)
    box(slide, 6.81, 4.97, 6.00, 1.05, AMBER)
    threshold = f'{result.settings.min_priority:.1f}'
    add_text(slide, f'CURRENT BETA THRESHOLD · Priority ≥ {threshold}', 7.01, 5.12, 5.58, .24, size=12, bold=True)
    add_text(slide, f'The {threshold} threshold is provisional and will be calibrated during Beta validation.',
             7.01, 5.51, 5.58, .37, size=11.5)
    add_text(slide, 'Assessed, eligible stores meeting the threshold enter Priority Opportunities & Actions (six by default).',
             .67, 6.18, 12.1, .26, size=10.5, color=GREY)
    uptime = 'Uptime: 95% target; restoration exposure uses healthy history where available.'
    if not result.settings.include_uptime:
        uptime += ' FLOWERS: hygiene only; excluded from business Priority.'
    notes = [
        'Missing evidence → incomplete assessment, not zero. Critical observations are reviewed separately from business Priority.',
        uptime,
        'Exposure components may overlap; headline exposure uses the largest. An opportunity signal, not a recovery promise.',
        f"Benchmark: {result.summary['benchmark_period'] or 'Unavailable'}. SBU peer composition is not available.",
    ]
    for i, text in enumerate(notes):
        add_text(slide, text, .67 + (i % 2) * 6.16, 6.53 + (i // 2) * .39,
                 5.91, .34, size=9.5, color=GREY)
    return slide


def overall_action_focus(result):
    """Summarize the full selected set on every page, using the existing helper."""
    return action_focus(result, result.actions)


def build_opportunities(prs, result):
    actions, settings = result.actions, result.settings
    pages = recommendation_pages(actions)
    ranks = dict(zip(result.opportunities['Store ID'], result.opportunities['Rank']))
    focus = overall_action_focus(result)
    for page_number, displayed in enumerate(pages, 1):
        title = ACTION_TITLE + (f' · {page_number}/{len(pages)}' if len(pages) > 1 else '')
        slide = page(prs, title, f"{result.summary['reporting_period']} · Higher Priority = stronger case for action · Threshold {settings.min_priority:.1f} is provisional")
        box(slide, 9.48, 1.55, 3.19, 5.36, AMBER)
        if not displayed:
            box(slide, .67, 1.55, 8.55, 5.36, WHITE, BORDER)
            add_text(slide, 'No material business opportunities\nat or above the current threshold.',
                     1.03, 2.36, 7.75, 1.32, size=23, bold=True)
            add_text(slide, 'Review operational/data observations separately.', 1.03, 4.08, 7.75, .8, size=16, color=GREY)
            add_text(slide, f'Priority ≥ {settings.min_priority:.1f} remains provisional; calibration follows Beta validation.',
                     1.03, 5.81, 7.75, .55, size=11, color=GREY)
            _next_review(slide, 2.04)
            continue
        compact = len(displayed) == 4
        for i, action in enumerate(displayed):
            if len(displayed) <= 2:
                single = len(displayed) == 1
                y = 1.55 + i * 2.75
                box(slide, .67, y, 8.55, 5.36 if single else 2.60, RGBColor(247, 249, 249), BORDER)
                shape = add_text(slide, f"#{ranks[action['Store ID']]} · {action['Store']}",
                                 1.00, y + .22, 7.88, .63 if single else .39, size=18 if single else 14,
                                 bold=True, color=GREEN)
                shape.name = 'Opportunity store: ' + str(action['Store ID'])
                add_text(slide, f"Priority {format_score(action['Priority'], settings.min_priority)} · {action['Metric']}",
                         1.00, y + (.99 if single else .70), 7.88, .45 if single else .28,
                         size=23 if single else 14, bold=True)
                add_text(slide, action['Issue'], 1.00, y + (1.64 if single else 1.10), 7.88, .39 if single else .27,
                         size=16 if single else 12, color=GREY)
                if single:
                    add_text(slide, 'Recommended Action', 1.00, y + 2.48, 7.88, .26, size=11, color=GREY)
                    add_text(slide, action['Action'], 1.00, y + 2.97, 7.88, .82, size=18, bold=True)
                    add_text(slide, 'Intended effect', 1.00, y + 4.04, 7.88, .26, size=11, color=GREY)
                    add_text(slide, action['Intended Effect'], 1.00, y + 4.49, 7.88, .53, size=15)
                else:
                    add_text(slide, action['Action'], 1.00, y + 1.54, 7.88, .45, size=13, bold=True)
                    add_text(slide, 'Intended effect: ' + action['Intended Effect'],
                             1.00, y + 2.14, 7.88, .30, size=11)
                continue
            y = 1.55 + i * (1.34 if compact else 1.79)
            box(slide, .67, y, 8.55, 1.27 if compact else 1.70,
                RGBColor(247, 249, 249) if i % 2 == 0 else WHITE, BORDER)
            header = f"#{ranks[action['Store ID']]} · {action['Store']}"
            shape = add_text(slide, header, .90, y + .08, 8.08, .31 if compact else .40,
                             size=12 if compact else 13, bold=True, color=GREEN)
            shape.name = 'Opportunity store: ' + str(action['Store ID'])
            label = f"Priority {format_score(action['Priority'], settings.min_priority)} · {action['Metric']}"
            add_text(slide, label, .90, y + (.36 if compact else .50), 8.08, .23,
                     size=11 if compact else 12, bold=True)
            add_text(slide, action['Issue'], .90, y + (.60 if compact else .81), 8.08, .23,
                     size=10 if compact else 11, color=GREY)
            add_text(slide, action['Action'], .90, y + (.84 if compact else 1.10), 8.08, .22 if compact else .29,
                     size=11 if compact else 12, bold=True)
            add_text(slide, 'Intended effect: ' + action['Intended Effect'], .90,
                     y + (1.07 if compact else 1.45), 8.08, .17 if compact else .23,
                     size=9 if compact else 10)
        add_text(slide, 'OVERALL ACTION FOCUS', 9.71, 1.78, 2.77, .32, size=13, bold=True)
        add_text(slide, 'Full selected opportunity set', 9.71, 2.15, 2.77, .24, size=9.5, color=GREY)
        labels = [('Primary Action KPI', focus['primary_kpi']),
                  ('Stores Requiring Action', plural(focus['store_count'])),
                  ('Priority Range', 'Highest ' + format_score(focus['highest_priority'], settings.min_priority)
                   + ' · Lowest ' + format_score(focus['lowest_priority'], settings.min_priority)),
                  ('Critical / Review Items', plural(focus['review_count'], 'item')
                   + (' for this store' if focus['store_count'] == 1 else ' for these stores'))]
        for i, (label, value) in enumerate(labels):
            y = 2.52 + i * .68
            add_text(slide, label, 9.71, y, 2.77, .22, size=10, color=GREY)
            add_text(slide, value, 9.71, y + .27, 2.77, .30, size=16 if i < 2 else 11, bold=True, color=GREEN if i == 0 else DARK)
        add_text(slide, 'Separate from business Priority', 9.71, 5.22, 2.77, .27, size=9.5, color=GREY)
        _next_review(slide, 5.65)
    return pages


def overview_rows(result):
    """Appendix display order only. All known stores retained without merging."""
    rows = result.stores.copy(deep=True)
    rows['_display_group'] = [0 if bool(r['Eligible Opportunity']) else 1 if r['Store Status'] == 'Active' else 2
                              for _, r in rows.iterrows()]
    return rows.sort_values(['_display_group', 'Opportunity Score', 'Store ID'],
                            ascending=[True, False, True], na_position='last', kind='mergesort').drop(columns='_display_group')


def overview_status(row):
    return row['Operational Status'] if row['Store Status'] == 'Active' else row['Store Status']


def overview_cells(row, threshold):
    return [row['Store Address Address'], overview_status(row), format_currency(row[G]),
            format_percent(row['% CVR']), format_percent(row['% PNA Orders']),
            format_percent(row['% Cancels DTP']), format_percent(row[U]),
            format_score(row['Opportunity Score'], threshold)]


def overview_pages(result):
    """At most 12 rows; long names use more space, never truncate identities."""
    if len(result.stores) < 5:
        return []
    pages, current, used = [], [], 0.0
    for _, row in overview_rows(result).iterrows():
        cells = overview_cells(row, result.settings.min_priority)
        lines = max(len(textwrap.wrap(str(cells[0]), 44)) or 1,
                    len(textwrap.wrap(str(cells[1]), 19)) or 1)
        height = max(.385, .17 * lines + .09)
        if current and (len(current) >= 12 or used + height > 4.84):
            pages.append(current); current, used = [], 0.0
        current.append((row, cells, height)); used += height
    if current:
        pages.append(current)
    return pages


def build_overview(prs, result):
    pages = overview_pages(result)
    widths = [3.62, 1.70, 1.32, 1.06, 1.06, 1.06, 1.06, 1.21]
    for number, entries in enumerate(pages, 1):
        title = 'Store Overview' + (f' · {number}/{len(pages)}' if len(pages) > 1 else '')
        slide = page(prs, title, f"{result.summary['reporting_period']} · {plural(len(result.stores))} known · Current reporting-period values")
        box(slide, .65, 1.57, sum(widths), .39, CREAM)
        x = .65
        for heading, width in zip(['Store', 'Status', 'GMV', 'CVR', 'PNA', 'Cancels', 'Uptime', 'Priority'], widths):
            add_text(slide, heading, x + .09, 1.68, width - .16, .22, size=10.5, bold=True, color=GREEN)
            x += width
        y = 2.03
        for i, (row, cells, height) in enumerate(entries):
            box(slide, .65, y, sum(widths), height - .025, WHITE if i % 2 else RGBColor(247, 249, 249))
            x = .65
            for j, (value, width) in enumerate(zip(cells, widths)):
                shape = add_text(slide, value, x + .09, y + .06, width - .16, height - .08,
                                 size=10.5, bold=j == 7, color=GREEN if j == 0 else DARK)
                shape.name = ('Overview store: ' if j == 0 else f'Overview column {j}: ') + str(row['Store ID'])
                x += width
            y += height
        add_text(slide, 'Select a store to open its diagnostics. Status uses existing operational / lifecycle classifications.',
                 .67, 7.01, 12.08, .23, size=9, color=GREY)
        if not result.settings.include_uptime:
            add_text(slide, 'FLOWERS uptime: hygiene only — excluded from business Priority.', .67, 6.74, 12.08, .20, size=9, color=GREY)
    return pages


def link_overview(prs, result, diagnostic_slides):
    targets = dict(zip(result.stores.sort_values('Store ID')['Store ID'].astype(str), diagnostic_slides))
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.name.startswith('Overview store: '):
                shape.click_action.target_slide = targets[shape.name.split(': ', 1)[1]]
