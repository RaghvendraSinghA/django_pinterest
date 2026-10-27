const passwordFields = document.querySelectorAll(
    'input[type="password"]'
);

console.log(
    `Found ${passwordFields.length} password fields`
);


const fileInput = document.getElementById("profile-pic-input")
const imagePreview = document.getElementById("profile-picture-preview")

console.log(imagePreview)

fileInput.addEventListener("change", function () {
        const file = this.files[0]

        if (file && file.type.startsWith("image/")) {
            imagePreview.src = URL.createObjectURL(file)
        }
})



console.log("auth.js")