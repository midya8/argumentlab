"""Exact sensitivity to a bounded supplied set of hypothetical attack switches."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .core import audit, integer, validate as graph_validate

SEMANTICS = ['conflict_free','admissible','complete','naive','preferred','stable','semi_stable','stage','grounded']
MODES = ['exists','credulous','skeptical_classical','skeptical_nonvacuous']

def validate(raw):
    if type(raw) is not dict or set(raw) != {'framework','switches','query'}:
        raise ValueError('expected exactly framework, switches and query')
    p=graph_validate(raw['framework']);n=p['arguments']
    if n>6:raise ValueError('sensitivity allows at most six arguments')
    es=raw['switches']
    if type(es) is not list or len(es)>6:raise ValueError('at most six switch pairs')
    pairs=graph_validate({'arguments':n,'attacks':es})['attacks']
    q=raw['query']
    if type(q) is not dict or set(q)!={'semantics','mode','argument','value'}:raise ValueError('invalid query fields')
    if q['semantics'] not in SEMANTICS or q['mode'] not in MODES:raise ValueError('unknown semantics or query mode')
    if type(q['value']) is not bool:raise ValueError('query value must be boolean')
    a=q['argument']
    if q['mode']=='exists':
        if a is not None:raise ValueError('exists query requires null argument')
    else:integer(a,0,n-1)
    return {'framework':p,'switches':pairs,'query':dict(q)}

def parse(text):
    if len(text.encode('utf8'))>65536:raise ValueError('input exceeds 65536 UTF-8 bytes')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate JSON key')
            d[k]=v
        return d
    return validate(json.loads(text,object_pairs_hook=pairs))

def framework_at(raw,mask):
    p=validate(raw);integer(mask,0,(1<<len(p['switches']))-1)
    es={tuple(e) for e in p['framework']['attacks']}
    for i,e in enumerate(p['switches']):
        if mask>>i&1:
            t=tuple(e)
            if t in es:es.remove(t)
            else:es.add(t)
    return {'arguments':p['framework']['arguments'],'attacks':[list(e) for e in sorted(es)]}

def sensitivity(raw):
    p=validate(raw);k=len(p['switches']);q=p['query'];base={tuple(e) for e in p['framework']['attacks']};rows=[]
    for mask in range(1<<k):
        graph=framework_at(p,mask);r=audit(graph);f=next(f for f in r['families'] if f['name']==q['semantics']);answer=f['exists'] if q['mode']=='exists' else f['acceptance'][q['argument']][q['mode']]
        changed=[p['switches'][i] for i in range(k) if mask>>i&1]
        rows.append({'mask':mask,'flips':mask.bit_count(),'changed_pairs':changed,'added_attacks':[e for e in changed if tuple(e) not in base],'removed_attacks':[e for e in changed if tuple(e) in base],'framework':graph,'answer':answer,'matches':answer is q['value'],'family':f,'all_extension_families':{f['name']:f['extensions'] for f in r['families']},'subset_classification':[{'mask':s['mask'],'defended_mask':s['defended_mask'],'range_mask':s['range_mask'],**{name:(s['mask']==r['contrasts']['grounded_mask'] if name=='grounded' else s[name]) for name in SEMANTICS}} for s in r['subsets']]})
    successes=[r['mask'] for r in rows if r['matches']]
    minimum=min((rows[m]['flips'] for m in successes),default=None)
    for row in rows:
        m=row['mask'];row['proper_successful_subconfigurations']=[s for s in successes if s!=m and s&m==s]
        row['inclusion_minimal_success']=row['matches'] and not row['proper_successful_subconfigurations']
        row['minimum_cardinality_success']=row['matches'] and row['flips']==minimum
    transitions=[]
    for row in rows:
        for i in range(k):
            if row['mask']>>i&1:continue
            to=rows[row['mask']|(1<<i)];old=set(row['family']['extensions']);new=set(to['family']['extensions'])
            transitions.append({'from_mask':row['mask'],'to_mask':to['mask'],'switch_index':i,'pair':p['switches'][i],'operation':'remove' if tuple(p['switches'][i]) in base else 'add','from_answer':row['answer'],'to_answer':to['answer'],'answer_changed':row['answer']!=to['answer'],'from_matches':row['matches'],'to_matches':to['matches'],'extensions_gained':sorted(new-old),'extensions_lost':sorted(old-new)})
    layers=[]
    for d in range(k+1):
        same=[r for r in rows if r['flips']==d]
        layers.append({'flips':d,'configurations':[r['mask'] for r in same],'true_answers':[r['mask'] for r in same if r['answer'] is True],'false_answers':[r['mask'] for r in same if r['answer'] is False],'inapplicable_answers':[r['mask'] for r in same if r['answer'] is None],'matching_configurations':[r['mask'] for r in same if r['matches']]})
    return {'schema':'argumentlab-switches/1','input':p,'baseline_answer':rows[0]['answer'],'success_exists':bool(successes),'successful_configurations':successes,'minimum_flips':minimum,'minimum_cardinality_configurations':[m for m in successes if rows[m]['flips']==minimum],'inclusion_minimal_configurations':[r['mask'] for r in rows if r['inclusion_minimal_success']],'configurations':rows,'transitions':transitions,'layers':layers,'checks':{'configurations':len(rows),'hypercube_edges':len(transitions),'classified_subsets':sum(len(r['subset_classification']) for r in rows)}}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input');ap.add_argument('--output');ap.add_argument('--configuration-mask',type=int);args=ap.parse_args()
    try:
        p=parse(Path(args.input).read_text());r=sensitivity(p)
        if args.configuration_mask is not None:r={'sensitivity':r,'selected_framework_audit':audit(framework_at(p,args.configuration_mask))}
        text=json.dumps(r,indent=2)+'\n'
        if args.output:Path(args.output).write_text(text)
        else:print(text,end='')
    except (ValueError,OSError) as exc:ap.exit(2,f'Invalid input: {exc}\n')

if __name__=='__main__':main()
