import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0A0E13",
        panel: "#141A21",
        panelBorder: "#232D37",
        accent: "#4ADE80", // Logo vibrant green
        textPrimary: "#F1F5F9", // Logo white/gray text
        textMuted: "#8B98A5",
        info: "#3B82F6",
        warn: "#F59E0B",
        negative: "#EF4444",
      },
      fontFamily: {
        heading: ["Sora", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["'Courier New'", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;