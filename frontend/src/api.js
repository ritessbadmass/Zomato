// In production, VITE_API_BASE_URL is set to the Render backend URL.
// In local dev, it falls back to "" so the Vite proxy (localhost:8000) is used.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function parseError(response) {
  let msg = `Request failed (${response.status})`;
  try {
    const data = await response.json();
    if (data && typeof data.detail === "string") {
      msg = data.detail;
    } else if (data && typeof data.detail === "object" && data.detail !== null) {
      msg = JSON.stringify(data.detail);
    }
  } catch {
    /* ignore */
  }
  return msg;
}

export async function fetchFilters() {
  const res = await fetch(`${API_BASE}/api/filters`);
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}

export async function fetchRecommendations(preferences) {
  const res = await fetch(`${API_BASE}/api/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preferences }),
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}
