"""Original synthetic argumentation controls, not a benchmark."""
import json
from pathlib import Path
from argumentlab import audit
ROOT=Path(__file__).resolve().parents[1]
CONTROLS=[
 ('Empty framework, one empty extension',0,[]),
 ('Unattacked argument',1,[]),
 ('Four independent arguments',4,[]),
 ('One directed attack',2,[[0,1]]),
 ('Defense through a seven-argument chain',7,[[i,i+1] for i in range(6)]),
 ('Mutual attack, two positions',2,[[0,1],[1,0]]),
 ('Odd cycle without a stable extension',3,[[0,1],[1,2],[2,0]]),
 ('Even cycle with two stable extensions',4,[[0,1],[1,2],[2,3],[3,0]]),
 ('Self attack and vacuous classical skeptical acceptance',1,[[0,0]]),
 ('Self attack alongside an independent argument',2,[[0,0]]),
 ('Every pair attacks both directions',3,[[a,b] for a in range(3) for b in range(3) if a!=b]),
 ('Eight self-attacking arguments',8,[[a,a] for a in range(8)]),
 ('Dense eight-argument limit',8,[[a,b] for a in range(8) for b in range(8)]),
 ('Unattacked argument breaks a cycle',4,[[0,1],[1,2],[2,0],[3,0]]),
 ('Preferred inclusion maximal is not maximum cardinality',3,[[1,0],[1,2],[2,1]]),
 ('Preferred intersection can exceed grounded',2,[[0,0],[0,1],[1,0]]),
 ('Preferred intersection need not be admissible',4,[[0,1],[0,3],[1,0],[1,3],[3,2],[3,3]]),
 ('Stage range is not semi-stable range',2,[[0,0],[0,1]]),
 ('Two disconnected mutual pairs',4,[[0,1],[1,0],[2,3],[3,2]]),
]
def main():
 rows=[{'name':name,'input':{'arguments':n,'attacks':es},'report':audit({'arguments':n,'attacks':es})} for name,n,es in CONTROLS]
 (ROOT/'docs/audits.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 (ROOT/'examples/demo.json').write_text(json.dumps(rows[5]['input'],indent=2)+'\n')
 print(json.dumps({'controls':len(rows),'subsets':sum(len(x['report']['subsets']) for x in rows),'complete_labellings':sum(len(x['report']['complete_labellings']) for x in rows),'bytes':(ROOT/'docs/audits.json').stat().st_size}))
if __name__=='__main__':main()
