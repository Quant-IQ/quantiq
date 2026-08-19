import { BacktestResult, TradesResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getBacktest(): Promise<BacktestResult> {
  const res = await fetch(`${BASE_URL}/api/backtest`);
  return handleResponse<BacktestResult>(res);
}

export async function getTrades(): Promise<TradesResponse> {
  const res = await fetch(`${BASE_URL}/api/trades`);
  return handleResponse<TradesResponse>(res);
}

export async function getPriceHistory(symbol: string): Promise<import('./types').Candle[]> {
  const res = await fetch(`${BASE_URL}/api/price-history?symbol=${symbol}`);
  return handleResponse<import('./types').Candle[]>(res);
}