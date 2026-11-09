# มาตรฐานถอดเสียงร่วม

ใช้กับ planner, editor และ subtitles เมื่อต้องสร้าง transcript ใหม่ ใช้ FFmpeg ดึงแทร็กเสียงไปถอดในเครื่องและเก็บผลพร้อมเวลาระดับคำ คำสั่งอยู่ใน `scripts/transcribe_local.py` ของ `capcut-story-planner`

| สภาพแวดล้อม | เครื่องมือที่ใช้ |
| --- | --- |
| Mac Apple Silicon ที่เข้าถึง Metal ได้ | MLX Whisper `large-v3` เส้นทางหลักตามผลตรวจจากงานไทยที่ผ่านมา |
| เครื่องที่ไม่ใช่ Mac Apple Silicon | Faster Whisper `large-v3` บน CPU แบบ `int8` |
| Mac Apple Silicon ที่ใช้ Metal ไม่ได้ | รายงานสาเหตุและขอให้ผู้ใช้เลือกเส้นทาง CPU แล้วจึงใช้ `--cpu` |

สคริปต์กำหนดรุ่นและ revision ของโมเดลไว้ ถ้าเครื่องมือหรือโมเดลขาด ให้หยุดขั้นถอดเสียงและแจ้งวิธีเตรียมเครื่อง การเปลี่ยนเครื่องมือหรือใช้บริการภายนอกต้องได้รับอนุญาตสำหรับงานนั้น Thonburian ใช้เป็นหลักฐานเสริมด้านคำพูดได้เมื่อมีผลถอดที่ตรงกับต้นฉบับ ตรวจเวลาและบทบาทผู้พูดกับเสียงและภาพ โดยเฉพาะเสียงทีมงานหรือเสียงพูดทับ

## เตรียมเครื่องและรัน

ติดตั้ง Python 3.12 และ FFmpeg ให้เรียกจาก PATH ได้ สร้าง virtual environment แล้วใช้ Python ของ environment นั้นตามคำสั่งด้านล่าง รันจากราก repo หรือใช้พาธจริงของสกิลที่ติดตั้ง ในเครื่องที่มีหลายชุดสกิล ให้ทั้งสามสกิลอ้างโฟลเดอร์ planner ฉบับเดียวกัน

```sh
# Apple Silicon
python -m pip install "mlx-whisper==0.4.3" "mlx==0.32.4" "huggingface-hub==2.4.0"

# เส้นทาง CPU
python -m pip install "faster-whisper==1.2.1" "ctranslate2==4.8.5" "huggingface-hub==2.4.0"
```

```sh
python skills/capcut-story-planner/scripts/transcribe_local.py prepare
python skills/capcut-story-planner/scripts/transcribe_local.py check
python skills/capcut-story-planner/scripts/transcribe_local.py run clip.mov transcript.json --language th
```

`prepare` ดาวน์โหลดเฉพาะไฟล์โมเดล ส่วน `check` และ `run` ใช้โมเดลจากแคช ใน Apple Silicon ที่เลือก CPU ให้ใส่ `--cpu` ก่อนชื่อคำสั่งย่อยทั้งสามคำสั่ง เว้น `--language` ถ้ายังไม่ทราบภาษา ใช้ `--audio-stream` เพื่อระบุแทร็กที่ต้องการ ค่าเริ่มต้นคือแทร็กเสียงแรก ควรลองกับคลิปสั้นที่รู้คำพูดก่อนทำงานจริง

## ใช้ transcript กับงานตัดและซับ

- เก็บผลดิบแยกจากข้อความซับและบันทึกแก้คำ ผลมีชื่อเครื่องมือ รุ่นโมเดลและ revision, SHA-256 ของต้นฉบับ, เลขแทร็ก และช่วงเวลาเป็นวินาทีจากต้นแทร็กเสียง ตรวจข้อมูลเหล่านี้ก่อนใช้ผลเดิม
- ตรวจเวลาเริ่มของแทร็กเทียบกับภาพด้วยข้อมูลสื่อ ถ้าใช้ไฟล์เสียงที่ตัดออกมาเฉพาะช่วง ให้บันทึก offset ไว้ แล้วจับคู่ผ่าน source in/out, speed และจุดตัดของ Timeline ล่าสุด
- ใช้เวลา ASR เป็นจุดหา ฟังจริงที่ต้นและท้ายคำก่อนตัดหรือวางซับ หากผลว่างหรือคำไม่ชัด ให้ตรวจเสียงจริงก่อนสรุปว่าช่วงนั้นไม่มีคำพูด
