"use client";

import { useLanguage } from "@/components/LanguageProvider";

const icons = ["◫", "▰", "⌂", "↗", "◎", "%"];

export default function NeedsSection() {
  const { t } = useLanguage();

  return (
    <section id="accounts" className="section-padding bg-white">
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
            {t.needs.eyebrow}
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
            {t.needs.title}
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            {t.needs.subtitle}
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {t.needs.cards.map((item: string[], index: number) => (
            <article
              key={item[0]}
              className="group relative overflow-hidden rounded-[1.75rem] border border-gray-100 bg-white p-7 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-[#006A4E]/20 hover:shadow-xl hover:shadow-[#006A4E]/8"
            >
              <span className="absolute right-6 top-5 text-5xl font-bold text-[#006A4E]/[0.04]">
                0{index + 1}
              </span>
              <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-[#006A4E] text-2xl font-bold text-white shadow-lg shadow-[#006A4E]/20 transition group-hover:bg-[#003B2F]">
                <span aria-hidden="true">{icons[index]}</span>
              </div>
              <p className="mt-6 text-xs font-bold uppercase tracking-[0.18em] text-[#E31B23]">
                {item[1]}
              </p>
              <h3 className="mt-2 text-xl font-semibold text-gray-950">
                {item[0]}
              </h3>
              <p className="mt-3 leading-7 text-gray-600">{item[2]}</p>
              <a
                href="#finder"
                className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[#006A4E]"
              >
                {item[3]}
                <span className="transition group-hover:translate-x-1" aria-hidden="true">→</span>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
