#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITES=ROOT/"sites"; STATE=ROOT/".deploy"/"state"; CHECKPOINT=STATE/"checkpoint.json"

def run(args,env=None): print("$"," ".join(args),flush=True); return subprocess.run(args,cwd=ROOT,env=env or os.environ.copy(),check=True)
def site_url(c): return "https://"+c["domain"].rstrip("/") if c.get("domain") else f"https://{c.get('deploy',{}).get('project',c['id'])}.pages.dev"
def health(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"seo-site-monitor/1.0"}),timeout=20) as r: return {"ok":200<=r.status<400,"status":r.status,"url":url}
    except Exception as e: return {"ok":False,"url":url,"error":str(e)}
def save_checkpoint(site_ids,next_index,reason=None):
    STATE.mkdir(parents=True,exist_ok=True); data={"siteIds":site_ids,"nextIndex":next_index,"nextSite":site_ids[next_index] if next_index<len(site_ids) else None,"updatedAt":time.time()}
    if reason: data["reason"]=reason
    CHECKPOINT.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
def selected_sites(args):
    sites=sorted(p for p in SITES.iterdir() if (p/"site.json").exists())
    wanted=[]
    if args.site: wanted += args.site
    if args.sites: wanted += [x.strip() for x in args.sites.split(",") if x.strip()]
    if wanted:
        ids=set(wanted); missing=ids-{p.name for p in sites}
        if missing: raise SystemExit(f"Unknown site(s): {', '.join(sorted(missing))}")
        sites=[p for p in sites if p.name in ids]
    if args.limit: sites=sites[:args.limit]
    return sites

def main():
    ap=argparse.ArgumentParser(description="Generate, deploy, and monitor the SEO site portfolio")
    mode=ap.add_mutually_exclusive_group(); mode.add_argument("--frontend-only",action="store_true"); mode.add_argument("--blogs-only",action="store_true")
    ap.add_argument("--site",action="append",help="Process one site; repeat for multiple sites")
    ap.add_argument("--sites",help="Comma-separated subset of site IDs")
    ap.add_argument("--limit",type=int,default=0); ap.add_argument("--resume",action="store_true",help="Resume from the persisted Gemini checkpoint")
    ap.add_argument("--mock",action="store_true",help="Never call an LLM; use deterministic ideas/posts for testing")
    ap.add_argument("--skip-generation",action="store_true"); ap.add_argument("--provider",default="cloudflare-pages",choices=["cloudflare-pages","cloudflare-workers","vercel","netlify","static"]); args=ap.parse_args()
    env=os.environ.copy()
    if args.mock: env["MOCK_LLM"]="1"
    run([sys.executable,"scripts/ideas.py"],env=env)
    sites=selected_sites(args); ids=[p.name for p in sites]
    start=0
    if args.resume and CHECKPOINT.exists():
        cp=json.loads(CHECKPOINT.read_text(encoding="utf-8")); old_ids=cp.get("siteIds",[]); old_next=int(cp.get("nextIndex",0));
        if old_ids==ids: start=min(old_next,len(ids)); print(f"Resuming at {start+1}/{len(ids)}: {ids[start] if start<len(ids) else 'complete'}")
        else: print("Checkpoint site set differs from current subset; starting from the beginning of the selected subset.")
    print(f"Processing {len(sites)-start} sites",flush=True); STATE.mkdir(parents=True,exist_ok=True)
    shared_posthog={}
    if not args.mock:
        try:
            from monitoring import provision_shared_posthog; shared_posthog=provision_shared_posthog()
        except Exception as exc: print(f"PostHog provisioning skipped: {exc}")
    results=[]; force_generation=args.blogs_only and not args.skip_generation; skip_generation=args.frontend_only or args.skip_generation
    for index in range(start,len(sites)):
        site_dir=sites[index]; site_id=site_dir.name; save_checkpoint(ids,index); started=time.time(); result={"site":site_id,"startedAt":started}
        try:
            config=json.loads((site_dir/"site.json").read_text(encoding="utf-8")); config.setdefault("deploy",{})["provider"]=args.provider; target=site_url(config)
            from monitoring import provision; config=provision(config,site_dir,target,shared_posthog)
            posts_exist=bool(list((site_dir/"_posts").glob("*.md")))
            if not skip_generation and (force_generation or not posts_exist):
                cmd=[sys.executable,"scripts/generate_posts.py",site_id];
                if args.mock: cmd.append("--mock")
                run(cmd,env=env)
            env2=env.copy(); env2["SITE_URL"]=target; mon=config.get("monitoring",{}); env2["GOOGLE_SITE_VERIFICATION"]=mon.get("googleVerificationToken",""); env2["NEXT_PUBLIC_POSTHOG_KEY"]=mon.get("posthogKey",""); env2["NEXT_PUBLIC_POSTHOG_HOST"]=mon.get("posthogHost","https://us.i.posthog.com"); env2["SEO_POSTS_DIR"]=str((site_dir/"_posts").resolve())
            run(["npm","run","build"],env=env2)
            if args.provider!="static": run([sys.executable,"scripts/site.py","deploy",site_id,args.provider],env=env2)
            from monitoring import finalize; finalize(config); result.update({"ok":True,"url":target,"health":health(target)})
        except subprocess.CalledProcessError as exc:
            exhausted=(STATE/"gemini_exhausted.json").exists()
            result.update({"ok":False,"error":str(exc)}); (STATE/f"{site_id}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); results.append(result)
            if exhausted:
                save_checkpoint(ids,index,"Gemini fallback chain exhausted; resume here after credits/rate limits recover."); print(f"Gemini exhausted at idea/site {index+1}: {site_id}. Checkpoint saved. Re-run with --resume.",file=sys.stderr); raise SystemExit(2)
        except Exception as exc:
            result.update({"ok":False,"error":str(exc)})
        result["durationSeconds"]=round(time.time()-started,2); results.append(result); (STATE/f"{site_id}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); save_checkpoint(ids,index+1)
        print(f"[{index+1}/{len(sites)}] {site_id}: {'OK' if result['ok'] else 'FAILED'}",flush=True)
    summary={"timestamp":time.time(),"total":len(results),"successful":sum(r["ok"] for r in results),"failed":sum(not r["ok"] for r in results),"results":results}; (STATE/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8"); print(json.dumps({k:summary[k] for k in ("total","successful","failed")},indent=2))
    if summary["failed"]: raise SystemExit(1)
if __name__=="__main__": main()
