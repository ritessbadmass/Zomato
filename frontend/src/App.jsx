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
      <header className="border-b border-red-100 bg-white shadow-sm">
        <div className="mx-auto flex max-w-5xl flex-col gap-1 px-4 py-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500 text-white">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.5 2 5.5 5 5 9c-.3 2.5.5 5 2.5 7 1.3 1.3 2 3 2 4.5V21h5v-.5c0-1.5.7-3.2 2-4.5 2-2 2.8-4.5 2.5-7-.5-4-3.5-7-7-7zm0 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-red-500 md:text-3xl">
                zomato
              </h1>
              <p className="text-xs text-slate-500">AI Recommendations</p>
            </div>
          </div>
          <div className="hidden md:block">
            <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-600">
              AI Powered
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-8">
        {filtersWarning && (
          <div
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
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
                  <span className="ml-2 text-red-600">
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
              <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-900">
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

      <footer className="mt-auto border-t border-slate-200 bg-white py-6 text-center text-sm text-slate-500">
        <p>Made with AI · Restaurant data from Zomato</p>
      </footer>
    </div>
  );
}
