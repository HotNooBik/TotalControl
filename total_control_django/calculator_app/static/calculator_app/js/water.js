// Скрипт для AJAX запроса на добавление воды
const addWaterBtn = document.getElementById("addWaterBtn");
const waterAmountInput = document.getElementById("waterAmount");
const currentWaterSpan = document.getElementById("currentWater");

addWaterBtn.addEventListener("click", function () {
    const waterAmount = parseInt(waterAmountInput.value) || 0;

    if (waterAmount != 0) {
        fetch(urls.addWater, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify({ amount: waterAmount }),
        })
            .then((response) => {
                if (
                    !response.headers
                        .get("content-type")
                        ?.includes("application/json")
                ) {
                    throw new Error("Ошибка сети");
                }
                return response.json();
            })
            .then((data) => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                currentWaterSpan.textContent = data.new_water;
                updateWaterLevel(data.water_percent);
            })
            .catch((error) => {
                console.error("Ошибка:", error.message);
                alert("Не удалось добавить воду.");
            });
    } else {
        waterAmountInput.value = 250;
    }
});

// Скрипт для стакана с водой
const waterElement = document.querySelector(".water");
const percentageElement = document.querySelector(".water-percentage");

function updateWaterLevel(percent) {
    waterElement.style.height = `${percent}%`;
    percentageElement.textContent = `${percent.toFixed(0)}%`;
}

const waterText = document.getElementById("currentWater").textContent.trim();
window.onload = updateWaterLevel(waterPercent);
