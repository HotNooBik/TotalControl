// Код для окна загрузки при поиске
const searchOverlay = document.getElementById("searchOverlay");
const loadingMessage = document.getElementById("loadingMessage");
const searchBtn = document.getElementById("sendbtn");
const addFoodBtns = document.querySelectorAll('[name="addFoodBtn"]');
const prevPageBtn = document.getElementById("prevPageBtn");
const nextPageBtn = document.getElementById("nextPageBtn");

function showSearchOverlay(message) {
    searchOverlay.classList.remove("d-none");
    loadingMessage.textContent = message;
}

searchBtn.addEventListener("click", () => {
    showSearchOverlay("Ищем продукты");
});

if (addFoodBtns) {
    addFoodBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            showSearchOverlay("Получаем информацию о продукте");
        });
    });
}

if (prevPageBtn) {
    [prevPageBtn, nextPageBtn].forEach((element) => {
        element.addEventListener("click", () => {
            showSearchOverlay("Загружаем продукты");
        });
    });
}

window.addEventListener("pageshow", function (event) {
    searchOverlay.classList.add("d-none");
});
