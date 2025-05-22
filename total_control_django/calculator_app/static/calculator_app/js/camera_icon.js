// Скрипт для подсветки иконки с камерой
const icon = document.getElementById("cameraIcon");
const iconHref = document.getElementById("cameraIconHref");

iconHref.addEventListener("mouseenter", () => {
    icon.classList.add("glow-hover");
});

iconHref.addEventListener("mouseleave", () => {
    icon.classList.remove("glow-hover");
});
