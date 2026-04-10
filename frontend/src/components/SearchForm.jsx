import { useState } from "react";

const defaultFilters = { locations: [], cuisines: [] };

// Budget mapping for backend compatibility
const budgetMapping = {
  "500": "low",
  "700": "low",
  "1000": "medium",
  "1500": "medium",
  "3000+": "high",
};

export default function SearchForm({ onSubmit, loading, filtersData }) {
  const fd = filtersData || defaultFilters;
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState("1000");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState(3);
  const [extraPreferences, setExtraPreferences] = useState("");
  const [showCuisineDropdown, setShowCuisineDropdown] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      location: location.trim(),
      budget: budgetMapping[budget],
      cuisine: cuisine.trim(),
      min_rating: minRating,
      extra_preferences: extraPreferences.trim(),
    });
  };

  const locId = "location-input-zomato";
  const cuiId = "cuisine-input-zomato";

  const budgetOptions = ["500", "700", "1000", "1500", "3000+"];

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto max-w-2xl space-y-5 rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-sm backdrop-blur md:p-8"
    >
      <div className="flex flex-col gap-2">
        <label htmlFor={locId} className="text-sm font-semibold text-slate-700">
          Location
        </label>
        <input
          id={locId}
          type="text"
          list="locations-list"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="City or area (e.g. Connaught Place)"
          className="rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-200"
        />
        <datalist id="locations-list">
          {(fd.locations || []).map((loc) => (
            <option key={loc} value={loc} />
          ))}
        </datalist>
      </div>

      <div className="flex flex-col gap-3">
        <label className="text-sm font-semibold text-slate-700">Max Budget (for 2)</label>
        <div className="flex flex-wrap gap-2">
          {budgetOptions.map((amount) => (
            <button
              key={amount}
              type="button"
              onClick={() => setBudget(amount)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                budget === amount
                  ? "bg-red-500 text-white shadow-md"
                  : "border border-slate-300 bg-white text-slate-700 hover:border-red-300 hover:bg-red-50"
              }`}
            >
              Rs. {amount}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor={cuiId} className="text-sm font-semibold text-slate-700">
          Cuisine
        </label>
        <div className="relative">
          <input
            id={cuiId}
            type="text"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
            onFocus={() => setShowCuisineDropdown(true)}
            placeholder="Select cuisine"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-200"
          />
          {showCuisineDropdown && (
            <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-slate-200 bg-white shadow-lg">
              <div className="p-2">
                <button
                  type="button"
                  onClick={() => {
                    setCuisine("");
                    setShowCuisineDropdown(false);
                  }}
                  className="w-full rounded px-3 py-2 text-left text-sm text-slate-600 hover:bg-slate-100"
                >
                  Any Cuisine
                </button>
                {(fd.cuisines || []).map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => {
                      setCuisine(c);
                      setShowCuisineDropdown(false);
                    }}
                    className="w-full rounded px-3 py-2 text-left text-sm text-slate-700 hover:bg-red-50 hover:text-red-600"
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
          )}
          {showCuisineDropdown && (
            <div
              className="fixed inset-0 z-0"
              onClick={() => setShowCuisineDropdown(false)}
            />
          )}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="min-rating" className="text-sm font-semibold text-slate-700">
          Minimum rating
        </label>
        <div className="flex flex-wrap items-center gap-4">
          <input
            id="min-rating"
            type="range"
            min={0}
            max={5}
            step={0.5}
            value={minRating}
            onChange={(e) => setMinRating(Number(e.target.value))}
            className="h-2 w-full max-w-md cursor-pointer accent-red-500"
          />
          <span className="min-w-[5rem] text-sm font-semibold text-red-600">
            {minRating.toFixed(1)} ★
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="extra-prefs" className="text-sm font-semibold text-slate-700">
          Additional preferences
        </label>
        <textarea
          id="extra-prefs"
          rows={3}
          value={extraPreferences}
          onChange={(e) => setExtraPreferences(e.target.value)}
          placeholder="e.g. family-friendly, outdoor seating, quick service..."
          className="resize-y rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-200"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-red-500 px-4 py-3 text-center text-sm font-semibold text-white shadow-md transition hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-60"
      >
        Find Restaurants
      </button>
    </form>
  );
}
