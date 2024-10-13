document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.getElementById("pickup-today-checkbox");
    const rows = document.querySelectorAll(".order-row");

    checkbox.addEventListener("change", function () {
        const today = new Date();
        const formattedToday = formatDate(today); // Format today's date

        rows.forEach(row => {
            const pickupDate = row.getAttribute("data-pickup-date");

            if (this.checked) {
                if (pickupDate === formattedToday) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            } else {
                row.style.display = "";
            }
        });
    });

    function formatDate(date) {
        const options = { year: "numeric", month: "long", day: "numeric" };
        return date.toLocaleDateString("en-US", options);
    }
});



