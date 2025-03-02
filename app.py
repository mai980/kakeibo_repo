import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 保存するCSVファイル名
DATA_FILE = "kakeibo_data.csv"

# タイトル
st.title("家計簿アプリ")

# データを読み込む関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["年月日", "入力時間", "金額", "大項目", "中項目", "メモ", "氏名"])

# データを保存する関数
def save_data():
    st.session_state.data.to_csv(DATA_FILE, index=False)

# セッションの初期化（起動時にCSVから読み込む）
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "categories" not in st.session_state:
    st.session_state.categories = {"食費": ["朝食", "昼食", "夕食"],
                                   "交通費": ["電車", "バス", "タクシー"],
                                   "娯楽": ["映画", "カラオケ"],
                                   "生活費": ["家賃", "水道光熱費"],
                                   "その他": []}

# タブメニュー
tab1, tab2 = st.tabs(["📋 家計簿入力", "⚙️ カテゴリ管理"])

# ---------------- 家計簿入力タブ ----------------
with tab1:
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("年月日", value=datetime.today())
            name = st.selectbox("氏名", ["たう", "萌伽"])
            amount = st.number_input("金額", min_value=0, value=0, step=100)

        with col2:
            category_large = st.selectbox("大項目", list(st.session_state.categories.keys()))
            category_small = st.selectbox("中項目", st.session_state.categories.get(category_large, []))
            memo = st.text_area("メモ", value="", height=100)

        submitted = st.form_submit_button("追加")

        if submitted:
            time_now = datetime.now().strftime("%H:%M:%S")  # hh:mm:ss 形式の時刻取得
            new_data = pd.DataFrame([[date, time_now, category_large, category_small, amount, memo, name]], 
                                    columns=["年月日", "入力時間", "金額", "大項目", "中項目", "メモ", "氏名"])
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            save_data()  # データ保存
            st.success("データを追加しました！")

    # データ表示
    st.subheader("入力データ")

    if not st.session_state.data.empty:
        # 編集可能なデータフレーム
        edited_data = st.data_editor(st.session_state.data, num_rows="dynamic", height=300)

        # 削除する行の選択
        selected_rows = st.multiselect("削除する行を選択", st.session_state.data.index.tolist())

        if st.button("選択した行を削除"):
            if selected_rows:
                st.session_state.data = st.session_state.data.drop(selected_rows).reset_index(drop=True)
                save_data()  # データ保存
                st.success("選択したデータを削除しました！")
            else:
                st.warning("削除する行を選択してください")

    # CSVエクスポート
    if not st.session_state.data.empty:
        csv = st.session_state.data.to_csv(index=False).encode('utf-8')
        st.download_button("CSVをダウンロード", data=csv, file_name="kakeibo.csv", mime="text/csv")

# ---------------- カテゴリ管理タブ ----------------
with tab2:
    st.subheader("カテゴリの管理")

    # 大項目の追加・削除
    new_large = st.text_input("新しい大項目を追加", value="")
    if st.button("大項目を追加"):
        if new_large and new_large not in st.session_state.categories:
            st.session_state.categories[new_large] = []
            st.success(f"大項目 '{new_large}' を追加しました")

    remove_large = st.selectbox("削除する大項目", list(st.session_state.categories.keys()))
    if st.button("大項目を削除"):
        if remove_large in st.session_state.categories:
            del st.session_state.categories[remove_large]
            st.success(f"大項目 '{remove_large}' を削除しました")

    # 中項目の追加・削除
    selected_large = st.selectbox("中項目を編集する大項目", list(st.session_state.categories.keys()))
    new_small = st.text_input(f"'{selected_large}' に追加する中項目", value="")
    
    if st.button("中項目を追加"):
        if new_small and new_small not in st.session_state.categories[selected_large]:
            st.session_state.categories[selected_large].append(new_small)
            st.success(f"'{selected_large}' に '{new_small}' を追加しました")

    remove_small = st.selectbox(f"'{selected_large}' の中項目を削除", st.session_state.categories[selected_large])
    
    if st.button("中項目を削除"):
        if remove_small in st.session_state.categories[selected_large]:
            st.session_state.categories[selected_large].remove(remove_small)
            st.success(f"'{selected_large}' から '{remove_small}' を削除しました")

# -------------------
