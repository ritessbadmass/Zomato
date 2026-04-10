function rankBadgeClass(rank) {
  if (rank === 1) return "bg-amber-400 text-amber-950 ring-2 ring-amber-200";
  if (rank === 2) return "bg-slate-300 text-slate-900 ring-2 ring-slate-200";
  if (rank === 3) return "bg-orange-300 text-orange-950 ring-2 ring-orange-200";
  return "bg-slate-200 text-slate-700 ring-2 ring-slate-100";
}

function isYes(val) {
  const s = String(val ?? "").toLowerCase().trim();
  return s === "yes" || s === "true" || s === "1";
}

function formatCost(avgCost) {
  const n = Number(avgCost);
  if (avgCost == null || Number.isNaN(n) || n <= 0) {
    return "Cost not available";
  }
  return `₹ ${Math.round(n)} for two`;
}

export default function RestaurantCard({ recommendation }) {
  const rank = Number(recommendation.rank) || 0;
  const online = isYes(recommendation.has_online_order);
  const booking = isYes(recommendation.has_table_booking);
  const ratingNum = Number(recommendation.rating);
  const ratingLabel = Number.isFinite(ratingNum)
    ? `${ratingNum.toFixed(1)} / 5`
    : String(recommendation.rating ?? "");

  return (
    <article
      className="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-lg"
    >
      <div className="flex items-start gap-3 border-b border-slate-100 bg-slate-50/80 px-5 py-4">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-sm font-bold ${rankBadgeClass(rank)}`}
        >
          #{rank}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-xl font-bold text-slate-900">
            {recommendation.restaurant_name}
          </h3>
          <p className="mt-1 flex items-start gap-1 text-sm text-slate-600">
            <span className="mt-0.5" aria-hidden>
              📍
            </span>
            <span>{recommendation.location}</span>
          </p>
          <p className="mt-1 flex items-start gap-1 text-sm text-slate-600">
            <span className="mt-0.5" aria-hidden>
              🍴
            </span>
            <span>{recommendation.cuisines}</span>
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 px-5 pt-4 text-sm">
        <span className="rounded-full bg-amber-50 px-3 py-1 font-medium text-amber-900">
          ⭐ {ratingLabel}
        </span>
        <span className="rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-900">
          {formatCost(recommendation.avg_cost)}
        </span>
        <span
          className={`rounded-full px-3 py-1 font-medium ${
            online
              ? "bg-green-100 text-green-900"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {online ? "Online Order ✓" : "No Online Order"}
        </span>
        <span
          className={`rounded-full px-3 py-1 font-medium ${
            booking
              ? "bg-sky-100 text-sky-900"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {booking ? "Table Booking ✓" : "No Booking"}
        </span>
      </div>

      <div className="mt-4 flex-1 px-5 pb-5">
        <div className="rounded-xl border border-amber-100 bg-amber-50/90 px-4 py-3">
          <p className="text-sm font-semibold text-amber-900">
            <span aria-hidden>✨</span> Why it fits you
          </p>
          <p className="mt-2 text-sm italic leading-relaxed text-amber-950/90">
            {recommendation.explanation}
          </p>
        </div>
      </div>
    </article>
  );
}
