document.getElementById('scanBtn').addEventListener('click', () => {
    document.getElementById('scanBtn').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.scripting.executeScript({
            target: {tabId: tabs[0].id},
            function: () => document.body.innerText.substring(0, 15000)
        }, (injectionResults) => {
            const text = injectionResults[0].result;
            chrome.runtime.sendMessage({ action: "analyze_text", text: text }, (response) => {
                document.getElementById('loading').classList.add('hidden');
                
                if (response && response.success && !response.data.error) {
                    displayResults(response.data);
                } else {
                    alert("Error: " + (response ? (response.error || response.data.error) : "No response from background script."));
                    document.getElementById('scanBtn').classList.remove('hidden');
                }
            });
        });
    });
});

function displayResults(data) {
    document.getElementById('results').classList.remove('hidden');
    
    const scoreEl = document.getElementById('riskScore');
    scoreEl.innerText = data.overall_risk_score;
    scoreEl.style.color = data.overall_risk_score > 60 ? '#ef4444' : (data.overall_risk_score > 30 ? '#eab308' : '#22c55e');
    
    const safeEl = document.getElementById('safeToSign');
    safeEl.innerText = data.safe_to_sign ? "Safe to Sign" : "Do Not Sign";
    safeEl.style.color = data.safe_to_sign ? '#22c55e' : '#ef4444';
    
    document.getElementById('summaryText').innerText = data.summary;
    
    const container = document.getElementById('clausesContainer');
    container.innerHTML = '';
    
    if (data.flagged_clauses) {
        data.flagged_clauses.forEach(clause => {
            const div = document.createElement('div');
            const riskClass = (clause.risk_level || 'medium').toLowerCase();
            div.className = `clause ${riskClass}`;
            div.innerHTML = `
                <div><span class="badge">${clause.clause_type}</span></div>
                <div style="color: #cbd5e1; margin-bottom: 5px;">"${clause.clause_text.substring(0, 100)}..."</div>
                <div style="color: #ef4444; font-weight: 500;">${clause.consequence}</div>
            `;
            container.appendChild(div);
        });
    }
}
