async function generateItinerary() {
    const dest = document.getElementById("p_destination").value;
    const days = document.getElementById("p_days").value;
    const type = document.getElementById("p_type").value;
    const interests = document.getElementById("p_interests").value;

    if (!dest || !days) {
        alert("Please enter destination and days.");
        return;
    }

    document.getElementById("itinerary_output").innerHTML =
        "⏳ Generating itinerary...";

    const res = await fetch("/api/itinerary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            destination: dest,
            days,
            traveler_type: type,
            interests
        })
    });

    const data = await res.json();

    document.getElementById("itinerary_output").innerHTML =
        data.itinerary || "❌ Unable to generate itinerary.";
}
