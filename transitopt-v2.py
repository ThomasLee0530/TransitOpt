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

# 2. 建立全港交通網絡圖 (包含方向標註)
@st.cache_data
def build_full_hk_network():
    G = nx.DiGraph()
    
    # [資料集 1] 港鐵全網絡 (MTR Network)
    mtr_edges = [
        # 觀塘綫
        ("調景嶺", "油塘", 3, "MTR 觀塘綫", ""), ("油塘", "藍田", 2, "MTR 觀塘綫", ""), 
        ("藍田", "觀塘", 2, "MTR 觀塘綫", ""), ("觀塘", "牛頭角", 2, "MTR 觀塘綫", ""),
        ("牛頭角", "九龍灣", 2, "MTR 觀塘綫", ""), ("九龍灣", "彩虹", 3, "MTR 觀塘綫", ""),
        ("彩虹", "鑽石山", 2, "MTR 觀塘綫", ""), ("鑽石山", "黃大仙", 2, "MTR 觀塘綫", ""),
        ("黃大仙", "樂富", 2, "MTR 觀塘綫", ""), ("樂富", "九龍塘", 2, "MTR 觀塘綫", ""),
        ("九龍塘", "石硤尾", 2, "MTR 觀塘綫", ""), ("石硤尾", "太子", 2, "MTR 觀塘綫", ""),
        ("太子", "旺角", 2, "MTR 觀塘綫", ""), ("旺角", "油麻地", 2, "MTR 觀塘綫", ""),
        ("油麻地", "何文田", 3, "MTR 觀塘綫", ""), ("何文田", "黃埔", 2, "MTR 觀塘綫", ""),
        
        # 荃灣綫
        ("荃灣", "大窩口", 3, "MTR 荃灣綫", ""), ("大窩口", "葵興", 2, "MTR 荃灣綫", ""),
        ("葵興", "葵芳", 2, "MTR 荃灣綫", ""), ("葵芳", "荔景", 2, "MTR 荃灣綫", ""),
        ("荔景", "美孚", 3, "MTR 荃灣綫", ""), ("美孚", "荔枝角", 2, "MTR 荃灣綫", ""),
        ("荔枝角", "長沙灣", 2, "MTR 荃灣綫", ""), ("長沙灣", "深水埗", 2, "MTR 荃灣綫", ""),
        ("深水埗", "太子", 2, "MTR 荃灣綫", ""), ("太子", "旺角", 2, "MTR 荃灣綫", ""),
        ("旺角", "油麻地", 2, "MTR 荃灣綫", ""), ("油麻地", "佐敦", 2, "MTR 荃灣綫", ""),
        ("佐敦", "尖沙咀", 2, "MTR 荃灣綫", ""), ("尖沙咀", "金鐘", 4, "MTR 荃灣綫", ""),
        ("金鐘", "中環", 2, "MTR 荃灣綫", ""),

        # 東鐵綫
        ("金鐘", "會展", 3, "MTR 東鐵綫", ""), ("會展", "紅磡", 5, "MTR 東鐵綫", ""),
        ("紅磡", "旺角東", 4, "MTR 東鐵綫", ""), ("旺角東", "九龍塘", 4, "MTR 東鐵綫", ""),
        ("九龍塘", "大圍", 5, "MTR 東鐵綫", ""), ("大圍", "沙田", 3, "MTR 東鐵綫", ""),
        ("沙田", "火炭", 4, "MTR 東鐵綫", ""), ("火炭", "大學 (CUHK)", 5, "MTR 東鐵綫", ""),
        ("大學 (CUHK)", "大埔墟", 6, "MTR 東鐵綫", ""), ("大埔墟", "太和", 3, "MTR 東鐵綫", ""),
        ("太和", "粉嶺", 6, "MTR 東鐵綫", ""), ("粉嶺", "上水", 3, "MTR 東鐵綫", ""),
        ("上水", "落馬洲", 10, "MTR 東鐵綫", ""), ("上水", "羅湖", 7, "MTR 東鐵綫", ""),
        
        # 屯馬綫
        ("屯門", "兆康", 3, "MTR 屯馬綫", ""), ("兆康", "天水圍", 5, "MTR 屯馬綫", ""),
        ("天水圍", "朗屏", 3, "MTR 屯馬綫", ""), ("朗屏", "元朗", 2, "MTR 屯馬綫", ""),
        ("元朗", "錦上路", 4, "MTR 屯馬綫", ""), ("錦上路", "荃灣西", 9, "MTR 屯馬綫", ""),
        ("荃灣西", "美孚", 6, "MTR 屯馬綫", ""), ("美孚", "南昌", 4, "MTR 屯馬綫", ""),
        ("南昌", "柯士甸", 4, "MTR 屯馬綫", ""), ("柯士甸", "尖東", 3, "MTR 屯馬綫", ""),
        ("尖東", "紅磡", 2, "MTR 屯馬綫", ""), ("紅磡", "何文田", 3, "MTR 屯馬綫", ""),
        ("何文田", "土瓜灣", 3, "MTR 屯馬綫", ""), ("土瓜灣", "宋皇臺", 2, "MTR 屯馬綫", ""),
        ("宋皇臺", "啟德", 2, "MTR 屯馬綫", ""), ("啟德", "鑽石山", 3, "MTR 鑽石山", ""),
        ("鑽石山", "大圍", 6, "MTR 屯馬綫", "")
    ]

    # [資料集 2] 巴士路線 (加上目的地提示 dest)
    bus_edges_one_way = [
        # 彩虹/鑽石山 往 科大 (往寶林方向)
        ("彩虹", "香港科技大學 (HKUST)", 15, "九巴 91M", "寶林"),
        ("鑽石山", "香港科技大學 (HKUST)", 20, "九巴 91M", "寶林"),
        ("坑口", "香港科技大學 (HKUST)", 10, "九巴 91M", "鑽石山"),
        ("寶琳", "香港科技大學 (HKUST)", 12, "九巴 91M", "鑽石山"),
        ("調景嶺", "香港科技大學 (HKUST)", 18, "九巴 792M", "西貢"),
        ("觀塘", "中環", 35, "城巴/九巴 619", "中環"),
        ("旺角", "灣仔", 20, "九巴/城巴 102", "箕灣"),
        ("屯門", "灣仔", 50, "城巴 962X", "銅鑼灣"),
        ("元朗", "金鐘", 45, "九巴 968", "銅鑼灣")
    ]

    # MTR 雙向加入
    for u, v, weight, line, dest in mtr_edges:
        G.add_edge(u, v, weight=weight, line=line, dest=dest)
        G.add_edge(v, u, weight=weight, line=line, dest=dest)
        
    # 巴士特定方向加入
    for u, v, weight, line, dest in bus_edges_one_way:
        G.add_edge(u, v, weight=weight, line=line, dest=dest)
        
    return G

# 3. 路徑壓縮與資訊提取
def compress_path(G, path):
    if len(path) < 2:
        return []
    
    compressed_steps = []
    current_board_station = path[0]
    current_line = None
    target_dest = ""
    accumulated_time = 0
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = G.get_edge_data(u, v)
        line = edge_data['line']
        duration = edge_data['weight']
        dest = edge_data.get('dest', '')
        
        if current_line is None:
            current_line = line
            target_dest = dest
            accumulated_time += duration
        elif line == current_line:
            accumulated_time += duration
        else:
            compressed_steps.append({
                "上車站": current_board_station,
                "落車站": u,
                "路線": current_line,
                "方向": target_dest,
                "車程時間": f"約 {accumulated_time} 分鐘"
            })
            current_board_station = u
            current_line = line
            target_dest = dest
            accumulated_time = duration
            
    compressed_steps.append({
        "上車站": current_board_station,
        "落車站": path[-1],
        "路線": current_line,
        "方向": target_dest,
        "車程時間": f"約 {accumulated_time} 分鐘"
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
            raw_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            total_time = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
            
            st.success(f"🎉 已為你規劃最佳路線！預估總車程時間： **{total_time} 分鐘**")
            
            compressed_steps = compress_path(G, raw_path)
            
            st.subheader("🧭 轉乘路線明細：")
            
            bus_checks = []
            for idx, step in enumerate(compressed_steps, 1):
                line = step["路線"]
                board = step["上車站"]
                alight = step["落車站"]
                time_str = step["車程時間"]
                dest_info = f"（往 {step['方向']} 方向）" if step['方向'] else ""
                
                st.markdown(f"""
                #### **Step {idx}: 乘搭 {line} {dest_info}**
                * 🟢 **上車站**：`{board}`
                * 🔴 **落車站**：`{alight}` ({time_str})
                """)
                st.divider()
                
                if "九巴" in line:
                    bus_no = line.split(" ")[1]
                    bus_checks.append({"route": bus_no, "board": board, "target_dest": step["方向"]})
                    
            # 5. 精準 API 車站與方向過濾
            if bus_checks:
                st.subheader("⏱️ 相關九巴路線實時到站時間 (Live ETA)")
                for item in bus_checks:
                    r_no = item["route"]
                    target_dest = item["target_dest"]
                    board_station = item["board"]
                    
                    api_url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{r_no}/1"
                    try:
                        res = requests.get(api_url, timeout=3)
                        if res.status_code == 200:
                            data = res.json().get("data", [])
                            if data:
                                eta_rows = []
                                now = datetime.now()
                                
                                # 精確過濾：匹配目的地 (例如: 寶林)
                                filtered_eta = [d for d in data if target_dest in d.get("dest_tc", "")] if target_dest else data
                                
                                for eta_item in filtered_eta[:3]:
                                    eta_str = eta_item.get("eta")
                                    if eta_str:
                                        eta_t = datetime.fromisoformat(eta_str)
                                        diff = int((eta_t - now.astimezone()).total_seconds() / 60)
                                        countdown = f"{diff} 分鐘" if diff > 0 else "即將到站"
                                        eta_rows.append({
                                            "目的地": eta_item.get("dest_tc"),
                                            "預計到站時間": eta_t.strftime("%H:%M:%S"),
                                            "到站倒數": countdown
                                        })
                                
                                if eta_rows:
                                    st.write(f"🚍 **九巴 {r_no}**（在 `{board_station}` 上車，往 `{target_dest}` 方向）即時班次：")
                                    st.dataframe(pd.DataFrame(eta_rows), use_container_width=True)
                    except Exception:
                        pass

        except nx.NetworkXNoPath:
            st.error("抱歉，目前數據庫中找不到連接這兩地的路線。")
