document.getElementById('scanBtn').addEventListener('click', () => {
    document.getElementById('scanBtn').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.scripting.executeScript({
            target: {tabId: tabs[0].id},
            function: () => document.body.innerText.substring(0, 15000)
        }, (injectionResults) => {
            if (chrome.runtime.lastError || !injectionResults || !injectionResults[0]) {
                alert("Cannot scan this page.");
                document.getElementById('scanBtn').classList.remove('hidden');
                document.getElementById('loading').classList.add('hidden');
                return;
            }
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
    
    // Update Score
    const scoreEl = document.getElementById('riskScore');
    scoreEl.innerText = data.overall_risk_score;
    
    if (data.safe_to_sign) {
        document.getElementById('verdictBox').classList.add('safe');
    } else {
        document.getElementById('verdictBox').classList.remove('safe');
    }
    
    let highCount = 0;
    let medCount = 0;
    
    const container = document.getElementById('warningsContainer');
    container.innerHTML = '';
    
    if (data.flagged_clauses) {
        data.flagged_clauses.forEach(clause => {
            const riskClass = (clause.risk_level || 'medium').toLowerCase();
            if (riskClass === 'high') highCount++;
            else medCount++;
            
            const dotClass = riskClass === 'high' ? 'red' : 'yellow';
            
            const div = document.createElement('div');
            div.className = 'ext-warning';
            div.innerHTML = `
                <div class="ext-warning-header">
                    <div class="dot ${dotClass}"></div>
                    <div class="ext-warning-title">${clause.clause_type}</div>
                </div>
                <div class="ext-warning-desc">${clause.why_flagged || clause.consequence}</div>
            `;
            container.appendChild(div);
        });
    }

    // Update Counts
    document.getElementById('highRiskCount').innerText = `${highCount} high risk`;
    document.getElementById('medRiskCount').innerText = `${medCount} medium`;
}
