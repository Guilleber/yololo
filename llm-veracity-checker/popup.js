document.getElementById("checkBtn").addEventListener("click", async () => {
    const text = document.getElementById("userInput").value;
    if (!text) {
        alert("Please enter some text.");
        return;
    }

    // Simulated API call (Replace with actual backend URL)
    try {
        const response = await fetch("http://localhost:5000/analyze", { // Update with real backend URL
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        document.getElementById("result").innerText = "Analysis: " + data.analysis;
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").innerText = "Error connecting to LLM.";
    }
});

