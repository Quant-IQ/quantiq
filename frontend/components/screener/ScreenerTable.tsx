"use client";
import { ScreenerData } from "@/lib/types";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";

export type SortConfig = {
  key: keyof ScreenerData | null;
  direction: "asc" | "desc";
};

interface Props {
  data: ScreenerData[];
  sortConfig: SortConfig;
  onSort: (key: keyof ScreenerData) => void;
  totalResults: number;
}

export default function ScreenerTable({ data, sortConfig, onSort, totalResults }: Props) {
  return (
    <div className="flex-1 flex flex-col h-full bg-[#141A21] border border-[var(--color-panel-border)] rounded-2xl shadow-2xl overflow-hidden">
      {/* Table Header / Actions */}
      <div className="px-6 py-4 flex items-center justify-between border-b border-[var(--color-panel-border)]">
        <div className="text-[var(--color-text-dim)] text-sm">
          Showing 1 - {data.length} of {totalResults} results
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent-green)] text-black text-sm font-bold hover:bg-[#1ea650] transition-colors shadow-lg">
          <ArrowDownTrayIcon className="w-4 h-4" strokeWidth={2.5} />
          Export Data
        </button>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-[#1A222C] z-10 shadow-sm border-b border-[var(--color-panel-border)]">
            <tr className="text-[var(--color-text-dim)] text-left select-none text-xs uppercase tracking-wider font-semibold">
              <th className="p-4 pl-6 cursor-pointer hover:text-white transition-colors" onClick={() => onSort("symbol")}>
                Name {sortConfig.key === "symbol" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
              <th className="p-4 text-right cursor-pointer hover:text-white transition-colors" onClick={() => onSort("ltp")}>
                Close Price {sortConfig.key === "ltp" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
              <th className="p-4 text-right cursor-pointer hover:text-white transition-colors" onClick={() => onSort("change_pct")}>
                1D Return {sortConfig.key === "change_pct" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
              <th className="p-4 text-right cursor-pointer hover:text-white transition-colors" onClick={() => onSort("day_high")}>
                High {sortConfig.key === "day_high" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
              <th className="p-4 text-right cursor-pointer hover:text-white transition-colors" onClick={() => onSort("day_low")}>
                Low {sortConfig.key === "day_low" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
              <th className="p-4 pr-6 text-right cursor-pointer hover:text-white transition-colors" onClick={() => onSort("volume")}>
                Volume {sortConfig.key === "volume" && (sortConfig.direction === "asc" ? "↑" : "↓")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-panel-border)]">
            {data.map((row) => {
              const isPos = row.change_pct >= 0;
              return (
                <tr 
                  key={row.symbol} 
                  onClick={() => window.location.href = `/stock/${row.symbol}`}
                  className="hover:bg-[var(--color-panel-border)]/50 transition-colors duration-200 group cursor-pointer"
                >
                  <td className="p-4 pl-6">
                    <div className="flex flex-col">
                      <span className="text-white font-bold text-[15px]">{row.symbol}</span>
                      <span className="text-[var(--color-text-dim)] text-[11px] font-semibold mt-0.5 uppercase tracking-widest">Equity / NSE</span>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <span className="font-mono tabular-nums text-white font-semibold text-[15px]">
                      ₹{row.ltp.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <div className={`inline-flex items-center justify-end gap-1 px-2.5 py-1 rounded-md text-xs font-bold font-mono tabular-nums ${isPos ? 'bg-[#22C55E]/10 text-[#22C55E]' : 'bg-[#F0665E]/10 text-[#F0665E]'}`}>
                      {isPos ? "+" : ""}{row.change_pct.toFixed(2)}%
                    </div>
                  </td>
                  <td className="p-4 text-right font-mono tabular-nums text-[var(--color-text-dim)] font-medium">
                    ₹{row.day_high.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="p-4 text-right font-mono tabular-nums text-[var(--color-text-dim)] font-medium">
                    ₹{row.day_low.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="p-4 pr-6 text-right font-mono tabular-nums text-[var(--color-text-dim)] font-medium">
                    {(row.volume / 1000).toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}k
                  </td>
                </tr>
              );
            })}
            {data.length === 0 && (
              <tr>
                <td colSpan={6} className="p-12 text-center text-[var(--color-text-dim)]">No stocks found matching filters.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
