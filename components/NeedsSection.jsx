const needItems = [
  {
    icon: "AC",
    title: "Accounts",
    description:
      "Open savings, current, and salary accounts with simple digital onboarding.",
    cta: "View Accounts",
  },
  {
    icon: "CD",
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
    <section className="bg-white">
      <div className="container-custom section-padding">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#006A4E]">
            Your Needs
          </p>
          <h2 className="mt-4 text-3xl font-bold text-slate-900 sm:text-4xl">
            What are you looking for?
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-600 sm:text-lg">
            Choose a banking solution that fits your everyday financial needs.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {needItems.map((item) => (
            <article
              key={item.title}
              className="card border border-slate-100 text-left"
            >
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-sm font-bold text-[#006A4E]">
                <span aria-hidden="true">{item.icon}</span>
              </div>

              <h3 className="mt-6 text-xl font-semibold text-slate-900">
                {item.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                {item.description}
              </p>

              <a
                href="#"
                className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[#006A4E] transition hover:gap-3"
              >
                {item.cta}
                <span aria-hidden="true">-&gt;</span>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
