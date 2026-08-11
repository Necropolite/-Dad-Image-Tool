const DEFAULT_BACKEND = "https://pete-ramey-assistant-api.cramey254.workers.dev";

const TOPICS = [
  {
    id: "hoof-mechanics",
    title: "Hoof Mechanics",
    label: "Foundation",
    summary: "Explore how breakover, heel height, toe length, bars, balance, and loading interact in the hoof.",
    questions: [
      "What does Pete teach about breakover?",
      "How does heel height affect hoof mechanics?",
      "How do toe and heel length relate to each other?"
    ],
    sources: [
      { title: "Breakover", url: "https://www.hoofrehab.com/Breakover.html", author: "Pete Ramey" },
      { title: "Heel Height: The Deciding Factor", url: "https://www.hoofrehab.com/HeelHeight.html", author: "Pete Ramey" },
      { title: "Toe and Heel Length", url: "https://www.hoofrehab.com/Coronet.html", author: "Pete Ramey" },
      { title: "The Bars", url: "https://www.hoofrehab.com/TheBars.htm", author: "Pete Ramey" }
    ],
    related: ["balance", "sole", "caudal-foot"]
  },
  {
    id: "nutrition",
    title: "Nutrition & Hoof Health",
    label: "Whole horse",
    summary: "Follow the relationship between diet, forage, carbohydrate load, mineral balance, hoof quality, and rehabilitation.",
    questions: [
      "How does nutrition fit into hoof rehabilitation?",
      "Why is zinc important to hoof health?",
      "How does Pete use Eleanor Kellon's nutrition work?"
    ],
    sources: [
      { title: "Feeding the Hoof", url: "https://www.hoofrehab.com/Diet.html", author: "Pete Ramey, incorporating specialist nutrition work" },
      { title: "Laminitis Update", url: "https://www.hoofrehab.com/LaminitisUpdate.html", author: "Pete Ramey" },
      { title: "The End of White Line Disease", url: "https://www.hoofrehab.com/WhiteLineDisease.html", author: "Pete Ramey" }
    ],
    related: ["laminitis", "rehabilitation", "sole"]
  },
  {
    id: "laminitis",
    title: "Laminitis & Distal Descent",
    label: "Rehabilitation",
    summary: "Explore Pete's laminitis material, sinking and distal descent, hoof-capsule relationships, and rehabilitation context.",
    questions: [
      "What does Pete teach about laminitis rehabilitation?",
      "What is distal descent of P3?",
      "How has Pete's thinking about sinking changed over time?"
    ],
    sources: [
      { title: "Laminitis Update", url: "https://www.hoofrehab.com/LaminitisUpdate.html", author: "Pete Ramey" },
      { title: "Reversing Distal Descent of P3", url: "https://www.hoofrehab.com/DistalDescent.htm", author: "Pete Ramey" },
      { title: "Auburn Case Work / Documentation", url: "https://www.hoofrehab.com/AuburnUvetschool.htm", author: "Pete Ramey and Auburn research context" }
    ],
    related: ["nutrition", "rehabilitation", "hoof-mechanics"]
  },
  {
    id: "caudal-foot",
    title: "Caudal Foot & Navicular",
    label: "Pain & function",
    summary: "Explore caudal-foot pain, navicular syndrome, landing patterns, frog and heel function, and rehabilitation support.",
    questions: [
      "What does Pete teach about navicular syndrome?",
      "Why can a horse land toe-first?",
      "How do boots and pads fit into caudal-foot rehabilitation?"
    ],
    sources: [
      { title: "Digging for the Truth about Navicular Disease", url: "https://www.hoofrehab.com/NavicularSyndrome.html", author: "Pete Ramey" },
      { title: "Boots and Pads: A True Breakthrough in Healing", url: "https://www.hoofrehab.com/BootArticle.htm", author: "Pete Ramey" },
      { title: "Frog Management", url: "https://www.hoofrehab.com/FrogTrim.html", author: "Pete Ramey" }
    ],
    related: ["frog", "hoof-mechanics", "rehabilitation"]
  },
  {
    id: "sole",
    title: "Sole & Protection",
    label: "Structure",
    summary: "Explore sole thickness, exfoliation, protection, loading, and how the sole fits into broader hoof rehabilitation.",
    questions: [
      "What does Pete teach about the horse's sole?",
      "Why do some horses develop thin soles?",
      "When does Pete use protection instead of leaving a horse fully barefoot?"
    ],
    sources: [
      { title: "Understanding the Horse's Sole", url: "https://www.hoofrehab.com/HorsesSole.html", author: "Pete Ramey" },
      { title: "Boots and Pads: A True Breakthrough in Healing", url: "https://www.hoofrehab.com/BootArticle.htm", author: "Pete Ramey" },
      { title: "Heel Height: The Deciding Factor", url: "https://www.hoofrehab.com/HeelHeight.html", author: "Pete Ramey" }
    ],
    related: ["hoof-mechanics", "caudal-foot", "rehabilitation"]
  },
  {
    id: "frog",
    title: "Frog & Thrush",
    label: "Caudal foot",
    summary: "Explore frog management, central sulcus problems, thrush treatment, and the frog's role in a functional caudal foot.",
    questions: [
      "How does Pete approach frog management?",
      "What does Pete teach about thrush treatment?",
      "How does frog health connect to caudal-foot function?"
    ],
    sources: [
      { title: "Frog Management", url: "https://www.hoofrehab.com/FrogTrim.html", author: "Pete Ramey" },
      { title: "Thrush Treatment", url: "https://www.hoofrehab.com/Thrush_treatment.htm", author: "Pete Ramey" },
      { title: "Hoof Casts", url: "https://www.hoofrehab.com/Hoofcast.html", author: "Pete Ramey" }
    ],
    related: ["caudal-foot", "sole", "rehabilitation"]
  },
  {
    id: "balance",
    title: "Balance & Asymmetry",
    label: "Form & movement",
    summary: "Explore mediolateral balance, high/low hooves, angular deformities, and whole-horse influences on hoof shape.",
    questions: [
      "What does Pete teach about mediolateral balance?",
      "How does Pete approach high and low hooves?",
      "How can whole-horse asymmetry affect the feet?"
    ],
    sources: [
      { title: "Mediolateral Balance", url: "https://www.hoofrehab.com/Balance.html", author: "Pete Ramey" },
      { title: "High/Low Hooves: a Whole-Horse Issue", url: "https://www.hoofrehab.com/HighLowHooves.htm", author: "Pete Ramey" },
      { title: "Hoof Care for Angular Deformities", url: "https://www.hoofrehab.com/Pigeon-toed.html", author: "Pete Ramey" }
    ],
    related: ["hoof-mechanics", "rehabilitation", "whole-horse"]
  },
  {
    id: "rehabilitation",
    title: "Rehabilitation Cases",
    label: "Applied learning",
    summary: "Use case material and protocols to see how mechanical, nutritional, environmental, and protective strategies come together over time.",
    questions: [
      "Show me an example of a HoofRehab rehabilitation case and explain what changed.",
      "What are the main ideas in the Hoof Rehabilitation Protocol?",
      "How should I interpret case reports compared with controlled research?"
    ],
    sources: [
      { title: "Rehabilitation Pictures", url: "https://www.hoofrehab.com/Rehabilitations_Pictures.html", author: "HoofRehab case archive" },
      { title: "Hoof Rehabilitation Protocol", url: "https://www.hoofrehab.com/HoofRehabProtocol.html", author: "Debra R. Taylor DVM, Ivy Ramey, and Pete Ramey" },
      { title: "Auburn Case Work / Documentation", url: "https://www.hoofrehab.com/AuburnUvetschool.htm", author: "HoofRehab / Auburn context" }
    ],
    related: ["laminitis", "caudal-foot", "nutrition"]
  },
  {
    id: "protection",
    title: "Boots, Pads & Hoof Casts",
    label: "Tools",
    summary: "Explore temporary protection and support strategies used to keep horses moving comfortably while rehabilitation progresses.",
    questions: [
      "Why does Pete use boots and pads during rehabilitation?",
      "When are hoof casts useful?",
      "How has Pete modified Easyboot Gloves and Glue-On shells?"
    ],
    sources: [
      { title: "Boots and Pads: A True Breakthrough in Healing", url: "https://www.hoofrehab.com/BootArticle.htm", author: "Pete Ramey" },
      { title: "Hoof Casts", url: "https://www.hoofrehab.com/Hoofcast.html", author: "Pete Ramey" },
      { title: "Modifications of Easyboot Gloves and Glue-On Shells", url: "https://www.hoofrehab.com/GloveMod.html", author: "Pete Ramey" }
    ],
    related: ["sole", "caudal-foot", "rehabilitation"]
  },
  {
    id: "whole-horse",
    title: "Whole-Horse Context",
    label: "Big picture",
    summary: "Explore how movement, conformation, season, environment, diet, and the rest of the horse can influence the feet.",
    questions: [
      "What does Pete mean by treating hoof problems as whole-horse problems?",
      "How can season and environment change the hoof?",
      "What did Pete learn from observing wild horses?"
    ],
    sources: [
      { title: "High/Low Hooves: a Whole-Horse Issue", url: "https://www.hoofrehab.com/HighLowHooves.htm", author: "Pete Ramey" },
      { title: "One Foot For All Seasons?", url: "https://www.hoofrehab.com/Seasons.html", author: "Pete Ramey" },
      { title: "Wild Horses", url: "https://www.hoofrehab.com/WildHorses.html", author: "Pete Ramey; observational/historical context" },
      { title: "Is Barefoot an Option for Your Draft Horse?", url: "https://www.hoofrehab.com/Draft.htm", author: "Pete Ramey" }
    ],
    related: ["nutrition", "balance", "hoof-mechanics"]
  }
];

const state = {
  backendUrl: sessionStorage.getItem("learningLabBackend") || localStorage.getItem("learningLabBackend") || DEFAULT_BACKEND,
  token: sessionStorage.getItem("learningLabToken") || localStorage.getItem("learningLabToken") || "",
  history: [],
  citations: [],
  busy: false,
  mode: "learn",
  topicId: null,
};

const conversation = document.getElementById("conversation");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const sourceList = document.getElementById("sourceList");
const connectionStatus = document.getElementById("connectionStatus");
const connectionButton = document.getElementById("connectionButton");
const newConversationButton = document.getElementById("newConversationButton");
const connectionDialog = document.getElementById("connectionDialog");
const connectionForm = document.getElementById("connectionForm");
const closeConnectionButton = document.getElementById("closeConnectionButton");
const backendUrlInput = document.getElementById("backendUrl");
const accessTokenInput = document.getElementById("accessToken");
const rememberTokenInput = document.getElementById("rememberToken");
const testConnectionButton = document.getElementById("testConnectionButton");
const connectionMessage = document.getElementById("connectionMessage");
const learnNav = document.getElementById("learnNav");
const askNav = document.getElementById("askNav");
const learnView = document.getElementById("learnView");
const askView = document.getElementById("askView");
const topicGrid = document.getElementById("topicGrid");
const topicHome = document.getElementById("topicHome");
const topicDetail = document.getElementById("topicDetail");
const topicDetailContent = document.getElementById("topicDetailContent");
const backToTopics = document.getElementById("backToTopics");
const topEyebrow = document.getElementById("topEyebrow");
const topTitle = document.getElementById("topTitle");

function normalizedBackend(value) {
  return String(value || "").trim().replace(/\/+$/, "");
}

function authHeaders(token = state.token) {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  };
}

function setConnectionStatus(connected, label) {
  connectionStatus.classList.toggle("connected", connected);
  connectionStatus.classList.toggle("disconnected", !connected);
  connectionStatus.querySelector("span:last-child").textContent = label || (connected ? "Connected" : "Not connected");
}

function setMode(mode) {
  state.mode = mode === "ask" ? "ask" : "learn";
  const asking = state.mode === "ask";
  learnView.hidden = asking;
  askView.hidden = !asking;
  learnNav.classList.toggle("active", !asking);
  askNav.classList.toggle("active", asking);
  topEyebrow.textContent = asking ? "Grounded conversation" : "Interactive hoof-care education";
  topTitle.textContent = asking ? "Ask the material" : (state.topicId ? TOPICS.find((topic) => topic.id === state.topicId)?.title || "Learn the material" : "Learn the material");
  if (asking) window.setTimeout(() => messageInput.focus(), 0);
}

function autoGrowInput() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 180)}px`;
}

function removeWelcome() {
  conversation.querySelectorAll(".welcome-card").forEach((card) => card.remove());
}

function appendMessage(role, text, citations = []) {
  removeWelcome();
  const wrapper = document.createElement("article");
  wrapper.className = `message ${role}`;
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = role === "user" ? "You" : "Learning Lab";
  const body = document.createElement("div");
  body.className = "message-body";
  if (role === "assistant") renderAnswerText(body, text, citations);
  else body.textContent = text;
  wrapper.append(label, body);
  conversation.appendChild(wrapper);
  conversation.scrollTop = conversation.scrollHeight;
  return wrapper;
}

function renderAnswerText(container, text, citations) {
  const citationMap = new Map(citations.map((citation) => [citation.id, citation]));
  const parts = String(text || "").split(/(\[S\d+\])/g);
  for (const part of parts) {
    const match = part.match(/^\[(S\d+)\]$/);
    if (!match) {
      container.appendChild(document.createTextNode(part));
      continue;
    }
    const id = match[1];
    const button = document.createElement("button");
    button.type = "button";
    button.className = "source-ref";
    button.textContent = id;
    button.title = citationMap.get(id)?.title || `View source ${id}`;
    button.addEventListener("click", () => focusSource(id));
    container.appendChild(button);
  }
}

function renderSources(citations) {
  state.citations = Array.isArray(citations) ? citations : [];
  sourceList.replaceChildren();
  if (!state.citations.length) {
    const empty = document.createElement("div");
    empty.className = "source-empty";
    empty.textContent = "Sources used for the latest answer will appear here.";
    sourceList.appendChild(empty);
    return;
  }
  for (const citation of state.citations) {
    const card = document.createElement("article");
    card.className = "source-card";
    card.id = `source-${citation.id}`;
    const id = document.createElement("div");
    id.className = "source-id";
    id.textContent = citation.id || "Source";
    const title = document.createElement("div");
    title.className = "source-title";
    title.textContent = citation.title || citation.source || "Untitled source";
    const meta = document.createElement("div");
    meta.className = "source-meta";
    const parts = [];
    if (citation.author) parts.push(citation.author);
    if (citation.publication) parts.push(citation.publication);
    if (citation.authority) parts.push(citation.authority.replaceAll("_", " "));
    meta.textContent = parts.join(" · ") || "Source metadata unavailable";
    card.append(id, title, meta);
    if (citation.url) {
      const link = document.createElement("a");
      link.href = citation.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Open original source";
      card.appendChild(document.createElement("br"));
      card.appendChild(link);
    }
    sourceList.appendChild(card);
  }
}

function focusSource(id) {
  const card = document.getElementById(`source-${id}`);
  if (!card) return;
  document.querySelectorAll(".source-card.highlight").forEach((item) => item.classList.remove("highlight"));
  card.classList.add("highlight");
  card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  window.setTimeout(() => card.classList.remove("highlight"), 1800);
}

function setBusy(busy) {
  state.busy = busy;
  sendButton.disabled = busy;
  messageInput.disabled = busy;
  sendButton.textContent = busy ? "Thinking..." : "Ask";
}

function friendlyError(error) {
  const message = String(error?.message || error || "Unknown error");
  if (message.includes("401")) return "The private access token was rejected. Open Connection settings and check the token.";
  if (message.includes("Failed to fetch")) return "The Learning Lab could not reach the backend. Check the backend URL and your internet connection.";
  return `The Learning Lab could not answer that question. ${message}`;
}

async function askQuestion(question) {
  const cleanQuestion = String(question || "").trim();
  if (!cleanQuestion || state.busy) return;
  if (!state.token) {
    openConnectionDialog("Enter the private access token before asking a question.");
    return;
  }
  setMode("ask");
  const priorHistory = state.history.slice(-8);
  appendMessage("user", cleanQuestion);
  state.history.push({ role: "user", content: cleanQuestion });
  messageInput.value = "";
  autoGrowInput();
  setBusy(true);
  try {
    const response = await fetch(`${state.backendUrl}/api/chat`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ message: cleanQuestion, history: priorHistory }),
    });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const data = await response.json();
    if (!data.answer) throw new Error("The backend returned no answer.");
    appendMessage("assistant", data.answer, data.citations || []);
    renderSources(data.citations || []);
    state.history.push({ role: "assistant", content: data.answer });
    setConnectionStatus(true, "Connected");
  } catch (error) {
    appendMessage("assistant", friendlyError(error));
    if (String(error?.message || "").includes("401")) setConnectionStatus(false, "Token rejected");
  } finally {
    setBusy(false);
    messageInput.focus();
  }
}

async function testConnection(url, token) {
  const backend = normalizedBackend(url);
  if (!backend || !token) throw new Error("Backend URL and access token are required.");
  const response = await fetch(`${backend}/health`, { method: "GET", headers: authHeaders(token) });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  const data = await response.json();
  if (!data.ok) throw new Error("Backend health check failed.");
  return data;
}

function openConnectionDialog(message = "") {
  backendUrlInput.value = state.backendUrl || DEFAULT_BACKEND;
  accessTokenInput.value = state.token;
  rememberTokenInput.checked = Boolean(localStorage.getItem("learningLabToken"));
  connectionMessage.textContent = message;
  if (!connectionDialog.open) connectionDialog.showModal();
}

function saveConnection(url, token, remember) {
  state.backendUrl = normalizedBackend(url);
  state.token = token;
  sessionStorage.setItem("learningLabBackend", state.backendUrl);
  sessionStorage.setItem("learningLabToken", state.token);
  if (remember) {
    localStorage.setItem("learningLabBackend", state.backendUrl);
    localStorage.setItem("learningLabToken", state.token);
  } else {
    localStorage.removeItem("learningLabBackend");
    localStorage.removeItem("learningLabToken");
  }
}

function resetConversation() {
  state.history = [];
  state.citations = [];
  conversation.replaceChildren();
  const card = document.createElement("div");
  card.className = "welcome-card";
  card.innerHTML = "<div class=\"welcome-kicker\">New conversation</div><h3>What do you want to understand?</h3><p>Ask a hoof-care question, follow an idea, or ask the Lab to explain something a different way.</p>";
  conversation.appendChild(card);
  renderSources([]);
  setMode("ask");
}

function getTopic(id) {
  return TOPICS.find((topic) => topic.id === id) || null;
}

function renderTopicGrid() {
  topicGrid.replaceChildren();
  for (const topic of TOPICS) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "topic-card";
    button.innerHTML = `<span class="topic-label">${topic.label}</span><strong>${topic.title}</strong><span>${topic.summary}</span><span class="topic-arrow">Explore →</span>`;
    button.addEventListener("click", () => openTopic(topic.id));
    topicGrid.appendChild(button);
  }
}

function openTopic(id) {
  const topic = getTopic(id);
  if (!topic) return;
  state.topicId = id;
  setMode("learn");
  topicHome.hidden = true;
  topicDetail.hidden = false;
  topTitle.textContent = topic.title;
  topicDetailContent.replaceChildren();

  const hero = document.createElement("div");
  hero.className = "topic-detail-hero";
  hero.innerHTML = `<div class="topic-label">${topic.label}</div><h3>${topic.title}</h3><p>${topic.summary}</p>`;

  const actions = document.createElement("div");
  actions.className = "topic-actions";
  const overview = document.createElement("button");
  overview.type = "button";
  overview.className = "primary-button";
  overview.textContent = "Teach me this topic";
  overview.addEventListener("click", () => askQuestion(`Give me a beginner-friendly overview of ${topic.title} using only the HoofRehab teaching corpus. Explain the main ideas, preserve important caveats, credit other contributors where needed, and cite the sources.`));
  const ask = document.createElement("button");
  ask.type = "button";
  ask.className = "secondary-button";
  ask.textContent = "Ask my own question";
  ask.addEventListener("click", () => {
    setMode("ask");
    messageInput.value = `About ${topic.title}: `;
    autoGrowInput();
    messageInput.focus();
  });
  actions.append(overview, ask);
  hero.appendChild(actions);

  const questionsSection = document.createElement("section");
  questionsSection.className = "learn-section";
  questionsSection.innerHTML = "<div class=\"section-label\">Questions to explore</div><h4>Start a conversation</h4>";
  const questions = document.createElement("div");
  questions.className = "question-list";
  for (const question of topic.questions) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "learning-question";
    button.textContent = question;
    button.addEventListener("click", () => askQuestion(question));
    questions.appendChild(button);
  }
  questionsSection.appendChild(questions);

  const sourceSection = document.createElement("section");
  sourceSection.className = "learn-section";
  sourceSection.innerHTML = "<div class=\"section-label\">Original material</div><h4>Read the sources</h4><p class=\"section-copy\">These are entry points into the public HoofRehab material for this subject. The Lab may use additional relevant records when you ask a question.</p>";
  const sourceGrid = document.createElement("div");
  sourceGrid.className = "learning-source-grid";
  for (const source of topic.sources) {
    const link = document.createElement("a");
    link.className = "learning-source";
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.innerHTML = `<strong>${source.title}</strong><span>${source.author}</span><em>Open original ↗</em>`;
    sourceGrid.appendChild(link);
  }
  sourceSection.appendChild(sourceGrid);

  const relatedSection = document.createElement("section");
  relatedSection.className = "learn-section";
  relatedSection.innerHTML = "<div class=\"section-label\">Keep going</div><h4>Related subjects</h4>";
  const related = document.createElement("div");
  related.className = "related-topics";
  for (const relatedId of topic.related) {
    const relatedTopic = getTopic(relatedId);
    if (!relatedTopic) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = relatedTopic.title;
    button.addEventListener("click", () => openTopic(relatedId));
    related.appendChild(button);
  }
  relatedSection.appendChild(related);

  topicDetailContent.append(hero, questionsSection, sourceSection, relatedSection);
  learnView.scrollTop = 0;
}

function showTopicHome() {
  state.topicId = null;
  topicDetail.hidden = true;
  topicHome.hidden = false;
  setMode("learn");
  topTitle.textContent = "Learn the material";
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion(messageInput.value);
});
messageInput.addEventListener("input", autoGrowInput);
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});
document.querySelectorAll(".suggestion").forEach((button) => button.addEventListener("click", () => askQuestion(button.dataset.question)));
learnNav.addEventListener("click", () => state.topicId ? openTopic(state.topicId) : showTopicHome());
askNav.addEventListener("click", () => setMode("ask"));
backToTopics.addEventListener("click", showTopicHome);
connectionButton.addEventListener("click", () => openConnectionDialog());
newConversationButton.addEventListener("click", resetConversation);
closeConnectionButton.addEventListener("click", () => connectionDialog.close());

connectionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = normalizedBackend(backendUrlInput.value);
  const token = accessTokenInput.value.trim();
  connectionMessage.textContent = "Checking connection...";
  try {
    await testConnection(url, token);
    saveConnection(url, token, rememberTokenInput.checked);
    setConnectionStatus(true, "Connected");
    connectionDialog.close();
  } catch (error) {
    connectionMessage.textContent = friendlyError(error);
    setConnectionStatus(false, "Not connected");
  }
});

testConnectionButton.addEventListener("click", async () => {
  const url = normalizedBackend(backendUrlInput.value);
  const token = accessTokenInput.value.trim();
  connectionMessage.textContent = "Checking connection...";
  testConnectionButton.disabled = true;
  try {
    const data = await testConnection(url, token);
    connectionMessage.textContent = `Connected. ${data.retrieval || "Knowledge retrieval"} is available.`;
  } catch (error) {
    connectionMessage.textContent = friendlyError(error);
  } finally {
    testConnectionButton.disabled = false;
  }
});

renderTopicGrid();
showTopicHome();
if (state.token) {
  testConnection(state.backendUrl, state.token)
    .then(() => setConnectionStatus(true, "Connected"))
    .catch(() => setConnectionStatus(false, "Connection needs attention"));
} else {
  window.setTimeout(() => openConnectionDialog("Enter the private access token to begin."), 250);
}
autoGrowInput();
