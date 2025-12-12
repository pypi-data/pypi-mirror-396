import { CSRF_HEADERS } from "./csrf-utils.js";
import { assert, selectOrError } from "./utils.js";
class DataGrid {
    constructor({ storageKey, head, container, searchInput, resetSearch }) {
        this.rows = [];
        this.storageKey = storageKey;
        this.sortableHeaders = new Map();
        head.querySelectorAll(".col-order").forEach(header => {
            const column = header.dataset.col;
            this.sortableHeaders.set(column, header);
        });
        this.container = container;
        this.searchInput = searchInput;
        this.resetSearch = resetSearch;
        this.state = this.restoreStateFromStorage();
    }
    init() {
        this.rows = this.fetchRows();
        this.reflectFilterStateOnInputs();
        this.filterRows();
        this.sortRows();
        this.renderToDOM();
        this.bindEvents();
    }
    bindEvents() {
        var _a;
        this.delayTimer = undefined;
        this.searchInput.addEventListener("input", () => {
            clearTimeout(this.delayTimer);
            this.delayTimer = setTimeout(() => {
                this.state.search = this.searchInput.value;
                this.filterRows();
                this.renderToDOM();
            }, 200);
        });
        this.searchInput.addEventListener("keypress", event => {
            // after enter, unfocus the search input to collapse the screen keyboard
            if (event.key === "enter") {
                this.searchInput.blur();
            }
        });
        (_a = this.resetSearch) === null || _a === void 0 ? void 0 : _a.addEventListener("click", () => {
            this.state.search = "";
            this.filterRows();
            this.renderToDOM();
            this.reflectFilterStateOnInputs();
        });
        for (const [column, header] of this.sortableHeaders) {
            header.addEventListener("click", () => {
                // The first click order the column ascending. All following clicks toggle the order.
                const ordering = header.classList.contains("col-order-asc") ? "desc" : "asc";
                this.sort([[column, ordering]]);
            });
        }
    }
    fetchRows() {
        const rows = [...this.container.children]
            .map(row => row)
            .map(row => {
            const searchWords = this.findSearchableCells(row).flatMap(element => DataGrid.searchWordsOf(element.textContent));
            return {
                element: row,
                searchWords,
                filterValues: this.fetchRowFilterValues(row),
                orderValues: this.fetchRowOrderValues(row),
            };
        });
        for (const column of this.sortableHeaders.keys()) {
            const orderValues = rows.map(row => row.orderValues.get(column));
            const isNumericalColumn = orderValues.every(orderValue => DataGrid.NUMBER_REGEX.test(orderValue));
            if (isNumericalColumn) {
                rows.forEach(row => {
                    const numberString = row.orderValues.get(column).replace(",", ".");
                    row.orderValues.set(column, parseFloat(numberString));
                });
            }
        }
        return rows;
    }
    fetchRowOrderValues(row) {
        const orderValues = new Map();
        for (const column of this.sortableHeaders.keys()) {
            const cell = row.querySelector(`[data-col=${column}]`);
            if (cell.matches("[data-order]")) {
                orderValues.set(column, cell.dataset.order);
            }
            else {
                orderValues.set(column, cell.innerHTML.trim());
            }
        }
        return orderValues;
    }
    static searchWordsOf(string) {
        return string.toLowerCase().trim().split(/\s+/);
    }
    // Filters rows respecting the current search string and filters by their searchWords and filterValues
    filterRows() {
        const searchWords = DataGrid.searchWordsOf(this.state.search);
        for (const row of this.rows) {
            const isDisplayedBySearch = searchWords.every(searchWord => row.searchWords.some(rowWord => rowWord.includes(searchWord)));
            const isDisplayedByFilters = [...this.state.equalityFilter].every(([name, filterValues]) => filterValues.some(filterValue => { var _a; return (_a = row.filterValues.get(name)) === null || _a === void 0 ? void 0 : _a.some(rowValue => rowValue === filterValue); }));
            const isDisplayedByRangeFilters = [...this.state.rangeFilter].every(([name, bound]) => {
                var _a;
                return (_a = row.filterValues
                    .get(name)) === null || _a === void 0 ? void 0 : _a.map(rawValue => parseFloat(rawValue)).some(rowValue => rowValue >= bound.low && rowValue <= bound.high);
            });
            row.isDisplayed = isDisplayedBySearch && isDisplayedByFilters && isDisplayedByRangeFilters;
        }
    }
    sort(order) {
        this.state.order = order;
        this.sortRows();
        this.renderToDOM();
    }
    // Sorts rows respecting the current order by their orderValues
    sortRows() {
        for (const header of this.sortableHeaders.values()) {
            header.classList.remove("col-order-asc", "col-order-desc");
        }
        for (const [column, ordering] of this.state.order) {
            const header = this.sortableHeaders.get(column);
            if (header === undefined) {
                // Silently ignore non-existing columns: They were probably renamed.
                // A correct state will be built the next time the user sorts the datagrid.
                continue;
            }
            header.classList.add(`col-order-${ordering}`);
        }
        this.rows.sort((a, b) => {
            for (const [column, order] of this.state.order) {
                if (a.orderValues.get(column) < b.orderValues.get(column)) {
                    return order === "asc" ? -1 : 1;
                }
                else if (a.orderValues.get(column) > b.orderValues.get(column)) {
                    return order === "asc" ? 1 : -1;
                }
            }
            return 0;
        });
    }
    // Reflects changes to the rows to the DOM
    renderToDOM() {
        [...this.container.children].map(element => element).forEach(element => element.remove());
        const elements = this.rows.filter(row => row.isDisplayed).map(row => row.element);
        this.container.append(...elements);
        this.saveStateToStorage();
    }
    restoreStateFromStorage() {
        var _a, _b, _c;
        const stored = (_a = JSON.parse(localStorage.getItem(this.storageKey))) !== null && _a !== void 0 ? _a : {};
        return {
            equalityFilter: new Map(stored.equalityFilter),
            rangeFilter: new Map(stored.rangeFilter),
            search: (_b = stored.search) !== null && _b !== void 0 ? _b : "",
            order: (_c = stored.order) !== null && _c !== void 0 ? _c : this.defaultOrder,
        };
    }
    saveStateToStorage() {
        const stored = {
            equalityFilter: [...this.state.equalityFilter],
            rangeFilter: [...this.state.rangeFilter],
            search: this.state.search,
            order: this.state.order,
        };
        localStorage.setItem(this.storageKey, JSON.stringify(stored));
    }
    reflectFilterStateOnInputs() {
        this.searchInput.value = this.state.search;
    }
}
DataGrid.NUMBER_REGEX = /^[+-]?\d+(?:[.,]\d*)?$/;
// Table based data grid which uses its head and body
export class TableGrid extends DataGrid {
    constructor({ table, ...options }) {
        const thead = selectOrError("thead", table);
        super({
            head: thead,
            container: table.querySelector("tbody"),
            ...options,
        });
        this.searchableColumnIndices = [];
        thead.querySelectorAll("th").forEach((header, index) => {
            if (!header.hasAttribute("data-not-searchable")) {
                this.searchableColumnIndices.push(index);
            }
        });
    }
    findSearchableCells(row) {
        return this.searchableColumnIndices.map(index => {
            const child = row.children[index];
            assert(child instanceof HTMLElement);
            return child;
        });
    }
    fetchRowFilterValues(_row) {
        return new Map();
    }
    get defaultOrder() {
        if (this.sortableHeaders.size > 0) {
            const [firstColumn] = this.sortableHeaders.keys();
            return [[firstColumn, "asc"]];
        }
        return [];
    }
}
export class EvaluationGrid extends TableGrid {
    constructor({ filterButtons, ...options }) {
        super(options);
        this.filterButtons = filterButtons;
    }
    bindEvents() {
        super.bindEvents();
        this.filterButtons.forEach(button => {
            const count = this.rows.filter(row => row.filterValues.get("evaluationState").includes(button.dataset.filter)).length;
            button.append(EvaluationGrid.createBadgePill(count));
            button.addEventListener("click", () => {
                if (button.classList.contains("active")) {
                    button.classList.remove("active");
                    this.state.equalityFilter.delete("evaluationState");
                }
                else {
                    this.filterButtons.forEach(button => button.classList.remove("active"));
                    button.classList.add("active");
                    this.state.equalityFilter.set("evaluationState", [button.dataset.filter]);
                }
                this.filterRows();
                this.renderToDOM();
            });
        });
    }
    static createBadgePill(count) {
        const badgeClass = count === 0 ? "badge-btn-zero" : "badge-btn";
        const pill = document.createElement("span");
        pill.classList.add("badge", "rounded-pill", badgeClass);
        pill.textContent = count.toString();
        return pill;
    }
    fetchRowFilterValues(row) {
        const evaluationState = [...row.querySelectorAll("[data-filter]")].map(element => element.dataset.filter);
        return new Map([["evaluationState", evaluationState]]);
    }
    get defaultOrder() {
        return [["name", "asc"]];
    }
    reflectFilterStateOnInputs() {
        super.reflectFilterStateOnInputs();
        if (this.state.equalityFilter.has("evaluationState")) {
            const activeEvaluationState = this.state.equalityFilter.get("evaluationState")[0];
            const activeButton = this.filterButtons.find(button => button.dataset.filter === activeEvaluationState);
            activeButton.classList.add("active");
        }
    }
}
export class QuestionnaireGrid extends TableGrid {
    constructor({ updateUrl, ...options }) {
        super(options);
        this.updateUrl = updateUrl;
    }
    bindEvents() {
        super.bindEvents();
        new Sortable(this.container, {
            handle: ".fa-up-down",
            draggable: ".sortable",
            scrollSensitivity: 70,
            onUpdate: event => {
                if (event.oldIndex !== undefined && event.newIndex !== undefined) {
                    this.reorderRow(event.oldIndex, event.newIndex);
                }
                fetch(this.updateUrl, {
                    method: "POST",
                    headers: CSRF_HEADERS,
                    body: new URLSearchParams(this.rows.map((row, index) => [row.element.dataset.id, index.toString()])),
                }).catch((error) => {
                    console.error(error);
                    window.alert(window.gettext("The server is not responding."));
                });
            },
        });
    }
    reorderRow(oldPosition, newPosition) {
        const displayedRows = this.rows.map((row, index) => ({ row, index })).filter(({ row }) => row.isDisplayed);
        this.rows.splice(displayedRows[oldPosition].index, 1);
        this.rows.splice(displayedRows[newPosition].index, 0, displayedRows[oldPosition].row);
    }
}
// Grid based data grid which has its container separated from its header
export class ResultGrid extends DataGrid {
    constructor({ filterCheckboxes, filterSliders, sortColumnSelect, sortOrderCheckboxes, resetFilter, resetOrder, ...options }) {
        super(options);
        this.filterCheckboxes = filterCheckboxes;
        this.filterSliders = filterSliders;
        this.sortColumnSelect = sortColumnSelect;
        this.sortOrderCheckboxes = sortOrderCheckboxes;
        this.resetFilter = resetFilter;
        this.resetOrder = resetOrder;
    }
    bindEvents() {
        super.bindEvents();
        for (const [name, { checkboxes }] of this.filterCheckboxes.entries()) {
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener("change", () => {
                    const values = checkboxes.filter(checkbox => checkbox.checked).map(elem => elem.value);
                    if (values.length > 0) {
                        this.state.equalityFilter.set(name, values);
                    }
                    else {
                        this.state.equalityFilter.delete(name);
                    }
                    this.filterRows();
                    this.renderToDOM();
                });
            });
        }
        for (const [name, { slider }] of this.filterSliders.entries()) {
            this.state.rangeFilter.set(name, slider.value);
            slider.onRangeChange = () => {
                this.state.rangeFilter.set(name, slider.value);
                this.filterRows();
                this.renderToDOM();
            };
        }
        this.sortColumnSelect.addEventListener("change", () => this.sortByInputs());
        this.sortOrderCheckboxes.forEach(checkbox => checkbox.addEventListener("change", () => this.sortByInputs()));
        this.resetFilter.addEventListener("click", () => {
            this.state.search = "";
            this.state.equalityFilter.clear();
            this.state.rangeFilter.clear();
            this.filterRows();
            this.renderToDOM();
            this.reflectFilterStateOnInputs();
        });
        this.resetOrder.addEventListener("click", () => {
            this.sort(this.defaultOrder);
        });
    }
    sortByInputs() {
        const column = this.sortColumnSelect.value;
        const order = this.sortOrderCheckboxes.find(checkbox => checkbox.checked).value;
        if (order === "asc" || order === "desc") {
            if (column === "name-semester") {
                this.sort([
                    ["name", order],
                    ["semester", order],
                ]);
            }
            else {
                this.sort([[column, order]]);
            }
        }
    }
    findSearchableCells(row) {
        return [...row.querySelectorAll(".evaluation-name, [data-col=responsible]")];
    }
    fetchRowFilterValues(row) {
        const filterValues = new Map();
        for (const [name, { selector, checkboxes }] of this.filterCheckboxes.entries()) {
            // To store filter values independent of the language, use the corresponding id from the checkbox
            const values = [...row.querySelectorAll(selector)]
                .map(element => element.textContent.trim())
                .map(filterName => { var _a; return (_a = checkboxes.find(checkbox => checkbox.dataset.filter === filterName)) === null || _a === void 0 ? void 0 : _a.value; })
                .filter(v => v !== undefined);
            filterValues.set(name, values);
        }
        for (const [name, { selector, slider }] of this.filterSliders.entries()) {
            const values = [...row.querySelectorAll(selector)]
                .map(element => element.dataset.filterValue)
                .filter(v => v !== undefined);
            filterValues.set(name, values);
            slider.includeValues(values.map(parseFloat));
        }
        return filterValues;
    }
    get defaultOrder() {
        return [
            ["name", "asc"],
            ["semester", "asc"],
        ];
    }
    reflectFilterStateOnInputs() {
        super.reflectFilterStateOnInputs();
        for (const [name, { checkboxes }] of this.filterCheckboxes.entries()) {
            checkboxes.forEach(checkbox => {
                let isActive;
                if (this.state.equalityFilter.has(name)) {
                    isActive = this.state.equalityFilter.get(name).some(filterValue => filterValue === checkbox.value);
                }
                else {
                    isActive = false;
                }
                checkbox.checked = isActive;
            });
        }
        for (const [name, { slider }] of this.filterSliders.entries()) {
            const filterRange = this.state.rangeFilter.get(name);
            if (filterRange !== undefined) {
                slider.value = filterRange;
            }
            else {
                slider.reset();
            }
        }
    }
}
