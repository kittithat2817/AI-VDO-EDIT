# ข้อจำกัดการเลือกเนื้อหาและซับ

อ่านเมื่อมีเทคซ้ำ เสียงบอกบท ตอนจบที่ผู้ใช้ระบุ หรือ caption profile เพิ่มใน story-plan ได้:

```json
{
  "editorial_constraints": {
    "require_speaker_review": true,
    "excluded_spans": [{"asset_id":"source-id","source_in":10,"source_out":12,"reason":"production prompt","evidence":"source/user/frame/audio review reference"}],
    "protected_ending": {"asset_id":"source-id","source_in":50,"source_out":52,"required_text":"ข้อความปิดที่ผู้ใช้กำหนด","evidence":"original-media review reference"}
  },
  "speaker_review": [{"asset_id":"source-id","source_in":12,"source_out":20,"role":"presenter","evidence":"วิธีตรวจและข้อจำกัดที่ทำจริง"}],
  "caption_profile": "path/to/user-selected-profile.json"
}
```

ช่วงพูดที่เลือกต้องอยู่ภายในช่วง review บทบาท presenter/content_guest ที่มีหลักฐาน เมื่อตั้ง require_speaker_review การแยกเสียงพูดสองคนไม่เท่ากับทราบบทบาท ใช้บริบท เสียง/ภาพ และข้อมูลจากผู้ใช้ประกอบ ไม่อนุมานตัวตนจาก ASR หรือความดังเพียงอย่างเดียว ไม่ลบผู้พูดร่วมที่เป็นเนื้อหาจริง ช่วงไม่แน่ใจเก็บเป็น uncertainty แทนการติดป้ายยืนยัน

excluded_spans เป็น source seconds ตาม inventory ที่ห้าม primary beats ทับ protected_ending ต้องมีเสียงต้นฉบับครบอยู่ใน beat สุดท้าย ไม่ใช่แค่สรุปมีคำ CTA เก็บข้อความปิด/เวลาของแต่ละงานใน job state ไม่ฝังเป็นคำปิดทุกคอนเทนต์

แยก transcript สำหรับวิเคราะห์ที่เก็บเต็ม ออกจาก display cues ที่ผู้ใช้เลือก full หรือ selective ในโหมด selective ให้แต่ละ cue มี purpose, role (main/keyword/sop), text, start/end และ source reference profile กำหนด target_words/max_words และ terms ของชื่อเฉพาะ คำสำคัญหนึ่งคำไม่ใช่การทำซับทุกคำทีละคำ คงคำปฏิเสธ/เงื่อนไขและหมายเหตุ SOP ที่ต้องครบ

ตรวจซับด้วย `scripts/validate_captions.py cues.json profile.json` ต้องมี dependency ตาม `scripts/requirements.txt` ตัวตรวจใช้ PyThaiNLP newmm และพจนานุกรมศัพท์ที่ระบุ ไม่ใช้ช่องว่าง/ASR subword เป็นจำนวนคำ การผ่านจำนวนคำไม่รับรองความกว้าง/เวลาอ่าน/การเลือกสาร ต้องตรวจแยก

หลังเขียน draft ใช้ `scripts/verify_native_edit.py draft.json inventory.json story-plan.json --timebase <หน่วยต่อวินาทีที่ตรวจแล้ว> --fps <fps จริง>` โดยใส่ native_primary_track_id ใน plan เพื่อเทียบ source identity, source/target range และปลายแทร็กหลัก ไม่ใช้ duration ของ overlay แทนตอนจบเสียงพูด ตัวตรวจไม่ยืนยัน speaker identity, คำพูดจริง หรือ native playback; source review และ validate_plan ต้องผ่านก่อน


## เลือกเทคที่จบความและต่อเรื่องได้

ใช้หน่วย **ประเด็นที่พูดจบ** เพื่อเทียบเทค แล้วจึงหาขอบตัดระดับคำ การเริ่มด้วยคำคล้ายกัน การเปลี่ยนคำกลางประโยค และการกลับมาพูดสารเดิมข้ามคัตเป็นเหตุให้ตรวจต้นฉบับพร้อมบริบทก่อน–หลัง แม้ ASR รวมเป็นประโยคเดียวก็ยังต้องตรวจเมื่อมี QC หรือหลักฐานขัดกัน

แยกสามกรณี: (1) การลองพูด/แก้คำซึ่งถูกเทคสมบูรณ์แทนที่ (2) คำถาม–คำตอบหรือประเด็นใหม่ที่มีหน้าที่ต่างกัน (3) การย้ำโดยตั้งใจ เก็บสองกรณีหลังด้วยเหตุผลเฉพาะสาร ห้ามใช้ป้าย hook/question/CTA หรือความถูกคนของเสียงเป็นเหตุผลว่าต้องเก็บ เมื่อผู้ใช้ QC ว่าทั้งสองช่วงเป็นเทคของสารเดียวกัน ให้ใช้ข้อมูลนั้นแก้การจัดประเภทเดิม

เทค `complete` ต้องมีประธาน/สิ่งอ้างถึงที่เข้าใจได้ คำสำคัญและเงื่อนไขครบ จบสาร และต่อช่วงถัดไปโดยไม่ย้อนเริ่มสารเดิม การมีคำสุดท้ายหรือ ASR อ่านลื่นไม่พิสูจน์เกณฑ์นี้ เลือกตาม QC ที่ชัดเจนและความครบก่อน; `last_complete` เป็นตัวตัดสินระหว่างเทคที่ผ่านแล้ว เก็บเหตุผล override เมื่อใช้เทคก่อน ผู้ใช้ระบุ timecode เป็นจุดค้นหา ให้แปลงด้วย FPS จริงและจับคู่คำพูด/ไฟล์ก่อนย้อนหาต้นประโยค ไม่เริ่มตัดที่ timecode กลางคำ

บันทึก `retake_groups`: id ไม่ซ้ำ, asset_id, source_in/out ของบริเวณทางเลือก, candidates (id, source_in/out, status: restart/complete/intentional_repetition, evidence), selected_candidate, selection_reason, policy และ override_reason ถ้ามี เก็บ candidate เท่าประเด็นที่เป็นทางเลือกกัน; บทนำที่ให้บริบทเฉพาะ เช่นตัวบุคคลหรือกลุ่มคน แยกเก็บก่อนรอบสมบูรณ์ อย่ารวมบทนำที่จำเป็นลงในช่วงห้ามใช้ กลุ่มที่มีเนื้อหาอื่นแทรกให้แยกช่วงตรวจเพื่อไม่ห้ามเนื้อหานั้นโดยปริยาย

ช่วงที่ใช้ต้องครอบคลุม candidate ที่เลือกครบ ส่งรอบที่ตัดออกเป็น excluded_spans พร้อมหลักฐาน ตัวตรวจ native ตรวจส่วนของ candidate ที่ไม่เลือกนอกช่วงที่เลือกบนทุกแทร็กที่มีเสียงได้ด้วย จึงไม่พึ่งการคัดลอก exclusion เพียงอย่างเดียว เก็บชื่อคลิป ประโยค เวลา และคำปิดของแต่ละงานใน job state

CTA เปรียบเทียบเป็นสารเดียวกันได้แม้รอบแรกเป็นวิธีสั่งและรอบหลังเป็นการยืนยันของแท้ เลือกรอบที่ตอบบรีฟครบ ตรวจแยกว่าช่องทางซื้อ คำชี้ภาพ คำเชิญชวน และเสียงปิดยังมีหลักฐานรองรับจากเสียงหรือสื่อเดิม ถ้าตัดเสียงเทคเก่าแล้วข้อความช่องทางซื้อยังจำเป็น ให้ย้ายข้อความ/ภาพเดิมไปตอน CTA ที่เก็บ ไม่สร้างคำพูดใหม่และไม่ถือว่าการเก็บชื่อสินค้าอย่างเดียวรักษา CTA ครบ

### บันทึกทบทวนเมื่อแก้ QC ความหมาย/เทคซ้ำ

ตั้ง `editorial_constraints.require_content_review: true` และเก็บ `content_review` หนึ่งรายการต่อ beat ที่เลือก (รวมภาพที่เป็น primary beat):

```json
{"beat_id":"beat-02","asset_id":"source-id","source_in":20,"source_out":24,
 "decision":"selected_take","meaning":"สารที่เทคนี้สื่อครบ",
 "evidence":"QC ผู้ใช้ + บริบทต้นฉบับ; ระบุวิธีตรวจและข้อจำกัดจริง",
 "reason":"รอบก่อนเป็นการเริ่มสารเดียวกันใหม่; รอบนี้รักษาเงื่อนไขครบ",
 "retake_group_ids":["thought-01"],"next_beat_id":"beat-03",
 "join_reason":"ระบุว่าเนื้อหาถัดไปเพิ่มอะไรและทำไมไม่ใช่เริ่มสารเดิมซ้ำ"}
```

decision เป็น selected_take / keep_distinct / intentional_repetition / non_speech; รายการสุดท้ายมี next_beat_id null และเหตุผลการจบ รายการต้องผูก asset/range และลำดับล่าสุด ไม่คัดลอกเหตุผลเหมือนกันทุก beat กลุ่มที่อ้างต้องตรงกับ retake_groups ที่ทับช่วงนั้น เมื่อเปลี่ยนช่วง/ลำดับต้องทบทวนใหม่ รวมกรณีคล้ายกันทั่ว selected timeline ไม่อ้างว่าตรวจทั้งคลิปจากการตรวจเฉพาะจุดแจ้ง

ถ้าจุดไม่แน่ใจไม่กระทบสารหลัก ให้จัดส่วนที่ยืนยันได้ก่อนและเก็บข้อจำกัด แยก uncertainty ของช่วงที่ไม่เลือกออกจากช่วงที่ส่งตัด ถ้าตัดสินความหมายหลักไม่ได้ให้หยุดเฉพาะส่วนนั้นและถาม ตัวตรวจยืนยันว่ามีบันทึกครบและผูกถูกช่วง **ไม่รับรองว่าการตีความเนื้อหาถูกต้อง** รายงานการฟังจริง, ASR, หลักฐานผู้ใช้ และการตรวจไฟล์แยกกัน

## Layout เมื่อบรีฟกำหนด

profile ที่เลือก one-line ใช้ `max_lines: 1`, `require_layout_evidence: true`, `shared_caption_anchor: true` cues มี layout.text, method, width, available_width, estimated_lines ซึ่งต้องวัดจากข้อความและฟอนต์ที่ใช้จริง ใช้ Thai shaping และรักษาพื้นที่ปลอดภัย/ขนาดอ่านง่าย; ไม่ใช้จำนวนคำหรือการไม่มี newline แทนผลแสดงบรรทัด อ้างอิง cue ที่ผู้ใช้ QC ว่าแสดงถูกได้โดยรักษากล่อง/ฟอนต์/scale และวัดความกว้างแบบเปรียบเทียบ เก็บข้อจำกัดว่าเป็นการประเมิน layout ไม่ใช่ native render

ส่ง native_caption_layout ใน plan: anchor x/y, track_ids, static_anchor และ cues ที่ bind segment_id, text, font_size, scale, line_max_width กับผลวัด เมื่อ static_anchor=true ต้องไม่มี material animation ที่ยังไม่ได้พิสูจน์ว่าไม่เคลื่อนตำแหน่ง ซับหลักและ keyword ใช้ anchor เดียวกันและไม่ทับเวลา SOP อยู่นอกชุดนี้และรักษาข้อความเต็ม หลังแก้ข้อความ/ฟอนต์/scale ต้องวัดใหม่ก่อนอ่าน native กลับ

ตัวตรวจ retake ต้องรักษา candidate ที่เลือกครบทั้งช่วง ไม่มีช่องว่างภายใน; native layout binding เก็บ material_fields ของ font_path/spacing/box/preset, content_styles และ target_timerange เพื่อจับการเปลี่ยนฟอนต์ สี หรือเวลา หลังวัดแล้ว static_anchor ต้องไม่มี position keyframes ที่ยังไม่ตรวจ
