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

        span = Math.floor(span/2)
        pin.style.gridRowEnd = `span ${span}`;
    });

});


//putting observer on each image to make them resize.

document.querySelectorAll(".pint").forEach(pin => {

    const image = pin.querySelector("img");

    const observer = new ResizeObserver(() => {

        console.log("observer called")

        const height = image.getBoundingClientRect().height;

        let span = Math.floor(
            (height + gap) / (rowHeight + gap)
        );

        // span = Math.ceil(span/2)

        pin.style.gridRowEnd = `span ${span}`;

    });

    observer.observe(pin);
});


