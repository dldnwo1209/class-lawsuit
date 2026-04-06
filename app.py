import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일
ACCUSE_FILE = 'accusations_mobile_v1.csv'

def load_data():
    if os.path.exists(ACCUSE_FILE):
        return pd.read_csv(ACCUSE_FILE)
    else:
        return pd.DataFrame(columns=['접수번호', '날짜', '피고소인', '사건내용', '추가설명', '상태'])

def save_data(df):
    df.to_csv(ACCUSE_FILE, index=False)

if 'accuse_db' not in st.session_state:
    st.session_state.accuse_db = load_data()

# --- 모바일 최적화 설정 ---
st.set_page_config(page_title="학급 고소장", layout="centered") # 모바일은 중앙 집중형이 필수

# CSS를 이용해 모바일 버튼 크기와 폰트 가독성 향상
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ 학급 고소장 접수")

# 모바일 하단 탭 메뉴처럼 작동하도록 구성
menu = st.radio("메뉴 선택", ["📝 고소장 작성", "🔒 인권예절부 관리"], horizontal=True)

st.divider()

# --- 1. 고소장 작성 (모바일 최적화) ---
if menu == "📝 고소장 작성":
    st.subheader("신고서 작성")
    with st.container():
        target = st.text_input("👤 피고소인 (누구인가요?)", placeholder="이름을 입력하세요")
        content = st.text_area("📄 사건 내용", placeholder="어떤 일이 있었는지 상세히 적어주세요", height=150)
        
        with st.expander("➕ 증거 첨부 (선택)"):
            evidence_text = st.text_area("글로 쓰는 증거", placeholder="대화 내용 등")
            evidence_img = st.file_uploader("사진 업로드", type=['png', 'jpg', 'jpeg'])
        
        if st.button("🚀 고소장 제출하기"):
            if target and content:
                new_idx = len(st.session_state.accuse_db) + 1
                new_data = {
                    '접수번호': f"CASE-{new_idx:03d}",
                    '날짜': datetime.now().strftime("%m-%d %H:%M"),
                    '피고소인': target,
                    '사건내용': content,
                    '추가설명': evidence_text if evidence_text else "없음",
                    '상태': '검토 대기'
                }
                st.session_state.accuse_db = pd.concat([st.session_state.accuse_db, pd.DataFrame([new_data])], ignore_index=True)
                save_data(st.session_state.accuse_db)
                st.balloons()
                st.success("접수되었습니다!")
            else:
                st.error("이름과 내용을 입력해주세요.")

# --- 2. 인권예절부 관리 (모바일 카드형 UI) ---
else:
    st.subheader("관리자 모드")
    admin_pw = st.text_input("비밀번호 입력", type="password")
    
    if admin_pw == "12345":
        if not st.session_state.accuse_db.empty:
            # 모바일에서는 표(Table)가 보기 불편하므로 사건 선택 후 수정하는 방식 채택
            st.write("---")
            case_list = st.session_state.accuse_db['접수번호'].tolist()
            selected_case = st.selectbox("검토할 사건 선택", case_list[::-1]) # 최신순
            
            idx = st.session_state.accuse_db[st.session_state.accuse_db['접수번호'] == selected_case].index[0]
            case_info = st.session_state.accuse_db.loc[idx]
            
            # 카드형 상세 보기
            st.info(f"**상태: {case_info['상태']}**\n\n**대상:** {case_info['피고소인']}\n\n**내용:** {case_info['사건내용']}")
            
            if case_info['추가설명'] != "없음":
                st.warning(f"**추가 증거:** {case_info['추가설명']}")
            
            st.write("---")
            # 버튼식 상태 변경
            st.write("📍 상태 변경하기")
            new_status = st.selectbox("변경할 상태 선택", ["검토 대기", "재판 회부", "기각", "처리 완료"], key="status_select")
            
            if st.button("✅ 상태 업데이트"):
                st.session_state.accuse_db.at[idx, '상태'] = new_status
                save_data(st.session_state.accuse_db)
                st.success("변경되었습니다!")
                st.rerun()
        else:
            st.write("접수된 사건이 없습니다.")
