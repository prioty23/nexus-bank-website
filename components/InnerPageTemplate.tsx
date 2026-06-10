type InnerPageTemplateProps = {
  title: string;
  description: string;
  cards: string[];
};

export default function InnerPageTemplate({
  title,
  description,
  cards,
}: InnerPageTemplateProps) {
  return (
    <main className="overflow-x-hidden">
      <section className="bg-[linear-gradient(135deg,rgba(0,106,78,0.12)_0%,rgba(236,253,245,0.85)_40%,#f8fafc_100%)]">
        <div className="container-custom py-18 text-center sm:py-20 lg:py-24">
          <p className="inline-flex rounded-full bg-[#006A4E]/10 px-4 py-1 text-sm font-semibold text-[#006A4E]">
            Nexus Bank
          </p>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-gray-950 sm:text-5xl">
            {title}
          </h1>
          <p className="mx-auto mt-5 max-w-3xl text-lg leading-8 text-gray-600">
            {description}
          </p>
        </div>
      </section>

      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006A4E]">
              Explore
            </p>
            <h2 className="mt-3 text-3xl font-semibold text-gray-950 sm:text-4xl">
              Solutions tailored for your banking journey
            </h2>
            <p className="mt-4 text-lg leading-8 text-gray-600">
              Browse these featured options to get a quick overview before we
              build out the full experience for this page.
            </p>
          </div>

          <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {cards.map((card) => (
              <article
                key={card}
                className="card group border border-gray-100 p-7 hover:border-[#006A4E]/20"
              >
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[#006A4E]/10 text-sm font-bold tracking-wide text-[#006A4E]">
                  {card
                    .split(" ")
                    .map((word) => word[0])
                    .join("")
                    .slice(0, 2)}
                </div>
                <h3 className="mt-5 text-xl font-semibold text-gray-950">
                  {card}
                </h3>
                <p className="mt-3 leading-7 text-gray-600">
                  Placeholder overview content for {card.toLowerCase()} will be
                  expanded in the next stage of the build.
                </p>
                <a
                  href="#"
                  className="mt-6 inline-flex items-center text-sm font-semibold text-[#006A4E] transition group-hover:translate-x-1"
                >
                  Learn More
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
