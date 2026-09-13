import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, sendEmailVerification, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIza" + "SyCeatVP72B2UDUS8o0nBp6-7cdFQK_yIxs",
  authDomain: "infinite-9c092-fb879.firebaseapp.com",
  projectId: "infinite-9c092-fb879",
  storageBucket: "infinite-9c092-fb879.firebasestorage.app",
  messagingSenderId: "17006881447",
  appId: "1:17006881447:web:647d8e727e6b82fe558982",
  measurementId: "G-XCDFBEYVER"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

let isAuthComplete = false;
let depsStarted = false;

function checkAuthAndStart() {
    if (isAuthComplete && !depsStarted && window.pywebview && window.pywebview.api) {
        depsStarted = true;
        
        const overlay = document.getElementById("loading-overlay");
        const rocket = document.getElementById("loading-rocket") || overlay.querySelector('.lucide-rocket');
        const loadingText = document.getElementById("loading-text");
        const loadingTitle = overlay.querySelector("h2");
        
        overlay.style.display = "flex";
        overlay.style.opacity = "1";
        
        if (loadingText) loadingText.style.opacity = "0";
        if (loadingTitle) loadingTitle.style.opacity = "0";
        if (rocket) {
            rocket.style.animation = 'none';
            void rocket.offsetWidth; 
            rocket.classList.add('rocket-intro-flight');
            
            setTimeout(() => {
                rocket.classList.remove('rocket-intro-flight');
                rocket.classList.add('rocket-pop-center');
                if (loadingText) loadingText.style.opacity = "1";
                if (loadingTitle) loadingTitle.style.opacity = "1";
                
                setTimeout(() => {
                    rocket.classList.remove('rocket-pop-center');
                    rocket.classList.add('rocket-pulse');
                    window.minLoadingAnimationDone = true;
                    if (window.pendingHideLoading) {
                        window.hideLoadingScreen();
                    }
                }, 500);
            }, 1200);
        }
        
        window.pywebview.api.start_dependencies();
    }
}

onAuthStateChanged(auth, (user) => {
    if (user) {
        if (user.emailVerified) {
            isAuthComplete = true;
            document.getElementById("auth-overlay").style.display = "none";
            checkAuthAndStart();
        } else {
            isAuthComplete = false;
            document.getElementById("auth-overlay").style.display = "flex";
            showAuthError("Please verify your email to access the app.");
            document.getElementById("auth-resend-btn").style.display = "block";
            document.getElementById("loading-overlay").style.display = "none";
        }
    } else {
        isAuthComplete = false;
        document.getElementById("auth-overlay").style.display = "flex";
        document.getElementById("auth-resend-btn").style.display = "none";
        document.getElementById("loading-overlay").style.display = "none";
    }
});

function showAuthError(msg) {
    const err = document.getElementById('auth-error');
    err.innerText = msg;
    err.style.display = 'block';
    document.getElementById('auth-msg').style.display = 'none';
}

function showAuthMsg(msg) {
    const errM = document.getElementById('auth-msg');
    errM.innerText = msg;
    errM.style.display = 'block';
    document.getElementById('auth-error').style.display = 'none';
}

document.getElementById('auth-login-btn').addEventListener('click', async () => {
    const email = document.getElementById('auth-email').value;
    const pass = document.getElementById('auth-pass').value;
    if(!email || !pass) return showAuthError("Please enter email and password");
    
    const btn = document.getElementById('auth-login-btn');
    btn.innerText = "LOGGING IN...";
    try {
        await signInWithEmailAndPassword(auth, email, pass);
    } catch(e) {
        showAuthError(e.message);
    }
    btn.innerText = "LOGIN";
});

document.getElementById('auth-signup-btn').addEventListener('click', async () => {
    const email = document.getElementById('auth-email').value;
    const pass = document.getElementById('auth-pass').value;
    if(!email || !pass) return showAuthError("Please enter email and password");
    
    const btn = document.getElementById('auth-signup-btn');
    btn.innerText = "CREATING...";
    try {
        const cred = await createUserWithEmailAndPassword(auth, email, pass);
        await sendEmailVerification(cred.user);
        showAuthMsg("Account created! Please check your email to verify.");
        document.getElementById('auth-resend-btn').style.display = 'block';
    } catch(e) {
        showAuthError(e.message);
    }
    btn.innerText = "CREATE ACCOUNT";
});

document.getElementById('auth-resend-btn').addEventListener('click', async () => {
    if(auth.currentUser) {
        try {
            await sendEmailVerification(auth.currentUser);
            showAuthMsg("Verification email sent again!");
        } catch(e) {
            showAuthError(e.message);
        }
    }
});

// Create a global function for Python to call if we ever want to force logout
window.logout = async function() {
    await signOut(auth);
};


let progressCardId = 0;
let currentProgressId = null;
let lastQuality = "1080p";
let lastIsPlaylist = false;

// Ensure API is ready
window.addEventListener('pywebviewready', function() {
    checkAuthAndStart();
    console.log("PyWebView API is ready");
    
    // Attach event listeners
    document.getElementById('addBtn').addEventListener('click', () => {
        const urls = document.getElementById('urlInput').value;
        const quality = document.getElementById('qualitySelect').value;
        const isPlaylist = document.getElementById('modeSelect').value === 'playlist';
        if(!urls.trim()) return;
        
        lastQuality = quality;
        lastIsPlaylist = isPlaylist;
        
        const urlList = urls.split('\n');
        for(let url of urlList) {
            if(url.trim()) {
                addPendingToUI(url.trim(), quality, isPlaylist);
            }
        }
        document.getElementById('urlInput').value = '';
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
            markCardCompleted(currentProgressId);
            currentProgressId = null;
        }
    }
};

window.updateProgress = function(percent) {
    if(currentProgressId) {
        const fill = document.getElementById(`dl-fill-${currentProgressId}`);
        const text = document.getElementById(`dl-text-${currentProgressId}`);
        if(fill && text) {
            fill.style.width = percent + "%";
            text.innerText = Math.floor(percent) + "%";
        } else {
            const card = document.getElementById(currentProgressId);
            if(card && card.querySelector('.progress-text')) {
                card.querySelector('.progress-text').innerText = Math.floor(percent) + "%";
                setRingProgress(card.querySelector('.progress-ring-bar'), percent);
            }
        }
    }
};

window.updateLoadingText = function(msg) {
    const text = document.getElementById('loading-text');
    if (text) text.innerText = msg;
};

window.hideLoadingScreen = function() {
    if (!window.minLoadingAnimationDone) {
        window.pendingHideLoading = true;
        return;
    }
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        const rocket = document.getElementById("loading-rocket") || overlay.querySelector('.lucide-rocket');
        if (rocket) {
            rocket.classList.remove('rocket-pulse');
            rocket.style.animation = 'none'; // stop pulse
            void rocket.offsetWidth; 
            rocket.classList.add('rocket-takeoff');
        }
        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.style.display = 'none', 500);
        }, 800);
    }
};

window.logMessage = function(msg) {
    if(msg.includes(">>> Starting Download:")) {
        const url = msg.replace(">>> Starting Download:", "").trim();
        let found = false;
        const cards = document.querySelectorAll('.queue-card');
        for(let card of cards) {
            if(card.getAttribute('data-url') === url) {
                currentProgressId = card.id;
                found = true;
                const btn = document.getElementById(`dl-btn-${card.id}`);
                if(btn && !btn.classList.contains('downloading')) {
                    btn.classList.add('downloading');
                    btn.onclick = null;
                    document.getElementById(`dl-text-${card.id}`).innerText = "0%";
                }
                break;
            }
        }
        if(!found) {
            createProgressCard(url, "Downloading", url);
        }
    }
    
    const overlay = document.getElementById('loading-overlay');
    if (overlay && overlay.style.display !== 'none') {
        updateLoadingText(msg);
    }
};

// Polling loop to fetch state from Python backend
setInterval(async () => {
    if (window.pywebview && window.pywebview.api) {
        try {
            const state = await window.pywebview.api.get_state();
            if (state) {
                if (state.logs && state.logs.length > 0) {
                    for (const msg of state.logs) {
                        logMessage(msg);
                    }
                }
                
                if (state.qsize !== -1) {
                    updateQueueStatus(state.qsize);
                }
                
                if (state.progress !== -1) {
                    updateProgress(state.progress);
                }
                
                if (state.hide_loading) {
                    hideLoadingScreen();
                }
            }
        } catch (e) {
            console.error("Poller error:", e);
        }
    }
}, 200);

function createProgressCard(title, subtitle, url = "") {
    if(currentProgressId) {
        markCardCompleted(currentProgressId);
    }
    
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

function addPendingToUI(url, quality, isPlaylist) {
    progressCardId++;
    const id = 'pending-' + progressCardId;
    
    let displayTitle = url.length > 50 ? url.substring(0, 47) + "..." : url;
    
    const html = `
        <div id="${id}" class="queue-card glass" data-url="${url}" data-quality="${quality}" data-playlist="${isPlaylist}" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; padding: 15px;">
            <div class="card-title" title="${url}" style="margin-bottom: 0;">${displayTitle}</div>
            
            <div style="display: flex; gap: 10px; align-items: center;">
                <button id="dl-btn-${id}" class="dl-anim-btn" onclick="startAnimDownload('${id}')">
                    <div class="dl-progress-fill" id="dl-fill-${id}"></div>
                    <div class="dl-content">
                        <span id="dl-text-${id}">Download</span>
                        <span id="dl-icon-${id}"><i data-lucide="arrow-right"></i></span>
                    </div>
                </button>
                <button class="btn danger-btn glass-btn" onclick="removePending('${id}')" style="padding: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px;"><i data-lucide="trash-2" style="width: 16px; height: 16px;"></i></button>
            </div>
        </div>
    `;
    
    document.getElementById('queueList').insertAdjacentHTML('beforeend', html);
    if (window.lucide) {
        lucide.createIcons();
    }
}

window.startAnimDownload = async function(id) {
    const card = document.getElementById(id);
    if(!card) return;
    
    const url = card.getAttribute('data-url');
    const quality = card.getAttribute('data-quality');
    const isPlaylist = card.getAttribute('data-playlist') === 'true';
    
    const btn = document.getElementById(`dl-btn-${id}`);
    if(btn) {
        btn.classList.add('downloading');
        btn.onclick = null;
        document.getElementById(`dl-text-${id}`).innerText = "0%";
    }
    
    currentProgressId = id;
    await window.pywebview.api.add_to_queue(url, quality, isPlaylist);
};

window.removePending = function(id) {
    const card = document.getElementById(id);
    if(card) card.remove();
};

function markCardCompleted(id) {
    const btn = document.getElementById(`dl-btn-${id}`);
    if(btn) {
        btn.classList.remove('downloading');
        btn.classList.add('done');
        const fill = document.getElementById(`dl-fill-${id}`);
        if(fill) fill.style.width = "100%";
        document.getElementById(`dl-text-${id}`).innerText = "Done";
        document.getElementById(`dl-icon-${id}`).innerHTML = '<i data-lucide="check"></i>';
        
        // Add open folder button next to trash
        const actionsDiv = btn.parentElement;
        if(actionsDiv && !actionsDiv.querySelector('.open-btn')) {
            const openBtn = document.createElement('button');
            openBtn.className = 'btn glass-btn open-btn';
            openBtn.style = 'padding: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px;';
            openBtn.innerHTML = '<i data-lucide="folder-open" style="width: 16px; height: 16px;"></i>';
            openBtn.onclick = window.openSaveFolder;
            actionsDiv.insertBefore(openBtn, btn.nextSibling);
        }
        
        if (window.lucide) {
            lucide.createIcons();
        }
    } else {
        const card = document.getElementById(id);
        if(card && card.querySelector('.card-status')) {
            card.querySelector('.card-status').innerText = "Completed";
            card.querySelector('.card-status').style.color = "#4ade80";
            card.querySelector('.progress-text').innerText = "100%";
            setRingProgress(card.querySelector('.progress-ring-bar'), 100);
            
            const actions = card.querySelector('.card-actions');
            if (actions) {
                actions.innerHTML = `<button class="btn glass-btn action-btn" onclick="openSaveFolder()" style="padding: 5px 10px; font-size: 10px; display: flex; align-items: center; justify-content: center; gap: 4px;"><i data-lucide="folder-open" style="width: 12px; height: 12px;"></i> OPEN FOLDER</button>`;
            }
            if (window.lucide) {
                lucide.createIcons();
            }
        }
    }
}

window.openSaveFolder = async function() {
    await window.pywebview.api.open_save_folder();
};


