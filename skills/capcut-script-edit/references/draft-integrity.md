# ตรวจไฟล์ CapCut ก่อนและหลังแก้

อ่านก่อนแก้ native draft ผ่านไฟล์ คู่มือนี้เป็นเกณฑ์ตรวจ ไม่ใช่ตัวเขียน draft ที่รับรองทุกเวอร์ชัน ห้ามเปิดหรือควบคุม CapCut เพื่อทดสอบหรือแก้ปัญหา

## ค้นหาและระบุรูปแบบ

- เริ่มจากโฟลเดอร์ที่ผู้ใช้ระบุ หากจำเป็นจึงตรวจ local draft registry ในพื้นที่ข้อมูล CapCut ของผู้ใช้ ใช้ registry เป็น locator เท่านั้น ไม่ใช้รายการล่าสุด/รายการแรกเป็นเป้าหมายเอง ไม่ฝังพาธหรือชื่อโปรเจกต์จากเครื่องต้นทางเป็นค่าถาวร
- ตัวอย่างในเครื่องที่ตรวจแบบอ่านอย่างเดียวเมื่อ 2026-10-28 มี draft_content.json และไฟล์ประกอบ เช่น draft_meta_info.json, draft_agency_config.json, draft_biz_config.json, draft_virtual_store.json บางตัวอย่างอ่านเป็น UTF-8 JSON ได้ ข้อสังเกตนี้ไม่รับรองไฟล์ทั้งหมดหรือรุ่นปัจจุบัน
- ตัวอย่างมี tracks, materials, keyframes, relationships, duration, fps, canvas_config และ platform metadata ค่า version/new_version เป็นข้อมูล schema ไม่ใช่หลักฐานเวอร์ชันแอปที่ติดตั้งอยู่ และไม่ใช่ allowlist ความเข้ากันได้
- ตรวจไฟล์จริงก่อนเลือก parser เก็บ encoding และ fields ที่ไม่รู้จักไว้ หากอ่านไม่ได้/เข้ารหัส/ขาดโครงสร้างจำเป็น ให้หยุดขั้นเขียน ไม่เปลี่ยน version เพื่อบังคับให้เปิด ไม่เดา schema หรืออ้างว่าเปลี่ยนนามสกุลแล้วใช้ได้

## Timing และการอ้างอิง

- อ่าน tracks[].segments และ materials จาก draft จริง ตัวอย่างพบ segment fields เช่น material_id, extra_material_refs, keyframe_refs, common_keyframes, group_id, source_timerange, target_timerange, render_timerange, speed, clip, volume และ render_index; ใช้เฉพาะ fields ที่มีความหมายตรวจได้ในไฟล์นั้น
- ตรวจหน่วยเวลาจาก metadata/โครงสร้างที่เชื่อถือได้หรือเทียบช่วงที่รู้ความยาวจริง ค่าตัวอย่างสอดคล้องกับ microseconds แต่ยังไม่ยืนยันเป็นกฎทุกเวอร์ชัน ห้ามนำ Premiere ticks มาใช้หรือกำหนดตัวคูณจากขนาดตัวเลขอย่างเดียว
- เมื่อทราบหน่วยแล้วคำนวณแบบ integer/rational ตาม FPS และขอบเฟรมจริง ตรวจ duration บวก source bounds และความยาวสูงสุดของ target ranges รวม speed/gaps/repeats ที่เกี่ยวข้อง
- รักษา reference graph ตามชนิด field ที่อ่านได้: segments → materials, animation/speed/transition/audio fade/channel mapping และ keyframes/relationships ที่เกี่ยวข้อง สร้าง ID ใหม่เฉพาะวัตถุใหม่ที่ต้องมี identity และ remap ให้ครบ อย่า rewrite ทุก string ที่ดูคล้าย ID; external resource IDs ไม่จำเป็นต้องอยู่ใน local material table
- อย่าแก้ shared material จนคลิปอื่นหรือชุดซับอื่นเปลี่ยนตาม Clone เฉพาะโครงสร้างที่จำเป็นและเข้าใจแล้ว
- ตรวจพาธสื่อและเสียงจริง รักษา volume, mute/enable, channel mappings, fades และ speed ที่ไม่อยู่ในขอบเขต การมีไฟล์เสียงอยู่ไม่ได้พิสูจน์ว่าลิงก์เสียงใน draft ถูกต้อง

## อ่านและเขียนอย่างไม่ทับงานล่าสุด

1. บันทึก fingerprint ของไฟล์ทุกตัวที่จะเขียน และ snapshot เชิงความหมายของ tracks, segments, materials และสิ่งนอกขอบเขต เก็บ checkpoint แยกจากโปรไฟล์ใช้ซ้ำ
2. ตรวจว่ามีการเปลี่ยนไฟล์ระหว่างงานหรือมีหลักฐานว่าแอปกำลังแก้ draft นั้น หากมีความขัดแย้งให้หยุดเขียนและให้ผู้ใช้จัดการสถานะเอง ห้ามปิดแอปเองหรือทับงานที่ยังไม่บันทึก
3. สำรองชุดไฟล์ที่จะเปลี่ยนตามความสัมพันธ์ที่จำเป็น เว้นแต่ผู้ใช้สั่งไม่ต้องสำรอง เตรียม staging นอกโฟลเดอร์ live เสมอ
4. แก้เฉพาะ fields ที่เข้าใจ เปิดอ่าน staging กลับ ตรวจ identities, references ที่เปลี่ยน, ranges, paths และ diff นอกขอบเขต ไม่ serialize แล้วลบ fields ที่ไม่รู้จัก
5. เมื่อสร้างสำเนา draft ตรวจ identity, media refs และ metadata ของสำเนา การคัดลอกโฟลเดอร์เฉย ๆ ไม่ยืนยันว่า CapCut จะค้นพบหรือแสดงรายการนั้น ห้ามแก้ global registry ทั้งชุดเพื่อพยายามลงทะเบียนโดยไม่มี schema และขอบเขตที่ตรวจได้
6. หากต้องเปลี่ยนหลายไฟล์ จัดเป็นชุดที่สอดคล้องกันและมีแนวทางคืนค่าเมื่อเขียนไม่ครบ ไม่อ้างว่าหลายไฟล์เป็น atomic transaction ตรวจ fingerprint ซ้ำก่อนแทนที่ หากเปลี่ยนให้โหลดใหม่ ไม่ retry เขียนแบบตาบอด
7. อ่านผลจากดิสก์กลับ ตรวจความยาว สื่อ และ diff; การทดสอบ parse สำเร็จไม่ใช่หลักฐานว่าแอปเปิด เล่นเสียง หรือ render เอฟเฟกต์ได้ รายงานสถานะตามจริง

หากติดข้อจำกัด ให้รักษาไฟล์ต้นทางและส่งแผน/cue list/ผลวิเคราะห์ที่ทำได้ พร้อมระบุว่าไม่ได้แก้ส่วนใด ไม่เปลี่ยนไปควบคุมแอปหรือส่งพรีวิวภายนอกแทน native draft โดยไม่แจ้ง
