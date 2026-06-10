import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function CardsPage() {
  return (
    <InnerPageTemplate
      title="Cards"
      description="Discover debit, credit, and prepaid cards for secure everyday spending."
      cards={["Debit Cards", "Credit Cards", "Prepaid Cards", "Card Offers"]}
    />
  );
}
