const newsItems = [
  {
    title: "Nexus Bank launches digital account opening service",
    category: "Digital Banking",
    date: "12 June 2026",
    description:
      "Customers can now open selected accounts online with a faster and more convenient onboarding experience.",
  },
  {
    title: "Nexus Bank supports small businesses through SME financing",
    category: "SME Banking",
    date: "28 May 2026",
    description:
      "The bank continues to empower entrepreneurs with accessible financing and advisory support.",
  },
  {
    title: "Nexus Bank wins excellence award for customer service",
    category: "Awards",
    date: "15 May 2026",
    description:
      "The recognition highlights the bank's commitment to reliable, customer-focused financial services.",
  },
];

export default function NewsSection() {
  return (
    <section id="support" className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
            Newsroom
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
            Latest news and activities
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            Stay updated with Nexus Bank&apos;s latest achievements, community
            initiatives, and financial insights.
          </p>
        </div>

        <div className="mt-10 grid gap-6 xl:grid-cols-3">
          {newsItems.map((item) => (
            <article
              key={item.title}
              className="card group border border-gray-100 p-7 hover:border-[#006A4E]/15"
            >
              <div className="flex items-center justify-between gap-4">
                <span className="rounded-full bg-[#006A4E]/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[#006A4E]">
                  {item.category}
                </span>
                <span className="text-sm text-gray-500">{item.date}</span>
              </div>
              <h3 className="mt-5 text-2xl font-semibold leading-tight text-gray-950">
                {item.title}
              </h3>
              <p className="mt-4 leading-7 text-gray-600">{item.description}</p>
              <a
                href="#"
                className="mt-6 inline-flex items-center text-sm font-semibold text-[#006A4E] transition group-hover:translate-x-1"
              >
                Read More
              </a>
            </article>
          ))}
        </div>

        <div className="mt-10 flex justify-center">
          <a href="#" className="btn-secondary">
            View All News
          </a>
        </div>
      </div>
    </section>
  );
}
