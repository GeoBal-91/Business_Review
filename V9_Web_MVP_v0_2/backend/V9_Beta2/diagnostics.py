"""Presentation-only view of existing store/metric records; no score calculation."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from ppt_core import add_text, add_footer, add_chart_image, save_chart
from formatting import format_score, format_percent, format_currency, format_number
from data_pipeline import G,D,N,T,U,present
from theme import GREEN, GREY, DARK, WHITE, ORANGE, MPL_GREEN
from scoring import RATE_COLUMNS

PALE=RGBColor(245,247,248)
BORDER=RGBColor(220,227,228)
MINT=RGBColor(233,247,242)
AMBER=RGBColor(255,245,223)


def box(slide,x,y,w,h,fill=PALE,border=None):
    shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    shape.adjustments[0]=.09
    shape.fill.solid();shape.fill.fore_color.rgb=fill
    if border:
        shape.line.color.rgb=border;shape.line.width=Pt(.7)
    else: shape.line.fill.background()
    shape._element.spPr.append(OxmlElement('a:effectLst'))
    for effect in shape._element.xpath('./p:style/a:effectRef'): effect.set('idx','0')
    return shape


def bar(slide,x,y,w,value,color=GREEN):
    box(slide,x,y,w,.055,BORDER)
    if present(value) and value>0: box(slide,x,y,w*min(1,max(0,value)),.055,color)


def metric_records(result,sid):
    return {r['metric']:r for r in result.metrics[result.metrics['Store ID']==sid].to_dict('records')}


def confidence_label(m):
    n=m['denominator']
    suffix=f" · n={n:,.0f}" if present(n) else ' · n unavailable'
    if m['state'] not in {'Assessed'} or not present(m['raw_rate']) or not present(m['confidence_weight']):
        return m['metric']+' · Rate unavailable / not assessed'+suffix, None
    return f"{m['metric']} {m['confidence_weight']:.0%}"+suffix, m['confidence_weight']


def trend_data(result,row):
    metric=row['Main Driver']
    if metric not in RATE_COLUMNS: return None
    months=pd.date_range(end=result.data.reporting_period,periods=6,freq='MS')
    hist=result.data.store_monthly
    series=hist[hist['Store ID']==row['Store ID']].set_index('Period')[RATE_COLUMNS[metric]].reindex(months)
    if series.notna().sum()<2: return None
    return metric,series


def driver_labels(row):
    if row['Scoring Status']=='Incomplete':
        return ('Leading known issue',row['Main Driver'] if row['Main Driver']!='None' else 'Not assessed',
                'Worst known KPI','Largest known exposure')
    return ('Main Business Action KPI',row['Main Driver'],'Worst KPI / Severity Driver','Largest Exposure KPI')


def kpi_card(slide,m,x,y,nonactive=False,missing_current=False):
    box(slide,x,y,2.94,1.34,WHITE,BORDER)
    name=m['metric']; raw=m['raw_rate']; b=m['benchmark']
    add_text(slide,name,x+.14,y+.10,1.6,.2,size=11,bold=True,color=GREY)
    add_text(slide,format_percent(raw),x+.14,y+.35,2.65,.32,size=21 if present(raw) else 15,bold=True)
    reference='Target' if name=='Uptime' else 'SBU'
    add_text(slide,f'{reference} {format_percent(b)}',x+.14,y+.75,2.66,.18,size=9)
    if nonactive:
        gap='Lifecycle state · reference only'
    elif not present(raw) or not present(b):
        gap='Gap not assessed'
    else:
        pp=(raw-b)*100
        direction='Above' if pp>1e-8 else 'Below' if pp < -1e-8 else 'At'
        gap=f'{direction} {reference} · {pp:+.1f} pp'
    add_text(slide,gap,x+.14,y+.98,2.66,.17,size=9)
    if name=='Uptime' and missing_current:
        add_text(slide,'Missing current evidence',x+.14,y+1.17,2.66,.15,size=8,bold=True,color=GREY)
    elif name=='Uptime' and not m['eligible']:
        add_text(slide,'Hygiene only — excluded from business Priority',x+.14,y+1.17,2.66,.15,size=7.7,bold=True,color=GREY)
    elif present(raw) and present(b):
        scale=max(raw,b,.001)*1.12
        bar(slide,x+1.50,y+.805,1.24,raw/scale)
        marker=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x+1.5+1.24*b/scale),Inches(y+.78),Inches(.018),Inches(.10))
        marker.fill.solid();marker.fill.fore_color.rgb=DARK;marker.line.fill.background()


def build_store(slide,result,row,charts):
    metrics=metric_records(result,row['Store ID'])
    incomplete=row['Scoring Status']=='Incomplete'
    nonactive=row['Store Status'] in {'Closed','No Activity'}
    material=bool(row['Eligible Opportunity'])
    name=row.get('Store Name')
    name=name if isinstance(name,str) and name.strip() else row['Store Address Address']
    add_text(slide,'Store Diagnostics',.65,.30,8,.18,size=9,bold=True,color=GREY)
    add_text(slide,name,.65,.54,11.95,.40,size=20 if len(name)<72 else 15,bold=True)
    location=' · '.join(str(row[k]) for k in ('City','Location') if isinstance(row.get(k),str) and row[k].strip())
    add_text(slide,(location+' · ' if location else '')+result.data.reporting_period.strftime('%B %Y'),.65,1.01,6.1,.20,size=10,color=GREY)
    badges=[row['Store Status'].upper(), 'DATA OK' if row['Data Quality']=='OK' else 'MISSING DATA' if row['Data Quality'] in {'Missing current data','Incomplete'} else 'DATA '+row['Data Quality'].upper(),row['Scoring Status'].upper()]
    x=.65
    for badge,w in zip(badges,[1.32,1.62,1.62]):
        box(slide,x,1.32,w,.25,MINT if badge in {'ACTIVE','DATA OK','COMPLETE'} else AMBER if incomplete else PALE)
        add_text(slide,badge,x+.08,1.355,w-.16,.15,size=8,bold=True)
        x+=w+.10
    for i,(label,key,formatter) in enumerate([('GMV',G,format_currency),('DELIVERED',D,format_number),('SESSIONS',N,format_number),('ATTEMPTS',T,format_number)]):
        x=6.80+i*1.52
        add_text(slide,label,x,1.07,1.4,.16,size=8,color=GREY)
        value=formatter(row[key]);add_text(slide,value,x,1.31,1.42,.25,size=14 if present(row[key]) else 10,bold=True)
    for i,metric in enumerate(['CVR','PNA','Cancels','Uptime']): kpi_card(slide,metrics[metric],.65+i*3.04,1.76,nonactive,row["Data Quality"]=="Missing current data")
    score_specs=[('Severity','Performance Severity Score',.65,1.65),('Impact','Business Impact Score',2.40,1.65),('Priority','Opportunity Score',4.15,2.35)]
    for label,key,x,w in score_specs:
        priority=label=='Priority'
        fill=GREEN if priority and material else AMBER if priority and incomplete else MINT if priority and not nonactive else PALE
        color=WHITE if priority and material else DARK
        box(slide,x,3.24,w,.90,fill)
        add_text(slide,label,x+.13,3.34,w-.26,.16,size=9,bold=True,color=color)
        value=format_score(row[key],result.settings.min_priority if priority else None)
        add_text(slide,value,x+.13,3.58,w-.26,.31,size=25 if present(row[key]) else 14,bold=True,color=color)
        if priority:
            state='NOT ASSESSED' if incomplete else 'NO ROUTINE RECOVERY' if nonactive else 'MATERIAL' if material else 'BELOW MAIN THRESHOLD'
            add_text(slide,state,x+.13,3.98,w-.26,.12,size=7.5,bold=True,color=color)
    main,value,worst,largest=driver_labels(row)
    if nonactive: main,value='Lifecycle state',row['Store Status']
    for j,(label,value) in enumerate([(main,value),(worst,row['Severity Driver']),(largest,row['Impact Source'])]):
        add_text(slide,label,6.83,3.27+j*.30,3.2,.20,size=9,color=GREY)
        add_text(slide,value,10.04,3.27+j*.30,2.78,.20,size=10,bold=True)
    box(slide,.65,4.28,5.85,1.45,WHITE,BORDER)
    add_text(slide,'Confidence / evidence',.80,4.40,5.5,.20,size=11,bold=True)
    for j,metric in enumerate(['CVR','PNA','Cancels']):
        text,weight=confidence_label(metrics[metric]); y=4.77+j*.29
        add_text(slide,text,.80,y,5.35 if weight is None else 3.20,.21,size=8.7 if weight is None else 10)
        if weight is not None: bar(slide,4.23,y+.10,2.06,weight)
    box(slide,6.68,4.28,6.09,1.45,WHITE,BORDER)
    trend=trend_data(result,row)
    heading='Leading known issue trend' if incomplete else 'Main KPI trend'
    add_text(slide,heading,6.84,4.40,5.6,.20,size=11,bold=True)
    if trend is None:
        add_text(slide,'Trend unavailable',6.84,4.90,5.4,.3,size=13,color=GREY)
    else:
        metric,series=trend
        fig,ax=plt.subplots(figsize=(5.7,.93))
        x=np.arange(6)
        ax.plot(x,series.to_numpy(dtype=float)*100,'o-',color=MPL_GREEN,linewidth=1.7,markersize=3,label=metric)
        reference=metrics[metric]['benchmark']
        if present(reference): ax.axhline(reference*100,color='#777777',linestyle='--',linewidth=.9,label='95% target' if metric=='Uptime' else 'Latest SBU')
        ax.set_xticks(x,series.index.strftime('%b'),fontsize=7)
        ax.tick_params(axis='y',labelsize=7)
        ax.set_ylabel('%',fontsize=7,rotation=0,labelpad=5)
        ax.spines[['top','right']].set_visible(False)
        ax.legend(loc='upper left',bbox_to_anchor=(0,1.4),ncol=2,fontsize=6.5,frameon=False)
        path=charts('diagnostic_'+hashlib.sha256(str(row['Store ID']).encode()).hexdigest()[:12]+'.png')
        save_chart(fig,path);add_chart_image(slide,path,6.92,4.79,5.63,.86)
    flags=[m for m in metrics.values() if m['critical_flag']]
    if flags and not nonactive:
        bits=[]
        for m in flags:
            n=f" · n={m['denominator']:,.0f}" if present(m['denominator']) else ' · uptime observation'
            bits.append(f"{m['metric']} {format_percent(m['raw_rate'])}"+n+(' (hygiene only)' if not m['eligible'] else ''))
        title='Critical Review — raw observations; separate from business materiality'
        body=' | '.join(bits)
    elif nonactive:
        title='Lifecycle / activity evidence'
        body=row['Store Status Reason']
    elif incomplete:
        title='Assessment incomplete — review evidence before selecting a business action'
        body=row['Store Status Reason'] if row['Data Quality']!='OK' else 'Unavailable metrics: '+', '.join(m['metric'] for m in metrics.values() if m['eligible'] and m['state']=='Missing')
    else:
        title='Assessment evidence'
        body=row['Store Status Reason']+' · Critical observations: None'
    add_text(slide,title,.75,5.86,11.9,.20,size=10,bold=True,color=ORANGE if flags or incomplete else GREY)
    add_text(slide,body,.75,6.11,11.9,.27,size=9.5)
    box(slide,.65,6.48,12.12,.82,MINT if not incomplete else AMBER)
    action_title='Required data review' if incomplete else 'Lifecycle / activity action' if nonactive else 'Recommended Action'
    add_text(slide,action_title,.80,6.57,11.7,.16,size=9,bold=True,color=GREY)
    add_text(slide,row['Recommended Focus'],.80,6.79,11.7,.22,size=12,bold=True)
    effect=metrics.get(row['Main Driver'],{}).get('intended_effect','') if not incomplete and not nonactive else ''
    if incomplete:
        detail=row['Store Status Reason'] if row['Data Quality']!='OK' else 'Unavailable metrics: '+', '.join(m['metric'] for m in metrics.values() if m['eligible'] and m['state']=='Missing')
        add_text(slide,'Evidence: '+detail,.80,7.07,11.7,.15,size=9,color=GREY)
    elif effect: add_text(slide,'Intended effect: '+effect,.80,7.07,11.7,.15,size=9,color=GREY)
    add_footer(slide)
    # Notes keep full identifiers and lifecycle context even when long labels wrap.
    return slide


def build(prs,result,charts):
    for _,row in result.stores.sort_values('Store ID').iterrows():
        slide=prs.slides.add_slide(prs.slide_layouts[6]);build_store(slide,result,row,charts)
