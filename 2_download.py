"""
2단계: 실제 엑셀 다운로드 스크립트 (템플릿)
================================================
1단계(1_inspect_page.py) 실행 결과를 보고,
아래 "TODO" 표시된 부분의 선택자(selector)를 실제 버튼에 맞게 수정하세요.

가장 흔한 패턴 3가지를 미리 준비해뒀습니다. 1단계 출력 결과를 보고
해당하는 방식의 주석을 해제(uncomment)하고 나머지는 지우면 됩니다.

실행:
    python 2_download.py
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import os

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

TODAY = datetime.now().strftime("%Y%m%d")

TARGETS = [
    {
        "name": "입양대상동물",
        "url": "https://www.animal.go.kr/front/awtis/protection/protectionList.do?menuNo=1000000060",
        "filename": f"입양대상동물_{TODAY}.xls",
    },
    {
        "name": "보호센터_보호동물",
        "url": "https://www.animal.go.kr/front/awtis/public/publicList.do?menuNo=1000000055",
        "filename": f"보호센터_보호동물_{TODAY}.xls",
    },
]


def debug_dump(page, target, tag):
    """실패 시 원인 파악용 스크린샷 + HTML 저장"""
    shot_path = os.path.join(DOWNLOAD_DIR, f"debug_{target['name']}_{tag}.png")
    html_path = os.path.join(DOWNLOAD_DIR, f"debug_{target['name']}_{tag}.html")
    try:
        page.screenshot(path=shot_path, full_page=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"  [디버그] 스크린샷 저장: {shot_path}")
        print(f"  [디버그] HTML 저장: {html_path}")
    except Exception as e:
        print(f"  [디버그] 저장 실패: {e}")


def find_excel_button(page):
    """여러 후보 텍스트/선택자로 엑셀 다운로드 버튼을 탐색"""
    candidates = [
        "text=엑셀다운로드",
        "text=엑셀 다운로드",
        "text=Excel",
        "img[alt*='엑셀']",
        "a[onclick*='excel' i]",
        "a[onclick*='Excel']",
        "button[onclick*='excel' i]",
        "[title*='엑셀']",
    ]
    for sel in candidates:
        loc = page.locator(sel)
        try:
            if loc.count() > 0 and loc.first.is_visible():
                print(f"  버튼 후보 발견: {sel}")
                return loc.first
        except Exception:
            continue
    return None


def download_one(page, target):
    print(f"\n>>> {target['name']} 다운로드 시작")
    # networkidle은 추적 스크립트 등으로 인해 영영 안 끝날 수 있어 domcontentloaded로 변경
    page.goto(target["url"], wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    print(f"  페이지 타이틀: {page.title()}")

    # 조회 버튼 (있으면 클릭, 없어도 진행)
    try:
        page.click("text=조회", timeout=5000)
        page.wait_for_timeout(1500)
    except Exception:
        print("  '조회' 버튼을 못 찾음 - 기본 목록으로 진행")

    # 엑셀 버튼 탐색
    btn = find_excel_button(page)
    if btn is None:
        print("  엑셀 다운로드 버튼을 찾지 못함 - 디버그 정보 저장")
        debug_dump(page, target, "no_button_found")
        # 페이지에 '엑셀'이라는 글자가 있는지 자체를 확인
        if "엑셀" in page.content():
            print("  (참고) 페이지 소스에는 '엑셀'이라는 단어가 존재함 -> 선택자만 문제일 가능성")
        else:
            print("  (참고) 페이지 소스에 '엑셀'이라는 단어 자체가 없음 -> 페이지가 다르게 로드됐을 가능성")
        raise RuntimeError("엑셀 다운로드 버튼을 찾지 못함")

    try:
        with page.expect_download(timeout=30000) as download_info:
            btn.click()
        download = download_info.value
        save_path = os.path.join(DOWNLOAD_DIR, target["filename"])
        download.save_as(save_path)
        print(f"  저장 완료: {save_path}")
        return save_path
    except Exception as e:
        debug_dump(page, target, "click_failed")
        raise


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        saved_files = []
        for target in TARGETS:
            try:
                saved_files.append(download_one(page, target))
            except Exception as e:
                print(f"  [실패] {target['name']}: {e}")
        browser.close()
        print("\n완료된 파일:", saved_files)


if __name__ == "__main__":
    main()
