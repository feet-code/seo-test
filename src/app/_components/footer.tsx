import Container from "@/app/_components/container";
import SignupForm from "@/app/_components/signup-form";

export function Footer() {
  return (
    <footer className="bg-neutral-50 border-t border-neutral-200 dark:bg-slate-800">
      <Container>
        <SignupForm
          endpoint={process.env.SIGNUP_ENDPOINT}
          fallbackEmail={process.env.SIGNUP_EMAIL}
          productName={process.env.SITE_PRODUCT_NAME}
          headline={process.env.SIGNUP_HEADLINE}
        />
        <div className="py-8 text-center text-sm text-neutral-500">
          © {new Date().getFullYear()} {process.env.SITE_PRODUCT_NAME || "All rights reserved."}
        </div>
      </Container>
    </footer>
  );
}

export default Footer;
