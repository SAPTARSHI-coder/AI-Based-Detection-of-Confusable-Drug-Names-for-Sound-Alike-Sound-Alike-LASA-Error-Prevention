# 📄 app/templates/index.html — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It is the **complete webpage** that opens in the browser — with all the visual design, buttons, forms, tables, animations, and the JavaScript logic that sends data to the server and displays the LASA analysis results.

---

## Real-Life Analogy

Think of this file as the **hospital reception room itself** — the physical space with the front desk, the waiting chairs, the LED displays, the forms patients fill in, and the system that shows results on the screen.

The Python files are the doctors and labs working behind the scenes. This HTML file is everything the patient (user) actually *sees* and *touches*.

---

## How an HTML File is Structured

```
<html>
  <head>  ← Settings: title, fonts, CSS styles (how things LOOK)
  <body>  ← Content: what actually appears on screen
    <header>  ← Top banner
    <main>    ← The interactive area
    <footer>  ← Bottom info bar
    <script>  ← JavaScript: what things DO when you click/type
```

There are three languages at work:
- **HTML** → The skeleton (what elements exist)
- **CSS** (inside `<style>`) → The skin (how everything looks)
- **JavaScript** (inside `<script>`) → The brain (what happens on interaction)

---

## Part 1: The `<head>` Section (Lines 3–9) — Setup & Fonts

```html
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>LASA::DETECT — AI Clinical Decision Support</title>
<meta name="description" content="AI-powered LASA drug name confusion detection..."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
```

| Tag | What it does |
|:---|:---|
| `charset="UTF-8"` | Allow all characters (letters, symbols, emojis) to display correctly |
| `viewport` | Make the page look good on mobile screens — scales automatically |
| `<title>` | Text shown on the browser tab |
| `<meta name="description">` | SEO description — shown in Google search results |
| `rel="preconnect"` | Tell the browser to connect to Google Fonts early (faster loading) |
| Google Fonts `<link>` | Download three fonts: **Share Tech Mono** (classic terminal), **Orbitron** (sci-fi titles), **JetBrains Mono** (code-style text) |

---

## Part 2: CSS Variables (Lines 11–35) — The Design System

```css
:root {
  --bg:         #020b02;   /* Near-black green background */
  --neon:       #00ff41;   /* Matrix green — the primary color */
  --danger:     #ff2244;   /* Red — HIGH risk */
  --warning:    #ffaa00;   /* Amber — MEDIUM risk */
  --text:       #c8ffc8;   /* Pale green text */
  --mono:       'JetBrains Mono', 'Share Tech Mono', monospace;
  --title:      'Orbitron', monospace;
  ...
}
```

`:root` means "apply these to the entire page." Everything defined with `--name` is a **CSS custom property** (variable). Instead of hardcoding `#00ff41` everywhere, you write `var(--neon)`. This means if you want to change the green color, you only change it in one place.

**The visual theme** is a **hacker/terminal aesthetic** — deep black background, neon green text, red danger indicators — inspired by The Matrix and cyberpunk design. Every color is chosen with a clinical purpose:

| Color | Hex | Means |
|:---|:---|:---|
| `--neon` | `#00ff41` | Safe / active / normal |
| `--danger` | `#ff2244` | HIGH risk |
| `--warning` | `#ffaa00` | MEDIUM risk |
| `--bg` | `#020b02` | Near-black background |

---

## Part 3: Visual Effects (Lines 50–88) — Matrix Rain, Scanlines, Grid

### The Matrix Canvas (Lines 51–58)

```css
#matrix-canvas {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  opacity: 0.04;
  z-index: 0;
}
```

A `<canvas>` element covering the entire screen. JavaScript will animate falling characters on it (the Matrix rain effect). 

- `position: fixed` → Stays in place even when you scroll
- `pointer-events: none` → You can't click on it — mouse clicks pass straight through to the content below
- `opacity: 0.04` → Very faint — 96% transparent. Just a subtle atmosphere, not distracting

### Scanlines Overlay (Lines 61–73)

```css
body::before {
  background: repeating-linear-gradient(
    0deg,
    transparent, transparent 2px,
    rgba(0,0,0,0.15) 2px,
    rgba(0,0,0,0.15) 4px
  );
}
```

`body::before` creates a virtual element that sits on top of the body. The `repeating-linear-gradient` draws horizontal stripes every 4px — 2px transparent then 2px slightly dark. This mimics the look of old CRT (cathode ray tube) monitor scanlines.

### Grid Overlay (Lines 76–85)

```css
body::after {
  background:
    linear-gradient(var(--neon-faint) 1px, transparent 1px),
    linear-gradient(90deg, var(--neon-faint) 1px, transparent 1px);
  background-size: 48px 48px;
}
```

`body::after` creates another virtual element with two overlapping gradient patterns — one horizontal, one vertical — making a 48×48px dot grid visible faintly across the page. Gives the feel of graph paper or a mission control display.

### `z-index` Layering

```css
header, main, footer { position: relative; z-index: 2; }
```

The page has three z-index layers:
- `z-index: 0` → background grid and matrix canvas
- `z-index: 1` → scanlines overlay
- `z-index: 2` → actual content (header, main, footer)

This ensures content is always visually on top.

---

## Part 4: Key CSS Components

### The `.sys-badge` Blinking Dot (Lines 98–119)

```css
.sys-badge::before {
  content: '';
  width: 6px; height: 6px;
  background: var(--neon);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--neon);
  animation: blink 1.2s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
```

Creates a small green blinking dot before the "LASA::DETECT v1.0" badge using `::before` (a CSS pseudo-element — a virtual element added by CSS, not HTML). The `blink` animation toggles opacity between 1 and 0, creating a blinking LED effect.

### `h1` Neon Glow (Lines 121–133)

```css
h1 {
  color: var(--neon);
  text-shadow:
    0 0 10px var(--neon),
    0 0 30px rgba(0,255,65,0.5),
    0 0 60px rgba(0,255,65,0.2);
}
```

Three layers of `text-shadow` — a tight glow, a medium glow, and a wide diffuse glow — create the neon tube light effect on the title text. This is a purely CSS trick, no images needed.

### Risk Badge Colors (Lines 428–450)

```css
.risk-HIGH   { color: var(--danger);  animation: flash-danger 2s infinite; }
.risk-MEDIUM { color: var(--warning); box-shadow: 0 0 20px var(--warn-glow); }
.risk-LOW    { color: var(--neon);    box-shadow: 0 0 20px var(--neon-glow); }
```

The `flash-danger` animation makes the HIGH risk badge pulse its red glow — drawing immediate attention. MEDIUM stays amber and static. LOW glows green and steady.

```css
clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
```

This clips the badge into a **parallelogram shape** (slanted left top, slanted right bottom) — a military/tactical HUD aesthetic.

### Probability Bar (Lines 545–565)

```css
.prob-bar-fill::after {
  width: 4px;
  filter: blur(2px);
}
```

The `::after` on the bar fill creates a bright, blurred "leading edge" — simulating a neon bar where the current end glows brightest. This is a CSS-only light pulse effect.

---

## Part 5: The HTML Body — Structure (Lines 650–846)

### Header (Lines 655–678)

```html
<div class="sys-badge">LASA::DETECT v1.0 — CLINICAL AI SYSTEM</div>
<h1>LASA·DETECT</h1>
<div class="status-bar">
  <div class="status-item"><span class="status-dot"></span> SYSTEM ONLINE</div>
  <div class="status-item"><span class="status-dot"></span> ML MODEL LOADED</div>
  <div class="status-item"><span class="status-dot warn"></span> FOR RESEARCH USE ONLY</div>
</div>
```

Three blinking status indicators at the bottom of the header — like server uptime lights on a rack. The third one is amber (`warn`) as a reminder this is not production clinical software.

### Tab Bar (Lines 686–689)

```html
<button class="tab active" id="tab-text" onclick="switchTab('text')">[ TEXT ANALYSIS ]</button>
<button class="tab" id="tab-voice" onclick="switchTab('voice')">[ VOICE ANALYSIS ]</button>
```

Two tabs, styled to look like terminal file tabs. `class="tab active"` = currently selected tab. `onclick="switchTab('text')"` calls a JavaScript function when clicked.

### Example Chips (Lines 695–700)

```html
<button class="example-chip" onclick="setExample('Push 500mg of metformin immediately.', 'diabetes')">
  SAFE: metformin/diabetes
</button>
```

Quick demo buttons. Clicking one calls `setExample(text, diagnosis)` which pre-fills the form. Four curated examples show real LASA risk scenarios.

### The Text Analysis Form (Lines 702–727)

```html
<form id="form-text" onsubmit="analyzeText(event)">
  <textarea id="sentence-input" placeholder="e.g. Administer dopamine 5mg IV push..."></textarea>
  <select id="diagnosis-text">
    <option value="">-- NULL (no context) --</option>
    <option value="cardiac_arrest">CARDIAC_ARREST</option>
    ...
  </select>
  <button type="submit">EXECUTE ANALYSIS</button>
</form>
```

- `onsubmit="analyzeText(event)"` → Call the JavaScript `analyzeText()` function when the form is submitted (instead of doing a traditional page reload)
- `<textarea>` → Multi-line text box for the clinical sentence
- `<select>` → Dropdown for diagnosis. `value=""` = no diagnosis (sends empty string to server)

### The Voice Panel (Lines 731–771)

```html
<button onclick="toggleRecording()">● RECORD AUDIO</button>
<div class="file-zone" onclick="document.getElementById('audio-input').click()">
  <input type="file" id="audio-input" accept=".wav,.mp3,.m4a,.ogg" onchange="fileChosen(this)"/>
</div>
```

- The record button calls `toggleRecording()` — a JavaScript function that accesses the microphone
- `<input type="file">` is hidden (`display: none`) — clicking the styled `file-zone` div triggers the hidden input. This is a standard trick for custom-styled file upload buttons
- `accept=".wav,.mp3,.m4a,.ogg"` → Only audio formats are selectable
- `onchange="fileChosen(this)"` → When a file is chosen, call JavaScript to display its name

### The Results Area (Lines 777–839)

```html
<div id="result-area" style="display:none">
  <div class="terminal-card">
    <div class="terminal-titlebar">
      <div class="terminal-dots"><span></span><span></span><span></span></div>
      LASA_ANALYSIS_OUTPUT.json
      <span id="res-timestamp"></span>
    </div>
    ...
  </div>
</div>
```

- `display: none` → Hidden by default. JavaScript shows it after a result arrives
- `terminal-dots` → Three circles mimicking macOS window control buttons (close/minimize/maximize) — for the terminal aesthetic
- `id="res-timestamp"` → Filled by JavaScript with the current time when a result is rendered

---

## Part 6: JavaScript — Line by Line (Lines 848–1112)

### The Matrix Rain Animation (Lines 850–878)

```javascript
(function(){
  const canvas = document.getElementById('matrix-canvas');
  const ctx    = canvas.getContext('2d');
  let cols, drops;
  const chars = '01アイウエオカキクケコ...ACGTMLDB><{}[]|=+-*/'.split('');
```

`(function(){...})()` — This is an **Immediately Invoked Function Expression (IIFE)**. The function runs immediately when the page loads, without waiting to be called. The parentheses at the end `()` trigger the execution.

`canvas.getContext('2d')` — Get the 2D drawing context — a set of drawing tools (draw rectangle, draw text, etc.) for the canvas element.

`chars` — An array of characters to use in the rain. Mix of `0`/`1` (binary), Japanese katakana (Matrix movie reference), DNA letters (`ACGT`), and code symbols.

```javascript
function resize() {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  cols  = Math.floor(canvas.width / 18);
  drops = Array(cols).fill(1);
}
resize();
window.addEventListener('resize', resize);
```

`resize()` is called immediately AND every time the window is resized.
- Sets canvas to full screen size
- Calculates how many columns of characters fit (`width / 18px per char`)
- `drops` = an array of vertical positions, one per column, all starting at 1 (row 1)

```javascript
function draw() {
  ctx.fillStyle = 'rgba(2,11,2,0.05)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00ff41';
  ctx.font = '13px JetBrains Mono, monospace';
  drops.forEach((y, i) => {
    const ch = chars[Math.floor(Math.random() * chars.length)];
    ctx.fillText(ch, i * 18, y * 18);
    if (y * 18 > canvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  });
}
setInterval(draw, 60);
```

**How the Matrix rain works:**

Every 60ms (`setInterval(draw, 60)` = ~16fps):

1. `ctx.fillRect(0, 0, ..., 'rgba(2,11,2,0.05)')` → Paint the entire canvas with a nearly transparent dark green. This *doesn't erase* old characters — it slightly fades them. This creates the trailing "ghost" effect as characters fall.

2. For each column `i`:
   - Pick a random character
   - Draw it at position `(i * 18, y * 18)` — column × 18px wide, row × 18px tall
   - If the character has fallen past the bottom AND a random number > 0.975 (2.5% chance) → reset drop to top (`drops[i] = 0`)
   - Move the drop down one row (`drops[i]++`)

The randomness in reset creates the staggered, natural rain appearance.

---

### `setExample()` (Lines 881–884)

```javascript
function setExample(text, diag) {
  document.getElementById('sentence-input').value = text;
  document.getElementById('diagnosis-text').value = diag;
}
```

`document.getElementById('...')` — Finds the HTML element with that `id`. `.value = text` — Sets its current value. Simple pre-fill of the form fields.

---

### `switchTab()` (Lines 887–898)

```javascript
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');
  hideResult();
}
```

Step by step:
1. Find ALL elements with class `tab` → remove `active` from each (deselect all tabs)
2. Find ALL elements with class `panel` → remove `active` from each (hide all panels)
3. Add `active` back to the clicked tab (tab ID = `"tab-text"` or `"tab-voice"`)
4. Add `active` back to its corresponding panel
5. Hide any existing result

CSS rule `.panel.active { display: block; }` ensures only the active panel is visible.

---

### `toggleRecording()` (Lines 910–940)

This function handles the live microphone recording feature.

```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
```
Ask the browser to access the user's microphone. If the user grants permission, returns a `stream` object.

```javascript
mediaRecorder = new MediaRecorder(stream);
audioChunks = [];
mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
```
Create a `MediaRecorder` — a browser API for recording audio. Every time a chunk of audio data is available, save it to `audioChunks`.

```javascript
mediaRecorder.onstop = () => {
  recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
  ...
};
mediaRecorder.start();
```
When recording stops, combine all chunks into a single `Blob` (Binary Large Object — raw binary data, like a file in memory) in WebM audio format. This blob will be uploaded to the server.

```javascript
mediaRecorder.stop();
mediaRecorder.stream.getTracks().forEach(t => t.stop());
```
Stop recording AND stop the microphone stream (releases the hardware — the browser's recording indicator disappears).

---

### `setLoading()` (Lines 943–947)

```javascript
function setLoading(id, on) {
  const btn = document.getElementById(id);
  btn.classList.toggle('loading', on);
  btn.disabled = on;
}
```

Toggles a loading state on a button. `classList.toggle('loading', on)` — adds the class `loading` if `on=true`, removes it if `on=false`. CSS rules `.loading .spinner { display: block; }` and `.loading .btn-text { display: none; }` then show the spinner and hide the button text automatically.

---

### `renderResult()` (Lines 950–1036) — The Most Important JS Function

This function takes the JSON response from the server and updates every part of the results area.

```javascript
function renderResult(data) {
  const d  = data.decision;
  const rl = d.risk_level;   // "LOW", "MEDIUM", or "HIGH"
```

The `data` object is exactly what `app.py` returned:
```json
{
  "status": "ok",
  "drug": "hydralazine",
  "extracted": {...},
  "decision": { "risk_level": "HIGH", "message": "⚠ Caution...", "reasons": [...] },
  "lasa_hits": [...]
}
```

**Setting the timestamp:**
```javascript
document.getElementById('res-timestamp').textContent =
  new Date().toISOString().replace('T',' ').slice(0,19) + ' UTC';
```
`new Date().toISOString()` → `"2024-01-15T14:32:00.000Z"` → strip to `"2024-01-15 14:32:00 UTC"`.

**Setting the drug name:**
```javascript
document.getElementById('res-drug').textContent = (data.drug || '—').toUpperCase();
```
Display the identified drug in uppercase.

**Setting the risk badge:**
```javascript
const badge = document.getElementById('res-risk-badge');
badge.className = 'risk-badge risk-' + rl;
```
Replace the element's entire CSS class list to `"risk-badge risk-HIGH"` (or MEDIUM/LOW). The corresponding CSS rules apply the correct color and animation.

**Building the reasons log:**
```javascript
(d.reasons || []).forEach(r => {
  const div = document.createElement('div');
  div.className = 'log-entry';
  div.textContent = r;
  rList.appendChild(div);
});
```
- `document.createElement('div')` → Create a new `<div>` element in memory
- `.textContent = r` → Set its text to one reason from the list
- `.appendChild(div)` → Add it to the log container in the DOM

This loops through all reasons and adds one styled row per reason.

**Building the LASA hits table:**
```javascript
hits.forEach(h => {
  const prob  = h.lasa_prob;
  const pct   = (prob * 100).toFixed(1) + '%';
  const color = prob > 0.75 ? 'var(--danger)' : prob > 0.45 ? 'var(--warning)' : 'var(--neon)';
  const row   = document.createElement('tr');
  row.innerHTML = `
    <td>${h.candidate}</td>
    <td>
      <div class="prob-bar">
        <div class="prob-bar-fill" style="width:${pct};background:${color}"></div>
      </div>
      <div class="prob-val">${pct}</div>
    </td>
    <td><span class="risk-badge risk-${h.risk_level}">${h.risk_level}</span></td>
    <td>${h.known_in_ismp ? '⚑ YES' : '—'}</td>
  `;
  tbody.appendChild(row);
});
```

For each LASA hit:
- Calculate color based on probability threshold (red/amber/green)
- Create a `<tr>` (table row) with 4 columns: drug name, probability bar, risk badge, ISMP flag
- The probability bar width is set dynamically to `pct` (e.g., `width: 87%`)
- Append the row to the table

**Template literals** (backtick strings `` `...` ``): Allow embedding variables directly in strings using `${variable}` — much cleaner than string concatenation.

---

### `analyzeText()` (Lines 1045–1065)

```javascript
async function analyzeText(e) {
  e.preventDefault();
```
`e.preventDefault()` — Prevent the default form submit behavior (which would reload the page). Instead, we handle the submission ourselves with JavaScript.

```javascript
  const form = new FormData();
  form.append('text', text);
  form.append('diagnosis', diagnosis);
  const res  = await fetch('/analyze', { method: 'POST', body: form });
  const data = await res.json();
```

`FormData` — A special object for packaging form fields for HTTP submission.

`fetch('/analyze', ...)` — Send a POST request to the `/analyze` endpoint of the FastAPI server. `await` pauses execution until the server responds.

`await res.json()` — Parse the server's JSON response into a JavaScript object.

```javascript
  if (!res.ok) throw new Error(data.detail || 'Internal Server Error');
  renderResult(data);
```
If the server returned a non-200 status code (error), throw an error that the `catch` block will handle. Otherwise, call `renderResult()` to display everything.

```javascript
  } catch(err) {
    showError(err.message);
  } finally {
    setLoading('btn-text', false);
  }
```
`finally` block always runs (whether success or failure) — always restore the button from loading state.

---

### `analyzeVoice()` (Lines 1068–1095)

Nearly identical to `analyzeText()` but handles two file sources:

```javascript
if (recordedBlob) {
  form.append('file', recordedBlob, 'recording.webm');
} else {
  form.append('file', fileInput.files[0]);
}
```
If the user recorded audio via the browser, use `recordedBlob`. If they uploaded a file, use that. Both are sent as file attachments to the `/voice` endpoint.

---

### Drag and Drop (Lines 1097–1112)

```javascript
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('active'); });
dz.addEventListener('dragleave', () => dz.classList.remove('active'));
dz.addEventListener('drop', e => {
  e.preventDefault();
  dz.classList.remove('active');
  const file = e.dataTransfer.files[0];
  if (file) {
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    fileChosen(input);
  }
});
```

Three event listeners on the drop zone:

| Event | What triggers it | What happens |
|:---|:---|:---|
| `dragover` | User drags a file over the zone | Highlight the zone (add `active` class), prevent default browser behavior |
| `dragleave` | User drags file away | Remove highlight |
| `drop` | User drops the file | Get the dropped file from `e.dataTransfer`, inject it into the hidden `<input>`, call `fileChosen()` |

`DataTransfer` is a browser API used to programmatically set a file input's files — normally you can't do this for security reasons, but `DataTransfer` provides the approved workaround.

---

## Summary: Complete User Journey Through the Code

```
User opens http://localhost:8000
└── index.html loads
    ├── CSS renders: dark background, grid, scanlines, neon colors
    ├── Matrix rain starts (setInterval every 60ms)
    └── Two tabs visible: TEXT ANALYSIS (active) | VOICE ANALYSIS

User types "hydralazine" + selects "anxiety" + clicks EXECUTE ANALYSIS
└── analyzeText(event) fires
    ├── e.preventDefault() — no page reload
    ├── button → loading state (spinner shows)
    ├── fetch POST /analyze → FastAPI processes → JSON returned
    ├── setLoading(false) — button restored
    └── renderResult(data):
        ├── Timestamp set
        ├── Drug name displayed: "HYDRALAZINE"
        ├── Badge: risk-badge risk-HIGH (pulsing red)
        ├── Message: "⚠ Caution: Potential LASA confusion with 'hydroxyzine'..."
        ├── Reasons log: 4 bullet points
        ├── Top 5 hits table with probability bars (red/amber/green)
        └── Context mismatch box shown: "antihypertensive not indicated for anxiety"
```
