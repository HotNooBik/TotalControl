// Код для удаления еды из избранного, путем нажатия на Удалить в списке избранного
let formIdToDelete = null;

function setFormId(foodId) {
    formIdToDelete = foodId;
}

document
    .getElementById("confirm-delete-btn")
    .addEventListener("click", function () {
        if (formIdToDelete) {
            document
                .getElementById("remove-food-form-" + formIdToDelete)
                .submit();
        }
    });
