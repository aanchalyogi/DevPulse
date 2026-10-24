
console.log(
    "Re-run buttons found:",
    document.querySelectorAll(".rerun-button").length
);
const button = document.getElementById("explain-button");

if (button) {
    button.addEventListener("click", async () => {
        const resultBox = document.getElementById("ai-result");
        const explanation = document.getElementById("ai-explanation");
        const responseBody = document.getElementById("response-body");

        button.disabled = true;
        button.textContent = "Analyzing...";
        resultBox.hidden = false;
        explanation.textContent = "Gemini is analyzing your API response...";

        try {
            const response = await fetch("/explain", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: button.dataset.status,
                    method: button.dataset.method,
                    url: button.dataset.url,
                    body: responseBody.textContent
                })
            });

            const data = await response.json();
          let text = data.explanation || "No explanation returned.";

// Clean escaped Markdown
text = text
    .replace(/\\n/g, "\n")
    .replace(/\\([#*`])/g, "$1")
    .replace(/\\([0-9]+)\./g, "$1.")
    .replace(/\\---/g, "---");

// Escape HTML for safety
text = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

// Format headings, bold text, code, and lists
text = text
    .replace(/^#{1,4}\s+(.+)$/gm, "<h4>$1</h4>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*\n]+)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^\s*[-*]\s+/gm, "• ")
    .replace(/\n/g, "<br>");

explanation.innerHTML = text;
        } catch (error) {
            explanation.textContent = "Could not contact the DevPulse server.";
        } finally {
            button.disabled = false;
            button.textContent = "Explain with AI";
        }
    });
}


document.querySelectorAll(".rerun-button").forEach((button) => {
    button.addEventListener("click", () => {
        const methodField = document.getElementById("method");
        const urlField = document.getElementById("url");
        const headersField = document.getElementById("headers");
        const bodyField = document.getElementById("body");

        try {
            methodField.value = button.dataset.method || "GET";
            urlField.value = button.dataset.url || "";

            headersField.value = JSON.stringify(
                JSON.parse(button.dataset.headers || "{}"),
                null,
                4
            );

            bodyField.value = JSON.parse(
                button.dataset.body || '""'
            );

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        } catch (error) {
            console.error("Could not load saved request:", error);
            alert("Could not load this saved request. Check the browser console.");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const historyItems = document.querySelectorAll("[data-history-item]");
    const toggleButton = document.getElementById("toggle-history-button");

    if (!toggleButton) return;

    if (historyItems.length <= 5) {
        toggleButton.style.display = "none";
        return;
    }

    let expanded = false;

    function updateHistory() {
        historyItems.forEach((item, index) => {
            item.style.display = expanded || index < 5 ? "" : "none";
        });

        toggleButton.textContent = expanded ? "Show Less" : "Show More";
    }

    toggleButton.addEventListener("click", function () {
        expanded = !expanded;
        updateHistory();
    });

    updateHistory();
});

document.addEventListener("DOMContentLoaded", function () {
    const explainButton = document.getElementById("explain-button");

    if (explainButton) {
        explainButton.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }
});

