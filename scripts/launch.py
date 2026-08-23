#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITES=ROOT/"sites"; STATE=ROOT/".deploy"/"state"; LOGS=ROOT/".deploy"/"logs"; CHECKPOINT=STATE/"checkpoint.json"
def run(args,env=None,*,site_id=None,step=None):
    label=f"{site_id}/{step}" if site_id and step else (step or "command"); log_path=LOGS/(site_id or "global")/(f"{step}.log" if step else "command.log"); log_path.parent.mkdir(parents=True,exist_ok=True); command=" ".join(str(x) for x in args)
    print("\n"+"="*72,flush=True); print(f"STEP: {label}",flush=True); print(f"COMMAND: {command}",flush=True); print(f"LOG: {log_path.relative_to(ROOT)}",flush=True); print("="*72,flush=True)
    started=time.time(); child_env=env or os.environ.copy()
    with log_path.open("w",encoding="utf-8",errors="replace") as log:
        log.write(f"COMMAND: {command}\nSTARTED: {time.ctime()}\n\n")
        proc=subprocess.Popen(args,cwd=ROOT,env=child_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace",bufsize=1)
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line,end="",flush=True); log.write(line); log.flush()
        code=proc.wait(); duration=round(time.time()-started,2); log.write(f"\nEXIT CODE: {code}\nDURATION: {duration}s\n")
    print(f"\nEXIT CODE: {code} | DURATION: {duration}s",flush=True)
    if code:
        print(f"\n✗ {label.upper()} FAILED",file=sys.stderr,flush=True); print(f"  Exit code: {code}",file=sys.stderr,flush=True); print(f"  Full log: {log_path.relative_to(ROOT)}",file=sys.stderr,flush=True)
        raise subprocess.CalledProcessError(code,args)
    print(f"✓ {label.upper()} COMPLETED",flush=True); return subprocess.CompletedProcess(args,code)
def site_url(c): return "https://"+c["domain"].rstrip("/") if c.get("domain") else f"https://{c.get('deploy',{}).get('project',c['id'])}.pages.dev"
def health(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"seo-site-monitor/1.0"}),timeout=20) as r:return {"ok":200<=r.status<400,"status":r.status,"url":url}
    except Exception as e:return {"ok":False,"url":url,"error":str(e)}
def save_checkpoint(site_ids,next_index,reason=None,step=None):
    STATE.mkdir(parents=True,exist_ok=True); d={"siteIds":site_ids,"nextIndex":next_index,"nextSite":site_ids[next_index] if next_index<len(site_ids) else None,"updatedAt":time.time()}
    if reason:d["reason"]=reason
    if step:d["step"]=step
    CHECKPOINT.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
def selected_sites(args):
    sites=sorted(p for p in SITES.iterdir() if (p/"site.json").exists()); wanted=(args.site or [])+([x.strip() for x in args.sites.split(",") if x.strip()] if args.sites else [])
    if wanted:
        ids=set(wanted); missing=ids-{p.name for p in sites}
        if missing:raise SystemExit(f"Unknown site(s): {', '.join(sorted(missing))}")
        sites=[p for p in sites if p.name in ids]
    return sites[:args.limit] if args.limit else sites
def main():
    ap=argparse.ArgumentParser(description="Generate, deploy, and monitor the SEO site portfolio"); mode=ap.add_mutually_exclusive_group(); mode.add_argument("--frontend-only",action="store_true"); mode.add_argument("--blogs-only",action="store_true")
    ap.add_argument("--site",action="append"); ap.add_argument("--sites"); ap.add_argument("--limit",type=int,default=0); ap.add_argument("--resume",action="store_true"); ap.add_argument("--mock",action="store_true"); ap.add_argument("--skip-generation",action="store_true"); ap.add_argument("--provider",default="cloudflare-pages",choices=["cloudflare-pages","cloudflare-workers","vercel","netlify","static"]); args=ap.parse_args()
    env=os.environ.copy();
    if args.mock:env["MOCK_LLM"]="1"
    STATE.mkdir(parents=True,exist_ok=True); marker=STATE/"gemini_exhausted.json";
    if marker.exists() and not args.resume: marker.unlink()
    run([sys.executable,"scripts/ideas.py"],env=env,step="ideas"); sites=selected_sites(args); ids=[p.name for p in sites]; start=0
    if args.resume and CHECKPOINT.exists():
        cp=json.loads(CHECKPOINT.read_text(encoding="utf-8"));
        if cp.get("siteIds")==ids:start=min(int(cp.get("nextIndex",0)),len(ids)); print(f"Resuming at {start+1}/{len(ids)}: {ids[start] if start<len(ids) else 'complete'}")
        else:print("Checkpoint site set differs from current subset; starting from selected subset beginning.")
    if not ids: raise SystemExit("No sites selected. Add sites/<id>/site.json or adjust --site/--sites/--limit.")
    print(f"Processing {len(ids)-start} sites (selected {len(ids)}, starting index {start+1})",flush=True); shared_posthog={}
    if not args.mock:
        try:
            from monitoring import provision_shared_posthog; shared_posthog=provision_shared_posthog()
        except Exception as exc:print(f"PostHog provisioning skipped: {exc}")
    results=[]; force_generation=args.blogs_only and not args.skip_generation; skip_generation=args.frontend_only or args.skip_generation
    for index in range(start,len(sites)):
        site_dir=sites[index]; site_id=site_dir.name; save_checkpoint(ids,index,step="start"); started=time.time(); result={"site":site_id,"startedAt":started}
        print(f"\n{'#'*72}\nSITE {index+1}/{len(ids)}: {site_id}\n{'#'*72}",flush=True)
        try:
            config=json.loads((site_dir/"site.json").read_text(encoding="utf-8")); config.setdefault("deploy",{})["provider"]=args.provider; target=site_url(config)
            if not args.mock:
                from monitoring import provision; config=provision(config,site_dir,target,shared_posthog)
            posts_exist=bool(list((site_dir/"_posts").glob("*.md")))
            if not skip_generation and (force_generation or not posts_exist):
                save_checkpoint(ids,index,step="generate"); cmd=[sys.executable,"scripts/generate_posts.py",site_id];
                if args.mock:cmd.append("--mock")
                run(cmd,env=env,site_id=site_id,step="generate")
            env2=env.copy(); mon=config.get("monitoring",{}); signup=config.get("signup",{}); env2.update({"SITE_URL":target,"SEO_POSTS_DIR":str((site_dir/"_posts").resolve()),"GOOGLE_SITE_VERIFICATION":mon.get("googleVerificationToken","") if not args.mock else "","NEXT_PUBLIC_POSTHOG_KEY":mon.get("posthogKey","") if not args.mock else "","NEXT_PUBLIC_POSTHOG_HOST":mon.get("posthogHost","https://us.i.posthog.com"),"SIGNUP_ENDPOINT":signup.get("endpoint",""),"SIGNUP_EMAIL":signup.get("email",""),"SIGNUP_HEADLINE":signup.get("headline","Interested? Get notified when this is available."),"SITE_PRODUCT_NAME":config.get("product",config.get("name",site_id)),"SITE_DESCRIPTION":config.get("valueProposition",""),"SITE_TOPIC":config.get("topic","")})
            save_checkpoint(ids,index,step="build"); run(["npm","run","build"],env=env2,site_id=site_id,step="build")
            if args.provider!="static":
                save_checkpoint(ids,index,step="deploy"); run([sys.executable,"scripts/site.py","deploy",site_id,args.provider],env=env2,site_id=site_id,step="deploy")
            if not args.mock:
                from monitoring import finalize; finalize(config)
            result.update({"ok":True,"url":target,"health":health(target)})
        except subprocess.CalledProcessError as exc:
            exhausted=marker.exists(); result.update({"ok":False,"error":f"Command failed with exit code {exc.returncode}"})
            step=(json.loads(CHECKPOINT.read_text(encoding="utf-8")).get("step") if CHECKPOINT.exists() else "unknown"); reason="Gemini fallback chain exhausted; resume here when credits/rate limits recover." if exhausted else "Command failed; fix the error and resume."
            save_checkpoint(ids,index,reason,step); (STATE/f"{site_id}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
            print(f"\n✗ STOPPED at site {index+1}/{len(ids)}: {site_id}\n  Failed step: {step}\n  Checkpoint: .deploy/state/checkpoint.json\n  Fix the failure and run: python scripts/launch.py --resume",file=sys.stderr,flush=True)
            raise SystemExit(2 if exhausted else 1)
        except Exception as exc:
            result.update({"ok":False,"error":repr(exc)}); save_checkpoint(ids,index,"Unexpected error; fix the error and resume.","python"); (STATE/f"{site_id}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); print(f"\n✗ UNEXPECTED FAILURE at site {index+1}/{len(ids)}: {site_id}\n  {exc!r}\n  Checkpoint saved. Run: python scripts/launch.py --resume",file=sys.stderr,flush=True); raise SystemExit(1)
        result["durationSeconds"]=round(time.time()-started,2); (STATE/f"{site_id}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); save_checkpoint(ids,index+1,step="complete"); print(f"[{index+1}/{len(ids)}] {site_id}: OK ({result['durationSeconds']}s)",flush=True); results.append(result)
    summary={"timestamp":time.time(),"total":len(results),"successful":sum(r["ok"] for r in results),"failed":sum(not r["ok"] for r in results),"results":results}; (STATE/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8"); print("\nFINAL SUMMARY\n"+json.dumps({k:summary[k] for k in ("total","successful","failed")},indent=2));
    if summary["failed"]:raise SystemExit(1)
if __name__=="__main__":main()
