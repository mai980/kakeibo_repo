import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 保存するCSVファイル名
DATA_FILE = "./kakeibo_data.csv"

# タイトル
st.title("家計簿アプリ")

# データを読み込む関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["年月日", "入力時間", "金額", "カテゴリ", "メモ", "氏名"])

# データを保存する関数
def save_data():
    st.session_state.data.to_csv(DATA_FILE, index=False)

# セッションの初期化（起動時にCSVから読み込む）
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "categories" not in st.session_state:
    st.session_state.categories = ["食費", "交通費", "娯楽", "生活費", "その他"]

# タブメニュー
tab1, tab2, tab3 = st.tabs(["📋 家計簿入力", "⚙️ カテゴリ管理", "今月の折半金額"])

# ---------------- 家計簿入力タブ ----------------
with tab1:
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("年月日", value=datetime.today())
            date = date.strftime("%Y-%m-%d")  # `date` を文字列に変換
            name = st.selectbox("氏名", ["たう", "萌伽", "共用"])
            amount = st.number_input("金額", min_value=0, value=0, step=100)

        with col2:
            category_large = st.selectbox("カテゴリ", st.session_state.categories)
            memo = st.text_area("メモ", value="", height=100)

        submitted = st.form_submit_button("追加")

        if submitted:
            time_now = datetime.now().strftime("%H:%M:%S")  # hh:mm:ss 形式の時刻取得
            new_data = pd.DataFrame([[date, time_now, amount, category_large, memo, name]], 
                                    columns=["年月日", "入力時間", "金額", "カテゴリ", "メモ", "氏名"])
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            save_data()  # データ保存
            st.success("データを追加しました！")

    # データ表示
    st.subheader("入力データ")

    if not st.session_state.data.empty:
        # 編集可能なデータフレーム
        edited_data = st.data_editor(st.session_state.data, height=300)

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
        csv = st.session_state.data.to_csv(index=False).encode("utf-8")
        st.download_button("CSVをダウンロード", data=csv, file_name="kakeibo.csv", mime="text/csv")

# ---------------- カテゴリ管理タブ ----------------
with tab2:
    st.subheader("カテゴリの管理")

    new_category = st.text_input("新しいカテゴリを追加", value="")
    if st.button("カテゴリを追加"):
        if new_category and new_category not in st.session_state.categories:
            st.session_state.categories.append(new_category)
            st.success(f"カテゴリ '{new_category}' を追加しました")

    remove_category = st.selectbox("削除するカテゴリ", st.session_state.categories)
    if st.button("カテゴリを削除"):
        if remove_category in st.session_state.categories:
            st.session_state.categories.remove(remove_category)
            st.success(f"カテゴリ '{remove_category}' を削除しました")

# ---------------- 2人の今月の折半金額 ----------------
with tab3:
    month = datetime.today().strftime("%Y年%m月")
    st.subheader(f"{month} の2人の折半金額")