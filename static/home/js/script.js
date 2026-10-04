
const searchInput = document.querySelector("#searchInput");


searchInput.addEventListener("input", () => {

    console.log(
        "Searching for:",
        searchInput.value
    );

});