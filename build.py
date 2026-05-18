"""
build.py — PMR Site Visit Dashboard Builder
รัน: python build.py
output: index.html (GitHub Pages จะเสิร์ฟไฟล์นี้)
"""

import pandas as pd
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────
CSV_FILE   = "raw-data-site-visit.csv"   # ชื่อไฟล์ CSV ที่ upload ขึ้น GitHub
OUTPUT     = "index.html"
TODAY      = datetime.today()
TODAY_STR  = TODAY.strftime("%d/%m/%Y")
TODAY_TS   = pd.Timestamp(TODAY.date())

# ──────────────────────────────────────
#  LOAD & CLEAN
# ──────────────────────────────────────
print(f"[1/4] Loading {CSV_FILE}...")

try:
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
except FileNotFoundError:
    # ลองหา xlsx แทน
    xlsx = CSV_FILE.replace(".csv", ".xlsx")
    print(f"  CSV not found, trying {xlsx}...")
    df = pd.read_excel(xlsx)

print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")
print(f"  Columns: {df.columns.tolist()}")

print("[2/4] Cleaning data...")

# Status
def clean_status(x):
    s = str(x).strip()
    if "Complete" in s: return "Complete"
    if "On Process" in s: return "On Process"
    return "Unknown"

df["Status"] = df["Status (สถานะการแก้ไข)"].apply(clean_status)

# Level
def clean_level(x):
    s = str(x)
    if s in ["Red", "Yellow", "Green"]: return s
    return "ไม่ระบุ"

df["ระดับ"] = df["ระดับความสำคัญ"].apply(clean_level)

# Category
def clean_cat(x):
    s = str(x)
    cats = [
        ("งาน Landscape", "งาน Landscape"), ("งานระบบ", "งานระบบ"),
        ("งานความสะอาด", "งานความสะอาด"), ("งานสถาปัตย์", "งานสถาปัตย์"),
        ("งานเฟอร์นิเจอร์", "งานเฟอร์นิเจอร์"), ("งานป้าย", "งานป้าย"),
        ("งานสระว่ายน้ำ", "งานสระว่ายน้ำ"), ("งานแสงสว่าง", "งานแสงสว่าง"),
        ("งานรักษาความปลอดภัย", "งานรักษาความปลอดภัย"),
        ("งานบรรยากาศ", "งานบรรยากาศ"), ("สิ่งอำนวยความสะดวก", "สิ่งอำนวยความสะดวก"),
        ("พนักงาน", "พนักงาน"), ("Backyard", "Backyard"),
    ]
    for k, v in cats:
        if k in s: return v
    return "อื่นๆ"

df["หมวด"] = df["หมวด (เลือก Dropdown)"].apply(clean_cat)

# Dates
df["visit_date"]    = pd.to_datetime(df["วันที่เข้าตรวจ(ใส่ D/M/2026)"], errors="coerce")
df["due_date"]      = pd.to_datetime(df["Duedate(กำหนดการแล้วเสร็จ)"],   errors="coerce")
df["complete_date"] = pd.to_datetime(df["Completion Date(วันที่แล้วเสร็จ)"], errors="coerce")

# Filter valid years
valid = (df["visit_date"].dt.year >= 2025) & (df["visit_date"].dt.year <= 2027)
df = df[valid].copy()
print(f"  Valid rows after date filter: {len(df):,}")

# Clean other fields
df["BU"]           = df["BU"].fillna("ไม่ระบุ").astype(str)
df["project_name"] = df["project_name"].fillna("").astype(str)
df["IO_Code"]      = df["IO_Code"].fillna("").astype(str)

def clean_resp(x):
    s = str(x).strip()
    if s in ["nan", "None", "", "-", " -"]: return "ไม่ระบุ"
    if re.match(r"^\d", s): return "ไม่ระบุ"
    return s[:40]

def clean_insp(x):
    s = str(x).strip().replace("\t", "").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if s in ["nan", "None", ""]: return "ไม่ระบุ"
    return s[:50]

df["ผู้รับผิดชอบ"] = df["Responsibility(ผู้รับผิดชอบ เช่น PMR,HC)"].apply(clean_resp)
df["ผู้ตรวจ"]      = df["ผู้ตรวจ (ระบุชื่อ)"].apply(clean_insp)

# Overdue: On Process AND (due_date < today OR due_date blank)
df["is_overdue"] = (
    (df["Status"] == "On Process") &
    (df["due_date"].isna() | (df["due_date"] < TODAY_TS))
)

df["month"] = df["visit_date"].dt.to_period("M").astype(str)

# Build records
records = []
for _, row in df.iterrows():
    records.append({
        "io":   str(row["IO_Code"]),
        "proj": row["project_name"],
        "sk":   row["BU"],
        "dt":   row["visit_date"].strftime("%Y-%m-%d") if pd.notna(row["visit_date"]) else "",
        "ins":  row["ผู้ตรวจ"],
        "cat":  row["หมวด"],
        "area": str(row.get("Issue / Area(พื้นที่)", "")),
        "det":  str(row["หัวข้อรายละเอียดที่พบ"])[:120],
        "imp":  str(row["Improvement Detail(สิ่งที่ต้องแก้ไข/ปรับปรุง)"])[:100],
        "resp": row["ผู้รับผิดชอบ"],
        "lv":   row["ระดับ"],
        "due":  row["due_date"].strftime("%Y-%m-%d") if pd.notna(row["due_date"]) else "",
        "comp": row["complete_date"].strftime("%Y-%m-%d") if pd.notna(row["complete_date"]) else "",
        "st":   row["Status"],
        "ov":   bool(row["is_overdue"]),
        "mo":   row["month"],
        "prog": str(row.get("Details Progress", ""))[:80] if pd.notna(row.get("Details Progress")) else "",
    })

total     = len(records)
complete  = sum(1 for r in records if r["st"] == "Complete")
onprocess = sum(1 for r in records if r["st"] == "On Process")
overdue   = sum(1 for r in records if r["ov"])
print(f"  Total:{total:,}  Complete:{complete:,}  OnProcess:{onprocess:,}  Overdue:{overdue:,}")

data_json = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
print(f"  Data size: {len(data_json.encode())/1024:.0f} KB")

# ──────────────────────────────────────
#  LOAD TEMPLATE & INJECT
# ──────────────────────────────────────
print("[3/4] Building HTML...")

template_path = Path("template.html")
if not template_path.exists():
    print("ERROR: template.html not found!")
    sys.exit(1)

with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

# Inject data
html = html.replace("PLACEHOLDER_DATA", data_json)

# Inject build date
html = html.replace("PLACEHOLDER_DATE", TODAY_STR)

# ──────────────────────────────────────
#  SAVE
# ──────────────────────────────────────
print(f"[4/4] Saving {OUTPUT}...")
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = Path(OUTPUT).stat().st_size / 1024 / 1024
print(f"  Done! {OUTPUT} = {size_mb:.1f} MB")
print(f"  Built at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
