"use client";

import { useLanguage } from "@/components/LanguageProvider";

export default function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-[#003B2F] text-white">
      <div className="container-custom py-16 lg:py-20">
        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/10 lg:p-10">
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#00A878]">
                {t.footer.newsletter}
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">
                {t.footer.newsletterTitle}
              </h2>
              <p className="mt-4 max-w-2xl leading-8 text-emerald-50/75">
                {t.footer.newsletterText}
              </p>
            </div>
            <form className="flex flex-col gap-4 sm:flex-row">
              <input
                type="email"
                placeholder={t.footer.emailPlaceholder}
                aria-label={t.footer.emailPlaceholder}
                className="h-12 w-full rounded-full border border-white/15 bg-white/10 px-5 text-white placeholder:text-emerald-50/50 outline-none transition focus:border-[#00A878] focus:ring-2 focus:ring-[#00A878]/20"
              />
              <button
                type="submit"
                className="inline-flex h-12 items-center justify-center rounded-full bg-[#00A878] px-6 text-sm font-semibold text-white transition hover:bg-[#00956b]"
              >
                {t.footer.subscribe}
              </button>
            </form>
          </div>
        </div>

        <div className="mt-14 grid gap-10 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-2xl font-semibold tracking-tight text-white">Nexus Bank</p>
            <p className="mt-4 leading-8 text-emerald-50/70">{t.footer.description}</p>
            <div className="mt-6 space-y-2 text-sm text-emerald-50/80">
              <p><span className="text-[#00A878]">{t.footer.hotline}:</span> 16666</p>
              <p><span className="text-[#00A878]">Email:</span> support@nexusbank.com</p>
            </div>
          </div>

          {[
            [t.footer.bankingTitle, t.footer.bankingLinks],
            [t.footer.companyTitle, t.footer.companyLinks],
            [t.footer.supportTitle, t.footer.supportLinks],
          ].map(([title, links]) => (
            <div key={title as string}>
              <h3 className="text-lg font-semibold text-white">{title as string}</h3>
              <div className="mt-5 space-y-3 text-sm text-emerald-50/70">
                {(links as string[]).map((item) => (
                  <a key={item} href="#" className="block transition hover:text-[#00A878]">
                    {item}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col gap-4 border-t border-white/10 pt-6 text-sm text-emerald-50/65 md:flex-row md:items-center md:justify-between">
          <p>{t.footer.copyright}</p>
          <div className="flex flex-wrap gap-5">
            {t.footer.legalLinks.map((item: string) => (
              <a key={item} href="#" className="transition hover:text-[#00A878]">
                {item}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
