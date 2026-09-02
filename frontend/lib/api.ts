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

export async function getScreener(): Promise<import('./types').ScreenerResponse> {
  const res = await fetch(`${BASE_URL}/api/screener`);
  return handleResponse<import('./types').ScreenerResponse>(res);
}

export async function getIndices(): Promise<import('./types').IndicesResponse> {
  const res = await fetch(`${BASE_URL}/api/dashboard/indices`);
  return handleResponse<import('./types').IndicesResponse>(res);
}

export async function getLiveSignals(): Promise<import('./types').SignalsResponse> {
  const res = await fetch(`${BASE_URL}/api/signals/live`);
  return handleResponse<import('./types').SignalsResponse>(res);
}

export async function getWatchlists(): Promise<import('./types').WatchlistsResponse> {
  const res = await fetch(`${BASE_URL}/api/watchlists`);
  return handleResponse<import('./types').WatchlistsResponse>(res);
}

export async function getWatchlistData(name: string): Promise<import('./types').ScreenerResponse> {
  const res = await fetch(`${BASE_URL}/api/watchlists/${name}`);
  return handleResponse<import('./types').ScreenerResponse>(res);
}

export async function getStockInfo(symbol: string): Promise<import('./types').StockInfo> {
  const res = await fetch(`${BASE_URL}/api/stock/${symbol}/info`);
  return handleResponse<import('./types').StockInfo>(res);
}

export async function getStockChart(symbol: string, range: string = "1y"): Promise<import('./types').StockChartResponse> {
  const res = await fetch(`${BASE_URL}/api/stock/${symbol}/chart?range=${range}`);
  return handleResponse<import('./types').StockChartResponse>(res);
}