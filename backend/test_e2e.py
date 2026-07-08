"""端到端测试 - 精简版"""
import requests, json, sys, time, datetime

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0

def test(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")

# Wait for server
print("Waiting for server...")
for i in range(30):
    try:
        r = requests.get(f"{BASE}/docs", timeout=2)
        if r.status_code == 200:
            print("Server ready.\n")
            break
    except:
        time.sleep(1)
else:
    print("Server not responding!")
    sys.exit(1)

# === A1: Login ===
print("=== A1: Login ===")
r = requests.post(f"{BASE}/api/auth/login", json={"username": "admin", "password": "admin123"})
test("Login 200", r.status_code == 200, str(r.status_code))
token = r.json().get("token", "") if r.status_code == 200 else ""
test("Has token", bool(token))

r = requests.post(f"{BASE}/api/auth/login", json={"username": "admin", "password": "wrong"})
test("Wrong pwd -> 401", r.status_code == 401, str(r.status_code))

headers = {"Authorization": f"Bearer {token}"}

# === B1: Upload + Detect ===
print("\n=== B1: Upload + Detect ===")
TEST_IMG = "D:/code/yolo/dataset/images/Abyssinian_1.jpg"
with open(TEST_IMG, "rb") as f:
    r = requests.post(f"{BASE}/api/upload",
        files={"file": ("cat.jpg", f, "image/jpeg")},
        data={"location_id": 1}, headers=headers)
test("Upload 200", r.status_code == 200, f"status={r.status_code} body={r.text[:200]}")
if r.status_code == 200:
    d = r.json()
    test("Has image_url", bool(d.get("image_url")))
    test("Has animals list", isinstance(d.get("animals"), list))
    animals = d.get("animals", [])
    total = d.get("total", 0)
    img_url = d.get("image_url", "")
    if animals:
        a = animals[0]
        test("Has breed_cn", bool(a.get("breed_cn")))
        test("Has confidence", isinstance(a.get("confidence"), (int, float)))
        test("Has box", isinstance(a.get("box"), dict))
        print(f"    Detected: {a.get('breed_cn')} conf={a.get('confidence'):.4f}")
    else:
        print("    No animals detected")
else:
    animals, total, img_url = [], 0, ""

# === B2: Save ===
print("\n=== B2: Save ===")
if img_url and animals:
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    body = {
        "location_id": 1,
        "image_path": img_url.lstrip("/"),
        "detect_time": now,
        "result_json": json.dumps(animals, ensure_ascii=False),
        "total_animals": total,
    }
    r = requests.post(f"{BASE}/api/detections", json=body, headers=headers)
    test("Save 201", r.status_code == 201, f"status={r.status_code} body={r.text[:200]}")
    det_id = r.json().get("id") if r.status_code == 201 else None
    if det_id:
        print(f"    saved id={det_id}")
else:
    det_id = None
    print("    SKIP (no B1 result)")

# === B3/B4: List + Detail ===
print("\n=== B3/B4: List + Detail ===")
r = requests.get(f"{BASE}/api/detections", headers=headers)
test("List 200", r.status_code == 200)
test("Has items", "items" in r.json())
test("Has total", "total" in r.json())
print(f"    total={r.json().get('total', 0)} records")

if det_id:
    r = requests.get(f"{BASE}/api/detections/{det_id}", headers=headers)
    test("Detail 200", r.status_code == 200)

# === B6-B9: Locations ===
print("\n=== B6-B9: Locations ===")
r = requests.get(f"{BASE}/api/locations", headers=headers)
test("List locations 200", r.status_code == 200)
test("5 locations", len(r.json().get("items", [])) == 5)

r = requests.post(f"{BASE}/api/locations", json={"name": "test_loc"}, headers=headers)
test("Create location 201", r.status_code == 201)
loc_id = r.json().get("id") if r.status_code == 201 else None

if loc_id:
    r = requests.put(f"{BASE}/api/locations/{loc_id}", json={"name": "test_loc_v2"}, headers=headers)
    test("Update location 200", r.status_code == 200)
    r = requests.delete(f"{BASE}/api/locations/{loc_id}", headers=headers)
    test("Delete location 200", r.status_code == 200)

# === B11-B13: Safety Tips ===
print("\n=== B11-B13: Safety Tips ===")
r = requests.post(f"{BASE}/api/safety-tips",
    json={"location_id": 1, "title": "Test Tip", "content": "Be careful!"}, headers=headers)
test("Create tip 201", r.status_code == 201)
tip_id = r.json().get("id") if r.status_code == 201 else None

if tip_id:
    # Publish
    r = requests.put(f"{BASE}/api/safety-tips/{tip_id}/status",
        json={"status": "published"}, headers=headers)
    test("Publish 200", r.status_code == 200, f"status={r.status_code}")

    # Verify location.safety_tip synced
    r = requests.get(f"{BASE}/api/locations", headers=headers)
    loc1 = [l for l in r.json()["items"] if l["id"] == 1][0]
    test("location.safety_tip synced", loc1["safety_tip"] == "Be careful!",
         f"got: {loc1['safety_tip']}")

    # Archive
    r = requests.put(f"{BASE}/api/safety-tips/{tip_id}/status",
        json={"status": "archived"}, headers=headers)
    test("Archive 200", r.status_code == 200)

    # Verify cleared
    r = requests.get(f"{BASE}/api/locations", headers=headers)
    loc1 = [l for l in r.json()["items"] if l["id"] == 1][0]
    test("location.safety_tip cleared", loc1["safety_tip"] is None,
         f"got: {loc1['safety_tip']}")

# === B15: Dashboard ===
print("\n=== B15: Dashboard ===")
r = requests.get(f"{BASE}/api/dashboard", headers=headers)
test("Dashboard 200", r.status_code == 200)
d = r.json()
test("Has stats", "stats" in d)
test("Has location_ranking", "location_ranking" in d)
test("Has breed_top5", "breed_top5" in d)
test("Has trend_14d", "trend_14d" in d)
test("trend_14d = 14 days", len(d.get("trend_14d", [])) == 14)
print(f"    stats: {d.get('stats')}")

# === B16: Report ===
print("\n=== B16/B17: Reports ===")
r = requests.get(f"{BASE}/api/reports/weekly?start=2026-07-01&end=2026-07-07&format=csv",
    headers=headers)
test("Weekly CSV 200", r.status_code == 200)
test("CSV has content", len(r.text) > 0)
print(f"    csv preview: {r.text[:100]}")

# === C1-C7: Public endpoints ===
print("\n=== C1-C7: Public ===")
r = requests.get(f"{BASE}/api/public/dashboard")
test("C1 Public dashboard 200", r.status_code == 200)
d = r.json()
test("C1 Has location_status", len(d.get("location_status", [])) == 5)

r = requests.get(f"{BASE}/api/public/calendar?month=2026-07")
test("C2 Calendar 200", r.status_code == 200)
d = r.json()
test("C2 Has days", len(d.get("days", [])) > 0)
if d.get("days"):
    day = d["days"][0]
    test("C2 day has date", "date" in day)
    test("C2 day has has_animals", "has_animals" in day)
    test("C2 day has locations", "locations" in day)

r = requests.get(f"{BASE}/api/public/detections?date=2026-07-07")
test("C3 Detections by date 200", r.status_code == 200)

r = requests.get(f"{BASE}/api/public/rankings")
test("C4 Rankings 200", r.status_code == 200)
d = r.json()
test("C4 Has breed_ranking", "breed_ranking" in d)
test("C4 Has location_ranking", "location_ranking" in d)

r = requests.get(f"{BASE}/api/public/guide")
test("C5 Guide 200", r.status_code == 200)
test("C5 5 locations", len(r.json().get("locations", [])) == 5)

r = requests.get(f"{BASE}/api/public/safety-tips")
test("C6 Safety tips 200", r.status_code == 200)

if det_id:
    r = requests.get(f"{BASE}/api/public/share-card/{det_id}")
    test("C7 Share card 200", r.status_code == 200)
    test("C7 Returns HTML", "<html" in r.text.lower() or "<!doctype" in r.text.lower(),
         f"content: {r.text[:80]}")

# === C8/C9: Community ===
print("\n=== C8/C9: Community ===")
with open(TEST_IMG, "rb") as f:
    r = requests.post(f"{BASE}/api/public/community",
        files={"image": ("comm.jpg", f, "image/jpeg")},
        data={"location_id": 1, "description": "test", "nickname": "tester", "auto_detect": "true"})
test("C8 Upload 201", r.status_code == 201, f"status={r.status_code} body={r.text[:200]}")
if r.status_code == 201:
    d = r.json()
    test("C8 Has breed (auto_detect)", bool(d.get("breed")), f"breed={d.get('breed')}")
    test("C8 Has id", bool(d.get("id")))

r = requests.get(f"{BASE}/api/public/community")
test("C9 List 200", r.status_code == 200)
d = r.json()
test("C9 Has items", "items" in d)
test("C9 Has total", "total" in d)
if d.get("items"):
    item = d["items"][0]
    test("C9 item has image_url", bool(item.get("image_url")))
    test("C9 item has breed_info", isinstance(item.get("breed_info"), (dict, type(None))))
    print(f"    total={d['total']} shares")

# === Auth guard ===
print("\n=== Auth Guard ===")
r = requests.get(f"{BASE}/api/locations")
test("No auth -> 401", r.status_code == 401, str(r.status_code))

# === Cleanup: Delete detection ===
print("\n=== Cleanup ===")
if det_id:
    r = requests.delete(f"{BASE}/api/detections/{det_id}", headers=headers)
    test("Delete detection 200", r.status_code == 200)
    r = requests.get(f"{BASE}/api/detections/{det_id}", headers=headers)
    test("Gone 404", r.status_code == 404)

# === Summary ===
print(f"\n{'='*50}")
print(f"Results: PASS={passed} FAIL={failed}")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED - review output above")
