const status = document.querySelector('#copy-status');
let toastTimer;
function announce(message) {
  status.textContent = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { status.textContent = ''; }, 3600);
}
function selectText(node) {
  const range = document.createRange();
  range.selectNodeContents(node);
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}
for (const button of document.querySelectorAll('.copy')) {
  button.addEventListener('click', async () => {
    const source = document.getElementById(button.dataset.copy);
    try {
      await navigator.clipboard.writeText(source.textContent);
      const original = 'คัดลอก';
      button.textContent = 'คัดลอกแล้ว';
      setTimeout(() => { button.textContent = original; }, 1700);
      announce('คัดลอกคำสั่งแล้ว วางในแชต Codex ได้เลย');
    } catch {
      source.closest('pre').focus({preventScroll:true});
      selectText(source);
      announce('เลือกข้อความแล้ว ใช้คำสั่งคัดลอกของอุปกรณ์');
    }
  });
}
const picker = document.querySelector('#prompt-picker');
const preview = document.querySelector('#library-prompt');
function showPrompt() {
  preview.textContent = document.getElementById(picker.value).textContent;
}
if (picker && preview) {
  picker.addEventListener('change', showPrompt);
  showPrompt();
}
