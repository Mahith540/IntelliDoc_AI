const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const bottomFlow = document.getElementById('bottom-flow');
const flowStatusText = document.getElementById('flow-status-text');
const flowPercent = document.getElementById('flow-percent');
const flowBar = document.getElementById('flow-bar');
const loadingOverlay = document.getElementById('loading-overlay');
const sendBtn = document.getElementById('send-btn');
const tracePanel = document.getElementById('trace-panel');
const traceContent = document.getElementById('trace-content');
const closeTrace = document.getElementById('close-trace');

// --- CINEMATIC CHAT LOGIC ---

function appendMessage(role, text, sources = [], context = null) {
    if (chatContainer.querySelector('.zoom-in')) {
        chatContainer.innerHTML = '';
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `flex flex-col ${role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-5 duration-700`;
    
    const bgClass = role === 'user' ? 'bg-indigo-600/10 border-indigo-500/20 text-white' : 'bg-slate-900/80 border-white/5 text-slate-200';
    const alignClass = role === 'user' ? 'rounded-l-3xl rounded-tr-3xl' : 'rounded-r-3xl rounded-tl-3xl';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="mt-6 pt-4 border-t border-white/5">
                <p class="text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3">Intelligence Sources</p>
                <div class="flex flex-wrap gap-2">
                    ${sources.map(s => `<span class="bg-indigo-500/5 text-[9px] text-indigo-400 px-3 py-1 rounded-full border border-indigo-500/10 font-mono">${s.split('/').pop()}</span>`).join('')}
                </div>
            </div>
        `;
    }

    let actionHtml = '';
    if (context) {
        actionHtml = `
            <button class="mt-4 text-[9px] text-indigo-400 hover:text-indigo-300 font-bold uppercase tracking-[0.2em] flex items-center transition-all group view-context-btn">
                <span class="w-4 h-[1px] bg-indigo-500/30 mr-2 group-hover:w-8 transition-all"></span>
                Analyze Context
            </button>
        `;
    }

    msgDiv.innerHTML = `
        <div class="max-w-[85%] md:max-w-[70%] ${bgClass} ${alignClass} border p-6 md:p-8 shadow-2xl backdrop-blur-md">
            <div class="text-sm md:text-base leading-relaxed space-y-4 prose prose-invert max-w-none">
                ${text.replace(/\n/g, '<br>')}
            </div>
            ${sourcesHtml}
            ${actionHtml}
        </div>
        <div class="mt-2 px-2 text-[9px] font-bold text-slate-600 uppercase tracking-widest">
            ${role === 'user' ? 'Operator' : 'IntelliDoc'}
        </div>
    `;
    
    if (context) {
        msgDiv.querySelector('.view-context-btn').addEventListener('click', () => {
            traceContent.textContent = context;
            tracePanel.classList.remove('hidden');
        });
    }

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
}

closeTrace.addEventListener('click', () => tracePanel.classList.add('hidden'));

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    appendMessage('user', question);
    userInput.value = '';
    
    loadingOverlay.classList.remove('hidden');
    sendBtn.disabled = true;

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            appendMessage('bot', data.answer, data.sources, data.context);
        } else {
            appendMessage('bot', `⚠️ **ERROR**: ${data.detail || 'Connection disrupted.'}`);
        }
    } catch (err) {
        appendMessage('bot', `⚠️ **FAILURE**: ${err.message}`);
    } finally {
        loadingOverlay.classList.add('hidden');
        sendBtn.disabled = false;
    }
});

// --- BOTTOM FLOW UPLOAD LOGIC ---

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-indigo-500', 'bg-indigo-500/5');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-500/5');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-500/5');
    const files = e.dataTransfer.files;
    if (files.length) handleUpload(files[0]);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleUpload(fileInput.files[0]);
});

async function handleUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show Bottom Flow Indicator
    bottomFlow.classList.remove('hidden');
    updateFlow('Reading Document...', 10);
    
    const stepDots = [document.getElementById('step-0-dot'), document.getElementById('step-1-dot')];
    stepDots[0].classList.replace('bg-slate-600', 'bg-indigo-500');
    stepDots[0].classList.add('animate-pulse');

    try {
        // Simple progress simulation for the UX while the bulk POST runs
        let simProgress = 10;
        const interval = setInterval(() => {
            if (simProgress < 90) {
                simProgress += Math.random() * 2;
                updateFlow(simProgress > 50 ? 'Building Intelligence...' : 'Reading Document...', simProgress);
                if (simProgress > 50) {
                    stepDots[0].classList.remove('animate-pulse');
                    stepDots[1].classList.replace('bg-slate-600', 'bg-indigo-500');
                    stepDots[1].classList.add('animate-pulse');
                }
            }
        }, 300);

        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        clearInterval(interval);

        if (response.ok) {
            updateFlow('Knowledge Acquired!', 100);
            stepDots.forEach(d => { d.classList.remove('animate-pulse'); d.classList.replace('bg-slate-600', 'bg-indigo-500'); });
            
            setTimeout(() => {
                bottomFlow.classList.add('hidden');
                // Reset dots
                stepDots.forEach(d => { d.classList.replace('bg-indigo-500', 'bg-slate-600'); });
                
                const stats = data.stats;
                appendMessage('bot', `✅ **SMART INGESTION COMPLETE**: ${file.name}
                <br><br>
                Integrated **${stats.num_chunks} information segments**. The hub is now updated.
                <br><br>
                *Content Preview:*<br>
                <span class="text-xs text-indigo-300 font-mono bg-indigo-500/5 p-2 block rounded border border-indigo-500/10">${stats.preview}...</span>`);
            }, 1000);
        } else {
            bottomFlow.classList.add('hidden');
            appendMessage('bot', `⚠️ **INGESTION FAILED**: ${data.detail || 'Data rejected.'}`);
        }
    } catch (err) {
        bottomFlow.classList.add('hidden');
        appendMessage('bot', `⚠️ **CONNECTION ERROR**: ${err.message}`);
    }
}

function updateFlow(text, percent) {
    flowStatusText.textContent = text;
    const p = Math.round(percent);
    flowPercent.textContent = `${p}%`;
    flowBar.style.width = `${p}%`;
}
