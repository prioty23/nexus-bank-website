import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function LoansPage() {
  return (
    <InnerPageTemplate
      title="Loans"
      description="Find flexible financing options for personal, home, auto, and business goals."
      cards={["Personal Loan", "Home Loan", "Auto Loan", "SME Loan"]}
    />
  );
}
