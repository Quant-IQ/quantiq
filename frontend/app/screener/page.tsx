"use client";
import { useEffect, useState, useMemo } from "react";
import { getScreener } from "@/lib/api";
import { ScreenerData } from "@/lib/types";
import ScreenerTable, { SortConfig } from "@/components/screener/ScreenerTable";
import ScreenerFilters, { FilterState } from "@/components/screener/ScreenerFilters";
import LoadingState from "@/components/ui/LoadingState";
import ErrorState from "@/components/ui/ErrorState";
import WatchlistSidebar from "@/components/dashboard/WatchlistSidebar";
import { FunnelIcon } from "@heroicons/react/24/outline";

import { useRouter } from "next/navigation";

const initialFilters: FilterState = {
  search: "",
  minPrice: "",
  maxPrice: "",
  minChange: "",
  maxChange: "",
  minVolume: "",
};

export default function ScreenerPage() {
  const router = useRouter();
  const [data, setData] = useState<ScreenerData[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [isFiltersOpen, setIsFiltersOpen] = useState(true);
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: null, direction: "desc" });

  const fetchData = () => {
    setLoading(true);
    setError(false);
    getScreener()
      .then((res) => setData(res.data))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSort = (key: keyof ScreenerData) => {
    let direction: "asc" | "desc" = "desc";
    if (sortConfig.key === key && sortConfig.direction === "desc") {
      direction = "asc";
    }
    setSortConfig({ key, direction });
  };

  const processedData = useMemo(() => {
    if (!data) return [];
    
    // Filter
    let result = data.filter((item) => {
      if (filters.search && !item.symbol.toLowerCase().includes(filters.search.toLowerCase())) return false;
      if (filters.minPrice !== "" && item.ltp < filters.minPrice) return false;
      if (filters.maxPrice !== "" && item.ltp > filters.maxPrice) return false;
      if (filters.minChange !== "" && item.change_pct < filters.minChange) return false;
      if (filters.maxChange !== "" && item.change_pct > filters.maxChange) return false;
      if (filters.minVolume !== "" && item.volume < filters.minVolume) return false;
      return true;
    });

    // Sort
    result.sort((a, b) => {
      if (!sortConfig.key) return 0;
      const aVal = a[sortConfig.key] ?? 0;
      const bVal = b[sortConfig.key] ?? 0;
      
      if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  }, [data, filters, sortConfig]);

  return (
    <div className="w-full flex h-full bg-[var(--color-bg-dark)]">
      {data && isFiltersOpen && (
        <ScreenerFilters 
          filters={filters} 
          setFilters={setFilters} 
          onClear={() => setFilters(initialFilters)} 
          onClose={() => setIsFiltersOpen(false)}
        />
      )}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        {/* Header */}
        <div className="px-8 py-6 glass-header sticky top-0 z-10 flex items-center gap-6">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => router.push("/")}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-white/5 border border-[var(--color-panel-border)] text-[var(--color-text-dim)] hover:text-white hover:bg-white/10 transition-colors"
              title="Back to Dashboard"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
            </button>
            <button 
              onClick={() => setIsFiltersOpen(!isFiltersOpen)}
              className={`flex items-center justify-center w-10 h-10 rounded-full border border-[var(--color-panel-border)] transition-colors ${isFiltersOpen ? 'bg-white/10 text-white' : 'bg-white/5 text-[var(--color-text-dim)] hover:text-white hover:bg-white/10'}`}
              title="Toggle Filters"
            >
              <FunnelIcon className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 flex items-center justify-between">
            <h1 className="font-bold text-white text-2xl tracking-tight">Advanced Screener</h1>
            <div className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-dim)] bg-white/5 px-3 py-1.5 rounded-full">
              {processedData.length} Matches
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-hidden p-8 flex flex-col">
          {loading && !data && <LoadingState message="Loading screener data..." />}
          {error && <ErrorState message="Couldn't load screener data." onRetry={fetchData} />}
          
          {data && (
            <ScreenerTable 
              data={processedData} 
              sortConfig={sortConfig} 
              onSort={handleSort}
              totalResults={data.length}
            />
          )}
        </div>
      </div>
    </div>
  );
}
