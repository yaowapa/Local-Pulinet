# 🏛 Local Knowledge Hub
**ฐานข้อมูลภูมิปัญญาท้องถิ่นไทย** — รวมบทความจาก 20 มหาวิทยาลัยทั่วประเทศไทย

---

## 📁 โครงสร้างไฟล์

```
LocalHub/
├── index.html              ← เว็บหลัก (ทั้งหมดอยู่ในไฟล์นี้)
├── admin.html              ← หน้า Admin Panel
├── scraper.py              ← Python scraper สำหรับดึงบทความอัตโนมัติ
├── sites.json              ← รายชื่อ 20 เว็บไซต์
├── .github/
│   └── workflows/
│       └── scrape.yml      ← GitHub Actions (รันอัตโนมัติทุกวัน)
└── README.md               ← คู่มือนี้
```

---

## 🚀 วิธีเผยแพร่เว็บ

### ตัวเลือก A — GitHub Pages (ฟรี + อัตโนมัติ)

> เหมาะสำหรับผู้ที่ต้องการให้ scraper รันอัตโนมัติทุกวัน

**ขั้นตอน:**

1. **สร้าง GitHub Repository ใหม่**
   - ไปที่ [github.com/new](https://github.com/new)
   - ตั้งชื่อ เช่น `local-knowledge-hub`
   - เลือก **Public** (GitHub Pages ฟรีเฉพาะ Public)
   - กด **Create repository**

2. **อัปโหลดไฟล์ทั้งหมด**
   - บน GitHub: กด **Add file → Upload files**
   - ลากโฟลเดอร์ `LocalHub/` ทั้งหมดขึ้นไป (รวมโฟลเดอร์ `.github/`)
   - กด **Commit changes**

3. **เปิด GitHub Pages**
   - ไปที่ **Settings** ของ repository
   - เลือกเมนู **Pages** (ด้านซ้าย)
   - ใต้ **Source** เลือก: `Deploy from a branch`
   - Branch: `main` / Folder: `/ (root)`
   - กด **Save**
   - รอ 2–3 นาที → เว็บจะพร้อมที่ `https://username.github.io/local-knowledge-hub/`

4. **เปิดใช้งาน GitHub Actions**
   - ไปที่แท็บ **Actions** ของ repository
   - ถ้ามีข้อความขอเปิดใช้ Actions → กด **I understand my workflows, go ahead and enable them**
   - Scraper จะรันอัตโนมัติทุกวันเวลา 09:00 น. (ไทย)
   - รันด้วยตนเอง: Actions → `Auto Scrape` → **Run workflow**

---

### ตัวเลือก B — Netlify (ลากวางไฟล์ ง่ายที่สุด)

> เหมาะสำหรับผู้ที่ต้องการเผยแพร่เร็วโดยไม่ต้องใช้ Git

**ขั้นตอน:**

1. ไปที่ [app.netlify.com](https://app.netlify.com)
2. สร้างบัญชีฟรี (ใช้ Google/GitHub ได้)
3. หน้าแรกจะมีกล่อง **"Drag and drop your site folder here"**
4. ลากโฟลเดอร์ `LocalHub/` ทั้งโฟลเดอร์ไปวาง
5. รอ 30 วินาที → ได้ URL เช่น `https://amazing-name-123.netlify.app`
6. เปลี่ยนชื่อ URL ได้ที่: Site settings → Domain management → Options → Edit site name

> **หมายเหตุ:** Netlify ลากวางไม่รองรับ GitHub Actions
> ถ้าต้องการ scraper อัตโนมัติ ให้ใช้ GitHub Pages (ตัวเลือก A)
> หรืออัปเดตด้วยตนเองโดย: รัน `python scraper.py` แล้วลากวาง `index.html` ใหม่

---

## 🤖 วิธีรัน Scraper ด้วยตนเอง

```bash
# 1. ติดตั้ง Python (ถ้ายังไม่มี): python.org/downloads
# 2. ติดตั้ง dependencies
pip install requests beautifulsoup4

# 3. รัน scraper (ต้องรันในโฟลเดอร์ที่มี index.html)
cd LocalHub
python scraper.py
```

Scraper จะ:
- ดึงบทความใหม่จาก 20 เว็บไซต์
- ตรวจหาบทความซ้ำ (ไม่เพิ่มซ้ำ)
- อัปเดต `index.html` อัตโนมัติ

---

## 🛠 Admin Panel

เปิดไฟล์ `admin.html` ใน browser เพื่อ:
- เพิ่ม / แก้ไข / ลบบทความ
- ค้นหาและกรองบทความ
- Export JSON สำรองข้อมูล
- Import JSON จากไฟล์สำรอง
- ดาวน์โหลด `index.html` ที่อัปเดตแล้ว

> Admin Panel ทำงานแบบ client-side ทั้งหมด ไม่ต้องมี server

---

## 🌐 เว็บไซต์ที่เชื่อมต่อ (20 แห่ง)

| ภูมิภาค | เว็บไซต์ |
|---------|---------|
| **ภาคเหนือ** | CMU Digital Collections, MFU Chiang Rai, MJU Food, MJU Museum, UP Local, Lanna Info, SSD |
| **ภาคอีสาน** | KKU Archive, MSU Isan, Esan Info, ISANNARU, SUT Korat, Esan (UBRU) |
| **ภาคใต้** | PSU South, Pattani Heritage, WU Library |
| **ภาคกลาง** | STOU Nonthaburi, STOU Digital |
| **ภาคตะวันออก** | BUU Library |
| **ภาคตะวันตก** | Silpakorn West |

---

## 📊 ข้อมูลในระบบ

- บทความทั้งหมด: **105+ บทความ** (เพิ่มขึ้นทุกวัน)
- หมวดหมู่: อาหาร, ประเพณี, ศิลปะ, ภูมิปัญญา, สถานที่, ธรรมชาติ, วิจัย
- แผนที่: แสดงพิกัดบทความบนแผนที่ประเทศไทย
- Dashboard: สถิติต่อมหาวิทยาลัยและภูมิภาค

---

## ❓ คำถามที่พบบ่อย

**Q: GitHub Actions รันแล้วไม่มีบทความใหม่?**
A: ปกติ — หากเว็บต้นทางไม่ได้อัปเดต scraper จะข้ามและไม่ commit

**Q: Admin Panel บันทึกได้ไหมโดยไม่มี server?**
A: ได้ — กด "💾 บันทึก index.html" จะดาวน์โหลดไฟล์ใหม่ให้นำไปแทนที่ไฟล์เดิม

**Q: ต้องการเพิ่มเว็บไซต์ใหม่ทำอย่างไร?**
A: เพิ่ม object ใน `SITES_CONFIG` ใน `index.html` และเพิ่มใน `SCRAPE_STRATEGY` ใน `scraper.py`

**Q: scraper.py รันบน Windows ได้ไหม?**
A: ได้ — ต้องมี Python 3.8+ และรัน `pip install requests beautifulsoup4`

---

*สร้างด้วย Claude AI · Local Knowledge Hub v1.1*
