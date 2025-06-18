document.addEventListener('DOMContentLoaded', function () {
    // 🔹 Set today's date as minimum
    const dateInput = document.getElementById('date');
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const today = `${year}-${month}-${day}`;
    dateInput.setAttribute('min', today);



    function normalizedatetomidnight(datestr){
        const date = new Date(datestr);
        date.setHours(0,0,0,0);
        const year = date.getFullYear();
        const month = String(date.getMonth()+1).padStart(2,'0');
        const day = String(date.getDate()+1).padStart(2,'0');
        return `${year}-${month}-${day}`;
    }

    // 🔹 Handle form submission via AJAX
    const taskForm = $('#taskForm');
    if (taskForm.length) {
        taskForm.on('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const rawDate = formData.get("date");
            if(rawDate){
                const normalizeddate = normalizedatetomidnight(rawDate);
                formData.set("date",normalizeddate);
            }
            $.ajax({
                url: '/new_task',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    showFlashMessage("Task added successfully!", "success");

                    // ⏳ Wait for message to finish before redirecting
                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 4500);
                },
                error: function () {
                    showFlashMessage("Failed to add task!", "error");
                }
            });
        });
    }
});

// 🔹 Show toast flash message
function getToastContainer() {
    let container = document.getElementById("flashMessageContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "flashMessageContainer";
        Object.assign(container.style, {
            position: "fixed",
            top: "1rem",
            right: "1rem",
            zIndex: 9999,
            display: "flex",
            flexDirection: "column",
            gap: "10px",
        });
        document.body.appendChild(container);
    }
    return container;
}

function showFlashMessage(message, type = "success") {
    const container = getToastContainer();
    const flashBox = document.createElement("div");
    flashBox.className = `toast-message toast-${type}`;
    Object.assign(flashBox.style, {
        backgroundColor: type === "success" ? "#0b6623" : "#b32d2e",
        color: "white",
        padding: "12px 18px",
        borderRadius: "6px",
        boxShadow: "0 3px 8px rgba(0,0,0,0.15)",
        opacity: "0",
        transform: "translateX(100%)",
        transition: "opacity 0.4s ease, transform 0.4s ease",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        fontWeight: "600",
        fontSize: "14px",
    });

    flashBox.innerHTML = `
        <span>${message}</span>
        <span style="margin-left: 15px; font-weight: bold; user-select:none;">✖</span>
    `;

    flashBox.onclick = () => {
        flashBox.style.opacity = "0";
        flashBox.style.transform = "translateX(100%)";
        setTimeout(() => container.removeChild(flashBox), 400);
    };

    container.appendChild(flashBox);

    requestAnimationFrame(() => {
        flashBox.style.opacity = "1";
        flashBox.style.transform = "translateX(0)";
    });

    setTimeout(() => {
        flashBox.style.opacity = "0";
        flashBox.style.transform = "translateX(100%)";
        setTimeout(() => {
            if (container.contains(flashBox)) container.removeChild(flashBox);
        }, 400);
    }, 4000);
}


