import { SiteProduct } from "@/interfaces/product";
import Link from "next/link";

export function ProductGrid({ products }: { products: SiteProduct[] }) {
  return (
    <section id="products" className="mb-20 md:mb-28">
      <div className="mb-8 max-w-3xl">
        <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-neutral-500">
          Focused tools
        </p>
        <h2 className="text-4xl font-bold tracking-tight md:text-6xl">
          Pick the workflow you want to improve
        </h2>
      </div>
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <article
            key={product.id}
            className="flex min-h-64 flex-col rounded-2xl border border-neutral-200 bg-white p-7 shadow-sm transition hover:-translate-y-1 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
          >
            <p className="mb-3 text-sm font-medium text-neutral-500">{product.topic}</p>
            <h3 className="mb-3 text-2xl font-bold tracking-tight">{product.name}</h3>
            <p className="mb-6 flex-1 leading-relaxed">{product.valueProposition || product.problem}</p>
            <Link
              href={`/products/${product.id}`}
              className="font-semibold underline decoration-2 underline-offset-4"
            >
              Explore {product.name} →
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
