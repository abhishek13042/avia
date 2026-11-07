"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/upload", label: "Try a video" },
  { href: "/benchmarks", label: "Benchmarks" },
  { href: "/about", label: "About" },
];

export function SiteNav() {
  const path = usePathname();
  return (
    <nav aria-label="Main">
      <Link href="/" className="brand">AVIA</Link>
      {LINKS.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="nav-link"
          aria-current={path === link.href ? "page" : undefined}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
