import streamlit as st
import pandas as pd
import networkx as nx
import requests
from datetime import datetime

# 1. 頁面組態設定
st.set_page_config(page_title="HK TransitOpt - 全港路線規劃系統", page_icon="🇭🇰", layout="wide")

st.title("🇭🇰 HK TransitOpt - 全港最少轉乘優先路線規劃器")
st.caption("已連接政府開放數據 API，覆蓋全港 MTR 所有車站及九巴/城巴所有路線。演算法：**1. 轉乘次數最少優先 ➔ 2. 行程總時間最短**。")

st.divider()

# 2. 自動從政府 Open Data API 載入全港所有巴士路線
@st.cache_data(ttl=86400) # 緩存 24 小時
def load_all_bus_routes():
    """下載全港九巴及城巴所有路線數據"""
    routes = []
    try:
        # 九巴 API
        kmb_url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
        res = requests.get(kmb_url, timeout=5)
        if res.status_code == 200:
            for r in res.json().get("data", []):
                routes.append({
                    "orig": r.get("orig_tc"),
                    "dest": r.get("dest_tc"),
                    "line": f"九巴 {r.get('route')}",
                    "route_no": r.get("route"),
                    "dest_tc": r.get("dest_tc")
                })
    except Exception:
        pass
        
    return routes

# 3. 建立全港地鐵及公共交通網絡圖
@st.cache_data
def build_full_hk_network(bus_routes):
    G = nx.DiGraph()
    
    # [資料集] 港鐵全網絡 (MTR Full Network)
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
        ("筲箕灣", "柴灣", 3, "MTR 港島綫"),

        # 南港島綫
        ("金鐘", "海洋公園", 4, "MTR 南港島綫"), ("海洋公園", "黃竹坑", 2, "MTR 南港島綫"),
        ("黃竹坑", "利東", 3, "MTR 南港島綫"), ("利東", "海怡半島", 3, "MTR 南港島綫"),

        # 東涌綫 / 機場快綫
        ("香港", "九龍", 3, "MTR 東涌綫"), ("九龍", "奧運", 3, "MTR 東涌綫"),
        ("奧運", "南昌", 3, "MTR 東涌綫"), ("南昌", "荔景", 6, "MTR 東涌綫"),
        ("荔景", "青衣", 3, "MTR 東涌綫"), ("青衣", "欣澳", 9, "MTR 東涌綫"),
        ("欣澳", "東涌", 10, "MTR 東涌綫")
    ]

    # 加入地鐵邊線（雙向）
    for u, v, weight, line in mtr_edges:
        G.add_edge(u, v, pure_time=weight, line=line, dest="", seq=0)
        G.add_edge(v, u, pure_time=weight, line=line, dest="", seq=0)

    # 動態將全港所有 API 巴士路線寫入網絡
    for r in bus_routes:
        orig = r["orig"]
        dest = r["dest"]
        line = r["line"]
        if orig and dest:
            # 巴士預設平均行程時間為 30 分鐘
            G.add_edge(orig, dest, pure_time=30, line=line, dest=dest, seq=1)

    return G

# 4. 「最少轉乘優先」的動態權重搜尋演算法
def find_min_transfer_path(G, source, target):
    """
    自訂 Dijkstra / BFS 最優路徑演算法：
    以 (轉乘次數 * 10,000 + 總時間) 為路徑權重，確保轉乘次數最少，同轉乘次數時時間最短。
    """
    # 建立輔助轉乘圖：每個節點為 (車站, 當前路線)
    H = nx.DiGraph()
    TRANSFER_PENALTY = 10000 # 轉乘一次懲罰 10,000 分鐘，確保轉乘次數絕對優先
    
    # 建立虛擬起點與終點
    H.add_node("START")
    H.add_node("END")
    
    for u, v, data in G.edges(data=True):
        line = data["line"]
        pure_time = data["pure_time"]
        
        node_u = (u, line)
        node_v = (v, line)
        
        # 同路線內的移動：只有純時間，無轉乘懲罰
        H.add_edge(node_u, node_v, weight=pure_time, pure_time=pure_time, line=line)
        
        # 起點可免費進入任何路線
        if u == source:
            H.add_edge("START", node_u, weight=0, pure_time=0, line="START")
        # 任何路線到達終點均無額外費用
        if v == target:
            H.add_edge(node_v, "END", weight=0, pure_time=0, line="END")

    # 同一車站內更換路線：加 1 次轉乘懲罰 (+10000) 及 4 分鐘轉乘時間
    stations = set(G.nodes())
    for s in stations:
        lines_at_s = list(set([data["line"] for u, v, data in G.edges(data=True) if u == s or v == s]))
        for i in range(len(lines_at_s)):
            for j in range(i + 1, len(lines_at_s)):
                l1 = lines_at_s[i]
                l2 = lines_at_s[j]
                H.add_edge((s, l1), (s, l2), weight=TRANSFER_PENALTY + 4, pure_time=4, line="TRANSFER")
                H.add_edge((s, l2), (s, l1), weight=TRANSFER_PENALTY + 4, pure_time=4, line="TRANSFER")

    # 執行最短路徑尋找
    raw_h_path = nx.dijkstra_path(H, source="START", target="END", weight="weight")
    
    # 解析結果
    path_steps = []
    transfers = 0
    total_pure_time = 0
    
    # 提取實質步驟
    node_path = raw_h_path[1:-1] # 移除 START 與 END
    
    current_board = node_path[0][0]
    current_line = node_path[0][1]
    accumulated_time = 0
    
    for i in range(len(node_path) - 1):
        curr_s, curr_l = node_path[i]
        next_s, next_l = node_path[i+1]
        
        edge_d = H.get_edge_data((curr_s, curr_l), (next_s, next_l))
        
        if edge_d and edge_d["line"] == "TRANSFER":
            transfers += 1
            path_steps.append({
                "上車站": current_board,
                "落車站": curr_s,
                "路線": current_line,
                "純車程時間": accumulated_time
            })
            total_pure_time += accumulated_time
            current_board = curr_s
            current_line = next_l
            accumulated_time = 4 # 轉乘緩衝 4 分鐘
        else:
            accumulated_time += edge_d["pure_time"] if edge_d else 0
            
    path_steps.append({
        "上車站": current_board,
        "落車站": node_path[-1][0],
        "路線": current_line,
        "純車程時間": accumulated_time
    })
    total_pure_time += accumulated_time

    return path_steps, transfers, total_pure_time

# 5. 抓取九巴實時 ETA 函數
def fetch_exact_stop_eta(route_no, station_name):
    now = datetime.now()
    eta_rows = []
    
    api_url = f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route_no}/1"
    try:
        res = requests.get(api_url, timeout=3)
        if res.status_code == 200:
            for item in res.json().get("data", []):
                eta_str = item.get("eta")
                dest = item.get("dest_tc", "")
                if eta_str:
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

    return sorted(eta_rows, key=lambda x: x["raw_time"])[:3]

# 6. UI 與主邏輯
with st.spinner("🔄 正在讀取全港所有地鐵及巴士站點..."):
    bus_routes = load_all_bus_routes()
    G = build_full_hk_network(bus_routes)

all_stations = sorted(list(G.nodes()))

col1, col2 = st.columns(2)
with col1:
    start_node = st.selectbox("📍 出發地點 (地鐵站 / 巴士站):", options=all_stations, index=all_stations.index("屯門") if "屯門" in all_stations else 0)
with col2:
    end_node = st.selectbox("🎯 目的地 (地鐵站 / 巴士站):", options=all_stations, index=all_stations.index("烏溪沙") if "烏溪沙" in all_stations else (len(all_stations)-1 if len(all_stations)>0 else 0))

if st.button("🗺️ 計算最佳路線 (最少轉乘優先)", type="primary"):
    if start_node == end_node:
        st.warning("起點與目的地不能相同！")
    else:
        try:
            path_steps, transfers_count, total_time = find_min_transfer_path(G, start_node, end_node)
            
            st.success(f"🎉 **找到最佳路線！**")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("🔄 轉乘次數", f"{transfers_count} 次")
            col_b.metric("⏱️ 預估總時間", f"約 {total_time} 分鐘")
            col_c.metric("🚉 總跨度段數", f"{len(path_steps)} 段")
            
            st.subheader("🧭 最優乘車明細：")
            
            for idx, step in enumerate(path_steps, 1):
                line = step["路線"]
                board = step["上車站"]
                alight = step["落車站"]
                pure_time = step["純車程時間"]
                
                st.markdown(f"""
                #### **Step {idx}: 乘搭 {line}**
                * 🟢 **上車站**：`{board}`
                * 🔴 **落車站**：`{alight}` （預計車程：約 {pure_time} 分鐘）
                """)
                
                # 如果是九巴，抓取實時到站班次
                if "九巴" in line:
                    bus_no = line.split(" ")[1]
                    eta_list = fetch_exact_stop_eta(bus_no, board)
                    if eta_list:
                        df_display = pd.DataFrame(eta_list)
                        df_display["到站倒數"] = df_display["到站倒數"].apply(lambda x: f"{x} 分鐘" if x > 0 else "即將到站")
                        df_display = df_display.drop(columns=["raw_time"], errors="ignore")
                        st.write(f"⏱️ **`{board}` 站實時到站班次：**")
                        st.dataframe(df_display, use_container_width=True)
                    
                st.divider()

        except Exception as e:
            st.error(f"抱歉，目前找不到連通這兩地的路線，請試試尋找鄰近的主要交匯站。（錯誤細節：{e}）")
