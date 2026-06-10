import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function SupportPage() {
  return (
    <InnerPageTemplate
      title="Support"
      description="Get help with banking services, branch locations, and customer support."
      cards={["Contact Us", "FAQ", "Branch Locator", "ATM Locator"]}
    />
  );
}
