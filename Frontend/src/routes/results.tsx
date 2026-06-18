import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Sparkles } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { RecommendationCard } from "@/components/RecommendationCard";
import { EmptyState } from "@/components/EmptyState";
import { SkillBadge } from "@/components/SkillBadge";
import { clearAnalysisState, getAnalysis, setAnalysis, setPendingFile } from "@/lib/analysis-store";
import type { AnalysisResult } from "@/lib/api";

export const Route = createFileRoute("/results")({
  head: () => ({
    meta: [{ title: "Your recommendations — Signal" }],
  }),
  component: Results,
});

function Results() {
  const navigate = useNavigate();
  const [result, setResult] = useState<AnalysisResult | null>(() => getAnalysis());
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setResult(getAnalysis());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && !result) {
      const t = setTimeout(() => navigate({ to: "/" }), 50);
      return () => clearTimeout(t);
    }
  }, [hydrated, result, navigate]);

  if (!result) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <main className="flex min-h-[80vh] items-center justify-center">
          <EmptyState
            icon={<FileText className="size-5 text-foreground" />}
            title="No analysis yet"
            description="Upload a resume to see your recommendations."
            action={
              <a
                href="/"
                className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background"
              >
                Upload resume
              </a>
            }
          />
        </main>
      </div>
    );
  }

  const avgScore =
    result.recommendations.length === 0
      ? 0
      : Math.round(
          result.recommendations.reduce((a, r) => a + r.matchPercentage, 0) /
            result.recommendations.length,
        );
  const top = result.recommendations[0];

  const reset = () => {
    clearAnalysisState();
    setAnalysis(null);
    setPendingFile(null);
    navigate({ to: "/" });
  };

  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="pt-28 pb-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col gap-10 lg:flex-row">
            {/* Sidebar */}
            <aside className="w-full shrink-0 lg:w-72">
              <div className="lg:sticky lg:top-24 space-y-6">
                <section className="rounded-xl border border-border bg-card p-5">
                  <p className="font-mono-tabular mb-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                    Resume
                  </p>
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex size-9 items-center justify-center rounded-lg border border-border bg-surface">
                      <FileText className="size-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{result.summary.fileName}</p>
                      {result.summary.headline && (
                        <p className="mt-0.5 text-xs text-muted-foreground">
                          {result.summary.headline}
                        </p>
                      )}
                    </div>
                  </div>

                  {result.summary.topSkills.length > 0 && (
                    <div className="mt-5">
                      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                        Top skills
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {result.summary.topSkills.map((s) => (
                          <SkillBadge key={s}>{s}</SkillBadge>
                        ))}
                      </div>
                    </div>
                  )}
                </section>

                <section className="rounded-xl border border-border bg-card p-5">
                  <p className="font-mono-tabular mb-4 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                    Match overview
                  </p>
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-[11px] text-muted-foreground">Matches</dt>
                      <dd className="font-mono-tabular mt-1 text-2xl font-semibold tracking-tighter">
                        {result.recommendations.length}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-[11px] text-muted-foreground">Avg. score</dt>
                      <dd className="font-mono-tabular mt-1 text-2xl font-semibold tracking-tighter">
                        {avgScore}%
                      </dd>
                    </div>
                    {top && (
                      <div className="col-span-2 border-t border-border pt-3">
                        <dt className="text-[11px] text-muted-foreground">Top match</dt>
                        <dd className="mt-1 text-sm font-medium">{top.jobTitle}</dd>
                        <dd className="text-xs text-muted-foreground">{top.company}</dd>
                      </div>
                    )}
                  </dl>
                </section>

                <button
                  onClick={reset}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-card py-2.5 text-sm font-medium transition-colors hover:bg-surface"
                >
                  <Upload className="size-4" />
                  Upload a different resume
                </button>
              </div>
            </aside>

            {/* Main results */}
            <section className="min-w-0 flex-1">
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35 }}
                className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-border pb-5"
              >
                <div>
                  <p className="font-mono-tabular mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                    Top recommendations
                  </p>
                  <h1 className="text-2xl font-semibold tracking-tight">
                    {result.recommendations.length} roles aligned to your profile
                  </h1>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Sparkles className="size-3.5" />
                  <span>
                    {result.explainable ? "Explanations included" : "Deterministic summaries"}
                  </span>
                </div>
              </motion.div>

              {result.recommendations.length === 0 ? (
                <EmptyState
                  icon={<FileText className="size-5" />}
                  title="No matching roles found"
                  description="We couldn't find a strong match for your current profile. Try uploading a more detailed resume."
                  action={
                    <button
                      onClick={reset}
                      className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background"
                    >
                      Upload again
                    </button>
                  }
                />
              ) : (
                <div className="space-y-5">
                  {result.recommendations.map((r, i) => (
                    <RecommendationCard key={r.id} rec={r} index={i} />
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
