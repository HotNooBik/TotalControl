// Получаем данные о еде
const foodElement = document.getElementById("food");
const calories = parseInt(foodElement.dataset.calories, 10);
const proteins = parseInt(foodElement.dataset.proteins, 10);
const fats = parseInt(foodElement.dataset.proteins, 10);
const carbs = parseInt(foodElement.dataset.proteins, 10);

// Убираем отправку формы после нажатия на Enter в каком-либо поле
const inputs = document.querySelectorAll("input");
inputs.forEach((input) => {
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.keyCode === 13) {
            e.preventDefault();
            this.blur();
        }
    });
});

document
    .getElementById("amount-input")
    .addEventListener("input", function (event) {
        let amount = parseFloat(event.target.value);

        if (!isNaN(amount)) {
            if (amount > 99999) {
                amount = 99999;
                event.target.value = 99999;
            }
            if (amount < 0) {
                amount = 0;
                event.target.value = 0;
            }

            document.getElementById("current-amount").textContent =
                amount.toFixed(1);

            // Пересчет значений
            const multiply = (value) => (value * amount).toFixed(1);
            amount /= 100;
            document.getElementById("calculated-calories").textContent =
                Math.round(multiply(calories));
            document.getElementById("calculated-proteins").textContent =
                multiply(proteins);
            document.getElementById("calculated-fats").textContent =
                multiply(fats);
            document.getElementById("calculated-carbs").textContent =
                multiply(carbs);
        }
    });
