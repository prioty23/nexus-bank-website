"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { translations } from "@/data/translations";

const LanguageContext = createContext(/** @type {any} */ (null));

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState("en");

  useEffect(() => {
    const savedLanguage = window.localStorage.getItem("nexus-language");
    if (savedLanguage === "en" || savedLanguage === "bn") {
      const restoreLanguage = window.setTimeout(() => {
        setLanguage(savedLanguage);
      }, 0);

      return () => window.clearTimeout(restoreLanguage);
    }
  }, []);

  const changeLanguage = (lang) => {
    if (lang !== "en" && lang !== "bn") {
      return;
    }

    setLanguage(lang);
    window.localStorage.setItem("nexus-language", lang);
  };

  return (
    <LanguageContext.Provider
      value={{ language, changeLanguage, t: translations[language] }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

/** @returns {any} */
export function useLanguage() {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }

  return context;
}
