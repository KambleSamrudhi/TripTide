document.addEventListener("DOMContentLoaded", () => {

    const slides = document.querySelectorAll(".onboardSlide");
    const dots = document.querySelectorAll(".dot");

    let index = 0;

    function showSlide(i) {
        slides.forEach((s, idx) => {
            s.style.opacity = idx === i ? "1" : "0";
        });

        dots.forEach((d, idx) => {
            d.classList.remove("bg-[#196561]");
            d.classList.remove("bg-gray-300");
            d.classList.add(idx === i ? "bg-[#196561]" : "bg-gray-300");
        });

        index = i;
    }

    // Dot click listeners
    dots.forEach(dot => {
        dot.addEventListener("click", () => {
            showSlide(Number(dot.dataset.slide));
        });
    });

    // Auto-slide every 4 seconds
    setInterval(() => {
        index = (index + 1) % slides.length;
        showSlide(index);
    }, 4000);

    // initial
    showSlide(0);

});
