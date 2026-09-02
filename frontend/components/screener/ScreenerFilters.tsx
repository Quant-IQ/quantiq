"use client";

import { ChevronDownIcon, FunnelIcon, PlusIcon, XMarkIcon } from "@heroicons/react/24/outline";

export interface FilterState {
  search: string;
  minPrice: number | "";
  maxPrice: number | "";
  minChange: number | "";
  maxChange: number | "";
  minVolume: number | "";
}

interface Props {
  filters: FilterState;
  setFilters: (f: FilterState) => void;
  onClear: () => void;
  onClose: () => void;
}

export default function ScreenerFilters({ filters, setFilters, onClear, onClose }: Props) {
  
  const update = (key: keyof FilterState, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  return (
    <div className="w-[320px] min-w-[250px] max-w-[600px] resize-x overflow-x-hidden h-full flex flex-col border-r border-[var(--color-panel-border)] bg-[#10151C] shadow-[4px_0_24px_rgba(0,0,0,0.4)] z-20 relative">
      <div className="p-6 border-b border-[var(--color-panel-border)] flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-2">
          <FunnelIcon className="w-5 h-5 text-white" />
          <h2 className="font-heading font-semibold text-white">Filters</h2>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={onClear} className="text-xs text-[var(--color-text-dim)] hover:text-white uppercase tracking-wider font-semibold transition-colors">Reset All</button>
          <button onClick={onClose} className="p-1 text-[var(--color-text-dim)] hover:text-white hover:bg-white/10 rounded-md transition-colors" title="Close Filters">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Accordion Item: Stock Universe / Search */}
        <div className="border-b border-[var(--color-panel-border)]">
          <div className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors">
            <span className="text-sm font-semibold text-white">Stock Universe</span>
            <ChevronDownIcon className="w-4 h-4 text-[var(--color-text-dim)]" />
          </div>
          <div className="px-4 pb-4">
            <input
              type="text"
              placeholder="Search by Symbol"
              value={filters.search}
              onChange={(e) => update("search", e.target.value)}
              className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
            />
          </div>
        </div>

        {/* Accordion Item: Close Price */}
        <div className="border-b border-[var(--color-panel-border)]">
          <div className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors">
            <span className="text-sm font-semibold text-white">Close Price (₹)</span>
            <ChevronDownIcon className="w-4 h-4 text-[var(--color-text-dim)]" />
          </div>
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between gap-2">
              <input
                type="number"
                placeholder="0.00"
                value={filters.minPrice}
                onChange={(e) => update("minPrice", e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white text-center placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
              />
              <span className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider flex-shrink-0 pt-0.5">to</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.maxPrice}
                onChange={(e) => update("maxPrice", e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white text-center placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
              />
            </div>
          </div>
        </div>

        {/* Accordion Item: 1D Return */}
        <div className="border-b border-[var(--color-panel-border)]">
          <div className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors">
            <span className="text-sm font-semibold text-white">1D Return (%)</span>
            <ChevronDownIcon className="w-4 h-4 text-[var(--color-text-dim)]" />
          </div>
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between gap-2">
              <input
                type="number"
                placeholder="Min %"
                value={filters.minChange}
                onChange={(e) => update("minChange", e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white text-center placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
              />
              <span className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider flex-shrink-0 pt-0.5">to</span>
              <input
                type="number"
                placeholder="Max %"
                value={filters.maxChange}
                onChange={(e) => update("maxChange", e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white text-center placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
              />
            </div>
          </div>
        </div>

        {/* Accordion Item: Volume */}
        <div className="border-b border-[var(--color-panel-border)]">
          <div className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors">
            <span className="text-sm font-semibold text-white">Daily Volume</span>
            <ChevronDownIcon className="w-4 h-4 text-[var(--color-text-dim)]" />
          </div>
          <div className="px-4 pb-4">
             <select
              value={filters.minVolume}
              onChange={(e) => update("minVolume", e.target.value === "" ? "" : Number(e.target.value))}
              className="w-full bg-[#1A222C] rounded-lg px-4 py-2.5 text-sm font-medium text-white placeholder-[var(--color-text-dim)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-green)] transition-shadow"
            >
              <option value="" className="bg-[var(--color-bg-dark)]">Any Volume</option>
              <option value="100000" className="bg-[var(--color-bg-dark)]">100k+</option>
              <option value="500000" className="bg-[var(--color-bg-dark)]">500k+</option>
              <option value="1000000" className="bg-[var(--color-bg-dark)]">1M+</option>
              <option value="5000000" className="bg-[var(--color-bg-dark)]">5M+</option>
            </select>
          </div>
        </div>

      </div>

      <div className="p-4 border-t border-[var(--color-panel-border)]">
        <button 
          onClick={() => alert("Custom filters are currently under development and will be available in the next release.")}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-[#141A21] border border-[var(--color-panel-border)] text-white font-semibold text-sm hover:bg-white/10 transition-colors shadow-lg"
        >
          <PlusIcon className="w-4 h-4" />
          Add Filter
        </button>
      </div>
    </div>
  );
}
