let exploreStays = [];

document.addEventListener("DOMContentLoaded", () => {
    loadAllStays();
});

function resolveImage(path) {
    if (!path) return "/static/img/placeholder.jpg";

    // FULL URL → use directly
    if (path.startsWith("http://") || path.startsWith("https://")) {
        return path;
    }

    // Otherwise → local image
    return `/static/images/${path}`;
}

// LOAD STAYS
async function loadAllStays() {
    const res = await fetch("/static/data/stays.json");
    const data = await res.json();

    exploreStays = Object.entries(data).flatMap(([destination, stays]) =>
        stays.map(s => ({
            ...s,
            destination,
            numeric_price: Number(String(s.price).replace(/[₹$, ]/g, "")) || 0
        }))
    );

    renderExplore(exploreStays);
}

// RENDER GRID
function renderExplore(list) {
    let html = "";

    if (list.length === 0) {
        html = `<p class="text-center text-gray-500">No stays match your filters.</p>`;
        document.getElementById("explore_grid").innerHTML = html;
        return;
    }

    list.forEach(s => {
        html += `
        <div class="bg-white rounded-xl shadow p-4">
            <div class="relative">
                <img src="${resolveImage(s.image)}"
                     class="w-full h-40 object-cover rounded-xl">

                <div class="absolute bottom-2 right-2 bg-black/70 text-white text-xs font-semibold px-2 py-1 rounded-full">
                    Approx. ${s.price} / day
                </div>
            </div>

            <h3 class="text-xl font-bold mt-2">${s.name}</h3>
            <p class="text-gray-600">${s.destination}</p>

            <p class="mt-1 font-semibold">⭐ ${s.rating}</p>
            <p class="text-[#196561] font-bold">${s.price}</p>

            <a href="/book/${s.destination}/${encodeURIComponent(s.name)}"
               class="book-link block mt-3 w-full text-center py-2 bg-[#196561] text-white rounded-xl">
               View Stay
            </a>
        </div>`;
    });

    document.getElementById("explore_grid").innerHTML = html;
}

// APPLY FILTERS
function applyExploreFilters() {
    let price = document.getElementById("exp_price").value;
    let rating = document.getElementById("exp_rating").value;
    let type = document.getElementById("exp_type").value;
    let amenity = document.getElementById("exp_amenity").value;
    let sort = document.getElementById("exp_sort").value;

    let filtered = [...exploreStays];

    // PRICE
    if (price !== "all") {
        const [min, max] = price.split("-");
        filtered = filtered.filter(s => {
            const p = s.numeric_price;
            if (!max) return p >= Number(min);
            return p >= Number(min) && p <= Number(max);
        });
    }

    // RATING
    if (rating !== "all") {
        filtered = filtered.filter(s => s.rating >= parseFloat(rating));
    }

    // TYPE
    if (type !== "all") {
        filtered = filtered.filter(s => s.type === type);
    }

    // AMENITY
    if (amenity !== "all") {
        filtered = filtered.filter(s => s.amenities.includes(amenity));
    }

    // SORT
    if (sort === "price_low_high") filtered.sort((a, b) => a.numeric_price - b.numeric_price);
    if (sort === "price_high_low") filtered.sort((a, b) => b.numeric_price - a.numeric_price);
    if (sort === "rating_high_low") filtered.sort((a, b) => b.rating - a.rating);

    renderExplore(filtered);
}
