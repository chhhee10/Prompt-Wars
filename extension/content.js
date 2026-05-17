// Passive content script for caching page text without blocking user interaction
function extractPageText() {
    let text = document.body.innerText;
    return text.substring(0, 15000); 
}

function init() {
    const scrapedText = extractPageText();
    if (scrapedText.length > 500) {
        chrome.storage.local.set({ lastScrapedText: scrapedText });
    }
}

// Quietly cache the page text shortly after load
setTimeout(init, 1500);
