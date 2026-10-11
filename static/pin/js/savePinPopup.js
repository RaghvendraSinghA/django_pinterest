const popup = document.querySelector("#save-popup");
const openButton = document.querySelector("#open-save-popup");
const closeButton = document.querySelector("#close-save-popup");
const boardList = document.querySelector("#save-popup-boards");
const saveForm = document.querySelector("#save-pin-form");

// Open popup
openButton?.addEventListener("click", () => {
    popup.classList.add("is-open");
    popup.setAttribute("aria-hidden", "false");
});

// Close popup
function closePopup() {
    popup.classList.remove("is-open");
    popup.setAttribute("aria-hidden", "true");
}

closeButton?.addEventListener("click", closePopup);

// Close when clicking outside the popup
popup?.addEventListener("click", (event) => {
    if (event.target === popup) {
        closePopup();
    }
});

// Save pin when a board is clicked
boardList?.addEventListener("click", async (event) => {
    const boardButton = event.target.closest(".save-board-option");

    if (!boardButton || boardButton.disabled || !saveForm) {
        return;
    }

    boardButton.disabled = true;

    const formData = new FormData(saveForm);
    formData.set("board_id", boardButton.dataset.boardId);

    try {
        const response = await fetch(saveForm.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        });

        if (!response.ok) {
            throw new Error("Unable to save pin.");
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error("Unable to save pin.");
        }

        // Turn the selected board light green
        boardButton.classList.add("is-saved");

    } catch (error) {
        console.error(error);
    } finally {
        boardButton.disabled = false;
    }
});