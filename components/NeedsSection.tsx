const needs = [
  {
    icon: "AC",
    title: "Accounts",
    description:
      "Open savings, current, and salary accounts with simple digital onboarding.",
    cta: "View Accounts",
  },
  {
    icon: "CR",
    title: "Cards",
    description:
      "Explore debit, credit, and prepaid cards designed for secure spending.",
    cta: "Explore Cards",
  },
  {
    icon: "LN",
    title: "Loans",
    description:
      "Get personal, home, auto, and business loans with flexible repayment options.",
    cta: "Find Loans",
  },
  {
    icon: "DP",
    title: "Deposits",
    description:
      "Grow your savings with fixed deposit and recurring deposit solutions.",
    cta: "See Deposits",
  },
  {
    icon: "DB",
    title: "Digital Banking",
    description:
      "Bank anytime using secure internet banking and mobile app services.",
    cta: "Go Digital",
  },
  {
    icon: "OF",
    title: "Offers",
    description:
      "Discover lifestyle, shopping, travel, and dining offers from Nexus Bank.",
    cta: "View Offers",
  },
];

export default function NeedsSection() {
  return (
    <section id="accounts" className="section-padding bg-white">
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
            Your Needs
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
            What are you looking for?
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            Choose a banking solution that fits your everyday financial needs.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {needs.map((item) => (
            <article
              key={item.title}
              className="card group border border-gray-100 p-7 hover:border-[#006A4E]/20"
            >
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[#006A4E]/10 text-sm font-bold tracking-wide text-[#006A4E]">
                <span aria-hidden="true">{item.icon}</span>
              </div>
              <h3 className="mt-5 text-xl font-semibold text-gray-950">
                {item.title}
              </h3>
              <p className="mt-3 leading-7 text-gray-600">{item.description}</p>
              <a
                href="#finder"
                className="mt-6 inline-flex items-center text-sm font-semibold text-[#006A4E] transition group-hover:translate-x-1"
              >
                {item.cta}
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
