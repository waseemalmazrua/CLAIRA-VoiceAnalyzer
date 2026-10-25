
import { Link } from "react-router";

import clairaMark from "../assets/CLAIRA-mark-blue-512.png";

const waveform = [
  22, 38, 55, 72, 44, 84, 61, 94, 52, 76,
  35, 68, 88, 48, 70, 42, 81, 57, 34, 63,
];

const features = [
  {
    number: "01",
    title: "Medical transcription",
    description:
      "Convert clinician speech into clear, accurate, and readable medical transcripts.",
  },
  {
    number: "02",
    title: "Clinical entity extraction",
    description:
      "Identify symptoms, conditions, medications, dosages, laboratory values, and demographics.",
  },
  {
    number: "03",
    title: "Clinical report generation",
    description:
      "Generate structured summaries, SOAP notes, risk signals, and AI-assisted clinical reports.",
  },
];

function BrandLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center">
        <img
          src={clairaMark}
          alt=""
          aria-hidden="true"
          className="h-11 w-11 object-contain sm:h-12 sm:w-12"
        />
        <span className="-ml-1 text-2xl font-semibold tracking-[0.08em] text-[#155f96] sm:text-3xl">
          LAIRA
        </span>
      </div>

      <span className="hidden h-6 w-px bg-[#155f96]/20 sm:block" />
      <span className="hidden text-sm font-semibold text-[#5c7484] sm:block">
        Voice
      </span>
    </div>
  );
}

function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#f5efe6] text-[#17364f]">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-52 -top-52 h-[34rem] w-[34rem] rounded-full bg-[#155f96]/8 blur-3xl" />
        <div className="absolute -left-52 top-[40%] h-[30rem] w-[30rem] rounded-full bg-[#d59a68]/12 blur-3xl" />
        <div className="absolute bottom-[-16rem] right-[20%] h-[30rem] w-[30rem] rounded-full bg-white/45 blur-3xl" />
      </div>

      <header className="relative z-20 border-b border-[#155f96]/10 bg-[#f5efe6]/75 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-6 lg:px-8">
          <Link
            to="/"
            aria-label="CLAIRA Voice home"
            className="rounded-xl outline-none transition focus-visible:ring-2 focus-visible:ring-[#155f96]/40"
          >
            <BrandLogo />
          </Link>

          <a
            href="#features"
            className="hidden text-sm font-medium text-[#526c7d] transition hover:text-[#155f96] md:block"
          >
            Features
          </a>

          <Link
            to="/login"
            className="rounded-full border border-[#155f96]/20 bg-white/75 px-5 py-2.5 text-sm font-semibold text-[#155f96] shadow-[0_8px_24px_rgba(23,54,79,0.07)] backdrop-blur transition duration-200 hover:-translate-y-0.5 hover:border-[#155f96]/35 hover:bg-white hover:shadow-[0_12px_28px_rgba(23,54,79,0.11)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#155f96]/35"
          >
            Sign in
          </Link>
        </nav>
      </header>

      <section className="relative z-10 mx-auto grid max-w-7xl items-center gap-14 px-5 pb-20 pt-14 sm:px-6 sm:pt-16 lg:grid-cols-[1.02fr_0.98fr] lg:gap-20 lg:px-8 lg:pb-24 lg:pt-20">
        <div className="max-w-2xl">
          <div className="mb-7 inline-flex items-center gap-3 rounded-full border border-[#155f96]/15 bg-white/60 px-4 py-2 text-sm font-medium text-[#155f96] shadow-[0_6px_20px_rgba(23,54,79,0.06)] backdrop-blur">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#155f96] opacity-25" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#155f96]" />
            </span>
            CLAIRA Voice · Medical Voice Analyzer
          </div>

          <h1 className="max-w-3xl text-[3.35rem] font-semibold leading-[1.02] tracking-[-0.05em] text-[#17364f] sm:text-6xl lg:text-[4.25rem]">
            From medical conversations
            <span className="mt-1 block text-[#155f96]">
              to structured clinical intelligence.
            </span>
          </h1>

          <p className="mt-7 max-w-xl text-base leading-8 text-[#5c7484] sm:text-lg">
            CLAIRA Voice transforms clinician speech into structured clinical
            intelligence through medical transcription, entity extraction,
            SOAP notes, and AI-assisted clinical reporting.
          </p>

          <div className="mt-9 flex flex-col gap-4 sm:flex-row">
            <Link
            to="/login"
            state={{
                redirectTo: "/voice",
                message: "Please sign in to start using CLAIRA Voice.",
            }}
            className="inline-flex items-center justify-center rounded-full bg-[#155f96] px-7 py-3.5 font-semibold !text-white"
            >
            Try CLAIRA Voice
            </Link>
          </div>

          <div className="mt-11 flex flex-wrap gap-x-7 gap-y-4 text-sm text-[#6c8291]">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-[#155f96]" />
              Secure workflow
            </span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-[#155f96]" />
              Structured reports
            </span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-[#155f96]" />
              AI-assisted reasoning
            </span>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-xl lg:max-w-none">
          <div className="absolute inset-10 rounded-[3rem] bg-[#155f96]/8 blur-3xl" />
          <div className="absolute bottom-[-2rem] left-1/2 h-16 w-[72%] -translate-x-1/2 rounded-full bg-[#17364f]/12 blur-2xl" />

          <div className="relative rounded-[2rem] border border-white/85 bg-white/70 p-3 shadow-[0_24px_60px_rgba(23,54,79,0.13)] backdrop-blur-xl">
            <div className="rounded-[1.55rem] border border-[#155f96]/10 bg-[#fffdfa] p-5 sm:p-7">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-[#17364f]">
                    Voice analysis
                  </p>
                  <p className="mt-1 text-xs text-[#8395a1]">
                    patient-consultation.wav
                  </p>
                </div>

                <span className="rounded-full border border-[#26725a]/10 bg-[#dfeee8] px-3 py-1 text-xs font-semibold text-[#26725a]">
                  Completed
                </span>
              </div>

              <div className="mt-8 flex h-28 items-center justify-center gap-1.5 rounded-2xl border border-[#155f96]/5 bg-[#f5efe6] px-5">
                {waveform.map((height, index) => (
                  <span
                    key={`${height}-${index}`}
                    className="w-1.5 rounded-full bg-[#155f96] transition hover:opacity-100"
                    style={{
                      height: `${height}%`,
                      opacity: 0.38 + (index % 5) * 0.12,
                    }}
                  />
                ))}
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <article className="rounded-2xl border border-[#155f96]/10 bg-white p-5 shadow-[0_8px_24px_rgba(23,54,79,0.035)]">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8a9aa5]">
                    Transcript
                  </p>
                  <p className="mt-3 text-sm leading-6 text-[#536c7d]">
                    Patient reports persistent chest discomfort and shortness
                    of breath during activity...
                  </p>
                </article>

                <article className="rounded-2xl border border-[#155f96]/10 bg-white p-5 shadow-[0_8px_24px_rgba(23,54,79,0.035)]">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8a9aa5]">
                    Entities
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <span className="rounded-full bg-[#e4f0f7] px-3 py-1 text-xs font-medium text-[#155f96]">
                      Chest pain
                    </span>
                    <span className="rounded-full bg-[#f3e6da] px-3 py-1 text-xs font-medium text-[#98613d]">
                      Dyspnea
                    </span>
                    <span className="rounded-full bg-[#e7ecef] px-3 py-1 text-xs font-medium text-[#526978]">
                      ECG
                    </span>
                  </div>
                </article>
              </div>

              <article className="mt-4 rounded-2xl bg-[#155f96] p-5 text-white shadow-[0_14px_30px_rgba(21,95,150,0.16)]">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/65">
                    AI clinical summary
                  </p>
                  <span className="text-xs font-medium text-[#d9edf9]">
                    96% confidence
                  </span>
                </div>

                <p className="mt-3 text-sm leading-6 text-white/85">
                  Findings suggest the need for further cardiovascular
                  assessment and review of relevant clinical results.
                </p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section
        id="features"
        className="relative z-10 border-y border-[#155f96]/10 bg-white/35"
      >
        <div className="mx-auto grid max-w-7xl px-5 py-8 sm:px-6 md:grid-cols-3 lg:px-8">
          {features.map((feature, index) => (
            <article
              key={feature.number}
              className={[
                "px-1 py-7 sm:px-6",
                index > 0
                  ? "border-t border-[#155f96]/10 md:border-l md:border-t-0"
                  : "",
              ].join(" ")}
            >
              <p className="text-xs font-semibold tracking-[0.2em] text-[#155f96]/55">
                {feature.number}
              </p>
              <h2 className="mt-5 text-lg font-semibold text-[#17364f]">
                {feature.title}
              </h2>
              <p className="mt-3 max-w-sm text-sm leading-6 text-[#667d8d]">
                {feature.description}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default LandingPage;
