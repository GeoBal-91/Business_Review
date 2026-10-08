"""CLI entry point; also safe to import from notebooks or an IDE."""
import argparse
from dataclasses import asdict, replace
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
from config import Settings, BASE_DIR
from analysis import run_analysis
from data_pipeline import DataValidationError


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [clean(v) for v in value]
    if isinstance(value, (np.integer,np.bool_)): return value.item()
    if isinstance(value, (float,np.floating)): return float(value) if math.isfinite(value) else None
    if isinstance(value, (Path,pd.Timestamp)): return str(value)
    if hasattr(value,'isoformat'): return value.isoformat()
    return value


def export_analysis(result, folder):
    from coverage_guard import comparison_exports
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    for name,frame in [('stores',result.stores),('metrics',result.metrics),('opportunities',result.opportunities),
                       ('coverage',result.data.coverage),('partner_comparisons',comparison_exports(result.data)),('monthly',result.data.monthly),('store_history',result.data.store_monthly),('sbu_history',result.data.selected_sbu),
                       ('actions',pd.DataFrame(result.actions,columns=['Store ID','Store','Metric','Issue','Action','Intended Effect','Priority','Metric Priority','Exposure','Owner','Deadline'])),
                       ('reviews',pd.DataFrame(result.reviews,columns=['Store ID','Store','Type','Issue','Action','Metric','Known Priority','Owner','Deadline']))]:
        frame.to_csv(folder / (name+'.csv'), index=False, float_format='%.17g')
    report = {**result.summary,'settings':asdict(result.settings), 'issues':[asdict(i) for i in result.data.issues],
              'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(BASE_DIR.glob('*.py'))}}
    (folder/'run_audit.json').write_text(json.dumps(clean(report),indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    (folder/'metric_records.json').write_text(json.dumps(clean(result.metrics.to_dict('records')),indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    from beta_validation import export_validation
    export_validation(result, folder)
    return folder


def main(argv=None):
    parser = argparse.ArgumentParser(description='V9_Beta2 partner business review')
    parser.add_argument('--partner',type=Path); parser.add_argument('--benchmark',type=Path)
    parser.add_argument('--output',type=Path,default=BASE_DIR/'Partner_Business_Review_V9_Beta2.pptx'); parser.add_argument('--sbu')
    parser.add_argument('--cvr-mode',choices=['reported'],help='Official reported CVR only; delivered/session is diagnostic')
    parser.add_argument('--priority-model',choices=['paired','simple_product'])
    parser.add_argument('--reporting-period'); parser.add_argument('--allow-partial-period',action='store_true')
    parser.add_argument('--analysis-only',action='store_true')
    args=parser.parse_args(argv)
    changes = {key:value for key,value in {'input_file':args.partner,'subbusiness_file':args.benchmark,
        'output_file':args.output,'partner_sbu':args.sbu,'cvr_mode':args.cvr_mode,'priority_model':args.priority_model,
        'reporting_period':args.reporting_period}.items() if value is not None}
    if args.allow_partial_period: changes['allow_partial_period']=True
    settings=replace(Settings(),**changes)
    folder=settings.output_file.parent/(settings.output_file.stem+'_audit')
    try:
        result=run_analysis(settings)
    except DataValidationError as exc:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'validation_errors.json').write_text(json.dumps([asdict(i) for i in exc.issues],indent=2),encoding='utf-8')
        parser.exit(2,str(exc)+'\n')
    export_analysis(result,folder)
    if not args.analysis_only:
        from presentation import render
        render(result)
        print('Created:',settings.output_file)
    print('Audit output:',folder)
    print(f"Stores: {len(result.stores)}; opportunities: {len(result.actions)}; review items: {len(result.reviews)}")
    return result


if __name__=='__main__':
    main()
