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
  const customer = product.buyer || product.audience;
  const outcome = product.valueProposition || product.problem;
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: product.name,
    description: product.valueProposition || product.problem,
    applicationCategory: "BusinessApplication",
    audience: { "@type": "Audience", audienceType: product.audience },
    featureList: [product.product, outcome],
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
        <article className="mx-auto mb-20 max-w-5xl">
          <header className="rounded-3xl bg-neutral-950 px-7 py-14 text-white md:px-12 md:py-20 dark:bg-slate-800">
            <p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-neutral-300">
              Purpose-built for {product.audience}
            </p>
            <h1 className="mb-7 max-w-4xl text-5xl font-bold tracking-tight md:text-7xl">
              {product.name}
            </h1>
            <p className="max-w-3xl text-2xl leading-relaxed text-neutral-200">{outcome}</p>
            <div className="mt-9 flex flex-wrap gap-4">
              <a
                href="#early-access"
                className="rounded-full bg-white px-6 py-3 font-semibold text-neutral-950 hover:bg-neutral-200"
              >
                Get early access
              </a>
              <a
                href="#how-it-works"
                className="rounded-full border border-neutral-600 px-6 py-3 font-semibold text-white hover:border-neutral-300"
              >
                See how it works
              </a>
            </div>
          </header>

          <section className="mt-10 grid gap-5 md:grid-cols-2">
            <div>
              <div className="h-full rounded-2xl border border-neutral-200 p-7 dark:border-slate-700">
                <p className="mb-3 text-sm font-semibold uppercase tracking-[0.15em] text-neutral-500">
                  The challenge
                </p>
                <h2 className="mb-3 text-2xl font-bold">Stop losing time and value to a fragmented process</h2>
                <p className="leading-relaxed">{product.problem}</p>
              </div>
            </div>
            <div>
              <div className="h-full rounded-2xl border border-neutral-200 p-7 dark:border-slate-700">
                <p className="mb-3 text-sm font-semibold uppercase tracking-[0.15em] text-neutral-500">
                  The solution
                </p>
                <h2 className="mb-3 text-2xl font-bold">A focused tool for the work that matters</h2>
                <p className="leading-relaxed">{product.product}</p>
              </div>
            </div>
          </section>

          <section id="how-it-works" className="mt-16 scroll-mt-8">
            <p className="mb-3 text-sm font-semibold uppercase tracking-[0.15em] text-neutral-500">
              How it works
            </p>
            <h2 className="max-w-3xl text-4xl font-bold tracking-tight">
              Move from scattered information to a clear next action
            </h2>
            <div className="mt-8 grid gap-5 md:grid-cols-3">
              <div className="rounded-2xl bg-neutral-50 p-7 dark:bg-slate-800">
                <span className="mb-5 block text-sm font-bold text-neutral-500">01</span>
                <h3 className="mb-3 text-xl font-bold">Bring the work into view</h3>
                <p className="leading-relaxed">
                  Connect or import the records your team already uses without replacing the systems that run
                  your business.
                </p>
              </div>
              <div className="rounded-2xl bg-neutral-50 p-7 dark:bg-slate-800">
                <span className="mb-5 block text-sm font-bold text-neutral-500">02</span>
                <h3 className="mb-3 text-xl font-bold">Find what deserves attention</h3>
                <p className="leading-relaxed">{product.product}</p>
              </div>
              <div className="rounded-2xl bg-neutral-50 p-7 dark:bg-slate-800">
                <span className="mb-5 block text-sm font-bold text-neutral-500">03</span>
                <h3 className="mb-3 text-xl font-bold">Act and measure the outcome</h3>
                <p className="leading-relaxed">{outcome}</p>
              </div>
            </div>
          </section>

          <section className="mt-16 rounded-3xl border border-neutral-200 p-8 md:p-10 dark:border-slate-700">
            <div className="grid gap-8 md:grid-cols-2 md:items-center">
              <div>
                <p className="mb-3 text-sm font-semibold uppercase tracking-[0.15em] text-neutral-500">
                  Built for your operation
                </p>
                <h2 className="text-3xl font-bold tracking-tight">Give the right owner a clearer decision</h2>
              </div>
              <div>
                <p className="text-lg leading-relaxed">
                  {product.name} is designed for {customer}. It keeps the workflow focused on one measurable
                  problem, so teams can spend less time reconstructing what happened and more time acting on it.
                </p>
              </div>
            </div>
          </section>

          <div id="early-access" className="scroll-mt-8">
            <SignupForm
              endpoint={process.env.SIGNUP_ENDPOINT}
              fallbackEmail={process.env.SIGNUP_EMAIL}
              productId={product.id}
              productName={product.name}
              siteName={process.env.SITE_NAME}
              headline={`Get early access to ${product.name}.`}
            />
          </div>
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
