import Container from "@/app/_components/container";
import { HeroPost } from "@/app/_components/hero-post";
import { Intro } from "@/app/_components/intro";
import { MoreStories } from "@/app/_components/more-stories";
import { ProductGrid } from "@/app/_components/product-grid";
import { getAllPosts } from "@/lib/api";
import { getSiteProducts } from "@/lib/site";

export default function Index() {
  const allPosts = getAllPosts();
  const products = getSiteProducts();

  const heroPost = allPosts[0];

  const morePosts = allPosts.slice(1, 13);

  return (
    <main>
      <Container>
        <Intro />
        <ProductGrid products={products} />
        {heroPost ? (
          <>
            <h2 className="mb-8 text-4xl font-bold tracking-tight md:text-6xl">Latest guides</h2>
            <HeroPost
              title={heroPost.title}
              coverImage={heroPost.coverImage}
              date={heroPost.date}
              author={heroPost.author}
              slug={heroPost.slug}
              excerpt={heroPost.excerpt}
            />
          </>
        ) : null}
        {morePosts.length > 0 && <MoreStories posts={morePosts} title="More guides" />}
      </Container>
    </main>
  );
}
