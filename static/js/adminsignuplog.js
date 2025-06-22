$(document).ready(function () {
    // Flash Message Utilities
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

    // Show loading spinner in table
    function showSpinnerInTable(tableSelector, colspan) {
        const tbody = $(`${tableSelector} tbody`);
        tbody.html(`
            <tr>
                <td colspan="${colspan}" style="text-align:center; padding: 2rem;">
                    <div style="color: white;">
                        <div class="spinner-border" style="color: white;" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div style="margin-top: 1rem;">Loading data...</div>
                    </div>
                </td>
            </tr>
        `);
    }

    // Clear table body
    function clearTableBody(tableSelector) {
        $(`${tableSelector} tbody`).empty();
    }

    $(document).on("click", ".delete-user-btn", function () {
        const row = $(this).closest("tr");
        const signupID = row.attr("data-signup_id");
    
        if (!signupID) {
            showFlashMessage("Missing Signup ID.", "error");
            return;
        }
    
        if (confirm("Are you sure you want to delete this user?")) {
            $.ajax({
                url: "/api/delete_user",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ signup_id: signupID }), // ✅ fixed here
                success: function () {
                    row.remove();
                    showFlashMessage("User removed successfully", "success");
                },
                error: function () {
                    showFlashMessage("Unable to remove user.", "error");
                }
            });
        }
    });
    

    // Fetch signup data and populate table
    async function fetchSignupLog() {
        const tableSelector = "#signuptable";
        let spinnerTimeout = setTimeout(() => {
            showSpinnerInTable(tableSelector, 4);
        }, 300);

        try {
            const response = await $.ajax({
                url: "/api/get_signup_log", // Make sure this API exists
                method: "GET",
                dataType: "json"
            });

            clearTimeout(spinnerTimeout);
            showSpinnerInTable(tableSelector, 4); // brief spinner
            await new Promise(resolve => setTimeout(resolve, 1500)); // smooth loading
            clearTableBody(tableSelector);

            const signupData = response?.signup_table || [];

            if (signupData.length > 0) {
                signupData.forEach(row => {
                    const tr = `
                        <tr data-signup_id="${row.signup_id}">
                            <td>${row.name}</td>
                            <td>${row.email}</td>
                            <td>${row.username}</td>
                            <td>${row.password}</td>
                            <td style="text-align:center;">
                                <button class="delete-user-btn custom-delete-btn" title="Delete User">
                                    <i class="fa-solid fa-trash-can"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                    $(`${tableSelector} tbody`).append(tr);
                });
            } else {
                $(`${tableSelector} tbody`).html(`
                    <tr><td colspan="5" style="text-align:center; color:#ccc;">No signup records found.</td></tr>
                `);
            }
        } catch (err) {
            clearTimeout(spinnerTimeout);
            $(`${tableSelector} tbody`).html(`
                <tr><td colspan="5" style="text-align:center; color:red;">Failed to load signup log.</td></tr>
            `);
            console.error("Signup log fetch error:", err);
        }
    }

    // Highlight active nav link (Sidebar)
    $(".Sidebar .nav-link").each(function () {
        if (this.href === window.location.href) {
            $(this).addClass("active").css("font-weight", "bold");
        } else {
            $(this).removeClass("active");
        }
    });

    fetchSignupLog();

    // Reload page on back/forward cache (Safari/Firefox)
    window.addEventListener('pageshow', function (event) {
        if (event.persisted || performance.getEntriesByType("navigation")[0]?.type === "back_forward") {
            window.location.reload();
        }
    });
});
