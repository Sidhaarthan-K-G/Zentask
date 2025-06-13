$(document).ready(function () {
    // 🔹 Toast container utility
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

    // 🔹 Show flash message (toast)
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

    // 🔹 Show spinner in table
    function showSpinnerInTable(tableSelector, colspan) {
        const tbody = $(`${tableSelector} tbody`);
        tbody.html(`
            <tr>
                <td colspan="${colspan}" class="text-center py-4">
                    <div class="spinner-wrapper">
                        <div class="spinner-border text-dark" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div class="mt-2 text-dark">Loading data...</div>
                    </div>
                </td>
            </tr>
        `);
    }

    // 🔹 Clear table body
    function clearTableBody(tableSelector) {
        $(`${tableSelector} tbody`).empty();
    }

    // 🔹 Format dropdown options with Font Awesome icons
    function formatStatusOption(state) {
        if (!state.id) return state.text;

        const icons = {
            "Not Done": "fa-hourglass-start text-secondary",
            "In Progress": "fa-spinner text-warning",
            "Done": "fa-check-circle text-success"
        };

        const icon = icons[state.text.trim()] || "fa-circle";
        return $(`<span><i class="fas ${icon} me-2"></i>${state.text}</span>`);
    }

    // 🔹 Fetch tasks from API and render table
    function fetchTasks() {
        const tableSelector = "#tasktable";
        let spinnerTimeout = setTimeout(() => {
            showSpinnerInTable(tableSelector, 5);
        }, 300);

        $.ajax({
            url: "/api/get_tasks",
            method: "GET",
            dataType: "json",
            success: function (data) {
                clearTimeout(spinnerTimeout);
                showSpinnerInTable(tableSelector, 5);

                setTimeout(() => {
                    clearTableBody(tableSelector);

                    if (data && data.tasks && data.tasks.length > 0) {
                        data.tasks.forEach(function (row) {
                            const tr = `
                                <tr data-email="${row.email}" data-taskid="${row.Task_id}">
                                    <td>${row.Task}</td>
                                    <td>${row.Due_date}</td>
                                    <td>${row.Priority}</td>
                                    <td>
                                        <select class="status-select form-select" data-taskid="${row.Task_id}">
                                            <option value="Not Done" ${row.Status === "Not Done" ? "selected" : ""}>Not Done</option>
                                            <option value="In Progress" ${row.Status === "In Progress" ? "selected" : ""}>In Progress</option>
                                            <option value="Done" ${row.Status === "Done" ? "selected" : ""}>Done</option>
                                        </select>
                                    </td>
                                    <td class="text-center">
                                        <button class="btn btn-sm btn-outline-danger delete-task-btn" title="Delete Task">
                                            <i class="fa-solid fa-trash-can"></i>
                                        </button>
                                    </td>
                                </tr>`;
                            $(`${tableSelector} tbody`).append(tr);
                        });

                        $('.status-select').select2({
                            width: '100%',
                            templateResult: formatStatusOption,
                            templateSelection: formatStatusOption,
                            minimumResultsForSearch: Infinity
                        });

                    } else {
                        $(`${tableSelector} tbody`).html(`
                            <tr><td colspan="5" class="text-center text-muted">No tasks found.</td></tr>
                        `);
                    }
                }, 2500); // Simulated delay
            },
            error: function () {
                clearTimeout(spinnerTimeout);
                $(`${tableSelector} tbody`).html(`
                    <tr><td colspan="5" class="text-center text-danger">Failed to load tasks.</td></tr>
                `);
            }
        });
    }

    // 🔹 Update task status
    function update() {
        const updates = [];

        $('#tasktable tbody tr').each(function () {
            const task = $(this).find('td:eq(0)').text().trim();
            const status = $(this).find('select.status-select').val();
            const email = $(this).data("email");

            if (task && status) {
                updates.push({
                    task: task,
                    Status: status,
                    email: email
                });
            }
        });

        if (updates.length === 0) {
            showFlashMessage("No updates to process.", "error");
            return;
        }

        $.ajax({
            url: "/api/update_tasks",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(updates),
            success: function () {
                showFlashMessage("Tasks updated successfully", "success");
                fetchTasks();
            },
            error: function () {
                showFlashMessage("Status update failed", "error");
            }
        });
    }

    // 🔹 Delete task
    $(document).on("click", ".delete-task-btn", function () {
        const row = $(this).closest("tr");
        const taskId = row.attr("data-taskid");

        if (!taskId) {
            showFlashMessage("Missing task ID.", "error");
            return;
        }

        if (confirm("Are you sure you want to delete this task?")) {
            $.ajax({
                url: "/api/delete_tasks",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ task_id: taskId }),
                success: function () {
                    row.remove();
                    showFlashMessage("Task deleted successfully", "success");
                },
                error: function () {
                    showFlashMessage("Unable to delete the task.", "error");
                }
            });
        }
    });

    // 🔹 Save button handler
    $("#saveBtn").on("click", function () {
        update();
    });

    // 🔹 Initial fetch
    fetchTasks();
});
