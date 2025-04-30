function initAdvancedTable(config) {
    const table = $(config.selector).DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: config.ajaxUrl,
            type: "GET",
            data: function (d) {
                let formData = $(config.filtersForm).serializeArray();
                formData.forEach(item => {
                    if (d[item.name]) {
                        if (!Array.isArray(d[item.name])) d[item.name] = [d[item.name]];
                        d[item.name].push(item.value);
                    } else {
                        d[item.name] = item.value;
                    }
                });
            }
        },
        pageLength: 25,
        scrollX: true,
        order: [[0, 'desc']],
        columns: config.columns
    });

    // Inline editing
    if (config.enableEditing) {
        $(config.selector + ' tbody').on('click', 'td', function () {
            const cell = table.cell($(this).closest('td'));
            if (!cell || !cell.index()) return;

            const originalValue = cell.data();
            const newValue = prompt("Edit value:", originalValue);
            if (newValue !== null && newValue !== originalValue) {
                const rowData = table.row(cell.index().row).data();
                const fieldIndex = cell.index().column;
                let orderId = table.row(cell.index().row).data().slice(-1)[0];
                $.ajax({
                    url: config.updateUrl,
                    method: "POST",
                    data: {
                        'order_id': orderId,  // Ajustable via config si nécessaire
                        'field_index': fieldIndex,
                        'new_value': newValue,
                        'csrfmiddlewaretoken': config.csrfToken
                    },
                    success: function (res) {
                        if (res.success) table.ajax.reload(null, false);
                        else alert("Server error: " + (res.error || "Unknown"));
                    },
                    error: function (xhr) {
                        alert("Failed to update: " + xhr.responseText);
                    }
                });
            }
        });
    }

    // Filter submit
    $(config.filtersForm).on('submit', function (e) {
        e.preventDefault();
        table.ajax.reload();
    });

    return table;
}
