document.addEventListener("DOMContentLoaded", () => {

    function loadMetrics() {
        fetch("/api/admin/metrics")
            .then(res => res.json())
            .then(data => {
                console.log("Admin Metrics:", data);

                // ---- METRIC CARDS ----
                document.getElementById("susValue").innerText = data.sus ?? "0";
                document.getElementById("npsValue").innerText = data.nps ?? "0";
                document.getElementById("tsrValue").innerText = (data.tsr ?? 0) + "%";
                document.getElementById("uerValue").innerText = (data.uer ?? 0) + "%";
                document.getElementById("engageValue").innerText = data.engagement ?? "0";
                document.getElementById("retentionValue").innerText = (data.retention ?? 0) + "%";

                // ---------------------------
                // DUMMY FALLBACK DATA
                // ---------------------------
                const dummyAI = { local: 12, online: 7 };
                const dummyClicks = {
                    "Search Button": 14,
                    "Plan Trip": 9,
                    "Explore Destination": 6,
                    "AI Chat": 11
                };

                // If backend returns empty → use dummy
                const aiUsage = Object.keys(data.ai_usage ?? {}).length ? data.ai_usage : dummyAI;
                const clickEvents = Object.keys(data.click_events ?? {}).length ? data.click_events : dummyClicks;

                // ---------------- AI Usage Chart ----------------
                new Chart(aiChart, {
                    type: "bar",
                    data: {
                        labels: Object.keys(aiUsage),
                        datasets: [{
                            label: "AI Interactions",
                            data: Object.values(aiUsage),
                            backgroundColor: ["#196561", "#4f46e5"]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } }
                    }
                });

                // ---------------- Click Events Chart ----------------
                new Chart(clickChart, {
                    type: "pie",
                    data: {
                        labels: Object.keys(clickEvents),
                        datasets: [{
                            data: Object.values(clickEvents),
                            backgroundColor: ["#196561", "#facc15", "#ef4444", "#3b82f6"]
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });

            })
            .catch(err => console.error("Error loading metrics:", err));
    }

    loadMetrics();
});
