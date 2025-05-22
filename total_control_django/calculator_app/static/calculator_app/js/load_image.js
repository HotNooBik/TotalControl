const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("image-input");
const previewImg = document.getElementById("preview-img");
const previewError = document.getElementById("preview-error");

function resetPreview() {
    previewImg.style.display = "none";
    previewImg.src = "";
    previewError.style.display = "none";
    previewError.textContent = "";
}

function showPreview(file) {
    resetPreview();

    const imageURL = URL.createObjectURL(file);
    previewImg.src = imageURL;
    previewImg.style.display = "block";

    previewImg.onerror = function () {
        resetPreview();
        previewError.innerHTML =
            '<i class="fa-solid fa-triangle-exclamation"></i> Файл повреждён или не является изображением.';
        previewError.style.display = "block";
    };
}

["dragenter", "dragover", "dragleave", "drop"].forEach(function (event) {
    dropArea.addEventListener(event, function (e) {
        e.preventDefault();
        e.stopPropagation();
    });
});

["dragenter", "dragover"].forEach(function (event) {
    dropArea.addEventListener(event, function () {
        dropArea.classList.add("highlight");
    });
});

["dragleave", "drop"].forEach(function (event) {
    dropArea.addEventListener(event, function () {
        dropArea.classList.remove("highlight");
    });
});

dropArea.addEventListener("drop", function (e) {
    e.preventDefault();
    e.stopPropagation();

    const items = e.dataTransfer.items;

    for (let i = 0; i < items.length; i++) {
        const item = items[i].webkitGetAsEntry?.();
        if (item && item.isDirectory) {
            return;
        }
    }

    const file = e.dataTransfer.files[0];
    if (file) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        showPreview(file);
    }
});

fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        showPreview(fileInput.files[0]);
    }
});

const spinnerText = document.getElementById("spinner-text");

document
    .getElementById("image-submit-form")
    .addEventListener("submit", function (e) {
        document.querySelector(".overlay-gif").classList.remove("d-none");
        document.getElementById("to-remove").style.visibility = "hidden";
        document.getElementById("spinner").classList.remove("d-none");

        let textVariants = [
            "Анализируем изображение..."
        ];
        textVariants = textVariants.concat(messages)
        let currentIndex = 0;

        const textInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % textVariants.length;
            spinnerText.textContent = textVariants[currentIndex];
        }, 3000);
    });
