import { assert, selectOrError } from "./utils.js";
const RANGE_DEBOUNCE_MS = 100.0;
export class RangeSlider {
    constructor(sliderId) {
        this.allowed = { low: 0, high: 0 };
        this._value = { low: 0, high: 0 };
        this.rangeSlider = selectOrError("#" + sliderId);
        this.lowSlider = selectOrError("[name=low]", this.rangeSlider);
        this.highSlider = selectOrError("[name=high]", this.rangeSlider);
        this.minLabel = selectOrError(".text-start", this.rangeSlider);
        this.maxLabel = selectOrError(".text-end", this.rangeSlider);
        this.rangeLabel = selectOrError(".range-values", this.rangeSlider);
        const setValueFromNestedElements = () => {
            this.value = { low: parseFloat(this.lowSlider.value), high: parseFloat(this.highSlider.value) };
        };
        this.lowSlider.addEventListener("input", setValueFromNestedElements);
        this.highSlider.addEventListener("input", setValueFromNestedElements);
    }
    get value() {
        return this._value;
    }
    set value(value) {
        this._value = value;
        this.lowSlider.value = this.value.low.toString();
        this.highSlider.value = this.value.high.toString();
        if (this.value.low > this.value.high) {
            [this.value.low, this.value.high] = [this.value.high, this.value.low];
        }
        this.rangeLabel.innerText = `${this.value.low} – ${this.value.high}`;
        // debounce on range change callback
        if (this.debounceTimeout !== undefined) {
            clearTimeout(this.debounceTimeout);
        }
        this.debounceTimeout = setTimeout(() => {
            this.onRangeChange();
        }, RANGE_DEBOUNCE_MS);
    }
    onRangeChange() { }
    includeValues(values) {
        assert(Math.min(...values) >= this.allowed.low);
        const max = Math.max(...values);
        if (max > this.allowed.high) {
            this.allowed.high = max;
            this.updateNestedElements();
            this.reset();
        }
    }
    reset() {
        this.value = { low: this.allowed.low, high: this.allowed.high };
    }
    updateNestedElements() {
        this.lowSlider.min = this.allowed.low.toString();
        this.lowSlider.max = this.allowed.high.toString();
        this.highSlider.min = this.allowed.low.toString();
        this.highSlider.max = this.allowed.high.toString();
        this.minLabel.innerText = this.allowed.low.toString();
        this.maxLabel.innerText = this.allowed.high.toString();
    }
}
