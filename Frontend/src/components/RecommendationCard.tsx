import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Sparkles, Lightbulb } from "lucide-react";
import type { Recommendation } from "@/lib/api";
import { SkillBadge } from "./SkillBadge";
import { MatchScore } from "./MatchScore";
import { cn } from "@/lib/utils";

export function RecommendationCard({ rec, index }: { rec: Recommendation; index: number }) {
  const [open, setOpen] = useState(index === 0);
  const dim = rec.matchPercentage < 80;

  return (
    <motion.article
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "overflow-hidden rounded-xl border border-border bg-card transition-shadow",
        "hover:shadow-[0_1px_2px_rgba(0,0,0,0.04),0_8px_24px_-12px_rgba(0,0,0,0.08)]",
        dim && "opacity-90",
      )}
    >
      <div className="p-6">
        <div className="mb-6 flex items-start justify-between gap-6">
          <div className="min-w-0">
            <h3 className="text-lg font-semibold tracking-tight">{rec.jobTitle}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {rec.company} · {rec.location}
            </p>
          </div>
          <MatchScore score={rec.matchPercentage} label={rec.matchLabel} dimmed={dim} />
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <h4 className="mb-3 font-mono-tabular text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Matching skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {rec.matchedSkills.map((s) => (
                <SkillBadge key={s}>{s}</SkillBadge>
              ))}
            </div>
          </div>
          <div>
            <h4 className="mb-3 font-mono-tabular text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Areas to strengthen
            </h4>
            <div className="flex flex-wrap gap-2">
              {rec.missingSkills.length === 0 ? (
                <span className="text-xs text-muted-foreground">No notable gaps.</span>
              ) : (
                rec.missingSkills.map((s) => (
                  <SkillBadge key={s} variant="gap">
                    {s}
                  </SkillBadge>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center justify-between border-t border-border bg-surface px-6 py-3 text-left text-xs font-medium text-muted-foreground transition-colors hover:bg-surface/60 hover:text-foreground"
      >
        <span>{open ? "Hide analysis" : "Show analysis & suggestions"}</span>
        <ChevronDown className={cn("size-4 transition-transform", open && "rotate-180")} />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="space-y-5 border-t border-border bg-surface/40 px-6 py-5">
              <section>
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold">
                  <Sparkles className="size-3.5 text-foreground" />
                  <span>Why this match</span>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">{rec.explanation}</p>
              </section>

              {rec.suggestions.length > 0 && (
                <section>
                  <div className="mb-2 flex items-center gap-2 text-xs font-semibold">
                    <Lightbulb className="size-3.5 text-foreground" />
                    <span>How to strengthen your application</span>
                  </div>
                  <ul className="space-y-2">
                    {rec.suggestions.map((s, i) => (
                      <li
                        key={i}
                        className="flex gap-3 text-sm leading-relaxed text-muted-foreground"
                      >
                        <span className="mt-2 size-1 shrink-0 rounded-full bg-foreground/40" />
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
