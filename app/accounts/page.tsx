import InnerPageTemplate from "@/components/InnerPageTemplate";

export default function AccountsPage() {
  return (
    <InnerPageTemplate
      title="Accounts"
      description="Explore savings, current, salary, and student accounts designed for your needs."
      cards={[
        "Savings Account",
        "Current Account",
        "Salary Account",
        "Student Account",
      ]}
    />
  );
}
