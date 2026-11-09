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






//pin detail container fixing for 768px and below

const pinDetailContainer = document.querySelector(".pin-detail-container");
const pinPageContainer = document.querySelector(".pin-page-container");

document.querySelectorAll(".pint").forEach(pin => {

    console.log("pin",pin)

    if(pin.classList.contains("pin-detail-container")){
        
        console.log("abc")

        const pinDetailContainer = document.querySelector(".pin-detail-container");

        const observer = new ResizeObserver(() => {

            console.log("observer called")

            const height = pinDetailContainer.getBoundingClientRect().height;

            let span = Math.floor(
                (height + gap) / (rowHeight + gap)
            );

            console.log("height",height)

            console.log("span",span)

            // span = Math.ceil(span/2)

            pinDetailContainer.style.gridRowEnd = `span ${span}`;
            // pinDetailContainer.style.gridRow = `span ${span}`;

        });

        observer.observe(pin);

    }else{

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
