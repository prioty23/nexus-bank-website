const services = [
  {
    icon: "\u{1F310}",
    title: "Internet Banking",
    description:
      "Manage accounts, transfers, bills, and statements from your browser.",
    cta: "Login Now",
  },
  {
    icon: "\u{1F4F1}",
    title: "Mobile Banking",
    description:
      "Use the Nexus mobile app for fast, secure banking anytime.",
    cta: "Get the App",
  },
  {
    icon: "\u{1F4CD}",
    title: "Branch Locator",
    description:
      "Find your nearest Nexus Bank branch and service point.",
    cta: "Find Branch",
  },
  {
    icon: "\u{1F3E7}",
    title: "ATM Locator",
    description:
      "Locate nearby ATMs for cash withdrawal and balance inquiry.",
    cta: "Find ATM",
  },
  {
    icon: "\u{1F3A7}",
    title: "Customer Support",
    description:
      "Get help with accounts, cards, loans, and digital services.",
    cta: "Contact Us",
  },
  {
    icon: "\u{1F4C4}",
    title: "Schedule of Charges",
    description:
      "View fees, charges, limits, and service-related information.",
    cta: "View Details",
  },
];

export default function ServicesSection() {
  return (
    <section id="services" className="section-padding bg-white">
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
            Services
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
            Banking services at your fingertips
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            Access essential banking services quickly, securely, and
            conveniently.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {services.map((item) => (
            <article
              key={item.title}
              className="card group border border-gray-100 p-7 hover:border-[#006A4E]/20"
            >
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[#006A4E]/10 text-2xl text-[#006A4E]">
                <span aria-hidden="true">{item.icon}</span>
              </div>
              <h3 className="mt-5 text-xl font-semibold text-gray-950">
                {item.title}
              </h3>
              <p className="mt-3 leading-7 text-gray-600">{item.description}</p>
              <a
                href="#"
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
