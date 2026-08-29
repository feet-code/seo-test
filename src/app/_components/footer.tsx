import Container from "@/app/_components/container";
export function Footer() {
  const name = process.env.SITE_NAME || process.env.SITE_PRODUCT_NAME || "All rights reserved.";
  return (
    <footer className="bg-neutral-50 border-t border-neutral-200 dark:bg-slate-800">
      <Container>
        <div className="py-8 text-center text-sm text-neutral-500">
          © {new Date().getFullYear()} {name}
        </div>
      </Container>
    </footer>
  );
}

export default Footer;
