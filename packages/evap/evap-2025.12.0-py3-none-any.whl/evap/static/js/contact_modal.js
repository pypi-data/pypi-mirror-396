import { selectOrError, sleep, assert } from "./utils.js";
import { CSRF_HEADERS } from "./csrf-utils.js";
const SUCCESS_MESSAGE_TIMEOUT = 3000;
export class ContactModalLogic {
    constructor(modalId, title) {
        this.attach = () => {
            this.actionButtonElement.addEventListener("click", async (event) => {
                var _a;
                this.actionButtonElement.disabled = true;
                event.preventDefault();
                const message = this.messageTextElement.value;
                if (message.trim() === "") {
                    this.modal.hide();
                    this.actionButtonElement.disabled = false;
                    return;
                }
                try {
                    const response = await fetch("/contact", {
                        body: new URLSearchParams({
                            anonymous: String((_a = this.anonymousRadioElement) === null || _a === void 0 ? void 0 : _a.checked),
                            message,
                            title: this.title,
                        }),
                        headers: CSRF_HEADERS,
                        method: "POST",
                    });
                    assert(response.ok);
                }
                catch (_) {
                    window.alert("Sending failed, sorry!");
                    return;
                }
                this.modal.hide();
                this.successMessageModal.show();
                this.messageTextElement.value = "";
                await sleep(SUCCESS_MESSAGE_TIMEOUT);
                this.successMessageModal.hide();
                this.actionButtonElement.disabled = false;
            });
            this.showButtonElements.forEach(button => button.addEventListener("click", () => {
                this.modal.show();
            }));
        };
        this.title = title;
        this.modal = new bootstrap.Modal(selectOrError("#" + modalId));
        this.successMessageModal = new bootstrap.Modal(selectOrError("#successMessageModal_" + modalId));
        this.actionButtonElement = selectOrError("#" + modalId + "ActionButton");
        this.messageTextElement = selectOrError("#" + modalId + "MessageText");
        this.anonymousRadioElement = document.querySelector("#" + modalId + "AnonymousName");
        this.showButtonElements = Array.from(document.querySelectorAll(`#${modalId}ShowButton, .${modalId}ShowButton`));
    }
}
