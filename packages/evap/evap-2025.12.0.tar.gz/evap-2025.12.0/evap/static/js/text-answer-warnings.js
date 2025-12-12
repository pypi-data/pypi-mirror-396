function normalize(text) {
    return text.toLowerCase().replace(/\s+/g, " ").trim();
}
function isTextMeaningless(text) {
    return text.length > 0 && ["", "ka", "na", "none", "keine", "keines", "keiner"].includes(text.replace(/\W/g, ""));
}
function doesTextContainTriggerString(text, triggerStrings) {
    return triggerStrings.some(triggerString => text.includes(triggerString));
}
function updateTextareaWarning(textarea, textAnswerWarnings) {
    const text = normalize(textarea.value);
    const matchingWarnings = [];
    if (isTextMeaningless(text)) {
        matchingWarnings.push("meaningless");
    }
    for (const [i, triggerStrings] of textAnswerWarnings.entries()) {
        if (doesTextContainTriggerString(text, triggerStrings)) {
            matchingWarnings.push(`trigger-string-${i}`);
        }
    }
    const showWarning = matchingWarnings.length > 0;
    textarea.classList.toggle("border", showWarning);
    textarea.classList.toggle("border-warning", showWarning);
    const row = textarea.closest(".row");
    for (const warning of row.querySelectorAll("[data-warning]")) {
        warning.classList.toggle("d-none", !matchingWarnings.includes(warning.dataset.warning));
    }
}
export function initTextAnswerWarnings(textareas, textAnswerWarnings) {
    textAnswerWarnings = textAnswerWarnings.map(triggerStrings => triggerStrings.map(normalize));
    textareas.forEach(textarea => {
        let warningDelayTimer;
        textarea.addEventListener("input", () => {
            clearTimeout(warningDelayTimer);
            warningDelayTimer = setTimeout(() => updateTextareaWarning(textarea, textAnswerWarnings), 300);
        });
        textarea.addEventListener("blur", () => {
            updateTextareaWarning(textarea, textAnswerWarnings);
        });
        updateTextareaWarning(textarea, textAnswerWarnings);
    });
}
export const testable = {
    normalize,
    isTextMeaningless,
    doesTextContainTriggerString,
};
