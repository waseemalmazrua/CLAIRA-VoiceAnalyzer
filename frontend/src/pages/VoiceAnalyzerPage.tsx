import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { supabase } from "../lib/supabase";

type Recommendation = {
  title: string;
  rationale: string;
  urgency: "high" | "medium" | "low";
};

type SoapNote = {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
};

type ClinicalReport = {
  chief_complaint: string;
  clinical_summary: string;
  key_findings: string[];
  possible_risks: string[];
  soap_note: SoapNote;
  recommendations: Recommendation[];
  disclaimer: string;
};

type AnalysisResult = {
  report: ClinicalReport;
};

type ApiErrorResponse = {
  detail?: string;
  message?: string;
};

const API_URL = (
  import.meta.env.VITE_API_URL ?? "http://localhost:9090"
).replace(/\/+$/, "");

function VoiceAnalyzerPage() {
  const navigate = useNavigate();

  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;

    setAudioFile(file);
    setResult(null);
    setError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!audioFile) {
      setError("Please select an audio file.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    try {
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession();

      if (sessionError || !session) {
        navigate("/login", {
          replace: true,
          state: {
            redirectTo: "/voice",
            message: "Please sign in to start using CLAIRA Voice.",
          },
        });

        return;
      }

      const formData = new FormData();

      // Must match the FastAPI endpoint:
      // file: UploadFile = File(...)
      formData.append("file", audioFile);

      const response = await fetch(`${API_URL}/analyze-audio`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
        body: formData,
      });

      if (response.status === 401) {
        await supabase.auth.signOut();

        navigate("/login", {
          replace: true,
          state: {
            redirectTo: "/voice",
            message: "Your session has expired. Please sign in again.",
          },
        });

        return;
      }

      if (!response.ok) {
        let errorMessage = `Request failed with status ${response.status}`;

        try {
          const errorData =
            (await response.json()) as ApiErrorResponse;

          errorMessage =
            errorData.detail ??
            errorData.message ??
            errorMessage;
        } catch {
          const responseText = await response.text();

          if (responseText) {
            errorMessage = responseText;
          }
        }

        throw new Error(errorMessage);
      }

      const data = (await response.json()) as AnalysisResult;

      setResult(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to analyze the audio file.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f5efe6] px-5 py-10 text-[#17364f]">
      <div className="mx-auto max-w-4xl">
        <header className="mb-10 flex items-center justify-between">
          <Link
            to="/"
            className="text-sm font-semibold text-[#155f96]"
          >
            ← Back to CLAIRA Voice
          </Link>

          <span className="text-sm font-medium text-[#6c8291]">
            Medical Voice Analyzer
          </span>
        </header>

        <section className="rounded-[2rem] border border-[#155f96]/10 bg-white/70 p-6 shadow-[0_24px_60px_rgba(23,54,79,0.10)] backdrop-blur-xl sm:p-10">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold text-[#155f96]">
              CLAIRA Voice
            </p>

            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
              Analyze a medical conversation
            </h1>

            <p className="mt-4 leading-7 text-[#667d8d]">
              Upload a medical audio recording to generate a
              transcript, extract clinical entities, and produce a
              structured clinical report.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="mt-10 rounded-3xl border border-dashed border-[#155f96]/25 bg-[#f9f6f0] p-6"
          >
            <label
              htmlFor="audio-file"
              className="block text-sm font-semibold"
            >
              Audio file
            </label>

            <div className="mt-4 flex flex-wrap items-center gap-4">
              <label
                htmlFor="audio-file"
                className="inline-flex cursor-pointer items-center rounded-full bg-[#e4f0f7] px-4 py-2 text-sm font-semibold text-[#155f96] transition hover:bg-[#d7e9f3] aria-disabled:cursor-not-allowed aria-disabled:opacity-60"
                aria-disabled={isAnalyzing}
              >
                Choose file
              </label>

              <input
                id="audio-file"
                name="file"
                type="file"
                lang="en"
                accept="audio/*,.wav,.mp3,.m4a,.webm,.flac"
                onChange={handleFileChange}
                disabled={isAnalyzing}
                className="sr-only"
              />

              <span className="text-sm text-[#8a9aa5]">
                {audioFile ? audioFile.name : "No file chosen"}
              </span>
            </div>

            {audioFile && (
              <div className="mt-4 rounded-2xl border border-[#155f96]/10 bg-white px-4 py-3">
                <p className="text-sm font-semibold text-[#345367]">
                  Selected file
                </p>

                <p className="mt-1 break-all text-sm text-[#667d8d]">
                  {audioFile.name}
                </p>

                <p className="mt-1 text-xs text-[#8a9aa5]">
                  {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            )}

            {error && (
              <div
                role="alert"
                className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!audioFile || isAnalyzing}
              className="mt-8 inline-flex min-w-44 items-center justify-center rounded-full bg-[#155f96] px-7 py-3.5 font-semibold !text-white transition hover:bg-[#104f80] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isAnalyzing
                ? "Analyzing audio..."
                : "Analyze audio"}
            </button>
          </form>
        </section>

        {result && (
          <section className="mt-8 space-y-6 rounded-[2rem] border border-[#155f96]/10 bg-white p-6 shadow-[0_18px_45px_rgba(23,54,79,0.08)] sm:p-8">
            <div>
              <p className="text-sm font-semibold text-[#155f96]">
                CLAIRA Clinical Report
              </p>

              <h2 className="mt-2 text-2xl font-semibold tracking-[-0.02em]">
                Analysis result
              </h2>
            </div>

            <div className="rounded-2xl border border-[#155f96]/10 bg-[#f9f6f0] p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#6c8291]">
                Chief complaint
              </p>

              <p className="mt-2 leading-7 text-[#345367]">
                {result.report.chief_complaint}
              </p>
            </div>

            <div className="rounded-2xl border border-[#155f96]/10 p-5">
              <h3 className="text-lg font-semibold text-[#17364f]">
                Clinical summary
              </h3>

              <p className="mt-3 leading-7 text-[#667d8d]">
                {result.report.clinical_summary}
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <div className="rounded-2xl border border-[#155f96]/10 p-5">
                <h3 className="font-semibold text-[#17364f]">
                  Key findings
                </h3>

                <ul className="mt-4 space-y-3">
                  {result.report.key_findings.map(
                    (finding, index) => (
                      <li
                        key={`${finding}-${index}`}
                        className="flex gap-3 text-sm leading-6 text-[#667d8d]"
                      >
                        <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-[#155f96]" />

                        <span>{finding}</span>
                      </li>
                    ),
                  )}
                </ul>
              </div>

              <div className="rounded-2xl border border-red-100 bg-red-50/40 p-5">
                <h3 className="font-semibold text-[#17364f]">
                  Possible risks
                </h3>

                <ul className="mt-4 space-y-3">
                  {result.report.possible_risks.map(
                    (risk, index) => (
                      <li
                        key={`${risk}-${index}`}
                        className="flex gap-3 text-sm leading-6 text-[#667d8d]"
                      >
                        <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-red-400" />

                        <span>{risk}</span>
                      </li>
                    ),
                  )}
                </ul>
              </div>
            </div>

            <div className="rounded-2xl border border-[#155f96]/10 p-5">
              <h3 className="text-lg font-semibold text-[#17364f]">
                SOAP note
              </h3>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl bg-[#f9f6f0] p-4">
                  <p className="text-sm font-semibold text-[#155f96]">
                    Subjective
                  </p>

                  <p className="mt-2 text-sm leading-6 text-[#667d8d]">
                    {result.report.soap_note.subjective}
                  </p>
                </div>

                <div className="rounded-2xl bg-[#f9f6f0] p-4">
                  <p className="text-sm font-semibold text-[#155f96]">
                    Objective
                  </p>

                  <p className="mt-2 text-sm leading-6 text-[#667d8d]">
                    {result.report.soap_note.objective}
                  </p>
                </div>

                <div className="rounded-2xl bg-[#f9f6f0] p-4">
                  <p className="text-sm font-semibold text-[#155f96]">
                    Assessment
                  </p>

                  <p className="mt-2 text-sm leading-6 text-[#667d8d]">
                    {result.report.soap_note.assessment}
                  </p>
                </div>

                <div className="rounded-2xl bg-[#f9f6f0] p-4">
                  <p className="text-sm font-semibold text-[#155f96]">
                    Plan
                  </p>

                  <p className="mt-2 text-sm leading-6 text-[#667d8d]">
                    {result.report.soap_note.plan}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-[#17364f]">
                Recommendations
              </h3>

              <div className="mt-4 space-y-4">
                {result.report.recommendations.map(
                  (recommendation, index) => (
                    <div
                      key={`${recommendation.title}-${index}`}
                      className="rounded-2xl border border-[#155f96]/10 p-5"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <h4 className="font-semibold text-[#17364f]">
                          {recommendation.title}
                        </h4>

                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
                            recommendation.urgency === "high"
                              ? "bg-red-100 text-red-700"
                              : recommendation.urgency === "medium"
                                ? "bg-amber-100 text-amber-700"
                                : "bg-emerald-100 text-emerald-700"
                          }`}
                        >
                          {recommendation.urgency}
                        </span>
                      </div>

                      <p className="mt-3 text-sm leading-6 text-[#667d8d]">
                        {recommendation.rationale}
                      </p>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm leading-6 text-amber-900">
                <span className="font-semibold">
                  Clinical disclaimer:{" "}
                </span>

                {result.report.disclaimer}
              </p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

export default VoiceAnalyzerPage;