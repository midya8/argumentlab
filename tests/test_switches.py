import copy,itertools,json,pathlib,random,subprocess,sys,tempfile,unittest
from argumentlab import audit
from argumentlab.switches import sensitivity,framework_at,parse,validate,SEMANTICS,MODES
from test_core import independent

def case(n,edges,switches,semantics='preferred',mode='credulous',argument=0,value=True):
    return {'framework':{'arguments':n,'attacks':edges},'switches':switches,'query':{'semantics':semantics,'mode':mode,'argument':None if mode=='exists' else argument,'value':value}}

class Switches(unittest.TestCase):
    def check(self,p):
        before=copy.deepcopy(p);r=sensitivity(p);self.assertEqual(p,before);norm=r['input'];k=len(norm['switches']);q=norm['query'];base={tuple(e) for e in norm['framework']['attacks']};success=[]
        for row in r['configurations']:
            m=row['mask'];changed={tuple(e) for i,e in enumerate(norm['switches']) if m>>i&1};es=base.symmetric_difference(changed);graph={'arguments':p['framework']['arguments'],'attacks':[list(e) for e in sorted(es)]};self.assertEqual(row['framework'],graph);self.assertEqual(row['flips'],len(changed));self.assertEqual({tuple(e) for e in row['added_attacks']},changed-base);self.assertEqual({tuple(e) for e in row['removed_attacks']},base&changed)
            fam=independent(graph);self.assertEqual(row['all_extension_families'],fam);chosen=fam[q['semantics']];yes=[s for s in chosen if q['argument'] is not None and s>>q['argument']&1];no=[s for s in chosen if s not in yes];answer=bool(chosen) if q['mode']=='exists' else bool(yes) if q['mode']=='credulous' else not no if q['mode']=='skeptical_classical' else (not no if chosen else None);self.assertIs(row['answer'],answer);self.assertIs(row['matches'],answer is q['value']);
            if row['matches']:success.append(m)
            for s in row['subset_classification']:
                for name in SEMANTICS:self.assertIs(s[name],s['mask'] in fam[name])
            native=audit(graph);self.assertEqual(row['family'],next(f for f in native['families'] if f['name']==q['semantics']))
            self.assertEqual(row['subset_classification'],[{'mask':s['mask'],'defended_mask':s['defended_mask'],'range_mask':s['range_mask'],**{name:s['mask'] in fam[name] for name in SEMANTICS}} for s in native['subsets']])
        self.assertEqual(r['successful_configurations'],success);minimum=min((m.bit_count() for m in success),default=None);self.assertEqual(r['minimum_flips'],minimum);self.assertEqual(r['minimum_cardinality_configurations'],[m for m in success if m.bit_count()==minimum]);minimal=[m for m in success if not any(s!=m and s&m==s for s in success)];self.assertEqual(r['inclusion_minimal_configurations'],minimal)
        self.assertEqual(r['checks']['hypercube_edges'],k*2**(k-1) if k else 0);seen=set()
        for t in r['transitions']:
            a,b=t['from_mask'],t['to_mask'];self.assertEqual(a^(1<<t['switch_index']),b);self.assertFalse(a>>t['switch_index']&1);self.assertNotIn((a,b),seen);seen.add((a,b));x,y=r['configurations'][a],r['configurations'][b];self.assertEqual(t['extensions_gained'],sorted(set(y['family']['extensions'])-set(x['family']['extensions'])));self.assertEqual(t['extensions_lost'],sorted(set(x['family']['extensions'])-set(y['family']['extensions'])));self.assertEqual(t['answer_changed'],x['answer']!=y['answer'])
        self.assertEqual(sorted(m for l in r['layers'] for m in l['configurations']),list(range(1<<k)))
        for row in r['configurations']:self.assertEqual(row['proper_successful_subconfigurations'],[s for s in success if s!=row['mask'] and s&row['mask']==s])
        return r
    def test_every_two_argument_base_graph_and_switch_set(self):
        es=list(itertools.product(range(2),repeat=2))
        for a in range(16):
            for b in range(16):self.check(case(2,[list(e) for i,e in enumerate(es) if a>>i&1],[list(e) for i,e in enumerate(es) if b>>i&1],'grounded'))
    def test_all_semantics_modes_and_both_targets(self):
        for sem in SEMANTICS:
            for mode in MODES:
                for value in [False,True]:self.check(case(2,[[0,0]],[[0,0],[0,1],[1,0]],sem,mode,1,value))
    def test_seeded_80_larger_switch_systems(self):
        rng=random.Random(20071)
        for i in range(80):
            n=rng.randrange(3,6);es=list(itertools.product(range(n),repeat=2));edges=[list(e) for e in es if rng.random()<.24];switches=[list(e) for e in rng.sample(es,rng.randrange(1,5))];self.check(case(n,edges,switches,SEMANTICS[i%9],MODES[i%4],rng.randrange(n),bool(i%2)))
    def test_classical_vacuity_is_not_nonvacuous_success(self):
        for value in [True,False]:
            r=self.check(case(1,[[0,0]],[],'stable','skeptical_nonvacuous',0,value));self.assertIsNone(r['baseline_answer']);self.assertFalse(r['success_exists']);self.assertIsNone(r['minimum_flips'])
        r=self.check(case(1,[[0,0]],[],'stable','skeptical_classical'));self.assertEqual(r['minimum_cardinality_configurations'],[0])
    def test_empty_framework_exists_only(self):
        for sem in SEMANTICS:self.assertEqual(self.check(case(0,[],[],sem,'exists'))['successful_configurations'],[0])
    def test_all_tied_one_flip_stable_repairs(self):
        es=[[0,1],[1,2],[2,0]];r=self.check(case(3,es,es,'stable','exists'));self.assertEqual(r['minimum_cardinality_configurations'],[1,2,4])
    def test_six_argument_six_switch_limit(self):self.check(case(6,[[a,a] for a in range(6)],[[a,a] for a in range(6)],'grounded','skeptical_nonvacuous',0))
    def test_validation(self):
        p=case(2,[],[]);bad=[None,{},dict(p,extra=1),dict(p,switches=[[0,0],[0,0]]),dict(p,switches=[[0,2]]),dict(p,switches=[[True,0]]),dict(p,framework={'arguments':7,'attacks':[]}),dict(p,switches=[[a,b] for a in range(2) for b in range(2)]*2)]
        for key,value in [('semantics','ideal'),('mode','unknown'),('argument',True),('argument',2),('value',1)]:bad.append(dict(p,query=dict(p['query'],**{key:value})))
        bad.append(dict(p,query=dict(p['query'],mode='exists',argument=0)))
        for x in bad:
            with self.assertRaises(ValueError):validate(x)
    def test_sorted_order_and_no_mutation(self):
        p=case(3,[[2,0],[0,1]],[[2,0],[0,2],[1,1]]);q=copy.deepcopy(p);q['switches'].reverse();q['framework']['attacks'].reverse();self.assertEqual(self.check(p),self.check(q))
    def test_parse_and_masks(self):
        with self.assertRaises(ValueError):parse(' '*65537)
        with self.assertRaises(ValueError):parse('{"framework":{},"framework":{},"switches":[],"query":{}}')
        for mask in [-1,True,1,1.0]:
            with self.assertRaises(ValueError):framework_at(case(1,[],[]),mask)
    def test_cli_selected_full_witness(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'input.json';raw=case(2,[[0,1]],[[0,1],[1,0]]);p.write_text(json.dumps(raw));z=subprocess.run([sys.executable,'-m','argumentlab.switches',str(p),'--configuration-mask','3'],capture_output=True,text=True,check=True);r=json.loads(z.stdout);self.assertEqual(r['sensitivity'],sensitivity(raw));self.assertEqual(r['selected_framework_audit'],audit(framework_at(raw,3)))
    def test_cli_invalid_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'in.json';out=pathlib.Path(d)/'out.json';p.write_text('{}');out.write_text('unchanged');r=subprocess.run([sys.executable,'-m','argumentlab.switches',str(p),'--output',str(out)],capture_output=True);self.assertEqual(r.returncode,2);self.assertEqual(out.read_text(),'unchanged')
    def test_retained_controls_replay_and_strict_contrasts(self):
        rows=json.loads((pathlib.Path(__file__).resolve().parents[1]/'docs/switch-audits.json').read_text())
        for row in rows:self.assertEqual(self.check(row['input']),row['report'])
        r=rows[-2]['report'];self.assertTrue(any(m not in r['minimum_cardinality_configurations'] for m in r['inclusion_minimal_configurations']))
        cs=rows[-1]['report']['configurations'];self.assertTrue(any(a['mask']!=b['mask'] and b['mask']!=c['mask'] and a['mask']&b['mask']==a['mask'] and b['mask']&c['mask']==b['mask'] and a['answer']==c['answer']!=b['answer'] for a in cs for b in cs for c in cs))
