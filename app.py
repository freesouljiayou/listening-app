import streamlit as st
import google.generativeai as genai
import os

# --- 頁面設定 ---
st.set_page_config(page_title="聽力解題神器 (手機版)", page_icon="🎧", layout="centered")

# --- 注入 CSS 樣式 (魔改介面) ---
st.markdown("""
    <style>
    /* 1. 強制放大錄音介面 (放大 1.3 倍) */
    div[data-testid="stAudioInput"] {
        transform: scale(1.3);
        transform-origin: center;
        margin-top: 20px;
        margin-bottom: 30px; /* 增加下方留白 */
    }

    /* 2. 放大「呼叫 AI」按鈕 */
    div.stButton > button {
        width: 100%;         /* 寬度填滿 */
        height: 70px;        /* 高度加高 */
        font-size: 24px;     /* 字變大 */
        font-weight: bold;
        border-radius: 12px; /* 圓角 */
        background-color: #FF4B4B; /* 鮮艷紅 */
        color: white;
    }
    
    /* 3. 調整相機與上傳區塊的標題 */
    .upload-header {
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 安全的 API Key 讀取 ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ 錯誤：找不到 API Key。請在 Streamlit Cloud 的 Secrets 欄位設定 GOOGLE_API_KEY。")
    st.stop()

genai.configure(api_key=api_key)

# ==========================================
# 📱 APP 介面開始
# ==========================================

st.title("🎧 英文聽力解題")

# --- 1. 最上面：錄音區 ---
st.info("👇 1. 先錄音 (按鈕已放大)")
audio_input = st.audio_input("請錄下考題聲音")

st.markdown("---")

# --- 2. 中間：解題按鈕 ---
# 依照你的需求，按鈕放在中間
# 我們使用 st.container 來區隔
with st.container():
    # 建立一個佔位符，如果使用者還沒拍照，這裡之後可以顯示警告
    msg_placeholder = st.empty()
    
    # 這就是那顆超大的按鈕
    start_button = st.button("🔥 呼叫 AI 開始解題")

st.markdown("---")

# --- 3. 最下面：照片區 (左右分開) ---
st.info("👇 2. 再提供照片 (二選一)")

# 建立左右兩欄
col1, col2 = st.columns(2)

img_file = None
camera_file = None
upload_file = None

with col1:
    st.markdown("<div class='upload-header'>📸 現場拍照</div>", unsafe_allow_html=True)
    # camera_input 會直接在網頁上打開相機視窗
    camera_file = st.camera_input("拍選項", label_visibility="collapsed")

with col2:
    st.markdown("<div class='upload-header'>📂 上傳檔案</div>", unsafe_allow_html=True)
    # file_uploader 讓你選相簿
    upload_file = st.file_uploader("選圖片", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# 邏輯判斷：使用者到底用了哪一種方式？
# 如果有用相機，就用相機的圖；不然就看有沒有上傳的圖
final_image = camera_file if camera_file else upload_file


# ==========================================
# 🧠 處理邏輯 (當按鈕被按下時)
# ==========================================

if start_button:
    # 1. 檢查錄音
    if not audio_input:
        msg_placeholder.warning("⚠️ 記得要先按上面的「錄音」喔！")
    
    # 2. 檢查照片 (相機或上傳只要有一個有東西就可以)
    elif not final_image:
        msg_placeholder.warning("⚠️ 記得在下面「拍照」或「上傳圖片」！")
        
    else:
        # 開始解題
        msg_placeholder.info("🤖 AI 正在聽音辨位中...請稍等")
        
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
            1. 聽聲音內容。
            2. 看圖片中的選項。
            3. 判斷哪個選項是正確答案。
            
            請回傳：
            - 正確選項 (A/B/C/D)
            - 聽力內容摘要 (英文原文+中文翻譯)
            - 解析 (為什麼選這個答案)
            """
            
            with st.spinner("分析中..."):
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes},
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
            st.success("分析完成！")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"發生錯誤：{e}")