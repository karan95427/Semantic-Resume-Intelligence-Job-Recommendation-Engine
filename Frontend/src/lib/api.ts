// API client for the AI Resume & Job Matching backend.
// Configure VITE_API_BASE_URL to override the default local FastAPI server.

export type MatchLabel = "Strong Match" | "Good Match" | "Fair Match" | "Stretch";

export interface Recommendation {
  id: string;
  jobTitle: string;
  company: string;
  location: string;
  matchPercentage: number;
  matchLabel: MatchLabel;
  matchedSkills: string[];
  missingSkills: string[];
  explanation: string;
  suggestions: string[];
}

export interface ResumeSummary {
  name?: string;
  headline?: string;
  topSkills: string[];
  yearsExperience?: number;
  fileName: string;
}

export interface AnalysisResult {
  summary: ResumeSummary;
  recommendations: Recommendation[];
  generatedAt: string;
  explainable: boolean;
}

export interface BackendReadiness {
  status: "ready" | "warming" | "degraded";
  ready: boolean;
  db_ready: boolean;
  index_ready: boolean;
  jobs_loaded: number;
  warmup_in_progress: boolean;
  warmup_attempts: number;
  warmup_started_at: string | null;
  warmup_completed_at: string | null;
  last_error: {
    stage: string;
    message: string;
    at: string;
  } | null;
  message: string;
}

interface BackendRecommendationExplanation {
  summary: string;
  matched_skills: string[];
  missing_skills: string[];
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
  source: string;
}

interface BackendRecommendation {
  id: number;
  title: string;
  company?: string | null;
  location?: string | null;
  description: string;
  match_score: number;
  match_label: string;
  semantic_score: number;
  skill_match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation?: BackendRecommendationExplanation | null;
}

interface BackendRecommendationResponse {
  filename: string;
  total_jobs_compared: number;
  recommendations: BackendRecommendation[];
}

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";
const DEFAULT_UPLOAD_TIMEOUT_MS = 90_000;
const DEFAULT_READINESS_TIMEOUT_MS = 60_000;
const READINESS_REQUEST_TIMEOUT_MS = 30_000;
const READINESS_POLL_INTERVAL_MS = 1_500;

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}

async function parseErrorMessage(res: Response) {
  const text = await res.text().catch(() => "");
  if (!text) return `Request failed (${res.status})`;

  try {
    const payload = JSON.parse(text) as { detail?: string; message?: string };
    return payload.detail || payload.message || text;
  } catch {
    return text;
  }
}

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export async function getBackendReadiness(
  opts: { signal?: AbortSignal } = {},
): Promise<BackendReadiness> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), READINESS_REQUEST_TIMEOUT_MS);
  const abortFromCaller = () => controller.abort();
  opts.signal?.addEventListener("abort", abortFromCaller, { once: true });

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/ready`, {
      signal: controller.signal,
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw new Error(
        "The readiness check timed out. The backend may be unreachable even if it appears to be running.",
      );
    }
    throw new Error(
      "The frontend could not reach the backend readiness endpoint. Check that the API is running on http://127.0.0.1:8000.",
    );
  } finally {
    window.clearTimeout(timeout);
    opts.signal?.removeEventListener("abort", abortFromCaller);
  }

  const payload = (await res.json()) as BackendReadiness;

  if (!res.ok && res.status !== 503) {
    throw new Error(payload.message || `Readiness check failed (${res.status})`);
  }

  return payload;
}

export async function waitForBackendReady(
  opts: { timeoutMs?: number; signal?: AbortSignal } = {},
): Promise<BackendReadiness> {
  const timeoutMs = opts.timeoutMs ?? DEFAULT_READINESS_TIMEOUT_MS;
  const startedAt = Date.now();
  let lastSnapshot: BackendReadiness | null = null;

  while (Date.now() - startedAt < timeoutMs) {
    if (opts.signal?.aborted) {
      throw new DOMException("Aborted", "AbortError");
    }

    lastSnapshot = await getBackendReadiness({ signal: opts.signal });
    if (lastSnapshot.ready) {
      return lastSnapshot;
    }

    await delay(READINESS_POLL_INTERVAL_MS);
  }

  throw new Error(
    lastSnapshot?.message || "The backend is still warming up. Please wait a moment and try again.",
  );
}

export async function uploadResume(
  file: File,
  opts: { explain?: boolean; signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<AnalysisResult> {
  const explain = opts.explain ?? true;
  const timeoutMs = opts.timeoutMs ?? DEFAULT_UPLOAD_TIMEOUT_MS;
  const form = new FormData();
  form.append("file", file);
  form.append("top_k", "5");
  form.append("explain", String(explain));

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  const abortFromCaller = () => controller.abort();
  opts.signal?.addEventListener("abort", abortFromCaller, { once: true });

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/job-recommendations`, {
      method: "POST",
      body: form,
      signal: controller.signal,
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw new Error(
        "The backend took too long to respond. It may still be starting up. Please try again in a few seconds.",
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
    opts.signal?.removeEventListener("abort", abortFromCaller);
  }

  if (!res.ok) {
    throw new Error(await parseErrorMessage(res));
  }

  return mapBackendResult((await res.json()) as BackendRecommendationResponse);
}

function labelFor(score: number): MatchLabel {
  if (score >= 90) return "Strong Match";
  if (score >= 80) return "Good Match";
  if (score >= 70) return "Fair Match";
  return "Stretch";
}

function normalizeLabel(label: string, score: number): MatchLabel {
  if (
    label === "Strong Match" ||
    label === "Good Match" ||
    label === "Fair Match" ||
    label === "Stretch"
  ) {
    return label;
  }
  return labelFor(score);
}

function fallbackExplanation(rec: BackendRecommendation) {
  const matched = rec.matched_skills.length
    ? `Matched skills: ${rec.matched_skills.join(", ")}.`
    : "No explicit matched skills were returned.";
  const missing = rec.missing_skills.length
    ? ` Areas to strengthen: ${rec.missing_skills.join(", ")}.`
    : " No major skill gaps were detected.";

  return `${rec.title} scored ${Math.round(rec.match_score)}%. ${matched}${missing}`;
}

function mapBackendResult(payload: BackendRecommendationResponse): AnalysisResult {
  const topSkills = Array.from(
    new Set(payload.recommendations.flatMap((rec) => rec.matched_skills)),
  ).slice(0, 8);

  return {
    summary: {
      headline: `${payload.total_jobs_compared} jobs compared`,
      topSkills,
      fileName: payload.filename,
    },
    recommendations: payload.recommendations.map((rec) => ({
      id: String(rec.id),
      jobTitle: rec.title,
      company: rec.company?.trim() || "Job dataset",
      location: rec.location?.trim() || "Location not specified",
      matchPercentage: Math.round(rec.match_score),
      matchLabel: normalizeLabel(rec.match_label, rec.match_score),
      matchedSkills: rec.matched_skills,
      missingSkills: rec.missing_skills,
      explanation: rec.explanation?.summary || fallbackExplanation(rec),
      suggestions: rec.explanation?.improvement_suggestions ?? [],
    })),
    generatedAt: new Date().toISOString(),
    explainable: payload.recommendations.some((rec) => Boolean(rec.explanation)),
  };
}
