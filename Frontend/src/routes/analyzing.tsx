import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";
import { LoadingSteps } from "@/components/LoadingSteps";
import { Navbar } from "@/components/Navbar";
import { waitForBackendReady, uploadResume } from "@/lib/api";
import {
  clearAnalysisState,
  getAnalysis,
  getPendingFile,
  setAnalysis,
  setPendingFile,
} from "@/lib/analysis-store";

export const Route = createFileRoute("/analyzing")({
  head: () => ({
    meta: [{ title: "Analyzing your resume - Signal" }],
  }),
  component: Analyzing,
});

const ANALYSIS_STEPS = [
  "Checking backend readiness",
  "Uploading resume",
  "Extracting resume content",
  "Matching opportunities",
  "Preparing results",
];

function Analyzing() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<number | null>(0);
  const [completedSteps, setCompletedSteps] = useState(0);

  useEffect(() => {
    const file = getPendingFile();
    if (!file) {
      if (getAnalysis()) {
        navigate({ to: "/results", replace: true });
        return;
      }

      navigate({ to: "/" });
      return;
    }

    let disposed = false;
    const controller = new AbortController();

    const run = async () => {
      let processingTimer: number | null = null;

      try {
        setActiveStep(0);
        setCompletedSteps(0);
        await waitForBackendReady({ signal: controller.signal });
        if (disposed) return;

        setCompletedSteps(1);
        setActiveStep(1);

        const uploadPromise = uploadResume(file, {
          explain: true,
          signal: controller.signal,
        });

        setCompletedSteps(2);
        setActiveStep(2);

        processingTimer = window.setTimeout(() => {
          if (disposed) return;
          setCompletedSteps(3);
          setActiveStep(3);
        }, 1200);

        const result = await uploadPromise;
        if (processingTimer !== null) {
          window.clearTimeout(processingTimer);
        }
        if (disposed) return;

        setCompletedSteps(ANALYSIS_STEPS.length);
        setActiveStep(null);
        setAnalysis(result);
        setPendingFile(null);
        navigate({ to: "/results", replace: true });
      } catch (e) {
        if (processingTimer !== null) {
          window.clearTimeout(processingTimer);
        }
        if (disposed) return;
        setError(e instanceof Error ? e.message : "Something went wrong.");
      }
    };

    void run();

    return () => {
      disposed = true;
      controller.abort();
    };
  }, [navigate]);

  if (error) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <main className="flex min-h-[80vh] items-center justify-center px-6">
          <EmptyState
            icon={<AlertCircle className="size-5 text-destructive" />}
            title="We couldn't analyze this resume"
            description={error}
            action={
              <button
                onClick={() => {
                  clearAnalysisState();
                  navigate({ to: "/" });
                }}
                className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background"
              >
                Try a different file
              </button>
            }
          />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="flex min-h-[80vh] flex-col items-center justify-center px-6 pb-16 pt-24">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto mb-10 max-w-md text-center"
        >
          <p className="font-mono-tabular mb-3 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
            Working
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">Analyzing your resume</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            We verify backend readiness first, then process your resume and route you to the results
            page as soon as the recommendations are ready.
          </p>
        </motion.div>

        <LoadingSteps
          steps={ANALYSIS_STEPS}
          activeStep={activeStep}
          completedSteps={completedSteps}
        />
      </main>
    </div>
  );
}
