"""Optional seeded exact-cover restarts for the two large near-Skolem certificates.
Budget exhaustion is not a nonexistence result. Normal reproduction uses shipped certificates.
"""
import random,time,json
from pathlib import Path

def gen(k,u):
 q=2*u; n=2*k-2; ds=[h for h in range(k,0,-1) if h!=q]; rows=[]; masks=[]; cols=[0]*(n+len(ds))
 for j,h in enumerate(ds):
  for a in range(n-h):
   b=a+h; mask=(1<<a)|(1<<b)|(1<<(n+j)); bit=1<<len(rows); rows.append((h,a+1,b+1)); masks.append(mask)
   for i in (a,b,n+j):cols[i]|=bit
 conflicts=[]
 for mask in masks:
  s=mask; v=0
  while s:
   b=s&-s;s-=b;v|=cols[b.bit_length()-1]
  conflicts.append(v)
 rng=random.Random(20261125+k); start=time.time()
 for trial in range(2000):
  budget=3000; dead=set()
  def dfs(uncovered,active):
   nonlocal budget
   if not uncovered:return ()
   if uncovered in dead or budget<=0:return None
   budget-=1
   s=uncovered; best=len(rows)+1; choices=0
   while s:
    b=s&-s;s-=b;c=cols[b.bit_length()-1]&active;count=c.bit_count()
    if count<best:best=count;choices=c
    if not count:return None
   opts=[]
   while choices:
    b=choices&-choices;choices-=b;opts.append(b.bit_length()-1)
   rng.shuffle(opts)
   for i in opts:
    if budget<=0:return None
    tail=dfs(uncovered^masks[i],active&~conflicts[i])
    if tail is not None:return (rows[i],)+tail
   dead.add(uncovered);return None
  r=dfs((1<<len(cols))-1,(1<<len(rows))-1)
  if r is not None:
   print('solved',k,u,trial,time.time()-start,flush=True); L=2*k+2*u-1; p={h:(a+u,b+u) for h,a,b in r};p[q]=(L-u,u);return p
  if trial%100==0:print('trial',k,trial,time.time()-start,flush=True)
 raise RuntimeError('budget exhausted')
if __name__ == '__main__':
 root=Path(__file__).resolve().parents[1]/'data/certificates'
 for k,u in [(30,9),(42,13)]:
  p=gen(k,u); (root/f'proof_k{k}_u{u}.json').write_text(json.dumps({'K':k,'u':u,'pairs':[{'h':h,'a':a,'b':b} for h,(a,b) in sorted(p.items())]},indent=2)+'\n')
