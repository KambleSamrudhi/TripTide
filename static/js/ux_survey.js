// triptide/static/js/ux_survey.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("ux-survey-form");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const questionNames = ["ux_q1", "ux_q2", "ux_q3", "ux_q4", "ux_q5"];
    const scores = [];
    let total = 0;

    // Collect 1–5 scores for all 5 questions
    for (const name of questionNames) {
      const checked = form.querySelector(`input[name="${name}"]:checked`);
      if (!checked) {
        alert("Please answer all rating questions before submitting.");
        return;
      }
      const val = parseInt(checked.value, 10);
      scores.push(val);
      total += val;
    }

    const avgScore = total / scores.length; // 1–5 average

    // Optional: also store in the anonymous profile (if you kept profile.js)
    if (window.TriptideProfile && typeof window.TriptideProfile.setUxScore === "function") {
      window.TriptideProfile.setUxScore(avgScore);
    }

    // ----- Send to backend so ADMIN page can see it -----

    // Build a 10-item SUS list by duplicating each of the 5 answers.
    // analytics_engine.submit_sus(sum(scores_list) * 2.5) will then compute the SUS score.
    const susList = [];
    scores.forEach(s => {
      susList.push(s, s);
    });

    try {
      if (typeof window.submitSUS === "function") {
        await window.submitSUS(susList);
      }
    } catch (e) {
      console.error("SUS submission failed:", e);
    }

    // Use Q5 ("How likely are you to use TripTide again?") as an NPS-style rating
    try {
      if (typeof window.submitNPS === "function") {
        await window.submitNPS(scores[4]);
      }
    } catch (e) {
      console.error("NPS submission failed:", e);
    }

    // Show thank-you message
    const statusEl = document.getElementById("ux-survey-status");
    if (statusEl) {
      statusEl.classList.remove("hidden");
    }
  });
});
