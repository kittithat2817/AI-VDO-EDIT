# ส่งแผนให้ capcut-script-edit

อ่าน SKILL.md ของ `capcut-script-edit` ที่ติดตั้งจริงก่อนทำต่อ หากไม่มี Skill tool ให้เปิดไฟล์จาก skills catalog; ตำแหน่งในเครื่องต้นทางคือ `~/.codex/skills/capcut-script-edit/SKILL.md` อ่าน `references/draft-integrity.md` ของสกิลนั้นก่อนเขียน และอ่าน `references/reusable-workflow.md` เมื่อต้องเก็บโปรไฟล์ซีรีส์

## ขอบเขตการทำงาน

ทั้งการสำรวจและการตัดต่อทำผ่านไฟล์บนดิสก์เท่านั้น ห้ามเปิด ปิด หรือควบคุม CapCut รวม UI automation, keyboard/mouse, deep link, app launch, reload และคำสั่งแอปเบื้องหลัง ไม่ใช้ live API ที่ควบคุมแอปหรือ UI เป็น fallback เมื่อไฟล์อ่านไม่ได้

ผลส่งมอบหลักคือ native draft ของ CapCut ที่แก้ไขต่อได้ ไม่ใช่เฉพาะวิดีโอหรือโปรเจกต์โปรแกรมอื่น การเรียกสกิลตามบรีฟไม่เพิ่มขั้นรอ Approved ทุกงาน หาก schema อ่านไม่ได้/เข้ารหัส/ขาดต้นแบบที่ตรวจได้ ให้หยุดเฉพาะขั้นเขียนและส่งแผนกับสิ่งที่ตรวจได้ต่อ

## ชุดงานที่ส่งต่อ

สร้าง `editor-handoff.md` ในโฟลเดอร์งาน พร้อม:

- เป้าหมายคอนเทนต์ ประเภทคลิป ช่องทาง ความยาว และขอบเขตแก้ที่ผู้ใช้ระบุ
- project/draft path และ identity, active timeline, fingerprint/revision, schema/timebase/FPS ที่ตรวจได้จริง
- path ของ inventory, story-plan ทั้งสองฉบับ, transcripts และผล validation
- SOP/profile ที่ใช้ รายการข้อความ/สื่อที่ต้องเติม และ uncertainties
- ลำดับสารและเหตุผลของรอยต่อ พร้อมข้อกำหนดอัปเดต source→edited mapping เมื่อเวลาหรือช่วงที่ใช้เปลี่ยน

ส่งคำสั่งให้ `capcut-script-edit` ในบริบทเดียวกัน: “ใช้แผนนี้เป็นแผนวางเรื่อง จัด source ranges ตามลำดับ และตัดต่อ native draft ผ่านไฟล์ตาม SOP และบรีฟ โดยไม่ควบคุมแอป” อ่านสกิลและทำงานต่อจริง เมื่อผู้ใช้ขอแค่แผน ให้ใช้ handoff.mode เป็น plan_only และจบที่ชุดแผน

ส่ง editorial_constraints, speaker_review และ caption_profile พร้อมแผน ตรวจผล native กลับว่าไม่ชนช่วงห้ามใช้และคงเสียงปิดครบ เมื่อเลือกซับแบบ selective ให้สร้างเฉพาะสารจำเป็นและ keyword ตามโปรไฟล์ ไม่ใช้ transcript เต็มเป็น display cues

## ผูกหลายไฟล์และตรวจแผนกับเวอร์ชันล่าสุด

ก่อนเขียน ตรวจ draft ล่าสุดเทียบ fingerprint/checkpoint หากผู้ใช้แก้ Timeline แล้วให้จับคู่ใหม่จากไฟล์ล่าสุด ไม่ replay เวลาหรือ material IDs จากแผนเก่าโดยไม่ตรวจ รักษาบทบาทสื่อ/หลักการใน workflow profile แยกจาก job state ของงานนี้

ผูก primary/supporting assets กับไฟล์และ materials จริงตาม inventory ตรวจ source ranges, native time units, speed และ audio links บาง backend มี field clip แต่ใช้ไฟล์จาก segment แรกกับทุกช่วง จึงต้องตรวจ implementation หรือ draft ผลลัพธ์จริง ไม่ถือว่า ordered cuts.json รับรองหลายไฟล์ได้

ใช้โครงสร้างที่อ่านและตรวจได้ของ draft เป้าหมาย สร้าง material mapping ต่อไฟล์ รักษา unknown fields และ reference graph แล้วตรวจว่าลำดับ B→C→A ยังชี้ source คนละตัวตามแผน หากไม่มีวิธีเขียนที่รองรับ ให้ส่งแผนพร้อมข้อจำกัด ไม่ใช้ไฟล์แรกแทนทุกช่วง ไม่สร้าง draft ว่างหรือ effect payload ด้วย schema ที่เดา

## เขียนและตรวจผ่านไฟล์

สำรองตามขอบเขตและเตรียม staging นอก live draft ตรวจ ranges, material references, sync และ diff นอกขอบเขตก่อนแทนที่ ตรวจ fingerprint ซ้ำก่อนเขียนจริง หากไฟล์เปลี่ยนหรือมีความขัดแย้งกับงานที่แอปกำลังแก้ ให้หยุดเขียนและแจ้งสถานะให้ผู้ใช้จัดการ ไม่ปิดแอปเองหรือทับงานที่ยังไม่บันทึก

ข้อกำหนดเฉพาะงานและ SOP ที่ผู้ใช้เลือกใช้เป็นแนวตัดต่อภายในข้อจำกัด file-only ใช้ซับใหม่เป็นข้อความธรรมดาตามคำพูดและเวลา draft ล่าสุดตาม capcut-script-edit; งานซับละเอียดส่ง capcut-subtitles เมื่ออยู่ในขอบเขตที่ขอ ไม่สร้าง text template/animation เพื่อเลียนแบบตัวอย่างโดยปริยาย

หลังย่อ เปลี่ยนความเร็ว หรือใส่ transition อัปเดตเสียง กราฟิก และซับตาม mapping ของแต่ละช่วง ไม่เลื่อนทั้งหมดด้วย offset เดียวหากมีหลายจุดตัด รายการ SOP ที่ยัง missing ส่งเป็นงานคงค้างพร้อมผลส่วนที่ทำได้ ไม่อ้างว่าผ่าน SOP จนเติมและตรวจครบ

อ่าน draft ที่เขียนกลับ ตรวจ source material/range ของทุก segment, ความยาว, ช่องว่าง/ภาพดำที่ไม่ตั้งใจ, audio references, ข้อความกำกับและ diff นอกขอบเขต ส่ง path draft/โฟลเดอร์ ชื่องาน ความยาวจริง รายการแก้ ผลตรวจ และส่วนที่ยังไม่ยืนยัน

แยกสถานะว่าแผนพร้อม, เขียน draft แล้ว และตรวจไฟล์/สื่อแล้ว การ parse JSON ผ่านไม่ใช่การยืนยันว่า CapCut เปิด เล่น หรือ render เอฟเฟกต์ได้ สกิลนี้ไม่เปิดแอปเพื่อตรวจ พรีวิวภายนอกทำได้เฉพาะเมื่อผู้ใช้ขอและต้องระบุว่าเป็น external preview ที่ไม่รับรอง native effects; ไม่ใช้แทน native draft
