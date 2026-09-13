let progressCardId = 0;
let currentProgressId = null;
let lastQuality = "1080p";
let lastIsPlaylist = false;

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
        lastQuality = quality;
        lastIsPlaylist = isPlaylist;
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
        const url = msg.replace(">>> Starting Download:", "").trim();
        createProgressCard(url, "Downloading", url);
    }
};

function createProgressCard(title, subtitle, url = "") {
    progressCardId++;
    const id = 'card-' + progressCardId;
    currentProgressId = id;
    
    // Shorten title if it's a URL
    let displayTitle = title;
    if(title.startsWith("http")) {
        displayTitle = title.length > 50 ? title.substring(0, 47) + "..." : title;
    }
    
    const cardHTML = `
        <div id="${id}" class="queue-card glass" data-url="${url}">
            <div class="card-info">
                <div class="card-title" title="${title}">${displayTitle}</div>
                <div class="card-status">${subtitle}</div>
                <div class="card-actions" style="margin-top: 8px; display: flex; gap: 10px;">
                    <button class="btn glass-btn action-btn pause-btn" onclick="pauseDownload('${id}')" style="padding: 5px 10px; font-size: 10px; display: flex; align-items: center; justify-content: center; gap: 4px;"><i data-lucide="pause" style="width: 12px; height: 12px;"></i> PAUSE</button>
                    <button class="btn danger-btn glass-btn action-btn cancel-btn" onclick="cancelDownload('${id}')" style="padding: 5px 10px; font-size: 10px; display: flex; align-items: center; justify-content: center; gap: 4px;"><i data-lucide="x" style="width: 12px; height: 12px;"></i> CANCEL</button>
                </div>
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
    if (window.lucide) {
        lucide.createIcons();
    }
}

window.pauseDownload = async function(id) {
    if(currentProgressId === id) {
        await window.pywebview.api.cancel_current_download();
    }
    
    const card = document.getElementById(id);
    if(card) {
        card.querySelector('.card-status').innerText = "Paused";
        card.querySelector('.card-status').style.color = "#fb923c"; // Orange for paused
        
        const pauseBtn = card.querySelector('.pause-btn');
        pauseBtn.innerHTML = '<i data-lucide="play" style="width: 12px; height: 12px;"></i> RESUME';
        pauseBtn.style.color = "#4ade80";
        pauseBtn.setAttribute('onclick', `resumeDownload('${id}')`);
        if (window.lucide) {
            lucide.createIcons();
        }
    }
};

window.resumeDownload = async function(id) {
    const card = document.getElementById(id);
    if(card) {
        const url = card.getAttribute('data-url');
        card.remove(); // Remove the paused card, a new one will spawn
        if(url) {
            await window.pywebview.api.add_to_queue(url, lastQuality, lastIsPlaylist);
        }
    }
};

window.cancelDownload = async function(id) {
    if(currentProgressId === id) {
        await window.pywebview.api.cancel_current_download();
    }
    
    const card = document.getElementById(id);
    if(card) {
        card.remove();
    }
};

function setRingProgress(element, percent) {
    const circumference = 176; // 2 * pi * 28
    const offset = circumference - (percent / 100) * circumference;
    element.style.strokeDashoffset = offset;
}
