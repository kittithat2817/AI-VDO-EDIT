const form = document.querySelector('#experiment-form');
const product = document.querySelector('#product');
const project = document.querySelector('#project');
const method = document.querySelector('#method');
const takeaway = document.querySelector('#takeaway');
const cta = document.querySelector('#cta');
const scope = document.querySelector('#scope');
const demoNote = document.querySelector('#demo-note');
const result = document.querySelector('#experiment-result');
const output = document.querySelector('#experiment-prompt');
const requiredFields = [product, project, method, takeaway];

function clearResult() {
  result.hidden = true;
  output.textContent = '';
}

form.addEventListener('input', (event) => {
  if (requiredFields.includes(event.target)) event.target.setCustomValidity('');
  clearResult();
});
form.addEventListener('change', clearResult);
form.addEventListener('reset', () => {
  demoNote.hidden = true;
  scope.options[1].disabled = false;
  requiredFields.forEach((field) => field.setCustomValidity(''));
  clearResult();
});

document.querySelector('#demo').addEventListener('click', () => {
  form.reset();
  product.value = 'แก้วเก็บความเย็น A (สมมติ)';
  project.value = 'ทดลองแก้ว A / แนวตั้ง';
  method.value = 'เทียบกับแก้วทั่วไป ใส่น้ำแข็งเท่ากัน ถ่ายเทียบเมื่อครบ 30 นาที';
  takeaway.value = 'ให้เห็นความต่างของน้ำแข็งที่เหลือภายใต้เงื่อนไขนี้';
  cta.value = '';
  demoNote.hidden = false;
  scope.options[1].disabled = true;
  product.focus();
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  for (const field of requiredFields) {
    if (!field.value.trim()) {
      field.setCustomValidity('กรุณากรอกข้อมูลในช่องนี้');
      field.reportValidity();
      return;
    }
  }

  const isDemo = !demoNote.hidden;
  const willEdit = scope.value === 'edit' && !isDemo;
  const sequence = form.elements.opening.value === 'question'
    ? 'ตั้งโจทย์ก่อน → แสดงวิธีทดลองและเงื่อนไข → แสดงผลที่ยืนยันได้ → สรุป'
    : 'เปิดด้วยภาพผลที่ยืนยันได้ → ย้อนตั้งโจทย์และแสดงวิธีทดลอง → อธิบายเงื่อนไขและสรุป';
  const lines = [
    ...(isDemo ? ['ตัวอย่างสมมติเพื่อฝึกดูคำสั่ง ให้หยุดที่แผนตัวอย่างและห้ามแก้โปรเจกต์จริง', ''] : []),
    willEdit
      ? 'ใช้ $capcut-story-planner แล้วส่งต่อ $capcut-script-edit วางแผนและตัดคลิปทดลองสินค้า'
      : 'ใช้ $capcut-story-planner วางแผนคลิปทดลองสินค้าอย่างเดียว',
    `โปรเจกต์และ Timeline: ${project.value.trim()}`,
    `สินค้า: ${product.value.trim()}`,
    `โจทย์ วิธีทดลอง และเงื่อนไข: ${method.value.trim()}`,
    `สารหลัก: ${takeaway.value.trim()}`,
    cta.value.trim() ? `CTA ที่ต้องการ: ${cta.value.trim()}` : 'ตอนจบ: สรุปผลตามหลักฐานของการทดลอง',
    '',
    sequence,
    'สำรวจ Media และ Timeline ของโปรเจกต์นี้ เลือกภาพสาธิตและเทคที่พูดจบความ ตัดเทคซ้ำ คำผิด และเสียงบอกบทที่ตรวจยืนยันได้',
    'ตรวจผลจากภาพและคำพูดต้นฉบับ เก็บเงื่อนไข คำบอกระดับ และข้อจำกัดที่มีผลต่อความหมาย หากผลยังไม่ชัดให้รายงานและถามก่อนเลือกช่วงสรุป',
    'ให้ซับตรงกับภาพและคำพูด ใช้ preset เครื่องหมาย-อย. และหมายเหตุ SOP ที่เกี่ยวข้องกับสินค้าปัจจุบัน',
    'ส่งแผนพร้อมชื่อไฟล์ ช่วงต้นฉบับ ลำดับเรื่อง เหตุผลที่เลือก และรายการที่ยังต้องยืนยัน',
    willEdit
      ? 'เมื่อแผนและ staging ผ่าน ให้สำรอง ตรวจ fingerprint เขียน native draft และอ่านผลกลับ พร้อมรายงานสิ่งที่ต้อง QC ใน CapCut'
      : 'หยุดที่แผน ห้ามเขียน native draft',
    'ทำผ่านไฟล์เท่านั้น ห้ามเปิด ปิด หรือควบคุม CapCut'
  ];
  output.textContent = lines.join('\n');
  result.hidden = false;
  document.querySelector('#result-title').focus();
});
