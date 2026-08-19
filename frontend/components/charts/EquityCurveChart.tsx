"use client";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { EquityPoint } from "@/lib/types";

export default function EquityCurveChart({ data }: { data: EquityPoint[] }) {
  return (
    <div className="bg-panel border border-panelBorder rounded-xl p-6 h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="date" stroke="#8B98A5" fontSize={12} />
          <YAxis stroke="#8B98A5" fontSize={12} />
          <Tooltip contentStyle={{ backgroundColor: "#1B232B", border: "1px solid #232D37" }} />
          <Line type="monotone" dataKey="value" stroke="#22C55E" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}