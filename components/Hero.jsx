export default function Hero() {
  return (
    <section className="bg-gradient-to-br from-emerald-50 via-white to-green-100">
      <div className="container-custom section-padding">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="max-w-2xl">
            <span className="inline-flex rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#006A4E] shadow-sm ring-1 ring-[#006A4E]/10">
              Smart Banking for Modern Life
            </span>
            <h1 className="mt-6 text-4xl font-bold leading-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Plan Better. 
              Bank Smarter. 
              Live Brighter.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-8 text-slate-600 sm:text-lg">
              Nexus Bank helps individuals, businesses, and communities manage
              money with secure, simple, and future-ready financial solutions.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:flex-row">
              <a href="#" className="btn-primary">
                Explore Products
              </a>
              <a href="#" className="btn-secondary">
                Open an Account
              </a>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-x-8 top-8 h-40 rounded-full bg-[#006A4E]/10 blur-3xl" />
            <div className="relative card overflow-hidden border border-white/60 bg-white/90 p-8 shadow-xl backdrop-blur">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">
                    Nexus Digital Account
                  </p>
                  <p className="mt-6 text-sm text-slate-500">Available Balance</p>
                  <p className="mt-2 text-4xl font-bold tracking-tight text-slate-900">
                    $24,850.00
                  </p>
                </div>
                <div className="rounded-2xl bg-[#006A4E] px-4 py-3 text-right text-white shadow-md">
                  <p className="text-xs uppercase tracking-[0.2em] text-white/70">
                    Status
                  </p>
                  <p className="mt-1 text-sm font-semibold">Active</p>
                </div>
              </div>

              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl bg-emerald-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">
                    Secure Banking
                  </p>
                  <p className="mt-2 text-sm text-slate-600">
                    Advanced protection for every transaction.
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">
                    Fast Transfer
                  </p>
                  <p className="mt-2 text-sm text-slate-600">
                    Send funds quickly with minimal effort.
                  </p>
                </div>
                <div className="rounded-2xl bg-emerald-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">
                    24/7 Support
                  </p>
                  <p className="mt-2 text-sm text-slate-600">
                    Real help whenever you need banking support.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
