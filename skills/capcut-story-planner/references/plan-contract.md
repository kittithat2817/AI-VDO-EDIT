# สัญญาแผน v1

บันทึกไฟล์ในโฟลเดอร์งานแยกจากสกิล สื่ออยู่ที่ path เดิม เวลาทั้งหมดเป็น **วินาทีในไฟล์ต้นฉบับ**; `timeline_in/out` เป็นวินาทีในลำดับใหม่ที่ความเร็ว 1x ยังไม่ใส่ transition ซ้อนหรือ retime ถ้างานเดิมมี speed/reverse/compound ต้อง resolve ให้ถึงต้นฉบับก่อน ไม่ใช้เวลา Timeline เดิมเป็น source time

## inventory.json

```json
{
  "version": 1,
  "project_id": "actual-project-id",
  "timeline_id": "actual-active-timeline-id",
  "coverage": {"media": true, "timeline": true},
  "assets": [
    {
      "asset_id": "source-b",
      "path": "/absolute/path/b.mp4",
      "kind": "video",
      "duration_seconds": 42.1,
      "material_ids": ["actual-material-id"],
      "origins": ["media", "timeline"],
      "content_type": "speech",
      "timeline_uses": [{"source_in": 2.0, "source_out": 12.0, "original_timeline_in": 5.0, "original_timeline_out": 15.0}]
    }
  ]
}
```

หนึ่ง asset ต่อไฟล์ต้นฉบับจริง ใช้ `kind` video/audio/image และ `content_type` speech/broll/music/sfx/other รูปภาพให้ duration_seconds เป็น null เก็บ material IDs ทุกตัวที่อ้างไฟล์เดียวกัน สำหรับแผนอย่างเดียว อนุญาตให้ assets เก็บ identity/path/duration ที่ผู้ใช้ยืนยันแม้ยังเปิดไฟล์ไม่ได้ โดยระบุ availability เป็น unverified และ provenance ว่ามาจากผู้ใช้ การผ่านโครงสร้างไม่แปลว่าตรวจไฟล์จริงแล้ว ส่วนรายการที่ยัง resolve identity/path/duration ไม่ได้ให้เก็บใน unresolved_assets พร้อมเหตุผลและ material IDs อย่าสร้าง path/duration สมมติให้แทน หากยังสำรวจบัญชีสื่อบางส่วนไม่ได้ ให้ coverage ส่วนนั้น false และระบุ discovery_notes ไม่อ้างว่าครบ

หาก origins มี timeline ให้เก็บ timeline_uses ที่อ่านได้จริง หากยังอ่านตำแหน่งเดิมไม่ได้ ให้ระบุ timeline_uses_unknown: true แทนการสร้างเวลา รายการที่ถูกเลือกแต่ยังมีสถานะนี้ต้อง resolve ก่อน automatic handoff

## story-plan.json

```json
{
  "version": 1,
  "project_id": "actual-project-id",
  "profile": "general",
  "goal": "ผู้ชมเข้าใจเหตุผลและคำตอบของประเด็นนี้",
  "status": "ready",
  "beats": [
    {
      "id": "beat-01",
      "role": "hook",
      "asset_id": "source-b",
      "source_in": 2.0,
      "source_out": 8.0,
      "timeline_in": 0.0,
      "timeline_out": 6.0,
      "summary": "สรุปสิ่งที่ช่วงนี้พูดหรือแสดง",
      "evidence": "transcript.json segment 3; original frame at 4.0s",
      "why_here": "เปิดคำถามหลักก่อนอธิบาย",
      "connects_to_next": "จบเรื่องด้วยคำตอบในช่วงเดียวกัน"
    }
  ],
  "requirements": [],
  "uncertainties": [],
  "omissions": [],
  "handoff": {"recipient": "capcut-script-edit", "mode": "automatic"}
}
```

- handoff.mode เป็น automatic สำหรับงานตัดต่อที่ขอให้ทำต่อ หรือ plan_only เมื่อผู้ใช้ขอแค่แผน โหมด plan_only จะไม่พร้อมเรียกสกิลตัดต่อ แม้ไฟล์และช่วงเวลาถูกต้อง
- ลำดับใน `beats` คือลำดับการเล่า จะเป็น B→C→A หรือ B ช่วงท้าย→B ช่วงต้นก็ได้ ไม่ sort ตามชื่อ/เวลาต้นฉบับ
- beat เป็นช่วงพูด/การกระทำหลักหนึ่งช่วง บทบาทใช้คำที่เหมาะกับงาน เช่น hook/context/explanation/demonstration/product/evidence/disclaimer/conclusion/cta ไม่ต้องมีครบทุกบทบาท
- `evidence` ระบุแหล่งตรวจได้จริง ไม่ใส่คำอ้างกว้าง ๆ ว่า “AI ตรวจแล้ว” `summary` เป็นคำสรุปของผู้วางแผน ไม่ใช่คำพูดอ้างตรงที่สร้างแทนต้นฉบับ
- แต่ละรอยต่ออธิบายเหตุผลต่อเนื่อง beat สุดท้ายอธิบายว่าจบสารอย่างไร `omissions` เก็บ asset/range ที่ข้ามพร้อมเหตุผล เมื่อมีการข้าม
- `status` ใช้ ready หรือ needs_core_clarification; `uncertainties` เป็นรายการ `{impact: "local" หรือ "core", description: "..."}` ปัญหาระดับ core ต้องชี้แจงก่อนส่งตัดต่อ ส่วน local เก็บไว้และจัดเรื่องส่วนอื่นต่อ
- ภาพ/เสียงประกอบเป็น asset ประเภทของตนเอง เก็บคำแนะนำวางประกอบใน `supporting_assets` ได้ แต่ไม่ใส่เพลง/ภาพนิ่งเป็น primary beat ของคลิปพูดเพื่อแทนคำพูดที่ไม่มี ตัวตรวจ v1 ตรวจเฉพาะ primary beats; สกิลตัดต่อต้องตรวจสื่อประกอบด้วย

## รายการ SOP

หนึ่งรายการต่อ requirement ที่ใช้: `{id, status, delivery, content?, asset_id?, source_note?}`

- status: satisfied / scheduled / missing / not_applicable
- delivery: text / media / spoken / none
- `scheduled + text` ต้องมี content จากข้อความ SOP/ผู้ใช้ที่ตรวจต้นทางแล้ว พร้อม source_note และผู้ตัดต่อเป็นผู้ใส่ข้อความจริง
- `satisfied` หรือ `scheduled` ที่ใช้ media/spoken ต้องระบุ asset_id ที่อยู่ใน inventory; ตรวจช่วงข้อความ/เสียงให้ตรงตามคำกล่าวด้วย
- missing ระบุ delivery none และเหตุผลใน source_note; เป็นรายการที่ต้องแก้ก่อนรายงานว่างานผ่าน SOP แต่ไม่ทำให้หยุดส่งเรื่องส่วนที่ชัดเจนไปจัดวาง
- required IDs ของ profile ต้องมีครบและใช้ not_applicable แทน missing ไม่ได้ ส่วน conditional ต้องตัดสินความเกี่ยวข้องจากงานและอธิบาย

`story-plan.md` เป็นฉบับอ่าน: เป้าคลิป, โครงที่เลือก, ตารางลำดับ/ไฟล์/เวลาเดิม/เวลาใหม่/หน้าที่/เหตุผล, ส่วนที่ข้าม, รายการ SOP, ความไม่แน่ใจ และสถานะการส่งต่อ ใช้ข้อมูลชุดเดียวกับ JSON

## ผลตัวตรวจ

`validate_plan.py inventory.json story-plan.json [--check-media]` พิมพ์ JSON และคืน exit code 0 เมื่อโครงสร้าง/การอ้างอิงผ่าน หรือ 1 เมื่อไม่ผ่าน

- `valid`: อ้างอิงและช่วงเวลาไม่ผิดสัญญา
- `handoff_ready`: valid, mode automatic, ตรวจไฟล์จริงด้วย --check-media แล้ว, สำรวจครบสองแหล่งและ resolve ตำแหน่ง Timeline ของช่วงที่เลือก, status ready และไม่มี uncertainty ระดับ core
- `sop_complete`: รายการ SOP ของ profile มีสถานะครบและไม่มี scheduled/missing แยกจากการมีไฟล์จริงหรือความถูกต้องของช่วงเวลา ไม่ใช่คำรับรองด้านการแพทย์หรือกฎหมาย
- `warnings`: ข้อที่ยังต้องทำหรือยืนยัน เช่นยังไม่ตรวจไฟล์จริง หรือยังมีข้อความรอใส่

`--check-media` ตรวจว่ามีไฟล์จริง และ ffprobe duration ของ primary sources ว่าครอบคลุม source range ไม่เปิด CapCut ไม่แก้ draft และไม่ส่งไฟล์ผ่านเครือข่าย

เมื่อมีเสียงบอกบท/เทคซ้ำ ประโยคปิดที่ต้องรักษา หรือโปรไฟล์ซับ อ่าน [editorial-contract.md](editorial-contract.md) เพื่อส่งข้อจำกัดที่ตัวตรวจและ editor ใช้จริง
