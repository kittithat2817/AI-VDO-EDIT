const form = document.querySelector('#bofu-form');
const product = document.querySelector('#product');
const project = document.querySelector('#project');
const offer = document.querySelector('#offer');
const cta = document.querySelector('#cta');
const scope = document.querySelector('#scope');
const demoNote = document.querySelector('#demo-note');
const result = document.querySelector('#bofu-result');
const output = document.querySelector('#bofu-prompt');
const requiredFields = [product, project, offer, cta];

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
  product.value = 'สินค้า A (สมมติ)';
  project.value = 'คลิปโปร A / แนวตั้ง';
  offer.value = 'ซื้อ 2 แถม 1 วันที่ 1–3 ธันวาคม 2569 เฉพาะออเดอร์ในไลฟ์';
  cta.value = 'กดตะกร้าสินค้าในไลฟ์ของร้าน';
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
  const pace = form.elements.pace.value;
  const sequence = pace === 'fast'
    ? 'เข้าโปรไว: เปิดด้วยฮุคที่โยงเหตุผลซื้อ → เข้าโปรและเงื่อนไข → ชวนซื้อทันที'
    : 'เก็บบริบท: เปิดด้วยมุกหรือสถานการณ์ → เก็บบริบทและเหตุผลซื้อเท่าที่จำเป็น → เข้าโปรและเงื่อนไข → ชวนซื้อ';
  const lines = [
    ...(isDemo ? ['ตัวอย่างสมมติเพื่อฝึกดูคำสั่ง ให้หยุดที่แผนตัวอย่างและห้ามแก้โปรเจกต์จริง', ''] : []),
    willEdit
      ? 'ใช้ $capcut-story-planner แล้วส่งต่อ $capcut-script-edit วางแผนและตัดคลิปโปรโมชัน BOFU'
      : 'ใช้ $capcut-story-planner วางแผนคลิปโปรโมชัน BOFU อย่างเดียว',
    `โปรเจกต์และ Timeline: ${project.value.trim()}`,
    `สินค้า: ${product.value.trim()}`,
    `ข้อเสนอ วันโปร และเงื่อนไข: ${offer.value.trim()}`,
    `CTA: ${cta.value.trim()}`,
    '',
    sequence,
    'สำรวจ Media และ Timeline ของโปรเจกต์นี้ เลือกเทคที่พูดจบความ ตัดเทคซ้ำ คำผิด และเสียงบอกบทที่ตรวจยืนยันได้',
    'ตรวจวันโปร ตัวเลข เงื่อนไข และช่องทางซื้อกับข้อมูลข้างต้น ถ้าขัดกันหรือยังไม่ชัด ให้ถามก่อนเลือกช่วงที่เกี่ยวข้อง',
    'ให้คำพูด ซับ และ CTA สื่อข้อเสนอเดียวกัน เก็บข้อมูลที่จำเป็นต่อการตัดสินใจซื้อ ใช้ภาพและเสียงจากสื่อที่อนุญาต',
    'ใช้ preset เครื่องหมาย-อย. ตาม SOP และตรวจให้ตรงกับสินค้าปัจจุบัน',
    'ส่งแผนพร้อมชื่อไฟล์ ช่วงต้นฉบับ ลำดับเรื่อง และรายการที่ต้องยืนยัน',
    willEdit
      ? 'เมื่อแผนและ staging ผ่าน ให้สำรอง ตรวจ fingerprint เขียน native draft และอ่านผลกลับ พร้อมรายงานสิ่งที่ต้อง QC ใน CapCut'
      : 'หยุดที่แผน ห้ามเขียน native draft',
    'ทำผ่านไฟล์เท่านั้น ห้ามเปิด ปิด หรือควบคุม CapCut'
  ];
  output.textContent = lines.join('\n');
  result.hidden = false;
  document.querySelector('#result-title').focus();
});
