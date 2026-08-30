import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import { MoreStories } from "@/app/_components/more-stories";
import SignupForm from "@/app/_components/signup-form";
import { ProductAnalytics } from "@/app/_components/product-analytics";
import { getAllPosts } from "@/lib/api";
import { getSiteProduct, getSiteProducts } from "@/lib/site";
import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

type Params = { params: Promise<{ id: string }> };

export default async function ProductPage({ params }: Params) {
  const { id } = await params;
  const product = getSiteProduct(id);
  if (!product) return notFound();

  const relatedPosts = getAllPosts().filter((post) => post.productId === product.id);
  const peers = getSiteProducts().filter((item) => item.id !== product.id);
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: product.name,
    description: product.valueProposition || product.problem,
    applicationCategory: "BusinessApplication",
    audience: { "@type": "Audience", audienceType: product.audience },
    featureList: product.product,
  };

  return (
    <main>
      <Container>
        <ProductAnalytics productId={product.id} productName={product.name} surface="product_landing" />
        <Header />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData).replace(/</g, "\\u003c") }}
        />
        <article className="mx-auto mb-20 max-w-4xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-neutral-500">
            {product.topic}
          </p>
          <h1 className="mb-7 text-5xl font-bold tracking-tight md:text-7xl">{product.name}</h1>
          <p className="mb-8 text-2xl leading-relaxed">{product.valueProposition}</p>
          <div className="grid gap-5 rounded-2xl border border-neutral-200 p-7 md:grid-cols-2 dark:border-slate-700">
            <div>
              <h2 className="mb-2 text-lg font-bold">The problem</h2>
              <p className="leading-relaxed">{product.problem}</p>
            </div>
            <div>
              <h2 className="mb-2 text-lg font-bold">The focused product</h2>
              <p className="leading-relaxed">{product.product}</p>
            </div>
          </div>
          <section className="mt-8 grid gap-5 md:grid-cols-3">
            <div className="rounded-2xl bg-neutral-50 p-6 dark:bg-slate-800">
              <h2 className="mb-2 text-lg font-bold">Who it is for</h2>
              <p className="leading-relaxed">
                {product.buyer ? `${product.buyer}, serving ` : "Teams serving "}
                {product.audience}.
              </p>
            </div>
            <div className="rounded-2xl bg-neutral-50 p-6 dark:bg-slate-800">
              <h2 className="mb-2 text-lg font-bold">Economic case</h2>
              <p className="leading-relaxed">
                {product.profitRationale ||
                  `The concept is designed to improve ${product.economicDriver || "a measurable business outcome"}.`}
              </p>
            </div>
            <div className="rounded-2xl bg-neutral-50 p-6 dark:bg-slate-800">
              <h2 className="mb-2 text-lg font-bold">What the probe must validate</h2>
              <p className="leading-relaxed">
                {product.primaryRisk ||
                  "Whether this problem is frequent and expensive enough to justify focused software."}
              </p>
            </div>
          </section>
          {product.monetization ? (
            <section className="mt-8 rounded-2xl border border-neutral-200 p-7 dark:border-slate-700">
              <h2 className="mb-2 text-lg font-bold">Pricing hypothesis</h2>
              <p className="leading-relaxed">{product.monetization}</p>
              <p className="mt-3 text-sm leading-relaxed text-neutral-600 dark:text-slate-300">
                This is an early validation hypothesis, not a published offer. The signup and search probes
                determine whether the problem deserves a product build.
              </p>
            </section>
          ) : null}
          <SignupForm
            endpoint={process.env.SIGNUP_ENDPOINT}
            fallbackEmail={process.env.SIGNUP_EMAIL}
            productId={product.id}
            productName={product.name}
            siteName={process.env.SITE_NAME}
            headline={`Want ${product.name}? Join the early-access list.`}
          />
        </article>
        {relatedPosts.length > 0 ? (
          <MoreStories posts={relatedPosts} title={`Guides for ${product.name}`} />
        ) : null}
        {peers.length > 0 ? (
          <section className="mb-24 rounded-2xl bg-neutral-50 p-8 dark:bg-slate-800">
            <h2 className="mb-5 text-3xl font-bold">Other tools for the same audience</h2>
            <div className="flex flex-wrap gap-3">
              {peers.map((peer) => (
                <Link
                  key={peer.id}
                  href={`/products/${peer.id}`}
                  className="rounded-full border border-neutral-300 px-4 py-2 font-medium hover:bg-white dark:border-slate-600 dark:hover:bg-slate-700"
                >
                  {peer.name}
                </Link>
              ))}
            </div>
          </section>
        ) : null}
      </Container>
    </main>
  );
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const product = getSiteProduct(id);
  if (!product) return notFound();
  return {
    title: `${product.name}: ${product.topic}`,
    description: product.valueProposition || product.problem,
  };
}

export function generateStaticParams() {
  return getSiteProducts().map((product) => ({ id: product.id }));
}
