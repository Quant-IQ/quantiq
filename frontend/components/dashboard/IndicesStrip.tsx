"use client";
import { useEffect, useState } from "react";
import { getIndices } from "@/lib/api";
import { IndexData } from "@/lib/types";
import { MagnifyingGlassIcon, BellIcon, UserIcon } from "@heroicons/react/24/outline";

export default function IndicesStrip() {
  const [indices, setIndices] = useState<IndexData[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getIndices()
      .then((data) => setIndices(data.indices))
      .catch(() => setIndices([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-12 w-full bg-panel border-b border-panelBorder animate-pulse" />;

  if (!indices || indices.length === 0) {
    return (
      <div className="h-11 w-full bg-panel/80 backdrop-blur-md border-b border-panelBorder flex items-center justify-center text-sm text-textMuted shrink-0 z-50">
        <span className="font-medium text-warn mr-2">Coming Soon:</span> Live Indices feed awaiting scripting team implementation
      </div>
    );
  }

  return (
    <div className="h-11 w-full bg-[var(--color-bg-dark)] border-b border-panelBorder flex items-center justify-between overflow-hidden shrink-0 z-50">
      <div className="flex-1 overflow-hidden h-full flex items-center">
        <div className="flex whitespace-nowrap animate-marquee">
          {/* We duplicate the map 3 times to create a seamless infinite scrolling effect */}
          {[...indices, ...indices, ...indices].map((idx, i) => {
            const isPos = idx.change >= 0;
            return (
              <div key={`${idx.name}-${i}`} className="flex items-center gap-2 text-sm px-8 border-r border-panelBorder/50 last:border-0">
                <span className="font-bold text-[11px] text-[var(--color-text-dim)] tracking-widest uppercase">{idx.name}</span>
                <span className="text-white font-mono tabular-nums text-[13px] font-bold">{idx.value.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                <span className={`font-mono tabular-nums text-xs font-bold ${isPos ? "text-[var(--color-accent-green)]" : "text-[#F0665E]"}`}>
                  {isPos ? "+" : ""}{idx.change.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Action Cluster (Search, Notifications, Profile) */}
      <div className="flex items-center gap-3 sm:gap-6 px-3 sm:px-6 h-full bg-[var(--color-bg-dark)] z-10 relative shrink-0">
        <button 
          onClick={() => window.dispatchEvent(new CustomEvent('open-command-palette'))}
          className="text-[var(--color-text-dim)] hover:text-white transition-colors"
        >
          <MagnifyingGlassIcon className="w-5 h-5" strokeWidth={2.5} />
        </button>
        <button className="text-[var(--color-text-dim)] hover:text-white transition-colors">
          <BellIcon className="w-5 h-5" strokeWidth={2.5} />
        </button>
        <button className="w-7 h-7 rounded-md bg-[var(--color-accent-green)] flex items-center justify-center text-black hover:opacity-90 transition-opacity ml-2">
          <UserIcon className="w-4 h-4" strokeWidth={2.5} />
        </button>
      </div>
    </div>
  );
}
