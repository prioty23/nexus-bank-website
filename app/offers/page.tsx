import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function OffersPage() {
  return (
    <InnerPageTemplate
      title="Offers"
      description="Enjoy shopping, dining, travel, and lifestyle offers with Nexus Bank."
      cards={[
        "Shopping Offers",
        "Dining Offers",
        "Travel Offers",
        "Lifestyle Offers",
      ]}
    />
  );
}
