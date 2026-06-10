const customerTypes = [
  "Individual Customer",
  "SME Owner",
  "Corporate Client",
  "Student",
  "Freelancer",
];

const interests = [
  "Opening an Account",
  "Getting a Loan",
  "Credit or Debit Card",
  "Saving or Deposit",
  "Digital Banking",
];

const priorities = [
  "Convenience",
  "Low Fees",
  "Fast Approval",
  "High Returns",
  "Business Growth",
];

export default function ProductFinder() {
  return (
    <section
      id="finder"
      className="section-padding bg-[linear-gradient(135deg,rgba(0,106,78,0.08)_0%,#f8fafc_40%,rgba(236,253,245,0.9)_100%)]"
    >
      <div className="container-custom">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-semibold text-gray-950 sm:text-4xl">
            Discover the perfect product for your needs
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            Answer a few simple questions and find the banking solution that
            matches your goals.
          </p>
        </div>

        <div className="mt-10 grid gap-8 rounded-[2rem] border border-[#006A4E]/10 bg-white p-8 shadow-xl shadow-[#006A4E]/8 lg:grid-cols-[0.95fr_1.05fr] lg:p-12">
          <div className="flex flex-col justify-between rounded-[1.75rem] bg-[#0F172A] p-8 text-white shadow-lg shadow-black/10">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
                Product Finder
              </p>
              <h3 className="mt-4 text-3xl font-semibold leading-tight">
                Not sure which product is right for you?
              </h3>
              <p className="mt-5 max-w-xl leading-8 text-gray-300">
                Use our guided selector to explore accounts, loans, cards,
                deposits and digital banking services designed around your
                lifestyle or business needs.
              </p>
            </div>

            <div className="mt-8">
              <a href="#services" className="btn-primary">
                See Recommendations
              </a>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-[#006A4E]/10 bg-[#F8FAFC] p-6 sm:p-8">
            <div className="space-y-6">
              <div>
                <label
                  htmlFor="customer-type"
                  className="mb-2 block text-sm font-semibold text-gray-700"
                >
                  I am a
                </label>
                <select
                  id="customer-type"
                  defaultValue=""
                  className="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10"
                >
                  <option value="" disabled>
                    Select customer type
                  </option>
                  {customerTypes.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="interest"
                  className="mb-2 block text-sm font-semibold text-gray-700"
                >
                  I am interested in
                </label>
                <select
                  id="interest"
                  defaultValue=""
                  className="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10"
                >
                  <option value="" disabled>
                    Select a category
                  </option>
                  {interests.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="priority"
                  className="mb-2 block text-sm font-semibold text-gray-700"
                >
                  My priority is
                </label>
                <select
                  id="priority"
                  defaultValue=""
                  className="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-gray-700 outline-none transition focus:border-[#006A4E] focus:ring-2 focus:ring-[#006A4E]/10"
                >
                  <option value="" disabled>
                    Select a priority
                  </option>
                  {priorities.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <button type="button" className="btn-primary w-full justify-center">
                See Recommendations
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
