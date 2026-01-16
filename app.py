import streamlit as st
import google.generativeai as genai

# ==========================================
# 👇 請把你在第一步複製的 Key 貼在下面引號裡面
# ==========================================
GOOGLE_API_KEY = "AIzaSyCQc1xJNlcNlh5MxxfIhtiPyxM2bSe158U"

# 設定 Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# 設定 APP 的外觀
st.set_page_config(page_title="聽力救星", page_icon="🎧")
st.title("🎧 英文聽力自動解題")
st.success("準備好了！請錄音並拍照。")

# --- 1. 錄音區 ---
st.header("1. 錄音 (Listening)")
# 這是錄音按鈕
audio_input = st.audio_input("請按下紅色麥克風按鈕錄音")

if audio_input:
    st.audio(audio_input) # 讓你自己聽聽看有沒有錄清楚

st.markdown("---") # 分隔線

# --- 2. 拍照區 ---
st.header("2. 拍照 (Reading)")
# 這是上傳圖片按鈕
img_file = st.file_uploader("請拍攝題目選項並上傳", type=["jpg", "png", "jpeg"])

if img_file:
    st.image(img_file, caption="你的題目", use_container_width=True)

st.markdown("---")

# --- 3. 解題區 ---
st.header("3. 答案")

# 當你按下按鈕時，程式才會開始跑
if st.button("🔥 呼叫 AI 幫我解題", type="primary"):
    
    # 檢查有沒有漏掉東西
    if not audio_input or not img_file:
        st.warning("⚠️ 等等！你要先「錄音」並且「上傳照片」我才能幫你喔！")
    
    # 檢查有沒有填寫 API Key
    elif "這裡貼上" in GOOGLE_API_KEY:
        st.error("⚠️ 程式碼第 7 行的 API Key 還沒填喔！請回去修改 app.py")
        
    else:
        # 顯示轉圈圈，代表 AI 正在思考
        with st.spinner("正在聽聲音 + 看題目... 請稍等..."):
            try:
                # 準備要丟給 AI 的資料
                image_bytes = img_file.getvalue()
                audio_bytes = audio_input.getvalue()

                # 使用 Gemini 1.5 Flash 模型 (速度快、免費額度高)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # 給 AI 的指令 (Prompt)
                prompt = """
                請扮演英文家教。
                1. 聆聽附帶的音檔。
                2. 閱讀圖片中的考題選項。
                3. 告訴我正確答案是哪一個 (A/B/C/D)。
                4. 給我一個簡短的解釋，告訴我為什麼選這個。
                """
                
                # 發送給 Google
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes},
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
                # 顯示結果
                st.info("✅ 分析完成！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"發生錯誤，可能是 Key 有問題或是檔案太大。\n錯誤訊息：{e}")