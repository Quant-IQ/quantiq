import { motion } from "framer-motion";

export default function StatCard({
  label,
  value,
  accentClass = "text-textPrimary",
}: {
  label: string;
  value: string;
  accentClass?: string;
}) {
  return (
    <div className="bg-panel border border-panelBorder rounded-xl p-6">
      <p className="text-sm text-textMuted">{label}</p>
      <motion.p
        key={value}
        initial={{ scale: 0.9, opacity: 0.5 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className={`text-4xl font-bold mt-2 tabular-nums ${accentClass}`}
      >
        {value}
      </motion.p>
    </div>
  );
}