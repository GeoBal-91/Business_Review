"""V2.1 business triage above the frozen Beta engine. No scoring mutations."""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import pandas as pd
from data_pipeline import G, D, N, T, period_row
from triage_config import TriageSettings

RULES = ('BASE_PRIORITY', 'SINGLE_STORE_OVERRIDE', 'MULTI_KPI_ESCALATION',
         'SEVERE_PRIMARY_CORROBORATION', 'BUSINESS_MATERIALITY_OVERRIDE')
RULE_FIELDS = ('Base Priority Rule', 'Single-Store Override', 'Multi-KPI Escalation',
               'Severe Primary + Corroboration', 'Business Materiality Override')
METRICS = ('CVR', 'PNA', 'Cancels', 'Uptime')
BUSINESS_CLASSES = ('ACTION', 'MONITOR', 'HEALTHY', 'UNCLASSIFIED')


def finite(value):
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def number(value):
    return float(value) if finite(value) else None


def ge(a, b):
    return a is not None and b is not None and a >= b - 1e-12


def le(a, b):
    return a is not None and b is not None and a <= b + 1e-12


def multiple(rate, reference, factor):
    # A ratio against zero is not evidence. Absolute-gap/absolute-rate tests remain available.
    return reference is not None and reference > 0 and ge(rate, factor * reference)


def signal(record, include_uptime):
    name = record['metric']
    raw, benchmark, n = (number(record.get(k)) for k in ('raw_rate', 'benchmark', 'denominator'))
    commercial = bool(record.get('eligible')) and (name != 'Uptime' or include_uptime)
    assessed = record.get('state') == 'Assessed' and raw is not None and benchmark is not None
    qualified = assessed and commercial and (name == 'Uptime' or ge(n, 50 if name == 'CVR' else 10))
    gap = raw - benchmark if raw is not None and benchmark is not None else None
    adverse = assessed and (gap < -1e-12 if name == 'CVR' else raw < .95 - 1e-12 if name == 'Uptime' else gap > 1e-12)
    severe = meaningful = material = False
    if assessed:
        if name == 'CVR':
            severe = le(raw, .6 * benchmark) and le(gap, -.03)
            meaningful = severe
        elif name in {'PNA', 'Cancels'}:
            severe = ge(raw, 2 * benchmark) and ge(raw, .20 if name == 'PNA' else .15)
            meaningful = adverse and (multiple(raw, benchmark, 1.25) or ge(gap, .03))
            material = adverse and multiple(raw, benchmark, 1.5)
        else:
            severe, material, meaningful = le(raw, .85), le(raw, .90), le(raw, .92)
    band = ('NOT_ASSESSED' if not assessed else 'SEVERE' if severe else
            'MATERIALLY_ADVERSE' if material else 'ADVERSE' if adverse else 'HEALTHY')
    evidence_complete = assessed or (record.get('state') == 'No exposure' and n == 0)
    return dict(metric=name, raw_rate=raw, benchmark=benchmark, denominator=n, gap=gap,
                commercial=commercial, assessed=assessed, evidence_floor=qualified,
                evidence_complete=evidence_complete,
                adverse=bool(adverse), severe=bool(severe), material=bool(material),
                meaningful=bool(meaningful), band=band)


def operational_states(row, signals, current, supported_model):
    status = row['Store Status']
    if not current or status == 'Unknown':
        states = ['MISSING_CURRENT' if not current or row.get('Data Quality') == 'Missing current data' else 'DATA_REVIEW']
    elif status == 'Closed':
        states = ['CLOSED']
    elif status == 'No Activity':
        states = ['NO_ACTIVITY']
    elif (row.get('Scoring Status') != 'Complete' or row.get('Data Quality') != 'OK'
          or not finite(row.get('Opportunity Score')) or not supported_model):
        states = ['DATA_REVIEW']
    else:
        states = ['COMPLETE']
    if row.get('Data Quality') != 'OK' and states[0] not in {'MISSING_CURRENT', 'DATA_REVIEW'}:
        states.append('DATA_REVIEW')
    u = signals['Uptime']
    if current and status == 'Active' and not u['commercial'] and (u['raw_rate'] is None or u['raw_rate'] < .95):
        states.append('HYGIENE_REVIEW')
    return states


def likely_driver(primary, signals, classified):
    """Hypotheses and investigation wording, not causal attribution."""
    if classified == 'UNCLASSIFIED':
        return 'Not assessed; review lifecycle / data evidence', 'Reconcile lifecycle and missing performance evidence before selecting a business intervention'
    ops = [signals[k] for k in ('PNA', 'Cancels')]
    strong = [s['metric'] for s in ops if s['commercial'] and s['evidence_floor'] and s['meaningful']]
    weak = [s['metric'] for s in ops if s['commercial'] and s['assessed'] and s['meaningful'] and not s['evidence_floor']]
    uptime = signals['Uptime']['commercial'] and signals['Uptime']['assessed'] and signals['Uptime']['meaningful']
    if primary == 'CVR':
        if uptime:
            return ('Store availability; possible contributing factor' + ('; low-n PNA/Cancels corroboration only' if weak else ''),
                    'Restore store availability and investigate stock/order execution issues, then reassess conversion')
        if strong:
            return ('Stock availability / order execution; evidence suggests an operational contribution',
                    'Investigate stock accuracy and order execution as possible contributors, then reassess conversion')
        if weak:
            return ('PNA/Cancels: low-denominator corroboration only; root cause unconfirmed',
                    'Investigate conversion and review the few affected orders; validate stock or execution issues before assigning a root cause')
        return ('Assortment / pricing / content / discoverability / funnel quality: investigate',
                'Review assortment, pricing, content and discoverability, then investigate the conversion journey')
    if primary == 'Cancels':
        return ('Stock accuracy / fulfilment; possible contributing factor' if 'PNA' in strong else
                'Order execution; investigate cancellation reasons' if not weak else
                'Few cancellation observations; root cause unconfirmed',
                'Review cancellation reasons and stock accuracy to investigate the upstream fulfilment issue')
    if primary == 'PNA':
        return ('Availability / stock synchronization; possible contributing factor' if 'PNA' in strong else
                'Product availability; verify the sample before causal attribution',
                'Review affected products, stock accuracy and availability synchronization; validate the cause of PNA')
    if primary == 'Uptime' and signals['Uptime']['commercial']:
        return 'Store availability; investigate scheduling / execution', 'Restore availability during scheduled opening hours and verify persistent downtime'
    return 'No supported primary issue', 'Continue routine monitoring of performance and evidence'


@dataclass
class TriageResult:
    analysis: object
    stores: pd.DataFrame
    actions: list
    traces: list
    summary: dict
    settings: TriageSettings


def classify(result, settings=None):
    settings = settings or TriageSettings()
    stores = result.stores
    if stores['Store ID'].duplicated().any():
        raise ValueError('Duplicate Store IDs in current analysis; do not merge automatically')
    period = result.data.reporting_period
    current = (stores['Period'] == period) & (stores['Last Observed Period'] == period)
    operating = current & (stores['Store Status'] == 'Active') & ((stores[[D, N, T]] > 0).any(axis=1))
    operating_count = int(operating.sum())
    supported = result.settings.priority_model == 'paired' and result.settings.min_priority == 5.0
    include_uptime = result.settings.partner_sbu != 'FLOWERS' and result.settings.include_uptime
    from presentation_polish import current_coverage_incomplete
    coverage_ok = not current_coverage_incomplete(result)
    latest = period_row(result.data.monthly, period)
    partner_gmv = number(latest.get(G)) if latest is not None else None
    valid_gmv = stores[current & stores[G].map(finite) & (stores['Store Status'] != 'Unknown')].sort_values(
        [G, 'Store ID'], ascending=[False, True], kind='mergesort')
    gmv_ranks = {sid: i + 1 for i, sid in enumerate(valid_gmv['Store ID'])}
    metadata, traces = [], []
    for idx, row in stores.iterrows():
        sid = row['Store ID']
        m = {x['metric']: signal(x, include_uptime) for x in result.metrics[result.metrics['Store ID'] == sid].to_dict('records')}
        if set(m) != set(METRICS):
            raise ValueError('Classification requires all four existing metric records')
        states = operational_states(row, m, bool(current.loc[idx]), supported)
        assessable = states[0] == 'COMPLETE' and all(x['evidence_complete'] for x in m.values() if x['commercial'])
        if states[0] == 'COMPLETE' and not assessable:
            states[0] = 'DATA_REVIEW'
        priority = number(row['Opportunity Score'])
        domain = [k for k, s in m.items() if s['evidence_floor'] and s['adverse']]
        severe = [k for k, s in m.items() if s['evidence_floor'] and s['severe']]
        operational = [k for k in ('PNA', 'Cancels', 'Uptime') if k in domain]
        material = [k for k in operational if m[k]['material']]
        corroboration = [k for k in ('PNA', 'Cancels', 'Uptime')
                         if m[k]['commercial'] and m[k]['assessed'] and m[k]['meaningful']
                         and (k == 'Uptime' or ge(m[k]['denominator'], 1))]
        raw_share = (float(row[G]) / partner_gmv if finite(row[G]) and partner_gmv is not None and partner_gmv > 0 else None)
        materiality_assessed = coverage_ok and raw_share is not None and bool(current.loc[idx])
        share_pass = materiality_assessed and ge(raw_share, .20)
        exposure = ge(number(row[D]), 20) or ge(number(row[N]), 200) or share_pass
        top_two = gmv_ranks.get(sid, math.inf) <= 2
        important = materiality_assessed and (share_pass or (top_two and exposure))
        p_range = lambda low, high: priority is not None and low <= priority < high
        entries = [priority is not None and priority >= 5, p_range(4, 5), p_range(4, 5), p_range(3.5, 5), p_range(3, 5)]
        floors = [assessable, m.get(row['Main Driver'], {}).get('evidence_floor', False), len(domain) >= 2,
                  m['CVR']['evidence_floor'], len(operational) >= 2]
        conditions = [True, operating_count == 1, len(severe) >= 1,
                      m['CVR']['severe'] and bool(corroboration), bool(material)]
        materiality = [True, True, True, True, bool(important)]
        matches = [bool(assessable and entries[i] and floors[i] and conditions[i] and materiality[i]) for i in range(5)]
        matched = [rule for rule, passed in zip(RULES, matches) if passed]
        raw_adverse = [s for s in m.values() if s['commercial'] and s['adverse']]
        any_severe = any(s['commercial'] and s['severe'] for s in m.values())
        # Material CVR miss is bounded by the tiny-gap allowance below. Operational ratio conditions block tolerance.
        any_material = any(s['commercial'] and s['material'] for s in m.values())
        tolerances = {'CVR': settings.healthy_cvr_gap_pp / 100,
                      'PNA': settings.healthy_pna_gap_pp / 100, 'Cancels': settings.healthy_cancels_gap_pp / 100}
        tiny = all(le(abs(s['gap']), tolerances[s['metric']]) if s['metric'] != 'Uptime'
                   else ge(s['raw_rate'], settings.healthy_uptime_min) for s in raw_adverse)
        healthy = (assessable and priority < settings.healthy_priority_below and not any_severe and not any_material and tiny)
        classification = 'UNCLASSIFIED' if not assessable else 'ACTION' if matched else 'HEALTHY' if healthy else 'MONITOR'
        low = le(number(row[D]), settings.low_delivered_max) or le(number(row[T]), settings.low_attempts_max)
        ultra = le(number(row[D]), settings.ultra_delivered_max) or le(number(row[T]), settings.ultra_attempts_max)
        low_corroboration = [k for k in corroboration if k != 'Uptime' and not m[k]['evidence_floor']]
        human = (classification == 'ACTION' and (low or ultra or bool(low_corroboration))) or 'DATA_REVIEW' in states or 'MISSING_CURRENT' in states or ('NO_ACTIVITY' in states and row.get('Lifecycle Status') != 'not launched') or ('CLOSED' in states and row.get('Closure Evidence') == 'Inferred')
        driver, action = likely_driver(row['Main Driver'], m, classification)
        if classification == 'UNCLASSIFIED':
            action = row.get('Recommended Focus', action)
        record = {'Store ID': sid, 'Business Classification': classification,
                  'Action Reason': matched[0] if matched else '', 'Supporting Rule Matches': matched[1:],
                  'Healthy Tolerance Candidate': bool(healthy and raw_adverse),
                  'Low Scale Flag': bool(low), 'Ultra Low Scale Flag': bool(ultra),
                  'Scale Evidence Available': finite(row[D]) or finite(row[T]),
                  'Human Review Required': bool(human), 'Primary Action KPI': row['Main Driver'],
                  'Likely Operational Driver': driver, 'Operational/Data State': states,
                  'V2.1 Recommended Action': action,
                  'Operating Commercial Store Count': operating_count,
                  'Store GMV Share': raw_share, 'GMV Display Rank': gmv_ranks.get(sid),
                  'Materiality Assessed': bool(materiality_assessed),
                  'Uptime Interpretation': m['Uptime']['band'],
                  'Low-Denominator Corroboration': low_corroboration,
                  'Qualified Adverse Domains': domain, 'Qualified Severe KPIs': severe,
                  'Classification Version': 'V2.1', 'Selected Triage Action': False, 'Triage Rank': None}
        record.update(dict(zip(RULE_FIELDS, matches)))
        metadata.append(record)
        traces.append({'Store ID': sid, 'assessable': bool(assessable), 'supported_paired_model': supported,
                       'signals': m, 'current_store_coverage_complete': coverage_ok,
                       'operating_commercial_stores': operating_count, 'store_gmv_share': raw_share,
                       'top_two_by_current_gmv': top_two, 'top_two_exposure_guard': bool(exposure),
                       'qualified_adverse_domains': domain, 'qualified_severe_kpis': severe,
                       'qualified_adverse_operational_kpis': operational, 'material_operational_kpis': material,
                       'meaningful_corroboration': corroboration,
                       'rules': {rule: {'entry_range': bool(entries[i]), 'evidence_floor': bool(floors[i]),
                                         'severe_or_material_condition': bool(conditions[i]),
                                         'materiality': bool(materiality[i]), 'outcome': matches[i]}
                                 for i, rule in enumerate(RULES)}})
    enriched = stores.merge(pd.DataFrame(metadata), on='Store ID', how='left', validate='one_to_one', sort=False)
    # Same frozen sort keys, on a separate triage subset. AnalysisResult opportunities/ranks remain untouched.
    ranked = enriched[enriched['Business Classification'] == 'ACTION'].sort_values(
        ['Opportunity Score', 'Business Impact Score', 'Performance Severity Score', 'Store ID'],
        ascending=[False, False, False, True], kind='mergesort')
    ranks = {sid: i + 1 for i, sid in enumerate(ranked['Store ID'])}
    enriched['Triage Rank'] = enriched['Store ID'].map(ranks)
    selected = ranked.head(result.settings.top_opportunities)
    enriched['Selected Triage Action'] = enriched['Store ID'].isin(selected['Store ID'])
    actions = []
    for _, row in selected.iterrows():
        primary = result.metrics[(result.metrics['Store ID'] == row['Store ID']) & (result.metrics['metric'] == row['Main Driver'])]
        if primary.empty:
            raise ValueError('ACTION row has no frozen Primary KPI; do not invent a driver')
        metric = primary.iloc[0]
        actions.append({'Store ID': row['Store ID'], 'Store': row['Store Address Address'], 'Metric': row['Main Driver'],
                        'Issue': row['Main Issue'], 'Action': row['V2.1 Recommended Action'],
                        'Intended Effect': metric['intended_effect'], 'Priority': row['Opportunity Score'],
                        'Metric Priority': metric['paired_priority'], 'Exposure': metric['exposure'],
                        'Owner': '', 'Deadline': '', 'Triage Rank': ranks[row['Store ID']],
                        **{k: row[k] for k in ['Business Classification', 'Action Reason', 'Primary Action KPI',
                                               'Likely Operational Driver', 'Low Scale Flag', 'Ultra Low Scale Flag',
                                               'Human Review Required']}})
    summary = counts(enriched)
    summary.update({'version': 'V9_Beta2', 'calibration_rules': 'V2.1', 'sbu': result.settings.partner_sbu,
                    'reporting_period': result.summary['reporting_period'],
                    'operating_commercial_stores': operating_count, 'selected_triage_actions': len(actions),
                    'base_priority_threshold': 5.0, 'threshold_status': 'Provisional',
                    'interpretation_settings': asdict(settings),
                    'input_hashes': result.summary['input_hashes'],
                    'current_coverage_complete': coverage_ok,
                    'materiality_note': 'Share/top-two materiality is not assessed under partial current coverage',
                    'heuristics_status': 'Healthy tolerance / scale defaults are isolated working assumptions, pending exact real-case fixture replay'})
    return TriageResult(result, enriched, actions, traces, summary, settings)


def counts(stores):
    action = stores['Business Classification'] == 'ACTION'
    return {'known_stores': len(stores), 'business_classification_counts': {k: int((stores['Business Classification'] == k).sum()) for k in BUSINESS_CLASSES},
            'action_reason_counts': {k: int((stores['Action Reason'] == k).sum()) for k in RULES},
            'healthy_tolerance_count': int(stores['Healthy Tolerance Candidate'].sum()),
            'low_scale_action_count': int((action & stores['Low Scale Flag']).sum()),
            'ultra_low_scale_action_count': int((action & stores['Ultra Low Scale Flag']).sum()),
            'human_review_required_count': int(stores['Human Review Required'].sum()),
            'unclassified_count': int((stores['Business Classification'] == 'UNCLASSIFIED').sum())}


def calibration_summary(profiles, duplicate_profile_aliases=None):
    """Deduplicate explicitly identified identical *profiles*, never merge store identities."""
    aliases = duplicate_profile_aliases or {}
    kept, omitted = [], []
    for name, triage in profiles.items():
        if name in aliases:
            target = aliases[name]
            if target not in profiles or target in aliases or target == name:
                raise ValueError('Duplicate alias must name an existing canonical profile')
            a, b = triage.analysis, profiles[target].analysis
            if a.settings.partner_sbu != b.settings.partner_sbu or a.summary['reporting_period'] != b.summary['reporting_period']:
                raise ValueError('Duplicate profile periods/SBUs conflict')
            pd.testing.assert_frame_equal(a.stores.sort_values('Store ID').reset_index(drop=True), b.stores.sort_values('Store ID').reset_index(drop=True), check_exact=True)
            pd.testing.assert_frame_equal(triage.stores.sort_values('Store ID').reset_index(drop=True), profiles[target].stores.sort_values('Store ID').reset_index(drop=True), check_exact=True)
            omitted.append({'profile': name, 'canonical_profile': target})
        else:
            kept.append(triage.stores)
    if not kept:
        raise ValueError('At least one canonical calibration profile is required')
    return {**counts(pd.concat(kept, ignore_index=True)), 'canonical_profiles': len(kept),
            'duplicate_profiles_excluded': omitted,
            'deduplication_policy': 'Explicit profile aliases verified against identical Store IDs and full records; no address-based store merging'}
