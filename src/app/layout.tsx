import Footer from "@/app/_components/footer";
import { HOME_OG_IMAGE_URL } from "@/lib/constants";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import cn from "classnames";
import { ThemeSwitcher } from "./_components/theme-switcher";
import { PostHog } from "./_components/posthog";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const siteUrl = process.env.SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: process.env.SITE_NAME || process.env.SITE_PRODUCT_NAME || "Focused workflow tools",
  description: process.env.SITE_DESCRIPTION || `Helpful information about ${process.env.SITE_TOPIC || "this topic"}.`,
  openGraph: { images: [HOME_OG_IMAGE_URL] },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const googleVerification = process.env.GOOGLE_SITE_VERIFICATION;
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon/favicon-16x16.png" />
        <link rel="manifest" href="/favicon/site.webmanifest" />
        <link rel="mask-icon" href="/favicon/safari-pinned-tab.svg" color="#000000" />
        <link rel="shortcut icon" href="/favicon/favicon.ico" />
        <meta name="theme-color" content="#000" />
        <link rel="alternate" type="application/rss+xml" href="/feed.xml" />
        {googleVerification ? <meta name="google-site-verification" content={googleVerification} /> : null}
      </head>
      <body className={cn(inter.className, "dark:bg-slate-900 dark:text-slate-400")}>
        <PostHog />
        <ThemeSwitcher />
        <div className="min-h-screen">{children}</div>
        <Footer />
      </body>
    </html>
  );
}
