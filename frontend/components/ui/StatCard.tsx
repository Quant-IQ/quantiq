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
      <p className={`text-4xl font-bold mt-2 tabular-nums ${accentClass}`}>{value}</p>
    </div>
  );
}