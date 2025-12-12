import { selectOrError } from "./utils.js";
export class ConfirmationModal extends HTMLElement {
    constructor() {
        var _a, _b;
        super();
        this.onDialogFormSubmit = (event) => {
            var _a, _b;
            event.preventDefault();
            const isConfirm = ((_a = event.submitter) === null || _a === void 0 ? void 0 : _a.dataset.eventType) === "confirm";
            if (isConfirm && this.internals.form && !this.internals.form.reportValidity()) {
                return;
            }
            this.closeDialogSlowly();
            if (isConfirm) {
                if (this.type === "submit") {
                    // Unfortunately, `this` cannot act as the submitter of the form. Instead, we make our `value` attribute
                    // visible to the form until submission is finished (the `submit` handlers of the form might cancel the
                    // submission again, which is why we hide reset the visible value again afterwards).
                    this.internals.setFormValue(this.getAttribute("value"));
                    (_b = this.internals.form) === null || _b === void 0 ? void 0 : _b.requestSubmit();
                    this.internals.setFormValue(null);
                }
                else {
                    this.dispatchEvent(new CustomEvent("confirmed", { detail: new FormData(this.dialogForm) }));
                }
            }
        };
        this.closeDialogSlowly = () => {
            this.dialog.addEventListener("animationend", () => {
                this.dialog.removeAttribute("closing");
                this.dialog.close();
            }, { once: true });
            this.dialog.setAttribute("closing", "");
        };
        const template = selectOrError("#confirmation-modal-template").content;
        const shadowRoot = this.attachShadow({ mode: "open" });
        shadowRoot.appendChild(template.cloneNode(true));
        this.type = (_a = this.getAttribute("type")) !== null && _a !== void 0 ? _a : "button";
        this.internals = this.attachInternals();
        this.dialog = selectOrError("dialog", shadowRoot);
        const confirmButton = selectOrError("[data-event-type=confirm]", this.dialog);
        const confirmButtonExtraClass = (_b = this.getAttribute("confirm-button-class")) !== null && _b !== void 0 ? _b : "btn-primary";
        confirmButton.className += " " + confirmButtonExtraClass;
        const showButton = selectOrError("[slot=show-button]", this);
        showButton.addEventListener("click", event => {
            event.stopPropagation();
            this.dialog.showModal();
        });
        const updateDisabledAttribute = () => {
            this.toggleAttribute("disabled", showButton.hasAttribute("disabled"));
        };
        new MutationObserver(updateDisabledAttribute).observe(showButton, {
            attributeFilter: ["disabled"],
        });
        updateDisabledAttribute();
        this.dialogForm = selectOrError("form[method=dialog]", this.dialog);
        this.dialogForm.addEventListener("submit", this.onDialogFormSubmit);
        this.dialog.addEventListener("click", event => event.stopPropagation());
    }
}
ConfirmationModal.formAssociated = true;
