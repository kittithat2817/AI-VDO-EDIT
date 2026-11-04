# Issue tracker: Local Markdown

เก็บ issues และ specs ของโปรเจกต์เป็น Markdown ใน `.scratch/`

## รูปแบบไฟล์

- หนึ่งฟีเจอร์ต่อโฟลเดอร์: `.scratch/<feature-slug>/`
- Spec: `.scratch/<feature-slug>/spec.md`
- หนึ่งไฟล์ต่อ ticket:
  `.scratch/<feature-slug>/issues/<NN>-<slug>.md`
  เริ่มเลขจาก `01` ห้ามรวมทุก ticket ในไฟล์เดียว
- บันทึกสถานะด้วย `Status:` ใกล้ส่วนต้นของ issue
  ใช้ชื่อสถานะจาก `triage-labels.md`
- เพิ่มความคิดเห็นและประวัติการสนทนาท้ายไฟล์ใต้ `## Comments`

## เมื่อ skill สั่งเผยแพร่ไปยัง issue tracker

สร้างไฟล์ใน `.scratch/<feature-slug>/` พร้อมสร้างโฟลเดอร์ถ้าจำเป็น

## เมื่อ skill สั่งอ่าน ticket

อ่านไฟล์ตาม path หรือหมายเลข issue ที่ผู้ใช้ระบุ

## การทำงานของ wayfinder

- Map: `.scratch/<effort>/map.md`
  มีส่วน Notes / Decisions-so-far / Fog
- Ticket ย่อย: `.scratch/<effort>/issues/NN-<slug>.md`
  เริ่มเลขจาก `01` และเขียนคำถามในเนื้อหา
- ระบุ `Type:` เป็น research, prototype, grilling หรือ task
- ใช้ `Status: claimed` เมื่อรับงาน และ `Status: resolved` เมื่อเสร็จ
- ระบุงานที่ขวางด้วย `Blocked by: NN, NN`
  งานจะพร้อมเมื่อ ticket ที่อ้างถึงทั้งหมดเป็น resolved
- เลือกงานที่ยังเปิด ไม่มีงานขวาง และยังไม่มีผู้รับ เรียงตามเลข
- ก่อนเริ่มงาน ให้บันทึก `Status: claimed`
- เมื่อเสร็จ ให้เพิ่มคำตอบใต้ `## Answer` เปลี่ยนเป็น resolved
  และเพิ่มข้อสรุปพร้อมลิงก์ใน Decisions-so-far ของ map
