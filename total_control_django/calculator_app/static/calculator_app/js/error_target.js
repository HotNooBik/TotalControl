// Скрипт для автоматического показа окна, в котором была допущена ошибка при вводе данных
const activeDiv = document.querySelector("div.show.active");
const activeButton = document.querySelector("button.active");

const divClassesToTransfer = ["show", "active"];
const buttonClassesToTransfer = ["active"];

if (activeDiv) {
    activeDiv.classList.remove(...divClassesToTransfer);
}

if (activeButton) {
    activeButton.classList.remove(...buttonClassesToTransfer);
}

const targetElements = document.querySelectorAll(`[id*='${target_window}']`);

targetElements.forEach((el) => {
    if (el.tagName.toLowerCase() === "div") {
        el.classList.add(...divClassesToTransfer);
    } else if (el.tagName.toLowerCase() === "button") {
        el.classList.add(...buttonClassesToTransfer);
    }
});
