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
            gap: "0.5rem",
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
        backgroundColor: type === "success" ? "#d4edda" : "#f8d7da",
        color: type === "success" ? "#155724" : "#721c24",
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
        <span>
            <i class="fa-solid ${type === "success" ? "fa-check-circle" : "fa-exclamation-circle"} me-2"></i>
            ${message}
        </span>
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
