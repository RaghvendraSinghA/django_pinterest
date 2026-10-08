const rowHeight = 16;
const gap = 16;


console.log("loaded pinDetail")

// document.querySelectorAll(".pint").forEach(pin => {
//     const height = pin.getBoundingClientRect().height;

//     console.log(pin)
    

//     const image = pin.querySelector('img')

//     console.log("complete:", image.complete);
//     console.log("naturalWidth:", image.naturalWidth);
//     console.log("naturalHeight:", image.naturalHeight);

//     console.log(image)

//     console.log("image", image.getBoundingClientRect())

//     console.log("height",height)

//     console.log("client rect",  pin.getBoundingClientRect())

//     const span = Math.ceil(
//         (height + gap) / (rowHeight + gap)
//     );

//     console.log("span",span)

//     pin.style.gridRowEnd = `span ${span}`;

//     console.log("event ocuured for calculating height")
// });



document.querySelectorAll(".pint").forEach(pin => {

    const image = pin.querySelector("img");

    console.log(image)

    image.addEventListener("load", () => {


        console.log("image info", image.getBoundingClientRect())
        const height = image.getBoundingClientRect().height;

        console.log("height", height)

        let span = Math.ceil(
            (height) / (rowHeight)
        );

        span = Math.floor(span/2)


        console.log("span", span)
        pin.style.gridRowEnd = `span ${span}`;
    });

});