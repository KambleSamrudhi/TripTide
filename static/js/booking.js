document.addEventListener("DOMContentLoaded", () => {
    loadSimilar();
});
function resolveImage(path) {
    if (!path) return "/static/img/placeholder.jpg";

    if (path.startsWith("http://") || path.startsWith("https://")) {
        return path;
    }
    return `/static/images/${path}`;
}

// Reserve Button
function reserveStay(stayName) {
    alert("🎉 Your stay at " + stayName + " has been reserved!");
}


// Favorites
function addFavorite(destination, stay) {
    let favs = JSON.parse(localStorage.getItem("favorites") || "[]");

    favs.push({ destination, stay });

    localStorage.setItem("favorites", JSON.stringify(favs));
    alert("❤️ Added to your favorites!");
}


// Similar stay recommendations
async function loadSimilar() {
    const destination = window.location.pathname.split("/")[2];

    const res = await fetch("/api/similar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ destination })
    });

    const data = await res.json();

    let html = "";

    data.stays.forEach(s => {
        html += `
    <div class="bg-white rounded-xl shadow p-4">
        <img src="${resolveImage(s.image)}" class="w-full h-32 object-cover rounded-xl">


                <h3 class="mt-2 text-xl font-bold">${s.name}</h3>
                <p class="text-gray-700">⭐ ${s.rating}</p>
                <p class="font-semibold text-[#196561]">${s.price}</p>

                <a href="/book/${destination}/${encodeURIComponent(s.name)}"
                   class="block mt-3 w-full text-center py-2 bg-[#196561] text-white rounded-xl">
                   View
                </a>
            </div>
        `;
    });

    document.getElementById("similar_box").innerHTML = html;
}
