import { SiteProduct } from "@/interfaces/product";

export function getSiteProducts(): SiteProduct[] {
  const raw = process.env.SITE_PRODUCTS_JSON;
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed.filter(isProduct);
      }
    } catch {
      // The backward-compatible fallback below keeps old single-product sites buildable.
    }
  }
  const name = process.env.SITE_PRODUCT_NAME || process.env.SITE_NAME || "Product";
  return [
    {
      id: "product",
      name,
      product: process.env.SITE_DESCRIPTION || "",
      audience: process.env.SITE_AUDIENCE || "",
      problem: process.env.SITE_DESCRIPTION || "",
      valueProposition: process.env.SITE_DESCRIPTION || "",
      topic: process.env.SITE_TOPIC || "",
    },
  ];
}

export function getSiteProduct(id: string): SiteProduct | undefined {
  return getSiteProducts().find((product) => product.id === id);
}

function isProduct(value: unknown): value is SiteProduct {
  if (!value || typeof value !== "object") return false;
  const product = value as Record<string, unknown>;
  return Boolean(product.id && product.name && product.product && product.topic);
}
