import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function DigitalBankingPage() {
  return (
    <InnerPageTemplate
      title="Digital Banking"
      description="Bank anytime, anywhere with secure digital banking services."
      cards={[
        "Internet Banking",
        "Mobile App",
        "Online Account Opening",
        "Fund Transfer",
      ]}
    />
  );
}
