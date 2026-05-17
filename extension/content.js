// Scrape text, find "I agree" buttons, intercept clicks
let scrapedText = "";
let hasScanned = false;
let riskData = null;

function extractPageText() {
    let text = document.body.innerText;
    return text.substring(0, 15000); 
}

function findAgreeButtons() {
    const keywords = ['i agree', 'accept', 'sign up', 'agree and continue', 'accept terms'];
    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a, [role="button"]'));
    return buttons.filter(btn => {
        const text = (btn.innerText || btn.value || '').toLowerCase().trim();
        return keywords.some(kw => text === kw || text.includes(kw));
    });
}

function createOverlay(data) {
    const overlay = document.createElement('div');
    overlay.id = "lexguard-overlay";
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(15, 23, 42, 0.95); color: #f8fafc; z-index: 2147483647;
        display: flex; justify-content: center; align-items: center; font-family: sans-serif;
    `;
    
    const isRisky = data.overall_risk_score > 50;
    const color = isRisky ? '#ef4444' : '#22c55e';
    
    overlay.innerHTML = `
        <div style="background: #1e293b; padding: 2rem; border-radius: 12px; max-width: 500px; text-align: center; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <h1 style="color: ${color}; margin-top: 0;">WAIT!</h1>
            <h2 style="margin: 10px 0;">Risk Score: ${data.overall_risk_score}/100</h2>
            <p style="color: #94a3b8; line-height: 1.5;">${data.summary}</p>
            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 25px;">
                <button id="lexguard-proceed" style="background: ${color}; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                    I Accept the Risk (Proceed)
                </button>
                <button id="lexguard-cancel" style="background: #334155; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    return new Promise((resolve) => {
        document.getElementById('lexguard-proceed').onclick = () => {
            overlay.remove();
            resolve(true);
        };
        document.getElementById('lexguard-cancel').onclick = () => {
            overlay.remove();
            resolve(false);
        };
    });
}

function init() {
    scrapedText = extractPageText();
    const buttons = findAgreeButtons();
    
    if (buttons.length > 0 && scrapedText.length > 500) {
        chrome.storage.local.set({ lastScrapedText: scrapedText });
        
        buttons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if (!hasScanned) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const toast = document.createElement('div');
                    toast.innerText = "LexGuard: Analyzing Terms of Service before you agree...";
                    toast.style.cssText = "position: fixed; bottom: 20px; right: 20px; background: #3b82f6; color: white; padding: 15px; border-radius: 8px; z-index: 2147483647; box-shadow: 0 4px 12px rgba(0,0,0,0.3); font-family: sans-serif;";
                    document.body.appendChild(toast);
                    
                    chrome.runtime.sendMessage({ action: "analyze_text", text: scrapedText }, async (response) => {
                        toast.remove();
                        hasScanned = true;
                        
                        if (response.success) {
                            riskData = response.data;
                            if (riskData.error) {
                                alert("LexGuard Error: " + riskData.error);
                                return;
                            }
                            
                            const proceed = await createOverlay(riskData);
                            if (proceed) {
                                btn.click();
                            }
                        } else {
                            alert("LexGuard Failed to Analyze: " + response.error);
                            btn.click();
                        }
                    });
                }
            });
        });
    }
}

setTimeout(init, 1500);
