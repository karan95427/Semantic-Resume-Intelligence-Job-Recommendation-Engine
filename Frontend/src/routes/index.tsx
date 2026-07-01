import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Sparkles, Target, FileText } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { UploadZone } from "@/components/UploadZone";
import { FAQAccordion } from "@/components/FAQAccordion";
import { clearAnalysisState, setPendingFile } from "@/lib/analysis-store";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CareerLens — Semantic Job Recommendation Engine" },
      {
        name: "description",
        content:
          "Upload your resume and receive ranked, explainable job recommendations with concrete suggestions to strengthen each application.",
      },
      { property: "og:title", content: "CareerLens — Semantic Job Recommendation Engine" },
      {
        property: "og:description",
        content:
          "Deterministic skill matching, transparent scoring, and supportive guidance to close the gaps that matter.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  const navigate = useNavigate();

  const handleFile = (f: File) => {
    clearAnalysisState();
    setPendingFile(f);
    navigate({ to: "/analyzing" });
  };

  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="pt-32 pb-24">
        {/* Hero */}
        <section className="mx-auto max-w-3xl px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="font-mono-tabular mb-5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              CareerLens · v1.0
            </p>
            <h1 className="text-balance text-5xl font-semibold tracking-tight md:text-6xl">
              The professional bridge between talent and role.
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
              A deterministic matching engine built for modern hiring. No gimmicks — just precise
              skill alignment, transparent scoring, and supportive guidance.
            </p>
          </motion.div>

          <motion.div
            id="upload"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="mt-12 scroll-mt-24"
          >
            <UploadZone onFile={handleFile} />
            <p className="mt-4 text-xs text-muted-foreground">
              Your file is processed in memory and never shared with third parties.
            </p>
          </motion.div>
        </section>

        {/* Methodology / Trust */}
        <section id="methodology" className="mx-auto mt-32 max-w-5xl px-6">
          <div className="mb-12 max-w-2xl">
            <p className="font-mono-tabular mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
              How recommendations work
            </p>
            <h2 className="text-3xl font-semibold tracking-tight">
              Rankings are deterministic. Explanations are transparent.
            </h2>
            <p className="mt-4 text-muted-foreground">
              The same resume produces the same ranking, every time. Each match includes a clear
              explanation of why it scored where it did and what would move it higher.
            </p>
          </div>

          <div className="grid gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-3">
            <TrustCard
              icon={<Target className="size-4" />}
              title="Deterministic matching"
              body="Sentence-transformer embeddings + FAISS retrieval produce stable, reproducible rankings — not probabilistic guesses."
            />
            <TrustCard
              icon={<ShieldCheck className="size-4" />}
              title="Privacy first"
              body="Resumes are processed ephemerally. We don't sell data, build profiles, or share with recruiters without consent."
            />
            <TrustCard
              icon={<Sparkles className="size-4" />}
              title="Explainable, with fallbacks"
              body="LLM-generated explanations are cached and degrade gracefully to deterministic summaries if the model is unavailable."
            />
          </div>
        </section>

        {/* How it works */}
        <section id="how" className="mx-auto mt-32 max-w-5xl px-6">
          <div className="mb-12 flex items-end justify-between">
            <div>
              <p className="font-mono-tabular mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                Process
              </p>
              <h2 className="text-3xl font-semibold tracking-tight">Four steps. One upload.</h2>
            </div>
          </div>

          <ol className="grid gap-6 md:grid-cols-4">
            {[
              {
                n: "01",
                t: "Upload",
                d: "Drop a PDF resume. We parse structure and content client-side.",
              },
              {
                n: "02",
                t: "Match",
                d: "Skills and experience are embedded and matched against open roles.",
              },
              { n: "03", t: "Rank", d: "Roles are ranked deterministically by skill alignment." },
              {
                n: "04",
                t: "Explain",
                d: "Each match comes with reasons and concrete suggestions.",
              },
            ].map((s) => (
              <li key={s.n} className="rounded-xl border border-border bg-card p-5">
                <div className="font-mono-tabular text-xs font-semibold text-muted-foreground">
                  {s.n}
                </div>
                <h3 className="mt-3 text-base font-semibold">{s.t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.d}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* Features detail */}
        <section className="mx-auto mt-32 max-w-5xl px-6">
          <div className="grid gap-10 md:grid-cols-2">
            <Feature
              title="Resume matching"
              body="Semantic embeddings capture the meaning of your experience, not just keywords — so 'React' and 'modern frontend' aren't treated as strangers."
            />
            <Feature
              title="Skill gap analysis"
              body="Each role surfaces the specific skills that would meaningfully strengthen your application, framed supportively."
            />
            <Feature
              title="LLM explanations"
              body="A short, human-readable rationale accompanies every match — what aligned, what didn't, and what to do next."
            />
            <Feature
              title="Improvement recommendations"
              body="Practical, action-oriented suggestions you can apply to your next revision, not generic advice."
            />
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="mx-auto mt-32 max-w-3xl px-6">
          <p className="font-mono-tabular mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            FAQ
          </p>
          <h2 className="mb-10 text-3xl font-semibold tracking-tight">Common questions</h2>
          <FAQAccordion
            items={[
              {
                q: "Is my resume stored?",
                a: "No. Files are parsed in memory for matching and discarded once your session ends. We never sell or share resume contents.",
              },
              {
                q: "How are match scores calculated?",
                a: "A sentence-transformer model embeds your skills and experience; FAISS retrieves the closest roles; a deterministic ranking layer normalises scores between 0 and 100.",
              },
              {
                q: "Will I get the same recommendations next time?",
                a: "Yes. The matching engine is deterministic — the same resume produces the same ranked list, even if explanations are regenerated.",
              },
              {
                q: "What happens if the explanation model is unavailable?",
                a: "Explanations gracefully fall back to a deterministic summary built from matched and missing skills. The ranking itself is unaffected.",
              },
              {
                q: "Do you only support PDF resumes?",
                a: "For now, yes. PDF is the most reliable format for accurate parsing. DOCX support is on the roadmap.",
              },
            ]}
          />
        </section>

        {/* CTA */}
        <section className="mx-auto mt-32 max-w-3xl px-6 text-center">
          <div className="rounded-2xl border border-border bg-surface px-8 py-12">
            <FileText className="mx-auto mb-4 size-5 text-foreground" />
            <h2 className="text-2xl font-semibold tracking-tight">Ready when you are.</h2>
            <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
              Upload a PDF and receive ranked recommendations in under a minute.
            </p>
            <a
              href="#upload"
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
            >
              Analyze resume <ArrowRight className="size-4" />
            </a>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

function TrustCard({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="bg-card p-6">
      <div className="mb-4 flex size-8 items-center justify-center rounded-md border border-border bg-surface text-foreground">
        {icon}
      </div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
    </div>
  );
}

function Feature({ title, body }: { title: string; body: string }) {
  return (
    <div className="border-l border-border pl-6">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
    </div>
  );
}
