"use client";

import { useEffect, useState } from "react";
import { getWatchlistData } from "@/lib/api";
import { ScreenerData } from "@/lib/types";
import LoadingState from "@/components/ui/LoadingState";
import Sparkline from "@/components/ui/Sparkline";

export default function WatchlistView({ watchlistName }: { watchlistName: string | null }) {
  const [data, setData] = useState<ScreenerData[] | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!watchlistName) return;
    setLoading(true);
    setData(null);
    getWatchlistData(watchlistName).then(res => {
      setData(res.data);
    }).finally(() => setLoading(false));
  }, [watchlistName]);

  if (!watchlistName) return <div className="flex-1 flex items-center justify-center text-[var(--color-text-dim)]">Select a watchlist</div>;
  
  return (
    <div className="flex-1 flex flex-col relative overflow-hidden">
      {/* Premium Header */}
      <div className="px-8 py-6 glass-header sticky top-0 z-10 flex items-center justify-between">
        <h2 className="font-bold text-white text-2xl tracking-tight">{watchlistName.replace(/_/g, " ")}</h2>
        <div className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-dim)] bg-white/5 px-3 py-1.5 rounded-full">
          {data?.length || 0} Symbols
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto px-8 py-6 custom-scrollbar">
        {loading && <LoadingState message="Fetching live market data..." />}
        
        {data && (
          <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-panel-border)] bg-black/40 text-[var(--color-text-dim)] text-left select-none text-xs uppercase tracking-wider font-semibold">
                  <th className="p-4 pl-6">Symbol</th>
                  <th className="p-4 text-right">LTP</th>
                  <th className="p-4 text-right">1D Change</th>
                  <th className="p-4 text-center">5D Trend</th>
                  <th className="p-4 text-right pr-6">Volume</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-panel-border)]">
                {data.map((row) => {
                  const isPos = row.change_pct >= 0;
                  return (
                    <tr 
                      key={row.symbol} 
                      onClick={() => window.location.href = `/stock/${row.symbol}`}
                      className="hover:bg-white/5 transition-colors duration-200 group cursor-pointer"
                    >
                      <td className="p-4 pl-6">
                        <div className="flex flex-col">
                          <span className="text-white font-semibold text-[15px]">{row.symbol}</span>
                        </div>
                      </td>
                      <td className="p-4 text-right tabular-nums text-white font-medium">₹{row.ltp.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                      <td className={`p-4 text-right tabular-nums font-semibold ${isPos ? 'text-[var(--color-accent-green)]' : 'text-[var(--color-accent-red)]'}`}>
                        <div className={`inline-flex items-center px-2 py-0.5 rounded ${isPos ? 'bg-[var(--color-accent-green)]/10' : 'bg-[var(--color-accent-red)]/10'}`}>
                          {isPos ? "+" : ""}{row.change_pct.toFixed(2)}%
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center items-center">
                          <Sparkline data={row.sparkline || []} isPositive={isPos} />
                        </div>
                      </td>
                      <td className="p-4 text-right pr-6 tabular-nums text-[var(--color-text-dim)]">
                        {(row.volume / 1000).toFixed(1)}k
                      </td>
                    </tr>
                  );
                })}
                {data.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-12 text-center text-[var(--color-text-dim)]">No stocks found in this watchlist.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
