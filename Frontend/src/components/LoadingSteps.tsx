import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  steps: string[];
  activeStep: number | null;
  completedSteps: number;
}

export function LoadingSteps({ steps, activeStep, completedSteps }: Props) {
  return (
    <div className="mx-auto w-full max-w-xl rounded-xl border border-border bg-surface p-8">
      <div className="space-y-5">
        {steps.map((label, i) => {
          const done = i < completedSteps;
          const current = activeStep === i;
          return (
            <div
              key={label}
              className={cn(
                "flex items-center justify-between transition-opacity",
                !done && !current && "opacity-40",
              )}
            >
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "flex size-5 items-center justify-center rounded-full border transition-colors",
                    done && "border-success bg-success text-background",
                    current && "border-foreground/30 bg-background",
                    !done && !current && "border-border bg-background",
                  )}
                  aria-hidden
                >
                  {done && <Check className="size-3" strokeWidth={3} />}
                  {current && (
                    <span className="size-1.5 animate-pulse rounded-full bg-foreground" />
                  )}
                </span>
                <span className="text-sm font-medium">{label}</span>
              </div>
              <span className="font-mono-tabular text-[10px] uppercase tracking-wider text-muted-foreground">
                {done ? "Done" : current ? "Running" : "Pending"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
