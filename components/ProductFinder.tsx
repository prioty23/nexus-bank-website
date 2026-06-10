"use client";

import { useLanguage } from "@/components/LanguageProvider";

export default function ProductFinder() {
  const { t } = useLanguage();
  const selectGroups = [
    ["customer-type", t.finder.labels[0], t.finder.placeholders[0], t.finder.customerTypes],
    ["interest", t.finder.labels[1], t.finder.placeholders[1], t.finder.interests],
    ["priority", t.finder.labels[2], t.finder.placeholders[2], t.finder.priorities],
  ];

  return (
    <section id="finder" className="section-padding bg-[#F8FAFC]">
      <div className="container-custom">
        <div className="relative overflow-hidden rounded-[2.5rem] bg-[#003B2F] p-5 shadow-2xl shadow-[#003B2F]/20 sm:p-8 lg:p-12">
          <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full border-[48px] border-white/5" />
          <div className="pointer-events-none absolute bottom-0 left-1/3 h-48 w-48 rounded-full bg-[#E31B23]/10 blur-3xl" />

          <div className="relative grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div className="flex flex-col justify-between text-white">
              <div>
                <p className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.2em] text-emerald-200">
                  <span className="h-2 w-2 rounded-full bg-[#E31B23]" />
                  {t.finder.badge}
                </p>
                <h2 className="mt-6 text-3xl font-semibold leading-tight sm:text-4xl">
                  {t.finder.title}
                </h2>
                <p className="mt-5 max-w-xl leading-8 text-emerald-50/70">
                  {t.finder.subtitle}
                </p>
              </div>
              <div className="mt-8 grid grid-cols-3 gap-3">
                {t.finder.steps.map((step: string, index: number) => (
                  <div key={step} className="border-t border-white/20 pt-3">
                    <span className="text-xs font-bold text-emerald-300">0{index + 1}</span>
                    <p className="mt-1 text-xs text-emerald-50/70 sm:text-sm">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[1.75rem] bg-white p-6 shadow-2xl shadow-black/15 sm:p-8">
              <div className="mb-6 flex items-center justify-between gap-4 border-b border-gray-100 pb-5">
                <div>
                  <p className="text-sm font-bold text-[#006A4E]">{t.finder.formTitle}</p>
                  <p className="mt-1 text-sm text-gray-500">{t.finder.duration}</p>
                </div>
                <span className="rounded-full bg-[#006A4E]/10 px-3 py-1 text-xs font-bold text-[#006A4E]">
                  {t.finder.questionCount}
                </span>
              </div>
              <div className="space-y-5">
                {selectGroups.map(([id, label, placeholder, options]) => (
                  <div key={id as string}>
                    <label
                      htmlFor={id as string}
                      className="mb-2 block text-sm font-semibold text-gray-700"
                    >
                      {label as string}
                    </label>
                    <select
                      id={id as string}
                      defaultValue=""
                      className="w-full rounded-xl border border-gray-200 bg-[#F8FAFC] px-4 py-3.5 text-gray-700 outline-none transition focus:border-[#006A4E] focus:bg-white focus:ring-2 focus:ring-[#006A4E]/10"
                    >
                      <option value="" disabled>{placeholder as string}</option>
                      {(options as string[]).map((item) => (
                        <option key={item} value={item}>{item}</option>
                      ))}
                    </select>
                  </div>
                ))}
                <button type="button" className="btn-primary w-full justify-center gap-2">
                  {t.finder.button}
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
