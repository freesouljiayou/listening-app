import streamlit as st
import google.generativeai as genai
import os

# --- 頁面設定 ---
st.set_page_config(page_title="聽力解題神器", page_icon="🎧")

# --- 安全的 API Key 讀取 ---
# 程式會去檢查雲端的「保險箱 (Secrets)」有沒有鑰匙
# 這樣就算程式碼被別人看到，你的鑰匙也是安全的
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # 這是為了防呆，如果沒設定好會跳出紅字警告
    st.error("⚠️ 錯誤：找不到 API Key。請在 Streamlit Cloud 的 Secrets 欄位設定 GOOGLE_API_KEY。")
    st.stop()

# 設定 Google AI
genai.configure(api_key=api_key)

# --- APP 介面開始 ---
st.title("🎧 英文聽力自動解題")
st.caption("流程：錄音 (Listening) + 拍照 (Reading) -> AI 老師解題")

# 1. 錄音區
st.header("1. 錄製題目聲音")
audio_input = st.audio_input("按下紅色麥克風開始錄音")

if audio_input:
    st.audio(audio_input)

st.markdown("---")

# 2. 拍照區
st.header("2. 上傳選項照片")
img_file = st.file_uploader("拍攝題目選項", type=["jpg", "png", "jpeg"])

if img_file:
    st.image(img_file, caption="題目預覽", use_container_width=True)

st.markdown("---")

# 3. 解題區
if st.button("🔥 呼叫 AI 解題", type="primary"):
    
    if not audio_input or not img_file:
        st.warning("請記得「錄音」並且「上傳照片」喔！")
    else:
        with st.spinner("AI 正在聆聽並思考答案中..."):
            try:
                # 準備資料
                image_bytes = img_file.getvalue()
                audio_bytes = audio_input.getvalue()

                # 使用 Gemini 1.5 Flash (快速、多模態)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # 給 AI 的指令
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
                
                # 發送請求
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes},
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
                # 顯示結果
                st.success("分析完成！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"發生錯誤：{e}")
