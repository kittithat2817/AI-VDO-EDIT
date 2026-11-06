# AI HERO VDO EDIT

สกิลสำหรับวางเรื่อง ตัดต่อ และตรวจ native draft ของ CapCut ผ่านไฟล์บนดิสก์ โดยไม่เปิด ปิด หรือควบคุมแอป

## สกิล

- [capcut-story-planner](skills/capcut-story-planner/SKILL.md): สำรวจสื่อ เลือกเทคที่จบความ เรียงเรื่อง และบันทึก source mapping กับเหตุผลของรอยต่อ
- [capcut-script-edit](skills/capcut-script-edit/SKILL.md): ตัดตามแผน สำรอง ตรวจ staging และ fingerprint ก่อนเขียน แล้วอ่าน native draft กลับตรวจ
- [capcut-subtitles](skills/capcut-subtitles/SKILL.md): จัดซับตามบรีฟ รองรับ selective captions และการตรวจหนึ่งบรรทัด

โปรไฟล์เฉพาะงานอยู่ที่ [hamhang-selective-captions.json](work/workflows/hamhang-selective-captions.json): เป้าหมาย 1–4 คำ สูงสุด 5 คำ, keyword หนึ่งคำ, ซับหลักและ keyword ใช้ตำแหน่งเดียวกัน และคงหมายเหตุ SOP ครบ

## ใช้งาน

ผู้ใช้ใหม่เริ่มจาก [SOP วางเรื่องและตัดต่อ CapCut ด้วย Codex](docs/capcut-ai-workflow-sop.md) พร้อมคำสั่งคัดลอกสำหรับขอแผน ตัดจริง และแก้ QC

คัดลอกโฟลเดอร์สกิลที่ต้องการจาก `skills/` ไปยังโฟลเดอร์สกิลของ Codex เช่น `~/.codex/skills/` โดยสำรองฉบับเดิมก่อนแทนที่ ติดตั้ง planner และ script-edit คู่กันเพื่อใช้เอกสารสัญญาร่วมกัน

ระบุโปรเจกต์ บรีฟ และ SOP ของงาน แล้วเรียก `capcut-story-planner` ตามด้วย `capcut-script-edit` ตรวจ source paths, FPS, timebase และเวอร์ชัน draft ใหม่ทุกงาน

## ตรวจสอบ

ต้องมี Python 3 และ `ffmpeg`/`ffprobe` สำหรับทดสอบและตรวจสื่อ

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/capcut-story-planner/scripts/requirements.txt
.venv/bin/python -m unittest discover -s skills/capcut-story-planner/tests -v
```

ตัวตรวจแยกสามส่วน: inventory + story-plan, caption cues + profile และ native draft readback มีการตรวจ retake ที่ไม่เลือก บันทึกทบทวนความหมายที่ผูกกับช่วงล่าสุด เสียงปิด และรูปแบบซับ

ผลตรวจไฟล์ไม่รับรองความถูกต้องของการตีความเสียงหรือการเล่น/render ใน CapCut ต้องแยกหลักฐาน ASR การฟังจริง และ QC ของผู้ใช้ในรายงาน

## ขอบเขตไฟล์ใน repository

เก็บสกิล สคริปต์ทดสอบ โปรไฟล์ และเอกสารที่ใช้ซ้ำได้ งานเฉพาะคลิปใน `.scratch/`, ภาพวิจัยใน `research/`, สื่อต้นฉบับ, native drafts, backups และ environments ไม่รวมใน repository
