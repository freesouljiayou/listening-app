import streamlit as st
import google.generativeai as genai
import os

# --- 頁面設定 ---
st.set_page_config(page_title="消防聽力特訓 (手機適配版)", page_icon="🎧", layout="centered")

# ==========================================
# 🎨 CSS 微調區 (只做必要的優化，不破壞版面)
# ==========================================
st.markdown("""
    <style>
    /* 1. 優化錄音區塊：不強制放大，改為適應螢幕寬度 */
    div[data-testid="stAudioInput"] {
        width: 100% !important; /* 強制寬度與螢幕同寬 */
        margin-top: 10px;
    }
    
    /* 讓錄音按鈕好按一點，增加一點點內距，但不要放大整個元件 */
    div[data-testid="stAudioInput"] button {
        min-height: 50px; /* 確保按鈕有一定高度 */
    }

    /* 2. 中間的「呼叫 AI」按鈕：藍色大按鈕，好按且顯眼 */
    div.stButton > button {
        width: 100%;
        height: 70px; /* 高度夠高，手指好點 */
        background-color: #007BFF;
        color: white;
        font-size: 22px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0px;
    }
    
    /* 3. 上傳區文字置中優化 */
    .upload-label {
        text-align: center;
        font-weight: 600;
        color: #444;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 安全的 API Key 讀取 ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ 請設定 API Key")
    st.stop()
genai.configure(api_key=api_key)

# ==========================================
# 📱 APP 介面佈局
# ==========================================

st.title("🎧 英文聽力解題")

# --- 1. 最上面：錄音區 (標準樣式，自動適配手機) ---
st.markdown("### 1. 錄製聲音")
# 這會顯示標準的錄音條，不會超出畫面
audio_input = st.audio_input("點擊錄音")

if audio_input:
    # 這裡顯示一個小的成功訊息就好，不顯示播放器佔空間
    st.success("✅ 錄音完成") 
    # 如果你想聽錄好的聲音，把下面這行註解打開：
    # st.audio(audio_input)

st.markdown("---")

# --- 2. 中間：解題按鈕 ---
start_button = st.button("🚀 呼叫 AI 解題")

st.markdown("---")

# --- 3. 最下面：照片區 (左右分開) ---
st.markdown("### 2. 提供題目")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='upload-label'>📸 開啟相機</div>", unsafe_allow_html=True)
    camera_file = st.camera_input("拍照", label_visibility="collapsed")

with col2:
    st.markdown("<div class='upload-label'>📂 上傳檔案</div>", unsafe_allow_html=True)
    upload_file = st.file_uploader("檔案", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# 邏輯判斷
final_image = camera_file if camera_file else upload_file

# ==========================================
# 🧠 AI 處理邏輯
# ==========================================

if start_button:
    if not audio_input:
        st.warning("⚠️ 第一步還沒做：請先錄音！")
    elif not final_image:
        st.warning("⚠️ 第二步還沒做：請提供題目照片！")
    else:
        with st.spinner("Gemini 2.5 正在分析中..."):
            try:
                # 準備資料
                image_bytes = final_image.getvalue()
                audio_bytes = audio_input.getvalue()

                # 使用 Gemini 2.5 Flash
                model = genai.GenerativeModel('gemini-2.5-flash')

                prompt = """
                你是一個英文檢定考試專家。
                請參考附帶的【圖片】(考題選項) 以及【聲音】(聽力內容)。
                
                任務：
                1. 仔細聆聽聲音內容。
                2. 閱讀圖片中的文字選項。
                3. 選出正確答案。
                
                請回傳：
                - 正確選項 (A/B/C/D)
                - 聽力重點摘要 (英文原文+中文翻譯)
                - 解析 (為什麼選這個答案)
                """
                
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes},
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
                st.success("分析完成！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"發生錯誤：{e}")