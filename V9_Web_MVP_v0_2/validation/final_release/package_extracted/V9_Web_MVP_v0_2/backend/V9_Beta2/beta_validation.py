"""Read-only Beta research exports from AnalysisResult, separate from scoring."""
from pathlib import Path
import json
import pandas as pd
from data_pipeline import G, D, N, T, U

STORE_MANUAL_COLUMNS = [
    'AM_Should_Be_Priority', 'AM_Rank', 'AM_Main_Action_KPI_Agree',
    'AM_Action_Relevance_1_5', 'AM_Important_Opportunity_Missed',
    'AM_Should_Not_Be_Pitched', 'AM_Comment',
]
PARTNER_MANUAL_COLUMNS = [
    'AM Overall Trust Score 1–5', 'Top Opportunity Alignment', 'Main Action Alignment',
    'False Positive Count', 'False Negative Count', 'Action Focus Useful Yes/No',
    'Appendix Navigation Friction 1–5', 'Partner-facing Narrative Logical Yes/Partly/No', 'Notes',
]


def store_frame(result):
    """Keep every known Store ID, all precision/missingness, no AM judgments."""
    rows = []
    actions = {a['Store ID']: a for a in result.actions}
    ranks = dict(zip(result.opportunities['Store ID'], result.opportunities['Rank']))
    fields = {
        'Store ID': 'Store ID', 'Store': 'Store Address Address',
        'Store Status': 'Store Status', 'Operational Status': 'Operational Status',
        'GMV': G, 'Delivered Orders': D, 'Sessions': N, 'Order Attempts': T,
        'CVR': '% CVR', 'PNA': '% PNA Orders', 'Cancels': '% Cancels DTP', 'Uptime': U,
        'Severity': 'Performance Severity Score', 'Impact': 'Business Impact Score',
        'Priority': 'Opportunity Score', 'Eligible Opportunity': 'Eligible Opportunity',
        'Main Action KPI': 'Main Driver', 'Critical Flags': 'Critical Flags',
        'Scoring Status': 'Scoring Status', 'AOV': '€ AOV Derived',
        'Data Quality': 'Data Quality', 'Last Observed Period': 'Last Observed Period',
        'Severity Driver': 'Severity Driver', 'Impact Source': 'Impact Source',
        'Paired Priority': 'Paired Priority', 'Simple Product Priority': 'Simple Product Priority',
        'Known Priority': 'Known Priority', 'Modeled Exposure Units': 'Modeled Exposure Units',
        'Metric Coverage': 'Metric Coverage', 'Scoring Scope': 'Scoring Scope',
    }
    for _, source in result.stores.iterrows():
        sid = source['Store ID']; selected = actions.get(sid)
        record = {'Reporting Period': result.summary['reporting_period'], 'SBU': result.settings.partner_sbu}
        record.update({label: source.get(key) for label, key in fields.items()})
        record.update({'Opportunity Rank': ranks.get(sid), 'Displayed Opportunity': sid in ranks,
                       'Recommended Action': selected['Action'] if selected else source['Recommended Focus'],
                       'Evidence': selected['Issue'] if selected else source['Main Issue'],
                       'Intended Effect': selected['Intended Effect'] if selected else '',
                       'Benchmark Period': result.summary['benchmark_period'],
                       'Priority Threshold': result.settings.min_priority,
                       'Threshold Status': result.summary['threshold_status']})
        for name in source.index:
            if any(name.startswith(metric + ' ') for metric in ['CVR', 'PNA', 'Cancels', 'Uptime']):
                record.setdefault(name, source[name])
        record.update({name: '' for name in STORE_MANUAL_COLUMNS})
        rows.append(record)
    return pd.DataFrame(rows)


def partner_frame(result):
    row = {'Partner / Identifier': '', 'SBU': result.settings.partner_sbu,
           'Reporting Period': result.summary['reporting_period']}
    row.update({name: '' for name in PARTNER_MANUAL_COLUMNS})
    return pd.DataFrame([row])


def validation_schema():
    return {
        'release': 'V9_Beta2', 'purpose': 'Manual Beta research only; no automatic calibration',
        'missing_values': 'Blank analytical cells mean unavailable, not zero. Rates are fractions; scores are 0–100 methodology scores, not percentages.',
        'opportunity_rank': 'Existing displayed AnalysisResult opportunity rank only; blank for unselected stores, including eligible stores beyond the executive limit.',
        'recommended_action': 'Selected action text where displayed, otherwise existing store Recommended Focus; incomplete leading issues are diagnostic only.',
        'store_manual_expected_values': {
            'AM_Should_Be_Priority': 'Yes / Partly / No', 'AM_Rank': 'Positive integer; rank among all known stores; blank if not ranked',
            'AM_Main_Action_KPI_Agree': 'Yes / Partly / No', 'AM_Action_Relevance_1_5': '1–5; 1 not relevant, 5 highly relevant',
            'AM_Important_Opportunity_Missed': 'Yes / No', 'AM_Should_Not_Be_Pitched': 'Yes / No', 'AM_Comment': 'Free text',
        },
        'partner_manual_expected_values': {
            'AM Overall Trust Score 1–5': '1–5; 1 low trust, 5 high trust',
            'Top Opportunity Alignment': 'Yes / Partly / No', 'Main Action Alignment': 'Yes / Partly / No',
            'False Positive Count': 'Nonnegative integer, AM-assessed', 'False Negative Count': 'Nonnegative integer, AM-assessed',
            'Action Focus Useful Yes/No': 'Yes / No', 'Appendix Navigation Friction 1–5': '1–5; 1 easy, 5 high friction',
            'Partner-facing Narrative Logical Yes/Partly/No': 'Yes / Partly / No', 'Notes': 'Free text',
        },
        'research_notes': [
            'All AM fields start empty. Save reviewed copies separately before regenerating a run.',
            'Review false positives, false negatives and scores around 3–7 manually; do not recalibrate automatically.',
            'Compare by SBU, AOV and volume; the 5.0 threshold and FLOWERS uptime exclusion remain provisional validation questions, not model changes.',
            'Use stable Store IDs. Similar names are never automatically merged.',
        ],
    }


def export_validation(result, folder):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    for name, frame in [('Beta_Validation_Stores.csv', store_frame(result)),
                        ('Beta_Validation_Partner.csv', partner_frame(result))]:
        frame.to_csv(folder / name, index=False, float_format='%.17g')
    (folder / 'Beta_Validation_Schema.json').write_text(
        json.dumps(validation_schema(), indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    return folder
