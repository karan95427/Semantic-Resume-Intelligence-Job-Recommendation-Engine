import { Link } from "@tanstack/react-router";
import { MoonStar, SunMedium } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "light" | "dark";

function getPreferredTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const stored = window.localStorage.getItem("signal.theme");
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark");
  window.localStorage.setItem("signal.theme", theme);
}

export function Navbar() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const preferred = getPreferredTheme();
    setTheme(preferred);
    applyTheme(preferred);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    applyTheme(nextTheme);
  };

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            SIGNAL
          </Link>
          <div className="hidden gap-6 text-sm font-medium text-muted-foreground md:flex">
            <a href="/#how" className="transition-colors hover:text-foreground">
              How it works
            </a>
            <a href="/#methodology" className="transition-colors hover:text-foreground">
              Methodology
            </a>
            <a href="/#faq" className="transition-colors hover:text-foreground">
              FAQ
            </a>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {theme === "dark" ? <SunMedium className="size-4" /> : <MoonStar className="size-4" />}
            <span className="hidden sm:inline">{theme === "dark" ? "Light mode" : "Dark mode"}</span>
          </button>
          <a
            href="/#upload"
            className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
          >
            Analyze resume
          </a>
        </div>
      </div>
    </nav>
  );
}
