"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/backtest", label: "Backtest Report" },
  { href: "/live", label: "Live Signals" },
];

export default function Navbar() {
  const pathname = usePathname();
  return (
    <nav className="border-b border-panelBorder">
      <div className="max-w-[1400px] mx-auto px-8 h-16 flex items-center justify-between">
        <span className="font-heading font-bold text-lg text-textPrimary">
          Quant<span className="text-accent">IQ</span>
        </span>
        <div className="flex gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium ${
                pathname === link.href ? "text-accent" : "text-textMuted hover:text-textPrimary"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}