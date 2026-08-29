"use client";

import { useEffect } from "react";

type PostHogWindow = typeof window & {
  posthog?: { capture?: (event: string, properties: Record<string, string>) => void };
};

export function ProductAnalytics({
  productId,
  productName,
  surface,
}: {
  productId: string;
  productName?: string;
  surface: "product_landing" | "blog_post";
}) {
  useEffect(() => {
    let captured = false;
    const capture = () => {
      if (captured) return;
      const posthog = (window as PostHogWindow).posthog;
      if (!posthog?.capture) return;
      captured = true;
      posthog.capture("product_probe_viewed", {
        product_id: productId,
        product_name: productName || productId,
        surface,
        source_path: window.location.pathname,
      });
    };
    capture();
    window.addEventListener("posthog-ready", capture);
    return () => window.removeEventListener("posthog-ready", capture);
  }, [productId, productName, surface]);

  return null;
}
