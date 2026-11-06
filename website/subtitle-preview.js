const form = document.getElementById('subtitle-form');
const preview = document.getElementById('caption-preview');
const frame = document.getElementById('caption-frame');
const line = document.getElementById('caption-demo-line');
const caption = document.getElementById('caption-demo-text');
const play = document.getElementById('caption-play');
const progress = document.getElementById('caption-progress');
const info = document.getElementById('caption-cue-info');
const warning = document.getElementById('caption-preview-warning');
const size = document.getElementById('caption-size');
const position = document.getElementById('caption-position');
const color = document.getElementById('caption-color');
const look = document.getElementById('caption-look');
const lineWords = document.getElementById('caption-line-words');
const lineWordsValue = document.getElementById('caption-line-words-value');

// The examples have known word boundaries, including the standalone reply.
const sample = [
  ['ทั้ง', 'วัน', 'ทั้ง', 'คืน'],
  ['ใช่'],
  ['ลอง', 'ปรับ', 'ซับ', 'แล้ว', 'ดู', 'ความต่าง'],
];
const selectiveSample = [sample[0], sample[1], ['ปรับ', 'ซับ']];
const characterCount = (text) => Array.from(text).length;
let cues = [];
let cueIndex = 0;
let timer = null;

function updateWarning() {
  const lineHeight = line.offsetHeight;
  line.style.setProperty('--caption-half-height', `${lineHeight / 2}px`);
  let message = '';
  if (line.scrollWidth > line.clientWidth) {
    message = 'บรรทัดซับกว้างเกินกรอบ ลองลดขนาดตัวอักษรหรือจำนวนคำต่อบรรทัด';
  } else if (lineHeight > frame.clientHeight) {
    message = 'ซับสูงเกินกรอบ ลองลดขนาดตัวอักษรหรือเพิ่มจำนวนคำต่อบรรทัด';
  }
  if (warning.textContent !== message) warning.textContent = message;
  warning.hidden = !message;
}

function showCue() {
  const words = cues[cueIndex];
  const text = words.join('');
  const wordsPerLine = Number(lineWords.value);
  const lines = [];
  for (let start = 0; start < words.length; start += wordsPerLine) {
    lines.push(words.slice(start, start + wordsPerLine).join(''));
  }
  caption.textContent = lines.join('\n');
  lineWordsValue.textContent = lineWords.value;
  progress.max = cues.length;
  progress.value = cueIndex + 1;
  const lengthNote = text === 'ใช่' ? ' · คำเดียวขึ้นเดี่ยวได้' : '';
  info.textContent = `ช่วง ${cueIndex + 1} จาก ${cues.length} · ${words.length} คำ · ${characterCount(text)} ตัวอักษร · ${lines.length} บรรทัด${lengthNote}`;
  updateWarning();
}

function updateStyle() {
  frame.dataset.ratio = form.elements.previewRatio.value;
  frame.dataset.look = look.value;
  frame.style.setProperty('--caption-size', size.value);
  frame.style.setProperty('--caption-position', `${position.value}%`);
  frame.style.setProperty('--caption-color', color.value);
  document.getElementById('caption-size-value').textContent = size.value;
  document.getElementById('caption-position-value').textContent = `${position.value}%`;
  updateWarning();
}

function updateCues() {
  cues = form.elements.captionMode.value === 'selective' ? selectiveSample : sample;
  cueIndex = 0;
  showCue();
}

function nextCue() {
  cueIndex = (cueIndex + 1) % cues.length;
  showCue();
}

function pause() {
  clearInterval(timer);
  timer = null;
  play.textContent = 'เล่นตัวอย่าง';
}

play.addEventListener('click', () => {
  if (timer !== null) {
    pause();
    return;
  }
  timer = setInterval(nextCue, 1700);
  play.textContent = 'พักตัวอย่าง';
});

document.getElementById('caption-next').addEventListener('click', () => {
  pause();
  nextCue();
});
preview.addEventListener('input', (event) => {
  if (event.target === lineWords) showCue();
  else updateStyle();
});
form.addEventListener('change', (event) => {
  if (event.target.name === 'captionMode') updateCues();
});
form.addEventListener('reset', () => {
  pause();
  requestAnimationFrame(() => {
    updateCues();
    updateStyle();
  });
});

updateCues();
updateStyle();
new ResizeObserver(updateWarning).observe(line);
document.fonts.ready.then(updateWarning);
