import "./translation.js";
import { assert } from "./utils.js";
const overrideSuccessfulSubmit = (form, onSuccess) => {
    form.addEventListener("submit", event => {
        event.preventDefault();
        const body = new FormData(form);
        fetch(form.action, { method: form.method, body })
            .then(response => {
            assert(response.ok);
            onSuccess({ body, response });
        })
            .catch((error) => {
            console.error(error);
            window.alert(window.gettext("The server is not responding."));
        });
    });
};
const makeCustomSuccessForm = (form) => {
    overrideSuccessfulSubmit(form, ({ body }) => {
        form.dispatchEvent(new CustomEvent("submit-success", { detail: { body } }));
    });
};
const makeReloadOnSuccessForm = (form) => {
    overrideSuccessfulSubmit(form, () => window.location.reload());
};
export const setupForms = () => {
    document.querySelectorAll("form[custom-success]").forEach(form => {
        makeCustomSuccessForm(form);
    });
    document.querySelectorAll("form[reload-on-success]").forEach(form => {
        makeReloadOnSuccessForm(form);
    });
};
