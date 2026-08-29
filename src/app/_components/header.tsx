import Link from "next/link";

const Header = () => {
  const name = process.env.SITE_NAME || process.env.SITE_PRODUCT_NAME || "Home";
  return (
    <h2 className="text-2xl md:text-4xl font-bold tracking-tight md:tracking-tighter leading-tight mb-20 mt-8 flex items-center">
      <Link href="/" className="hover:underline">
        {name}
      </Link>
      .
    </h2>
  );
};

export default Header;
