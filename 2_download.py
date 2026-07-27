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


def download_one(page, target):
    print(f"\n>>> {target['name']} 다운로드 시작")
    page.goto(target["url"], wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1000)

    # ------------------------------------------------------------------
    # TODO 1) 필요 시 검색조건(조회) 버튼 클릭 - 기본 조건으로 충분하면 생략 가능
    # 1단계 출력에서 확인한 '조회' 버튼의 정확한 텍스트/선택자로 교체하세요.
    # ------------------------------------------------------------------
    try:
        page.click("text=조회", timeout=5000)
        page.wait_for_timeout(1000)
    except Exception:
        print("  '조회' 버튼을 못 찾음 - 기본 목록으로 진행")

    # ------------------------------------------------------------------
    # TODO 2) 엑셀 다운로드 버튼 클릭
    # 1단계 출력 결과에서 찾은 실제 텍스트/onclick/선택자로 아래 3가지 중
    # 맞는 방식 하나를 선택해서 사용하세요.
    # ------------------------------------------------------------------
    with page.expect_download(timeout=30000) as download_info:
        # 방식 A: 버튼 텍스트가 "엑셀다운로드" 또는 "엑셀 다운로드"인 경우
        page.click("text=엑셀다운로드")

        # 방식 B: <a onclick="fn_excelDown()"> 같은 함수 호출인 경우
        # page.evaluate("fn_excelDown()")   # 1단계에서 확인한 실제 함수명으로 교체

        # 방식 C: alt="엑셀다운로드" 아이콘 이미지인 경우
        # page.click("img[alt='엑셀다운로드']")

    download = download_info.value
    save_path = os.path.join(DOWNLOAD_DIR, target["filename"])
    download.save_as(save_path)
    print(f"  저장 완료: {save_path}")
    return save_path


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
