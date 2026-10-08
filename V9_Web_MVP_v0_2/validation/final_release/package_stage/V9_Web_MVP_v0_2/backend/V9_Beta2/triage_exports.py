"""Additive, full-precision V2.1 exports; original Beta exports stay untouched."""
from pathlib import Path
import json
import pandas as pd
from main import clean, export_analysis
from beta_validation import store_frame


def write_json(path, value):
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def csv_frame(frame):
    frame = frame.copy(deep=True)
    for name in frame:
        frame[name] = frame[name].map(lambda x: json.dumps(clean(x), ensure_ascii=False, separators=(',', ':')) if isinstance(x, (list, dict, tuple)) else x)
    return frame


def validation_frame(triage):
    base = store_frame(triage.analysis)
    fields = ['Store ID'] + [n for n in triage.stores if n not in triage.analysis.stores]
    out = base.merge(triage.stores[fields], on='Store ID', how='left', validate='one_to_one', sort=False)
    for field in ['AM_Business_Classification_Agree', 'AM_Action_Reason_Agree',
                  'AM_Operational_Driver_Agree', 'AM_Recovery_Context_Comment']:
        out[field] = ''
    return out


def export_triage(triage, folder, include_beta=True):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if include_beta:
        export_analysis(triage.analysis, folder)
    frames = [('Business_Classification', triage.stores),
              ('Business_Actions', pd.DataFrame(triage.actions, columns=[
                  'Store ID', 'Store', 'Metric', 'Issue', 'Action', 'Intended Effect', 'Priority', 'Metric Priority',
                  'Exposure', 'Owner', 'Deadline', 'Triage Rank', 'Business Classification', 'Action Reason',
                  'Primary Action KPI', 'Likely Operational Driver', 'Low Scale Flag', 'Ultra Low Scale Flag', 'Human Review Required'])),
              ('Beta_Validation_Stores_V2_1', validation_frame(triage))]
    for name, frame in frames:
        csv_frame(frame).to_csv(folder / (name + '.csv'), index=False, float_format='%.17g')
    write_json(folder / 'Business_Classification.json', triage.stores.to_dict('records'))
    write_json(folder / 'Classification_Rule_Trace.json', triage.traces)
    write_json(folder / 'Classification_Summary.json', triage.summary)
    write_json(folder / 'Classification_Schema.json', {
        'version': 'V2.1', 'engine': 'V9_Beta2 (frozen V9_Beta1_1 analytics)',
        'files': {'stores.csv': 'Original engine rows, unchanged', 'actions.csv': 'Original engine actions, unchanged',
                  'Business_Classification.csv': 'Original store fields plus separate V2.1 classification metadata',
                  'Business_Actions.csv': 'Selected ACTION rows with evidence-aware wording; same numerical sort keys',
                  'Beta_Validation_Stores_V2_1.csv': 'Original Beta feedback columns plus V2.1 fields; manual judgments blank'},
        'rates': 'Fractions', 'scores': 'Full-precision methodology scores; not percentages',
        'missing': 'Blank CSV / null JSON, never inferred zero',
        'trace': 'Ordered rule entry, evidence-floor, condition, materiality and final outcome for every store',
        'manual_expected_values': {'AM_Business_Classification_Agree': 'Yes / Partly / No',
                                   'AM_Action_Reason_Agree': 'Yes / Partly / No',
                                   'AM_Operational_Driver_Agree': 'Yes / Partly / No',
                                   'AM_Recovery_Context_Comment': 'Free text'},
        'ranking': 'Triage Rank orders ACTION rows with the frozen Priority/Impact/Severity/Store ID keys. Original Opportunity Rank/eligibility remain unchanged.',
        'scale': 'Working review heuristics only, never a scoring or classification modifier',
    })
    return folder
