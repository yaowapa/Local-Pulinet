#!/usr/bin/env python3
"""
Local Knowledge Hub — Auto Scraper
รัน: python scraper.py
หรือผ่าน GitHub Actions ทุกวัน

จะดึงบทความใหม่จาก 20 เว็บ แล้วอัปเดต index.html อัตโนมัติ
"""
import json, re, sys, time, hashlib
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("กรุณาติดตั้ง: pip install requests beautifulsoup4")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────
HTML_FILE   = Path(__file__).parent / "index.html"
MAX_PER_SITE = 8   # บทความสูงสุดต่อเว็บ
TIMEOUT      = 15  # วินาที
HEADERS      = {"User-Agent": "LocalKnowledgeHub/1.0 (Educational aggregator; contact admin)"}

# Category keyword mapping (ใช้ตรวจหมวดหมู่จากชื่อบทความ)
CAT_KEYWORDS = {
    "food":      ["อาหาร","กิน","แกง","ข้าว","ขนม","ผัก","น้ำพริก","ส้มตำ","ต้ม","ผัด","ยำ"],
    "tradition": ["ประเพณี","พิธี","บวช","งาน","เทศกาล","ลอย","สงกรานต์","ตรุษ","บุญ","งานบวง"],
    "arts":      ["ศิลปะ","ดนตรี","ฟ้อน","รำ","เพลง","หัตถกรรม","ผ้า","ทอ","ปั้น","สลัก","จิตรกรรม"],
    "wisdom":    ["ภูมิปัญญา","สมุนไพร","ยา","พื้นบ้าน","โบราณ","ช่าง","เครื่องมือ","วิธี","การทำ"],
    "place":     ["วัด","เมือง","หมู่บ้าน","อำเภอ","จังหวัด","สถาน","โบราณ","ปราสาท","เจดีย์","แหล่ง"],
    "nature":    ["ป่า","ต้นไม้","สัตว์","ดอกไม้","แม่น้ำ","ธรรมชาติ","นก","ปลา","พืช","สวน"],
}

def guess_cat(title: str) -> str:
    title_lower = title.lower()
    for cat, keywords in CAT_KEYWORDS.items():
        if any(k in title for k in keywords):
            return cat
    return "research"

# คำสำคัญที่บ่งชี้ว่าบทความเกี่ยวกับข้อมูลท้องถิ่น
LOCAL_KEYWORDS = [
    "ท้องถิ่น","ชุมชน","พื้นบ้าน","ภูมิปัญญา","วัฒนธรรม","ประเพณี","ตำนาน","ประวัติ",
    "ล้านนา","อีสาน","อิสาน","ภาคเหนือ","ภาคใต้","ภาคกลาง","ภาคอีสาน",
    "อาหาร","แกง","ขนม","สมุนไพร","ยาพื้นบ้าน",
    "ศิลปะ","หัตถกรรม","ผ้า","ทอ","ดนตรี","ฟ้อน","รำ","เพลง",
    "วัด","โบราณสถาน","โบราณวัตถุ","ปราสาท","เจดีย์","พระ",
    "ชนเผ่า","ชาติพันธุ์","กลุ่มชน","ชาวบ้าน","หมู่บ้าน",
    "ป่า","สัตว์","พืช","ต้นไม้","แม่น้ำ","ภูเขา","ธรรมชาติ",
    "มรดก","เรื่องเล่า","นิทาน","ความเชื่อ","พิธีกรรม",
    "จังหวัด","อำเภอ","ตำบล","เมือง","แหล่ง",
]

def is_local_content(title: str) -> bool:
    """ตรวจว่าบทความเกี่ยวกับข้อมูลท้องถิ่นหรือไม่"""
    return any(k in title for k in LOCAL_KEYWORDS)

def make_id(source: str, url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{source}_{h}"

# ── Scrapers ─────────────────────────────────────────────────────────────────

def scrape_wordpress_api(site: dict) -> list:
    """ดึงบทความจาก WordPress REST API (ดีที่สุด)"""
    base = site["url"].rstrip("/")
    results = []
    try:
        api_url = f"{base}/wp-json/wp/v2/posts"
        r = requests.get(api_url,
            params={"per_page": MAX_PER_SITE, "_fields": "id,title,excerpt,link,date,featured_media"},
            headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        for post in r.json():
            title = BeautifulSoup(post["title"]["rendered"], "html.parser").get_text().strip()
            excerpt = BeautifulSoup(post["excerpt"]["rendered"], "html.parser").get_text().strip()[:200]
            image = None
            if post.get("featured_media"):
                try:
                    ir = requests.get(f"{base}/wp-json/wp/v2/media/{post['featured_media']}",
                                      headers=HEADERS, timeout=8)
                    if ir.status_code == 200:
                        image = ir.json().get("source_url")
                except Exception:
                    pass
            results.append({
                "id":      make_id(site["id"], post["link"]),
                "source":  site["id"],
                "cat":     guess_cat(title),
                "title":   title,
                "excerpt": excerpt,
                "url":     post["link"],
                "date":    post.get("date","")[:10],
                "tags":    [],
                "image":   image,
                "lat":     site.get("default_lat"),
                "lng":     site.get("default_lng"),
            })
        return results
    except Exception as e:
        print(f"  ⚠ WordPress API error ({site['id']}): {e}")
        return []

def scrape_html_links(site: dict) -> list:
    """ดึงบทความจาก HTML — สำหรับเว็บที่ไม่ใช่ WordPress"""
    results = []
    try:
        r = requests.get(site["url"], headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")
        # หา link ที่มีชื่อบทความ
        seen = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("http"):
                href = site["url"].rstrip("/") + "/" + href.lstrip("/")
            if href in seen or len(href) < 20:
                continue
            # skip ลิงก์ที่เป็น navigation, login, etc.
            skip_url_words = ["login","register","contact","about","search","javascript","#","mailto","tel:",
                              "logout","admin","wp-admin","feed","rss","sitemap","tag/","category/",
                              "page/","author/","attachment/","?replytocom","comment","download","pdf"]
            if any(w in href.lower() for w in skip_url_words):
                continue
            text = a.get_text(strip=True)
            if len(text) < 10 or len(text) > 200:
                continue
            # skip ชื่อที่เป็น navigation / system (ไม่ใช่บทความเนื้อหา)
            skip_titles = ["หน้าแรก","หน้าหลัก","ช่วยเหลือ","สถิติ","คู่มือ","เข้าสู่ระบบ","ออกจากระบบ",
                           "ติดต่อ","เกี่ยวกับ","ค้นหา","แผนผัง","นโยบาย","เงื่อนไข","cookies",
                           "home","help","login","logout","about","contact","search","sitemap",
                           "next","prev","previous","read more","อ่านต่อ","ดูเพิ่ม","more",
                           "รายละเอียด","detail","view","download","full text"]
            if any(t.lower() in text.lower() for t in skip_titles) and len(text) < 30:
                continue
            # รับเฉพาะบทความที่เกี่ยวกับข้อมูลท้องถิ่น
            if not is_local_content(text):
                continue
            seen.add(href)
            results.append({
                "id":      make_id(site["id"], href),
                "source":  site["id"],
                "cat":     guess_cat(text),
                "title":   text,
                "excerpt": "",
                "url":     href,
                "date":    datetime.now().strftime("%Y-%m-%d"),
                "tags":    [],
                "lat":     site.get("default_lat"),
                "lng":     site.get("default_lng"),
            })
            if len(results) >= MAX_PER_SITE:
                break
    except Exception as e:
        print(f"  ⚠ HTML scrape error ({site['id']}): {e}")
    return results

def scrape_omeka(site: dict) -> list:
    """ดึงรายการจาก Omeka archive (KKU)"""
    results = []
    try:
        api_url = site["url"].rstrip("/") + "/omeka/api/items"
        r = requests.get(api_url, params={"per_page": MAX_PER_SITE}, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            for item in r.json():
                title_el = item.get("element_texts", [])
                title = next((e["text"] for e in title_el if e.get("element",{}).get("name")=="Title"), "")
                url = item.get("url", site["url"])
                if title:
                    results.append({
                        "id":      make_id(site["id"], url),
                        "source":  site["id"],
                        "cat":     guess_cat(title),
                        "title":   title,
                        "excerpt": "",
                        "url":     url,
                        "date":    datetime.now().strftime("%Y-%m-%d"),
                        "tags":    [],
                        "lat":     site.get("default_lat"),
                        "lng":     site.get("default_lng"),
                    })
    except Exception as e:
        print(f"  ⚠ Omeka error ({site['id']}): {e}")
    return results

# ── Site strategy map ─────────────────────────────────────────────────────────
SCRAPE_STRATEGY = {
    "ssd":              scrape_wordpress_api,
    "esan":             scrape_wordpress_api,
    "mju_food":         scrape_wordpress_api,
    "esan_info":        scrape_wordpress_api,
    "lanna_info":       scrape_html_links,
    "cmu_dc":           scrape_html_links,
    "mfu_cr":           scrape_html_links,
    "mju_museum":       scrape_html_links,
    "up_local":         scrape_html_links,
    "kku_archive":      scrape_omeka,
    "msu_isan":         scrape_html_links,
    "isannaru":         scrape_html_links,
    "sut_korat":        scrape_html_links,
    "su_west":          scrape_wordpress_api,
    "stou_nont":        scrape_html_links,
    "stou_digital":     scrape_html_links,
    "buu_lib":          scrape_html_links,
    "pattani_heritage": scrape_html_links,
    "psu_south":        scrape_html_links,
    "wu_lib":           scrape_html_links,
}

# Default coords per site (ใช้เมื่อ scraper ไม่รู้พิกัด)
DEFAULT_COORDS = {
    "ssd":              [18.905, 99.025],
    "esan":             [15.244, 104.857],
    "lanna_info":       [18.796, 98.972],
    "cmu_dc":           [18.794, 98.975],
    "mfu_cr":           [19.910, 99.832],
    "mju_food":         [18.871, 98.981],
    "mju_museum":       [18.870, 98.981],
    "up_local":         [19.163, 99.905],
    "kku_archive":      [16.442, 102.836],
    "msu_isan":         [16.188, 103.301],
    "isannaru":         [16.185, 103.298],
    "esan_info":        [15.235, 104.860],
    "sut_korat":        [14.987, 102.101],
    "su_west":          [13.820, 100.065],
    "stou_nont":        [13.858, 100.520],
    "stou_digital":     [13.860, 100.522],
    "buu_lib":          [13.361, 100.985],
    "pattani_heritage": [6.871,  101.253],
    "psu_south":        [7.007,  100.473],
    "wu_lib":           [8.640,  99.953],
}

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"🔄 Local Knowledge Hub Scraper — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"   ไฟล์: {HTML_FILE}")

    # อ่าน HTML ปัจจุบัน
    if not HTML_FILE.exists():
        print("❌ ไม่พบ index.html")
        sys.exit(1)
    html = HTML_FILE.read_text(encoding="utf-8")

    # โหลด config จาก SITES_CONFIG
    m = re.search(r'<script id="SITES_CONFIG" type="application/json">\s*(\[.*?\])\s*</script>',
                  html, re.DOTALL)
    sites = json.loads(m.group(1)) if m else []

    # โหลด articles ปัจจุบัน (เพื่อ merge ไม่ให้ซ้ำ)
    m2 = re.search(r'<script id="ARTICLES_DATA" type="application/json">\s*(\[.*?\])\s*</script>',
                   html, re.DOTALL)
    existing = json.loads(m2.group(1)) if m2 else []
    existing_ids = {a["id"] for a in existing}
    existing_urls = {a["url"] for a in existing}

    print(f"   บทความปัจจุบัน: {len(existing)}")

    new_articles = []
    for site in sites:
        sid = site["id"]
        coords = DEFAULT_COORDS.get(sid, [13.7, 100.5])
        site["default_lat"] = coords[0]
        site["default_lng"] = coords[1]

        fn = SCRAPE_STRATEGY.get(sid, scrape_html_links)
        print(f"  📡 {sid} ({site.get('name_th','')})…", end=" ", flush=True)
        try:
            arts = fn(site)
        except Exception as e:
            print(f"❌ {e}")
            arts = []

        added = 0
        for art in arts:
            if art["id"] not in existing_ids and art["url"] not in existing_urls:
                new_articles.append(art)
                existing_ids.add(art["id"])
                existing_urls.add(art["url"])
                added += 1
        print(f"✅ +{added} ใหม่ ({len(arts)} ดึงมา)")
        time.sleep(1)  #礼貌 delay

    # ── เติมรูปให้บทความเก่าที่ยังไม่มีรูป (WordPress sites) ──────────────────
    WP_SITE_BASES = {s["id"]: s["url"].rstrip("/") for s in sites
                     if SCRAPE_STRATEGY.get(s["id"]) == scrape_wordpress_api}
    need_image = [a for a in existing if not a.get("image") and a["source"] in WP_SITE_BASES]
    if need_image:
        print(f"\n🖼  เติมรูปบทความเก่าที่ยังไม่มีรูป {len(need_image)} ชิ้น…")
        enriched = 0
        for art in need_image:
            base = WP_SITE_BASES[art["source"]]
            m_pid = re.search(r'[?&]p=(\d+)', art["url"])
            if not m_pid:
                continue
            pid = m_pid.group(1)
            try:
                r1 = requests.get(f"{base}/wp-json/wp/v2/posts/{pid}",
                                  params={"_fields": "featured_media"},
                                  headers=HEADERS, timeout=8)
                if r1.status_code != 200:
                    continue
                mid = r1.json().get("featured_media")
                if not mid:
                    continue
                r2 = requests.get(f"{base}/wp-json/wp/v2/media/{mid}",
                                  params={"_fields": "source_url"},
                                  headers=HEADERS, timeout=8)
                if r2.status_code == 200:
                    url = r2.json().get("source_url")
                    if url:
                        art["image"] = url
                        enriched += 1
            except Exception:
                pass
            time.sleep(0.5)
        print(f"   เติมรูปได้ {enriched} ชิ้น")

    # รวมบทความ: ใหม่อยู่บน, เก่าอยู่ล่าง
    all_articles = new_articles + existing
    print(f"\n✅ รวมบทความ: {len(existing)} เดิม + {len(new_articles)} ใหม่ = {len(all_articles)}")

    # อัปเดต HTML
    new_json = json.dumps(all_articles, ensure_ascii=False, indent=2)
    new_tag = f'<script id="ARTICLES_DATA" type="application/json">\n{new_json}\n</script>'
    old_tag = re.search(r'<script id="ARTICLES_DATA" type="application/json">.*?</script>',
                        html, re.DOTALL)
    if old_tag:
        html = html[:old_tag.start()] + new_tag + html[old_tag.end():]
    else:
        print("⚠️  ไม่พบ ARTICLES_DATA tag ใน HTML")
        sys.exit(1)

    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"💾 บันทึก index.html แล้ว ({len(html):,} bytes)")
    print(f"🎉 เสร็จสิ้น! เพิ่มบทความใหม่ {len(new_articles)} บทความ")

if __name__ == "__main__":
    main()
