import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "QuantIQ",
  description: "Algorithmic trading dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-body">
        <Navbar />
        <main className="max-w-[1400px] mx-auto px-8">{children}</main>
      </body>
    </html>
  );
}