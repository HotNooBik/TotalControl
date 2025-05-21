const options = document.querySelectorAll('.activity-option');
const hiddenInput = document.querySelector('#id_activity_coef');
const currentCoef = hiddenInput.value

function setActiveOption(selectedOption) {
    options.forEach(option => {
        option.classList.remove('active');
    });
    selectedOption.classList.add('active');
    hiddenInput.value = selectedOption.dataset.value;
}

options.forEach(option => {
    option.addEventListener('click', function () {
        setActiveOption(this);
    });
});

// Активируем элемент пользователя по умолчанию
switch (currentCoef) {
    case '1.2':
        setActiveOption(options[0]);
        break;
    case '1.375':
        setActiveOption(options[1]);
        break;
    case '1.5':
        setActiveOption(options[2]);
        break;
    default:
        setActiveOption(options[3]);
}
