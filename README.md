# PMR Site Visit Dashboard

Dashboard แสดงผลข้อมูล Site Visit โครงการ PLUS+ Property

🔗 **URL:** https://penyarakpl-arch.github.io/pm-sitevisit-dashboard

---

## 📁 โครงสร้างไฟล์

```
pm-sitevisit-dashboard/
├── raw-data-site-visit.csv   ← ไฟล์ข้อมูล (upload ทับทุกครั้งที่อัปเดต)
├── template.html              ← โครงสร้าง dashboard (ไม่ต้องแก้)
├── build.py                   ← script แปลง CSV → HTML (ไม่ต้องแก้)
├── requirements.txt           ← Python packages (ไม่ต้องแก้)
├── index.html                 ← output (GitHub สร้างให้อัตโนมัติ)
└── .github/workflows/
    └── deploy.yml             ← GitHub Actions config (ไม่ต้องแก้)
```

---

## 🔄 วิธีอัปเดตข้อมูล (ทำทุกครั้งที่มีข้อมูลใหม่)

### ขั้นตอน 1 — Export CSV จาก Power BI
1. เปิด Power BI Desktop → Refresh ข้อมูล
2. Export → บันทึกเป็น **`raw-data-site-visit.csv`** (ชื่อต้องตรงนี้)

### ขั้นตอน 2 — Upload ขึ้น GitHub
1. เปิด https://github.com/penyarakpl-arch/pm-sitevisit-dashboard
2. คลิกที่ไฟล์ **`raw-data-site-visit.csv`**
3. กดไอคอน ✏️ (Edit) ที่มุมขวาบน → แล้วกด **"Upload file"**  
   หรือ ลากไฟล์ใหม่มาวางทับในหน้า repo ได้เลย
4. เลื่อนลงล่าง → กด **"Commit changes"**

### ขั้นตอน 3 — รอ Build อัตโนมัติ
- GitHub Actions จะรันอัตโนมัติทันที (~2 นาที)
- ดูสถานะได้ที่ tab **"Actions"** — ✅ = สำเร็จ

### ขั้นตอน 4 — เปิด Dashboard
- เข้า URL: https://penyarakpl-arch.github.io/pm-sitevisit-dashboard
- กด Ctrl+Shift+R เพื่อ refresh cache

---

## 🛠️ ตั้งค่าครั้งแรก (ทำครั้งเดียว)

### 1. เปิดใช้ GitHub Pages
1. ไปที่ **Settings** (แถบเมนูบน repo)
2. เลือก **Pages** (เมนูซ้าย)
3. Source → เลือก **"GitHub Actions"**
4. กด Save

### 2. Upload ไฟล์ทั้งหมด
Upload ไฟล์เหล่านี้ขึ้น repo:
- `raw-data-site-visit.csv`
- `template.html`
- `build.py`
- `requirements.txt`
- `.github/workflows/deploy.yml`

---

## ❓ แก้ปัญหาเบื้องต้น

| ปัญหา | วิธีแก้ |
|---|---|
| Actions ❌ failed | คลิก Actions → ดู error log → แจ้ง Claude |
| Dashboard ไม่อัปเดต | กด Ctrl+Shift+R หรือเปิด incognito |
| ข้อมูลไม่ครบ | ตรวจสอบชื่อ column ใน CSV ว่าตรงกับเดิม |
| ไฟล์ CSV ชื่อผิด | ต้องชื่อ `raw-data-site-visit.csv` เท่านั้น |
