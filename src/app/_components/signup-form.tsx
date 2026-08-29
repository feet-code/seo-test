"use client";

import { FormEvent, useState } from "react";

type Props = {
  endpoint?: string;
  fallbackEmail?: string;
  productId?: string;
  productName?: string;
  siteName?: string;
  headline?: string;
};

export default function SignupForm({ endpoint = "", fallbackEmail = "", productId = "product", productName = "this product", siteName = "", headline = "Interested? Get notified when this is available." }: Props) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email) return;
    const properties = { product_id: productId, product_name: productName, site_name: siteName, source_path: window.location.pathname };
    const posthog = (window as typeof window & { posthog?: { capture?: (event: string, properties: Record<string, string>) => void } }).posthog;
    posthog?.capture?.("product_interest_submitted", properties);
    if (!endpoint) {
      if (fallbackEmail) window.location.href = `mailto:${fallbackEmail}?subject=${encodeURIComponent(`Interest in ${productName}`)}&body=${encodeURIComponent(`I am interested in ${productName}. My email is ${email}.`)}`;
      else setStatus("Signup is not configured yet.");
      return;
    }
    try {
      const response = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, productId, product: productName, site: siteName, sourcePath: window.location.pathname }) });
      if (!response.ok) throw new Error("request failed");
      setEmail(""); setStatus("Thanks — we'll be in touch.");
    } catch { setStatus("Something went wrong. Please try again."); }
  }

  return (
    <section className="w-full max-w-xl mx-auto my-12 px-6">
      <h2 className="text-2xl font-bold tracking-tight mb-3">{headline}</h2>
      <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3">
        <input aria-label="Email address" required type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className="flex-1 rounded border border-neutral-300 bg-white px-4 py-3 text-black" />
        <button type="submit" className="rounded bg-black px-5 py-3 font-semibold text-white hover:opacity-80">Notify me</button>
      </form>
      {status ? <p className="mt-3 text-sm">{status}</p> : null}
    </section>
  );
}
