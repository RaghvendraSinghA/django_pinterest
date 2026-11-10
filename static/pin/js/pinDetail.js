const rowHeight = 16;
const gap = 16;


console.log("loaded pinDetail")



document.querySelectorAll(".pint").forEach(pin => {

    const image = pin.querySelector("img");

    image.addEventListener("load", () => {

        const height = image.getBoundingClientRect().height;

        let span = Math.floor(
            (height) / (rowHeight)
        );

        span = Math.floor(span / 2)
        pin.style.gridRowEnd = `span ${span}`;
    });

});






//pin detail container fixing for 768px and below

const pinDetailContainer = document.querySelector(".pin-detail-container");
const pinPageContainer = document.querySelector(".pin-page-container");

document.querySelectorAll(".pint").forEach(pin => {

    console.log("pin", pin)

    if (pin.classList.contains("pin-detail-container")) {

        console.log("abc")

        const pinDetailContainer = document.querySelector(".pin-detail-container");

        const observer = new ResizeObserver(() => {

            console.log("observer called")

            const height = pinDetailContainer.getBoundingClientRect().height;

            let span = Math.floor(
                (height + gap) / (rowHeight + gap)
            );

            console.log("height", height)

            console.log("span", span)

            // span = Math.ceil(span/2)

            pinDetailContainer.style.gridRowEnd = `span ${span}`;
            // pinDetailContainer.style.gridRow = `span ${span}`;

        });

        observer.observe(pin);

    } else {

        const image = pin.querySelector("img");

        const observer = new ResizeObserver(() => {

            console.log("observer called")

            const height = image.getBoundingClientRect().height;

            let span = Math.floor(
                (height + gap) / (rowHeight + gap)
            );

            // span = Math.ceil(span/2)

            pin.style.gridRowEnd = `span ${span}`;

            // pin.style.gridRow = `span ${span}`;

        });

        observer.observe(pin);

    }
});



// removing refresh on like

document.querySelectorAll(".like-form").forEach((form) => {

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const url = form.action;
        const csrfToken = form.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error("Failed to update like");
            }

            const data = await response.json();

            // Update like count
            const container = form.closest(".like-count");
            //closest finds the nearest parent element of form that has the class like-count, we used this beacuse, like_count is sibling of form.
            // closest start from form and goes up till it find like-count, it can go upto last ancestor like top-most.
            container.querySelector(".like-count-text").textContent =
                data.like_count;

            // Update heart icon
            const img = form.querySelector("img");

            if (data.liked) {
                img.src = "/static/images/red-heart.png";
                img.alt = "Unlike";
                img.classList.add("red-heart");
            } else {
                img.src = "/static/images/heart.png";
                img.alt = "Like";
                img.classList.remove("red-heart");
            }

        } catch (error) {
            console.error(error);
        }
    });

});



// updating screen refresh on follow


document.querySelectorAll(".follow-form").forEach((form) => {

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const url = form.action;

        const csrfToken = form.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        const button = form.querySelector(".follow-btn");

        try {

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            if (!response.ok) {
                throw new Error("Failed to update follow status");
            }

            const data = await response.json();

            // Update follow button
            button.textContent = data.followed ? "Unfollow" : "+ Follow";

            // Update followers count
            const container = form.closest(".follow-followers");

            container.querySelector(".followers-count").textContent =
                `Followers: ${data.followers_count}`;

        } catch (error) {
            console.error(error);
        }

    });

});




// comment refresh fix

// Adding comments without page refresh

document.querySelectorAll(".add-comment-form").forEach((form) => {

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        try {

            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
            });

            const data = await response.json();

            if (!response.ok) {
                console.error(data.errors);
                return;
            }

            const commentList = document.querySelector(".comment-list");

            // Remove "No comments yet" if present
            const emptyMessage = commentList.querySelector("p");

            if (emptyMessage && commentList.children.length === 1) {
                emptyMessage.remove();
            }

            // Insert Django-generated comment HTML
            commentList.insertAdjacentHTML("beforeend", data.html);

            form.reset();

        } catch (error) {
            console.error(error);
        }

    });

});




// Adding nested replies without page refresh

const commentList = document.querySelector(".comment-list");

commentList.addEventListener("submit", async (event) => {

    const form = event.target.closest(".reply-form");

    if (!form) return;

    event.preventDefault();

    try {

        const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error(data.errors);
            return;
        }

        // Find the comment to which we are replying
        const parentThread = form.closest(".comment-thread");

        // Find its replies container
        const repliesContainer = parentThread.querySelector(
            ":scope > .current-comment-replies"
        );

        // Insert the newly created reply
        repliesContainer.insertAdjacentHTML("beforeend", data.html);

        // Clear reply textarea
        form.reset();

    } catch (error) {
        console.error("Error adding reply:", error);
    }

});



// adding reply with enter btn

document.querySelector(".comment-list").addEventListener("keydown", (event) => {
    if (!event.target.classList.contains("reply-textarea")) return;

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();

        const form = event.target.closest(".reply-form");
        form.requestSubmit();
    }
});




// deleting comment-list

const commentListToDelete = document.querySelector(".comment-list");

commentListToDelete.addEventListener("submit", async (event) => {

    const form = event.target.closest(".delete-comment-form");

    if (!form) return;

    event.preventDefault();

    try {

        const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error(data);
            return;
        }

        const commentThread = form.closest(".comment-thread");

        commentThread.remove();

    } catch (error) {
        console.error("Error deleting comment:", error);
    }

});



// edit comment


document.querySelector(".comment-list").addEventListener("dblclick", (event) => {

    const p = event.target.closest(".commenter-text");

    if (!p || !p.dataset.editUrl) return;

    const oldText = p.textContent.trim();

    const input = document.createElement("input");
    input.type = "text";
    input.className = "edit-comment-input";
    input.value = oldText;

    p.replaceWith(input);
    input.focus();
    input.select();

    input.addEventListener("keydown", async (event) => {

        if (event.key !== "Enter") return;

        const formData = new FormData();
        formData.append("text", input.value);

        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        try {
            const response = await fetch(p.dataset.editUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Update failed");
            }

            p.textContent = data.text;
            input.replaceWith(p);

        } catch (error) {
            console.error(error);
            input.replaceWith(p);
        }
    });
});



// renaming pin title


const pinTitle = document.querySelector(".pin-title");

pinTitle.addEventListener("dblclick", () => {

    if (!pinTitle.dataset.editUrl) return;

    const oldTitle = pinTitle.textContent.trim();

    const input = document.createElement("input");
    input.type = "text";
    input.className = "edit-pin-title-input";
    input.value = oldTitle;

    pinTitle.replaceWith(input);

    input.focus();
    input.select();

    input.addEventListener("keydown", async (event) => {

        if (event.key !== "Enter") return;

        const newTitle = input.value.trim();

        if (!newTitle) return;

        const formData = new FormData();
        formData.append("title", newTitle);

        try {

            const csrfToken = document.querySelector(
                "[name=csrfmiddlewaretoken]"
            ).value;

            const response = await fetch(pinTitle.dataset.editUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error);
            }

            pinTitle.textContent = data.title;
            input.replaceWith(pinTitle);

        } catch (error) {
            console.error("Pin title update failed:", error);
            input.replaceWith(pinTitle);
        }

    });

});


