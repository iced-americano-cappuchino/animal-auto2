# -*- coding: utf-8 -*-
"""
3단계: 병합 + 시각화
======================
downloads/ 폴더에 있는 오늘 날짜의 두 엑셀 파일을 읽어서
1) 컬럼명을 정리하고
2) 공통 컬럼 기준으로 병합(concat, 출처 컬럼 추가)하고
3) 상태별/품종별 차트를 만들어 저장합니다.

실행:
    pip install pandas openpyxl xlrd matplotlib --break-system-packages
    python 3_merge_visualize.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import glob
import os
from datetime import datetime

# ------------------------------------------------------------------
# 한글 폰트 설정 (Ubuntu 러너: NanumGothic / 로컬 Windows: Malgun Gothic)
# ------------------------------------------------------------------
fonts = glob.glob('/usr/share/fonts/**/NanumGothic*.ttf', recursive=True)
print("찾은 폰트 파일:", fonts)
if fonts:
    fm.fontManager.addfont(fonts[0])
    plt.rcParams['font.family'] = 'NanumGothic'
    print("폰트 적용: NanumGothic")
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    print("경고: 나눔폰트 없음 - Ubuntu 러너에서는 글씨가 깨집니다")
plt.rcParams['axes.unicode_minus'] = False

# ------------------------------------------------------------------
# 경로 설정
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
TODAY = datetime.now().strftime("%Y%m%d")


def find_latest_file(keyword):
    pattern = os.path.join(DOWNLOAD_DIR, f"*{keyword}*")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"'{keyword}' 포함된 파일을 downloads/ 에서 찾을 수 없습니다.")
    return files[-1]


def load_excel(path):
    # 정부 사이트 다운로드 파일은 확장자만 .xls인 html 표 형식인 경우가 많음
    try:
        return pd.read_excel(path)
    except Exception:
        tables = pd.read_html(path)
        return tables[0]


def main():
    f1 = find_latest_file("입양대상동물")
    f2 = find_latest_file("보호센터_보호동물")
    df_adopt = load_excel(f1)
    df_protect = load_excel(f2)

    print("[입양대상동물] 컬럼:", list(df_adopt.columns))
    print("[보호센터_보호동물] 컬럼:", list(df_protect.columns))

    # 컬럼명 공백 제거
    df_adopt.columns = [str(c).strip() for c in df_adopt.columns]
    df_protect.columns = [str(c).strip() for c in df_protect.columns]

    # 출처 표시
    df_adopt["출처"] = "입양대상동물"
    df_protect["출처"] = "보호센터_보호동물"

    # 세로 병합 (컬럼이 다르면 없는 쪽은 NaN으로 채워짐)
    merged = pd.concat([df_adopt, df_protect], ignore_index=True, sort=False)
    merged_path = os.path.join(OUTPUT_DIR, f"merged_{TODAY}.xlsx")
    merged.to_excel(merged_path, index=False)
    print(f"\n병합 완료: {merged_path} (총 {len(merged)}건)")

    # ------------------------------------------------------------------
    # 시각화 1: 출처별 건수
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))
    merged["출처"].value_counts().plot(kind="bar", ax=ax, color=["#4C72B0", "#DD8452"])
    ax.set_title("출처별 동물 건수")
    ax.set_ylabel("건수")
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, f"chart_source_count_{TODAY}.png")
    plt.savefig(chart1_path, dpi=150)
    plt.close()
    print(f"차트 저장: {chart1_path}")

    # ------------------------------------------------------------------
    # 시각화 2: 상태 컬럼이 있으면 상태별 분포
    # ------------------------------------------------------------------
    if "상태" in merged.columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        merged["상태"].value_counts().plot(kind="bar", ax=ax, color="#55A868")
        ax.set_title("상태별 건수")
        ax.set_ylabel("건수")
        plt.tight_layout()
        chart2_path = os.path.join(OUTPUT_DIR, f"chart_status_count_{TODAY}.png")
        plt.savefig(chart2_path, dpi=150)
        plt.close()
        print(f"차트 저장: {chart2_path}")

    # ------------------------------------------------------------------
    # 시각화 3: 품종 컬럼이 있으면 상위 10개 품종
    # ------------------------------------------------------------------
    if "품종" in merged.columns:
        fig, ax = plt.subplots(figsize=(7, 4))
        merged["품종"].value_counts().head(10).plot(kind="barh", ax=ax, color="#C44E52")
        ax.invert_yaxis()
        ax.set_title("상위 10개 품종")
        ax.set_xlabel("건수")
        plt.tight_layout()
        chart3_path = os.path.join(OUTPUT_DIR, f"chart_top_breeds_{TODAY}.png")
        plt.savefig(chart3_path, dpi=150)
        plt.close()
        print(f"차트 저장: {chart3_path}")

    print("\n완료.")


if __name__ == "__main__":
    main()
