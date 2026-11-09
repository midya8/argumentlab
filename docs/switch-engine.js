import {audit,validate as graphValidate} from './engine.js';
const SEMANTICS=['conflict_free','admissible','complete','naive','preferred','stable','semi_stable','stage','grounded'],MODES=['exists','credulous','skeptical_classical','skeptical_nonvacuous'];
const exact=(x,keys)=>x!==null&&typeof x==='object'&&!Array.isArray(x)&&JSON.stringify(Object.keys(x).sort())===JSON.stringify([...keys].sort());
const integer=(x,lo,hi)=>{if(!Number.isSafeInteger(x)||typeof x!=='number'||x<lo||x>hi)throw Error(`expected integer in [${lo},${hi}]`);return x;};
export function validate(raw){
 if(!exact(raw,['framework','switches','query']))throw Error('expected exactly framework, switches and query');
 const p=graphValidate(raw.framework),n=p.arguments;if(n>6)throw Error('sensitivity allows at most six arguments');
 if(!Array.isArray(raw.switches)||raw.switches.length>6)throw Error('at most six switch pairs');
 const pairs=graphValidate({arguments:n,attacks:raw.switches}).attacks,q=raw.query;
 if(!exact(q,['semantics','mode','argument','value'])||!SEMANTICS.includes(q.semantics)||!MODES.includes(q.mode)||typeof q.value!=='boolean')throw Error('invalid query');
 if(q.mode==='exists'){if(q.argument!==null)throw Error('exists query requires null argument');}else integer(q.argument,0,n-1);
 return {framework:p,switches:pairs,query:{...q}};
}
export function frameworkAt(raw,mask){
 const p=validate(raw);integer(mask,0,2**p.switches.length-1);const es=new Map(p.framework.attacks.map(e=>[e.join(','),e]));
 p.switches.forEach((e,i)=>{if(Math.floor(mask/2**i)%2){const key=e.join(',');if(es.has(key))es.delete(key);else es.set(key,e);}});
 return {arguments:p.framework.arguments,attacks:[...es.values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]).map(e=>[...e])};
}
const pop=m=>m.toString(2).split('1').length-1;
export function sensitivity(raw){
 const p=validate(raw),q=p.query,k=p.switches.length,base=new Set(p.framework.attacks.map(e=>e.join(','))),rows=[];
 for(let mask=0;mask<2**k;mask++){
  const graph=frameworkAt(p,mask),r=audit(graph),f=r.families.find(f=>f.name===q.semantics),answer=q.mode==='exists'?f.exists:f.acceptance[q.argument][q.mode],changed=p.switches.filter((_,i)=>Math.floor(mask/2**i)%2);
  rows.push({mask,flips:pop(mask),changed_pairs:changed.map(e=>[...e]),added_attacks:changed.filter(e=>!base.has(e.join(','))),removed_attacks:changed.filter(e=>base.has(e.join(','))),framework:graph,answer,matches:answer===q.value,family:f,all_extension_families:Object.fromEntries(r.families.map(f=>[f.name,f.extensions])),subset_classification:r.subsets.map(s=>({mask:s.mask,defended_mask:s.defended_mask,range_mask:s.range_mask,...Object.fromEntries(SEMANTICS.map(name=>[name,name==='grounded'?s.mask===r.contrasts.grounded_mask:s[name]]))}))});
 }
 const successes=rows.filter(r=>r.matches).map(r=>r.mask),minimum=successes.length?Math.min(...successes.map(m=>rows[m].flips)):null;
 for(const row of rows){row.proper_successful_subconfigurations=successes.filter(s=>s!==row.mask&&(s&row.mask)===s);row.inclusion_minimal_success=row.matches&&row.proper_successful_subconfigurations.length===0;row.minimum_cardinality_success=row.matches&&row.flips===minimum;}
 const transitions=[];
 for(const row of rows)for(let i=0;i<k;i++)if(Math.floor(row.mask/2**i)%2===0){
  const to=rows[row.mask+2**i],old=new Set(row.family.extensions),fresh=new Set(to.family.extensions);
  transitions.push({from_mask:row.mask,to_mask:to.mask,switch_index:i,pair:p.switches[i],operation:base.has(p.switches[i].join(','))?'remove':'add',from_answer:row.answer,to_answer:to.answer,answer_changed:row.answer!==to.answer,from_matches:row.matches,to_matches:to.matches,extensions_gained:[...fresh].filter(m=>!old.has(m)).sort((a,b)=>a-b),extensions_lost:[...old].filter(m=>!fresh.has(m)).sort((a,b)=>a-b)});
 }
 const layers=[];for(let d=0;d<=k;d++){const same=rows.filter(r=>r.flips===d);layers.push({flips:d,configurations:same.map(r=>r.mask),true_answers:same.filter(r=>r.answer===true).map(r=>r.mask),false_answers:same.filter(r=>r.answer===false).map(r=>r.mask),inapplicable_answers:same.filter(r=>r.answer===null).map(r=>r.mask),matching_configurations:same.filter(r=>r.matches).map(r=>r.mask)});}
 return {schema:'argumentlab-switches/1',input:p,baseline_answer:rows[0].answer,success_exists:successes.length>0,successful_configurations:successes,minimum_flips:minimum,minimum_cardinality_configurations:successes.filter(m=>rows[m].flips===minimum),inclusion_minimal_configurations:rows.filter(r=>r.inclusion_minimal_success).map(r=>r.mask),configurations:rows,transitions,layers,checks:{configurations:rows.length,hypercube_edges:transitions.length,classified_subsets:rows.reduce((s,r)=>s+r.subset_classification.length,0)}};
}
