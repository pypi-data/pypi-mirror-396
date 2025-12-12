import "./translation.js";
import { unwrap, assert } from "./utils.js";
class NotebookFormLogic {
    constructor(notebook) {
        this.notebook = notebook;
        this.updateCooldown = 2000;
        this.onSubmit = (event) => {
            event.preventDefault();
            const submitter = unwrap(event.submitter);
            submitter.disabled = true;
            this.notebook.setAttribute("data-state", "sending");
            fetch(this.notebook.action, {
                body: new FormData(this.notebook),
                method: "POST",
            })
                .then(response => {
                assert(response.ok);
                this.notebook.setAttribute("data-state", "successful");
                setTimeout(() => {
                    this.notebook.setAttribute("data-state", "ready");
                    submitter.disabled = false;
                }, this.updateCooldown);
            })
                .catch(() => {
                this.notebook.setAttribute("data-state", "ready");
                submitter.disabled = false;
                alert(window.gettext("The server is not responding."));
            });
        };
        this.attach = () => {
            this.notebook.addEventListener("submit", this.onSubmit);
        };
    }
}
export class NotebookLogic {
    constructor(notebookCard, notebookForm, evapContent, collapseNotebookButton, localStorageKey) {
        this.notebookCard = notebookCard;
        this.evapContent = evapContent;
        this.collapseNotebookButton = collapseNotebookButton;
        this.localStorageKey = localStorageKey;
        this.onShowNotebook = () => {
            this.notebookCard.classList.add("notebook-container");
            localStorage.setItem(this.localStorageKey, "true");
            this.evapContent.classList.add("notebook-margin");
            this.collapseNotebookButton.classList.replace("show", "hide");
        };
        this.onHideNotebook = () => {
            this.notebookCard.classList.remove("notebook-container");
            localStorage.setItem(this.localStorageKey, "false");
            this.evapContent.classList.remove("notebook-margin");
            this.collapseNotebookButton.classList.replace("hide", "show");
        };
        this.attach = () => {
            if (localStorage.getItem(this.localStorageKey) == "true") {
                this.notebookCard.classList.add("show");
                this.onShowNotebook();
            }
            this.notebookCard.addEventListener("show.bs.collapse", this.onShowNotebook);
            this.notebookCard.addEventListener("hidden.bs.collapse", this.onHideNotebook);
            this.formLogic.attach();
        };
        this.formLogic = new NotebookFormLogic(notebookForm);
    }
}
