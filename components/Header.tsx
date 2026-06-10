"use client";

import { useLanguage } from "@/components/LanguageProvider";
import Link from "next/link";
import { useState } from "react";

const navRoutes = [
  ["/accounts", ["/accounts", "/accounts", "/accounts", "/accounts"]],
  ["/cards", ["/cards", "/cards", "/cards", "/cards"]],
  ["/loans", ["/loans", "/loans", "/loans", "/loans"]],
  ["/deposits", ["/deposits", "/deposits", "/deposits", "/deposits"]],
  ["/digital-banking", ["/digital-banking", "/digital-banking", "/digital-banking", "/digital-banking"]],
  ["/offers", ["/offers", "/offers", "/offers", "/offers"]],
  ["/support", ["/support", "/support", "/support", "/support"]],
];

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { language, changeLanguage, t } = useLanguage();

  const navItems: Array<{
    label: string;
    href: string;
    links: Array<{ label: string; href: string }>;
  }> = t.header.navigation.map(
    ([label, links]: [string, string[]], index: number) => ({
      label,
      href: navRoutes[index][0] as string,
      links: links.map((linkLabel, linkIndex) => ({
        label: linkLabel,
        href: (navRoutes[index][1] as string[])[linkIndex],
      })),
    }),
  );

  const languageButton = (lang: "en" | "bn", label: string) => (
    <button
      type="button"
      onClick={() => changeLanguage(lang)}
      aria-pressed={language === lang}
      className={`border-b-2 pb-0.5 transition ${
        language === lang
          ? "border-[#006A4E] font-bold text-[#006A4E]"
          : "border-transparent text-gray-500 hover:text-[#006A4E]"
      }`}
    >
      {label}
    </button>
  );

  return (
    <header className="sticky top-0 z-30 bg-white shadow-sm">
      <div className="container-custom flex items-center justify-between py-4">
        <Link href="/" className="text-2xl font-semibold tracking-tight text-[#006A4E]">
          Nexus Bank
        </Link>

        <nav className="hidden items-center gap-2 lg:flex">
          {navItems.map((item) => (
            <div key={item.href} className="group relative">
              <Link
                href={item.href}
                className="inline-flex items-center rounded-full px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E]"
              >
                {item.label}
              </Link>
              <div className="invisible absolute left-0 top-full z-20 mt-3 w-64 rounded-[1.5rem] border border-gray-100 bg-white p-3 opacity-0 shadow-xl shadow-black/8 transition duration-200 group-hover:visible group-hover:opacity-100">
                {item.links.map((link) => (
                  <Link
                    key={link.label}
                    href={link.href}
                    className="block rounded-xl px-4 py-3 text-sm text-gray-600 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E]"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-3 text-sm font-medium xl:flex">
            <span className="text-[#006A4E]">{t.header.hotline}: 16666</span>
            <span className="text-gray-300">|</span>
            {languageButton("en", "EN")}
            <span className="text-gray-300">|</span>
            {languageButton("bn", "BN")}
          </div>
          <Link href="/support" className="hidden btn-primary sm:inline-flex">
            {t.header.login}
          </Link>
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
        <div className="container-custom hidden items-center gap-5 py-3 text-sm text-gray-600 md:flex">
          {t.header.topLinks.map((item: string, index: number) => (
            <div key={item} className="flex items-center gap-5">
              {index > 0 ? <span className="text-gray-300">|</span> : null}
              <a href="#" className="transition hover:text-[#006A4E]">{item}</a>
            </div>
          ))}
        </div>
      </div>

      {menuOpen ? (
        <div className="border-t border-black/5 bg-white lg:hidden">
          <div className="container-custom space-y-3 py-4">
            <div className="flex items-center justify-between rounded-2xl bg-[#F8FAFC] px-4 py-3 text-sm font-medium">
              <span className="text-[#006A4E]">{t.header.hotline}: 16666</span>
              <div className="flex items-center gap-3">
                {languageButton("en", "EN")}
                <span className="text-gray-300">|</span>
                {languageButton("bn", "BN")}
              </div>
            </div>
            {t.header.topLinks.map((item: string) => (
              <a
                key={item}
                href="#"
                onClick={() => setMenuOpen(false)}
                className="block rounded-2xl px-4 py-3 text-sm font-medium text-gray-700 transition hover:bg-[#006A4E]/5 hover:text-[#006A4E]"
              >
                {item}
              </a>
            ))}
            {navItems.map((item) => (
              <div key={item.href} className="rounded-2xl border border-gray-100 bg-gray-50/60 px-4 py-3">
                <Link
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  className="block text-sm font-semibold text-gray-800"
                >
                  {item.label}
                </Link>
                <div className="mt-3 space-y-2 pl-4">
                  {item.links.map((link) => (
                    <Link
                      key={link.label}
                      href={link.href}
                      onClick={() => setMenuOpen(false)}
                      className="block text-sm text-gray-600 transition hover:text-[#006A4E]"
                    >
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
            <Link
              href="/support"
              onClick={() => setMenuOpen(false)}
              className="btn-primary mt-3 w-full justify-center"
            >
              {t.header.login}
            </Link>
          </div>
        </div>
      ) : null}
    </header>
  );
}
