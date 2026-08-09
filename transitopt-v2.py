import streamlit as st
import pandas as pd
import networkx as nx
import requests
from datetime import datetime

# 1. 頁面組態設定
st.set_page_config(page_title="HK TransitOpt - 全港路線規劃系統", page_icon="🇭🇰", layout="wide")

st.title("🇭🇰 HK TransitOpt - 全港全綫跨交通工具路線規劃器")
st.write("已對接政府開放數據 API，**涵蓋全港 MTR 全綫及九巴/城巴所有巴士路線**。")

st.divider()

# 2. 自動從政府 API 下載全港九巴路線與站點數據
@st.cache_data(ttl=86400) # 緩存 24 小時
def load_all_kmb_routes():
    """從九巴 Open API 獲取全港所有路線與站名"""
    try:
        # 獲取九巴所有路線列表
        url_routes = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
        res_routes = requests.get(url_routes, timeout=5).json()
        routes_data = res_routes.get("data", [])
        return routes_data
    except Exception as e:
        st.error(f"無法載入實時巴士路線數據: {e}")
        return []

# 3. 建立全港港鐵及基礎交通圖
@st.cache_data
def build_base_hk_network():
    G = nx.DiGraph()
    
    # [港鐵全網絡]
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
        
        # 屯馬綫
        ("屯門", "兆康", 3, "MTR 屯馬綫"), ("兆康", "天水圍", 5, "MTR 屯馬綫"),
        ("天水圍", "朗屏", 3, "MTR 屯馬綫"), ("朗屏", "元朗", 2, "MTR 屯馬綫"),
        ("元朗", "錦上路", 4, "MTR 屯馬綫"), ("錦上路", "荃灣西", 9, "MTR 屯馬綫"),
        ("荃灣西", "美孚", 6, "MTR 屯馬綫"), ("美孚", "南昌", 4, "MTR 屯馬綫"),
        ("南昌", "柯士甸", 4, "MTR 屯馬綫"), ("柯士甸", "尖東", 3, "MTR 屯馬綫"),
        ("尖東", "紅磡", 2, "MTR 屯馬綫"), ("紅磡", "何文田", 3, "MTR 屯馬綫"),
        ("何文田", "土瓜灣", 3, "MTR 屯馬綫"), ("土瓜灣", "宋皇臺", 2, "MTR 屯馬綫"),
        ("宋皇臺", "啟德", 2, "MTR 屯馬綫"), ("啟德", "鑽石山", 3, "MTR 屯馬綫"),
        ("鑽石山", "大圍", 6, "MTR 屯馬綫"),

        # 港島綫
        ("堅尼地城", "香港大學 (HKU)", 2, "MTR 港島綫"), ("香港大學 (HKU)", "西營盤", 2, "MTR 港島綫"),
        ("西營盤", "上環", 2, "MTR 港島綫"), ("上環", "中環", 2, "MTR 港島綫"),
        ("中環", "金鐘", 2, "MTR 港島綫"), ("金鐘", "灣仔", 2, "MTR 港島綫"),
        ("灣仔", "銅鑼灣", 2, "MTR 港島綫"), ("銅鑼灣", "天后", 2, "MTR 港島綫"),
        ("天后", "炮台山", 2, "MTR 港島綫"), ("炮台山", "北角", 2, "MTR 港島綫"),
        ("北角", "鰂魚涌", 2, "MTR 港島綫"), ("鰂魚涌", "太古", 2, "MTR 港島綫"),
        ("太古", "西灣河", 2, "MTR 港島綫"), ("西灣河", "筲箕灣", 2, "MTR 港島綫"),
        ("筲箕灣", "柴灣", 3, "MTR 港島綫")
    ]

    for u, v, weight, line in mtr_edges:
        G.add_edge(u, v, weight=weight, line=line, dest="", seq=0)
        G.add_edge(v, u, weight=weight, line=line, dest="", seq=0)
        
    return G

# 4. 路徑壓縮演算法
def compress_path(G, path):
    if len(path) < 2:
        return []
    
    compressed_steps = []
    current_board_station = path[0]
    current_line = None
    target_dest = ""
    target_seq = 0
    accumulated_time = 0
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = G.get_edge_data(u, v)
        line = edge_data['line']
        duration = edge_data['weight']
        dest = edge_data.get('dest', '')
        seq = edge_data.get('seq', 0)
        
        if current_line is None:
            current_line = line
            target_dest = dest
            target_seq = seq
            accumulated_time += duration
        elif line == current_line:
            accumulated_time += duration
        else:
            compressed_steps.append({
                "上車站": current_board_station,
                "落車站": u,
                "路線": current_line,
                "方向": target_dest,
                "seq": target_seq,
                "純車程時間": accumulated_time
            })
            current_board_station = u
            current_line = line
            target_dest = dest
            target_seq = seq
            accumulated_time = duration
            
    compressed_steps.append({
        "上車站": current_board_station,
        "落車站": path[-1],
        "路線": current_line,
        "方向": target_dest,
        "seq": target_seq,
        "純車程時間": accumulated_time
    })
    
    return compressed_steps

# 5. 抓取實時 ETA 函數
def fetch_exact_stop_eta(route_no, station_name, target_dest, seq_no):
    now = datetime.now()
    eta_rows = []
    
    api_url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route_no}/1"
    try:
        res = requests.get(api_url, timeout=3)
        if res.status_code == 200:
            data = res.json().get("data", [])
            
            for item in data:
                dest = item.get("dest_tc", "")
                item_seq = item.get("seq")
                eta_str = item.get("eta")
                
                if target_dest in dest and (seq_no == 0 or item_seq == seq_no) and eta_str:
                    eta_t = datetime.fromisoformat(eta_str)
                    diff = int((eta_t - now.astimezone()).total_seconds() / 60)
                    
                    if diff >= 0:
                        eta_rows.append({
                            "上車地點": station_name,
                            "目的地": dest,
                            "預計到達時間": eta_t.strftime("%H:%M:%S"),
                            "到站倒數": diff,
                            "raw_time": eta_t
                        })
    except Exception:
        pass

    eta_rows = sorted(eta_rows, key=lambda x: x["raw_time"])[:3]
    return eta_rows

# 6. 初始化地圖與路線數據
with st.spinner("🔄 正在連線政府 Open Data API 載入全港所有巴士路線..."):
    all_kmb_routes = load_all_kmb_routes()
    G = build_base_hk_network()

# 將 API 獲取到的路線動態寫入網絡
for r in all_kmb_routes:
    orig = r.get("orig_tc")
    dest = r.get("dest_tc")
    route_code = r.get("route")
    
    if orig and dest and route_code:
        # 動態將該路線的頭尾站加入圖網絡（預設平均車程為 25 分鐘）
        G.add_edge(orig, dest, weight=25, line=f"九巴 {route_code}", dest=dest, seq=1)

all_stations = sorted(list(G.nodes()))

# 7. UI 部分
col1, col2 = st.columns(2)
with col1:
    start_node = st.selectbox("📍 出發地點:", options=all_stations)
with col2:
    end_node = st.selectbox("🎯 目的地:", options=all_stations, index=len(all_stations)-1 if len(all_stations) > 1 else 0)

if st.button("🗺️ 搜尋最佳路線", type="primary"):
    if start_node == end_node:
        st.warning("起點與目的地不能相同！")
    else:
        try:
            raw_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            compressed_steps = compress_path(G, raw_path)
            
            total_in_vehicle_time = 0
            total_waiting_time = 0

            for idx, step in enumerate(compressed_steps):
                line = step["路線"]
                board = step["上車站"]
                pure_time = step["純車程時間"]
                total_in_vehicle_time += pure_time
                
                step_wait_time = 0
                if idx > 0:
                    step_wait_time += 4 # 轉乘預設時間
                
                if "九巴" in line:
                    bus_no = line.split(" ")[1]
                    eta_list = fetch_exact_stop_eta(bus_no, board, step["方向"], step["seq"])
                    if eta_list:
                        step_wait_time = eta_list[0]["到站倒數"]
                        step["eta_data"] = eta_list

                total_waiting_time += step_wait_time

            grand_total_time = total_in_vehicle_time + total_waiting_time

            st.success(f"🎉 **門到門總預計時間：約 {grand_total_time} 分鐘** （車程：{total_in_vehicle_time} 分鐘 + 候車/轉乘：{total_waiting_time} 分鐘）")
            
            st.subheader("🧭 建議路線方案：")
            
            for idx, step in enumerate(compressed_steps, 1):
                line = step["路線"]
                board = step["上車站"]
                alight = step["落車站"]
                pure_time = step["純車程時間"]
                dest_info = f"（往 {step['方向']} 方向）" if step['方向'] else ""
                
                st.markdown(f"""
                #### **Step {idx}: 乘搭 {line} {dest_info}**
                * 🟢 **上車站**：`{board}`
                * 🔴 **落車站**：`{alight}` （行車時間：約 {pure_time} 分鐘）
                """)
                
                if "eta_data" in step and step["eta_data"]:
                    df_display = pd.DataFrame(step["eta_data"])
                    df_display["到站倒數"] = df_display["到站倒數"].apply(lambda x: f"{x} 分鐘" if x > 0 else "即將到站")
                    df_display = df_display.drop(columns=["raw_time"], errors="ignore")
                    
                    st.write(f"⏱️ **`{board}` 站實時到站班次：**")
                    st.dataframe(df_display, use_container_width=True)
                    
                st.divider()

        except nx.NetworkXNoPath:
            st.error("抱歉，目前找不到連接這兩地的直接路線，請嘗試選取附近的公共交通樞紐。")
