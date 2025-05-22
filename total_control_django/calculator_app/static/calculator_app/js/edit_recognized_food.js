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

// Код для обновления данных в Итого после изменения чекбокосов продуктов
const checkboxes = document.querySelectorAll('input[name*="-save_flag"]');
const totalProductsSpan = document.querySelector("#total-products");
const totalCaloriesSpan = document.querySelector("#total-calories");
const totalProteinsSpan = document.querySelector("#total-proteins");
const totalFatsSpan = document.querySelector("#total-fats");
const totalCarbsSpan = document.querySelector("#total-carbs");

// Функция для получения данных КБЖУ из формы
const getProductData = (index) => {
    const calories =
        parseFloat(
            document.querySelector(`#id_form-${index}-calories`)?.value
        ) || 0;
    const proteins =
        parseFloat(
            document.querySelector(`#id_form-${index}-proteins`)?.value
        ) || 0;
    const fats =
        parseFloat(document.querySelector(`#id_form-${index}-fats`)?.value) ||
        0;
    const carbs =
        parseFloat(document.querySelector(`#id_form-${index}-carbs`)?.value) ||
        0;
    return { calories, proteins, fats, carbs };
};

// Функция для обновления итогов
const updateTotals = () => {
    let totalProducts = 0;
    let totalCalories = 0;
    let totalProteins = 0;
    let totalFats = 0;
    let totalCarbs = 0;

    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
            const index = checkbox.name.match(/form-(\d+)-save_flag/)[1];
            const data = getProductData(index);
            totalProducts += 1;
            totalCalories += data.calories;
            totalProteins += data.proteins;
            totalFats += data.fats;
            totalCarbs += data.carbs;
        }
    });

    totalProductsSpan.textContent = totalProducts;
    totalCaloriesSpan.textContent = Math.round(totalCalories);
    totalProteinsSpan.textContent = totalProteins.toFixed(1);
    totalFatsSpan.textContent = totalFats.toFixed(1);
    totalCarbsSpan.textContent = totalCarbs.toFixed(1);
};

checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateTotals);
});

// Код для обновление итогового КБЖУ при изменении каких-либо полей ввода
const cpfcFields = ["calories", "proteins", "fats", "carbs"];
cpfcFields.forEach((field) => {
    const inputs = document.querySelectorAll(`input[name*="-${field}"]`);
    inputs.forEach((input) => {
        input.addEventListener("blur", () => {
            const value = parseFloat(input.value);
            if (!isNaN(value)) {
                input.value =
                    field === "calories" ? Math.round(value) : value.toFixed(1);
            }
            updateTotals();
        });
    });
});

// Код для изменения названия продукта
const foodNameInputs = document.querySelectorAll('input[name*="-food_name"]');
foodNameInputs.forEach((input) => {
    input.addEventListener("blur", () => {
        const index = input.name.match(/form-(\d+)-food_name/)[1];
        const span = document.querySelector(`#food-name-label-${index}`);
        if (span) {
            span.textContent = input.value;
        }
    });
});
