import { cn } from "@/lib/utils";

type Variant = "neutral" | "gap";

export function SkillBadge({
  children,
  variant = "neutral",
  className,
}: {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-medium",
        variant === "neutral" && "border-border bg-surface text-foreground",
        variant === "gap" && "border-amber-200/70 bg-amber-50 text-amber-800",
        className,
      )}
    >
      {children}
    </span>
  );
}
