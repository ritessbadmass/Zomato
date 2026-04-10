import { useState } from "react";

const defaultFilters = { locations: [], cuisines: [] };

export default function SearchForm({ onSubmit, loading, filtersData }) {
  const fd = filtersData || defaultFilters;
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState("medium");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState(3);
  const [extraPreferences, setExtraPreferences] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      location: location.trim(),
      budget,
      cuisine: cuisine.trim(),
      min_rating: minRating,
      extra_preferences: extraPreferences.trim(),
    });
  };

  const locId = "location-input-zomato";
  const cuiId = "cuisine-input-zomato";

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
          className="rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200"
        />
        <datalist id="locations-list">
          {(fd.locations || []).map((loc) => (
            <option key={loc} value={loc} />
          ))}
        </datalist>
      </div>

      <fieldset className="flex flex-col gap-3">
        <legend className="text-sm font-semibold text-slate-700">Budget</legend>
        <div className="flex flex-wrap gap-4">
          {[
            { v: "low", label: "Low" },
            { v: "medium", label: "Medium" },
            { v: "high", label: "High" },
          ].map(({ v, label }) => (
            <label
              key={v}
              className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50"
            >
              <input
                type="radio"
                name="budget"
                value={v}
                checked={budget === v}
                onChange={() => setBudget(v)}
                className="text-amber-600 focus:ring-amber-500"
              />
              <span className="text-sm font-medium text-slate-800">{label}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="flex flex-col gap-2">
        <label htmlFor={cuiId} className="text-sm font-semibold text-slate-700">
          Cuisine
        </label>
        <input
          id={cuiId}
          type="text"
          list="cuisines-list"
          value={cuisine}
          onChange={(e) => setCuisine(e.target.value)}
          placeholder="e.g. North Indian, Italian"
          className="rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200"
        />
        <datalist id="cuisines-list">
          {(fd.cuisines || []).map((c) => (
            <option key={c} value={c} />
          ))}
        </datalist>
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
            className="h-2 w-full max-w-md cursor-pointer accent-amber-600"
          />
          <span className="min-w-[5rem] text-sm font-semibold text-amber-700">
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
          className="resize-y rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-amber-500 px-4 py-3 text-center text-sm font-semibold text-white shadow-md transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-60"
      >
        Find Restaurants
      </button>
    </form>
  );
}
