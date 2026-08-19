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