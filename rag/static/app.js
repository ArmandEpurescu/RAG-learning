const messages = document.querySelector("#messages");
const traceLog = document.querySelector("#traceLog");
const chatForm = document.querySelector("#chatForm");
const questionInput = document.querySelector("#questionInput");
const llmSelect = document.querySelector("#llmSelect");
const speakToggle = document.querySelector("#speakToggle");
const voiceSelect = document.querySelector("#voiceSelect");
const voiceButton = document.querySelector("#voiceButton");
const clearButton = document.querySelector("#clearButton");
const statusLine = document.querySelector("#statusLine");

let recognition = null;
let assistantMessage = null;
let assistantText = "";
let availableVoices = [];

function addMessage(role, text) {
  const node = document.createElement("div");
  node.className = `message ${role}`;
  node.textContent = text;
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
  return node;
}

function appendTrace(title, payload) {
  const node = document.createElement("div");
  node.className = "trace-item";
  const value = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  node.textContent = `${title}\n${value}`;
  traceLog.appendChild(node);
  traceLog.scrollTop = traceLog.scrollHeight;
}

function speak(text) {
  if (!speakToggle.checked || !("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const selectedVoice = availableVoices.find((voice) => voice.name === voiceSelect.value);
  if (selectedVoice) utterance.voice = selectedVoice;
  utterance.rate = 1;
  window.speechSynthesis.speak(utterance);
}

function loadVoices() {
  if (!("speechSynthesis" in window)) {
    voiceSelect.disabled = true;
    return;
  }

  availableVoices = window.speechSynthesis.getVoices();
  voiceSelect.textContent = "";
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "System default";
  voiceSelect.appendChild(defaultOption);

  for (const voice of availableVoices) {
    const option = document.createElement("option");
    option.value = voice.name;
    option.textContent = `${voice.name} (${voice.lang})`;
    voiceSelect.appendChild(option);
  }
}

function parseSse(buffer, onEvent) {
  const blocks = buffer.split("\n\n");
  const remainder = blocks.pop() || "";
  for (const block of blocks) {
    let event = "message";
    const dataLines = [];
    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
    }
    if (dataLines.length) onEvent(event, JSON.parse(dataLines.join("\n")));
  }
  return remainder;
}

async function ask(question) {
  addMessage("user", question);
  assistantText = "";
  assistantMessage = addMessage("assistant", "");
  statusLine.textContent = "Retrieving context...";

  const payload = {
    question,
    top_k: 5,
    llm: llmSelect.value || null,
  };

  const response = await fetch("/ask/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok || !response.body) {
    const errorText = await response.text();
    assistantMessage.textContent = errorText || `Request failed with ${response.status}`;
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    buffer = parseSse(buffer, (event, data) => {
      if (event === "token") {
        assistantText += data.text;
        assistantMessage.textContent = assistantText;
      } else if (event === "answer") {
        assistantText += data.text;
        assistantMessage.textContent = assistantText;
      } else if (event === "done") {
        statusLine.textContent = "Ready";
        speak(assistantText);
      } else {
        appendTrace(event, data);
      }
    });
  }

  if (!assistantText.trim()) {
    assistantMessage.textContent = "No answer returned.";
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  questionInput.value = "";
  questionInput.style.height = "auto";
  try {
    await ask(question);
  } catch (error) {
    addMessage("meta", `Error: ${error.message}`);
    statusLine.textContent = "Error";
  }
});

questionInput.addEventListener("input", () => {
  questionInput.style.height = "auto";
  questionInput.style.height = `${questionInput.scrollHeight}px`;
});

clearButton.addEventListener("click", () => {
  messages.textContent = "";
  traceLog.textContent = "";
});

function setupVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceButton.disabled = true;
    voiceButton.title = "Voice input is not supported by this browser";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = true;
  recognition.continuous = false;

  recognition.onstart = () => voiceButton.classList.add("listening");
  recognition.onend = () => voiceButton.classList.remove("listening");
  recognition.onresult = (event) => {
    let transcript = "";
    for (const result of event.results) transcript += result[0].transcript;
    questionInput.value = transcript.trim();
  };
}

voiceButton.addEventListener("click", () => {
  if (!recognition) return;
  recognition.start();
});

setupVoice();
loadVoices();
if ("speechSynthesis" in window) {
  window.speechSynthesis.onvoiceschanged = loadVoices;
}
addMessage("meta", "Ask a question or use the mic. The trace panel shows retrieval steps, sources, and timings.");
