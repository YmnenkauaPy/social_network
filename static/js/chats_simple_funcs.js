function extractLinks(value) {
    const sanitizedValue = value.replace(/<br>/gi, '');
    const urlRegex = /https?:\/\/[^\s/$.?#].[^\s]*/gi;
    return sanitizedValue.match(urlRegex) || [];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();

    const isToday = date.toDateString() === now.toDateString();
    const isYesterday = new Date(now - 24 * 60 * 60 * 1000).toDateString() === date.toDateString();

    const optionsTime = { hour: '2-digit', minute: '2-digit' }; // Формат времени (например, 14:30)
    const optionsDate = { month: 'long', day: 'numeric', year: 'numeric' }; // Формат полной даты

    if (isToday) {
        return `Today, ${date.toLocaleTimeString([], optionsTime)}`;
    } else if (isYesterday) {
        return `Yesterday, ${date.toLocaleTimeString([], optionsTime)}`;
    } else {
        return `${date.toLocaleDateString('en-US', optionsDate)}, ${date.toLocaleTimeString([], optionsTime)}`;
    }
}

// Function for truncating text
function truncateText(text, maxLength) {
    if (text.length > maxLength) {
        return text.slice(0, maxLength) + '...';
    }
    return text;
}

const lastMessages = document.querySelectorAll('[id^="last_message_"]');

lastMessages.forEach((messageElement) => {
    const content = messageElement.getAttribute('content-value');
    const file = messageElement.getAttribute('file-content-value');

    if (/\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file)) {
        messageElement.innerHTML = `<b>photo</b>`
    } else if (content) {
        const truncatedText = truncateText(content, 25);
        messageElement.innerHTML = truncatedText;
    } else if (!content && !file) {
        messageElement.innerHTML = '<b>No messages</b>';
    }
});

function previewImage(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append("image", file);

        fetch('/upload_image/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.imageUrl) {
                // Используйте imageUrl без изменений
                previewImg.src = data.imageUrl;
            } else {
                console.error("Image upload failed");
            }
        })
        .catch(error => {
            console.error("Error uploading image:", error);
        });
    }
}


function removeImage(event) {
    console.log(event)
    const preview = document.getElementById('image-preview');
    const fileInput = document.getElementById('file-upload');
    const previewImg = document.getElementById('preview-img');

    // Извлекаем путь без /media/
    const relativePath = previewImg.src.split('/media/')[1];

    if (event == 'delete') {
        function deleteImage(ImagePath) {
            fetch(`/delete_image/${ImagePath}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'File deleted') {
                    console.log('Image deleted');
                } else {
                    console.error('Error deleting file:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }

        deleteImage(relativePath)
    }

    preview.style.display = 'none';
    fileInput.value = '';
    previewImg.src = '';
}

function replyToMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    const messageContent = messageElement ? messageElement.innerText : 'Message content not found';

    const replyContent = document.getElementById('reply-content');

    const truncatedText = truncateText(messageContent, 25);

    replyContent.innerText = truncatedText;

    const replyLink = document.querySelector('#reply-message a');
    replyLink.setAttribute('data-message-id', messageId);

    document.getElementById('reply-message').style.display = 'block';
}

function findMessageThatWasReplied(id=null) {
    let messageElement
    if (id === null) {
        const messageId = document.querySelector('#reply-message a').getAttribute('data-message-id');
        messageElement = document.getElementById(messageId);
    } else {
        messageElement = document.getElementById(`message-${id}`);
    }

    if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth' });

        const markElement = document.createElement('mark');
        markElement.innerHTML = messageElement.innerHTML;
        messageElement.innerHTML = '';
        messageElement.appendChild(markElement);


        setTimeout(() => {
            messageElement.innerHTML = markElement.innerHTML;
        }, 1000);
    } else {
        console.log('Message not found');
    }
}

function cancelReply() {
    const replyContainer = document.getElementById("reply-message");
    replyContainer.style.display = "none";
}

function liked(id) {
    fetch(`/liked/message/${id}/`)
        .then(response => response.json())
        .then(data => {
            const icon = document.getElementById(`icon_like_${id}`)

            if (data.user_liked) {
                icon.classList.remove('bi-heart')
                icon.classList.add('bi-heart-fill')

            } else {
                icon.classList.remove('bi-heart-fill')
                icon.classList.add('bi-heart')
            }
            if (data.liked > 0) {
                document.getElementById(`likes_count_${id}`).innerHTML = data.liked
            } else {
                document.getElementById(`likes_count_${id}`).innerHTML = ''
            }
        })
        .catch(error => {
            console.error('Error loading like:', error);
        });
}

