import streamlit as st
import pandas as pd
import networkx as nx
import requests
from datetime import datetime

# 1. 頁面設定
st.set_page_config(page_title="HK TransitOpt - 全港路線規劃系統", page_icon="🇭🇰", layout="wide")

st.title("🇭🇰 HK TransitOpt - 全港跨交通工具最佳路線規劃器")
st.write("涵蓋港鐵全綫、九巴及城巴網路，利用 **NetworkX (Dijkstra 演算法)** 自動推算最快轉乘方案。")

st.divider()

# 2. 建立全港交通網絡圖（包含港鐵各綫與主要巴士線）
@st.cache_data
def build_full_hk_network():
    G = nx.DiGraph() # 有向圖 (Directed Graph)
    
    # [資料集 1] 港鐵全網絡 (MTR Network)
    mtr_edges = [
        # 觀塘綫
        ("調景嶺", "油塘", 3, "MTR 觀塘綫"), ("油塘", "藍田", 2, "MTR 觀塘綫"), 
        ("藍田", "觀塘", 2, "MTR 觀塘綫"), ("觀塘", "牛頭角", 2, "MTR 觀塘綫"),
        ("牛頭角", "九龍灣", 2, "MTR 觀塘綫"), ("九龍灣", "彩虹", 3, "MTR 觀塘綫"),
        ("彩虹", "鑽石山", 2, "MTR 觀塘綫"), ("鑽石山", "黃大仙", 2, "MTR 觀塘綫"),
        ("黃大仙", "樂富", 2, "MTR 觀塘綫"), ("樂富", "九龍塘", 2, "MTR 觀塘綫"),
        ("九龍塘", "石硤尾", 2, "MTR 觀塘綫"), ("石硤尾", "太子", 2, "MTR 觀塘綫"),
        ("太子", "旺角", 2, "MTR 觀塘綫"), ("旺角", "油麻地", 2, "MTR 觀塘綫"),
        ("油麻地", "何文田", 3, "MTR 觀塘綫"), ("何文田", "黃埔", 2, "MTR 觀塘綫"),
        
        # 荃灣綫
        ("荃灣", "大窩口", 3, "MTR 荃灣綫"), ("大窩口", "葵興", 2, "MTR 荃灣綫"),
        ("葵興", "葵芳", 2, "MTR 荃灣綫"), ("葵芳", "荔景", 2, "MTR 荃灣綫"),
        ("荔景", "美孚", 3, "MTR 荃灣綫"), ("美孚", "荔枝角", 2, "MTR 荃灣綫"),
        ("荔枝角", "長沙灣", 2, "MTR 荃灣綫"), ("長沙灣", "深水埗", 2, "MTR 荃灣綫"),
        ("深水埗", "太子", 2, "MTR 荃灣綫"), ("太子", "旺角", 2, "MTR 荃灣綫"),
        ("旺角", "油麻地", 2, "MTR 荃灣綫"), ("油麻地", "佐敦", 2, "MTR 荃灣綫"),
        ("佐敦", "尖沙咀", 2, "MTR 荃灣綫"), ("尖沙咀", "金鐘", 4, "MTR 荃灣綫"),
        ("金鐘", "中環", 2, "MTR 荃灣綫"),

        # 東鐵綫
        ("金鐘", "會展", 3, "MTR 東鐵綫"), ("會展", "紅磡", 5, "MTR 東鐵綫"),
        ("紅磡", "旺角東", 4, "MTR 東鐵綫"), ("旺角東", "九龍塘", 4, "MTR 東鐵綫"),
        ("九龍塘", "大圍", 5, "MTR 東鐵綫"), ("大圍", "沙田", 3, "MTR 東鐵綫"),
        ("沙田", "火炭", 4, "MTR 東鐵綫"), ("火炭", "大學 (CUHK)", 5, "MTR 東鐵綫"),
        ("大學 (CUHK)", "大埔墟", 6, "MTR 東鐵綫"), ("大埔墟", "太和", 3, "MTR 東鐵綫"),
        ("太和", "粉嶺", 6, "MTR 東鐵綫"), ("粉嶺", "上水", 3, "MTR 東鐵綫"),
        ("上水", "落馬洲", 10, "MTR 東鐵綫"), ("上水", "羅湖", 7, "MTR 東鐵綫"),
        
        # 港島綫
        ("堅尼地城", "香港大學 (HKU)", 2, "MTR 港島綫"), ("香港大學 (HKU)", "西營盤", 2, "MTR 港島綫"),
        ("西營盤", "上環", 2, "MTR 港島綫"), ("上環", "中環", 2, "MTR 港島綫"),
        ("中環", "金鐘", 2, "MTR 港島綫"), ("金鐘", "灣仔", 2, "MTR 港島綫"),
        ("灣仔", "銅鑼灣", 2, "MTR 港島綫"), ("銅鑼灣", "天后", 2, "MTR 港島綫"),
        ("天后", "炮台山", 2, "MTR 港島綫"), ("炮台山", "北角", 2, "MTR 港島綫"),
        ("北角", "鰂魚涌", 2, "MTR 港島綫"), ("鰂魚涌", "太古", 2, "MTR 港島綫"),
        ("太古", "西灣河", 2, "MTR 港島綫"), ("西灣河", "筲箕灣", 2, "MTR 港島綫"),
        ("筲箕灣", "柴灣", 3, "MTR 港島綫"),
        
        # 屯馬綫 (部分重點站)
        ("屯門", "兆康", 3, "MTR 屯馬綫"), ("兆康", "天水圍", 5, "MTR 屯馬綫"),
        ("天水圍", "朗屏", 3, "MTR 屯馬綫"), ("朗屏", "元朗", 2, "MTR 屯馬綫"),
        ("元朗", "錦上路", 4, "MTR 屯馬綫"), ("錦上路", "荃灣西", 9, "MTR 屯馬綫"),
        ("荃灣西", "美孚", 6, "MTR 屯馬綫"), ("美孚", "南昌", 4, "MTR 屯馬綫"),
        ("南昌", "柯士甸", 4, "MTR 屯馬綫"), ("柯士甸", "尖東", 3, "MTR 屯馬綫"),
        ("尖東", "紅磡", 2, "MTR 屯馬綫"), ("紅磡", "何文田", 3, "MTR 屯馬綫"),
        ("何文田", "土瓜灣", 3, "MTR 屯馬綫"), ("土瓜灣", "宋皇臺", 2, "MTR 屯馬綫"),
        ("宋皇臺", "啟德", 2, "MTR 屯馬綫"), ("啟德", "鑽石山", 3, "MTR 屯馬綫"),
        ("鑽石山", "大圍", 6, "MTR 屯馬綫")
    ]

    # [資料集 2] 主要巴士路線 (KMB / Citybus)
    bus_edges = [
        # 九巴科大專綫
        ("彩虹", "香港科技大學 (HKUST)", 15, "九巴 91M"),
        ("鑽石山", "香港科技大學 (HKUST)", 20, "九巴 91M"),
        ("坑口", "香港科技大學 (HKUST)", 10, "九巴 91M"),
        ("寶琳", "香港科技大學 (HKUST)", 12, "九巴 91M"),
        ("調景嶺", "香港科技大學 (HKUST)", 18, "九巴 792M"),
        
        # 過海巴士綫
        ("觀塘", "中環", 35, "城巴/九巴 619"),
        ("觀塘", "銅鑼灣", 30, "城巴/九巴 619"),
        ("旺角", "灣仔", 20, "九巴/城巴 102"),
        ("旺角", "銅鑼灣", 22, "九巴/城巴 102"),
        ("屯門", "灣仔", 50, "城巴 962X"),
        ("屯門", "中環", 45, "城巴 962X"),
        ("元朗", "金鐘", 45, "九巴 968"),
        ("沙田", "中環", 40, "九巴 182")
    ]

    # 將數據雙向加入 Graph (雙向通行)
    for u, v, weight, line in mtr_edges + bus_edges:
        G.add_edge(u, v, weight=weight, line=line)
        G.add_edge(v, u, weight=weight, line=line) # 反向車程
        
    return G

G = build_full_hk_network()
all_stations = sorted(list(G.nodes()))

# 3. 介面選擇
col1, col2 = st.columns(2)
with col1:
    start_node = st.selectbox("📍 出發車站 / 地點:", options=all_stations, index=all_stations.index("屯門") if "屯門" in all_stations else 0)
with col2:
    end_node = st.selectbox("🎯 目的地車站 / 校園:", options=all_stations, index=all_stations.index("香港科技大學 (HKUST)") if "香港科技大學 (HKUST)" in all_stations else 1)

if st.button("🗺️ 計算全港最佳跨交通路線", type="primary"):
    if start_node == end_node:
        st.warning("起點與目的地不能相同！")
    else:
        try:
            # 4. 使用 NetworkX 執行 Dijkstra 最短路徑演算法
            shortest_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            total_time = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
            
            st.success(f"🎉 已為你規劃全港最佳路線！預估總車程時間： **{total_time} 分鐘**")
            
            st.subheader("🧭 轉乘路線明細：")
            
            path_details = []
            bus_to_fetch = []
            
            for i in range(len(shortest_path) - 1):
                u = shortest_path[i]
                v = shortest_path[i+1]
                edge_data = G.get_edge_data(u, v)
                line = edge_data['line']
                duration = edge_data['weight']
                
                path_details.append({
                    "步驟": f"Step {i+1}",
                    "出發地": u,
                    "目的地": v,
                    "建議交通工具 / 路線": line,
                    "預計車程": f"{duration} 分鐘"
                })
                
                if "九巴" in line:
                    bus_no = line.split(" ")[1]
                    bus_to_fetch.append(bus_no)
            
            st.table(pd.DataFrame(path_details))
            
            # 5. 連動實時 API (若有九巴路線)
            if bus_to_fetch:
                st.divider()
                st.subheader("⏱️ 路線中涉及之九巴實時班次 (Live ETA)")
                for b_no in set(bus_to_fetch):
                    api_url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{b_no}/1"
                    try:
                        res = requests.get(api_url, timeout=3)
                        if res.status_code == 200:
                            data = res.json().get("data", [])
                            if data:
                                eta_rows = []
                                now = datetime.now()
                                for item in data[:3]:
                                    eta_str = item.get("eta")
                                    if eta_str:
                                        eta_t = datetime.fromisoformat(eta_str)
                                        diff = int((eta_t - now.astimezone()).total_seconds() / 60)
                                        eta_rows.append({"目的地": item.get("dest_tc"), "預計到站": eta_t.strftime("%H:%M"), "倒數": f"{diff} 分鐘" if diff > 0 else "即將到站"})
                                st.write(f"🚍 **九巴 {b_no}** 即時班次：")
                                st.dataframe(pd.DataFrame(eta_rows), use_container_width=True)
                    except Exception:
                        pass

        except nx.NetworkXNoPath:
            st.error("抱歉，目前數據庫中找不到連接這兩地的路線。")
