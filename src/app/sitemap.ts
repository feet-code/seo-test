import { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/api";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = (process.env.SITE_URL || "http://localhost:3000").replace(/\/$/, "");
  const posts = getAllPosts();
  return [
    { url: `${base}/`, lastModified: new Date() },
    ...posts.map((post) => ({ url: `${base}/posts/${post.slug}`, lastModified: new Date(post.date) })),
  ];
}
