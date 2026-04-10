export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <div
        className="h-14 w-14 rounded-full border-4 border-amber-200 border-t-amber-600 animate-spin"
        aria-hidden
      />
      <p className="text-center text-sm font-medium text-slate-600">
        Finding the best restaurants for you...
      </p>
    </div>
  );
}
