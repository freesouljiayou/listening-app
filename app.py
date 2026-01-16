import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="API 健檢中心", page_icon="🏥")
st.title("🏥 API 鑰匙與環境健檢")

# 1. 檢查鑰匙是否存在
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success(f"✅ 步驟 1: 成功讀取到 Secrets 鑰匙 (開頭是: {api_key[:5]}...)")
    genai.configure(api_key=api_key)
else:
    st.error("❌ 步驟 1 失敗: 找不到 API Key，請檢查 Secrets 設定。")
    st.stop()

# 2. 檢查套件版本 (這很重要，舊版不支援 Flash)
try:
    import google.generativeai as ai_lib
    version = ai_lib.__version__
    st.info(f"ℹ️ 目前安裝的 google-generativeai 版本: {version}")
except:
    st.warning("無法偵測版本號")

# 3. 實際連線測試
if st.button("🚀 開始連線測試"):
    try:
        st.write("正在詢問 Google 你的鑰匙能用哪些模型...")
        
        # 列出所有可用模型
        available_models = []
        for m in genai.list_models():
            available_models.append(m.name)
            
        # 顯示清單
        st.json(available_models)
        
        # 判斷結果
        target_model = "models/gemini-1.5-flash"
        
        if target_model in available_models:
            st.balloons()
            st.success(f"🎉 恭喜！你的鑰匙 **支援** {target_model}！")
            st.markdown("### 結論：")
            st.markdown("既然鑰匙沒問題，那之前的錯誤 99% 是因為 `requirements.txt` 裡面的版本太舊。請記得去更新 requirements.txt。")
        else:
            st.error(f"❌ 慘！你的鑰匙清單裡 **找不到** {target_model}。")
            st.markdown("### 結論：")
            st.markdown("你的這把鑰匙權限不足 (可能是舊的 Cloud Key)。**請直接去 Google AI Studio 申請一把新的**，最快解決！")

    except Exception as e:
        st.error(f"❌ 連線發生致命錯誤：{e}")
        st.markdown("這通常代表你的鑰匙無效，或是沒有開啟 API 權限。")
