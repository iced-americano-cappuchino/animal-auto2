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
        "text=엑셀 다운로드",
        "text=엑셀다운로드",
        "text=Excel",
        "input[value*='엑셀']",
        "input[type='button'][value*='엑셀']",
        "input[type='submit'][value*='엑셀']",
        "img[alt*='엑셀']",
        "a[onclick*='excel' i]",
        "a[onclick*='Excel']",
        "button[onclick*='excel' i]",
        "input[onclick*='excel' i]",
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


def download_one(page, target, max_retries=4):
    print(f"\n>>> {target['name']} 다운로드 시작")

    main_url = "https://www.animal.go.kr/"

    for attempt in range(1, max_retries + 1):
        print(f"  시도 {attempt}/{max_retries}")
        try:
            page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  메인페이지 접속 실패(무시하고 진행): {e}")

        page.goto(target["url"], referer=main_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # 사이트가 간헐적으로 "페이지를 찾을 수 없습니다" 오류를 반환하는 경우 재시도
        body_text = ""
        try:
            body_text = page.inner_text("body")
        except Exception:
            pass

        if "페이지를 찾을 수 없습니다" in body_text or "존재하지 않거나" in body_text:
            print(f"  사이트 오류 페이지 감지 - {attempt}번째 시도 실패, 재시도 대기...")
            page.wait_for_timeout(5000 * attempt)  # 재시도마다 대기 시간을 늘림
            continue
        else:
            break
    else:
        raise RuntimeError(f"{max_retries}번 재시도했지만 계속 오류 페이지가 나옴")

    print(f"  페이지 타이틀: {page.title()}")

    # 조회 버튼 (있으면 클릭, 없어도 진행) - input[value=조회] 형태도 포함해서 탐색
    search_candidates = [
        "text=조회",
        "input[value='조회']",
        "input[type='submit'][value*='조회']",
        "input[type='button'][value*='조회']",
        "button:has-text('조회')",
    ]
    clicked_search = False
    for sel in search_candidates:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=5000)
                clicked_search = True
                print(f"  '조회' 버튼 클릭 성공: {sel}")
                page.wait_for_timeout(1500)
                break
        except Exception:
            continue
    if not clicked_search:
        print("  '조회' 버튼을 못 찾음 - 기본 목록으로 진행")

    # 엑셀 버튼 탐색
    # "엑셀 다운로드" 버튼이 늦게 렌더링될 수 있으니 최대 10초 대기
    try:
        page.wait_for_selector("text=엑셀 다운로드, input[value*='엑셀']", timeout=10000, state="attached")
    except Exception:
        pass

    btn = find_excel_button(page)
    if btn is None:
        print("  엑셀 다운로드 버튼을 찾지 못함 - 디버그 정보 저장")
        debug_dump(page, target, "no_button_found")
        # 페이지에 '엑셀'이라는 글자가 있는지 자체를 확인
        if "엑셀" in page.content():
            print("  (참고) 페이지 소스에는 '엑셀'이라는 단어가 존재함 -> 선택자만 문제일 가능성")
        else:
            print("  (참고) 페이지 소스에 '엑셀'이라는 단어 자체가 없음 -> 페이지가 다르게 로드됐을 가능성")

        # 아티팩트를 못 찾는 경우를 대비해 로그에 직접 본문 텍스트 일부 출력
        try:
            body_text = page.inner_text("body")
            print("  ----- 페이지 본문 텍스트 (앞부분 1500자) -----")
            print(body_text[:1500])
            print("  ----- 페이지 본문 텍스트 끝 -----")
        except Exception as e:
            print(f"  본문 텍스트 추출 실패: {e}")

        raise RuntimeError("엑셀 다운로드 버튼을 찾지 못함")

    try:
        btn.scroll_into_view_if_needed(timeout=5000)
    except Exception:
        pass

    try:
        with page.expect_download(timeout=30000) as download_info:
            try:
                btn.click(timeout=5000)
            except Exception:
                # 보통 클릭이 막히면(다른 요소에 가려짐 등) 강제 클릭 시도
                btn.click(timeout=5000, force=True)
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
