import streamlit as st
import google.generativeai as genai
import os

# --- 頁面設定 ---
st.set_page_config(page_title="消防聽力特訓 (極簡版)", page_icon="🎧", layout="centered")

# ==========================================
# 🎨 CSS 優化區
# ==========================================
st.markdown("""
    <style>
    /* 1. 錄音區：全寬度 */
    div[data-testid="stAudioInput"] {
        width: 100% !important;
        margin-top: 5px;
    }
    
    div[data-testid="stAudioInput"] button {
        min-height: 50px;
    }

    /* 2. 中間的「呼叫 AI」按鈕：藍色大按鈕 */
    div.stButton > button {
        width: 100%;
        height: 70px;
        background-color: #007BFF;
        color: white;
        font-size: 22px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0px;
    }
    
    /* 3. 上傳區說明文字 */
    .upload-hint {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
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

# --- 1. 最上面：錄音區 ---
st.markdown("### 1. 錄製聲音")
audio_input = st.audio_input("點擊錄音")

# --- 2. 中間：解題按鈕 ---
start_button = st.button("🚀 呼叫 AI 解題")

# 【答案顯示區】放在按鈕正下方
result_container = st.container()

st.markdown("---")

# --- 3. 最下面：照片區 (整合版) ---
st.markdown("### 2. 提供題目")

st.markdown("<div class='upload-hint'>👇 點擊下方框框 -> 選擇「拍照」或是「圖庫」</div>", unsafe_allow_html=True)

# 這裡合併成一個單一的上傳元件
img_file = st.file_uploader("上傳題目", type=["jpg", "png", "jpeg"], label_visibility="collapsed")


# ==========================================
# 🧠 AI 處理邏輯
# ==========================================

if start_button:
    # 檢查是否缺資料
    if not audio_input:
        st.warning("⚠️ 請先錄音！")
    elif not img_file:
        st.warning("⚠️ 請提供照片！(點擊下方框框 -> 選擇相機即可變焦)")
    else:
        # 使用容器顯示結果
        with result_container:
            with st.spinner("Gemini 2.5 正在分析中..."):
                try:
                    # 準備資料
                    image_bytes = img_file.getvalue()
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
                    
                    # 顯示結果
                    st.success("✅ 分析完成！")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"發生錯誤：{e}")