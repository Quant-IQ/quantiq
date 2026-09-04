import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CommandPalette from "@/components/ui/CommandPalette";
import IndicesStrip from "@/components/dashboard/IndicesStrip";
import MobileBottomNav from "@/components/dashboard/MobileBottomNav";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "QuantIQ | Premium Platform",
  description: "Algorithmic trading dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased h-screen w-screen overflow-hidden flex flex-col`}>
        <IndicesStrip />
        <main className="flex-1 overflow-hidden relative pb-[64px] md:pb-0">
          {children}
        </main>
        <CommandPalette />
        <MobileBottomNav />
      </body>
    </html>
  );
}