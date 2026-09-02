"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MagnifyingGlassIcon, CalculatorIcon, ArrowRightIcon } from "@heroicons/react/24/outline";
import { useRouter } from "next/navigation";

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Handle Cmd+K / Ctrl+K
  useEffect(() => {
    const handleOpen = () => setIsOpen(true);
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("open-command-palette", handleOpen);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("open-command-palette", handleOpen);
    };
  }, []);

  // Auto-focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery("");
    }
  }, [isOpen]);

  const mockTickers = [
    { symbol: "RELIANCE.NS", name: "Reliance Industries", type: "Equity" },
    { symbol: "TCS.NS", name: "Tata Consultancy Services", type: "Equity" },
    { symbol: "INFY.NS", name: "Infosys Limited", type: "Equity" },
    { symbol: "HDFCBANK.NS", name: "HDFC Bank", type: "Equity" },
    { symbol: "NIFTY50", name: "Nifty 50 Index", type: "Index" },
  ];

  const filteredTickers = query
    ? mockTickers.filter(
        (t) =>
          t.symbol.toLowerCase().includes(query.toLowerCase()) ||
          t.name.toLowerCase().includes(query.toLowerCase())
      )
    : mockTickers;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="relative w-full max-w-xl bg-[var(--color-bg-dark)] border border-[var(--color-panel-border)] rounded-xl shadow-2xl overflow-hidden flex flex-col"
          >
            {/* Search Input */}
            <div className="flex items-center px-4 py-4 border-b border-[var(--color-panel-border)]">
              <MagnifyingGlassIcon className="w-5 h-5 text-[var(--color-text-dim)] mr-3" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search tickers, commands, or strategies..."
                className="flex-1 bg-transparent border-none outline-none text-[var(--color-text-bright)] placeholder-[var(--color-text-dim)] text-lg"
              />
              <div className="flex items-center gap-1 text-xs text-[var(--color-text-dim)] bg-white/5 px-2 py-1 rounded">
                <kbd className="font-mono">ESC</kbd> to close
              </div>
            </div>

            {/* Results */}
            <div className="max-h-[60vh] overflow-y-auto custom-scrollbar p-2 bg-[#0A0E13]/50">
              {filteredTickers.length > 0 ? (
                <div className="space-y-1">
                  <div className="px-3 py-2 text-xs font-semibold text-[var(--color-text-dim)] uppercase tracking-wider">
                    Tickers
                  </div>
                  {filteredTickers.map((ticker) => (
                    <button
                      key={ticker.symbol}
                      onClick={() => {
                        setIsOpen(false);
                        router.push(`/stock/${ticker.symbol.replace('.NS', '')}`);
                      }}
                      className="w-full flex items-center justify-between px-3 py-3 rounded-lg hover:bg-white/5 transition-colors group text-left"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center border border-[var(--color-panel-border)]">
                          <CalculatorIcon className="w-4 h-4 text-[var(--color-text-bright)]" />
                        </div>
                        <div>
                          <div className="text-[var(--color-text-bright)] font-semibold">{ticker.symbol}</div>
                          <div className="text-[var(--color-text-dim)] text-sm">{ticker.name}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[var(--color-text-dim)] text-[10px] border border-[var(--color-panel-border)] rounded px-1.5 py-0.5 uppercase tracking-wider">
                          {ticker.type}
                        </span>
                        <ArrowRightIcon className="w-4 h-4 text-[var(--color-accent-green)] opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-1" />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center text-[var(--color-text-dim)]">
                  No results found for "{query}"
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
