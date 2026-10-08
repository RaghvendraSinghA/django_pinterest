

const createButton = document.querySelector("#create-button");
const slider = document.querySelector(".slider");

createButton.addEventListener("click", () => {
    slider.classList.toggle("open");
});



const searchBar = document.querySelector(".popup-container .search-bar");



//registering event listener to hide and show search popup and sidebar popup

const searchBarDiv = document.querySelector(".search-bar");
const searchBarPopup = document.querySelector(".popup-container");
const sideBarPopup = document.querySelector(".sidebar-popup");

console.log(searchBarDiv)
console.log(searchBarPopup)
console.log(sideBarPopup)

searchBarDiv.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
    searchBar.classList.add("selected-searchbar");
})


searchBarPopup.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
})

sideBarPopup.addEventListener("click",()=>{
    searchBarPopup.classList.toggle("remove-none")
    sideBarPopup.classList.toggle("remove-none")
})