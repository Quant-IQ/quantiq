export interface EquityPoint {
  date: string;
  value: number;
}

export interface BacktestResult {
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  equity_curve: EquityPoint[];
}

export interface Trade {
  id: number;
  timestamp: string;
  symbol: string;
  signal: "BUY" | "SELL";
  price: number;
  quantity: number | null;
}

export interface TradesResponse {
  trades: Trade[];
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface ScreenerData {
  symbol: string;
  ltp: number;
  change_pct: number;
  day_high: number;
  day_low: number;
  volume: number;
  sparkline?: number[];
}

export interface ScreenerResponse {
  data: ScreenerData[];
}

export interface IndexData {
  name: string;
  value: number;
  change: number;
  change_pct: number;
}

export interface IndicesResponse {
  indices: IndexData[];
}

export interface SignalsResponse {
  signals: Trade[];
}

export interface StockInfo {
  symbol: string;
  name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
  fifty_two_week_high?: number;
  fifty_two_week_low?: number;
  description?: string;
  previous_close?: number;
  current_price?: number;
}

export interface ChartPoint {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  value: number; // Volume
}

export interface StockChartResponse {
  data: ChartPoint[];
}

export interface WatchlistsResponse {
  watchlists: string[];
}