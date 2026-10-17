"""Render README figures from saved reports only; never import/train/evaluate the model.
Run: MPLCONFIGDIR=/tmp/habitat-matplotlib .venv/bin/python docs/charts/generate.py
"""
from pathlib import Path
import csv
import argparse
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--preview-dir', type=Path, help='Optional PNG inspection copies outside the published chart directory')
args = parser.parse_args()
if args.preview_dir: args.preview_dir.mkdir(parents=True, exist_ok=True)
NAVY, TEAL, SLATE, AMBER = '#203247', '#357779', '#637588', '#A7772F'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans', 'Arial', 'sans-serif'], 'font.size': 12, 'text.color': NAVY,
    'axes.labelcolor': NAVY, 'xtick.color': SLATE, 'ytick.color': SLATE,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#CBD3DA',
    'figure.facecolor': 'white', 'axes.facecolor': 'white', 'svg.fonttype': 'path',
    'svg.hashsalt': 'habitat-readme-showcase', 'savefig.facecolor': 'white'})
SOURCES = ['reports/evaluation.json', 'reports/model_comparison.json', 'reports/fairness.json',
    'reports/v5-safeguard.json', 'reports/splits.json', 'reports/v7-validation-policy-investigation.json']
before = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}
def load(p): return json.loads((ROOT/p).read_text())
def canvas(title, subtitle, height=4.8):
    fig, ax = plt.subplots(figsize=(11, height))
    fig.subplots_adjust(left=.16, right=.92, top=.74, bottom=.22)
    fig.text(.055,.94,title,fontsize=20,fontweight='bold',va='top')
    fig.text(.055,.85,subtitle,fontsize=11,color=SLATE,va='top')
    return fig,ax
def save(fig, name, note):
    fig.text(.055,.055,note,fontsize=10,color=SLATE,va='bottom')
    fig.savefig(OUT/f'{name}.svg',metadata={'Date': None, 'Creator':'HABITAT AI · report-backed README figure'})
    if args.preview_dir: fig.savefig(args.preview_dir/f'{name}.png', dpi=130)
    svg = OUT/f'{name}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
def percent(ax):
    ax.set_xlim(0,100); ax.xaxis.set_major_formatter(PercentFormatter(100));
    ax.grid(axis='x',color='#E6EAEE',linewidth=.7); ax.set_axisbelow(True)

m = load('reports/model_comparison.json'); e=load('reports/evaluation.json')
assert m['random_forest']==e
for series in m.values():
    (nt,nf),(pf,pt)=series['confusion_matrix']
    expected={'accuracy':(nt+pt)/(nt+nf+pf+pt),'precision':pt/(pt+nf),'recall':pt/(pt+pf),'f1':2*pt/(2*pt+nf+pf)}
    assert all(abs(series[k]-v)<1e-12 for k,v in expected.items())
cm=np.array(e['confusion_matrix']); tn,fp,fn,tp=cm.ravel()
assert cm.sum()==e['test_records']==300 and tp+fn==e['positive_support']==96
for k,v in {'accuracy':(tn+tp)/300,'precision':tp/(tp+fp),'recall':tp/(tp+fn), 'f1':2*tp/(2*tp+fp+fn)}.items():
    assert abs(e[k]-v)<1e-12
labels=['Accuracy','Precision','Recall','F1']; keys=['accuracy','precision','recall','f1']
fig,ax=canvas('Model vs transparent checklist','Held-out synthetic test · n = 300 · same cases, four complementary metrics',5.5)
y=np.arange(4); h=.32
for offset,series,color,hatch in [(-h/2,'random_forest',TEAL,''),(h/2,'checklist',SLATE,'//')]:
    vals=[100*m[series][k] for k in keys]
    bars=ax.barh(y+offset,vals,h,color=color,hatch=hatch,label='Random Forest' if series=='random_forest' else 'Checklist')
    ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=5,fontsize=11)
ax.set_yticks(y,labels); ax.invert_yaxis(); percent(ax); ax.set_xlabel('Metric (%)')
ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),ncol=2,frameon=False,fontsize=11)
save(fig,'model-comparison','Checklist recall is higher. Synthetic-label agreement does not establish real-world usefulness.')

fig,ax=canvas('Where the model gets cases wrong','Random Forest · held-out synthetic test · n = 300 · positive = additional review',5.7)
fig.subplots_adjust(left=.24,right=.79,top=.73,bottom=.25)
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
colors=LinearSegmentedColormap.from_list('habitat',[(0,'#F1F5F7'),(.55,'#B8D0D0'),(1,NAVY)])
for (r,c),value in np.ndenumerate(cm):
    ax.add_patch(Rectangle((c-.5,r-.5),1,1,facecolor=colors(value/cm.max()),edgecolor='white',linewidth=2))
ax.set_xlim(-.5,1.5); ax.set_ylim(1.5,-.5); ax.set_aspect('equal')
for (r,c),v in np.ndenumerate(cm):
    kind=[['True negative','False positive'],['False negative','True positive']][r][c]
    ax.text(c,r,f'{kind}\n{v} cases',ha='center',va='center',fontsize=13,color='white' if v>100 else NAVY)
ax.set_xticks([0,1],['Routine','Additional\nreview']); ax.set_yticks([0,1],['Routine','Additional review'])
ax.set_xlabel('Predicted class'); ax.set_ylabel('Actual synthetic label')
# Counts are directly labelled; vector cells need no raster colour scale.
save(fig,'confusion-matrix','26 of 96 positive cases missed by classification; uncertainty routing is a separate policy.')

s=load('reports/v5-safeguard.json'); a=s['without_uncertainty']; b=s['with_uncertainty']
assert a['human_escalation_count']+a['remaining_routed_count']==300
assert b['human_escalation_count']+b['remaining_routed_count']==300
fig,ax=canvas('The workload of uncertainty escalation','Held-out synthetic test · n = 300 · every real case would still need human handling',4.8)
vals=[a['human_escalation_rate']*100,b['human_escalation_rate']*100]
ax.barh([0,1],vals,color=[SLATE,TEAL],height=.48)
for y,v,d in zip([0,1],vals,[a,b]): ax.text(v+1,y,f"{v:.2f}% · {d['human_escalation_count']}/300",va='center',fontsize=12)
ax.set_yticks([0,1],['Additional class\nonly','Additional class\n+ uncertainty']); ax.invert_yaxis(); percent(ax)
ax.set_xlabel('Routed to extra human review (%)')
save(fig,'uncertainty-workload','Remaining-route errors: 26/189 → 12/128. Different remaining populations; no causal or savings claim.')

f=load('reports/fairness.json'); gs=f['groups']
fig,ax=canvas('Synthetic group errors remain unequal','Held-out test · n = 300 · false-negative rate = missed positives / positive labels',5)
vals=[g['false_negative_rate']*100 for g in gs]
for g in gs: assert int(g['count'])==g['positive_count']+g['negative_count']
ax.barh(range(3),vals,color=TEAL,height=.48)
for i,(g,v) in enumerate(zip(gs,vals)):
    misses=round(g['false_negative_rate']*g['positive_count'])
    ax.text(v+1,i,f"{v:.2f}% · {misses}/{g['positive_count']} positives",va='center')
ax.set_yticks(range(3),[f"{g['group']} · n = {int(g['count'])}" for g in gs]);ax.invert_yaxis();percent(ax)
ax.set_xlabel('False-negative rate (%)')
save(fig,'fairness-fnr','Arbitrary audit groups, small samples; no confidence intervals or proof of real-world fairness.')

sp=load('reports/splits.json'); sizes=[sp[k]['size'] for k in ['train','validation','test']]
for k,n in zip(['train','validation','test'],sizes):
    with (ROOT/f'data/splits/{k}.csv').open() as h: assert sum(1 for _ in csv.DictReader(h))==n
assert sizes==[1400,300,300] and sum(sizes)==2000
fig,ax=canvas('One source dataset, three isolated partitions','Original generated synthetic records · n = 2,000 · related scenarios stay in one partition',3.8)
left=0
for label,n,color in zip(['Train','Validation','Test'],sizes,[NAVY,TEAL,SLATE]):
    ax.barh(0,n,left=left,color=color,height=.5,edgecolor='white',linewidth=2)
    ax.text(left+n/2,0,f'{label}\n{n:,} · {n/20:.0f}%',color='white',ha='center',va='center',fontsize=12)
    left+=n
ax.set_xlim(0,2000);ax.set_ylim(-.6,.6);ax.set_yticks([]);ax.set_xlabel('Records');ax.set_xticks([0,500,1000,1500,2000])
save(fig,'dataset-split','Separate fairness fixture: 200 paired scenarios / 400 rows; excluded from the 2,000-record total.')

p=load('reports/v7-validation-policy-investigation.json'); orig=p['original'];cand=p['minimum_workload_target_policy']
fig,ax=canvas('Why the original routing policy stays active','Validation only · n = 300, including 98 positives · candidate not evaluated on final test',5.8)
y=np.arange(2);h=.32
for off,key,label,color,hatch in [(-h/2,'routing_recall','Routing recall',TEAL,''),(h/2,'extra_review_rate','Extra-review workload',SLATE,'//')]:
    vals=[100*d[key] for d in [orig,cand]]
    bars=ax.barh(y+off,vals,h,label=label,color=color,hatch=hatch)
    ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=4,fontsize=11)
ax.set_yticks(y,['Retained policy','Unadopted\ncandidate']);ax.invert_yaxis();percent(ax);ax.set_xlabel('Validation rate (%)')
ax.axvline(p['target']*100,color=AMBER,ls='--',lw=1.5)
ax.axvline(p['provisional_workload_ceiling']*100,color=SLATE,ls=':',lw=1.5)
ax.legend(loc='lower left',bbox_to_anchor=(0,1.03),ncol=2,frameon=False,fontsize=11)
save(fig,'validation-tradeoff','Dashed: 90% recall target. Dotted: provisional 70% workload ceiling; buyer capacity is unvalidated.')

fig,ax=canvas('Meet the people behind HABITAT AI','Team self-reported contribution allocation · not GitHub commit statistics',3.4)
fig.subplots_adjust(left=.055,right=.96,top=.70,bottom=.28)
left=0
for name,value,color in [('Advaith Ganesh',60,NAVY),('Abdul Malik',20,TEAL),('Ishaant Verma',20,SLATE)]:
    ax.barh(0,value,left=left,color=color,height=.6,edgecolor='white',linewidth=2)
    ax.text(left+value/2,0,f'{name}\n{value}%',ha='center',va='center',color='white',fontsize=11)
    left+=value
ax.set_xlim(0,100);ax.set_ylim(-.5,.5);ax.axis('off')
save(fig,'team-contributions','Human authors: Advaith Ganesh · Abdul Malik · Ishaant Verma. Development assisted by OpenAI Codex.')

assert before=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}
manifest={'scope':'Static README charts; stored reports read only. No model imported, retrained or evaluated.',
 'sources_sha256':before,'figures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.svg'))},
 'team_graphic_source':'Human-supplied brief, 18 October 2026; self-reported allocation 60/20/20, not commit statistics.',
 'plotted_values':{'model_comparison':{k:{metric:v[metric] for metric in keys} for k,v in m.items()},
 'confusion_matrix':cm.tolist(),'extra_review_counts':[a['human_escalation_count'],b['human_escalation_count']],
 'fairness':[{'group':g['group'],'n':g['count'],'positive_n':g['positive_count'],'fnr':g['false_negative_rate']} for g in gs],
 'split':sizes,'validation':{'retained':orig,'candidate':cand,'target':p['target'],'provisional_workload_ceiling':p['provisional_workload_ceiling']}}}
(OUT/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Generated 6 report-backed figures + 1 self-reported team graphic; source hashes unchanged.')
