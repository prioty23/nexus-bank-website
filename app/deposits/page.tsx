import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function DepositsPage() {
  return (
    <InnerPageTemplate
      title="Deposits"
      description="Grow your money with secure fixed deposit and savings solutions."
      cards={[
        "Fixed Deposit",
        "Monthly Savings",
        "Term Deposit",
        "Deposit Calculator",
      ]}
    />
  );
}
