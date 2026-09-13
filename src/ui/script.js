let progressCardId = 0;
let currentProgressId = null;

// Ensure API is ready
window.addEventListener('pywebviewready', function() {
    console.log("PyWebView API is ready");
    
    // Attach event listeners
    document.getElementById('addBtn').addEventListener('click', async () => {
        const urls = document.getElementById('urlInput').value.trim();
        if(!urls) return;
        
        const quality = document.getElementById('qualitySelect').value;
        const mode = document.getElementById('modeSelect').value;
        const isPlaylist = mode === 'playlist';
        
        // Add placeholder card for UI feedback
        createProgressCard("Downloading...", urls.split('\n').length + " items");
        document.getElementById('urlInput').value = '';
        
        // Call Python
        await window.pywebview.api.add_to_queue(urls, quality, isPlaylist);
    });

    document.getElementById('folderBtn').addEventListener('click', async () => {
        const result = await window.pywebview.api.select_folder();
        if(result) {
            document.getElementById('folderBtn').innerText = "📂 " + result;
        }
    });

    document.getElementById('stopBtn').addEventListener('click', async () => {
        await window.pywebview.api.stop_download();
        document.getElementById('queueList').innerHTML = ''; // clear visual queue
    });
    
    document.querySelector('.paste-btn').addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            document.getElementById('urlInput').value += text;
        } catch(e) {
            console.log("Paste failed");
        }
    });
});

// Exposed functions for Python to call
window.updateQueueStatus = function(qsize) {
    document.getElementById('queueCount').innerText = qsize;
    const stopBtn = document.getElementById('stopBtn');
    if(qsize > 0) {
        stopBtn.style.display = 'block';
    } else {
        stopBtn.style.display = 'none';
        if(currentProgressId) {
            // Mark the last card as completed
            const card = document.getElementById(currentProgressId);
            if(card) {
                card.querySelector('.card-status').innerText = "Completed";
                card.querySelector('.progress-text').innerText = "100%";
                setRingProgress(card.querySelector('.progress-ring-bar'), 100);
            }
            currentProgressId = null;
        }
    }
};

window.updateProgress = function(percent) {
    if(currentProgressId) {
        const card = document.getElementById(currentProgressId);
        if(card) {
            card.querySelector('.progress-text').innerText = Math.floor(percent) + "%";
            setRingProgress(card.querySelector('.progress-ring-bar'), percent);
        }
    }
};

window.logMessage = function(msg) {
    if(msg.includes(">>> Starting Download:")) {
        const title = msg.replace(">>> Starting Download:", "").trim();
        createProgressCard(title, "Downloading");
    }
};

function createProgressCard(title, subtitle) {
    progressCardId++;
    const id = 'card-' + progressCardId;
    currentProgressId = id;
    
    const cardHTML = `
        <div id="${id}" class="queue-card glass">
            <div class="card-info">
                <div class="card-title">${title}</div>
                <div class="card-status">${subtitle}</div>
            </div>
            <div class="progress-ring">
                <svg>
                    <circle class="progress-ring-circle" cx="30" cy="30" r="28"></circle>
                    <circle class="progress-ring-bar" cx="30" cy="30" r="28"></circle>
                </svg>
                <div class="progress-text">0%</div>
            </div>
        </div>
    `;
    
    const queueList = document.getElementById('queueList');
    queueList.insertAdjacentHTML('afterbegin', cardHTML);
}

function setRingProgress(element, percent) {
    const circumference = 176; // 2 * pi * 28
    const offset = circumference - (percent / 100) * circumference;
    element.style.strokeDashoffset = offset;
}
