"""Reproduce the paired/product comparison and stress deck (synthetic data)."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_regression import fixture,zero,run
from data_pipeline import D,N,T,P,C,G,U
from presentation import render
from main import export_analysis


def build(folder):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    rows=[fixture('Conversion '+str(i),**{N:10000,'% CVR':.005*i}) for i in range(7)]
    rows += [fixture('Mixed severity and exposure',**{D:0,G:0,N:100000,T:1,P:0,C:1,'% CVR':.18}),fixture('Tiny critical',**{D:0,G:0,N:1,T:1,P:0,C:1,'% CVR':0}),
             fixture('Missing current',month='July'),zero('Confirmed closed',**{'Lifecycle Status':'closed'})]
    # Credible larger SBU aggregate: input is synthetic and explicitly labelled.
    benchmark=fixture('SBU',**{D:20000,N:100000,T:40000,P:3200,C:1000,G:200000})
    result=run(rows,[benchmark])
    fields=['Store ID','Store Status','Scoring Status','Performance Severity Score','Business Impact Score',
            'Paired Priority','Simple Product Priority','Main Driver','Impact Source','Critical Flags']
    result.stores[fields].to_csv(folder/'candidate_comparison.csv',index=False,float_format='%.17g')
    export_analysis(result,folder/'synthetic_audit')
    render(result,folder/'synthetic_stress.pptx')
    return result

if __name__=='__main__': build(sys.argv[1] if len(sys.argv)>1 else Path(__file__).parents[1]/'validation'/'examples')
