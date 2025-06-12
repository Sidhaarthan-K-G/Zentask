$(document).ready(function () {
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
        tbody[0].offsetHeight;
        requestAnimationFrame(() => {});
    }

    function clearTableBody(tableSelector) {
        $(`${tableSelector} tbody`).empty();
    }
    function fetchTasks() {
        const tableSelector = "#tasktable";
        let spinnerTimeout = setTimeout(() => {
            showSpinnerInTable(tableSelector, 4);
        }, 300);

        $.ajax({
            url: "/api/get_tasks",
            method: "GET",
            dataType: "json",
            success: function (data) {
                clearTimeout(spinnerTimeout);
                showSpinnerInTable(tableSelector, 4); // show spinner immediately after clearing timeout

                // Simulate 2-3 sec delay
                setTimeout(() => {
                    clearTableBody(tableSelector);

                    if (data && data.tasks && data.tasks.length > 0) {
                        data.tasks.forEach(function (row) {
                            const tr = `
                                <tr>
                                    <td>${row.Task}</td>
                                    <td>${row.Due_date}</td>
                                    <td>${row.Priority}</td>
                                    <td>
                                        <select class="status-select" data-taskid="${row.id || ''}">
                                            <option value="Not Done" ${row.Status === "Not Done" ? "selected" : ""}>Not Done</option>
                                            <option value="In Progress" ${row.Status === "In Progress" ? "selected" : ""}>In Progress</option>
                                            <option value="Done" ${row.Status === "Done" ? "selected" : ""}>Done</option>
                                        </select>
                                    </td>
                                </tr>`;
                            $(`${tableSelector} tbody`).append(tr);
                        });
                    } else {
                        $(`${tableSelector} tbody`).html(`
                            <tr><td colspan="4" class="text-center text-muted">No tasks found.</td></tr>
                        `);
                    }
                }, 2500); // delay between 2-3 sec, here fixed to 2.5 seconds
            },
            error: function (xhr, status, error) {
                clearTimeout(spinnerTimeout);
                $(`${tableSelector} tbody`).html(`
                    <tr><td colspan="4" class="text-center text-danger">Failed to load tasks.</td></tr>
                `);
            }
        });
    }

    // Initial load
    fetchTasks();
});
