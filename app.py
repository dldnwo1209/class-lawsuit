import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일
ACCUSE_FILE = 'accusations_v4.csv'

def load_data():
    if os.path.exists(ACCUSE_FILE):
        return pd.read_csv(ACCUSE_FILE)
    else:
        return pd.DataFrame(columns=['접수번호', '날짜', '피고소인', '사건내용', '추가설명', '상태'])

def save_data(df):
    df.to_csv(ACCUSE_FILE, index=False)

if 'accuse_db' not in st.session_state:
    st.session_state.accuse_db = load_data()

st.set_page_config(page_title="학급 고소장 접수처", layout="centered")
st.title("⚖️ 학급 고소장 접수 시스템")

tab1, tab2 = st.tabs(["📝 고소장 작성", "🔒 인권예절부 관리"])

# --- 1. 고소장 작성 ---
with tab1:
    st.header("신고서 작성")
    with st.form("accuse_form", clear_on_submit=True):
        st.info("💡 모든 항목은 익명으로 처리됩니다.")
        target = st.text_input("피고소인 (누구를 고소합니까?)")
        content = st.text_area("사건 내용 (상세 상황 설명)")
        evidence_text = st.text_area("글로 설명하는 추가 증거 (선택 사항)")
        evidence_img = st.file_uploader("사진 증거 업로드", type=['png', 'jpg', 'jpeg'])
        submit = st.form_submit_button("고소장 최종 제출")
        
        if submit:
            if target and content:
                new_idx = len(st.session_state.accuse_db) + 1
                new_data = {
                    '접수번호': f"CASE-{new_idx:03d}",
                    '날짜': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    '피고소인': target,
                    '사건내용': content,
                    '추가설명': evidence_text if evidence_text else "없음",
                    '상태': '검토 대기'
                }
                st.session_state.accuse_db = pd.concat([st.session_state.accuse_db, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.accuse_db)
                st.success(f"접수 완료! (번호: CASE-{new_idx:03d})")
            else:
                st.error("피고소인과 사건 내용은 필수 입력 사항입니다.")

# --- 2. 인권예절부 관리 (버전 업데이트) ---
with tab2:
    st.header("관리자 모드")
    admin_pw = st.text_input("인권예절부 비밀번호", type="password")
    
    if admin_pw == "12345":
        if not st.session_state.accuse_db.empty:
            st.subheader("📋 전체 고소 목록")
            # 상태 열을 드롭다운 선택식으로 설정
            status_options = ["검토 대기", "증거 보완 필요", "재판 회부", "기각", "처리 완료"]
            
            edited_df = st.data_editor(
                st.session_state.accuse_db,
                column_config={
                    "상태": st.column_config.SelectboxColumn(
                        "사건 상태",
                        help="사건의 현재 진행 상황을 선택하세요",
                        options=status_options,
                        required=True,
                    )
                },
                disabled=["접수번호", "날짜", "피고소인", "사건내용", "추가설명"], # 상태 외 수정 불가
                use_container_width=True
            )
            
            if st.button("✅ 변경 사항 저장"):
                st.session_state.accuse_db = edited_df
                save_data(st.session_state.accuse_db)
                st.success("상태가 성공적으로 업데이트되었습니다.")
                st.rerun()

            st.divider()
            st.subheader("🔍 상세 내용 확인")
            case_no = st.selectbox("사건 번호 선택", st.session_state.accuse_db['접수번호'])
            case_info = st.session_state.accuse_db[st.session_state.accuse_db['접수번호'] == case_no].iloc[0]
            
            st.write(f"**피고소인:** {case_info['피고소인']} | **현재 상태:** {case_info['상태']}")
            st.info(f"**사건 내용:**\n\n{case_info['사건내용']}")
            st.success(f"**추가 증거:**\n\n{case_info['추가설명']}")
            
        else:
            st.write("접수된 고소장이 없습니다.")
    elif admin_pw != "":
        st.error("비밀번호가 틀렸습니다.")
