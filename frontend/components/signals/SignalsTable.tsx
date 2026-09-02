import { Trade } from "@/lib/types";
import SignalRow from "./SignalRow";
import { AnimatePresence } from "framer-motion";

export default function SignalsTable({ trades }: { trades: Trade[] }) {
  return (
    <div className="bg-panel border border-panelBorder rounded-xl overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-panelBorder text-textMuted text-left">
            <th className="p-4 font-medium">Time</th>
            <th className="p-4 font-medium">Symbol</th>
            <th className="p-4 font-medium">Signal</th>
            <th className="p-4 font-medium text-right">Price</th>
            <th className="p-4 font-medium text-right">Qty</th>
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {trades.map((trade) => (
              <SignalRow key={trade.id} trade={trade} />
            ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  );
}