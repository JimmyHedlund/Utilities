import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "MD Converter",
  description: "Convert PDF and PowerPoint files to Markdown."
};

const navItems = [
  { href: "/", label: "Upload" },
  { href: "/jobs", label: "Jobs" },
  { href: "/settings", label: "Settings" }
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="app-header">
          <Link className="brand" href="/">
            MD Converter
          </Link>
          <nav aria-label="Primary">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}

