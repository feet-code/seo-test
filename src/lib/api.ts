import { Post } from "@/interfaces/post";
import fs from "fs";
import matter from "gray-matter";
import { join, resolve } from "path";

// During automated builds, SEO_POSTS_DIR points at the selected site's post
// directory. Falling back to _posts keeps the starter template backwards compatible.
const postsDirectory = resolve(process.cwd(), process.env.SEO_POSTS_DIR || "_posts");

export function getPostSlugs() {
  return fs
    .readdirSync(postsDirectory)
    .filter((file) => file.endsWith(".md"));
}

export function getPostBySlug(slug: string) {
  const realSlug = slug.replace(/\.md$/, "");
  const fullPath = join(postsDirectory, `${realSlug}.md`);

  if (!fs.existsSync(fullPath)) {
    return undefined;
  }

  const fileContents = fs.readFileSync(fullPath, "utf8");
  const { data, content } = matter(fileContents);

  return { ...data, slug: realSlug, content } as Post;
}

export function getAllPosts(): Post[] {
  const slugs = getPostSlugs();
  const posts = slugs
    .map((slug) => getPostBySlug(slug))
    .filter((post): post is Post => Boolean(post))
    .sort((post1, post2) => (post1.date > post2.date ? -1 : 1));

  return posts;
}
