import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 頁面設定
st.set_page_config(page_title="香港巴士/港鐵到站助手", page_icon="🚌", layout="wide")

st.title("🚌 香港專營巴士實時到站查詢系統")
st.write("直接串接九巴 (KMB) Open Data API，提供精確的實時車次到站倒數。")

st.divider()

col1, col2 = st.columns(2)
with col1:
    route_input = st.text_input("輸入九巴路線號碼 (例如: 1A, 271, 91M, 290A):", value="1A").upper().strip()
with col2:
    bound_option = st.selectbox("選擇方向:", ["去程 / Outbound", "回程 / Inbound"])

bound_code = "outbound" if "Outbound" in bound_option else "inbound"

if st.button("🔍 查詢實時班次", type="primary"):
    api_url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route_input}/1"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", [])
            filtered_data = [item for item in data if item.get("dir") == ("O" if bound_code == "outbound" else "I")]
            
            if filtered_data:
                eta_list = []
                now = datetime.now()
                
                for item in filtered_data[:8]: # 顯示前 8 筆到站紀錄
                    eta_str = item.get("eta")
                    remark = item.get("rmk_tc", "")
                    
                    if eta_str:
                        eta_time = datetime.fromisoformat(eta_str)
                        diff_minutes = int((eta_time - now.astimezone()).total_seconds() / 60)
                        count_down = f"{diff_minutes} 分鐘" if diff_minutes > 0 else "即將到站"
                        
                        eta_list.append({
                            "目的地": item.get("dest_tc"),
                            "預計到站時間": eta_time.strftime("%H:%M:%S"),
                            "倒數時間": count_down,
                            "備註": remark
                        })
                
                if eta_list:
                    st.success(f"成功取得路線 **{route_input}** 的最新班次數據！")
                    st.dataframe(pd.DataFrame(eta_list), use_container_width=True)
                else:
                    st.warning("目前無預計到站班次數據。")
            else:
                st.error(f"找不到路線 **{route_input}** 的數據，請檢查路線號碼或方向。")
        else:
            st.error("API 連線失敗，請檢查網路。")
    except Exception as e:
        st.error(f"連線錯誤: {e}")
        