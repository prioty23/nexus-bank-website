"use client";

import { translations } from "@/data/translations";
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

type Message = {
  role: "bot" | "user";
  text: string;
};

const chatbotText = translations.en.chatbot;
const CHATBOT_API_URL = "http://127.0.0.1:8000/chat";
const TYPING_MESSAGE = "Eastern AI is typing...";
const ERROR_MESSAGE =
  "Sorry, I could not connect to the chatbot server. Please try again later.";

const SESSION_STORAGE_KEY = "eastern_ai_session_id";

function createSessionId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function formatMessage(text: string) {
  const pattern =
    /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|\+?\d[\d\s-]{7,}\d|16230)/g;

  return text.split(pattern).map((part, index) => {
    const cleanPart = part.trim();

    if (cleanPart.startsWith("http://") || cleanPart.startsWith("https://")) {
      return (
        <a
          key={index}
          href={cleanPart}
          target="_blank"
          rel="noopener noreferrer"
          className="break-all font-semibold underline underline-offset-2"
        >
          {cleanPart}
        </a>
      );
    }

    if (/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(cleanPart)) {
      return (
        <a
          key={index}
          href={`mailto:${cleanPart}`}
          className="font-semibold underline underline-offset-2"
        >
          {cleanPart}
        </a>
      );
    }

    if (/^(\+?\d[\d\s-]{7,}\d|16230)$/.test(cleanPart)) {
      const phoneNumber = cleanPart.replace(/[^\d+]/g, "");

      return (
        <a
          key={index}
          href={`tel:${phoneNumber}`}
          className="font-semibold underline underline-offset-2"
        >
          {cleanPart}
        </a>
      );
    }

    return part;
  });
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: chatbotText.welcome },
  ]);

  const messageListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!messageListRef.current) {
      return;
    }

    messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
  }, [messages, isOpen]);

  const getCurrentSessionId = () => {
    const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);

    if (savedSessionId) {
      return savedSessionId;
    }

    const currentSessionId = createSessionId();
    localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId);

    return currentSessionId;
  };

  const handleEndSession = () => {
    const newSessionId = createSessionId();

    localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);

    setMessages([{ role: "bot", text: chatbotText.welcome }]);
    setInput("");
  };

  const sendMessage = async (message: string) => {
    const userMessage = message.trim();

    if (!userMessage || isLoading) {
      return;
    }

    const currentSessionId = getCurrentSessionId();

    const chatWithUserMessage: Message[] = [
      ...messages,
      { role: "user", text: userMessage },
    ];

    const chatWithTypingMessage: Message[] = [
      ...chatWithUserMessage,
      { role: "bot", text: TYPING_MESSAGE },
    ];

    setMessages(chatWithTypingMessage);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(CHATBOT_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: currentSessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Chatbot request failed");
      }

      const data = (await response.json()) as { reply?: string };
      const botReply = data.reply ?? ERROR_MESSAGE;

      setMessages([
        ...chatWithUserMessage,
        { role: "bot", text: botReply },
      ]);
    } catch {
      setMessages([
        ...chatWithUserMessage,
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

  const showQuickActions = messages.length === 1;

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        className="fixed bottom-5 right-5 z-40 inline-flex h-14 w-14 items-center justify-center rounded-full bg-[#006A4E] text-white shadow-2xl shadow-[#006A4E]/30 transition hover:bg-[#00543E] sm:bottom-6 sm:right-6 sm:h-16 sm:w-16"
        aria-label={isOpen ? chatbotText.close : chatbotText.open}
      >
        <span className="text-xl sm:text-2xl">AI</span>
      </button>

      {isOpen ? (
        <div className="fixed inset-x-3 bottom-24 z-40 max-w-[calc(100vw-1.5rem)] sm:inset-x-auto sm:right-6 sm:w-[360px] sm:max-w-[360px]">
          <div className="overflow-hidden rounded-[1.75rem] border border-[#006A4E]/10 bg-white shadow-2xl shadow-black/15">
            <div className="flex items-start justify-between gap-4 bg-[#006A4E] px-4 py-4 text-white sm:px-5">
              <div className="min-w-0">
                <p className="text-base font-semibold">{chatbotText.title}</p>
                <p className="mt-1 text-sm text-emerald-100">
                  {chatbotText.status}
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={handleEndSession}
                  disabled={isLoading}
                  className="rounded-full bg-white/10 px-3 py-2 text-xs font-medium transition hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  End
                </button>

                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-lg transition hover:bg-white/20"
                  aria-label={chatbotText.close}
                >
                  {"\u00D7"}
                </button>
              </div>
            </div>

            <div className="space-y-4 bg-[#F8FAFC] px-4 py-5 sm:px-5">
              <div
                ref={messageListRef}
                className="max-h-72 space-y-3 overflow-y-auto pr-1"
              >
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`max-w-[88%] whitespace-pre-line rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                      message.role === "bot"
                        ? "bg-white text-gray-700"
                        : "ml-auto bg-[#006A4E] text-white"
                    }`}
                  >
                    {formatMessage(message.text)}
                  </div>
                ))}
              </div>

              {showQuickActions ? (
                <div className="flex flex-wrap gap-2">
                  {chatbotText.quickActions.map((action: string) => (
                    <button
                      key={action}
                      type="button"
                      onClick={() => {
                        void sendMessage(action);
                      }}
                      disabled={isLoading}
                      className="rounded-full border border-[#006A4E]/15 bg-white px-3 py-2 text-sm font-medium text-[#006A4E] transition hover:bg-[#006A4E]/5 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              ) : null}

              <form
                onSubmit={handleSubmit}
                className="flex flex-col gap-3 min-[420px]:flex-row"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder={chatbotText.placeholder}
                  aria-label={chatbotText.placeholder}
                  disabled={isLoading}
                  className="min-w-0 flex-1 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10 disabled:cursor-not-allowed disabled:opacity-60"
                />

                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full justify-center px-5 disabled:cursor-not-allowed disabled:opacity-60 min-[420px]:w-auto"
                >
                  {chatbotText.send}
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
