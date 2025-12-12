import { selectOrError } from "./utils.js";
export function makeFormSortable(tableId, prefix, rowChanged, rowAdded, removeAsButton, usesTemplate) {
    function applyOrdering() {
        document.querySelectorAll(`#${tableId} tbody tr`).forEach((tableRow, i) => {
            if (rowChanged(tableRow)) {
                tableRow.querySelectorAll("input[id$=-order]").forEach(input => {
                    input.value = i.toString();
                });
            }
            else {
                // if the row is empty (has no text in the input fields) set the order to -1 (default),
                // so that the one extra row doesn't change its initial value
                tableRow.querySelectorAll("input[id$=-order]").forEach(input => {
                    input.value = "-1";
                });
            }
        });
    }
    // This is the only remaining jQuery usage, since formset requires jQuery
    $(`#${tableId} tbody tr`).formset({
        prefix: prefix,
        deleteCssClass: removeAsButton ? "btn btn-danger btn-sm" : "delete-row",
        deleteText: removeAsButton ? '<span class="fas fa-trash"></span>' : window.gettext("Delete"),
        addText: window.gettext("add another"),
        added: function (rowJQuery) {
            const row = rowJQuery.get()[0];
            row.querySelectorAll("input[id$=-order]").forEach(input => {
                var _a, _b;
                input.value = (_b = (_a = row.parentElement) === null || _a === void 0 ? void 0 : _a.childElementCount.toString()) !== null && _b !== void 0 ? _b : "";
            });
            // We have to empty the formset, otherwise sometimes old contents from
            // invalid forms are copied (#644).
            // Checkboxes with 'data-keep' need to stay checked.
            row.querySelectorAll("input[type=checkbox]:not([data-keep]),input[type=radio]").forEach(el => {
                el.checked = false;
            });
            row.querySelectorAll("input[type=text],input[type=textarea]").forEach(input => {
                input.value = "";
            });
            row.querySelectorAll("select").forEach(el => {
                el.querySelectorAll("option[selected]").forEach(option => {
                    option.removeAttribute("selected");
                });
                const option = el.querySelector("option");
                if (option) {
                    option.selected = true;
                }
            });
            //Check the first item in every button group
            row.querySelectorAll(".btn-group").forEach(group => {
                const input = group.querySelector("input");
                if (input) {
                    input.checked = true;
                }
            });
            //Remove all error messages
            row.querySelectorAll(".error-label").forEach(el => {
                el.remove();
            });
            rowAdded(row);
        },
        formTemplate: usesTemplate ? ".form-template" : null,
    });
    const tableBody = selectOrError(`#${tableId} tbody`);
    new Sortable(tableBody, {
        draggable: ".sortable",
        handle: ".fa-up-down",
        scrollSensitivity: 70,
    });
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", () => {
            applyOrdering();
        });
    });
}
