"use strict";

const DATA_URL = "data/sdvx_songs.json";
const LEVEL_COLORS = { 17: "#42d9ff", 18: "#ff8a3d", 19: "#ff4fac", 20: "#a47aff" };

const state = { songs: [], results: [], metadata: null };
const elements = {
  checkboxes: [...document.querySelectorAll('input[name="level"]')],
  count: document.querySelector("#recommend-count"),
  draw: document.querySelector("#draw-button"),
  results: document.querySelector("#results"),
  message: document.querySelector("#message"),
  availability: document.querySelector("#availability"),
  dataMeta: document.querySelector("#data-meta"),
  copy: document.querySelector("#copy-results"),
};

function selectedLevels() {
  return elements.checkboxes.filter((box) => box.checked).map((box) => Number(box.value));
}

function eligibleSongs() {
  const levels = new Set(selectedLevels());
  return state.songs.filter((song) => levels.has(song.level));
}

function saveSettings() {
  localStorage.setItem("sdvx-recommend-settings", JSON.stringify({
    levels: selectedLevels(), count: elements.count.value,
  }));
}

function restoreSettings() {
  const params = new URLSearchParams(location.search);
  let levels;
  let count;
  try {
    const saved = JSON.parse(localStorage.getItem("sdvx-recommend-settings") || "null");
    levels = saved?.levels;
    count = saved?.count;
  } catch (_) { /* Ignore malformed browser storage. */ }
  if (params.has("levels")) levels = params.get("levels").split(",").map(Number);
  if (params.has("count")) count = params.get("count");
  if (Array.isArray(levels)) elements.checkboxes.forEach((box) => { box.checked = levels.includes(Number(box.value)); });
  if (count && Number.isFinite(Number(count))) elements.count.value = count;
}

function updateAvailability() {
  const available = eligibleSongs().length;
  elements.availability.textContent = `현재 선택에서 ${available.toLocaleString("ko-KR")}개 채보를 추천할 수 있습니다.`;
  elements.draw.disabled = !state.songs.length || !available;
  elements.message.textContent = available ? "" : "레벨을 하나 이상 선택해 주세요.";
  elements.count.max = String(Math.max(available, 1));
  saveSettings();
}

function shuffledSample(items, count) {
  const copy = [...items];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const random = new Uint32Array(1);
    crypto.getRandomValues(random);
    const swapIndex = Math.floor((random[0] / 2 ** 32) * (index + 1));
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy.slice(0, count);
}

function renderResults() {
  elements.results.replaceChildren();
  state.results.forEach((song) => {
    const item = document.createElement("li");
    item.className = "result-card";
    const content = document.createElement("div");
    const title = document.createElement("h3");
    title.className = "song-title";
    title.textContent = song.title;
    const meta = document.createElement("div");
    meta.className = "song-meta";
    const level = document.createElement("span");
    level.className = "badge";
    level.style.setProperty("--badge-color", LEVEL_COLORS[song.level]);
    level.textContent = `LV ${song.level}`;
    const difficulty = document.createElement("span");
    difficulty.textContent = `CHART ${song.difficulty}`;
    meta.append(level, difficulty);
    content.append(title, meta);

    let link;
    if (song.url) {
      link = document.createElement("a");
      link.href = song.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "채보 보기 ↗";
    } else {
      link = document.createElement("span");
      link.textContent = "링크 없음";
      link.classList.add("disabled");
    }
    link.classList.add("song-link");
    item.append(content, link);
    elements.results.append(item);
  });
  elements.copy.hidden = !state.results.length;
}

function draw() {
  const available = eligibleSongs();
  const requested = Number(elements.count.value);
  if (!Number.isInteger(requested) || requested < 1) {
    elements.message.textContent = "추천 곡 수는 1 이상의 정수로 입력해 주세요.";
    return;
  }
  if (requested > available.length) {
    elements.message.textContent = `선택한 레벨에는 ${available.length}개 채보만 있습니다. 그 이하로 입력해 주세요.`;
    return;
  }
  state.results = shuffledSample(available, requested);
  elements.message.textContent = `${requested}개 채보를 중복 없이 추천했습니다.`;
  saveSettings();
  renderResults();
  document.querySelector("#results-title").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function copyResults() {
  const text = state.results.map((song, index) =>
    `${index + 1}. ${song.title} (LV ${song.level} / ${song.difficulty})${song.url ? ` ${song.url}` : " [링크 없음]"}`
  ).join("\n");
  try {
    await navigator.clipboard.writeText(text);
    elements.message.textContent = "추천 결과를 클립보드에 복사했습니다.";
  } catch (_) {
    elements.message.textContent = "브라우저가 클립보드 복사를 허용하지 않았습니다.";
  }
}

async function loadData() {
  try {
    const response = await fetch(DATA_URL, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.songs)) throw new Error("잘못된 데이터 형식");
    state.songs = data.songs.filter((song) => song.title && [17, 18, 19, 20].includes(song.level) && typeof song.url === "string");
    state.metadata = data;
    for (const level of [17, 18, 19, 20]) {
      const count = state.songs.filter((song) => song.level === level).length;
      document.querySelector(`[data-count="${level}"]`).textContent = `${count.toLocaleString("ko-KR")}곡`;
    }
    const updated = new Date(data.generatedAt);
    elements.dataMeta.textContent = `총 ${state.songs.length.toLocaleString("ko-KR")}개 채보 · 데이터 ${Number.isNaN(updated.valueOf()) ? "업데이트 일시 미상" : updated.toLocaleString("ko-KR")}`;
    updateAvailability();
  } catch (error) {
    elements.message.textContent = "곡 데이터를 불러오지 못했습니다. 정적 웹 서버에서 다시 열어 주세요.";
    elements.availability.textContent = `로드 오류: ${error.message}`;
  }
}

document.querySelector("#select-all").addEventListener("click", () => { elements.checkboxes.forEach((box) => { box.checked = true; }); updateAvailability(); });
document.querySelector("#clear-all").addEventListener("click", () => { elements.checkboxes.forEach((box) => { box.checked = false; }); updateAvailability(); });
elements.checkboxes.forEach((box) => box.addEventListener("change", updateAvailability));
elements.count.addEventListener("change", saveSettings);
elements.draw.addEventListener("click", draw);
elements.copy.addEventListener("click", copyResults);

restoreSettings();
loadData();
