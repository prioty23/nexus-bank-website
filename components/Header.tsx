"use client";

import { useLanguage } from "@/components/LanguageProvider";
import { translations } from "@/data/translations";
import Link from "next/link";
import { useState } from "react";

const topLinkRoutes = [
  "https://www.ebl.com.bd/retail/retail-deposit",
  "https://www.ebl.com.bd/sme/sme-loans",
  "https://www.ebl.com.bd/corporate/banking/Corporate-Banking-Division",
];
const EBL_HOTLINE = "16230";

const navRoutes: Array<[string, string[]]> = [
  [
    "https://www.ebl.com.bd/retail/retail-deposit",
    [
      "https://www.ebl.com.bd/retail/retail-loan",
      "https://www.ebl.com.bd/retail/retail-deposit",
      "https://www.ebl.com.bd/retail/EBL-Cards",
      "https://www.ebl.com.bd/retail-digital/ebl-skybanking",
      "https://www.ebl.com.bd/retail-ecommerce/ebl-skypay",
      "https://www.ebl.com.bd/retail/ebl-insta-account",
      "https://www.ebl.com.bd/retail/ebl-insta-banking",
      "https://www.ebl.com.bd/priority/",
      "https://www.ebl.com.bd/powerbanking",
      "https://www.ebl.com.bd/ebl-super-saver",
      "https://www.ebl.com.bd/retail/Women-Banking",
      "https://www.ebl.com.bd/agentbanking",
      "https://www.ebl.com.bd/retail/EBL-Payroll-Banking",
      "https://www.ebl.com.bd/retail/EBL-Student-Banking",
      "https://www.ebl.com.bd/retail/ebl-bancassurance",
      "https://www.ebl.com.bd/retail/ebl-retail-propositions",
    ],
  ],
  [
    "https://www.ebl.com.bd/islamicbanking",
    [
      "https://www.ebl.com.bd/islamicbanking#overview",
      "https://www.ebl.com.bd/islamic/member_ssc",
      "https://www.ebl.com.bd/islamic/islamic-retail-finance",
      "https://www.ebl.com.bd/islamic/islamic-sme-finance",
      "https://www.ebl.com.bd/islamic/islamic-corporate-finance",
      "https://www.ebl.com.bd/islamic/islamic-cards",
      "https://www.ebl.com.bd/islamic/profit-distribution",
      "https://www.ebl.com.bd/islamicbanking#iwindows",
      "https://www.ebl.com.bd/islamic/notice",
    ],
  ],
  [
    "https://www.ebl.com.bd/retail/retail-deposit",
    [
      "https://www.ebl.com.bd/retail/retail-deposit",
      "https://www.ebl.com.bd/retail-deposit/EBL-Current-Account",
      "https://www.ebl.com.bd/retail-deposit/EBL-FD",
      "https://www.ebl.com.bd/retail-deposit/EBL-Confidence",
    ],
  ],
  [
    "https://www.ebl.com.bd/retail/EBL-Cards",
    [
      "https://www.ebl.com.bd/retail/EBL-Cards",
      "https://www.ebl.com.bd/islamic/islamic-cards",
      "https://www.ebl.com.bd/retail/EBL-Cards",
      "https://www.ebl.com.bd/retail/EBL-Cards",
    ],
  ],
  [
    "https://www.ebl.com.bd/retail/retail-loan",
    [
      "https://www.ebl.com.bd/retail/retail-loan",
      "https://www.ebl.com.bd/sme/sme-loans",
      "https://www.ebl.com.bd/islamic/islamic-retail-finance",
      "https://www.ebl.com.bd/islamic/islamic-sme-finance",
    ],
  ],
  [
    "https://www.ebl.com.bd/retail-digital/ebl-skybanking",
    [
      "https://www.ebl.com.bd/retail-digital/ebl-skybanking",
      "https://www.ebl.com.bd/retail-digital/ebl-missed-call-alert-service",
      "https://www.ebl.com.bd/retail-digital/ebl-365-plus",
      "https://www.ebl.com.bd/retail-ecommerce/ebl-skypay",
    ],
  ],
  [
    "https://www.ebl.com.bd/contact",
    [
      "https://www.ebl.com.bd/contact",
      "https://www.ebl.com.bd/locator/",
      "https://www.ebl.com.bd/forms-downloads",
      "https://www.ebl.com.bd/schedule-of-charges",
    ],
  ],
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { language, changeLanguage, t } = useLanguage();

  const navItems: Array<{
    label: string;
    href: string;
    links: Array<{ label: string; href: string }>;
  }> = navRoutes.map(
    ([href, routes], index: number) => {
      const translatedItem = t.header.navigation[index];
      const fallbackItem = translations.en.header.navigation[index];
      const [label, links] =
        translatedItem?.[1]?.length === (routes as string[]).length
          ? translatedItem
          : fallbackItem;

      return {
      label,
      href: href as string,
      links: (links as string[]).map((linkLabel: string, linkIndex: number) => ({
        label: linkLabel,
        href: (routes as string[])[linkIndex],
      })),
    };
    },
  );

  const languageButton = (lang: "en" | "bn", label: string) => (
    <button
      type="button"
      onClick={() => {
        changeLanguage(lang);
        setMenuOpen(false);
      }}
      aria-pressed={language === lang}
      className={`rounded-full border px-3 py-1 text-xs font-semibold transition sm:text-sm ${
        language === lang
          ? "border-[#006A4E] bg-[#006A4E]/8 text-[#006A4E]"
          : "border-[#006A4E]/15 text-gray-500 hover:border-[#006A4E]/30 hover:text-[#006A4E]"
      }`}
    >
      {label}
    </button>
  );

  return (
    <header className="sticky top-0 z-30 bg-white shadow-sm">
      <div className="container-custom flex items-center justify-between gap-3 py-4">
        <Link
          href="/"
          onClick={() => setMenuOpen(false)}
          className="shrink-0 text-xl font-semibold tracking-tight text-[#006A4E] sm:text-2xl"
        >
          Eastern Bank PLC
        </Link>

        <nav className="hidden min-w-0 flex-1 items-center justify-center gap-1 lg:flex xl:gap-2">
          {navItems.map((item, index) => (
            <div key={item.label} className="group relative">
              <a
                href={item.href}
                className="inline-flex items-center rounded-full px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E] xl:px-4 xl:text-sm"
              >
                {item.label}
              </a>
              <div
                className={`invisible absolute top-full z-20 mt-3 max-h-[70vh] w-72 overflow-y-auto rounded-[1.5rem] border border-gray-100 bg-white p-3 opacity-0 shadow-xl shadow-black/8 transition duration-200 group-hover:visible group-hover:opacity-100 ${
                  index >= navItems.length - 2 ? "right-0" : "left-0"
                }`}
              >
                {item.links.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    className="block rounded-xl px-4 py-3 text-sm text-gray-600 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E]"
                  >
                    {link.label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <div className="hidden items-center gap-2 text-sm font-medium lg:flex">
            <span className="hidden text-[#006A4E] 2xl:inline">
              {t.header.hotline}: {EBL_HOTLINE}
            </span>
            {languageButton("en", "EN")}
            {languageButton("bn", "BN")}
          </div>
          <a href="#footer" className="hidden btn-primary min-[480px]:inline-flex">
            {t.header.login}
          </a>
          <div className="flex items-center gap-2 lg:hidden">
            {languageButton("en", "EN")}
            {languageButton("bn", "BN")}
          </div>
          <button
            type="button"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-[#006A4E]/20 text-[#006A4E] transition hover:bg-[#006A4E]/5 lg:hidden"
          >
            <span className="sr-only">Toggle navigation</span>
            <div className="flex flex-col gap-1.5">
              <span className={`block h-0.5 w-5 bg-current transition ${menuOpen ? "translate-y-2 rotate-45" : ""}`} />
              <span className={`block h-0.5 w-5 bg-current transition ${menuOpen ? "opacity-0" : ""}`} />
              <span className={`block h-0.5 w-5 bg-current transition ${menuOpen ? "-translate-y-2 -rotate-45" : ""}`} />
            </div>
          </button>
        </div>
      </div>

      <div className="border-t border-black/5 bg-[#F8FAFC]">
        <div className="container-custom hidden flex-wrap items-center gap-4 py-3 text-sm text-gray-600 md:flex">
          {t.header.topLinks.map((item: string, index: number) => (
            <div key={item} className="flex items-center gap-4">
              {index > 0 ? <span className="text-gray-300">|</span> : null}
              <a href={topLinkRoutes[index]} className="transition hover:text-[#006A4E]">{item}</a>
            </div>
          ))}
        </div>
      </div>

      {menuOpen ? (
        <div className="border-t border-black/5 bg-white lg:hidden">
          <div className="container-custom space-y-3 py-4">
            <div className="flex flex-col gap-3 rounded-2xl bg-[#F8FAFC] px-4 py-3 text-sm font-medium sm:flex-row sm:items-center sm:justify-between">
              <span className="break-words text-[#006A4E]">
                {t.header.hotline}: {EBL_HOTLINE}
              </span>
              <div className="flex flex-wrap items-center gap-2">
                {languageButton("en", "EN")}
                {languageButton("bn", "BN")}
              </div>
            </div>
            {t.header.topLinks.map((item: string) => (
              <a
                key={item}
                href={topLinkRoutes[t.header.topLinks.indexOf(item)]}
                onClick={() => setMenuOpen(false)}
                className="block rounded-2xl px-4 py-3 text-sm font-medium text-gray-700 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E]"
              >
                {item}
              </a>
            ))}
            {navItems.map((item) => (
              <div key={item.label} className="rounded-2xl border border-gray-100 bg-gray-50/60 px-4 py-3">
                <a
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  className="block text-sm font-semibold text-gray-800"
                >
                  {item.label}
                </a>
                <div className="mt-3 space-y-2 pl-4">
                  {item.links.map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      onClick={() => setMenuOpen(false)}
                      className="block text-sm text-gray-600 transition hover:text-[#006A4E]"
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
              </div>
            ))}
            <a
              href="#footer"
              onClick={() => setMenuOpen(false)}
              className="btn-primary mt-3 w-full justify-center"
            >
              {t.header.login}
            </a>
          </div>
        </div>
      ) : null}
    </header>
  );
}
