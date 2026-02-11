async function uploadFile(input) {
    const formData = new FormData();
    formData.append('file', input.files[0]);
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.status === 'success') alert('Indexed: ' + data.filename);
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msgDiv = document.getElementById('messages');
    const userMsg = input.value;
    input.value = '';

    msgDiv.innerHTML += `<div><b>You:</b> ${userMsg}</div>`;

    const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
    });
    const data = await res.json();

    let imgHtml = '<div class="image-grid">';
    data.images.forEach(img => imgHtml += `<img src="${img.url}" title="${img.title}">`);
    imgHtml += '</div>';

    msgDiv.innerHTML += `<div><b>Lumina:</b> ${data.answer} ${imgHtml}</div>`;
}