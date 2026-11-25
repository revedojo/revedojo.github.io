import json,sys,os
from seg import segments
pages={'reve':['index','results','shop','supporters','tokushoho'],'bst':['index']}
src={'reve':'/home/claude/site','bst':'/home/claude/bst_site'}
for site,ps in pages.items():
  for p in ps:
    t=open(f"{src[site]}/{p}.html",encoding='utf-8').read()
    seen=[]
    for s in segments(t):
      if s not in seen: seen.append(s)
    json.dump(seen,open(f"segs_{site}_{p}.json",'w'),ensure_ascii=False,indent=0)
    print(site,p,len(seen),sum(len(s) for s in seen))
