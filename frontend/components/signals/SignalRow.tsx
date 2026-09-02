import { Trade } from "@/lib/types";
import Badge from "@/components/ui/Badge";
import { formatTimestamp } from "@/lib/utils";
import { motion } from "framer-motion";

export default function SignalRow({ trade }: { trade: Trade }) {
  return (
    <motion.tr 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="border-b border-panelBorder last:border-0"
    >
      <td className="p-4 text-textMuted">{formatTimestamp(trade.timestamp)}</td>
      <td className="p-4 text-textPrimary font-medium">{trade.symbol}</td>
      <td className="p-4"><Badge signal={trade.signal} /></td>
      <td className="p-4 text-right tabular-nums text-textPrimary">₹{trade.price.toFixed(2)}</td>
      <td className="p-4 text-right tabular-nums text-textMuted">{trade.quantity ?? "—"}</td>
    </motion.tr>
  );
}