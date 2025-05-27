window.addEventListener("DOMContentLoaded", () => {
        setTimeout(() => {
            document.getElementById("spinner").classList.add("d-none");
            document.getElementById("taskTableContainer").classList.remove("hidden");
        }, 1000);
    });