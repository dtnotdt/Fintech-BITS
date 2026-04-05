/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Outfit", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50:  "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",   // cyan-500 — primary
          600: "#0891b2",
          700: "#0e7490",
          800: "#155e75",
          900: "#164e63",
        },
        accent: {
          50:  "#f5f3ff",
          100: "#ede9fe",
          400: "#a78bfa",
          500: "#8b5cf6",   // violet-500 — accent
          600: "#7c3aed",
          700: "#6d28d9",
        },
        surface: {
          50:  "#f8fafc",   // near-white page bg
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
      },
      animation: {
        "fade-in":    "fadeIn 0.35s ease-out",
        "slide-up":   "slideUp 0.35s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow":  "spin 2s linear infinite",
        "float":      "float 4s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 },                          to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: "translateY(14px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        float:   { "0%,100%": { transform: "translateY(0)" },    "50%": { transform: "translateY(-8px)" } },
      },
      backdropBlur: { xs: "2px" },
    },
  },
  plugins: [],
};
