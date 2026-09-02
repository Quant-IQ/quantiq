"use client";

export default function Sparkline({ data, isPositive }: { data: number[], isPositive: boolean }) {
  if (!data || data.length < 2) return <div className="w-16 h-6" />;
  
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  
  // Map values to Y between 2 (top) and 22 (bottom) for a 24px height SVG
  const mapY = (val: number) => 22 - ((val - min) / range) * 20;
  
  // Map X evenly across 64px width
  const stepX = 64 / (data.length - 1);
  
  const points = data.map((val, i) => `${i * stepX},${mapY(val)}`).join(" ");
  
  const color = isPositive ? "var(--color-accent-green)" : "var(--color-accent-red)";
  
  return (
    <svg width="64" height="24" className="overflow-visible opacity-80 group-hover:opacity-100 transition-opacity drop-shadow-md">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}
