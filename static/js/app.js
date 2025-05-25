/**
 * @fileoverview 前端 JavaScript，用于与会议管理 API 交互。
 * @version 1.0.1
 */

/**
 * @brief 当 DOM 完全加载后执行初始化操作。
 * @details 获取必要的 DOM 元素引用，为表单添加提交事件监听器，并加载初始会议列表。
 */
document.addEventListener('DOMContentLoaded', () => {
    /** @type {HTMLUListElement} 会议列表的 UL 元素 */
    const conferenceList = document.getElementById('conferenceList');
    /** @type {HTMLFormElement} 会议表单元素 */
    const conferenceForm = document.getElementById('conferenceForm');
    /** @type {HTMLInputElement} 隐藏的会议 ID 输入框 */
    const conferenceIdInput = document.getElementById('conferenceId');
    /** @type {HTMLInputElement} 会议名称输入框 */
    const nameInput = document.getElementById('name');
    /** @type {HTMLInputElement} 会议日期输入框 */
    const dateInput = document.getElementById('date');
    /** @type {HTMLInputElement} 会议地点输入框 */
    const locationInput = document.getElementById('location');
    /** @type {HTMLTextAreaElement} 会议描述文本域 */
    const descriptionInput = document.getElementById('description');
    /** @type {HTMLButtonElement} 表单提交按钮 */
    const submitBtn = document.getElementById('submitBtn');
    /** @type {HTMLButtonElement} 取消编辑按钮 */
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    /** @type {HTMLElement} 表单标题元素 */
    const formTitle = document.getElementById('formTitle');
    /** @type {HTMLDivElement} 显示消息的 Div */
    const messageArea = document.getElementById('messageArea');

    let isEditMode = false;

    /**
     * @brief 从 API 获取会议列表并更新页面显示。
     * @async
     */
    async function fetchAndDisplayConferences() {
        console.log("Fetching conferences...");
        try {
            const response = await fetch('/api/conferences');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const conferences = await response.json();
            console.log("Conferences received:", conferences);

            conferenceList.innerHTML = ''; // 清空当前列表

            if (conferences.length === 0) {
                conferenceList.innerHTML = '<li>未找到会议信息。</li>';
                return;
            }

            conferences.forEach(conf => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <div class="content">
                        <strong>${conf.name} (ID: ${conf.id})</strong>
                        日期: ${conf.date}<br>
                        地点: ${conf.location}<br>
                        ${conf.description ? `描述: ${conf.description}` : ''}
                    </div>
                    <div class="actions">
                        <button class="edit-btn" data-id="${conf.id}">编辑</button>
                        <button class="delete-btn" data-id="${conf.id}">删除</button>
                    </div>
                `;
                conferenceList.appendChild(listItem);
            });
        } catch (error) {
            console.error('获取会议列表失败:', error);
            conferenceList.innerHTML = '<li>加载会议列表失败，请重试。</li>';
            displayMessage('加载会议列表失败: ' + error.message, 'error');
        }
    }

    /**
     * @brief 处理会议表单提交事件 (添加或更新)。
     * @async
     * @param {Event} event 表单提交事件对象。
     */
    async function handleConferenceSubmit(event) {
        event.preventDefault(); // 阻止表单默认提交行为
        clearMessage();

        const conferenceData = {
            name: nameInput.value.trim(),
            date: dateInput.value,
            location: locationInput.value.trim(),
            description: descriptionInput.value.trim() || null
        };

        let url = '/api/conferences';
        let method = 'POST';

        if (isEditMode && conferenceIdInput.value) {
            url = `/api/conferences/${conferenceIdInput.value}`;
            method = 'PUT';
            console.log("Submitting updated conference:", conferenceData, "to", url);
        } else {
            console.log("Submitting new conference:", conferenceData);
        }

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(conferenceData),
            });

            const responseData = await response.json();

            if (!response.ok) {
                const errorMsg = responseData.detail || `HTTP error! status: ${response.status}`;
                console.error("Server response error:", responseData);
                throw new Error(errorMsg);
            }

            console.log(`Conference ${isEditMode ? 'updated' : 'added'} successfully:`, responseData);
            displayMessage(`会议已成功${isEditMode ? '更新' : '添加'}！`, 'success');
            resetForm();
            await fetchAndDisplayConferences();

        } catch (error) {
            console.error(`处理会议失败:`, error);
            displayMessage(`${isEditMode ? '更新' : '添加'}会议失败: ${error.message}`, 'error');
        }
    }

    /**
     * @brief 为编辑会议准备表单。
     * @async
     * @param {number} id 要编辑的会议 ID。
     */
    async function populateFormForEdit(id) {
        clearMessage();
        console.log(`Fetching conference ${id} for editing...`);
        try {
            const response = await fetch(`/api/conferences/${id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const conf = await response.json();

            conferenceIdInput.value = conf.id;
            nameInput.value = conf.name;
            dateInput.value = conf.date;
            locationInput.value = conf.location;
            descriptionInput.value = conf.description || '';

            formTitle.textContent = '编辑会议';
            submitBtn.textContent = '更新会议';
            cancelEditBtn.style.display = 'inline-block';
            isEditMode = true;
            nameInput.focus(); // 将焦点移到第一个输入框
        } catch (error) {
            console.error('获取会议详情失败:', error);
            displayMessage('获取会议详情失败: ' + error.message, 'error');
        }
    }

    /**
     * @brief 处理删除会议的请求。
     * @async
     * @param {number} id 要删除的会议 ID。
     */
    async function handleDeleteConference(id) {
        clearMessage();
        if (!confirm(`确定要删除 ID 为 ${id} 的会议吗？`)) {
            return;
        }
        console.log(`Deleting conference ${id}...`);
        try {
            const response = await fetch(`/api/conferences/${id}`, {
                method: 'DELETE',
            });

            const responseData = await response.json(); // FastAPI DELETE 返回 JSON

            if (!response.ok) {
                 const errorMsg = responseData.detail || `HTTP error! status: ${response.status}`;
                console.error("Server response error:", responseData);
                throw new Error(errorMsg);
            }
            console.log('Conference deleted successfully:', responseData);
            displayMessage(responseData.message || '会议已成功删除！', 'success');
            await fetchAndDisplayConferences();
        } catch (error) {
            console.error('删除会议失败:', error);
            displayMessage('删除会议失败: ' + error.message, 'error');
        }
    }

    /**
     * @brief 重置表单到添加模式。
     */
    function resetForm() {
        conferenceForm.reset();
        conferenceIdInput.value = '';
        formTitle.textContent = '添加新会议';
        submitBtn.textContent = '添加会议';
        cancelEditBtn.style.display = 'none';
        isEditMode = false;
        clearMessage();
    }

    /**
     * @brief 在页面上显示消息。
     * @param {string} message 要显示的消息。
     * @param {'success'|'error'} type 消息类型。
     */
    function displayMessage(message, type) {
        messageArea.textContent = message;
        messageArea.className = type; // 'success' or 'error'
    }

    /**
     * @brief 清除页面上显示的消息。
     */
    function clearMessage() {
        messageArea.textContent = '';
        messageArea.className = '';
    }

    // --- 事件监听器 ---
    if (conferenceForm) {
        conferenceForm.addEventListener('submit', handleConferenceSubmit);
    } else {
        console.error("无法找到 #conferenceForm 元素！");
    }

    if (conferenceList) {
        conferenceList.addEventListener('click', (event) => {
            const target = event.target;
            if (target.classList.contains('edit-btn')) {
                const id = target.dataset.id;
                populateFormForEdit(parseInt(id));
            } else if (target.classList.contains('delete-btn')) {
                const id = target.dataset.id;
                handleDeleteConference(parseInt(id));
            }
        });
        // 页面加载时首次获取并显示会议
        fetchAndDisplayConferences();
    } else {
         console.error("无法找到 #conferenceList 元素！");
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', resetForm);
    }

});