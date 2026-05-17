// Background service worker to handle API requests without CORS issues
const API_URL = "https://lexguard-1068366375204.us-central1.run.app/analyze";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyze_text") {
        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document: request.text, language: request.language || "en" })
        })
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data: data }))
        .catch(err => sendResponse({ success: false, error: err.message }));
        return true; // Keep the message channel open for async response
    }
});
