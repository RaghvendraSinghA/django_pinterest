const popup = document.querySelector("#save-popup")    //popup overlay
const openButton = document.querySelector("#open-save-popup")    // save button of pin detail page
const closeButton = document.querySelector("#close-save-popup")    //close save-popup buttom
const boardList = document.querySelector("#save-popup-boards")  // container of boards
const saveForm = document.querySelector("#save-pin-form")  // 

// Open popup
openButton?.addEventListener("click", () => {
    popup.classList.add("is-open")
    popup.setAttribute("aria-hidden", "false")
})

// Close popup
function closePopup() {
    popup.classList.remove("is-open")
    popup.setAttribute("aria-hidden", "true")
}

closeButton?.addEventListener("click", closePopup)

// Close when clicking outside the popup
popup?.addEventListener("click", (event) => {
    if (event.target === popup) {
        closePopup()
    }
});

// Save pin when a board is clicked
boardList?.addEventListener("click", async (event) => {
    const boardButton = event.target.closest(".save-board-option")

    if (!boardButton || boardButton.disabled || !saveForm) {
        return
    }

    //  saveForm is element defined top of this file, it sits outside of board and it is only for  validated user So, if user is not validated then saveForm does't exit and since we are using one event handler on whole popup so it will be trigger and try to make request.

    boardButton.disabled = true

    const formData = new FormData(saveForm)
    formData.set("board_id", boardButton.dataset.boardId)

    try {
        const response = await fetch(saveForm.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        })

        if (!response.ok) {
            throw new Error("Unable to save pin.")
        }

        const data = await response.json()

        if (!data.success) {
            throw new Error("Unable to save pin.")
        }

        // adding toast notification

        Toastify({
            text: `Pin saved to your board !`,
            duration: 3000,
            gravity: "top",      // "top" or "bottom"
            position: "right",     // "left", "center" or "right"
            close: true,
            stopOnFocus: true,
            style: { background: "#2e7d32" },
        }).showToast()


        // Turn the selected board light green
        boardButton.classList.add("is-saved")

    } catch (error) {
        console.error(error)
        Toastify({
            text: "Couldn't save the pin. Please try again.",
            duration: 3000,
            gravity: "top",
            position: "right",
            stopOnFocus: true,
            style: { background: "#c62828" },
        }).showToast()

    } finally {
        boardButton.disabled = false
    }
})