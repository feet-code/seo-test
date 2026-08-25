"use client";

import { useEffect } from "react";

export function PostHog() {
  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com";

  useEffect(() => {
    if (!key || typeof window === "undefined") return;
    if ((window as any).__seoPosthogLoaded) return;
    (window as any).__seoPosthogLoaded = true;

    const script = document.createElement("script");
    script.src = `${host}/static/array.js`;
    script.async = true;
    script.onload = () => {
      const ph = (window as any).posthog;
      if (ph?.init) {
        ph.init(key, { api_host: host, capture_pageview: true, persistence: "localStorage" });
        window.dispatchEvent(new Event("posthog-ready"));
      }
    };
    document.head.appendChild(script);
  }, [key, host]);

  return null;
}
