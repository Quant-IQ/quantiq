"use client";

import { useEffect, useState } from "react";
import { getWatchlists } from "@/lib/api";

export default function MobileWatchlistSelector({
  activeWatchlist,
  onSelect
}: {
  activeWatchlist: string | null;
  onSelect: (name: string | null) => void;
}) {
  const [watchlists, setWatchlists] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWatchlists().then(res => {
      setWatchlists(res.watchlists);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="md:hidden h-[48px] w-full flex items-center px-4 animate-pulse bg-white/5 border-b border-[var(--color-panel-border)] shrink-0" />;
  
  if (watchlists.length === 0) return null;

  return (
    <div className="md:hidden w-full bg-[var(--color-bg-dark)] border-b border-[var(--color-panel-border)] shrink-0">
      <div className="flex overflow-x-auto custom-scrollbar px-3 py-2.5 gap-2 snap-x">
        <button
          onClick={() => onSelect(null)}
          className={`snap-start whitespace-nowrap px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all shadow-sm ${
            activeWatchlist === null
              ? "bg-white text-black"
              : "bg-white/5 text-[var(--color-text-dim)] border border-white/10"
          }`}
        >
          Overview
        </button>
        {watchlists.map((name) => (
          <button
            key={name}
            onClick={() => onSelect(name)}
            className={`snap-start whitespace-nowrap px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all shadow-sm ${
              activeWatchlist === name
                ? "bg-[var(--color-accent-green)] text-black"
                : "bg-white/5 text-[var(--color-text-dim)] border border-white/10"
            }`}
          >
            {name.replace(/_/g, " ")}
          </button>
        ))}
      </div>
    </div>
  );
}
