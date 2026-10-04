

const createButton = document.querySelector("#create-button");
const slider = document.querySelector(".slider");

createButton.addEventListener("click", () => {
    slider.classList.toggle("open");
});