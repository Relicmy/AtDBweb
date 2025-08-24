class App {
    constructor() {
        this.backend = null;
        this.initBackend();
        this.initManagers();
    }

    initBackend() {
        if (typeof qt === 'undefined') {
            console.warn("Qt WebChannel недоступен");
            setTimeout(() => this.initBackend(), 1000);
            return;
        }

        new QWebChannel(qt.webChannelTransport, channel => {
            this.backend = channel.objects.bridge;
            console.log("Подключено к бэкенду:", this.backend);

            if (this.backend?.getTasks) {
                this.backend.getTasks().then(tasks => {
                    this.modalManager.updateTaskList(tasks);
                }).catch(console.error);
            }

            this.initUI();
        });
    }

    initManagers() {
        this.modalManager = new ModalManager(this);
        this.panelManager = new PanelManager(this);
        this.tabManager = new TabManager(this);
        this.fileUploadManager = new FileUploadManager(this);
    }

    initUI() {
        document.getElementById("create-task")?.addEventListener("click", () => {
            this.modalManager.open({
                title: "Новая задача",
                placeholder: "Введите название",
                buttons: [
                    { id: "cancel-create", class: "btn-cancel", action: "cancel", text: "Отмена" },
                    { id: "confirm-create", class: "btn-create", action: "create", text: "Создать" }
                ]
            });
        });

        document.getElementById("del-task")?.addEventListener("click", () => {
            this.modalManager.open({
                title: "Удалить задачу",
                placeholder: "Введите название",
                buttons: [
                    { id: "cancel-delete", class: "btn-cancel", action: "cancel", text: "Отмена" },
                    { id: "confirm-delete", class: "btn-delete", action: "delete", text: "Удалить" }
                ]
            });
        });

        this.panelManager.init();
        this.tabManager.init();
        this.fileUploadManager.init();
        this.panelManager.showDefaultPanel();
    }
}

class ModalManager {
    constructor(app) {
        this.app = app;
        this.container = document.getElementById("modal-create");
    }

    open({ title, placeholder, buttons }) {
        if (!this.container) return;

        this.container.innerHTML = `
            <div id="modal-create-task">
                <h3>${title}</h3>
                <input id="name-task" type="text" placeholder="${placeholder}" autofocus>
                <div class="modal-buttons">
                    ${buttons.map(btn => `
                        <button id="${btn.id}" class="b-create-task ${btn.class}" data-action="${btn.action}">
                            ${btn.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        this.container.style.display = "flex";
        document.getElementById("name-task")?.focus();
        this.setupButtonHandlers();
    }

    setupButtonHandlers() {
        document.querySelectorAll("#modal-create-task button").forEach(button => {
            button.addEventListener("click", () => {
                const action = button.dataset.action;
                const name = document.getElementById("name-task")?.value.trim();

                if (action === "cancel") {
                    this.close();
                    return;
                }

                if (!name) {
                    alert("Пожалуйста, введите название задачи");
                    document.getElementById("name-task")?.focus();
                    return;
                }

                this.handleAction(action, name);
            });
        });
    }

    handleAction(action, name) {
        if (!this.app.backend) {
            console.error("Бэкенд не доступен");
            return;
        }

        switch (action) {
            case "delete":
                this.app.backend.dellTask(name);
                break;
            case "create":
                this.app.backend.addTask(name);
                break;
        }
        this.updateTaskListAfterAction();
        this.close();
    }

    async updateTaskListAfterAction() {
        try {
            // Предположим, что бэкенд возвращает список задач
            const tasks = await this.app.backend.getTasks();
            // ✅ Вызываем updateTaskList в правильном контексте
            this.updateTaskList(Array.isArray(tasks) ? tasks : []);
        } catch (err) {
            console.warn("Не удалось получить список задач:", err);
            // Можно оставить старый список
        }
    }

    close() {
        if (!this.container) return;
        this.container.innerHTML = "";
        this.container.style.display = "none";
    }

    updateTaskList(tasks = []) {
        const list = document.getElementById("task-list");
        if (!list) return;

        list.innerHTML = tasks.length
            ? tasks.map(task => `<div class="button-task">${task}</div>`).join('')
            : '<div class="not-tasks"><img src="/AutoDataset/public/folder-add-file.svg" alt="">Создайте новую задачу</div>';
    }
}

class PanelManager {
    constructor(app) {
        this.app = app;
    }

    init() {
        this.setupBackButton();
        this.setupTaskList();
    }

    setupBackButton() {
        document.getElementById("back-button")?.addEventListener("click", () => this.showDefaultPanel());
    }

    setupTaskList() {
        const taskList = document.getElementById("task-list");
        if (!taskList) return;

        taskList.addEventListener("click", (e) => {
            const target = e.target.closest(".button-task");
            if (!target) return;

            document.querySelectorAll(".button-task").forEach(el => el.classList.remove("active"));
            target.classList.add("active");
            this.showSettingsPanel(target.textContent);
        });
    }

    showDefaultPanel() {
        document.getElementById("default-panel")?.classList.remove("hidden");
        document.getElementById("settings-ui")?.classList.add("hidden");
        document.querySelectorAll(".button-task").forEach(el => el.classList.remove("active"));
    }

    showSettingsPanel(taskName = "") {
        document.getElementById("default-panel")?.classList.add("hidden");
        document.getElementById("settings-ui")?.classList.remove("hidden");
        document.getElementById("current-task-name").textContent = taskName || "Текущая задача";
    }
    
}

class TabManager {
    constructor(app) {
        this.app = app;
    }

    async init() {
        this.setupTabs();
        
        await this.loadInitialTab();
    }

    setupTabs() {
        document.querySelectorAll(".tab").forEach(button => {
            button.addEventListener("click", () => this.handleTabClick(button));
        });
    }

    async loadInitialTab() {
        const defaultTab = document.querySelector('.tab[data-tab="append-file"]');
        if (defaultTab) await this.handleTabClick(defaultTab);
    }

    async handleTabClick(button) {
        const tabId = button.getAttribute("data-tab");

        document.querySelectorAll(".tab").forEach(btn => btn.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(pane => pane.classList.remove("active"));

        button.classList.add("active");
        const targetPane = document.getElementById("tab-" + tabId);
        if (!targetPane) return;

        targetPane.classList.add("active");

        if (tabId === "augmentation") {
            await this.loadAugmentationTab(targetPane);
        }
    }
    initAugmentationSettings(container) {
        console.log("🔧 initAugmentationSettings: старт");

        // === 1. Кнопки "Обзор" ===
        document.querySelectorAll('.browse-btn[data-action="browse"]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const targetId = btn.dataset.target;
                const input = document.getElementById(targetId);
                const backend = this.app.backend;

                if (!input || typeof backend?.openDirectoryDialog !== 'function') {
                    console.error("openDirectoryDialog недоступен");
                    return;
                }

                try {
                    const path = await backend.openDirectoryDialog();
                    if (path) input.value = path;
                } catch (err) {
                    console.error("Ошибка выбора папки:", err);
                    alert("Не удалось открыть диалог выбора папки.");
                }
            });
        });

        // === 2. Переключение .op-params (операции) ===
        document.querySelectorAll('.op-toggle').forEach(toggle => {
            const card = toggle.closest('.operation-card');
            const params = card?.querySelector('.op-params');
            if (!params) return;

            params.style.display = toggle.checked ? 'grid' : 'none';

            toggle.addEventListener('change', function () {
                params.style.display = this.checked ? 'grid' : 'none';
            });
        });

        // === 3. Цвета ===
        const setupColorPicker = (input, btn, list) => {
            if (!input || !btn || !list) return;
            btn.addEventListener('click', () => {
                const color = input.value;
                const item = document.createElement('div');
                item.className = 'color-item';
                item.style.backgroundColor = color;
                item.dataset.color = color;
                item.addEventListener('click', () => item.remove());
                list.appendChild(item);
                input.value = '#000000';
            });
        };

        setupColorPicker(
            document.querySelector('.color-input[data-purpose="bg"]'),
            document.querySelector('.add-color-btn[data-purpose="bg"]'),
            document.getElementById('color-list')
        );

        setupColorPicker(
            document.querySelector('.color-input[data-purpose="group"]'),
            document.querySelector('.add-color-btn[data-purpose="group"]'),
            document.getElementById('group-color-list')
        );

        // === 4. Переключатели фона и группировки ===
        const bgToggle = document.getElementById('bg-replace-toggle');
        const bgParams = document.querySelector('.bg-params');
        if (bgToggle && bgParams) {
            bgParams.style.display = bgToggle.checked ? 'block' : 'none';
            bgToggle.addEventListener('change', () => {
                bgParams.style.display = bgToggle.checked ? 'block' : 'none';
            });
        }

        const groupToggle = document.getElementById('grouping-toggle');
        const groupParams = document.querySelector('.group-params');
        if (groupToggle && groupParams) {
            groupParams.style.display = groupToggle.checked ? 'block' : 'none';
            groupToggle.addEventListener('change', () => {
                groupParams.style.display = groupToggle.checked ? 'block' : 'none';
            });
        }

        // === 5. Радиокнопки ===
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', function () {
                document.querySelectorAll(`input[name="${this.name}"]`)
                    .forEach(r => {
                        const custom = r.nextElementSibling;
                        if (custom && custom.classList.contains('radio-custom')) {
                            if (r.checked) {
                                custom.style.backgroundColor = '#bb86fc'; // или добавь класс
                            } else {
                                custom.style.backgroundColor = '';
                            }
                        }
                    });
            });
        });

            // === Кнопка сохранения аугментации
        document.getElementById('update-Augmentations')?.addEventListener('click', () => {
            const backend = this.app.backend;
            let name_task = document.getElementById("current-task-name");
            if (typeof backend?.update_augmentations !== 'function') {
                alert("❌ update_augmentation недоступна");
                return;
            }
            const page_settings = document.getElementById('tab-augmentation')
            const htmlContent = page_settings.innerHTML;
            this.app.backend.update_augmentations(name_task.textContent.trim(), htmlContent);
        })

        // === 6. Кнопка запуска ===
        document.getElementById('start-augmentation')?.addEventListener('click', () => {
            const backend = this.app.backend;
            if (typeof backend?.startAugmentation !== 'function') {
                alert("❌ startAugmentation недоступна");
                return;
            }

            const config = {
                input_img: document.getElementById('input-path-img')?.value?.trim() || '',
                output_img: document.getElementById('output-path-img')?.value?.trim() || '',
                input_txt: document.getElementById('input-path-txt')?.value?.trim() || '',
                output_txt: document.getElementById('output-path-txt')?.value?.trim() || '',
                mode: document.querySelector('input[name="process-mode"]:checked')?.value,
                bg_enabled: document.getElementById('bg-replace-toggle')?.checked,
                group_enabled: document.getElementById('grouping-toggle')?.checked
            };

            if (!config.input_img || !config.output_img || !config.input_txt || !config.output_txt) {
                alert("Заполните все пути ввода/вывода.");
                return;
            }

            console.log("🚀 Конфиг:", config);
            backend.startAugmentation(JSON.stringify(config));
            alert("✅ Аугментация запущена!");
        });

        console.log("✅ initAugmentationSettings: готова");
    }


    async loadAugmentationTab(container) {
        try {
            container.innerHTML = '<div class="tab-loader">Загрузка...</div>';
            let name_task = document.getElementById("current-task-name");

            if (!name_task) {
                throw new Error("Элемент current-task-name не найден");
            }

            console.log("Название задачи:", name_task.textContent);

            // Передаем название задачи в бэкенд и получаем HTML строку
            const html = await this.app.backend.renderHTML(name_task.textContent.trim());

            // Просто вставляем HTML, не обрабатываем как Response
            container.innerHTML = html;

            // Передаём container для надёжности
            this.initAugmentationSettings(container);

        } catch (error) {
            console.error("Ошибка загрузки:", error);
            container.innerHTML = '<div class="tab-error">Ошибка загрузки: ' + error.message + '</div>';
        }
    }

    initElementSelection() {
        // 1. Функция для получения XPath
        const getXPath = (element) => {
            if (!element) return "";
            if (element.id) return `//*[@id="${element.id}"]`;
            if (element === document.body) return "/html/body";

            let ix = 0;
            const siblings = element.parentNode.childNodes;
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) {
                    return `${getXPath(element.parentNode)}/${element.tagName}[${ix + 1}]`;
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
            return "";
        };

        // 2. Обработчик кликов
        document.addEventListener("click", (e) => {
            e.preventDefault();
            const element = e.target;

            // Удаляем предыдущее выделение
            document.querySelectorAll(".highlighted-element").forEach(el => {
                el.classList.remove("highlighted-element");
            });

            // Добавляем новый маркер
            element.classList.add("highlighted-element");

            // Подготавливаем данные
            const data = {
                xpath: getXPath(element),
                rect: element.getBoundingClientRect(),
                html: element.outerHTML
            };

            // Отправляем через WebChannel
            // if (window.pySide?.sendData) {
            //     window.pySide.sendData(JSON.stringify(data));
            // } else {
            //     console.warn("WebChannel не доступен");
            // }
        }); 
    }
    initBrowserTab() {
        document.getElementById('start-browser')?.addEventListener('click', () => {
            this.startSeleniumBrowser();
        });
    }

    startSeleniumBrowser() {
        const container = document.getElementById('browser-container');
        container.style.display = 'block';

        if (window.pySide?.startBrowser) {
            window.pySide.startBrowser();
        } else {
            console.error('WebChannel not connected');
        }
    }
}

class FileUploadManager {
    constructor(app) {
        this.app = app;
    }

    init() {
        const dropZone = document.getElementById('dropZone');
        if (!dropZone) return;

        const elements = {
            fileInputImage: document.getElementById('fileInput-image'),
            fileInputCoords: document.getElementById('fileInput-coords'),
            fileListImage: document.getElementById('fileList-image'),
            fileListCoords: document.getElementById('fileList-coords'),
            fileNameCC: document.getElementById('coords-cheaker'),
            fileNameIC: document.getElementById('image-cheaker')
        };

        if (Object.values(elements).some(el => !el)) return;

        elements.fileInputImage.addEventListener('change', (e) =>
            this.handleFileUpload(e.target.files, elements.fileNameIC, elements.fileListImage, 'image'));

        elements.fileInputCoords.addEventListener('change', (e) =>
            this.handleFileUpload(e.target.files, elements.fileNameCC, elements.fileListCoords, 'coords'));

        dropZone.addEventListener('dragover', this.handleDragOver);
        dropZone.addEventListener('dragleave', this.handleDragLeave);
        dropZone.addEventListener('drop', (e) => this.handleDrop(e, elements));
    }

    handleFileUpload(files, fileNameElement, fileListElement, type) {
        if (!files.length) {
            fileNameElement.textContent = type === 'image'
                ? 'Изображения не выбраны'
                : 'Файлы координат не выбраны';
            fileListElement.innerHTML = '';
            return;
        }

        fileNameElement.textContent = files.length === 1
            ? files[0].name
            : `${files.length} файлов выбрано`;

        fileListElement.innerHTML = '';
        const list = document.createElement('ul');

        Array.from(files).forEach(file => {
            const item = document.createElement('li');
            item.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            list.appendChild(item);
        });

        fileListElement.appendChild(list);
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('highlight');
    }

    handleDragLeave(e) {
        e.currentTarget.classList.remove('highlight');
    }

    handleDrop(e, elements) {
        e.preventDefault();
        e.currentTarget.classList.remove('highlight');

        if (!e.dataTransfer.files.length) return;

        const isImage = Array.from(elementsFromPoint(e.clientX, e.clientY))
            .some(el => el.classList.contains('fileInput-image'));

        const targetInput = isImage ? elements.fileInputImage : elements.fileInputCoords;
        targetInput.files = e.dataTransfer.files;
        targetInput.dispatchEvent(new Event('change'));
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${units[i]}`;
    }
}

function addItem() {
    const container = document.getElementById('items-container');
    const item = document.createElement('div');
    item.className = 'item';
    item.innerHTML = `
      <input class="int-form" type="text" placeholder="введите адрес страницы">
      <input class="int-form" type="text" placeholder="введите css класс элемента">
      <input class="int-form" type="text" placeholder="введите текст элемента">
      <input class="int-form" type="text" placeholder="введите классовость элемента">
      <button type="button" class="remove-btn" onclick="removeItem(this)">✕</button>
    `;
    container.appendChild(item);
}

function removeItem(button) {
    const item = button.parentElement;
    if (document.querySelectorAll('.item').length > 1) {
        item.remove();
    } else {
        alert("Нельзя удалить последнюю позицию.");
    }
}

// Функция для получения всех данных
function getFormData() {
    const items = [];
    document.querySelectorAll('.item').forEach(item => {
        const inputs = item.querySelectorAll('input');
        items.push({
            url: inputs[0].value,
            cssClass: inputs[1].value,
            text: inputs[2].value,
            klassnost: inputs[3].value  // "классовость" — как в вашем примере
        });
    });
    return items;
}

// function initAugmentationSettings() {
//     console.log("🔧 initAugmentationSettings: старт");

//     // 1. Кнопки "Обзор"
//     document.querySelectorAll('.browse-btn[data-action="browse"]').forEach(btn => {
//         btn.addEventListener('click', async () => {
//             const targetId = btn.dataset.target;
//             const input = document.getElementById(targetId);
//             // Проверяем, что backend и метод доступны
//             if (!input || typeof backend?.openDirectoryDialog !== 'function') {
//                 console.error("backend.openDirectoryDialog недоступен или input не найден");
//                 return;
//             }

//             try {
//                 const path = await backend.openDirectoryDialog();
//                 if (path) input.value = path;
//             } catch (err) {
//                 console.error("Ошибка выбора папки:", err);
//                 alert("Не удалось открыть диалог выбора папки.");
//             }
//         });
//     });

//     // 2. Переключение .op-params для операций
//     document.querySelectorAll('.op-toggle').forEach(toggle => {
//         const card = toggle.closest('.operation-card');
//         const params = card?.querySelector('.op-params');
//         if (!params) return;

//         // Инициализация: показываем/скрываем при загрузке
//         params.style.display = toggle.checked ? 'grid' : 'none';

//         // Обработчик изменения
//         toggle.addEventListener('change', function () {
//             params.style.display = this.checked ? 'grid' : 'none';
//         });
//     });

//     // 3. Цвета
//     const setupColorPicker = (input, btn, list) => {
//         if (!input || !btn || !list) {
//             console.warn("setupColorPicker: один из элементов не найден", { input, btn, list });
//             return;
//         }

//         btn.addEventListener('click', () => {
//             const color = input.value;
//             const item = document.createElement('div');
//             item.className = 'color-item';
//             item.style.backgroundColor = color;
//             item.dataset.color = color;
//             item.addEventListener('click', () => item.remove());
//             list.appendChild(item);
//             // Сброс цвета после добавления (опционально)
//             input.value = '#000000';
//         });
//     };

//     setupColorPicker(
//         document.querySelector('.color-input[data-purpose="bg"]'),
//         document.querySelector('.add-color-btn[data-purpose="bg"]'),
//         document.getElementById('color-list')
//     );

//     setupColorPicker(
//         document.querySelector('.color-input[data-purpose="group"]'),
//         document.querySelector('.add-color-btn[data-purpose="group"]'),
//         document.getElementById('group-color-list')
//     );

//     // 4. Переключатели фона и группировки
//     const bgToggle = document.getElementById('bg-replace-toggle');
//     const bgParams = document.querySelector('.bg-params');
//     if (bgToggle && bgParams) {
//         bgParams.style.display = bgToggle.checked ? 'block' : 'none';
//         bgToggle.addEventListener('change', () => {
//             bgParams.style.display = bgToggle.checked ? 'block' : 'none';
//         });
//     }

//     const groupToggle = document.getElementById('grouping-toggle');
//     const groupParams = document.querySelector('.group-params');
//     if (groupToggle && groupParams) {
//         groupParams.style.display = groupToggle.checked ? 'block' : 'none';
//         groupToggle.addEventListener('change', () => {
//             groupParams.style.display = groupToggle.checked ? 'block' : 'none';
//         });
//     }

//     // 5. Радиокнопки
//     document.querySelectorAll('input[type="radio"]').forEach(radio => {
//         const option = radio.closest('.radio-option');
//         if (!option) return;

//         radio.addEventListener('change', () => {
//             document.querySelectorAll(`input[name="${radio.name}"]`)
//                 .forEach(r => r.closest('.radio-option')?.classList.remove('active'));
//             option.classList.add('active');
//         });

//         // Инициализация
//         if (radio.checked) {
//             option.classList.add('active');
//         }
//     });

//     // 6. Кнопка запуска
//     document.getElementById('start-augmentation')?.addEventListener('click', () => {
//         if (typeof backend?.startAugmentation !== 'function') {
//             alert("❌ Функция startAugmentation недоступна. Проверь backend.");
//             console.error("backend.startAugmentation не является функцией");
//             return;
//         }

//         const config = {
//             input_img: document.getElementById('input-path-img')?.value?.trim() || '',
//             output_img: document.getElementById('output-path-img')?.value?.trim() || '',
//             input_txt: document.getElementById('input-path-txt')?.value?.trim() || '',
//             output_txt: document.getElementById('output-path-txt')?.value?.trim() || '',
//             mode: document.querySelector('input[name="process-mode"]:checked')?.value,
//             bg_enabled: document.getElementById('bg-replace-toggle')?.checked,
//             group_enabled: document.getElementById('grouping-toggle')?.checked
//         };

//         // Проверка обязательных полей
//         if (!config.input_img || !config.output_img || !config.input_txt || !config.output_txt) {
//             alert("Заполните все пути ввода/вывода.");
//             return;
//         }

//         console.log("🚀 Конфиг аугментации:", config);

//         try {
//             backend.startAugmentation(JSON.stringify(config));
//             alert("✅ Аугментация запущена!");
//         } catch (err) {
//             console.error("Ошибка при вызове startAugmentation:", err);
//             alert("❌ Ошибка при запуске аугментации.");
//         }
//     });

//     console.log("✅ initAugmentationSettings: готова");
// }

// Запуск приложения
document.addEventListener('DOMContentLoaded', () => {
    new App();
});