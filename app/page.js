import Footer from "@/components/Footer";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import NeedsSection from "@/components/NeedsSection";
import NewsSection from "@/components/NewsSection";
import ProductFinder from "@/components/ProductFinder";
import ServicesSection from "@/components/ServicesSection";

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-gray-900">
      <Header />
      <Hero />
      <NeedsSection />
      <ProductFinder />
      <ServicesSection />
      <NewsSection />
      <Footer />
    </main>
  );
}
