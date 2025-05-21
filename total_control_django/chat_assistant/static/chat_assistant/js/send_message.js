// Скрипты для отображения вопроса после ввода и сообщения о загрузке ответа
const link = document.getElementById("chat-link");
link.classList.remove('fs-5');
link.classList.add('menu-link-active', 'fs-4');

const fileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const messageBox = document.getElementById('message-box');
const form = document.getElementById('sendMsg');
const messageArea = document.getElementById('chat');

function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

function renderPreviewImage(imageSrc) {
    preview.innerHTML = `
        <div class="position-relative d-inline-block">
            <img src="${imageSrc}" class="img-fluid rounded border" style="height:50px; width:50px;" alt="Предпросмотр изображения">
            <button type="button" class="btn-close position-absolute top-0 start-100 translate-middle" 
                    aria-label="Удалить изображение" style="background-color: white;" id="remove-image"></button>
        </div>
    `;
    document.getElementById('remove-image').addEventListener('click', () => {
        fileInput.value = '';
        preview.innerHTML = '';
    });
}

document.addEventListener('paste', function (event) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (const item of items) {
        if (item.type.indexOf("image") !== -1) {
            const blob = item.getAsFile();
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(blob);
            fileInput.files = dataTransfer.files;

            const reader = new FileReader();
            reader.onload = function (e) {
                renderPreviewImage(e.target.result);
            };
            reader.readAsDataURL(blob);
        }
    }
});

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            renderPreviewImage(e.target.result);
        };
        reader.readAsDataURL(file);
    }
});

form.addEventListener('submit', function(e) {
    e.preventDefault();

    const messageText = escapeHTML(messageBox.value.trim());
    if (!messageText) return;
    
    const file = fileInput.files[0];

    function finishAndSubmit() {
        const botMessage = document.createElement('div');
        botMessage.className = 'row d-flex flex-row justify-content-lg-start mb-3 pt-1';
        botMessage.innerHTML = `
            <div class="col-auto">
                <div class="d-flex align-items-center justify-content-center rounded-circle bg-ferngreen text-white" 
                    style="width: 50px; height: 50px;">
                    <i class="fa-solid fa-robot fs-3"></i>
                </div>
            </div>
            <div class="col-auto">
                <div class="px-3 py-2 pb-1 ms-3 my-2 rounded-3 bg-secondary-subtle text-start">
                    <span class="typing-dots">
                        <span class="dot">.</span>
                        <span class="dot">.</span>
                        <span class="dot">.</span>
                    </span>
                </div>
            </div>
        `;
        messageArea.appendChild(botMessage);
        messageArea.scrollTop = messageArea.scrollHeight;

        setTimeout(() => {
            form.submit();
            messageBox.value = '';
            fileInput.value = '';
            preview.innerHTML = '';
        }, 500);
    }

    let userMessageHTML = `
        <div class="row d-flex flex-row justify-content-end mb-3 pt-1">
            <div class="col-auto">
                ${messageText ? `<div class="px-3 py-2 ms-3 my-2 rounded-3 bg-ferngreen-lighter text-start">${messageText}</div>` : ''}
    `;

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            userMessageHTML += `
                    <div class="d-flex justify-content-end my-2">
                        <img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px; max-width: 200px;" alt="Image">
                    </div>
                    <p class="small ms-3 mt-2 rounded-3 text-muted d-flex justify-content-end">сейчас</p>
                </div>
            </div>
            `;
            messageArea.insertAdjacentHTML('beforeend', userMessageHTML);
            messageArea.scrollTop = messageArea.scrollHeight;
            finishAndSubmit();
        };
        reader.readAsDataURL(file);
    } else {
        userMessageHTML += `<p class="small ms-3 mt-2 rounded-3 text-muted d-flex justify-content-end">сейчас</p></div></div>`;
        messageArea.insertAdjacentHTML('beforeend', userMessageHTML);
        messageArea.scrollTop = messageArea.scrollHeight;
        finishAndSubmit();
    }
});

messageArea.scrollTop = messageArea.scrollHeight;