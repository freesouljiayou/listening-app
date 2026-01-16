import streamlit as st
import google.generativeai as genai
import os

# --- 頁面設定 ---
st.set_page_config(page_title="聽力解題神器 (2026版)", page_icon="🎧")

# --- 安全的 API Key 讀取 ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ 錯誤：找不到 API Key。請在 Streamlit Cloud 的 Secrets 欄位設定 GOOGLE_API_KEY。")
    st.stop()

# 設定 Google AI
genai.configure(api_key=api_key)

# --- APP 介面 ---
st.title("🎧 英文聽力自動解題 (Gemini 2.5)")
st.caption("目前使用模型：Gemini 2.5 Flash (最新極速版)")

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
        with st.spinner("Gemini 2.5 正在極速分析中..."):
            try:
                # 準備資料
                image_bytes = img_file.getvalue()
                audio_bytes = audio_input.getvalue()

                # === 關鍵修改：使用你的清單裡有的 Gemini 2.5 Flash ===
                model = genai.GenerativeModel('gemini-2.5-flash')

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
