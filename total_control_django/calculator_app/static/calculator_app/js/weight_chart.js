// Скрипт для графика веса на главном экране
document.addEventListener('DOMContentLoaded', function () {
    const ctx1 = document.getElementById('weightChart')

    try {
        fetch(urls.getWeightHistory, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ period: "all", limit: 10, get_info: false })
        })
            .then(response => {
                if (!response.headers.get("content-type")?.includes("application/json")) {
                    throw new Error('Ошибка сети');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return Promise.reject(new Error(data.error));
                }

                const labels = data.labels
                const data_points = data.data_points

                const lastFiveIndexStart = labels.length - 5;

                chartInstance = new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Вес (в кг)',
                            data: data_points,
                            fill: false,
                            borderColor: 'rgb(255, 145, 0)',
                            backgroundColor: 'rgb(255, 166, 49)',
                            tension: 0.1,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                        }],
                    },
                    options: {
                        scales: {
                            x: {
                                type: 'category',
                                offset: true,
                                min: lastFiveIndexStart >= 0 ? lastFiveIndexStart : 0,
                                max: labels.length - 1,
                                ticks: {
                                    autoSkip: false
                                },
                            },
                            y: {
                                position: 'right',
                                offset: true,
                                min: Math.round(Math.min(...data_points) - 1),
                                max: Math.round(Math.max(...data_points) + 1),
                                grid: {
                                    display: true,
                                    color: "rgba(0, 0, 0, 0.1)",
                                    lineWidth: 1,
                                    drawBorder: true
                                }
                            },
                        },
                        plugins: {
                            legend: false,
                            zoom: {
                                limits: {
                                    x: {
                                        min: 0,
                                        max: labels.length - 1
                                    },
                                    y: {
                                        min: Math.round(Math.min(...data_points) - 2),
                                        max: Math.round(Math.max(...data_points) + 2),
                                    },
                                },
                                pan: {
                                    enabled: true,
                                    mode: 'xy',
                                },
                                zoom: {
                                    wheel: {
                                        enabled: true,
                                    },
                                    pinch: {
                                        enabled: true
                                    },
                                    mode: 'xy',
                                    scaleMode: 'xy',
                                }
                            },
                            tooltip: {
                                enabled: true,
                                mode: 'index',
                                bodyFont: {
                                    size: 14,
                                },
                                titleFont: {
                                    size: 15,
                                },
                                padding: 12,
                                borderWidth: 2,
                                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                                bodyColor: '#fff',
                                titleColor: '#fff',
                            },
                        },
                        responsive: true
                    }
                });

                document.getElementById("weightLoader").classList.add("d-none");
            })
            .catch(error => {
                console.error('Ошибка:', error.message);
                alert('Не удалось загрузить график.');
                return Promise.reject(error);
            });
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }


    // Скрипт для графика в модальном окне с фильтрами
    let chartFullInstance = null;
    const filterBtn = document.getElementById("filterBtn");
    const resetBtn = document.getElementById("resetBtn");
    const filterButtons = {
        all: document.getElementById("allFilterBtn"),
        week: document.getElementById("weekFilterBtn"),
        month: document.getElementById("monthFilterBtn"),
        year: document.getElementById("yearFilterBtn")
    };
    const meanWeightValue = document.getElementById("meanWeightValue");
    const maxWeightValue = document.getElementById("maxWeightValue");
    const minWeightValue = document.getElementById("minWeightValue");

    function handleFilterClick(filterType, buttonElement) {
        if (buttonElement.classList.contains('active')) return;
        Object.values(filterButtons).forEach(btn => {
            btn.classList.remove('active');
        });
        buttonElement.classList.add('active');
        updateModalChart(filterType);
    }

    filterButtons.all.addEventListener('click', () => handleFilterClick('all', filterButtons.all));
    filterButtons.week.addEventListener('click', () => handleFilterClick('week', filterButtons.week));
    filterButtons.month.addEventListener('click', () => handleFilterClick('month', filterButtons.month));
    filterButtons.year.addEventListener('click', () => handleFilterClick('year', filterButtons.year));

    resetBtn.addEventListener('click', function () {
        chartFullInstance.resetZoom();
    })


    filterBtn.addEventListener('click', function () {
        initModalChart();
        updateModalChart();
    });

    function initModalChart() {
        const ctx2 = document.getElementById('weightChartFull')

        if (chartFullInstance) {
            chartFullInstance.destroy();
        }

        chartFullInstance = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Вес (в кг)',
                    data: [],
                    fill: false,
                    borderColor: 'rgb(255, 145, 0)',
                    backgroundColor: 'rgb(255, 166, 49)',
                    tension: 0.1,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                }],
            },
            options: {
                scales: {
                    x: {
                        type: 'category',
                        offset: true,
                        min: 0,
                        max: 0,
                        ticks: {
                            autoSkip: false
                        },
                    },
                    y: {
                        position: 'right',
                        offset: true,
                        min: 0,
                        max: 0,
                        grid: {
                            display: true,
                            color: "rgba(0, 0, 0, 0.1)",
                            lineWidth: 1,
                            drawBorder: true
                        }
                    },
                },
                plugins: {
                    legend: false,
                    zoom: {
                        limits: {
                            x: {
                                min: 0,
                                max: 0,
                            },
                            y: {
                                min: 0,
                                max: 0,
                            },
                        },
                        pan: {
                            enabled: true,
                            mode: 'xy',
                        },
                        zoom: {
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'xy',
                            scaleMode: 'xy',
                        }
                    },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false,
                        bodyFont: {
                            size: 16,
                        },
                        titleFont: {
                            size: 17,
                        },
                        padding: 12,
                        borderWidth: 2,
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        bodyColor: '#fff',
                        titleColor: '#fff',
                    },
                }
            }
        });

    };

    function updateModalChart(period = 'all') {

        document.getElementById("fullWeightLoader").classList.remove("d-none");
        try {
            fetch(urls.getWeightHistory, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ period: period, limit: 0, get_info: true })
            })
                .then(response => {
                    if (!response.headers.get("content-type")?.includes("application/json")) {
                        throw new Error('Ошибка сети');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return Promise.reject(new Error(data.error));
                    }

                    meanWeightValue.textContent = data.mean;
                    maxWeightValue.textContent = data.max;
                    minWeightValue.textContent = data.min;

                    chartFullInstance.data.labels = data.labels;
                    chartFullInstance.data.datasets[0].data = data.data_points;

                    const lastTenIndexStart = data.labels.length - 10;
                    chartFullInstance.options.scales.x.min = lastTenIndexStart >= 0 ? lastTenIndexStart : 0
                    chartFullInstance.options.scales.x.max = data.labels.length - 1

                    chartFullInstance.options.scales.y.min = Math.round(Math.min(...data.data_points) - 1)
                    chartFullInstance.options.scales.y.max = Math.round(Math.max(...data.data_points) + 1)

                    chartFullInstance.options.plugins.zoom.limits.x.max = data.labels.length - 1
                    chartFullInstance.options.plugins.zoom.limits.y.min = Math.round(Math.min(...data.data_points) - 3)
                    chartFullInstance.options.plugins.zoom.limits.y.max = Math.round(Math.max(...data.data_points) + 3)

                    chartFullInstance.update();
                })
                .catch(error => {
                    console.error('Ошибка:', error.message);
                    alert('Не удалось загрузить график.');
                    return Promise.reject(error);
                });
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
        document.getElementById("fullWeightLoader").classList.add("d-none");
    };
});