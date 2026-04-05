import { useState, useEffect } from "react";

const STORAGE_KEY = "intentshield_theme";

/**
 * Shared theme hook for IntentShield.
 * - Reads from localStorage on mount.
 * - Defaults to "light" if nothing is saved.
 * - Syncs `document.documentElement.classList` immediately on change
 *   so all Tailwind `dark:` variants respond instantly.
 * - Returns [theme, toggleTheme].
 */
export function useTheme() {
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") return "light";
    const saved = localStorage.getItem(STORAGE_KEY);
    // Default to light mode — only override if explicitly saved
    return saved === "dark" ? "dark" : "light";
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () =>
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));

  return [theme, toggleTheme];
}
