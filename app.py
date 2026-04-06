import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일
ACCUSE_FILE = 'accusations_v2.csv'

def load_data():
    if os.path.exists(ACCUSE_FILE):
        return pd.read_csv(ACCUSE_FILE)
    else:
        return pd.DataFrame(columns=['접수번호', '날짜', '피고소인', '사건내용', '증인', '추가설명', '상태'])

def save_data(df):
    df.to_csv(ACCUSE_FILE, index=False)

if 'accuse_db' not in st.session_state:
    st.session_state.accuse_db = load_data()

# --- UI 레이아웃 ---
st.set_page_config(page_title="학급 고소장 접수처", layout="centered")
st.title("⚖️ 학급 고소장 접수 시스템")

tab1, tab2 = st.tabs(["📝 고소장 작성", "🔒 인권예절부 관리"])

# --- 1. 고소장 작성 ---
with tab1:
    st.header("신고서 작성")
    with st.form("accuse_form", clear_on_submit=True):
        st.info("💡 모든 항목은 익명으로 처리됩니다. 증거가 있다면 상세히 적어주세요.")
        
        target = st.text_input("피고소인 (누구를 고소합니까?)")
        content = st.text_area("사건 내용 (상세 상황 설명)")
        
        st.markdown("---")
        st.subheader("📁 증거 제시 (선택 사항)")
        st.caption("증거가 없다면 공란으로 두셔도 됩니다.")
        
        witness = st.text_input("증인 (함께 있었던 사람의 이름)")
        evidence_text = st.text_area("글로 설명하는 추가 증거 (예: 대화 내용, 상황 묘사 등)")
        
        # 사진 업로드 (Streamlit Cloud 배포 시 파일 용량 제한 주의)
        evidence_img = st.file_uploader("사진 증거 업로드 (이미지 파일)", type=['png', 'jpg', 'jpeg'])
        
        submit = st.form_submit_button("고소장 최종 제출")
        
        if submit:
            if target and content:
                new_idx = len(st.session_state.accuse_db) + 1
                new_data = {
                    '접수번호': f"CASE-{new_idx:03d}",
                    '날짜': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    '피고소인': target,
                    '사건내용': content,
                    '증인': witness if witness else "없음",
                    '추가설명': evidence_text if evidence_text else "없음",
                    '상태': '검토 대기'
                }
                st.session_state.accuse_db = pd.concat([st.session_state.accuse_db, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.accuse_db)
                st.success(f"접수 완료! (번호: CASE-{new_idx:03d})")
                if evidence_img:
                    st.info("📸 사진 증거가 첨부되었습니다. (관리자 확인 가능)")
            else:
                st.error("피고소인과 사건 내용은 필수 입력 사항입니다.")

# --- 2. 인권예절부 전용 (비밀번호: 12345) ---
with tab2:
    st.header("관리자 모드")
    admin_pw = st.text_input("인권예절부 비밀번호", type="password")
    
    if admin_pw == "12345":
        if not st.session_state.accuse_db.empty:
            st.subheader("📋 전체 고소 목록")
            #