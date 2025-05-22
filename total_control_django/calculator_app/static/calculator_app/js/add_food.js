// Скрипт для пересчета КБЖУ добавляемого продукта при изменении кол-ва
document
    .getElementById("amount-input")
    .addEventListener("input", function (event) {
        let amount = parseFloat(event.target.value);

        const unit = document.getElementById("unit").value;
        console.log(unit);

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
            switch (unit) {
                case "portion":
                    document.getElementById("calculated-calories").textContent =
                        Math.round(multiply(food.per_portion.calories));
                    document.getElementById("calculated-proteins").textContent =
                        multiply(food.per_portion.proteins);
                    document.getElementById("calculated-fats").textContent =
                        multiply(food.per_portion.fats);
                    document.getElementById("calculated-carbs").textContent =
                        multiply(food.per_portion.carbs);
                    break;

                case "g":
                    amount /= 100;
                    document.getElementById("calculated-calories").textContent =
                        Math.round(multiply(food.per_100g.calories));
                    document.getElementById("calculated-proteins").textContent =
                        multiply(food.per_100g.proteins);
                    document.getElementById("calculated-fats").textContent =
                        multiply(food.per_100g.fats);
                    document.getElementById("calculated-carbs").textContent =
                        multiply(food.per_100g.carbs);
                    break;

                case "ml":
                default:
                    amount /= 100;
                    document.getElementById("calculated-calories").textContent =
                        Math.round(multiply(food.per_100ml.calories));
                    document.getElementById("calculated-proteins").textContent =
                        multiply(food.per_100ml.proteins);
                    document.getElementById("calculated-fats").textContent =
                        multiply(food.per_100ml.fats);
                    document.getElementById("calculated-carbs").textContent =
                        multiply(food.per_100ml.carbs);
            }
        }
    });

document.getElementById("unit").addEventListener("change", function (event) {
    const unit = event.target.value;

    switch (unit) {
        case "portion":
            document.getElementById("amount-input").value = 1;
            document.getElementById("amount-title").innerHTML =
                'На <span id="current-amount">1.0</span> порций по <i>' +
                servingName +
                "</i>:";
            document.getElementById("calculated-calories").textContent =
                food.per_portion.calories;
            document.getElementById("calculated-proteins").textContent =
                food.per_portion.proteins.toFixed(1);
            document.getElementById("calculated-fats").textContent =
                food.per_portion.fats.toFixed(1);
            document.getElementById("calculated-carbs").textContent =
                food.per_portion.carbs.toFixed(1);
            break;

        case "g":
            document.getElementById("amount-input").value = 100;
            document.getElementById("amount-title").innerHTML =
                'На <span id="current-amount">100.0</span> грамм продукта:';
            document.getElementById("calculated-calories").textContent =
                food.per_100g.calories;
            document.getElementById("calculated-proteins").textContent =
                food.per_100g.proteins.toFixed(1);
            document.getElementById("calculated-fats").textContent =
                food.per_100g.fats.toFixed(1);
            document.getElementById("calculated-carbs").textContent =
                food.per_100g.carbs.toFixed(1);
            break;

        case "ml":
        default:
            document.getElementById("amount-input").value = 100;
            document.getElementById("amount-title").innerHTML =
                'На <span id="current-amount">100.0</span> мл. продукта:';
            document.getElementById("calculated-calories").textContent =
                food.per_100ml.calories;
            document.getElementById("calculated-proteins").textContent =
                food.per_100ml.proteins.toFixed(1);
            document.getElementById("calculated-fats").textContent =
                food.per_100ml.fats.toFixed(1);
            document.getElementById("calculated-carbs").textContent =
                food.per_100ml.carbs.toFixed(1);
    }
});
