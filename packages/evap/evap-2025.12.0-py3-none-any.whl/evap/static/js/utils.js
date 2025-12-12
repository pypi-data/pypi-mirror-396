export const selectOrError = (selector, root = document) => {
    const elem = root.querySelector(selector);
    assert(elem, `Element with selector ${selector} not found`);
    return elem;
};
export function assert(condition, message = "Assertion Failed") {
    if (!condition) {
        throw new Error(message);
    }
}
export function assertDefined(val) {
    assert(val !== undefined);
    assert(val !== null);
}
export const sleep = (ms) => new Promise(resolve => window.setTimeout(resolve, ms));
export const clamp = (val, lowest, highest) => Math.min(highest, Math.max(lowest, val));
export const saneParseInt = (s) => {
    if (!/^-?[0-9]+$/.test(s)) {
        return null;
    }
    const num = parseInt(s);
    assert(!isNaN(num));
    return num;
};
export const findPreviousElementSibling = (element, selector) => {
    while (element.previousElementSibling) {
        element = element.previousElementSibling;
        if (element.matches(selector)) {
            return element;
        }
    }
    return null;
};
export function unwrap(val) {
    assertDefined(val);
    return val;
}
export const isVisible = (element) => element.offsetWidth !== 0 || element.offsetHeight !== 0;
export const fadeOutThenRemove = (element) => {
    element.style.transition = "opacity 600ms";
    element.style.opacity = "0";
    setTimeout(() => {
        element.remove();
    }, 600);
};
