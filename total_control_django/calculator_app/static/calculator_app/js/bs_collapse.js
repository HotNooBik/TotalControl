// Скрипт для изменения кнопки для раскрытия добавленной еды
document.addEventListener('hide.bs.modal', function (event) {
    if (document.activeElement) {
        document.activeElement.blur();
    }
});

const collapseElement = document.getElementById('collapseMealsToday');
const collapseMealsTodayIcon = document.getElementById('collapseMealsTodayIcon');

collapseElement.addEventListener('show.bs.collapse', function () {
    collapseMealsTodayIcon.classList.remove('fa-caret-down');
    collapseMealsTodayIcon.classList.add('fa-caret-up');
});

collapseElement.addEventListener('hide.bs.collapse', function () {
    collapseMealsTodayIcon.classList.remove('fa-caret-up');
    collapseMealsTodayIcon.classList.add('fa-caret-down');
});
