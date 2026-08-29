import { Metadata } from "next";
import { notFound } from "next/navigation";
import { getAllPosts, getPostBySlug } from "@/lib/api";
import { CMS_NAME } from "@/lib/constants";
import markdownToHtml from "@/lib/markdownToHtml";
import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import { PostBody } from "@/app/_components/post-body";
import { PostHeader } from "@/app/_components/post-header";
import SignupForm from "@/app/_components/signup-form";
import { ProductAnalytics } from "@/app/_components/product-analytics";
import Link from "next/link";

export default async function Post(props: Params) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return notFound();
  }

  const content = await markdownToHtml(post.content || "");

  return (
    <main>
      <Container>
        {post.productId ? (
          <ProductAnalytics
            productId={post.productId}
            productName={post.productName}
            surface="blog_post"
          />
        ) : null}
        <Header />
        <article className="mb-32">
          <PostHeader
            title={post.title}
            coverImage={post.coverImage}
            date={post.date}
            author={post.author}
          />
          <PostBody content={content} />
          {post.productId ? (
            <div className="mx-auto max-w-2xl">
              <p className="mt-10 text-sm text-neutral-500">
                This guide supports the{" "}
                <Link href={`/products/${post.productId}`} className="font-semibold underline">
                  {post.productName || "related product"}
                </Link>{" "}
                research probe.
              </p>
              <SignupForm
                endpoint={process.env.SIGNUP_ENDPOINT}
                fallbackEmail={process.env.SIGNUP_EMAIL}
                productId={post.productId}
                productName={post.productName}
                siteName={process.env.SITE_NAME}
                headline={`Interested in ${post.productName || "this product"}? Get early access.`}
              />
            </div>
          ) : null}
        </article>
      </Container>
    </main>
  );
}

type Params = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata(props: Params): Promise<Metadata> {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return notFound();
  }

  const title = `${post.title} | ${process.env.SITE_NAME || CMS_NAME}`;

  return {
    title,
    openGraph: {
      title,
      images: [post.ogImage.url],
    },
  };
}

export async function generateStaticParams() {
  const posts = getAllPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}
