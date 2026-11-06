const form = document.querySelector('#subtitle-form');
const project = document.querySelector('#project');
const rangeMode = document.querySelector('#range');
const timelinePoints = document.querySelector('#timeline-points');
const timelineIn = document.querySelector('#timeline-in');
const timelineOut = document.querySelector('#timeline-out');
const operation = document.querySelector('#operation');
const track = document.querySelector('#track');
const targetField = document.querySelector('#target-field');
const scope = document.querySelector('#scope');
const demoNote = document.querySelector('#demo-note');
const result = document.querySelector('#subtitle-result');
const output = document.querySelector('#subtitle-prompt');

function value(id) {
  return document.getElementById(id).value.trim();
}

function clearResult() {
  result.hidden = true;
  output.textContent = '';
}

function clearTimelineErrors() {
  timelineIn.setCustomValidity('');
  timelineOut.setCustomValidity('');
}

function updateTimelineFields() {
  const needsIn = ['in-out', 'in-to-end'].includes(rangeMode.value);
  const needsOut = ['in-out', 'start-to-out'].includes(rangeMode.value);
  timelinePoints.hidden = !needsIn && !needsOut;
  document.getElementById('timeline-in-field').hidden = !needsIn;
  document.getElementById('timeline-out-field').hidden = !needsOut;
  timelineIn.disabled = !needsIn;
  timelineOut.disabled = !needsOut;
  timelineIn.required = needsIn;
  timelineOut.required = needsOut;
  clearTimelineErrors();
}

function parseTimecode(text) {
  const frames = text.match(/^(\d{2}):([0-5]\d):([0-5]\d):(\d{2})$/);
  if (frames) {
    const [, hours, minutes, seconds, frame] = frames.map(Number);
    return { unit: 'frame', order: (hours * 3600 + minutes * 60 + seconds) * 100 + frame };
  }
  const clock = text.match(/^(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)(?:\.(\d{1,3}))?$/);
  if (!clock) return null;
  const [, hours = '0', minutes, seconds, fraction = ''] = clock;
  const wholeSeconds = Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds);
  return { unit: 'clock', order: wholeSeconds * 1000 + Number(fraction.padEnd(3, '0')) };
}

function timelineSelection() {
  const start = timelineIn.disabled ? '' : timelineIn.value.trim();
  const end = timelineOut.disabled ? '' : timelineOut.value.trim();
  const from = parseTimecode(start);
  const to = parseTimecode(end);
  for (const [field, time] of [[timelineIn, from], [timelineOut, to]]) {
    if (!field.disabled && !time) {
      field.setCustomValidity('กรอกเวลา เช่น 00:05, 00:01:20.500 หรือ 00:01:20:12');
      field.reportValidity();
      return null;
    }
  }
  if (from && to && from.unit !== to.unit) {
    timelineOut.setCustomValidity('ใช้รูปแบบเวลาเดียวกันที่จุด In และ Out เมื่อระบุเลขเฟรม');
  } else if (to && to.order <= (from?.order ?? 0)) {
    timelineOut.setCustomValidity(from ? 'จุด Out ต้องอยู่หลังจุด In' : 'จุด Out ต้องอยู่หลังต้น Timeline');
  }
  if (!timelineOut.reportValidity()) return null;

  const ranges = {
    all: 'ทั้ง Timeline ปัจจุบัน',
    'in-out': `จาก In ${start} ถึง Out ${end}`,
    'in-to-end': `จาก In ${start} ถึงท้าย Timeline ปัจจุบัน`,
    'start-to-out': `จากต้น Timeline ปัจจุบันถึง Out ${end}`,
  };
  return { description: ranges[rangeMode.value], usesFrames: from?.unit === 'frame' || to?.unit === 'frame' };
}

function updateOperation() {
  const editing = operation.value === 'edit';
  targetField.hidden = !editing;
  track.disabled = !editing;
  track.required = editing;
  track.setCustomValidity('');
}

function previewInstructions() {
  const ratio = form.elements.previewRatio.value === 'portrait' ? '9:16' : '16:9';
  const look = document.getElementById('caption-look').selectedOptions[0].textContent;
  const frame = document.getElementById('caption-frame');
  const line = document.getElementById('caption-demo-line');
  const fontSize = Number.parseFloat(getComputedStyle(line).fontSize);
  const fontPercent = Number((100 * fontSize / frame.clientWidth).toFixed(2));
  return [
    `ใช้ค่าจาก Subtitle Preview กรอบอ้างอิง ${ratio} แบบ${look} สีตัวอักษร ${value('caption-color').toUpperCase()}`,
    `ขนาดจากแถบพรีวิว ${value('caption-size')} (เทียบขนาดฟอนต์ประมาณ ${fontPercent}% ของความกว้างเฟรมตัวอย่าง) ตำแหน่งแนวตั้ง ${value('caption-position')}% วัดจากขอบบนถึงกึ่งกลางซับ`,
    `จัดข้อความสูงสุด ${value('caption-line-words')} คำต่อบรรทัดในช่วงซับเดียวกัน นับคำไทยตามหน่วยคำในบริบทและขึ้นบรรทัดที่ขอบคำ`,
    'เทียบสไตล์กับเฟรมจริงโดยรักษาสัดส่วนของ Timeline ตรวจซับตัวอย่างให้อยู่ในกรอบ และแจ้งค่าที่รูปแบบซับของโปรเจกต์รองรับไม่ครบก่อนเขียน',
  ];
}

form.addEventListener('input', (event) => {
  if (event.target === project || event.target === track) event.target.setCustomValidity('');
  if (event.target === timelineIn || event.target === timelineOut) clearTimelineErrors();
  clearResult();
});
form.addEventListener('change', clearResult);
operation.addEventListener('change', updateOperation);
rangeMode.addEventListener('change', updateTimelineFields);
form.addEventListener('reset', () => {
  demoNote.hidden = true;
  scope.options[1].disabled = false;
  project.setCustomValidity('');
  clearResult();
  requestAnimationFrame(() => {
    updateOperation();
    updateTimelineFields();
  });
});
updateOperation();
updateTimelineFields();

document.querySelector('#demo').addEventListener('click', () => {
  form.reset();
  project.value = 'รีวิวสินค้า A (สมมติ) / แนวตั้ง';
  rangeMode.value = 'in-out';
  timelineIn.value = '00:05';
  timelineOut.value = '00:32';
  updateTimelineFields();
  document.querySelector('#spoken').value = 'ไทย';
  document.querySelector('#notes').value = 'สะกดชื่อสินค้าเป็น “สินค้า A” และเก็บตัวเลขตามเสียง';
  demoNote.hidden = false;
  scope.options[1].disabled = true;
  project.focus();
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const editing = operation.value === 'edit';
  for (const field of editing ? [project, track] : [project]) {
    if (!field.value.trim()) {
      field.setCustomValidity('กรุณากรอกข้อมูลในช่องนี้');
      field.reportValidity();
      return;
    }
  }
  const selection = timelineSelection();
  if (!selection) return;

  const isDemo = !demoNote.hidden;
  const write = scope.value === 'write' && !isDemo;
  const selective = form.elements.captionMode.value === 'selective';
  const lines = [
    ...(isDemo ? ['ตัวอย่างสมมติเพื่อฝึกดูคำสั่ง ให้หยุดที่ตัวอย่างแผนซับและห้ามแก้โปรเจกต์จริง', ''] : []),
    'ใช้ $capcut-subtitles ทำซับข้อความธรรมดาที่แก้ไขต่อได้ใน CapCut',
    `โปรเจกต์และ Timeline: ${project.value.trim()}`,
    `ช่วงใน Timeline: ${selection.description}`,
    ...(rangeMode.value !== 'all' ? ['ทำซับเฉพาะช่วงที่ระบุ ตรวจขอบเขตจากเวลาใน Timeline ปัจจุบัน และรักษาซับนอกช่วง'] : []),
    ...(selection.usesFrames ? ['อ่าน HH:MM:SS:FF ตาม FPS ของ Timeline และตรวจว่าเลขเฟรมอยู่ในช่วงที่รองรับ'] : []),
    editing ? `แก้เฉพาะชุดซับ: ${track.value.trim()}` : 'เพิ่มซับเป็นชุดใหม่และคงชุดซับเดิมไว้',
    value('spoken') ? `ภาษาเสียง: ${value('spoken')}` : 'ตรวจภาษาเสียงจากต้นฉบับ',
    value('translation') ? `แปลซับเป็น: ${value('translation')}` : 'ใช้ภาษาเดียวกับเสียงต้นฉบับ',
    selective ? 'ซับแบบเลือกเน้น: ย่อเฉพาะข้อความขึ้นจอ รักษาชื่อเฉพาะ ตัวเลข คำปฏิเสธและเงื่อนไข' : 'ซับเต็ม: เก็บคำพูดตามต้นฉบับ แบ่งวลีให้อ่านทัน',
    ...previewInstructions(),
    'คำพูดสั้นที่จบความ เช่น “ใช่” ให้ขึ้นซับคำเดียวได้โดยไม่ต้องรวมกับช่วงข้างเคียง',
    ...(value('notes') ? [
      `รายละเอียดเพิ่มเติม: ${value('notes')}`,
      'หากรายละเอียดเพิ่มเติมระบุสไตล์หรือซับต้นแบบ ให้ยึดเฉพาะค่าที่ระบุไว้เหนือค่าพรีวิว',
    ] : []),
    '',
    'ถอดคำพูดและจับเวลาจากเสียงบน Timeline ล่าสุด ระบุช่วงฟังไม่ชัดให้ตรวจ และรักษาภาพ เสียง จุดตัด และความยาวเดิม',
    write ? 'ตรวจ staging และสำรองก่อนเขียน native draft แล้วอ่านกลับตรวจคำสะกด ซิงค์ และบรรทัด พร้อมส่งชื่อชุดซับและช่วงที่แก้' : 'ส่งรายการข้อความและเวลาให้ตรวจ หยุดก่อนเขียน native draft',
    'ทำผ่านไฟล์เท่านั้น ห้ามเปิด ปิด หรือควบคุม CapCut'
  ];
  output.textContent = lines.join('\n');
  result.hidden = false;
  document.querySelector('#result-title').focus();
});
