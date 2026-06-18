import type { AnalysisResult } from "./api";

// Minimal in-memory store shared across routes. Persists the most recent
// analysis result so /analyzing and /results can read it without prop drilling.
let current: AnalysisResult | null = null;
let pendingFile: File | null = null;
let currentAnalysisRequest: Promise<AnalysisResult> | null = null;
const ANALYSIS_STORAGE_KEY = "signal.analysis.result";

function canUseSessionStorage() {
  return typeof window !== "undefined" && typeof window.sessionStorage !== "undefined";
}

function readStoredAnalysis() {
  if (!canUseSessionStorage()) return null;

  try {
    const raw = window.sessionStorage.getItem(ANALYSIS_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AnalysisResult) : null;
  } catch {
    return null;
  }
}

export function setAnalysis(result: AnalysisResult | null) {
  current = result;

  if (!canUseSessionStorage()) return;

  try {
    if (result) {
      window.sessionStorage.setItem(ANALYSIS_STORAGE_KEY, JSON.stringify(result));
    } else {
      window.sessionStorage.removeItem(ANALYSIS_STORAGE_KEY);
    }
  } catch {
    // Ignore storage failures and fall back to in-memory state.
  }
}
export function getAnalysis() {
  if (!current) {
    current = readStoredAnalysis();
  }
  return current;
}
export function setAnalysisRequest(request: Promise<AnalysisResult> | null) {
  currentAnalysisRequest = request;
}
export function getAnalysisRequest() {
  return currentAnalysisRequest;
}
export function setPendingFile(f: File | null) {
  pendingFile = f;
}
export function getPendingFile() {
  return pendingFile;
}

export function clearAnalysisState() {
  current = null;
  pendingFile = null;
  currentAnalysisRequest = null;

  if (!canUseSessionStorage()) return;

  try {
    window.sessionStorage.removeItem(ANALYSIS_STORAGE_KEY);
  } catch {
    // Ignore storage failures and fall back to in-memory state.
  }
}
