"use client";

import { useLanguage } from "@/components/LanguageProvider";
import { FormEvent, useState } from "react";

type Message = {
  role: "bot" | "user";
  text?: string;
  translationKey?: "welcome" | "reply";
};

export default function Chatbot() {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", translationKey: "welcome" },
  ]);

  const sendMessage = (message: string) => {
    const trimmed = message.trim();
    if (!trimmed) {
      return;
    }

    setMessages((current) => [
      ...current,
      { role: "user", text: trimmed },
      { role: "bot", translationKey: "reply" },
    ]);
    setInput("");
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sendMessage(input);
  };

  const showQuickActions = messages.length === 1;

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-5 right-5 z-40 inline-flex h-16 w-16 items-center justify-center rounded-full bg-[#006A4E] text-white shadow-2xl shadow-[#006A4E]/30 transition hover:bg-[#00543E] sm:bottom-6 sm:right-6"
        aria-label={t.chatbot.open}
      >
        <span className="text-2xl">AI</span>
      </button>

      {isOpen ? (
        <div className="fixed inset-x-4 bottom-24 z-40 sm:inset-x-auto sm:right-6 sm:w-[360px]">
          <div className="overflow-hidden rounded-[1.75rem] border border-[#006A4E]/10 bg-white shadow-2xl shadow-black/15">
            <div className="flex items-start justify-between gap-4 bg-[#006A4E] px-5 py-4 text-white">
              <div>
                <p className="text-base font-semibold">{t.chatbot.title}</p>
                <p className="mt-1 text-sm text-emerald-100">{t.chatbot.status}</p>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-lg transition hover:bg-white/20"
                aria-label={t.chatbot.close}
              >
                ×
              </button>
            </div>

            <div className="space-y-4 bg-[#F8FAFC] px-5 py-5">
              <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                      message.role === "bot"
                        ? "bg-white text-gray-700"
                        : "ml-auto bg-[#006A4E] text-white"
                    }`}
                  >
                    {message.translationKey
                      ? t.chatbot[message.translationKey]
                      : message.text}
                  </div>
                ))}
              </div>

              {showQuickActions ? (
                <div className="flex flex-wrap gap-2">
                  {t.chatbot.quickActions.map((action: string) => (
                    <button
                      key={action}
                      type="button"
                      onClick={() => sendMessage(action)}
                      className="rounded-full border border-[#006A4E]/15 bg-white px-3 py-2 text-sm font-medium text-[#006A4E] transition hover:bg-[#006A4E]/5"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              ) : null}

              <form onSubmit={handleSubmit} className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder={t.chatbot.placeholder}
                  aria-label={t.chatbot.placeholder}
                  className="min-w-0 flex-1 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10"
                />
                <button type="submit" className="btn-primary px-5">
                  {t.chatbot.send}
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
