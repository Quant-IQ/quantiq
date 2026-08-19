"use client";
import { useState, useEffect, useCallback, useRef } from "react";

export function usePolling<T>(fetchFn: () => Promise<T>, intervalMs: number) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(() => {
    fetchFn()
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [fetchFn]);

  useEffect(() => {
    fetchData(); // initial fetch
    intervalRef.current = setInterval(fetchData, intervalMs);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchData, intervalMs]);

  return { data, loading, error, refetch: fetchData };
}