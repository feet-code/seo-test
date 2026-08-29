export function Intro() {
  const name = process.env.SITE_NAME || process.env.SITE_PRODUCT_NAME || "Practical tools";
  const audience = process.env.SITE_AUDIENCE;
  const topic = process.env.SITE_TOPIC;
  return (
    <section className="mt-16 mb-16 max-w-5xl md:mb-20">
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-neutral-500">
        {audience ? `Built for ${audience}` : "Focused workflow software"}
      </p>
      <h1 className="text-5xl md:text-8xl font-bold tracking-tighter leading-tight">
        {name}
      </h1>
      <p className="mt-6 max-w-3xl text-xl leading-relaxed md:text-2xl">
        Practical tools and field-tested guides for {topic || "recurring work"}.
      </p>
    </section>
  );
}
