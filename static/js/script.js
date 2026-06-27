const imageInput = document.getElementById("imageInput");
const scanBtn = document.getElementById("scanBtn");

const progressBar = document.getElementById("progressBar");
const statusBox = document.getElementById("statusBox");

const originalImage = document.getElementById("originalImage");
const blurImage = document.getElementById("blurImage");
const grayImage = document.getElementById("grayImage");
const claheImage = document.getElementById("claheImage");
const thresholdImage = document.getElementById("thresholdImage");

const ocrText = document.getElementById("ocrText");

// ======================================
// PROGRESS
// ======================================

function setProgress(percent, text) {

    progressBar.style.width = percent + "%";
    progressBar.innerHTML = percent + "%";

    statusBox.innerHTML = text;
}

// ======================================
// FILL FORM
// ======================================

function fillForm(data){

    for(let key in data){

        const element = document.getElementById(key);

        if(element){

            element.value = data[key];

        }

    }

}

// ======================================
// BUTTON
// ======================================

scanBtn.addEventListener("click", async ()=>{

    if(imageInput.files.length===0){

        alert("Silakan pilih gambar KTP.");

        return;

    }

    const formData = new FormData();

    formData.append(
        "image",
        imageInput.files[0]
    );

    // ======================================
    // Fake Progress (Presentasi)
    // ======================================

    setProgress(
        10,
        "Upload gambar..."
    );

    await delay(400);

    setProgress(
        25,
        "Gaussian Blur..."
    );

    await delay(400);

    setProgress(
        40,
        "Grayscale..."
    );

    await delay(400);

    setProgress(
        55,
        "CLAHE..."
    );

    await delay(400);

    setProgress(
        70,
        "Adaptive Threshold..."
    );

    // ======================================

    const response = await fetch(
        "/scan",
        {

            method:"POST",

            body:formData

        }
    );

    const result = await response.json();

    // ======================================

    setProgress(
        85,
        "EasyOCR..."
    );

    await delay(500);

    setProgress(
        95,
        "Parsing..."
    );

    await delay(500);

    setProgress(
        100,
        "Selesai."
    );

    // ======================================
    // IMAGE
    // ======================================

    originalImage.src =
        "/" + result.images.original + "?" + Date.now();

    blurImage.src =
        "/" + result.images.blur + "?" + Date.now();

    grayImage.src =
        "/" + result.images.gray + "?" + Date.now();

    claheImage.src =
        "/" + result.images.clahe + "?" + Date.now();

    thresholdImage.src =
        "/" + result.images.threshold + "?" + Date.now();

    // ======================================
    // OCR
    // ======================================

    ocrText.value = result.raw_text;

    // ======================================
    // FORM
    // ======================================

    fillForm(
        result.data
    );

});

// ======================================
// Delay
// ======================================

function delay(ms){

    return new Promise(resolve=>{

        setTimeout(resolve,ms);

    });

}

