import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일
ACCUSE_FILE = 'accusations_mobile_v6.csv'

def load_data():
    if os.path.exists(ACCUSE_FILE):
        return pd.read_csv(ACCUSE_FILE)
    else:
        return pd.DataFrame(columns=['접수번호', '날짜', '피고소인', '사건내용', '사진보유', '추가설명', '상태'])

def save_data(df):
    df.to_csv(ACCUSE_FILE, index=False)

if 'accuse_db' not in st.session_state:
    st.session_state.accuse_db = load_data()

# --- 모바일 최적화 설정 ---
st.set_page_config(page_title="학급 고소장", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    .stCheckbox { font-size: 1.1rem; padding: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ 학급 고소장 접수")
menu = st.radio("메뉴 선택", ["📝 고소장 작성", "🔒 인권예절부 관리"], horizontal=True)
st.divider()

# --- 1. 고소장 작성 (체크박스 적용) ---
if menu == "📝 고소장 작성":
    st.subheader("신고서 작성")
    with st.form("accuse_form", clear_on_submit=True):
        target = st.text_input("👤 피고소인 (누구인가요?)", placeholder="이름 입력")
        content = st.text_area("📄 사건 내용", placeholder="어떤 일이 있었나요?", height=150)
        
        st.write("🔍 **추가 증거 확인**")
        # 사진 업로드 대신 체크박스 배치
        has_photo = st.checkbox("📸 제출 가능한 사진/영상 증거가 있습니다.")
        
        evidence_text = st.text_area("✍️ 증거 상세 설명", 
                                   placeholder="증인 이름, 대화 내용 혹은 사진 증거 링크(구글 드라이브 등)를 적어주세요.")
        
        if st.form_submit_button("🚀 고소장 최종 제출하기"):
            if target and content:
                case_id = f"CASE-{len(st.session_state.accuse_db) + 1:03d}"
                new_data = {
                    '접수번호': case_id,
                    '날짜': datetime.now().strftime("%m-%d %H:%M"),
                    '피고소인': target,
                    '사건내용': content,
                    '사진보유': "보유" if has_photo else "없음",
                    '추가설명': evidence_text if evidence_text else "내용 없음",
                    '상태': '검토 대기'
                }
                st.session_state.accuse_db = pd.concat([st.session_state.accuse_db, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.accuse_db)
                st.success(f"성공적으로 접수되었습니다! (번호: {case_id})")
                st.balloons()
            else:
                st.error("피고소인과 사건 내용은 반드시 입력해야 합니다.")

# --- 2. 인권예절부 관리 ---
else:
    st.subheader("관리자 모드")
    admin_pw = st.text_input("비밀번호", type="password")
    
    if admin_pw == "12345":
        if not st.session_state.accuse_db.empty:
            case_list = st.session_state.accuse_db['접수번호'].tolist()
            selected_case = st.selectbox("검토할 사건 선택", case_list[::-1])
            
            idx = st.session_state.accuse_db[st.session_state.accuse_db['접수번호'] == selected_case].index[0]
            case_info = st.session_state.accuse_db.loc[idx]
            
            # 카드형 상세 정보
            st.info(f"**현재 상태: {case_info['상태']}**")
            st.write(f"**피고소인:** {case_info['피고소인']}")
            st.write(f"**사진 증거 여부:** {case_info['사진보유']}")
            
            with st.expander("📄 사건 내용 보기", expanded=True):
                st.write(case_info['사건내용'])
            
            with st.expander("✍️ 추가 증거/링크 보기"):
                st.write(case_info['추가설명'])
            
            st.divider()
            new_status = st.selectbox("상태 변경", ["검토 대기", "재판 회부", "기각", "처리 완료"])
            if st.button("✅ 상태 업데이트"):
                st.session_state.accuse_db.at[idx, '상태'] = new_status
                save_data(st.session_state.accuse_db)
                st.success("상태가 업데이트되었습니다.")
                st.rerun()
        else:
            st.write("접수된 고소장이 없습니다.")
