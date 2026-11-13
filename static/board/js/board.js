const boardName = document.querySelector(".board-detail-name")

boardName.addEventListener("dblclick", () => {

    const oldName = boardName.textContent.trim()

    const input = document.createElement("input")
    input.type = "text"
    input.className = "edit-board-name-input"
    input.value = oldName

    boardName.replaceWith(input)

    input.focus()

    input.addEventListener("keydown", async (event) => {

        if (event.key !== "Enter") return

        const newName = input.value.trim()

        if (!newName) return

        const formData = new FormData()
        formData.append("name", newName)

        try {

            const response = await fetch(boardName.dataset.editUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
                },
                body: formData
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error)
            }

            boardName.textContent = data.name
            input.replaceWith(boardName)

            document.title = data.name

        } catch (error) {
            console.error("Board rename failed:", error)
            input.replaceWith(boardName)
        }

    })

})