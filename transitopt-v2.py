import streamlit as st
import pandas as pd
import networkx as nx
import requests
from datetime import datetime

# 1. 頁面設定
st.set_page_config(page_title="HK TransitOpt - 全港路線規劃系統", page_icon="🇭🇰", layout="wide")

st.title("HK TransitOpt - 全港跨交通工具最佳路線規劃器")
st.write("涵蓋港鐵全綫、九巴及城巴網路，利用 **NetworkX (Dijkstra 演算法)** 自動推算最快轉乘方案。")

st.divider()

# 2. 建立全港交通網絡圖
@st.cache_data
def build_full_hk_network():
    G = nx.DiGraph()
    
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
        
        # 屯馬綫
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

    # [資料集 2] 主要巴士路線
    bus_edges = [
        ("彩虹", "香港科技大學 (HKUST)", 15, "九巴 91M"),
        ("鑽石山", "香港科技大學 (HKUST)", 20, "九巴 91M"),
        ("坑口", "香港科技大學 (HKUST)", 10, "九巴 91M"),
        ("寶琳", "香港科技大學 (HKUST)", 12, "九巴 91M"),
        ("調景嶺", "香港科技大學 (HKUST)", 18, "九巴 792M"),
        ("觀塘", "中環", 35, "城巴/九巴 619"),
        ("觀塘", "銅鑼灣", 30, "城巴/九巴 619"),
        ("旺角", "灣仔", 20, "九巴/城巴 102"),
        ("旺角", "銅鑼灣", 22, "九巴/城巴 102"),
        ("屯門", "灣仔", 50, "城巴 962X"),
        ("屯門", "中環", 45, "城巴 962X"),
        ("元朗", "金鐘", 45, "九巴 968"),
        ("沙田", "中環", 40, "九巴 182")
    ]

    for u, v, weight, line in mtr_edges + bus_edges:
        G.add_edge(u, v, weight=weight, line=line)
        G.add_edge(v, u, weight=weight, line=line)
        
    return G

# 3. 核心優化演算法：路徑壓縮 (Path Compression Algorithm)
def compress_path(G, path):
    """
    將連續相同路線的路段合併，只保留【上車點】與【落車點】，並計算中間經過的站數與總時間。
    """
    if len(path) < 2:
        return []
    
    compressed_steps = []
    
    current_board_station = path[0]  # 當前乘車點 (上車點)
    current_line = None
    accumulated_time = 0
    passed_stations_count = 0
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = G.get_edge_data(u, v)
        line = edge_data['line']
        duration = edge_data['weight']
        
        # 第一次進入或路線改變 (換乘)
        if current_line is None:
            current_line = line
            accumulated_time += duration
            passed_stations_count += 1
        elif line == current_line:
            # 同一條路線，累加時間與站數
            accumulated_time += duration
            passed_stations_count += 1
        else:
            # 路線變更，結算上一段車程
            compressed_steps.append({
                "上車站 (Boarding)": current_board_station,
                "落車站 (Alighting)": u,
                "搭乘交通工具 / 路線": current_line,
                "車程時間": f"約 {accumulated_time} 分鐘",
                "經過站數": f"{passed_stations_count} 站"
            })
            # 重置為新路線
            current_board_station = u
            current_line = line
            accumulated_time = duration
            passed_stations_count = 1
            
    # 結算最後一段車程
    compressed_steps.append({
        "上車站 (Boarding)": current_board_station,
        "落車站 (Alighting)": path[-1],
        "搭乘交通工具 / 路線": current_line,
        "車程時間": f"約 {accumulated_time} 分鐘",
        "經過站數": f"{passed_stations_count} 站"
    })
    
    return compressed_steps

G = build_full_hk_network()
all_stations = sorted(list(G.nodes()))

# 4. UI 介面
col1, col2 = st.columns(2)
with col1:
    start_node = st.selectbox("📍 出發車站 / 地點:", options=all_stations, index=all_stations.index("屯門") if "屯門" in all_stations else 0)
with col2:
    end_node = st.selectbox("🎯 目的地車站 / 校園:", options=all_stations, index=all_stations.index("香港科技大學 (HKUST)") if "香港科技大學 (HKUST)" in all_stations else 1)

if st.button("🗺️ 計算全港最佳路線", type="primary"):
    if start_node == end_node:
        st.warning("起點與目的地不能相同！")
    else:
        try:
            # Dijkstra 最短路徑
            raw_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            total_time = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
            
            st.success(f"🎉 已為你規劃最佳路線！預估總車程時間： **{total_time} 分鐘**")
            
            # 執行路徑壓縮
            compressed_steps = compress_path(G, raw_path)
            
            st.subheader("🧭 轉乘路線明細 (只顯示上落車點)：")
            
            # 格式化輸出
            bus_to_fetch = []
            for idx, step in enumerate(compressed_steps, 1):
                line = step["搭乘交通工具 / 路線"]
                board = step["上車站 (Boarding)"]
                alight = step["落車站 (Alighting)"]
                time_str = step["車程時間"]
                count_str = step["經過站數"]
                
                # 乾淨、精緻的 Markdown 卡片樣式
                st.markdown(f"""
                #### **Step {idx}: 乘搭 {line}**
                * 🟢 **上車**：`{board}`
                * 🔴 **落車**：`{alight}` (經過 {count_str}，{time_str})
                """)
                st.divider()
                
                if "九巴" in line:
                    bus_no = line.split(" ")[1]
                    bus_to_fetch.append(bus_no)
                    
            # 5. 實時 API 連動 (抓取上車站的九巴倒數)
            if bus_to_fetch:
                st.subheader("⏱️ 相關九巴路線實時到站時間 (Live ETA)")
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
        
