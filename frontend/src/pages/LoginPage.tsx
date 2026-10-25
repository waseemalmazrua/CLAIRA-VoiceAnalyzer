import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import clairaMark from "../assets/CLAIRA-mark-blue-512.png";
import { supabase } from "../lib/supabase";

type LoginLocationState = {
  redirectTo?: string;
  message?: string;
};

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const locationState = location.state as LoginLocationState | null;
  const redirectTo = locationState?.redirectTo ?? "/voice";
  const loginMessage = locationState?.message;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [authMethod, setAuthMethod] = useState<"email" | "google" | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleEmailSignIn(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    setErrorMessage("");

    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedEmail) {
      setErrorMessage("Please enter your email address.");
      return;
    }

    if (!password) {
      setErrorMessage("Please enter your password.");
      return;
    }

    setLoading(true);
    setAuthMethod("email");

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: normalizedEmail,
        password,
      });

      if (error) {
        setErrorMessage(error.message);
        return;
      }

      navigate(redirectTo, { replace: true });
    } catch {
      setErrorMessage("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
      setAuthMethod(null);
    }
  }

  async function handleGoogleSignIn() {
    setErrorMessage("");
    setLoading(true);
    setAuthMethod("google");

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}${redirectTo}`,
        },
      });

      if (error) {
        setErrorMessage(error.message);
        setLoading(false);
        setAuthMethod(null);
      }
    } catch {
      setErrorMessage(
        "Unable to continue with Google. Please try again.",
      );
      setLoading(false);
      setAuthMethod(null);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f5efe6] px-5 py-12">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -right-40 -top-40 h-96 w-96 rounded-full bg-[#155f96]/8 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[#d59a68]/10 blur-3xl" />
      </div>

      <section className="relative z-10 w-full max-w-md rounded-[2rem] border border-[#155f96]/10 bg-white/80 p-8 shadow-[0_24px_70px_rgba(23,54,79,0.12)] backdrop-blur-xl sm:p-10">
        <div className="flex flex-col items-center text-center">
          <Link
            to="/"
            aria-label="Return to CLAIRA Voice home"
            className="flex items-center rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-[#155f96]/30"
          >
            <img
              src={clairaMark}
              alt=""
              aria-hidden="true"
              className="h-14 w-14 object-contain"
            />

            <span className="-ml-1 text-3xl font-semibold tracking-[0.08em] text-[#155f96]">
              LAIRA
            </span>

            <span className="ml-3 border-l border-[#155f96]/20 pl-3 text-sm font-semibold text-[#5c7484]">
              Voice
            </span>
          </Link>

          <h1 className="mt-8 text-3xl font-semibold tracking-[-0.03em] text-[#17364f]">
            Welcome to CLAIRA Voice
          </h1>

          <p className="mt-3 max-w-sm text-sm leading-6 text-[#667d8d]">
            Sign in to analyze medical conversations and access your
            structured clinical reports.
          </p>
        </div>

        {loginMessage && (
          <div className="mt-6 rounded-2xl border border-[#155f96]/15 bg-[#e4f0f7] px-4 py-3 text-sm leading-6 text-[#155f96]">
            {loginMessage}
          </div>
        )}

        <form className="mt-8 space-y-5" onSubmit={handleEmailSignIn} noValidate>
          <div>
            <label htmlFor="email" className="mb-2 block text-sm font-semibold text-[#345367]">
              Email address
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              inputMode="email"
              placeholder="name@example.com"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setErrorMessage("");
              }}
              disabled={loading}
              className="w-full rounded-2xl border border-[#155f96]/15 bg-white px-4 py-3.5 text-[#17364f] outline-none transition placeholder:text-[#9aa9b3] focus:border-[#155f96]/40 focus:ring-4 focus:ring-[#155f96]/8 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between gap-4">
              <label htmlFor="password" className="text-sm font-semibold text-[#345367]">
                Password
              </label>

              <button
                type="button"
                disabled={loading}
                className="text-xs font-semibold text-[#155f96] transition hover:text-[#104f80] disabled:cursor-not-allowed disabled:opacity-60"
              >
                Forgot password?
              </button>
            </div>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setErrorMessage("");
              }}
              disabled={loading}
              className="w-full rounded-2xl border border-[#155f96]/15 bg-white px-4 py-3.5 text-[#17364f] outline-none transition placeholder:text-[#9aa9b3] focus:border-[#155f96]/40 focus:ring-4 focus:ring-[#155f96]/8 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          {errorMessage && (
            <div
              role="alert"
              className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
            >
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center rounded-2xl bg-[#155f96] px-5 py-3.5 font-semibold !text-white shadow-[0_14px_30px_rgba(21,95,150,0.2)] transition hover:-translate-y-0.5 hover:bg-[#104f80] disabled:cursor-not-allowed disabled:opacity-65 disabled:hover:translate-y-0"
          >
            {loading && authMethod === "email" ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="my-7 flex items-center gap-4">
          <div className="h-px flex-1 bg-[#155f96]/10" />
          <span className="text-xs font-medium uppercase tracking-[0.16em] text-[#8a9aa5]">
            Or
          </span>
          <div className="h-px flex-1 bg-[#155f96]/10" />
        </div>

        <button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="flex w-full items-center justify-center gap-3 rounded-2xl border border-[#155f96]/15 bg-white px-5 py-3.5 font-semibold text-[#345367] transition hover:-translate-y-0.5 hover:border-[#155f96]/30 hover:bg-[#fbfaf7] disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span
            aria-hidden="true"
            className="flex h-6 w-6 items-center justify-center rounded-full text-sm font-bold text-[#4285f4]"
          >
            G
          </span>

          {loading && authMethod === "google"
            ? "Connecting..."
            : "Continue with Google"}
        </button>

        <p className="mt-8 text-center text-sm text-[#718694]">
          Don&apos;t have an account?{" "}
          <button
            type="button"
            disabled={loading}
            className="font-semibold text-[#155f96] transition hover:text-[#104f80] disabled:cursor-not-allowed disabled:opacity-60"
          >
            Create account
          </button>
        </p>
      </section>
    </main>
  );
}

export default LoginPage;
