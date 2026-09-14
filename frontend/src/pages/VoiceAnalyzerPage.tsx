import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { supabase } from "../lib/supabase";

type AnalysisResult = {
  transcript?: string;
  entities?: unknown;
  clinical_report?: unknown;
  [key: string]: unknown;
};

type ApiErrorResponse = {
  detail?: string;
  message?: string;
};

const API_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:9090";

function VoiceAnalyzerPage() {
  const navigate = useNavigate();

  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0] ?? null;

    setAudioFile(file);
    setResult(null);
    setError("");
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
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
            message:
              "Please sign in to start using CLAIRA Voice.",
          },
        });

        return;
      }

      const formData = new FormData();

      // Must match:
      // file: UploadFile = File(...)
      formData.append("file", audioFile);

      const response = await fetch(
        `${API_URL}/analyze-audio`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
          body: formData,
        },
      );

      if (response.status === 401) {
        await supabase.auth.signOut();

        navigate("/login", {
          replace: true,
          state: {
            redirectTo: "/voice",
            message:
              "Your session has expired. Please sign in again.",
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

            <input
              id="audio-file"
              name="file"
              type="file"
              accept="audio/*,.wav,.mp3,.m4a,.webm"
              onChange={handleFileChange}
              disabled={isAnalyzing}
              className="mt-4 block w-full rounded-2xl border border-[#155f96]/15 bg-white p-3 text-sm file:mr-4 file:rounded-full file:border-0 file:bg-[#e4f0f7] file:px-4 file:py-2 file:font-semibold file:text-[#155f96] disabled:cursor-not-allowed disabled:opacity-60"
            />

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
              className="mt-6 inline-flex min-w-44 items-center justify-center rounded-full bg-[#155f96] px-7 py-3.5 font-semibold !text-white transition hover:bg-[#104f80] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isAnalyzing
                ? "Analyzing audio..."
                : "Analyze audio"}
            </button>
          </form>
        </section>

        {result && (
          <section className="mt-8 rounded-[2rem] border border-[#155f96]/10 bg-white p-6 shadow-[0_18px_45px_rgba(23,54,79,0.08)] sm:p-8">
            <h2 className="text-xl font-semibold">
              Analysis result
            </h2>

            <pre className="mt-5 max-h-[600px] overflow-auto whitespace-pre-wrap rounded-2xl bg-[#17364f] p-5 text-sm leading-6 !text-white">
              {JSON.stringify(result, null, 2)}
            </pre>
          </section>
        )}
      </div>
    </main>
  );
}

export default VoiceAnalyzerPage;