// Скрипт для обозначения активности пользователя при регистрации
const options = document.querySelectorAll(".activity-option");
const hiddenInput = document.querySelector("#id_activity_coef");

function setActiveOption(selectedOption) {
    options.forEach((option) => {
        option.classList.remove("active");
    });
    selectedOption.classList.add("active");
    hiddenInput.value = selectedOption.dataset.value;
}

options.forEach((option) => {
    option.addEventListener("click", function () {
        setActiveOption(this);
    });
});

// Активируем первый элемент по умолчанию
setActiveOption(options[0]);
