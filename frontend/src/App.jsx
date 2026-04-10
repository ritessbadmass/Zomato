import { useCallback, useEffect, useState } from "react";
import { fetchFilters, fetchRecommendations } from "./api.js";
import LoadingSpinner from "./components/LoadingSpinner.jsx";
import RestaurantCard from "./components/RestaurantCard.jsx";
import SearchForm from "./components/SearchForm.jsx";

const emptyFilters = { locations: [], cuisines: [] };

export default function App() {
  const [filtersData, setFiltersData] = useState(emptyFilters);
  const [filtersWarning, setFiltersWarning] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalFiltered, setTotalFiltered] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const [relaxedFilters, setRelaxedFilters] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchFilters();
        if (!cancelled) {
          setFiltersData({
            locations: data.locations || [],
            cuisines: data.cuisines || [],
          });
          setFiltersWarning("");
        }
      } catch (e) {
        if (!cancelled) {
          setFiltersData(emptyFilters);
          setFiltersWarning(
            "Could not load location and cuisine suggestions. You can still type freely."
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const scrollToForm = useCallback(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const handleSubmit = async (preferences) => {
    setLoading(true);
    setError("");
    setRecommendations([]);
    setSummary("");
    setTotalFiltered(0);
    setRelaxedFilters(false);
    setHasSearched(true);

    try {
      const res = await fetchRecommendations(preferences);
      const recs = Array.isArray(res.recommendations) ? res.recommendations : [];
      setRecommendations(recs);
      setSummary(typeof res.summary === "string" ? res.summary : "");
      setTotalFiltered(
        typeof res.total_filtered === "number" ? res.total_filtered : recs.length
      );
      setRelaxedFilters(Boolean(res.relaxed_filters));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearNewSearch = () => {
    setRecommendations([]);
    setSummary("");
    setTotalFiltered(0);
    setError("");
    setHasSearched(false);
    setRelaxedFilters(false);
    scrollToForm();
  };

  const handleTryAgain = () => {
    setError("");
  };

  const showResults =
    hasSearched && !loading && !error && recommendations.length > 0;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-amber-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-col gap-1 px-4 py-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 md:text-3xl">
              Zomato AI <span aria-hidden>🍽️</span>
            </h1>
            <p className="text-sm text-slate-500">Powered by Claude</p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-8">
        {filtersWarning && (
          <div
            className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
            role="status"
          >
            {filtersWarning}
          </div>
        )}

        <SearchForm
          onSubmit={handleSubmit}
          loading={loading}
          filtersData={filtersData}
        />

        {loading && <LoadingSpinner />}

        {error && (
          <div className="space-y-4 rounded-xl border border-red-200 bg-red-50 px-4 py-4 text-red-900">
            <p className="font-medium">{error}</p>
            <button
              type="button"
              onClick={handleTryAgain}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {showResults && (
          <>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-medium text-slate-700">
                Found {totalFiltered} restaurants · Showing top{" "}
                {recommendations.length} AI-curated picks
                {relaxedFilters && (
                  <span className="ml-2 text-amber-700">
                    (some filters were relaxed to find matches)
                  </span>
                )}
              </p>
              <button
                type="button"
                onClick={handleClearNewSearch}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-800 shadow-sm hover:bg-slate-50"
              >
                Clear / New Search
              </button>
            </div>

            {summary && (
              <div className="rounded-xl border border-sky-100 bg-sky-50 px-4 py-3 text-sm text-sky-950">
                {summary}
              </div>
            )}

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              {recommendations.map((rec) => (
                <RestaurantCard key={`${rec.rank}-${rec.restaurant_name}`} recommendation={rec} />
              ))}
            </div>
          </>
        )}

        {hasSearched && !loading && !error && recommendations.length === 0 && (
          <p className="rounded-xl border border-slate-200 bg-white px-4 py-6 text-center text-slate-600">
            No recommendations returned. Try adjusting your preferences or search again.
          </p>
        )}
      </main>

      <footer className="mt-auto border-t border-slate-200 bg-white/80 py-6 text-center text-sm text-slate-500">
        Built with Claude AI · Data from Zomato
      </footer>
    </div>
  );
}
