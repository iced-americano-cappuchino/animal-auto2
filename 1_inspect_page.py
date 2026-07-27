"""
1단계: 진단 스크립트
======================
목적: 두 페이지(입양대상동물, 보호센터 보호동물)를 열어서
      화면에 있는 버튼/링크/입력필드의 이름과 속성을 전부 출력합니다.
      이걸로 "엑셀다운로드" 버튼의 정확한 텍스트/선택자를 확인합니다.

실행 전 준비:
    pip install playwright --break-system-packages
    playwright install chromium

실행:
    python 1_inspect_page.py

실행하면 브라우저 창이 뜨고(headless=False), 콘솔에 버튼 목록이 출력됩니다.
캡처하거나 출력 내용을 복사해서 알려주시면 2단계 스크립트를 완성할 수 있습니다.
"""

from playwright.sync_api import sync_playwright

URLS = {
    "입양대상동물": "https://www.animal.go.kr/front/awtis/protection/protectionList.do?menuNo=1000000060",
    "보호센터_보호동물": "https://www.animal.go.kr/front/awtis/public/publicList.do?menuNo=1000000055",
}


def inspect(page, name, url):
    print(f"\n{'=' * 60}")
    print(f"[{name}] {url}")
    print("=" * 60)

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1500)

    # 1) 페이지 안의 모든 버튼(button, input[type=button/submit], a 태그 중 클릭 가능한 것) 출력
    print("\n--- <button> 태그 목록 ---")
    for i, btn in enumerate(page.query_selector_all("button")):
        text = (btn.inner_text() or "").strip()
        onclick = btn.get_attribute("onclick") or ""
        cls = btn.get_attribute("class") or ""
        idv = btn.get_attribute("id") or ""
        if text or onclick:
            print(f"  [{i}] text='{text}' id='{idv}' class='{cls}' onclick='{onclick[:80]}'")

    print("\n--- <a> 태그 중 'excel', '엑셀', '다운로드' 포함 항목 ---")
    for i, a in enumerate(page.query_selector_all("a")):
        text = (a.inner_text() or "").strip()
        href = a.get_attribute("href") or ""
        onclick = a.get_attribute("onclick") or ""
        combined = f"{text} {href} {onclick}".lower()
        if "excel" in combined or "엑셀" in text or "다운로드" in text:
            print(f"  [{i}] text='{text}' href='{href}' onclick='{onclick[:120]}'")

    print("\n--- input[type=image] / img (아이콘 버튼일 수 있음) ---")
    for i, el in enumerate(page.query_selector_all("input[type=image], img[onclick], img[alt*='엑셀'], img[alt*='다운로드']")):
        alt = el.get_attribute("alt") or ""
        onclick = el.get_attribute("onclick") or ""
        src = el.get_attribute("src") or ""
        print(f"  [{i}] alt='{alt}' src='{src}' onclick='{onclick[:120]}'")

    print("\n--- 검색 조건 관련 <input>/<select> (날짜, 지역 등) ---")
    for i, el in enumerate(page.query_selector_all("input, select")):
        name = el.get_attribute("name") or ""
        idv = el.get_attribute("id") or ""
        typ = el.get_attribute("type") or el.evaluate("e => e.tagName")
        if name or idv:
            print(f"  [{i}] tag={typ} name='{name}' id='{idv}'")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()
        for name, url in URLS.items():
            inspect(page, name, url)
        print("\n\n확인 후 Enter를 누르면 브라우저가 닫힙니다...")
        input()
        browser.close()


if __name__ == "__main__":
    main()
