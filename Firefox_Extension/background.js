const SYSTEM_PROMPT =
  "You are a community note creator, tasked to fact-check posts based on provided web search results. " +
  "Answer only based on the provided articles. " +
  "If there is no relevant information, say you couldn't find any. " +
  "Keep your answer to 140 characters maximum.";

browser.runtime.onMessage.addListener((request) => {
  if (request.type === "sendToLLM") {
    return handleFactCheck(request.text);
  }
});

async function handleFactCheck(text) {
  const stored = await browser.storage.local.get(["tavily_key", "llm_model", "openai_key", "gemini_key"]);
  const model = stored.llm_model || "gemini-2.5-flash";

  if (!stored.tavily_key) return { success: false, error: "Tavily API key not set — open the extension popup to configure it." };

  const llmKey = model.startsWith("gemini") ? stored.gemini_key : stored.openai_key;
  if (!llmKey) return { success: false, error: `API key for ${model} not set — open the extension popup to configure it.` };

  // 1. Web search
  let sources;
  try {
    sources = await tavilySearch(text, stored.tavily_key);
  } catch (e) {
    return { success: false, error: "Tavily search failed: " + e.message };
  }

  // 2. LLM verdict
  const sourcesText = sources.map(s => `${s.title}: ${s.content}`).join("\n\n");
  const userPrompt = `Post: ${text}\n\nRelevant articles:\n${sourcesText}`;

  try {
    const message = model.startsWith("gemini")
      ? await callGemini(model, userPrompt, llmKey)
      : await callOpenAI(model, userPrompt, llmKey);

    return {
      success: true,
      data: {
        message,
        source_count: sources.length,
        sources: sources.slice(0, 3).map(s => ({ title: s.title, url: s.url })),
      },
    };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function tavilySearch(query, apiKey) {
  const res = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, query, search_depth: "advanced", max_results: 5 }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.results || [];
}

async function callGemini(model, userPrompt, apiKey) {
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
        contents: [{ parts: [{ text: userPrompt }] }],
      }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Gemini error: ${err.error?.message || res.status}`);
  }
  const data = await res.json();
  return data.candidates[0].content.parts[0].text;
}

async function callOpenAI(model, userPrompt, apiKey) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}` },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userPrompt },
      ],
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`OpenAI error: ${err.error?.message || res.status}`);
  }
  const data = await res.json();
  return data.choices[0].message.content;
}
