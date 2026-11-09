"""Original synthetic attack-switch controls, not a benchmark."""
import itertools,json,random
from pathlib import Path
from argumentlab.switches import sensitivity,SEMANTICS
ROOT=Path(__file__).resolve().parents[1]
def inp(n,es,sw,sem='preferred',mode='credulous',a=0,value=True):
    return {'framework':{'arguments':n,'attacks':es},'switches':sw,'query':{'semantics':sem,'mode':mode,'argument':None if mode=='exists' else a,'value':value}}
def controls():
    cycle=[[0,1],[1,2],[2,0]]
    rows=[('Three tied nearest stable-existence repairs',inp(3,cycle,cycle,'stable','exists')),
      ('Classical skeptical vacuity needs zero edits',inp(1,[[0,0]],[[0,0]],'stable','skeptical_classical')),
      ('Nonvacuous skeptical answer needs a real position',inp(1,[[0,0]],[[0,0]],'stable','skeptical_nonvacuous')),
      ('Null does not count as false',inp(1,[[0,0]],[],'stable','skeptical_nonvacuous',0,False)),
      ('Locked self attack makes positive goal impossible',inp(2,[[0,0]],[[1,1]],'preferred')),
      ('Empty framework has one stable extension',inp(0,[],[],'stable','exists')),
      ('No switches, goal already satisfied',inp(1,[],[],'grounded')),
      ('Six arguments, every self attack switchable',inp(6,[[a,a] for a in range(6)],[[a,a] for a in range(6)],'grounded','skeptical_nonvacuous')),
      ('Mixed additions and removals',inp(3,[[0,1],[1,0],[2,2]],[[0,1],[1,2],[2,0],[2,2]],'complete','credulous',2)),
      ('Negative credulous target retains every counterexample',inp(3,[[0,1],[1,0]],[[0,0],[0,1],[1,2]],'stable','credulous',0,False))]
    for sem in SEMANTICS:rows.append((sem+' exact family under switches',inp(3,[[0,1],[1,2]],[[0,1],[1,0],[2,0]],sem,'skeptical_nonvacuous',2)))
    rng=random.Random(71024);found={}
    for _ in range(2000):
        n=3;es=list(itertools.product(range(n),repeat=2));base=[list(e) for e in es if rng.random()<.25];sw=[list(e) for e in rng.sample(es,4)];p=inp(n,base,sw,'preferred','credulous',rng.randrange(n));r=sensitivity(p)
        if 'minimal' not in found and any(m not in r['minimum_cardinality_configurations'] for m in r['inclusion_minimal_configurations']):found['minimal']=('Inclusion-minimal is not minimum edit count',p)
        if 'nonmonotone' not in found:
            for a in r['configurations']:
                for b in r['configurations']:
                    for c in r['configurations']:
                        if a['mask']!=b['mask']!=c['mask'] and a['mask']&b['mask']==a['mask'] and b['mask']&c['mask']==b['mask'] and a['answer']==c['answer']!=b['answer']:
                            found['nonmonotone']=('More supplied switches can lose and regain acceptance',p);break
                    if 'nonmonotone' in found:break
                if 'nonmonotone' in found:break
        if len(found)==2:break
    assert len(found)==2
    return rows+[found['minimal'],found['nonmonotone']]
def main():
    rows=[{'name':name,'input':p,'report':sensitivity(p)} for name,p in controls()];(ROOT/'docs/switch-audits.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(ROOT/'examples/switches.json').write_text(json.dumps(rows[-2]['input'],indent=2)+'\n');print(json.dumps({'controls':len(rows),'configurations':sum(len(x['report']['configurations']) for x in rows),'transitions':sum(len(x['report']['transitions']) for x in rows),'classified_subsets':sum(x['report']['checks']['classified_subsets'] for x in rows),'bytes':(ROOT/'docs/switch-audits.json').stat().st_size,'strict_controls':rows[-2:][0]['input']}))
if __name__=='__main__':main()
