document.addEventListener("DOMContentLoaded", () => {
    loadDestinations();
});

async function loadDestinations() {
    try {
        const res = await fetch("/static/data/destinations.json");
        const data = await res.json();

        renderDestinations("india_grid", data.india);
        renderDestinations("intl_grid", data.international);

    } catch (err) {
        console.error("Error loading destinations:", err);
    }
}

function cleanImagePath(path) {
    return path.split("/").pop();
}

function renderDestinations(containerId, list) {
    let html = "";

    list.forEach(d => {
        const img = cleanImagePath(d.image);

        html += `
        <a href="/destination/${d.id}" class="block">
            <img src="/static/images/${img}"
                 class="w-full h-40 object-cover rounded-xl shadow"
                 onerror="this.src='/static/images/placeholder.jpg'">

            <p class="mt-2 font-semibold text-center">${d.name}</p>
        </a>`;
    });

    document.getElementById(containerId).innerHTML = html;
}
