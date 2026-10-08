


// slider popup
const createButton = document.querySelector("#create-button");
const slider = document.querySelector(".slider");

createButton.addEventListener("click", () => {
    slider.classList.toggle("open");
});

// slider popup end



const searchBar = document.querySelector(".popup-container .search-bar");



//registering event listener to hide and show search popup and sidebar popup

const searchBarDiv = document.querySelector(".search-bar");
const searchBarPopup = document.querySelector(".popup-container");
const sideBarPopup = document.querySelector(".sidebar-popup");
const searchBarInput = document.querySelector(".popup-container .searchbar-input");
const sidebar = document.querySelector(".sidebar");


searchBarDiv.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
    searchBar.classList.add("selected-searchbar");
    searchBarInput.focus()
    sidebar.style.borderRight = "1px solid black";
})


searchBarPopup.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
    searchBarInput.value=""
    sidebar.style.borderRight = "1px solid rgb(149, 148, 148)";
})

sideBarPopup.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
    searchBarInput.value=""
    sidebar.style.borderRight = "1px solid rgb(149, 148, 148)";
})


//end of popup setting on searchbar



