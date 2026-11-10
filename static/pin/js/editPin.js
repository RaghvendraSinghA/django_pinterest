const imageInput = document.querySelector("#pin-image");
const imagePreview = document.querySelector("#image-preview");

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
        alert("Please select a valid image.");
        imageInput.value = "";
        return;
    }

    const imageUrl = URL.createObjectURL(file);

    imagePreview.src = imageUrl;
});