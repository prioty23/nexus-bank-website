"use client";

import { useLanguage } from "@/components/LanguageProvider";

const icons = ["◎", "▯", "⌖", "▣", "?", "≡"];

export default function ServicesSection() {
  const { t } = useLanguage();

  return (
    <section id="services" className="section-padding bg-white">
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
            {t.services.eyebrow}
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
            {t.services.title}
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            {t.services.subtitle}
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {t.services.cards.map((item: string[], index: number) => (
            <article
              key={item[0]}
              className="group flex min-h-64 flex-col rounded-[1.5rem] border border-gray-200 bg-[#F8FAFC] p-6 transition duration-300 hover:border-[#006A4E] hover:bg-[#003B2F] hover:shadow-xl hover:shadow-[#003B2F]/15"
            >
              <div className="flex items-start justify-between">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-white text-2xl font-bold text-[#006A4E] shadow-sm">
                  <span aria-hidden="true">{icons[index]}</span>
                </div>
                <span className="font-mono text-xs font-bold text-gray-400 transition group-hover:text-emerald-200">
                  0{index + 1}
                </span>
              </div>
              <h3 className="mt-7 text-xl font-semibold text-gray-950 transition group-hover:text-white">
                {item[0]}
              </h3>
              <p className="mt-3 flex-1 leading-7 text-gray-600 transition group-hover:text-emerald-50/70">
                {item[1]}
              </p>
              <a
                href="#"
                className="mt-6 inline-flex items-center justify-between border-t border-gray-200 pt-4 text-sm font-semibold text-[#006A4E] transition group-hover:border-white/15 group-hover:text-emerald-200"
              >
                {item[2]}
                <span className="transition group-hover:translate-x-1" aria-hidden="true">→</span>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
