var _a;
import { selectOrError } from "./utils.js";
function isInvisible(el) {
    if (getComputedStyle(el).display === "none") {
        return true;
    }
    return el.parentElement !== null && isInvisible(el.parentElement);
}
function hasTabbingTarget(element) {
    return element.querySelector(".tab-selectable") !== null;
}
function selectByNumberKey(row, num) {
    let index = 2 * num - 1;
    if (num === 0) {
        // Select "No answer"
        index = row.children.length - 1;
    }
    if (!(0 <= index && index < row.children.length)) {
        return;
    }
    const nextElement = row.children[index];
    nextElement.click();
}
const studentForm = selectOrError("#student-vote-form");
const selectables = studentForm.querySelectorAll(".tab-selectable");
const rows = Array.from(studentForm.getElementsByClassName("tab-row"));
const letterRegex = new RegExp("^[A-Za-zÄÖÜäöü.*+-]$");
// Sometimes we just want the browser to do its thing.
let disableFocusHandler = false;
selectables[0].addEventListener("focus", () => {
    if (disableFocusHandler) {
        disableFocusHandler = false;
        return;
    }
    requestAnimationFrame(() => {
        // When first entering the form area with the altered tabbing rules, we
        // need to make sure that we start on the correct input.
        const correctInput = findCorrectInputInRow(rows[0]);
        if (selectables[0] !== correctInput) {
            fancyFocus(correctInput);
        }
    });
});
studentForm.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.altKey) {
        return;
    }
    const current = document.activeElement;
    if (!current.matches("input, label, span, textarea, button")) {
        return;
    }
    if (current.tagName !== "TEXTAREA") {
        // We want to disable backspace, because users may think that
        // they can undo their selection, but they would be sent to the
        // student index (or where they came from otherwise).
        // Additionally, pressing Enter shouldn't submit the form.
        switch (e.key) {
            case "Enter":
                current.click(); // fallthrough
            case "Backspace":
                e.preventDefault();
                return;
        }
    }
    // Since the event could be caught on either the outer label or
    // the nested text / input, the full row could be two steps up
    const currentRow = current.closest(".tab-row");
    if (currentRow === null) {
        return;
    }
    const insideSubmitRow = currentRow.closest(".card-submit-area") !== null;
    if (!insideSubmitRow && current.tagName !== "TEXTAREA") {
        const num = parseInt(e.key);
        if (!isNaN(num)) {
            // Even if the number does not trigger a selection (for example pressing "9"),
            // nothing else should happen, because it would be very frustrating if only some numbers
            // would work as expected.
            e.preventDefault();
            selectByNumberKey(currentRow, num);
            return;
        }
    }
    if (e.key !== "Tab") {
        if (current.tagName !== "TEXTAREA" && letterRegex.test(e.key)) {
            const wholeRow = currentRow.closest("div.row");
            if (wholeRow === null) {
                return;
            }
            e.preventDefault();
            const textAnswerButton = wholeRow.querySelector('[data-bs-toggle="collapse"]');
            const textField = wholeRow.querySelector("textarea.tab-selectable");
            if (textAnswerButton !== null && textField !== null) {
                if (isInvisible(textField)) {
                    textAnswerButton.click();
                }
                fancyFocus(textField);
                textField.value += e.key;
                textField.dispatchEvent(new Event("input"));
            }
        }
        return;
    }
    const curRowIndex = rows.indexOf(currentRow);
    const direction = e.shiftKey ? -1 : 1;
    let nextRowIndex = curRowIndex;
    do {
        nextRowIndex += direction;
        if (nextRowIndex === -1) {
            // User wants to tab out in front of the form area
            // To correctly select the first element in front of the form,
            // select the first element tracked by this.
            // Just giving back control to the browser here doesn't work, because
            // it would navigate backwards through the controls of the current row.
            disableFocusHandler = true;
            selectables[0].focus({ preventScroll: true });
            return;
        }
        else if (nextRowIndex === rows.length) {
            // User wants to tab out behind the form area
            selectables[selectables.length - 1].focus({ preventScroll: true });
            return;
        }
    } while (isInvisible(rows[nextRowIndex]) || !hasTabbingTarget(rows[nextRowIndex]));
    e.preventDefault();
    fancyFocus(findCorrectInputInRow(rows[nextRowIndex]));
});
function findCorrectInputInRow(row) {
    const alreadySelectedElement = row.querySelector(".tab-selectable:checked");
    if (alreadySelectedElement) {
        return alreadySelectedElement;
    }
    const possibleTargets = row.querySelectorAll(".tab-selectable");
    if (possibleTargets.length === 3) {
        // Yes-No / No-Yes question, should focus first element
        return possibleTargets[0];
    }
    // Everything else: The middle of all the answers excluding "no answer"
    // This also handles all the single possibility cases
    const index = Math.floor((possibleTargets.length - 1) / 2);
    return possibleTargets[index];
}
function fancyFocus(element) {
    element.focus({ preventScroll: true });
    element.scrollIntoView({
        behavior: "smooth",
        block: "center",
    });
}
(_a = document.querySelector("#btn-jump-unanswered-question")) === null || _a === void 0 ? void 0 : _a.addEventListener("click", scrollToFirstChoiceError);
function scrollToFirstChoiceError() {
    var _a;
    const firstErrorRow = document.querySelector(".row .choice-error");
    const tabRow = (_a = firstErrorRow === null || firstErrorRow === void 0 ? void 0 : firstErrorRow.closest(".row")) === null || _a === void 0 ? void 0 : _a.querySelector(".tab-row");
    if (tabRow) {
        fancyFocus(findCorrectInputInRow(tabRow));
    }
}
