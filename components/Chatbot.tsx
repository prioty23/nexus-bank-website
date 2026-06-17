"use client";

import { useLanguage } from "@/components/LanguageProvider";
import { FormEvent, useEffect, useRef, useState } from "react";

type BotTranslationKey = "welcome";

type Message = {
  role: "bot" | "user";
  text?: string;
  translationKey?: BotTranslationKey;
};

const CHATBOT_API_URL = "http://127.0.0.1:8000/chat";
const TYPING_MESSAGE = "Nexus AI is typing...";
const ERROR_MESSAGE =
  "Sorry, I could not connect to the chatbot server. Please try again later.";

export default function Chatbot() {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", translationKey: "welcome" },
  ]);
  const messageListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!messageListRef.current) {
      return;
    }

    messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
  }, [messages, isOpen]);

  const resolveBotMessage = (translationKey: BotTranslationKey) => {
    return t.chatbot[translationKey];
  };

  const sendMessage = async (message: string) => {
    const trimmed = message.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setMessages((current) => [
      ...current,
      { role: "user", text: trimmed },
      { role: "bot", text: TYPING_MESSAGE },
    ]);
    setInput("");

    setIsLoading(true);

    try {
      const response = await fetch(CHATBOT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          session_id: "frontend-session",
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data: { reply?: string } = await response.json();

      setMessages((current) => [
        ...current.slice(0, -1),
        { role: "bot", text: data.reply ?? ERROR_MESSAGE },
      ]);
    } catch {
      setMessages((current) => [
        ...current.slice(0, -1),
        { role: "bot", text: ERROR_MESSAGE },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await sendMessage(input);
  };

  const showQuickActions =
    messages.length === 1 && messages[0]?.translationKey === "welcome";

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        className="fixed bottom-5 right-5 z-40 inline-flex h-14 w-14 items-center justify-center rounded-full bg-[#006A4E] text-white shadow-2xl shadow-[#006A4E]/30 transition hover:bg-[#00543E] sm:bottom-6 sm:right-6 sm:h-16 sm:w-16"
        aria-label={isOpen ? t.chatbot.close : t.chatbot.open}
      >
        <span className="text-xl sm:text-2xl">AI</span>
      </button>

      {isOpen ? (
        <div className="fixed inset-x-3 bottom-24 z-40 max-w-[calc(100vw-1.5rem)] sm:inset-x-auto sm:right-6 sm:w-[360px] sm:max-w-[360px]">
          <div className="overflow-hidden rounded-[1.75rem] border border-[#006A4E]/10 bg-white shadow-2xl shadow-black/15">
            <div className="flex items-start justify-between gap-4 bg-[#006A4E] px-4 py-4 text-white sm:px-5">
              <div className="min-w-0">
                <p className="text-base font-semibold">{t.chatbot.title}</p>
                <p className="mt-1 text-sm text-emerald-100">{t.chatbot.status}</p>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white/10 text-lg transition hover:bg-white/20"
                aria-label={t.chatbot.close}
              >
                {"\u00D7"}
              </button>
            </div>

            <div className="space-y-4 bg-[#F8FAFC] px-4 py-5 sm:px-5">
              <div
                ref={messageListRef}
                className="max-h-72 space-y-3 overflow-y-auto pr-1"
              >
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                      message.role === "bot"
                        ? "bg-white text-gray-700"
                        : "ml-auto bg-[#006A4E] text-white"
                    }`}
                  >
                    {message.translationKey
                      ? resolveBotMessage(message.translationKey)
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
                      onClick={() => {
                        void sendMessage(action);
                      }}
                      disabled={isLoading}
                      className="rounded-full border border-[#006A4E]/15 bg-white px-3 py-2 text-sm font-medium text-[#006A4E] transition hover:bg-[#006A4E]/5"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              ) : null}

              <form onSubmit={handleSubmit} className="flex flex-col gap-3 min-[420px]:flex-row">
                <input
                  type="text"
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder={t.chatbot.placeholder}
                  aria-label={t.chatbot.placeholder}
                  disabled={isLoading}
                  className="min-w-0 flex-1 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10"
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full justify-center px-5 min-[420px]:w-auto"
                >
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
