import { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/api";
import { getSiteProducts } from "@/lib/site";

// sitemap.xml is generated entirely at build time for static export.
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = (process.env.SITE_URL || "http://localhost:3000").replace(/\/$/, "");
  const posts = getAllPosts();
  const products = getSiteProducts();
  return [
    { url: `${base}/`, lastModified: new Date() },
    ...products.map((product) => ({ url: `${base}/products/${product.id}`, lastModified: new Date() })),
    ...posts.map((post) => ({ url: `${base}/posts/${post.slug}`, lastModified: new Date(post.date) })),
  ];
}
