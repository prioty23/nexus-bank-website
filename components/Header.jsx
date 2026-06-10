"use client";

import { useState } from "react";

const customerTypes = [
  "Personal Banking",
  "SME Banking",
  "Corporate Banking",
];

const navLinks = [
  "Accounts",
  "Cards",
  "Loans",
  "Deposits",
  "Digital Banking",
  "Offers",
  "Support",
];

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="bg-[#006A4E] text-white">
        <div className="container-custom flex flex-col gap-3 py-3 text-xs font-medium sm:flex-row sm:items-center sm:justify-between sm:text-sm">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            {customerTypes.map((type) => (
              <a key={type} href="#" className="transition hover:text-white/80">
                {type}
              </a>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <span>Hotline: 10000</span>
            <button
              type="button"
              className="transition hover:text-white/80"
              aria-label="Switch language"
            >
              EN | BN
            </button>
          </div>
        </div>
      </div>

      <div className="container-custom">
        <div className="flex items-center justify-between py-4">
          <a href="#" className="text-2xl font-bold tracking-tight text-[#006A4E]">
            Nexus Bank
          </a>

          <nav className="hidden items-center gap-6 lg:flex">
            {navLinks.map((link) => (
              <a
                key={link}
                href="#"
                className="text-sm font-medium text-slate-700 transition hover:text-[#006A4E]"
              >
                {link}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <a href="#" className="btn-primary hidden lg:inline-flex">
              Login
            </a>

            <button
              type="button"
              className="inline-flex items-center justify-center rounded-md border border-slate-200 p-2 text-slate-700 lg:hidden"
              onClick={() => setIsMenuOpen((open) => !open)}
              aria-expanded={isMenuOpen}
              aria-label="Toggle navigation menu"
            >
              <span className="sr-only">Open menu</span>
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18 18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 6.75h16.5m-16.5 5.25h16.5m-16.5 5.25h16.5"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="border-t border-slate-200 py-4 lg:hidden">
            <nav className="flex flex-col gap-3">
              {navLinks.map((link) => (
                <a
                  key={link}
                  href="#"
                  className="rounded-lg px-2 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 hover:text-[#006A4E]"
                >
                  {link}
                </a>
              ))}
              <a href="#" className="btn-primary mt-2 w-full">
                Login
              </a>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
