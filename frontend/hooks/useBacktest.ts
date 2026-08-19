"use client";
import { useState, useEffect, useCallback } from "react";
import { getBacktest } from "@/lib/api";
import { BacktestResult } from "@/lib/types";

export function useBacktest() {
  const [data, setData] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getBacktest()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}