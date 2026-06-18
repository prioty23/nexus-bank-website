import Chatbot from "@/components/Chatbot";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import { LanguageProvider } from "@/components/LanguageProvider";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Eastern Bank PLC",
  description: "Modern banking for individuals, businesses, and communities.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <LanguageProvider>
          <Header />
          <div className="flex-1">{children}</div>
          <Chatbot />
          <Footer />
        </LanguageProvider>
      </body>
    </html>
  );
}
