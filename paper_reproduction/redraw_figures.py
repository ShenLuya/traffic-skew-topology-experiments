"""Regenerate paper figures from archived run-level CSV files.

This program never invokes BookSim and never edits the archived input CSVs.
Run from any directory with::

    python paper_reproduction/redraw_figures.py

Outputs are placed in ``paper_reproduction/generated`` so the tracked
reference figures remain available for comparison.
"""
from pathlib import Path
import csv, json, math, statistics as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
OUT = ROOT / 'generated'
FIG = OUT / 'figures'
OUT.mkdir(exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
RATES = [.02, .04, .06, .07, .075, .08, .10]
TOPS = ['mesh', 'torus', 'fattree']
NAMES = {'mesh':'Mesh', 'torus':'Torus', 'fattree':'Fat-Tree'}
COLORS = ['#0072B2', '#D55E00', '#009E73']
BOUND = 1 / (64 * .2)

def read(name):
    with (DATA/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def completed(r): return r['status'] in ('OK', 'STABLE')
def stats(vals):
    # Two-sided 95% Student t critical values, df=2 and df=4.
    critical={3:4.302652729696142,5:2.7764451051977987}
    return (st.mean(vals), critical[len(vals)]*st.stdev(vals)/math.sqrt(len(vals))) if len(vals)>1 else (vals[0],float('nan'))
def save_csv(name, rs):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0])); w.writeheader();w.writerows(rs)
def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'), bbox_inches='tight')
    fig.savefig(FIG/(name+'.png'), dpi=200,bbox_inches='tight')
    plt.close(fig)
def load_axis(ax, rates=RATES):
    ax.axvspan(BOUND, .103, color='#eeeeee', zorder=0)
    ax.axvline(BOUND, color='#777777', lw=.8, ls=':', zorder=1)
    ax.set_xlim(min(rates)-.002,max(rates)+.003)
    ax.set_xticks([.02,.04,.06,.075,.10] if rates==RATES else rates)
    ax.tick_params(axis='x',rotation=35)
    ax.grid(axis='y',alpha=.22)
    ax.set_xlabel('Offered rate\n(flits/node/cycle)')
def foot(fig, text):
    # Interpretation and sample sizes are supplied by the manuscript captions.
    pass

raw = [r for r in read('mesh_torus_raw_runs.csv')+read('fattree64_raw_runs.csv') if r['topology'] in TOPS and float(r['injection_rate']) in RATES]
assert len(raw)==210
for r in raw:
    if completed(r):
        r['accepted_over_injected']=str(float(r['accepted_rate'])/float(r['injected_rate']))
groups={}
summary=[]
for top in TOPS:
    for traffic in ['uniform','hotspotmix']:
        for rate in RATES:
            rs=[r for r in raw if r['topology']==top and r['traffic']==traffic and float(r['injection_rate'])==rate]
            assert sorted(int(r['seed']) for r in rs)==[101,202,303,404,505]
            good=[r for r in rs if completed(r)]
            row=dict(topology=top,traffic=traffic,injection_rate=rate,n_runs=len(rs),n_completed=len(good),n_threshold_exit=len(rs)-len(good))
            for field in ['latency','injected_rate','accepted_rate','accepted_over_injected']:
                vals=[float(r[field]) for r in good]
                mean,ci=stats(vals) if vals else ('','')
                row['mean_'+field]=mean;row['ci95_'+field]=ci
            summary.append(row);groups[(top,traffic,rate)]=row
save_csv('recomputed_main_summary.csv',summary)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'pdf.fonttype':42,'ps.fonttype':42})
fig,axs=plt.subplots(1,3,figsize=(8.5,3.5),sharey=True)
for ax,top in zip(axs,TOPS):
    for traffic,color,marker,label in [('uniform',COLORS[0],'o','Uniform'),('hotspotmix',COLORS[1],'s','20% hotspot')]:
        ss=[groups[top,traffic,r] for r in RATES]
        vals=[s['mean_latency'] if s['n_completed']==5 else np.nan for s in ss]
        cis=[s['ci95_latency'] if s['n_completed']==5 else np.nan for s in ss]
        ax.errorbar(RATES,vals,yerr=cis,color=color,marker=marker,ms=4,capsize=3,lw=1.25,label=label)
    exit_rates=[r for r in RATES if groups[top,'hotspotmix',r]['n_completed']==0]
    ax.axhspan(120,145,color='#f5f5f5',zorder=.1)
    ax.axhline(120,color='#bbbbbb',lw=.8,zorder=1)
    ax.plot(exit_rates,[133]*len(exit_rates),linestyle='none',marker='x',color=COLORS[1],ms=7,mew=1.5,zorder=5)
    load_axis(ax);ax.set_title(NAMES[top]);ax.set_ylim(0,145)
    ax.text(.5,.94,'Threshold exit',transform=ax.transAxes,ha='center',fontsize=8,color='#666666')
axs[0].set_ylabel('Mean packet latency (cycles)')
axs[0].legend(loc='upper left',frameon=False,fontsize=8)
foot(fig,'Bars: 95% t intervals across five seeds. Crosses in the top band mark 0/5 completed hotspot conditions and are not latency values. Gray: offered hotspot load exceeds unit-rate ejection.')
fig.tight_layout();save(fig,'main_latency')

fig,axs=plt.subplots(1,3,figsize=(8.5,3.5),sharey=True)
for ax,top in zip(axs,TOPS):
    for traffic,color,marker,label in [('uniform',COLORS[0],'o','Uniform'),('hotspotmix',COLORS[1],'s','20% hotspot')]:
        ss=[groups[top,traffic,r] for r in RATES]
        vals=[s['mean_accepted_over_injected'] if s['n_completed']==5 else np.nan for s in ss]
        cis=[s['ci95_accepted_over_injected'] if s['n_completed']==5 else np.nan for s in ss]
        ax.errorbar(RATES,vals,yerr=cis,color=color,marker=marker,ms=4,capsize=3,lw=1.25,label=label)
    ax.axhline(1,color='#555555',lw=.7,ls='--');load_axis(ax);ax.set_title(NAMES[top])
axs[0].set_ylabel('Accepted / injected flit rate')
axs[0].legend(loc='lower left',frameon=False,fontsize=8)
foot(fig,'Finite-window rate ratio; values above one can occur. This is not a packet-loss probability or a stability test.')
fig.tight_layout();save(fig,'rate_ratio')

ldfs=[]
fig,ax=plt.subplots(figsize=(7.5,3.3))
for top,color,marker in zip(TOPS,COLORS,['o','s','^']):
    ys=[]
    for r in RATES:
        u,h=groups[top,'uniform',r],groups[top,'hotspotmix',r]
        val=h['mean_latency']/u['mean_latency'] if h['n_completed']==u['n_completed']==5 else np.nan
        ys.append(val)
        ldfs.append(dict(topology=top,injection_rate=r,ldf_ratio_of_means=val if np.isfinite(val) else '',n_uniform=u['n_completed'],n_hotspot=h['n_completed']))
    ax.plot(RATES,ys,color=color,marker=marker,ms=5,label=NAMES[top])
load_axis(ax);ax.axhline(1,color='#555555',lw=.7,ls='--');ax.set_ylabel('LDF (ratio of mean latencies)');ax.legend(frameon=False,ncol=3,loc='upper left')
foot(fig,'LDF uses five-seed means; no confidence interval for this ratio is claimed. Gray region is beyond the destination offered-load bound.')
fig.tight_layout();save(fig,'main_ldf');save_csv('recomputed_ldf.csv',ldfs)

pilot=read('position_raw_runs.csv')
assert len(pilot)==54
ps=[]
fig,axs=plt.subplots(1,3,figsize=(8.5,3.6),sharey=True)
for ax,top in zip(axs,TOPS):
    for node,color,marker in zip([0,3,27],COLORS,['o','s','^']):
        ys=[];cis=[]
        for rate in [.06,.075,.08]:
            if node==0:
                rs=[r for r in raw if r['topology']==top and r['traffic']=='hotspotmix' and float(r['injection_rate'])==rate and int(r['seed']) in [101,202,303]]
                vals=[float(r['latency']) for r in rs if completed(r)]
            else:
                rs=[r for r in pilot if r['topology']==top and int(r['hotspot_node'])==node and float(r['injection_rate'])==rate]
                vals=[float(r['latency_cycles']) for r in rs if completed(r)]
            assert len(rs)==3
            mean,ci=stats(vals) if len(vals)==3 else (np.nan,np.nan)
            ys.append(mean);cis.append(ci)
            ps.append(dict(topology=top,hotspot_node=node,injection_rate=rate,n_completed=len(vals),n_attempted=3,mean_latency=mean if np.isfinite(mean) else '',ci95_latency=ci if np.isfinite(ci) else ''))
            if len(vals)<3:
                offset={0:-.0007,3:0,27:.0007}[node]
                ax.plot(rate+offset,225,marker='x',color=color,ms=7,mew=1.5)
        ax.errorbar([.06,.075,.08],ys,yerr=cis,label=f'Node {node}',color=color,marker=marker,ms=4,capsize=3,lw=1.1)
    load_axis(ax,[.06,.075,.08]);ax.set_title(NAMES[top]);ax.set_ylim(-12,245)
    ax.axhspan(212,245,color='#f5f5f5',zorder=0)
    ax.axhline(212,color='#bbbbbb',lw=.8)
    ax.text(.5,.94,'Exit status',transform=ax.transAxes,ha='center',fontsize=8,color='#666666')
axs[0].set_ylabel('Mean packet latency (cycles)')
axs[0].legend(frameon=False,fontsize=8,loc='upper left')
foot(fig,'Exploratory pilot, three matched seeds. Bars: 95% t intervals. Crosses at the plot top denote threshold exits, not latency values.')
fig.tight_layout();save(fig,'position_pilot');save_csv('recomputed_position_summary.csv',ps)

print(json.dumps({'main_runs':len(raw),'main_completed':sum(completed(r) for r in raw),'pilot_new_runs':len(pilot),'pilot_completed':sum(completed(r) for r in pilot),'bound':BOUND,'figures':4,'output_directory':str(OUT)},indent=2))
