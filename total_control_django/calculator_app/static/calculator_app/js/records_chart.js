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
                    !response.headers.get("content-type")?.includes("application/json")
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
                                label: 'Калории',
                                data: data.data_points.map((entry) => entry.data.calories),
                                backgroundColor: 'rgba(230, 222, 123, 0.9)',
                            },
                            {
                                label: 'Цель к.',
                                data: data.data_points.map(
                                    (entry) => entry.data.calories_goal
                                ),
                                type: 'line',
                                showLine: false,
                                borderColor: 'rgb(196, 189, 102)',
                                backgroundColor: 'rgb(196, 189, 102)',
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: 'line',
                            },
                            {
                                label: 'Белки',
                                data: data.data_points.map((entry) => entry.data.proteins),
                                backgroundColor: 'rgba(116, 181, 221, 0.9)',
                                hidden: true
                            },
                            {
                                label: 'Цель б.',
                                data: data.data_points.map(
                                    (entry) => entry.data.proteins_goal
                                ),
                                type: 'line',
                                showLine: false,
                                borderColor: 'rgb(102, 166, 196)',
                                backgroundColor: 'rgb(102, 166, 196)',
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: 'line',
                                hidden: true
                            },
                            {
                                label: 'Жиры',
                                data: data.data_points.map((entry) => entry.data.fats),
                                backgroundColor: 'rgba(219, 115, 115, 0.9)',
                                hidden: true
                            },
                            {
                                label: 'Цель ж.',
                                data: data.data_points.map(
                                    (entry) => entry.data.fats_goal
                                ),
                                type: 'line',
                                showLine: false,
                                borderColor: 'rgb(196, 102, 102)',
                                backgroundColor: 'rgb(196, 102, 102)',
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: 'line',
                                hidden: true
                            },
                            {
                                label: 'Углеводы',
                                data: data.data_points.map((entry) => entry.data.carbs),
                                backgroundColor: 'rgba(128, 221, 117, 0.9)',
                                hidden: true
                            },
                            {
                                label: 'Цель у.',
                                data: data.data_points.map(
                                    (entry) => entry.data.carbs_goal
                                ),
                                type: 'line',
                                showLine: false,
                                borderColor: 'rgb(110, 196, 102)',
                                backgroundColor: 'rgb(110, 196, 102)',
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: 'line',
                                hidden: true
                            },
                            {
                                label: 'Вода (мл)',
                                data: data.data_points.map((entry) => entry.data.water),
                                backgroundColor: 'rgba(117, 127, 221, 0.9)',
                                hidden: true
                            },
                            {
                                label: 'Цель в.',
                                data: data.data_points.map(
                                    (entry) => entry.data.water_goal
                                ),
                                type: 'line',
                                showLine: false,
                                borderColor: 'rgb(102, 108, 196)',
                                backgroundColor: 'rgb(102, 108, 196)',
                                pointRadius: 30,
                                pointBorderWidth: 2,
                                pointStyle: 'line',
                                hidden: true
                            },
                        ]
                    },
                    options: {
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    boxWidth: 10,
                                    boxHeight: 10,
                                    usePointStyle: true,
                                    pointStyle: 'circle',
                                }
                            }
                        }
                    }
                });

                console.log(data);
            })
            .catch((error) => {
                console.error("Ошибка:", error.message);
                alert("Не удалось загрузить график.");
                return Promise.reject(error);
            });
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }

    // try {
    //     fetch(urls.getWeightHistory, {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //             'X-CSRFToken': csrf,
    //             'X-Requested-With': 'XMLHttpRequest'
    //         },
    //         body: JSON.stringify({ period: "all", limit: 10 })
    //     })
    //         .then(response => {
    //             if (!response.headers.get("content-type")?.includes("application/json")) {
    //                 throw new Error('Ошибка сети');
    //             }
    //             return response.json();
    //         })
    //         .then(data => {
    //             if (data.error) {
    //                 alert(data.error);
    //                 return Promise.reject(new Error(data.error));
    //             }

    //             const labels = data.labels
    //             const data_points = data.data_points

    //             const lastFiveIndexStart = labels.length - 5;

    //             chartInstance = new Chart(ctx1, {
    //                 type: 'line',
    //                 data: {
    //                     labels: labels,
    //                     datasets: [{
    //                         label: 'Вес (в кг)',
    //                         data: data_points,
    //                         fill: false,
    //                         borderColor: 'rgb(255, 145, 0)',
    //                         backgroundColor: 'rgb(255, 166, 49)',
    //                         tension: 0.1,
    //                         pointRadius: 6,
    //                         pointHoverRadius: 8,
    //                     }],
    //                 },
    //                 options: {
    //                     scales: {
    //                         x: {
    //                             type: 'category',
    //                             offset: true,
    //                             min: lastFiveIndexStart >= 0 ? lastFiveIndexStart : 0,
    //                             max: labels.length - 1,
    //                             ticks: {
    //                                 autoSkip: false
    //                             },
    //                         },
    //                         y: {
    //                             position: 'right',
    //                             offset: true,
    //                             min: Math.round(Math.min(...data_points) - 1),
    //                             max: Math.round(Math.max(...data_points) + 1),
    //                             grid: {
    //                                 display: true,
    //                                 color: "rgba(0, 0, 0, 0.1)",
    //                                 lineWidth: 1,
    //                                 drawBorder: true
    //                             }
    //                         },
    //                     },
    //                     plugins: {
    //                         legend: false,
    //                         zoom: {
    //                             limits: {
    //                                 x: {
    //                                     min: 0,
    //                                     max: labels.length - 1
    //                                 },
    //                                 y: {
    //                                     min: Math.round(Math.min(...data_points) - 2),
    //                                     max: Math.round(Math.max(...data_points) + 2),
    //                                 },
    //                             },
    //                             pan: {
    //                                 enabled: true,
    //                                 mode: 'xy',
    //                             },
    //                             zoom: {
    //                                 wheel: {
    //                                     enabled: true,
    //                                 },
    //                                 pinch: {
    //                                     enabled: true
    //                                 },
    //                                 mode: 'xy',
    //                                 scaleMode: 'xy',
    //                             }
    //                         },
    //                         tooltip: {
    //                             enabled: true,
    //                             mode: 'index',
    //                             bodyFont: {
    //                                 size: 14,
    //                             },
    //                             titleFont: {
    //                                 size: 15,
    //                             },
    //                             padding: 12,
    //                             borderWidth: 2,
    //                             backgroundColor: 'rgba(0, 0, 0, 0.7)',
    //                             bodyColor: '#fff',
    //                             titleColor: '#fff',
    //                         },
    //                     },
    //                     responsive: true
    //                 }
    //             });

    //             document.getElementById("weightLoader").classList.add("d-none");
    //         })
    //         .catch(error => {
    //             console.error('Ошибка:', error.message);
    //             alert('Не удалось загрузить график.');
    //             return Promise.reject(error);
    //         });
    // } catch (error) {
    //     console.error('Ошибка загрузки данных:', error);
    // }

    // // Скрипт для графика в модальном окне с фильтрами
    // let chartFullInstance = null;
    // const filterBtn = document.getElementById("filterBtn");
    // const resetBtn = document.getElementById("resetBtn");
    // const filterButtons = {
    //     all: document.getElementById("allFilterBtn"),
    //     week: document.getElementById("weekFilterBtn"),
    //     month: document.getElementById("monthFilterBtn"),
    //     year: document.getElementById("yearFilterBtn")
    // };
    // const meanWeightValue = document.getElementById("meanWeightValue");
    // const maxWeightValue = document.getElementById("maxWeightValue");
    // const minWeightValue = document.getElementById("minWeightValue");

    // function handleFilterClick(filterType, buttonElement) {
    //     if (buttonElement.classList.contains('active')) return;
    //     Object.values(filterButtons).forEach(btn => {
    //         btn.classList.remove('active');
    //     });
    //     buttonElement.classList.add('active');
    //     updateModalChart(filterType);
    // }

    // filterButtons.all.addEventListener('click', () => handleFilterClick('all', filterButtons.all));
    // filterButtons.week.addEventListener('click', () => handleFilterClick('week', filterButtons.week));
    // filterButtons.month.addEventListener('click', () => handleFilterClick('month', filterButtons.month));
    // filterButtons.year.addEventListener('click', () => handleFilterClick('year', filterButtons.year));

    // resetBtn.addEventListener('click', function () {
    //     chartFullInstance.resetZoom();
    // })

    // filterBtn.addEventListener('click', function () {
    //     initModalChart();
    //     updateModalChart();
    // });

    // function initModalChart() {
    //     const ctx2 = document.getElementById('weightChartFull')

    //     if (chartFullInstance) {
    //         chartFullInstance.destroy();
    //     }

    //     chartFullInstance = new Chart(ctx2, {
    //         type: 'line',
    //         data: {
    //             labels: [],
    //             datasets: [{
    //                 label: 'Вес (в кг)',
    //                 data: [],
    //                 fill: false,
    //                 borderColor: 'rgb(255, 145, 0)',
    //                 backgroundColor: 'rgb(255, 166, 49)',
    //                 tension: 0.1,
    //                 pointRadius: 6,
    //                 pointHoverRadius: 8,
    //             }],
    //         },
    //         options: {
    //             scales: {
    //                 x: {
    //                     type: 'category',
    //                     offset: true,
    //                     min: 0,
    //                     max: 0,
    //                     ticks: {
    //                         autoSkip: false
    //                     },
    //                 },
    //                 y: {
    //                     position: 'right',
    //                     offset: true,
    //                     min: 0,
    //                     max: 0,
    //                     grid: {
    //                         display: true,
    //                         color: "rgba(0, 0, 0, 0.1)",
    //                         lineWidth: 1,
    //                         drawBorder: true
    //                     }
    //                 },
    //             },
    //             plugins: {
    //                 legend: false,
    //                 zoom: {
    //                     limits: {
    //                         x: {
    //                             min: 0,
    //                             max: 0,
    //                         },
    //                         y: {
    //                             min: 0,
    //                             max: 0,
    //                         },
    //                     },
    //                     pan: {
    //                         enabled: true,
    //                         mode: 'xy',
    //                     },
    //                     zoom: {
    //                         wheel: {
    //                             enabled: true,
    //                         },
    //                         pinch: {
    //                             enabled: true
    //                         },
    //                         mode: 'xy',
    //                         scaleMode: 'xy',
    //                     }
    //                 },
    //                 tooltip: {
    //                     enabled: true,
    //                     mode: 'index',
    //                     intersect: false,
    //                     bodyFont: {
    //                         size: 16,
    //                     },
    //                     titleFont: {
    //                         size: 17,
    //                     },
    //                     padding: 12,
    //                     borderWidth: 2,
    //                     backgroundColor: 'rgba(0, 0, 0, 0.7)',
    //                     bodyColor: '#fff',
    //                     titleColor: '#fff',
    //                 },
    //             }
    //         }
    //     });

    // };

    // function updateModalChart(period = 'all') {

    //     document.getElementById("fullWeightLoader").classList.remove("d-none");
    //     try {
    //         fetch(urls.getWeightHistory, {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 'X-CSRFToken': csrf,
    //                 'X-Requested-With': 'XMLHttpRequest'
    //             },
    //             body: JSON.stringify({ period: period, limit: 0 })
    //         })
    //             .then(response => {
    //                 if (!response.headers.get("content-type")?.includes("application/json")) {
    //                     throw new Error('Ошибка сети');
    //                 }
    //                 return response.json();
    //             })
    //             .then(data => {
    //                 if (data.error) {
    //                     alert(data.error);
    //                     return Promise.reject(new Error(data.error));
    //                 }

    //                 meanWeightValue.textContent = data.mean;
    //                 maxWeightValue.textContent = data.max;
    //                 minWeightValue.textContent = data.min;

    //                 chartFullInstance.data.labels = data.labels;
    //                 chartFullInstance.data.datasets[0].data = data.data_points;

    //                 const lastTenIndexStart = data.labels.length - 10;
    //                 chartFullInstance.options.scales.x.min = lastTenIndexStart >= 0 ? lastTenIndexStart : 0
    //                 chartFullInstance.options.scales.x.max = data.labels.length - 1

    //                 chartFullInstance.options.scales.y.min = Math.round(Math.min(...data.data_points) - 1)
    //                 chartFullInstance.options.scales.y.max = Math.round(Math.max(...data.data_points) + 1)

    //                 chartFullInstance.options.plugins.zoom.limits.x.max = data.labels.length - 1
    //                 chartFullInstance.options.plugins.zoom.limits.y.min = Math.round(Math.min(...data.data_points) - 3)
    //                 chartFullInstance.options.plugins.zoom.limits.y.max = Math.round(Math.max(...data.data_points) + 3)

    //                 console.log(chartFullInstance)

    //                 chartFullInstance.update();
    //             })
    //             .catch(error => {
    //                 console.error('Ошибка:', error.message);
    //                 alert('Не удалось загрузить график.');
    //                 return Promise.reject(error);
    //             });
    //     } catch (error) {
    //         console.error('Ошибка загрузки данных:', error);
    //     }
    //     document.getElementById("fullWeightLoader").classList.add("d-none");
    // };
});
