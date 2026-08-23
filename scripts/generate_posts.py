#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,time,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITES=ROOT/"sites"; STATE=ROOT/".deploy"/"state"
DEFAULT_MODELS=["gemini-2.5-flash-lite","gemini-2.5-flash"]
class GeminiExhausted(Exception): pass

def models():
    raw=os.getenv("GEMINI_MODELS"); vals=[x.strip() for x in raw.split(",")] if raw else DEFAULT_MODELS
    return [x for i,x in enumerate(vals) if x and x not in vals[:i]]

def load_site(site_id):
    d=SITES/site_id; p=d/"site.json"
    if not p.exists(): raise SystemExit(f"Unknown site '{site_id}'")
    return json.loads(p.read_text(encoding="utf-8")),d

def example_format():
    files=sorted((ROOT/"_posts").glob("*.md"))
    if not files: raise SystemExit("No example Markdown files found in _posts/")
    return files[0].read_text(encoding="utf-8")[:3000]

def prompt_for(site):
    n=max(1,min(int(site.get("articleCount",5)),10)); a=site.get("author",{}); im=site.get("images",{})
    return f'''Create exactly {n} original blog posts for this website. Product/service: {site.get("product")}. Product URL: {site.get("productUrl")}. Audience: {site.get("audience")}. Main topic: {site.get("topic")}. Value proposition/problem: {site.get("valueProposition")}. Attract qualified organic-search visitors likely to need or buy this product. Prioritize distinct search intents, useful information, topical authority, specificity, and natural conversion opportunities. Do not write generic filler, keyword stuffing, fake statistics, fake claims, or capabilities not provided. Return ONLY a JSON array with slug, title, excerpt, and content (Markdown). Do not include YAML frontmatter. Match this template structure: {example_format()}. Use author {a.get("name","John Smith")}, author picture {a.get("picture","/assets/blog/authors/jj.jpeg")}, cover image {im.get("coverImage","/assets/blog/preview/cover.jpg")}, OG image {im.get("ogImage","/assets/blog/dynamic-routing/cover.jpg")}.'''

def mock_articles(site,n):
    topic=site.get("topic") or site.get("name") or "this topic"; product=site.get("product") or "the product"; base=re.sub(r"[^a-z0-9]+","-",topic.lower()).strip("-")
    return [{"slug":f"{base}-guide-{i+1}","title":f"A Practical Guide to {topic.title()}","excerpt":f"A practical guide to {topic} and common ways to solve the problem efficiently.","content":f"## Why {topic} matters\n\nPeople working with {topic} often need a simple, repeatable workflow.\n\n## A practical approach\n\nDefine the problem, document the current workflow, and remove repetitive steps. {product} is designed around this problem.\n\n## Next steps\n\nTest a small improvement, measure the result, and expand what works."} for i in range(n)]

def call_model(model,prompt):
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise GeminiExhausted("GEMINI_API_KEY is not set")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.8,"responseMimeType":"application/json"}}
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=180) as response: return json.load(response)["candidates"][0]["content"]["parts"][0]["text"]

def call_gemini(prompt,site_id):
    last=None
    for model in models():
        for attempt in range(3):
            try:
                print(f"  Gemini: {model} attempt {attempt+1}/3",flush=True); return call_model(model,prompt)
            except urllib.error.HTTPError as exc:
                last=exc
                if exc.code in {400,401,403}: raise SystemExit(f"Gemini request failed: HTTP {exc.code}") from exc
                if exc.code not in {408,409,425,429,500,502,503,504}: break
                time.sleep(min(30,2**attempt*2))
            except urllib.error.URLError as exc:
                last=exc; time.sleep(min(30,2**attempt*2))
            except Exception as exc:
                last=exc
                if attempt==2: break
                time.sleep(min(30,2**attempt*2))
    STATE.mkdir(parents=True,exist_ok=True)
    (STATE/"gemini_exhausted.json").write_text(json.dumps({"site":site_id,"timestamp":time.time(),"models":models(),"error":str(last)},indent=2)+"\n",encoding="utf-8")
    raise GeminiExhausted(f"All configured Gemini models failed: {last}")

def clean_json(text,n):
    text=re.sub(r"^```(?:json)?\s*|\s*```$","",text.strip()); data=json.loads(text)
    if not isinstance(data,list) or len(data)!=n: raise ValueError(f"Gemini returned {len(data) if isinstance(data,list) else 'invalid'} articles; expected {n}")
    return data

def safe_slug(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
    if not s: raise ValueError("Generated an empty slug")
    return s

def write_posts(site,d,articles):
    p=d/"_posts"; p.mkdir(parents=True,exist_ok=True)
    for old in p.glob("*.md"): old.unlink()
    now=datetime.now(timezone.utc).replace(microsecond=0); seen=set(); a=site.get("author",{}); im=site.get("images",{})
    for i,x in enumerate(articles):
        title=str(x.get("title","")).strip(); excerpt=str(x.get("excerpt","")).strip(); content=str(x.get("content","")).strip(); slug=safe_slug(str(x.get("slug",title)))
        if not title or not excerpt or not content: raise ValueError(f"Article {i+1} missing title, excerpt, or content")
        if slug in seen: raise ValueError(f"Duplicate generated slug: {slug}")
        seen.add(slug)
        fm="\n".join(["---",f"title: {json.dumps(title,ensure_ascii=False)}",f"excerpt: {json.dumps(excerpt,ensure_ascii=False)}",f"coverImage: {json.dumps(im.get('coverImage','/assets/blog/preview/cover.jpg'))}",f"date: {json.dumps(now.isoformat().replace('+00:00','Z'))}","author:",f"  name: {json.dumps(a.get('name','John Smith'))}",f"  picture: {json.dumps(a.get('picture','/assets/blog/authors/jj.jpeg'))}","ogImage:",f"  url: {json.dumps(im.get('ogImage','/assets/blog/dynamic-routing/cover.jpg'))}","---","",content,""])
        (p/f"{slug}.md").write_text(fm,encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("site_id"); ap.add_argument("--mock",action="store_true"); args=ap.parse_args(); site,d=load_site(args.site_id); n=max(1,min(int(site.get("articleCount",5)),10))
    mock=args.mock or os.getenv("MOCK_LLM","").lower() in {"1","true","yes"}
    print(f"Generating {n} posts for {args.site_id} ({'mock' if mock else 'Gemini failover'})")
    raw=mock_articles(site,n) if mock else clean_json(call_gemini(prompt_for(site),args.site_id),n)
    write_posts(site,d,raw); print(f"Wrote {len(raw)} posts to {d/'_posts'}")
if __name__=="__main__": main()
