const $ = (id) => document.getElementById(id);

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = "";
    if (Array.isArray(data.detail)) {
      // Handle FastAPI validation errors (422)
      msg = data.detail.map(d => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
    } else {
      msg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data);
    }
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return data;
}

async function loadCities() {
  const warn = $("locality-warn");
  try {
    const data = await fetchJSON("/api/v1/locations");
    const sel = $("city");
    sel.innerHTML = '<option value="">— Pick a broad area —</option>';
    (data.locations || []).forEach((city) => {
      const o = document.createElement("option");
      o.value = city;
      o.textContent = city;
      sel.appendChild(o);
    });
  } catch (e) {
    if (warn) {
      warn.hidden = false;
      warn.textContent = "Could not load areas list; please try reloading the page.";
    }
  }
}

async function loadLocalitiesForCity(city) {
  const sel = $("locality");
  sel.disabled = true;
  sel.innerHTML = '<option value="">— Loading localities... —</option>';
  try {
    const data = await fetchJSON(`/api/v1/localities?city=${encodeURIComponent(city)}`);
    sel.innerHTML = '<option value="">— Any specific locality (optional) —</option>';
    (data.localities || []).forEach((loc) => {
      const o = document.createElement("option");
      o.value = loc;
      o.textContent = loc;
      sel.appendChild(o);
    });
    sel.disabled = false;
  } catch (e) {
    sel.innerHTML = '<option value="">— Could not load localities —</option>';
  }
}

$("city").addEventListener("change", (e) => {
  const city = e.target.value;
  if (city) {
    loadLocalitiesForCity(city);
  } else {
    $("locality").innerHTML = '<option value="">— Pick a broad area first —</option>';
    $("locality").disabled = true;
  }
});

function rankClass(r) {
  if (r === 1) return "rank-1";
  if (r === 2) return "rank-2";
  if (r === 3) return "rank-3";
  return "rank-n";
}

function renderResults(data) {
  const out = $("results");
  const metaContainer = $("results-meta");
  const items = data.items || [];
  const summary = data.summary || "";

  let metaHtml = "";
  if (data.meta && data.meta.shortlist_size !== undefined) {
    metaHtml = `Found ${items.length} top matches from a shortlist of ${data.meta.shortlist_size}`;
  }
  if (metaContainer) metaContainer.textContent = metaHtml;

  let html = "";
  if (summary) {
    html += `<div class="summary-box">${escapeHtml(summary)}</div>`;
  }

  if (items.length === 0) {
    html += `<div class="card" style="text-align: center; color: var(--text-secondary);">
      <p>No restaurants matched your exact criteria. Try broadening your budget or cuisine preferences.</p>
    </div>`;
    out.innerHTML = html;
    return;
  }

  html += '<div class="grid">';
  items.forEach((it) => {
    const r = it.rank || 0;
    const cuisines = (it.cuisines || []).join(", ");
    const cuisinesLower = cuisines.toLowerCase();
    const rating = Number(it.rating);
    let ratingClass = "";
    if (rating >= 4.0) ratingClass = "";
    else if (rating >= 3.0) ratingClass = "low";
    else ratingClass = "very-low";

    // Intelligence for image selection
    let imgPath = "/static/images/generic.png";
    if (cuisinesLower.includes("north indian") || cuisinesLower.includes("mughlai")) {
      imgPath = "/static/images/north_indian.png";
    } else if (cuisinesLower.includes("south indian")) {
      imgPath = "/static/images/south_indian.png";
    } else if (cuisinesLower.includes("chinese") || cuisinesLower.includes("thai") || cuisinesLower.includes("asian")) {
      imgPath = "/static/images/chinese.png";
    } else if (cuisinesLower.includes("cafe") || cuisinesLower.includes("bakery") || cuisinesLower.includes("dessert") || cuisinesLower.includes("beverages")) {
      imgPath = "/static/images/cafe.png";
    } else if (it.rating >= 4.5 || (it.cost_display && it.cost_display.includes("1500"))) {
      imgPath = "/static/images/fine_dining.png";
    }

    html += `
      <article class="result-card">
        <div class="card-img-container">
          <img src="${imgPath}" alt="${escapeHtml(it.name)}" class="card-img" onerror="this.src='/static/images/generic.png'">
        </div>
        <div class="card-head">
          <span class="rank ${rankClass(r)}">${r}</span>
          <div class="card-title-group">
            <h2 class="card-title" title="${escapeHtml(it.name)}">${escapeHtml(it.name)}</h2>
            <p class="card-subtitle">${escapeHtml(cuisines)}</p>
          </div>
        </div>
        <div class="card-body">
          <div class="badge-group">
            <span class="badge badge-rating ${ratingClass}">★ ${rating.toFixed(1)}</span>
            <span class="badge">${escapeHtml(it.cost_display || "₹₹₹")}</span>
            <span class="badge">${escapeHtml(it.location || "Nearby")}</span>
          </div>
          <div class="explain">${escapeHtml(it.explanation || "")}</div>
        </div>
      </article>`;
  });
  html += "</div>";
  out.innerHTML = html;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

// Handle Tag Chip Toggles
document.querySelectorAll(".tag-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("active");
    const activeTags = Array.from(document.querySelectorAll(".tag-chip.active"))
      .map(c => c.dataset.value);
    $("extras").value = activeTags.join(", ");
  });
});

$("rec-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("error").innerHTML = "";
  $("results").innerHTML = "";
  $("loading").style.display = "block";
  $("submit").disabled = true;

  const prefs = {
    location: $("locality").value.trim() || $("city").value.trim(),
    budget_max_inr: Number($("budget").value),
    cuisine: $("cuisine").value.trim(),
    min_rating: Number($("min_rating").value),
    extras: $("extras").value.trim(),
  };

  try {
    const data = await fetchJSON("/api/v1/recommend", {
      method: "POST",
      body: JSON.stringify({ preferences: prefs }),
    });
    $("loading").style.display = "none";
    $("submit").disabled = false;
    $("after-results").style.display = "block";
    renderResults(data);
    
    // Smooth scroll to results
    setTimeout(() => {
      window.scrollTo({
        top: $("after-results").offsetTop - 20,
        behavior: "smooth"
      });
    }, 100);
  } catch (err) {
    $("loading").style.display = "none";
    $("submit").disabled = false;
    $("error").innerHTML = `<div class="err">${escapeHtml(err.message)}</div>`;
  }
});

$("clear").addEventListener("click", () => {
  $("results").innerHTML = "";
  $("error").innerHTML = "";
  $("after-results").style.display = "none";
  document.querySelectorAll(".tag-chip").forEach(c => c.classList.remove("active"));
  $("extras").value = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
});

loadCities();
