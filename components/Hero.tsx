"use client";

import { useState } from "react";

const slides = [
  {
    badge: "Smart Banking for Modern Life",
    title: "Plan Better. Bank Smarter. Live Brighter.",
    description:
      "Manage your everyday banking with secure, simple, and future-ready financial solutions.",
    primaryLabel: "Explore Products",
    primaryHref: "#finder",
    secondaryLabel: "Open an Account",
    secondaryHref: "#open-account",
  },
  {
    badge: "Digital Banking",
    title: "Bank anytime, anywhere with confidence.",
    description:
      "Enjoy fast transfers, bill payments, account services, and secure mobile banking from one place.",
    primaryLabel: "Start Digital Banking",
    primaryHref: "#services",
    secondaryLabel: "Learn More",
    secondaryHref: "#support",
  },
  {
    badge: "Home Loan",
    title: "Move closer to your dream home.",
    description:
      "Explore flexible home financing options designed to make your dream address possible.",
    primaryLabel: "Explore Home Loans",
    primaryHref: "#finder",
    secondaryLabel: "Calculate EMI",
    secondaryHref: "#services",
  },
  {
    badge: "SME Banking",
    title: "Power your business with smarter finance.",
    description:
      "Get banking support, working capital, and digital tools built for growing businesses.",
    primaryLabel: "Explore SME Banking",
    primaryHref: "#services",
    secondaryLabel: "Talk to Us",
    secondaryHref: "#support",
  },
];

export default function Hero() {
  const [activeSlide, setActiveSlide] = useState(0);
  const slide = slides[activeSlide];

  const goToPrevious = () => {
    setActiveSlide((current) => (current === 0 ? slides.length - 1 : current - 1));
  };

  const goToNext = () => {
    setActiveSlide((current) => (current === slides.length - 1 ? 0 : current + 1));
  };

  return (
    <section className="overflow-hidden bg-[linear-gradient(135deg,rgba(0,106,78,0.12)_0%,rgba(236,253,245,0.8)_38%,#f8fafc_100%)]">
      <div className="container-custom grid gap-12 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-28">
        <div className="max-w-2xl">
          <p className="mb-5 inline-flex rounded-full bg-[#006A4E]/10 px-4 py-1 text-sm font-semibold text-[#006A4E]">
            {slide.badge}
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-gray-950 sm:text-5xl lg:text-6xl">
            {slide.title}
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-gray-600">
            {slide.description}
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a href={slide.primaryHref} className="btn-primary">
              {slide.primaryLabel}
            </a>
            <a href={slide.secondaryHref} className="btn-secondary">
              {slide.secondaryLabel}
            </a>
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              {slides.map((item, index) => (
                <button
                  key={item.title}
                  type="button"
                  onClick={() => setActiveSlide(index)}
                  aria-label={`Go to slide ${index + 1}`}
                  className={`h-3 rounded-full transition ${
                    activeSlide === index
                      ? "w-10 bg-[#006A4E]"
                      : "w-3 bg-[#006A4E]/25 hover:bg-[#006A4E]/45"
                  }`}
                />
              ))}
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={goToPrevious}
                className="inline-flex items-center justify-center rounded-full border border-[#006A4E]/20 px-4 py-2 text-sm font-semibold text-[#006A4E] transition hover:bg-[#006A4E]/5"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={goToNext}
                className="inline-flex items-center justify-center rounded-full border border-[#006A4E]/20 px-4 py-2 text-sm font-semibold text-[#006A4E] transition hover:bg-[#006A4E]/5"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-[#006A4E]/10 bg-white p-6 shadow-2xl shadow-[#006A4E]/10 sm:p-8">
          <div className="rounded-[1.75rem] bg-[#0F172A] p-6 text-white">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-emerald-300">
                  Nexus Digital Account
                </p>
                <p className="mt-4 text-sm text-gray-300">Available Balance</p>
                <p className="mt-2 text-4xl font-semibold tracking-tight">
                  $24,850.00
                </p>
              </div>
              <div className="rounded-full bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200">
                Active
              </div>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-sm font-semibold text-white">Secure Banking</p>
                <p className="mt-2 text-sm text-gray-300">Protected access</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-sm font-semibold text-white">Fast Transfer</p>
                <p className="mt-2 text-sm text-gray-300">Move funds quickly</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-sm font-semibold text-white">24/7 Support</p>
                <p className="mt-2 text-sm text-gray-300">Always available</p>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-[#006A4E]/10 bg-[#006A4E]/5 p-4 shadow-sm">
              <p className="text-sm font-semibold text-[#006A4E]">
                Secure Banking
              </p>
            </div>
            <div className="rounded-2xl border border-[#006A4E]/10 bg-[#006A4E]/5 p-4 shadow-sm">
              <p className="text-sm font-semibold text-[#006A4E]">
                Fast Transfer
              </p>
            </div>
            <div className="rounded-2xl border border-[#006A4E]/10 bg-[#006A4E]/5 p-4 shadow-sm">
              <p className="text-sm font-semibold text-[#006A4E]">24/7 Support</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
