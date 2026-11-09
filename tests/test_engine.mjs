import test from 'node:test';import assert from 'node:assert/strict';import {audit} from '../docs/engine.js';import {execFileSync} from 'node:child_process';
test('all 531 finite directed frameworks match independent native implementation exactly',()=>{
 const python=`import json,itertools\nfrom argumentlab import audit\nrows=[]\nfor n in range(4):\n es=list(itertools.product(range(n),repeat=2))\n for s in range(1<<len(es)):\n  p={'arguments':n,'attacks':[list(e) for i,e in enumerate(es) if s>>i&1]};rows.append({'input':p,'report':audit(p)})\nprint(json.dumps(rows))`;
 const rows=JSON.parse(execFileSync(process.env.PYTHON||'python',['-c',python],{encoding:'utf8',maxBuffer:30*1024*1024}));assert.equal(rows.length,531);let leaves=0;const count=x=>{if(x===null||typeof x!=='object'){leaves++;return;}Object.values(x).forEach(count);};for(const r of rows){assert.deepEqual(audit(r.input),r.report);count(r.report);}console.log(JSON.stringify({frameworks:531,exactScalarLeaves:leaves}));
});

test('19 retained full reports match exactly including eight-argument limits',async()=>{
 const fs=await import('node:fs');const rows=JSON.parse(fs.readFileSync(new URL('../docs/audits.json',import.meta.url),'utf8'));assert.equal(rows.length,19);let leaves=0;const count=x=>{if(x===null||typeof x!=='object'){leaves++;return;}Object.values(x).forEach(count);};for(const row of rows){assert.deepEqual(audit(row.input),row.report);count(row.report);}console.log(JSON.stringify({retainedReports:rows.length,exactScalarLeaves:leaves}));
});
test('validation, graph order, no mutation and strict contrasts',()=>{
 for(const p of [null,{}, {arguments:true,attacks:[]},{arguments:9,attacks:[]},{arguments:1,attacks:[[0,1]]},{arguments:1,attacks:[[0,0],[0,0]]},{arguments:2,attacks:[[true,0]]},{arguments:0,attacks:[[0,0]]}])assert.throws(()=>audit(p));
 const p={arguments:3,attacks:[[1,0],[1,2],[2,1]]},before=structuredClone(p),r=audit(p);assert.deepEqual(p,before);assert.deepEqual(audit({...p,attacks:[...p.attacks].reverse()}),r);assert.deepEqual(r.contrasts.preferred_not_maximum_cardinality,[2]);assert.deepEqual(r.contrasts.maximum_cardinality_admissible,[5]);const s=audit({arguments:2,attacks:[[0,0],[0,1]]}).families;assert.deepEqual(s.find(f=>f.name==='stage').extensions,[2]);assert.deepEqual(s.find(f=>f.name==='semi_stable').extensions,[0]);
});
test('100 seeded larger graphs agree with independent full ternary complete/stable oracle',()=>{
 let seed=9217;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2**32;};
 for(let trial=0;trial<100;trial++){
  const n=4+Math.floor(rand()*3),attacks=[];for(let a=0;a<n;a++)for(let b=0;b<n;b++)if(rand()<.29)attacks.push([a,b]);const r=audit({arguments:n,attacks}),valid=[];
  for(let code=0;code<3**n;code++){let z=code;const labels=[];for(let a=0;a<n;a++){labels.push(z%3);z=Math.floor(z/3);}let ok=true;for(let a=0;a<n;a++){const incoming=attacks.filter(e=>e[1]===a).map(e=>labels[e[0]]);if(labels[a]===0)ok&&=incoming.every(x=>x===1);else if(labels[a]===1)ok&&=incoming.includes(0);else ok&&=!incoming.includes(0)&&incoming.includes(2);}if(ok)valid.push({mask:labels.reduce((m,l,a)=>m+(l===0?2**a:0),0),labels});}
  valid.sort((a,b)=>a.mask-b.mask);assert.deepEqual(r.complete_labellings.map(l=>l.extension_mask),valid.map(l=>l.mask));assert.deepEqual(r.families.find(f=>f.name==='stable').extensions,valid.filter(l=>!l.labels.includes(2)).map(l=>l.mask));
 }
});
