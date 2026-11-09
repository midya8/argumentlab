import copy
import itertools
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import unittest
from argumentlab import audit, parse, validate


def independent(raw):
    n=raw['arguments']; A=set(range(n)); edges={tuple(e) for e in raw['attacks']}
    sets=[{a for a in A if mask>>a&1} for mask in range(1<<n)]
    def attacks(S): return {b for a,b in edges if a in S}
    def defended(S): return {a for a in A if all(c in attacks(S) for c,b in edges if b==a)}
    cf=[S for S in sets if not any(a in S and b in S for a,b in edges)]
    adm=[S for S in cf if S<=defended(S)]
    complete=[S for S in adm if S==defended(S)]
    maximal=lambda xs:[S for S in xs if not any(S<T for T in xs)]
    rng=lambda S:S|attacks(S)
    range_max=lambda xs:[S for S in xs if not any(rng(S)<rng(T) for T in xs)]
    f={'conflict_free':cf,'admissible':adm,'complete':complete,'naive':maximal(cf),'preferred':maximal(complete),'stable':[S for S in cf if rng(S)==A],'semi_stable':range_max(complete),'stage':range_max(cf),'grounded':[set.intersection(*complete)]}
    return {k:sorted(sum(1<<a for a in S) for S in v) for k,v in f.items()}


def ternary(raw):
    n=raw['arguments']; edges=raw['attacks']; valid=[]
    for L in itertools.product(['in','out','undec'],repeat=n):
        legal=True
        for a in range(n):
            ats=[L[b] for b,c in edges if c==a]
            if L[a]=='in': legal &= all(x=='out' for x in ats)
            elif L[a]=='out': legal &= 'in' in ats
            else: legal &= 'in' not in ats and 'undec' in ats
        if legal: valid.append((sum(1<<a for a in range(n) if L[a]=='in'),list(L)))
    return sorted(valid)


class Core(unittest.TestCase):
    def check(self,p,labels=True):
        before=copy.deepcopy(p);r=audit(p);self.assertEqual(p,before)
        families={f['name']:f['extensions'] for f in r['families']};self.assertEqual(families,independent(p))
        if labels:self.assertEqual([(x['extension_mask'],x['labels']) for x in r['complete_labellings']],ternary(p))
        n=p['arguments'];E={tuple(e) for e in p['attacks']};full=(1<<n)-1
        for row in r['subsets']:
            s=row['mask'];S={a for a in range(n) if s>>a&1}
            self.assertEqual(row['members'],sorted(S));self.assertEqual(row['conflicts'],[list(e) for e in sorted(E) if set(e)<=S])
            for d in row['defense']:
                a=d['argument'];ats=sorted(b for b,c in E if c==a);self.assertEqual(d['attackers'],ats)
                responses=[{'attacker':b,'defenders':sorted(c for c in S if (c,b) in E)} for b in ats]
                self.assertEqual(d['responses'],responses);bad=[z['attacker'] for z in responses if not z['defenders']]
                self.assertEqual(d['unanswered'],bad);self.assertEqual(d['defended'],not bad)
            for key,family in [('larger_admissible','admissible'),('larger_conflict_free','conflict_free')]:self.assertEqual(row[key],[t for t in families[family] if s!=t and s&t==s])
            for key,family in [('admissible_range_dominators','admissible'),('cf_range_dominators','conflict_free')]:
                R=row['range_mask'];self.assertEqual(row[key],[t for t in families[family] if R!=r['subsets'][t]['range_mask'] and R&r['subsets'][t]['range_mask']==R])
        for f in r['families']:
            for a in f['acceptance']:
                yes=[s for s in f['extensions'] if s>>a['argument']&1];no=[s for s in f['extensions'] if not s>>a['argument']&1]
                self.assertEqual(a['containing_extensions'],yes);self.assertEqual(a['excluding_extensions'],no);self.assertEqual(a['credulous'],bool(yes));self.assertEqual(a['skeptical_classical'],not no);self.assertEqual(a['skeptical_nonvacuous'],not no if f['exists'] else None)
                self.assertEqual(a['witness_extension'],yes[0] if yes else None);self.assertEqual(a['counterexample_extension'],no[0] if no else None)
        prev=0
        for step in r['grounded_trace']:
            self.assertEqual(step['mask'],prev);row=r['subsets'][prev];self.assertEqual(step['next_mask'],row['defended_mask']);self.assertEqual(step['defense'],row['defense']);prev=step['next_mask']
        self.assertTrue(r['grounded_trace'][-1]['fixed']);self.assertEqual(families['grounded'],[prev])
        return r
    def test_all_531_directed_frameworks_up_to_three_arguments(self):
        count=0
        for n in range(4):
            es=list(itertools.product(range(n),repeat=2))
            for bits in range(1<<len(es)):
                self.check({'arguments':n,'attacks':[list(e) for j,e in enumerate(es) if bits>>j&1]});count+=1
        self.assertEqual(count,531)
    def test_seeded_120_larger_graphs_and_ternary_oracle(self):
        rng=random.Random(8291)
        for _ in range(120):
            n=rng.randrange(4,7);self.check({'arguments':n,'attacks':[list(e) for e in itertools.product(range(n),repeat=2) if rng.random()<.27]})
    def test_empty_framework_has_one_empty_stable_extension(self):
        r=self.check({'arguments':0,'attacks':[]});self.assertTrue(all(f['exists'] and f['extensions']==[0] for f in r['families']))
    def test_self_attack_has_no_stable_extension(self):
        r=self.check({'arguments':1,'attacks':[[0,0]]});stable=next(f for f in r['families'] if f['name']=='stable');self.assertFalse(stable['exists']);self.assertTrue(stable['acceptance'][0]['skeptical_classical']);self.assertIsNone(stable['acceptance'][0]['skeptical_nonvacuous']);self.assertFalse(stable['acceptance'][0]['credulous'])
    def test_odd_cycle(self):self.check({'arguments':3,'attacks':[[0,1],[1,2],[2,0]]})
    def test_even_cycle(self):self.check({'arguments':4,'attacks':[[0,1],[1,2],[2,3],[3,0]]})
    def test_chain_grounded_trace(self):
        r=self.check({'arguments':7,'attacks':[[i,i+1] for i in range(6)]});self.assertEqual([s['mask'] for s in r['grounded_trace']],[0,1,5,21,85]);self.assertEqual(r['grounded_trace'][-1]['next_mask'],85)
    def test_maximum_eight_unattacked(self):
        r=self.check({'arguments':8,'attacks':[]});self.assertEqual(r['contrasts']['grounded_mask'],255)
    def test_all_eight_self_attacks(self):self.check({'arguments':8,'attacks':[[i,i] for i in range(8)]})
    def test_edge_order_invariance(self):
        p={'arguments':4,'attacks':[[0,2],[2,1],[1,0],[3,3]]};q=copy.deepcopy(p);q['attacks'].reverse();self.assertEqual(audit(p),audit(q))
    def test_strict_input_validation(self):
        bad=[None,{}, {'arguments':True,'attacks':[]},{'arguments':9,'attacks':[]},{'arguments':1,'attacks':[[0,1]]},{'arguments':1,'attacks':[[0,0],[0,0]]},{'arguments':1,'attacks':[[False,0]]},{'arguments':0,'attacks':[[0,0]]},{'arguments':1.0,'attacks':[]},{'arguments':1,'attacks':[],'extra':1}]
        for p in bad:
            with self.assertRaises(ValueError):validate(p)
    def test_duplicate_json_keys_and_byte_limit(self):
        with self.assertRaises(ValueError):parse('{"arguments":0,"arguments":1,"attacks":[]}')
        with self.assertRaises(ValueError):parse(' '*65537)
    def test_preferred_inclusion_not_maximum_cardinality(self):
        r=self.check({'arguments':3,'attacks':[[1,0],[1,2],[2,1]]});self.assertEqual(r['contrasts']['preferred_not_maximum_cardinality'],[2]);self.assertEqual(r['contrasts']['maximum_cardinality_admissible'],[5])
    def test_grounded_not_preferred_intersection(self):
        r=self.check({'arguments':2,'attacks':[[0,0],[0,1],[1,0]]});self.assertEqual(r['contrasts']['grounded_mask'],0);self.assertEqual(r['contrasts']['preferred_intersection_mask'],2)
    def test_preferred_intersection_can_fail_admissibility(self):
        r=self.check({'arguments':4,'attacks':[[0,1],[0,3],[1,0],[1,3],[3,2],[3,3]]});self.assertFalse(r['contrasts']['preferred_intersection_is_admissible']);self.assertEqual(r['contrasts']['preferred_intersection_mask'],4)
    def test_relabel_argument_permutation(self):
        p={'arguments':4,'attacks':[[0,1],[1,0],[1,2],[2,3],[3,2],[2,2]]};perm=[2,0,3,1];q={'arguments':4,'attacks':[[perm[a],perm[b]] for a,b in p['attacks']]};a=self.check(p);b=self.check(q)
        remap=lambda m:sum(1<<perm[i] for i in range(4) if m>>i&1)
        for x,y in zip(a['families'],b['families']):self.assertEqual(sorted(map(remap,x['extensions'])),y['extensions'])
    def test_no_mutation(self):
        p={'arguments':3,'attacks':[[2,0],[0,1]]};q=copy.deepcopy(p);audit(p);self.assertEqual(p,q)
    def test_cli_invalid_output_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            ip=pathlib.Path(d)/'in.json';op=pathlib.Path(d)/'out.json';ip.write_text('{"arguments":true,"attacks":[]}');op.write_text('unchanged');p=subprocess.run([sys.executable,'-m','argumentlab',str(ip),'--output',str(op)],capture_output=True,text=True);self.assertEqual(p.returncode,2);self.assertEqual(op.read_text(),'unchanged')
    def test_cli_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'in.json';p.write_text('{"arguments":2,"attacks":[[0,1],[1,0]]}');x=subprocess.run([sys.executable,'-m','argumentlab',str(p)],capture_output=True,text=True,check=True);self.assertEqual(json.loads(x.stdout),audit(json.loads(p.read_text())))

if __name__=='__main__':unittest.main()
