const API_BASE = "https://hj96k-studygenie-backend.hf.space";
let currentLectureId = null;

// UI Elements
const sections = {
    upload: document.getElementById('upload-section'),
    results: document.getElementById('results-section')
};

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setup3DEffects();
});

// State management
function showSection(name) {
    Object.values(sections).forEach(s => s.classList.add('hidden'));
    sections[name].classList.remove('hidden');

    // Clear results if going to upload
    if (name === 'upload') {
        currentLectureId = null;
        document.getElementById('video-url').value = '';
        document.getElementById('file-name').innerText = 'Drag & Drop Lecture Video';
    }
}

// 3D Card Hover Logic
function setup3DEffects() {
    const cards = document.querySelectorAll('.card-3d-effect, .card-3d');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)`;
        });
    });
}

// File Name Display
document.getElementById('video-file').addEventListener('change', (e) => {
    const name = e.target.files[0]?.name || "Drag & Drop Lecture Video";
    document.getElementById('file-name').innerText = name;
});

// Process Video
document.getElementById('process-btn').addEventListener('click', async () => {
    const urlInput = document.getElementById('video-url').value;
    const fileInput = document.getElementById('video-file').files[0];

    if (!urlInput && !fileInput) {
        alert("Please provide a video link or upload a file.");
        return;
    }

    const formData = new FormData();
    if (fileInput) formData.append('file', fileInput);
    if (urlInput) formData.append('url', urlInput);

    // Show Loading
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('process-btn').disabled = true;

    try {
        const response = await fetch(`${API_BASE}/process-video/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Processing failed");

        const data = await response.json();
        displayResults(data);
        showSection('results');
        loadHistory(); // Refresh sidebar
    } catch (err) {
        alert(err.message);
    } finally {
        document.getElementById('loader').classList.add('hidden');
        document.getElementById('process-btn').disabled = false;
    }
});

function displayResults(data) {
    currentLectureId = data.id;

    // Notes
    document.getElementById('lecture-notes').innerText = data.summary;

    // Quiz
    const quizHtml = `
        <div class='quiz-block'>
            <h3 style="color: var(--primary); margin-bottom: 10px;">Multiple Choice</h3>
            <pre style="white-space: pre-wrap; font-size: 0.9rem;">${data.quiz.mcqs}</pre>
            <h3 style='margin-top:20px; color: var(--primary); margin-bottom: 10px;'>Short Answer</h3>
            <pre style="white-space: pre-wrap; font-size: 0.9rem;">${data.quiz.short_answers}</pre>
        </div>
    `;
    document.getElementById('quiz-content').innerHTML = quizHtml;

    // Flashcards
    const flashHtml = data.flashcards.split('\n').filter(c => c.trim()).map(card => `
        <div class="flashcard glass">
            <p>${card}</p>
        </div>
    `).join('');
    document.getElementById('flashcards-content').innerHTML = flashHtml;
}

// Chat Implementation
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-query').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const input = document.getElementById('chat-query');
    const query = input.value;
    if (!query || !currentLectureId) return;

    // Add User Message
    addMessage(query, 'user');
    input.value = '';

    const formData = new FormData();
    formData.append('lecture_id', currentLectureId);
    formData.append('message', query);

    try {
        const response = await fetch(`${API_BASE}/chat/`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        addMessage(data.response, 'buddy');
    } catch (err) {
        addMessage("Neural link interrupted. Please try again.", 'buddy');
    }
}

function addMessage(text, type) {
    const chatBox = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// History Implementation
async function loadHistory() {
    const historyList = document.getElementById('history-list');

    try {
        const response = await fetch(`${API_BASE}/lectures/`);
        const lectures = await response.json();

        if (lectures.length === 0) {
            historyList.innerHTML = "<p style='color: var(--text-dim); text-align: center; font-size: 0.8rem;'>No sessions yet.</p>";
            return;
        }

        historyList.innerHTML = lectures.reverse().map(l => `
            <div class="history-item" onclick="viewLecture(${l.id})" title="${l.title}">
                ${l.title}
            </div>
        `).join('');
    } catch (err) {
        console.error("Failed to load history");
    }
}

async function viewLecture(id) {
    try {
        const response = await fetch(`${API_BASE}/lecture/${id}`);
        const data = await response.json();
        // Since we didn't save quiz/flashcards in specific table columns but used logic 
        // to generate them on the fly, for history we'll just show notes 
        displayResults({
            id: data.id,
            summary: data.summary,
            quiz: { mcqs: "Retrieved from neural vault...", short_answers: "Retrieved from neural vault..." },
            flashcards: "Synchronizing..."
        });
        showSection('results');
    } catch (err) {
        alert("Failed to load session details.");
    }
}

// Custom Task Execution
document.getElementById('execute-task-btn')?.addEventListener('click', async () => {
    const taskInput = document.getElementById('custom-task');
    const task = taskInput.value;
    if (!task || !currentLectureId) return;

    addMessage(`Command: ${task}`, 'user');
    taskInput.value = '';

    await handleAIRequest(task);
});

async function triggerTask(type) {
    if (!currentLectureId) {
        alert("Please process a lecture first.");
        return;
    }

    let prompt = "";
    switch (type) {
        case 'quiz': prompt = "Generate a new set of 5 questions (3 MCQs, 2 Short) from this lecture."; break;
        case 'flashcards': prompt = "Extract 8 key flashcards (Question: Answer) from this content."; break;
        case 'infographic': prompt = "Create a structured breakdown of the core concepts in this lecture for an infographic style visualization."; break;
        case 'summary': prompt = "Re-summarize this lecture focusing only on the most exam-critical points."; break;
    }

    addMessage(`Action: ${prompt}`, 'user');
    await handleAIRequest(prompt);
}

async function handleAIRequest(message) {
    const formData = new FormData();
    formData.append('lecture_id', currentLectureId);
    formData.append('message', message);

    try {
        const response = await fetch(`${API_BASE}/chat/`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        addMessage(data.response, 'buddy');
    } catch (err) {
        addMessage("Neural link failure. Reconstruction impossible.", 'buddy');
    }
}
