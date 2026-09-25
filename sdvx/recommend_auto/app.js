"use strict";

const DATA_URL = new URL("data/sdvx_songs.json", document.baseURI);
const state = { songs: [], results: [], copyLines: [], heading: "" };

const elements = {
  count: document.querySelector("#select1"),
  draw: document.querySelector("#draw-button"),
  copyImage: document.querySelector("#copy-image"),
  copyText: document.querySelector("#copy-text"),
  levels: [...document.querySelectorAll('input[name="level"]')],
  message: document.querySelector("#message2"),
  status: document.querySelector("#status"),
  results: document.querySelector("#results"),
  searchForm: document.querySelector("#search-form"),
  searchInput: document.querySelector("#search-input"),
  searchResults: document.querySelector("#search-results"),
  updated: document.querySelector("#lastupdatedate"),
  songCount: document.querySelector("#song-count"),
};

function selectedLevels() {
  return elements.levels.filter((box) => box.checked).map((box) => Number(box.value));
}

function seededRandom(seed, min, max) {
  const normalized = ((seed * 9301 + 49297) % 233280) / 233280;
  return Math.floor(min + normalized * (max - min + 1));
}

function todaysSeed() {
  const today = new Date();
  return today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
}

function randomInteger(maxExclusive) {
  if (globalThis.crypto?.getRandomValues) {
    const value = new Uint32Array(1);
    crypto.getRandomValues(value);
    return Math.floor((value[0] / 2 ** 32) * maxExclusive);
  }
  return Math.floor(Math.random() * maxExclusive);
}

function sampleWithoutReplacement(items, count) {
  const copy = [...items];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = randomInteger(index + 1);
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy.slice(0, count);
}

function songCopyLine(song) {
  const chartLabel = [song.chartType, displayDifficulty(song)].filter((value) => value !== "" && value != null).join(" ");
  return song.url
    ? `[${song.title}](${song.url}) [ ${chartLabel} ]`
    : `${song.title} [ ${chartLabel} ]`;
}

function displayDifficulty(song) {
  const value = Number(song.difficulty);
  if (song.difficultySource === "wiki" && song.level >= 18 && Number.isInteger(value)) {
    return value.toFixed(1);
  }
  return String(song.difficulty);
}

function makeJacket(song) {
  const wrap = document.createElement("span");
  wrap.className = "jacket-wrap";
  const fallback = document.createElement("span");
  fallback.className = "jacket-fallback";
  fallback.textContent = "NO IMAGE";
  wrap.append(fallback);

  if (song.jacketPath) {
    const image = document.createElement("img");
    image.className = "jacket";
    image.alt = `${song.title} 자켓`;
    image.addEventListener("load", () => {
      fallback.remove();
    }, { once: true });
    image.addEventListener("error", () => image.remove(), { once: true });
    image.src = new URL(song.jacketPath, document.baseURI).href;
    wrap.append(image);
  }
  return wrap;
}

function makeSongRow(song) {
  const row = document.createElement("div");
  row.className = "result-row";
  row.append(makeJacket(song));

  const info = document.createElement("div");
  info.className = "song-info";
  let title;
  if (song.url) {
    title = document.createElement("a");
    title.href = song.url;
    title.target = "_blank";
    title.rel = "noopener noreferrer";
  } else {
    title = document.createElement("span");
    title.classList.add("no-link");
  }
  title.classList.add("song-title");
  title.textContent = song.title;

  const meta = document.createElement("div");
  meta.className = "song-meta";
  const chartLabel = [song.chartType, displayDifficulty(song)].filter((value) => value !== "" && value != null).join(" ");
  meta.textContent = song.url ? chartLabel : `${chartLabel} · 링크 없음`;
  info.append(title, meta);
  row.append(info);
  return row;
}

function renderSongs(songs, heading = "") {
  elements.results.replaceChildren();
  state.results = songs;
  state.heading = heading;
  state.copyLines = songs.map(songCopyLine);
  if (heading) {
    const title = document.createElement("div");
    title.className = "daily-title";
    title.textContent = heading;
    elements.results.append(title);
    state.copyLines.unshift(heading);
  }
  songs.forEach((song) => elements.results.append(makeSongRow(song)));
}

function showTodaysSongs() {
  const seed = todaysSeed();
  const songs = [17, 18, 19].map((level) => {
    const candidates = state.songs.filter((song) => song.level === level);
    return candidates[seededRandom(seed, 0, candidates.length - 1)];
  }).filter(Boolean);
  renderSongs(songs, `${seed} 오늘의 추천곡`);
}

function drawSongs() {
  const levels = new Set(selectedLevels());
  const candidates = state.songs.filter((song) => levels.has(song.level));
  elements.results.replaceChildren();

  if (candidates.length === 0) {
    const easterEgg = document.createElement("div");
    easterEgg.className = "easter-egg";
    easterEgg.textContent = "Dyscontrolled galaxy!!";
    elements.results.append(easterEgg);
    state.results = [];
    state.heading = "";
    state.copyLines = ["Dyscontrolled galaxy!!"];
  } else {
    const count = Number(elements.count.value);
    if (count > candidates.length) {
      elements.status.textContent = `선택한 레벨에는 ${candidates.length}곡만 있습니다.`;
      return;
    }
    renderSongs(sampleWithoutReplacement(candidates, count));
    elements.status.textContent = "";
  }

  elements.message.textContent = "마음에 들지 않는다면 재추첨 버튼을 눌러주세요";
  elements.draw.textContent = "재추첨";
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  return copied;
}

async function copyTextResults() {
  const text = state.copyLines.join("\n");
  if (!text) {
    elements.status.textContent = "복사할 추천 결과가 없습니다.";
    return;
  }
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
    else if (!fallbackCopy(text)) throw new Error("copy unavailable");
    elements.status.textContent = "클립보드에 복사되었습니다!";
  } catch (_) {
    elements.status.textContent = fallbackCopy(text) ? "클립보드에 복사되었습니다!" : "이 브라우저에서는 자동 복사를 사용할 수 없습니다.";
  }
}

function canvasBlob(canvas) {
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

async function copyImageResults() {
  if (!state.copyLines.length) {
    elements.status.textContent = "복사할 추천 결과가 없습니다.";
    return;
  }
  if (!globalThis.ClipboardItem || !navigator.clipboard?.write) {
    elements.status.textContent = "이 브라우저에서는 사진 복사를 사용할 수 없습니다. 텍스트 복사를 이용해 주세요.";
    return;
  }
  const rows = [...elements.results.querySelectorAll(".result-row")];
  const width = Math.max(520, Math.ceil(elements.results.getBoundingClientRect().width));
  const headingHeight = state.heading ? 38 : 0;
  const rowHeight = 78;
  const height = Math.max(58, 16 + headingHeight + Math.max(rows.length, 1) * rowHeight);
  const scale = 2;
  const canvas = document.createElement("canvas");
  canvas.width = width * scale;
  canvas.height = height * scale;
  const context = canvas.getContext("2d");
  context.scale(scale, scale);
  context.fillStyle = "#fff";
  context.fillRect(0, 0, width, height);
  let y = 16;
  if (state.heading) {
    context.fillStyle = "#212529";
    context.font = '16px "Noto Sans KR", sans-serif';
    context.fillText(state.heading, 0, y + 20, width);
    y += headingHeight;
  }
  if (!rows.length) {
    context.fillStyle = "#212529";
    context.font = '16px "Noto Sans KR", sans-serif';
    context.fillText(state.copyLines.join(" "), 0, y + 24, width);
  }
  for (const row of rows) {
    const image = row.querySelector("img.jacket");
    if (image?.complete && image.naturalWidth) {
      context.drawImage(image, 0, y + 6, 64, 64);
    } else {
      context.fillStyle = "#e9ecef";
      context.fillRect(0, y + 6, 64, 64);
      context.fillStyle = "#6c757d";
      context.font = '10px "Noto Sans KR", sans-serif';
      context.fillText("NO IMAGE", 8, y + 42);
    }
    context.fillStyle = "#007bff";
    context.font = '16px "Noto Sans KR", sans-serif';
    context.fillText(row.querySelector(".song-title")?.textContent || "", 76, y + 28, width - 82);
    context.fillStyle = "#6c757d";
    context.font = '13px "Noto Sans KR", sans-serif';
    context.fillText(row.querySelector(".song-meta")?.textContent || "", 76, y + 50, width - 82);
    context.strokeStyle = "#e3e6e8";
    context.beginPath();
    context.moveTo(0, y + rowHeight - 1);
    context.lineTo(width, y + rowHeight - 1);
    context.stroke();
    y += rowHeight;
  }
  try {
    const blob = await canvasBlob(canvas);
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
    elements.status.textContent = "추천 결과를 사진으로 복사했습니다.";
  } catch (_) {
    elements.status.textContent = "사진 복사에 실패했습니다. 텍스트 복사를 이용해 주세요.";
  }
}

function searchSongs(event) {
  event.preventDefault();
  const query = elements.searchInput.value.trim().toLocaleLowerCase();
  elements.searchResults.replaceChildren();
  const matches = state.songs.filter((song) => song.title.toLocaleLowerCase().includes(query));
  matches.forEach((song) => {
    const item = document.createElement("li");
    if (song.url) {
      const link = document.createElement("a");
      link.href = song.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = song.title;
      item.append(link);
    } else {
      item.textContent = `${song.title} · 링크 없음`;
    }
    elements.searchResults.append(item);
  });
}

function applyData(data, sourceLabel) {
  if (!data || !Array.isArray(data.songs)) throw new Error("잘못된 데이터 형식");
  state.songs = data.songs.filter((song) => song.title && [17, 18, 19, 20].includes(song.level));
  const updated = new Date(data.generatedAt);
  elements.updated.textContent = `last update : ${Number.isNaN(updated.valueOf()) ? "unknown" : updated.toLocaleDateString("ko-KR")}`;
  elements.songCount.textContent = `전체 곡 수: ${state.songs.length}곡`;
  elements.status.textContent = sourceLabel;
  elements.draw.disabled = false;
  showTodaysSongs();
}

async function loadData() {
  const fallback = globalThis.SDVX_SONG_DATA;
  if (location.protocol === "file:") {
    applyData(fallback, "로컬 파일용 데이터로 실행 중입니다.");
    return;
  }
  try {
    const response = await fetch(DATA_URL, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    applyData(await response.json(), "");
  } catch (error) {
    if (fallback) applyData(fallback, "JSON을 불러오지 못해 내장 데이터로 실행 중입니다.");
    else {
      elements.status.textContent = `로드 오류: ${error.message}`;
      elements.message.textContent = "곡 데이터를 불러오지 못했습니다.";
    }
  }
}

elements.draw.addEventListener("click", drawSongs);
elements.copyText.addEventListener("click", copyTextResults);
elements.copyImage.addEventListener("click", copyImageResults);
elements.searchForm.addEventListener("submit", searchSongs);
document.querySelector("#select-all").addEventListener("click", () => elements.levels.forEach((box) => { box.checked = true; }));
document.querySelector("#clear-all").addEventListener("click", () => elements.levels.forEach((box) => { box.checked = false; }));

loadData();
