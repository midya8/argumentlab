// Independent set-based finite extension enumeration. No native report is used.
const names=['conflict_free','admissible','complete','naive','preferred','stable','semi_stable','stage','grounded'];
const equal=(a,b)=>a.size===b.size&&[...a].every(x=>b.has(x));
const sub=(a,b)=>[...a].every(x=>b.has(x));
const strict=(a,b)=>a.size<b.size&&sub(a,b);
const sorted=s=>[...s].sort((a,b)=>a-b);
const mask=s=>[...s].reduce((m,a)=>m+2**a,0);
export function validate(raw){
 if(raw===null||typeof raw!=='object'||Array.isArray(raw)||Object.keys(raw).sort().join(',')!=='arguments,attacks')throw Error('expected exactly arguments and attacks');
 const n=raw.arguments;
 if(!Number.isSafeInteger(n)||n<0||n>8)throw Error('expected 0-8 arguments');
 if(!Array.isArray(raw.attacks)||raw.attacks.length>n*n)throw Error('at most n*n attack pairs');
 const seen=new Set(),edges=raw.attacks.map(e=>{if(!Array.isArray(e)||e.length!==2||e.some(a=>!Number.isSafeInteger(a)||a<0||a>=n))throw Error('invalid attack pair');const key=e.join(',');if(seen.has(key))throw Error('duplicate attack');seen.add(key);return [...e];}).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
 return {arguments:n,attacks:edges};
}
export function audit(raw){
 const p=validate(raw),n=p.arguments,edges=p.attacks,A=new Set(Array.from({length:n},(_,a)=>a)),full=2**n-1;
 const outgoing=Array.from({length:n},()=>new Set());for(const [a,b] of edges)outgoing[a].add(b);
 const incoming=Array.from({length:n},(_,a)=>edges.filter(e=>e[1]===a).map(e=>e[0]));
 const all=Array.from({length:2**n},(_,m)=>new Set([...A].filter(a=>Math.floor(m/2**a)%2)));
 const attacked=S=>new Set([...S].flatMap(a=>[...outgoing[a]]));
 const data=all.map(S=>{const out=attacked(S),def=new Set([...A].filter(a=>incoming[a].every(b=>out.has(b)))),conflicts=edges.filter(([a,b])=>S.has(a)&&S.has(b)),cf=!conflicts.length,adm=cf&&sub(S,def);return {S,out,def,range:new Set([...S,...out]),cf,adm,com:adm&&equal(S,def),stable:cf&&new Set([...S,...out]).size===n,conflicts};});
 const cf=data.filter(x=>x.cf),adm=data.filter(x=>x.adm),com=data.filter(x=>x.com);
 const naive=cf.filter(x=>!cf.some(y=>strict(x.S,y.S))),preferred=adm.filter(x=>!adm.some(y=>strict(x.S,y.S))),semi=adm.filter(x=>!adm.some(y=>strict(x.range,y.range))),stage=cf.filter(x=>!cf.some(y=>strict(x.range,y.range)));
 const rows=data.map(d=>{
  const defense=[...A].map(a=>{const responses=incoming[a].map(b=>({attacker:b,defenders:sorted(new Set([...d.S].filter(c=>outgoing[c].has(b))))})),unanswered=responses.filter(r=>!r.defenders.length).map(r=>r.attacker);return {argument:a,attackers:[...incoming[a]],responses,unanswered,defended:unanswered.length===0};});
  return {mask:mask(d.S),members:sorted(d.S),attacked_mask:mask(d.out),range_mask:mask(d.range),defended_mask:mask(d.def),conflicts:d.conflicts.map(e=>[...e]),defense,conflict_free:d.cf,admissible:d.adm,complete:d.com,stable:d.stable,larger_conflict_free:cf.filter(x=>strict(d.S,x.S)).map(x=>mask(x.S)),larger_admissible:adm.filter(x=>strict(d.S,x.S)).map(x=>mask(x.S)),cf_range_dominators:cf.filter(x=>strict(d.range,x.range)).map(x=>mask(x.S)),admissible_range_dominators:adm.filter(x=>strict(d.range,x.range)).map(x=>mask(x.S)),naive:naive.includes(d),preferred:preferred.includes(d),semi_stable:semi.includes(d),stage:stage.includes(d)};
 });
 let current=new Set();const grounded_trace=[];
 for(;;){const r=rows[mask(current)],next=data[mask(current)].def;grounded_trace.push({step:grounded_trace.length,mask:mask(current),next_mask:mask(next),added_mask:mask(new Set([...next].filter(a=>!current.has(a)))),fixed:equal(current,next),defense:r.defense});if(equal(current,next))break;if(!sub(current,next))throw Error('grounded chain failed');current=next;}
 const grounded=mask(current),chosen={conflict_free:cf,admissible:adm,complete:com,naive,preferred,stable:data.filter(x=>x.stable),semi_stable:semi,stage,grounded:[data[grounded]]};
 const families=names.map(name=>{const extensions=chosen[name].map(x=>mask(x.S));let union=0,intersection=full;for(const t of extensions){union|=t;intersection&=t;}
  const acceptance=[...A].map(a=>{const containing_extensions=extensions.filter(t=>Math.floor(t/2**a)%2),excluding_extensions=extensions.filter(t=>!(Math.floor(t/2**a)%2));return {argument:a,credulous:containing_extensions.length>0,skeptical_classical:excluding_extensions.length===0,skeptical_nonvacuous:extensions.length?excluding_extensions.length===0:null,containing_extensions,excluding_extensions,witness_extension:containing_extensions[0]??null,counterexample_extension:excluding_extensions[0]??null};});
  return {name,extensions,exists:extensions.length>0,union_mask:union,intersection_classical_mask:intersection,intersection_nonvacuous_mask:extensions.length?intersection:null,acceptance};});
 const complete_labellings=com.map(d=>{const labels=[...A].map(a=>d.S.has(a)?'in':d.out.has(a)?'out':'undec'),legality=[...A].map(a=>{const in_attackers=incoming[a].filter(b=>labels[b]==='in'),undec_attackers=incoming[a].filter(b=>labels[b]==='undec'),expect=in_attackers.length?'out':undec_attackers.length?'undec':'in';if(labels[a]!==expect)throw Error('illegal complete label');return {argument:a,label:labels[a],attacker_labels:incoming[a].map(b=>[b,labels[b]]),in_attackers,undec_attackers,legal:true};});return {extension_mask:mask(d.S),in_mask:mask(d.S),out_mask:mask(d.out),undec_mask:mask(new Set([...A].filter(a=>!d.S.has(a)&&!d.out.has(a)))),labels,legality};});
 const inclusion=(aa,bb)=>chosen[aa].every(x=>chosen[bb].includes(x));
 if(!com.includes(data[grounded])||!com.every(x=>sub(current,x.S))||!inclusion('stable','semi_stable')||!inclusion('semi_stable','preferred')||!inclusion('preferred','complete')||!inclusion('complete','admissible')||!inclusion('admissible','conflict_free')||!inclusion('stable','stage')||!inclusion('stage','naive'))throw Error('semantic inclusion failed');
 let preferred_intersection=full;for(const d of preferred)preferred_intersection&=mask(d.S);const max=Math.max(...adm.map(d=>d.S.size));
 return {schema:'argumentlab/1',input:p,incoming,subsets:rows,families,grounded_trace,complete_labellings,contrasts:{grounded_mask:grounded,preferred_intersection_mask:preferred_intersection,preferred_intersection_is_admissible:rows[preferred_intersection].admissible,preferred_not_maximum_cardinality:preferred.filter(x=>x.S.size<max).map(x=>mask(x.S)),maximum_cardinality_admissible:adm.filter(x=>x.S.size===max).map(x=>mask(x.S))},checks:{subsets:rows.length,complete_labellings:complete_labellings.length,grounded_fixed_point:true,grounded_least_complete:true,family_inclusions:true,complete_labelling_legality:true}};
}
