// Скрипт для истории приёмов пищи на главном экране
document.addEventListener("DOMContentLoaded", function () {
    const ctx3 = document.getElementById("dailyRecordChart");

    try {
        fetch(urls.getRecordsHistory, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify({ limit: 4, get_entries: true }),
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
                    return Promise.reject(new Error(data.error));
                }

                const labels = data.labels;
                const data_points = data.data_points;

                recordsChartInstance = new Chart(ctx3, {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: "Калории",
                                data: data.data_points.map(
                                    (entry) => entry.data.calories
                                ),
                                backgroundColor: "rgba(230, 222, 123, 0.9)",
                            },
                            {
                                label: "Цель к.",
                                data: data.data_points.map(
                                    (entry) => entry.data.calories_goal
                                ),
                                type: "line",
                                showLine: false,
                                borderColor: "rgb(196, 189, 102)",
                                backgroundColor: "rgb(196, 189, 102)",
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: "line",
                            },
                            {
                                label: "Белки",
                                data: data.data_points.map(
                                    (entry) => entry.data.proteins
                                ),
                                backgroundColor: "rgba(116, 181, 221, 0.9)",
                                hidden: true,
                            },
                            {
                                label: "Цель б.",
                                data: data.data_points.map(
                                    (entry) => entry.data.proteins_goal
                                ),
                                type: "line",
                                showLine: false,
                                borderColor: "rgb(102, 166, 196)",
                                backgroundColor: "rgb(102, 166, 196)",
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: "line",
                                hidden: true,
                            },
                            {
                                label: "Жиры",
                                data: data.data_points.map(
                                    (entry) => entry.data.fats
                                ),
                                backgroundColor: "rgba(219, 115, 115, 0.9)",
                                hidden: true,
                            },
                            {
                                label: "Цель ж.",
                                data: data.data_points.map(
                                    (entry) => entry.data.fats_goal
                                ),
                                type: "line",
                                showLine: false,
                                borderColor: "rgb(196, 102, 102)",
                                backgroundColor: "rgb(196, 102, 102)",
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: "line",
                                hidden: true,
                            },
                            {
                                label: "Углеводы",
                                data: data.data_points.map(
                                    (entry) => entry.data.carbs
                                ),
                                backgroundColor: "rgba(128, 221, 117, 0.9)",
                                hidden: true,
                            },
                            {
                                label: "Цель у.",
                                data: data.data_points.map(
                                    (entry) => entry.data.carbs_goal
                                ),
                                type: "line",
                                showLine: false,
                                borderColor: "rgb(110, 196, 102)",
                                backgroundColor: "rgb(110, 196, 102)",
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: "line",
                                hidden: true,
                            },
                            {
                                label: "Вода (мл)",
                                data: data.data_points.map(
                                    (entry) => entry.data.water
                                ),
                                backgroundColor: "rgba(117, 127, 221, 0.9)",
                                hidden: true,
                            },
                            {
                                label: "Цель в.",
                                data: data.data_points.map(
                                    (entry) => entry.data.water_goal
                                ),
                                type: "line",
                                showLine: false,
                                borderColor: "rgb(102, 108, 196)",
                                backgroundColor: "rgb(102, 108, 196)",
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: "line",
                                hidden: true,
                            },
                        ],
                    },
                    options: {
                        plugins: {
                            legend: {
                                position: "right",
                                labels: {
                                    boxWidth: 10,
                                    boxHeight: 10,
                                    usePointStyle: true,
                                    pointStyle: "circle",
                                },
                            },
                        },
                    },
                });

                document
                    .getElementById("recordsLoader")
                    .classList.add("d-none");
            })
            .catch((error) => {
                console.error("Ошибка:", error.message);
                alert("Не удалось загрузить график.");
                return Promise.reject(error);
            });
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
});
