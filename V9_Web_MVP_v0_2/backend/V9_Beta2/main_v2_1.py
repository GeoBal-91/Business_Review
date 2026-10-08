"""V9_Beta2 entry point with preserved V2.1 classification."""
import argparse
from dataclasses import replace
from pathlib import Path
import json
from config import Settings, BASE_DIR
from analysis import run_analysis
from data_pipeline import DataValidationError
from business_classification import classify
from triage_config import TriageSettings
from triage_exports import export_triage, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description='V9_Beta2 · preserved V2.1 business classification')
    parser.add_argument('--partner', type=Path)
    parser.add_argument('--benchmark', type=Path)
    parser.add_argument('--sbu')
    parser.add_argument('--list-sbus', action='store_true', help='Print supported SBU values from the benchmark as JSON')
    parser.add_argument('--output', type=Path, default=BASE_DIR / 'Partner_Business_Review_V9_Beta2.pptx')
    parser.add_argument('--reporting-period')
    parser.add_argument('--allow-partial-period', action='store_true')
    parser.add_argument('--analysis-only', action='store_true')
    parser.add_argument('--triage-settings', type=Path, help='JSON with isolated tolerance/review heuristic settings')
    args = parser.parse_args(argv)
    if args.list_sbus:
        from sbu_catalog import supported_sbus
        try:
            print(json.dumps(supported_sbus(args.benchmark or Settings().subbusiness_file)))
        except (DataValidationError, OSError) as exc:
            parser.exit(2, str(exc) + '\n')
        return
    changes = {key: value for key, value in {'input_file': args.partner, 'subbusiness_file': args.benchmark,
                'partner_sbu': args.sbu, 'output_file': args.output, 'reporting_period': args.reporting_period}.items() if value is not None}
    if args.allow_partial_period:
        changes['allow_partial_period'] = True
    config = TriageSettings(**json.loads(args.triage_settings.read_text())) if args.triage_settings else TriageSettings()
    settings = replace(Settings(), **changes)
    folder = args.output.parent / (args.output.stem + '_audit')
    try:
        result = run_analysis(settings)
        triage = classify(result, config)
    except DataValidationError as exc:
        from dataclasses import asdict
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'validation_errors.json', [asdict(x) for x in exc.issues])
        parser.exit(2, str(exc) + '\n')
    export_triage(triage, folder)
    if not args.analysis_only:
        from triage_presentation import render
        render(triage, args.output)
        print('Created:', args.output)
    print('V2.1 classification:', triage.summary['business_classification_counts'])
    print('Audit output:', folder)
    return triage


if __name__ == '__main__':
    main()
