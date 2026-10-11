const searchInput = document.querySelector("#search-input");
const searchResults = document.querySelector("#search-results");

let timeout;

searchInput.addEventListener("input", () => {
    clearTimeout(timeout);

    const query = searchInput.value.trim();

    timeout = setTimeout(async () => {
        if (!query) {
            searchResults.replaceChildren();
            return;
        }

        try {
            const response = await fetch(
                `/search/?q=${encodeURIComponent(query)}`
            );

            const data = await response.json();

            searchResults.replaceChildren();

            

            data.results.forEach(pin => {
                const result = document.createElement("a");
                result.className = "search-result";
                result.href = pin.url;

                const image = document.createElement("img");
                image.src = pin.image;
                image.alt = pin.title;
                image.className = "search-img";

                const title = document.createElement("div");
                title.textContent = pin.title;
                title.className = "search-item-name"


                result.append(image, title);
                searchResults.appendChild(result);
            });
        } catch (error) {
            console.error("Search failed:", error);
        }
    }, 300);
});