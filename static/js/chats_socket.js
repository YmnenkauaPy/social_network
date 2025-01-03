document.addEventListener('DOMContentLoaded', () => {
    const chatSelectors = document.querySelectorAll('.chat-selector');
    const chatDisplay = document.getElementById('chat-display');
    let socket;
    const avatarUrl = document.getElementById('user-data').dataset.avatar;

    chatSelectors.forEach(chat => {
        chat.addEventListener('click', function(event) {
            event.preventDefault();
            const chatId = this.getAttribute('data-chat-id');
            if (socket) {
                socket.close();
            }
            socket = new WebSocket(`ws://${window.location.host}/ws/chat/${chatId}/`);
            loadChat(chatId);
        });
    });

    function markMessageAsRead(messageId, chatId) {
        if (socket) {
            socket.send(JSON.stringify({
                'event': 'mark_as_read',
                'id': messageId,
                'chat_id':chatId,
            }));
        }
    }

    function makeLastMessage(messageId, chatId) {
        if (socket) {
            socket.send(JSON.stringify({
                'event': 'make_last_message',
                'chat_id': Number(chatId),
                'msg_id': messageId,
            }));
        }
    }

    function loadChat(chatId) {
        chatDisplay.innerHTML = '<p class="text-muted fs-5">Loading chat...</p>';
        const user = document.getElementById('user').getAttribute('value')

        fetch(`/get/chat/${chatId}/`)
            .then(response => response.text())
            .then(data => {
                chatDisplay.innerHTML = data;
                initializeWebSocket(chatId, user);
                loadMessages(chatId, user);
                initializeMessageForm();

                const chatScroll = document.getElementById('chat-scroll');
                if (chatScroll) {
                    chatScroll.scrollTop = chatScroll.scrollHeight;
                }
            })
            .catch(error => {
                console.error('Error loading chat:', error);
                chatDisplay.innerHTML = '<p class="text-danger">Failed to load chat.</p>';
            });
    }

    function initializeWebSocket(chatId, user) {
        if (socket) {
            socket.onmessage = null;
        } else {
            socket = new WebSocket(`ws://${window.location.host}/ws/chat/${chatId}/`);
        }

        socket.onmessage = async function(e) {
            const data = JSON.parse(e.data);

            const response = await fetch(`/get/messages/${chatId}/`);
            const answer = await response.json();
            const exists = answer.messages.some(message => Number(message.id) === Number(data.id));

            const noMessagesElement = document.getElementById('noMessages');
            if (noMessagesElement) {
                noMessagesElement.remove();
            }

            if (data['event'] === 'send_message' && exists) {
                const chatLog = document.getElementById('chat-log');
                const isOwnMessage = data.sender_id === Number(user);

                let messageElement;

                let formattedContent = '';

                if (data.content) {
                    formattedContent = formatContent(data.content);

                    const links = extractLinks(formattedContent);
                    formattedContent = links.length > 0
                        ? `<a href="${links[0]}">${formattedContent}</a>`
                        : formattedContent;
                }

                const date = data.sent_at
                const formattedDate = formatDate(date);

                let truncatedText;

                if (data.replied_to_content) {
                    truncatedText = truncateText(data.replied_to_content, 15);
                }

                if (isOwnMessage) {
                    messageElement = `
                        <div class="d-flex align-items-start justify-content-end mb-2">
                            ${truncatedText ? `<a href="javascript:void(0)" onclick="findMessageThatWasReplied(${data.replied_to_id})"><div class="bg-light text-muted p-1 rounded">
                                <small>Replied to: ${truncatedText}</small>
                            </div></a>` : ''}
                            <i class="bi bi-arrow-return-right" onclick="replyToMessage('message-${data.id}')" aria-hidden="true"></i>
                            <div class="position-relative d-inline-block mt-auto">
                                ${data.user_liked
                                    ? `<i class="bi bi-heart-fill fs-5" style="color:red" id="icon_like_${data.id}"></i>`
                                    : `<i class="bi bi-heart fs-5" style="color:red" id="icon_like_${data.id}" onclick="liked(${data.id})"></i>`}
                                <span id = "likes_count_${data.id}" class="position-absolute top-50 start-50 translate-middle text-black fw-bold" onclick="liked(${data.id})">${data.liked > 0 ? data.liked : ''}</span>
                            </div>
                            <div style="background-color: rgb(240, 240, 240)" class="text-dark p-2 rounded-3 shadow-sm" style="max-width: 75%;">
                                ${ data.file_content ? `<div class="mb-2">
                                    <img src="${data.file_content}" alt="Message Image" class="img-fluid" style="max-width: 500px; max-height: 500px; object-fit: contain;">
                                </div>` : ''}
                                <p class="mb-0" id='message-${data.id}'>${formattedContent}</p>
                                <div class="d-flex align-items-center justify-content-end mb-2">
                                    <small class="text-muted">${formattedDate}</small>
                                    ${data.read ? `<i class="bi bi-check-all ms-2" id="read_${data.id}"></i>` : `<i class="bi bi-check ms-2" id="read_${data.id}"></i>`}
                                </div>
                            </div>
                            <img src="${avatarUrl}" alt="User Avatar" class="rounded-circle me-2" style="width: 40px; height: 40px; object-fit: cover;">
                        </div>
                    `;
                } else {
                    messageElement = `
                        <div class="d-flex align-items-start">
                            <img src="${data.sender_profile_pic}" alt="User Avatar" class="rounded-circle me-2" style="width: 40px; height: 40px; object-fit: cover;">
                            <div style="background-color: rgb(220, 220, 220)" class="text-dark p-2 rounded-3 shadow-sm" style="max-width: 75%;">
                                <p class="mb-1 fw-bold">${data.sender_name}</p>
                                ${data.file_content ? `<div class="mb-2">
                                    <img src="${data.file_content}" alt="Message Image" class="img-fluid" style="max-width: 500px; max-height: 500px; object-fit: contain;">
                                </div>` : ''}
                                <p class="mb-0" id='message-${data.id}'>${formattedContent}</p>
                                <div class="d-flex align-items-center justify-content-end mb-2">
                                    <small class="text-muted">${formattedDate}</small>
                                    ${data.read ? `<i class="bi bi-check-all ms-2" id="read_${data.id}"></i>` : `<i class="bi bi-check ms-2" id="read_${data.id}"></i>`}
                                </div>
                            </div>
                            <div class="position-relative d-inline-block mt-auto">
                                ${data.user_liked
                                    ? `<i class="bi bi-heart-fill fs-5" style="color:red" id="icon_like_${data.id}"></i>`
                                    : `<i class="bi bi-heart fs-5" style="color:red" id="icon_like_${data.id}" onclick="liked(${data.id})"></i>`}
                                <span id = "likes_count_${data.id}" class="position-absolute top-50 start-50 translate-middle text-black fw-bold" onclick="liked(${data.id})">${data.liked > 0 ? data.liked : ''}</span>
                            </div>
                            <i class="bi bi-arrow-return-left" data-message-id="${data.id}" onclick="replyToMessage('message-${data.id}')" aria-hidden="true"></i>
                            ${truncatedText ? `<a href="javascript:void(0)" onclick="findMessageThatWasReplied(${data.replied_to_id})"><div class="bg-light text-muted p-1 rounded">
                                <small>Replied to: ${truncatedText}</small>
                            </div></a>` : ''}
                        </div>`;
                }

                chatLog.innerHTML += messageElement;

                const chat_id = document.getElementById('chatId').getAttribute('name')

                if (!isOwnMessage) {
                    const newMessage = document.getElementById(`message-${data.id}`);
                    const observer = new IntersectionObserver((entries, observer) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                const messageId = entry.target.id.split('-')[1];
                                markMessageAsRead(messageId, chat_id);
                                observer.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.5 });
                    observer.observe(newMessage);
                }

                const chatScroll = document.getElementById('chat-scroll');
                chatScroll.scrollTop = chatScroll.scrollHeight;
                makeLastMessage(data.id, chat_id)

                document.getElementById('reply-message').style.display = 'none';
                removeImage('close')

            } else if (data['event'] === 'message_read' && exists) {
                const messageId = data.id;
                const icon = document.getElementById(`read_${messageId}`);

                if (data.read && icon) {
                    icon.classList.remove('bi-check');
                    icon.classList.add('bi-check-all');
                }
            } else if (data['event'] === 'last_message') {
                const lastMessage = document.getElementById(`last_message_${data.chat_id}`)
                truncatedText = truncateText(data.msg_content, 25);
                lastMessage.innerHTML = truncatedText;
                lastMessage.value = truncatedText;
            }
        }
    }

    function loadMessages(chatId, user) {
        fetch(`/get/messages/${chatId}/`)
            .then(response => response.json())
            .then(data => {
                const chatLog = document.getElementById('chat-log');
                chatLog.innerHTML = '';

                if (data.messages.length === 0) {
                    chatLog.innerHTML = '<p id="noMessages" class="text-muted">No messages yet.</p>';
                } else {
                    data.messages.forEach(msg => {
                        const isOwnMessage = msg.sender_id === Number(user);
                        let messageElement;

                        let formattedContent = '';
                        if (msg.content) {
                            formattedContent = formatContent(msg.content);

                            const links = extractLinks(formattedContent);
                            formattedContent = links.length > 0
                                ? `<a href="${links[0]}">${formattedContent}</a>`
                                : formattedContent;
                        }

                        const date = msg.sent_at;
                        const formattedDate = formatDate(date);

                        let truncatedText;
        
                        if (msg.replied_to_content) {
                            truncatedText = truncateText(msg.replied_to_content, 15);
                        }

                        if (isOwnMessage) {
                            messageElement = `
                                <div class="d-flex align-items-start justify-content-end mb-2">
                                    ${truncatedText ? `<a href="javascript:void(0)" onclick="findMessageThatWasReplied(${msg.replied_to_id})"><div class="text-muted p-1 rounded">
                                        <small>Replied to: ${truncatedText}</small>
                                    </div></a>` : ''}
                                    <i class="bi bi-arrow-return-right" data-message-id="${msg.id}" onclick="replyToMessage('message-${msg.id}')" aria-hidden="true"></i>
                                    <div class="position-relative d-inline-block mt-auto">
                                        ${msg.user_liked
                                            ? `<i class="bi bi-heart-fill fs-5" style="color:red" id="icon_like_${msg.id}"></i>`
                                            : `<i class="bi bi-heart fs-5" style="color:red" id="icon_like_${msg.id}" onclick="liked(${msg.id})"></i>`}
                                        <span id = "likes_count_${msg.id}" class="position-absolute top-50 start-50 translate-middle text-black fw-bold" onclick="liked(${msg.id})">${msg.liked > 0 ? msg.liked : ''}</span>
                                    </div>

                                    <div style="background-color: rgb(240, 240, 240)" class="text-dark p-2 rounded-3 shadow-sm" style="max-width: 75%;">
                                        ${msg.file_content ? `<div class="mb-2">
                                            <img src="${msg.file_content}" alt="Message Image" class="img-fluid" style="max-width: 500px; max-height: 500px; object-fit: contain;">
                                        </div>` : ''}
                                        <p class="mb-0" id="message-${msg.id}">${formattedContent}</p>
                                        <div class="d-flex align-items-center justify-content-end mb-2">
                                            <small class="text-muted">${formattedDate}</small>
                                            ${msg.read ? `<i class="bi bi-check-all ms-2" id="read_${msg.id}"></i>` : `<i class="bi bi-check ms-2" id="read_${msg.id}"></i>`}
                                        </div>
                                    </div>
                                    <img src="${avatarUrl}" alt="User Avatar"
                                    class="rounded-circle me-2" style="width: 40px; height: 40px; object-fit: cover;">
                                </div>`;
                        } else {
                            messageElement = `
                                <div class="d-flex align-items-start mb-2">
                                    <img src="${msg.sender_profile_pic}" alt="User Avatar" class="rounded-circle me-2" style="width: 40px; height: 40px; object-fit: cover;">
                                    <div style="background-color: rgb(220, 220, 220)" class="text-dark p-2 rounded-3 shadow-sm" style="max-width: 75%;">
                                        <p class="mb-1 fw-bold">${msg.sender_name}</p>
                                        ${msg.file_content ? `<div class="mb-2">
                                            <img src="${msg.file_content}" alt="Message Image" class="img-fluid" style="max-width: 500px; max-height: 500px; object-fit: contain;">
                                        </div>` : ''}
                                        <p class="mb-0" id="message-${msg.id}">${formattedContent}</p>
                                        <div class="d-flex align-items-center justify-content-end mb-2">
                                            <small class="text-muted">${formattedDate}</small>
                                            ${msg.read ? `<i class="bi bi-check-all ms-2" id="read_${msg.id}"></i>` : `<i class="bi bi-check ms-2" id="read_${msg.id}"></i>`}
                                        </div>
                                    </div>
                                    <div class="position-relative d-inline-block mt-auto">
                                        ${msg.user_liked
                                            ? `<i class="bi bi-heart-fill fs-5" style="color:red" id="icon_like_${msg.id}"></i>`
                                            : `<i class="bi bi-heart fs-5" style="color:red" id="icon_like_${msg.id}" onclick="liked(${msg.id})"></i>`}
                                        <span id = "likes_count_${msg.id}" class="position-absolute top-50 start-50 translate-middle text-black fw-bold" onclick="liked(${msg.id})">${msg.liked > 0 ? msg.liked : ''}</span>
                                    </div>

                                    <i class="bi bi-arrow-return-left" data-message-id="${msg.id}" onclick="replyToMessage('message-${msg.id}')" aria-hidden="true"></i>
                                    ${truncatedText ? `<a href="javascript:void(0)" onclick="findMessageThatWasReplied(${msg.replied_to_id})"><div class="bg-light text-muted p-1 rounded">
                                        <small>Replied to: ${truncatedText}</small>
                                    </div></a>` : ''}
                                </div>`;
                        }

                        chatLog.innerHTML += messageElement;

                        if (!isOwnMessage) {
                            const newMessage = document.getElementById(`message-${msg.id}`);
                            const observer = new IntersectionObserver((entries, observer) => {
                                entries.forEach(entry => {
                                    if (entry.isIntersecting) {
                                        const messageId = entry.target.id.split('-')[1];
                                        markMessageAsRead(messageId, chatId);
                                        observer.unobserve(entry.target);
                                    }
                                });
                            }, { threshold: 0.5 });
                            observer.observe(newMessage);
                        }
                    });

                    const chatScroll = document.getElementById('chat-scroll');
                    chatScroll.scrollTop = chatScroll.scrollHeight;
                }
            })
            .catch(error => console.error('Error loading messages:', error));
    }

    function initializeMessageForm() {
        const form = document.getElementById('message-form');
        const input = document.querySelector('#chat-message-input');
        const chat_id = document.getElementById('chatId').getAttribute('name')

        if (form) {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                sendMessage(input, chat_id);
            });

            input.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    sendMessage(input, chat_id);
                }
            });
        }

        function sendMessage(input, chatId) {
            const message = input.value.trim();
            var messageId = document.querySelector('#reply-message a').getAttribute('data-message-id');
            const file_content = document.getElementById('preview-img').getAttribute('src')

            if (messageId) {
                messageId = messageId.replace(/\D/g, '')
            }

            if (socket && (message || file_content)) {
                socket.send(JSON.stringify({
                    'event': 'send_message',
                    message: message,
                    replied_to_id: messageId,
                    file_content:file_content,
                    chat_id:chatId,
                }));
                input.value = '';
            }
        }
    }
});