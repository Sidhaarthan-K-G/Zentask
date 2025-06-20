$(document).ready(function () {
    // 🔹 Toast utility
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

    function formatStatusOption(state) {
        if (!state.id) return state.text;
        const icons = {
            "Not Done": "fa-hourglass-start text-secondary",
            "In Progress": "fa-spinner text-warning",
            "Done": "fa-check-circle text-success",
            "Overdue": "fa-clock text-danger"
        };
        const icon = icons[state.text.trim()] || "fa-circle";
        return $(`<span><i class="fas ${icon} me-2"></i>${state.text}</span>`);
    }

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

    function clearTableBody(tableSelector) {
        $(`${tableSelector} tbody`).empty();
    }

    function markOverdueTasks() {
        const rows = document.querySelectorAll("#tasktable tbody tr");
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        rows.forEach(row => {
            const dueDateCell = row.querySelector("td:nth-child(2)");
            const taskId = row.dataset.taskid;
            if (!dueDateCell || !taskId) return;

            const dueDateStr = dueDateCell.textContent.trim();
            const dueDate = new Date(dueDateStr);
            dueDate.setHours(0, 0, 0, 0);

            const statusSelect = row.querySelector("td:nth-child(4) select");
            const currentStatus = statusSelect ? statusSelect.value.trim() : "Overdue";

            if (dueDate < today && currentStatus !== "Overdue" && currentStatus !== "Done") {
                if (statusSelect) {
                    statusSelect.value = "Overdue";
                    $(statusSelect).trigger("change.select2");
                }

                $(row).find("select, input, textarea, button").each(function () {
                    const isDeleteButton = $(this).hasClass("delete-task-btn") || $(this).find(".fa-trash-can").length > 0;
                    if (!isDeleteButton) {
                        $(this).prop("disabled", true);
                    }
                });

                $.ajax({
                    url: '/api/update_task_status',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ task_id: taskId, status: "Overdue" }),
                    success: () => console.log(`Task ${taskId} marked as overdue`),
                    error: () => console.error(`Failed to update task ${taskId} as overdue`)
                });
            }
        });
    }

    async function fetchTasks() {
        const tableSelector = "#tasktable";
        let spinnerTimeout = setTimeout(() => {
            showSpinnerInTable(tableSelector, 5);
        }, 300);

        try {
            const data = await $.ajax({
                url: "/api/get_tasks",
                method: "GET",
                dataType: "json"
            });

            clearTimeout(spinnerTimeout);
            showSpinnerInTable(tableSelector, 5);

            await new Promise(resolve => setTimeout(resolve, 2000));
            clearTableBody(tableSelector);

            if (data?.tasks?.length > 0) {
                data.tasks.forEach(row => {
                    let statusHtml = "";

                    if (row.Status === "Overdue") {
                        statusHtml = `
                            <div class="form-select readonly-dropdown">
                                <i class="fas fa-clock text-danger me-2"></i> Overdue
                            </div>
                        `;
                    } else {
                        statusHtml = `
                            <select class="status-select" data-taskid="${row.Task_id}">
                                <option value="Not Done" ${row.Status === "Not Done" ? "selected" : ""}>Not Done</option>
                                <option value="In Progress" ${row.Status === "In Progress" ? "selected" : ""}>In Progress</option>
                                <option value="Done" ${row.Status === "Done" ? "selected" : ""}>Done</option>
                                <option value="Overdue" ${row.Status === "Overdue" ? "selected" : ""}>Overdue</option>
                            </select>
                        `;
                    }

                    const tr = `
                        <tr data-email="${row.email}" data-taskid="${row.Task_id}">
                            <td>${row.Task}</td>
                            <td>${row.Due_date}</td>
                            <td>${row.Priority}</td>
                            <td>${statusHtml}</td>
                            <td style="text-align:center;">
                                <button class="delete-task-btn custom-delete-btn" title="Delete Task">
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
                    <tr><td colspan="5" style="text-align:center; color:#ccc;">No tasks found.</td></tr>
                `);
            }

            markOverdueTasks();

        } catch (err) {
            clearTimeout(spinnerTimeout);
            $(`${tableSelector} tbody`).html(`
                <tr><td colspan="5" style="text-align:center; color:red;">Failed to load tasks.</td></tr>
            `);
        }
    }

    $("#statusfilter").on("change", function () {
        const selectedStatus = $(this).val().toLowerCase();
        $("#tasktable tbody tr").each(function () {
            const statusText = $(this).find(".status-select").val()?.toLowerCase() || "overdue";
            $(this).toggle(selectedStatus === "all" || statusText === selectedStatus);
        });
    });

    function update() {
        const updates = [];
        $('#tasktable tbody tr').each(function () {
            const task = $(this).find('td:eq(0)').text().trim();
            const status = $(this).find('select.status-select').val();
            const email = $(this).data("email");

            if (task && status) {
                updates.push({ task: task, Status: status, email: email });
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
            success: () => {
                showFlashMessage("Tasks updated successfully", "success");
                fetchTasks();
            },
            error: () => showFlashMessage("Status update failed", "error")
        });
    }

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

    $("#saveBtn").on("click", function () {
        update();
    });

    const taskForm = $('#taskForm');
    if (taskForm.length) {
        taskForm.on('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const rawDate = formData.get("date");
            if (rawDate) {
                const date = new Date(rawDate);
                date.setHours(0, 0, 0, 0);
                const normalized = date.toISOString().split("T")[0];
                formData.set("date", normalized);
            }

            $.ajax({
                url: '/new_task',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function () {
                    showFlashMessage("Task added successfully!", "success");
                    setTimeout(() => window.location.href = "/dashboard", 4500);
                },
                error: function () {
                    showFlashMessage("Failed to add task!", "error");
                }
            });
        });
    }

    fetchTasks();
});
