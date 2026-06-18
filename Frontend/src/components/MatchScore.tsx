import { cn } from "@/lib/utils";
import type { MatchLabel } from "@/lib/api";

const labelStyles: Record<MatchLabel, string> = {
  "Strong Match": "bg-emerald-50 text-emerald-700",
  "Good Match": "bg-sky-50 text-sky-700",
  "Fair Match": "bg-zinc-100 text-zinc-700",
  Stretch: "bg-amber-50 text-amber-700",
};

export function MatchScore({
  score,
  label,
  dimmed,
}: {
  score: number;
  label: MatchLabel;
  dimmed?: boolean;
}) {
  return (
    <div className="text-right">
      <div
        className={cn(
          "font-mono-tabular text-2xl font-semibold tracking-tighter",
          dimmed && "text-muted-foreground",
        )}
      >
        {score}%
      </div>
      <div
        className={cn(
          "mt-1 inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider",
          labelStyles[label],
        )}
      >
        {label}
      </div>
    </div>
  );
}
