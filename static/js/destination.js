document.addEventListener("DOMContentLoaded", () => {
    const place = window.location.pathname.split("/").pop();

    loadWeather(place);
    loadSafety(place);
    loadCulture(place);
    loadPacking(place);
    loadStays(place);
    loadExperiences(place);
    loadMap(place);
    loadDistance(place);
});

// IMAGE RESOLVER
function resolveImage(path) {
    if (!path) return "/static/img/placeholder.jpg";

    if (path.startsWith("http://") || path.startsWith("https://")) {
        return path;
    }

    return `/static/images/${path}`;
}

// WEATHER
async function loadWeather(place) {
    let res = await fetch(`/api/weather`);
    let data = await res.json();

    document.getElementById("weather_box").innerHTML =
        `<p><strong>Temperature:</strong> ${data.weather.temp}°C</p>
         <p><strong>Condition:</strong> ${data.weather.condition}</p>
         <p><strong>Wind:</strong> ${data.weather.wind} km/h</p>`;
}

// SAFETY
async function loadSafety(place) {
    let res = await fetch(`/api/safety/region`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: place })
    });
    let data = await res.json();
    document.getElementById("safety_box").innerHTML =
        `<p><strong>Safety Score:</strong> ${data.score}</p>`;
}

// CULTURE
async function loadCulture(place) {
    let res = await fetch(`/api/culture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination: place })
    });
    let data = await res.json();
    document.getElementById("culture_box").innerHTML = data.story;
}

// PACKING
async function loadPacking(place) {
    let res = await fetch(`/api/packing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            destination: place,
            climate: "tropical",
            duration: 4,
            activities: ["tourism"],
            traveler_type: "Solo"
        })
    });
    let data = await res.json();
    document.getElementById("packing_box").innerHTML = data.packing_list;
}

// EXPERIENCES
async function loadExperiences(place) {
    let res = await fetch(`/api/local_experiences`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            destination: place,
            traveler_type: "Solo"
        })
    });
    let data = await res.json();
    document.getElementById("experiences_box").innerHTML = data.experiences;
}

// STAYS
let allStays = [];

async function loadStays(place) {
    let res = await fetch(`/api/stays/` + place);
    allStays = await res.json();

    // ensure numeric_price exists
    allStays = allStays.map(s => ({
        ...s,
        numeric_price: Number(String(s.price).replace(/[₹$, ]/g, "")) || 0
    }));

    renderStays(allStays);
}

// Apply frontend filters
function applyFilters() {
    let price = document.getElementById("filter_price").value;
    let rating = document.getElementById("filter_rating").value;
    let type = document.getElementById("filter_type").value;
    let amenity = document.getElementById("filter_amenities").value;

    let filtered = allStays;

    if (price !== "all") {
        const [min, max] = price.split("-");
        filtered = filtered.filter(s => {
            const p = s.numeric_price;
            if (!max) return p >= Number(min);
            return p >= Number(min) && p <= Number(max);
        });
    }

    if (rating !== "all") filtered = filtered.filter(s => s.rating >= parseFloat(rating));
    if (type !== "all") filtered = filtered.filter(s => s.type === type);
    if (amenity !== "all") filtered = filtered.filter(s => s.amenities.includes(amenity));

    renderStays(filtered);
}

// RENDER STAYS
function renderStays(stays) {
    let html = "";

    if (stays.length === 0) {
        document.getElementById("stays_grid").innerHTML =
            `<p class="text-center text-gray-500">No stays match your filters.</p>`;
        return;
    }

    stays.forEach(s => {
        html += `
        <div class="bg-white rounded-xl shadow p-4">
            <img src="${resolveImage(s.image)}" class="w-full h-40 object-cover rounded-xl">

            <h3 class="text-xl font-bold mt-2">${s.name}</h3>
            <p class="text-gray-600">${s.tagline || ""}</p>

            <p class="mt-2 font-semibold">⭐ ${s.rating}</p>
            <p class="text-[#196561] font-bold">${s.price}</p>

            <a href="/book/${s.destination}/${encodeURIComponent(s.name)}"
               class="block mt-3 w-full text-center py-2 bg-[#196561] text-white rounded-xl">
               Book Now
            </a>
        </div>`;
    });

    document.getElementById("stays_grid").innerHTML = html;
}

// MAP → revert to iframe
function loadMap(place) {
    const iframe = document.getElementById("map_iframe");
    iframe.src = `https://www.google.com/maps?q=${place}&output=embed`;
}

// DISTANCE
async function loadDistance(place) {
    let res = await fetch(`/api/distance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ place })
    });

    let data = await res.json();
    document.getElementById("distance_text").innerHTML =
        `Distance from you: <strong>${data.distance_km} km</strong>`;
}
