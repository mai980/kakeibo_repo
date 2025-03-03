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
        # ファイルがない場合、新しく作成
        df = pd.DataFrame(columns=["支払日", "金額", "購入品使用者", "支払い者", "カテゴリ", "その他のカテゴリ", "メモ", "入力年月日", "入力時間"])
        df.to_csv(DATA_FILE, index=False)  # 空のCSVファイルを作成
        return df

# セッションの初期化（起動時にCSVから読み込む）
if "data" not in st.session_state:
    st.session_state.data = load_data()

# データを保存する関数
def save_data():
    if not st.session_state.data.empty:
        st.session_state.data.to_csv(DATA_FILE, index=False)
    else:
        # データが空の場合、ヘッダーだけを書き込む
        pd.DataFrame(columns=["支払日", "金額", "購入品使用者", "支払い者", "カテゴリ", "その他のカテゴリ", "メモ", "入力年月日", "入力時間"]).to_csv(DATA_FILE, index=False)


# 支払日,金額,購入品使用者,支払い者,カテゴリ,その他のカテゴリ,メモ,入力年月日,入力時間
# 2025-03-03,,200,萌伽,たう,食費,,メモです,20250303,20:02:58
# 2025-03-03,,400,萌伽,萌伽,食費,,メモです,20250303,20:03:07
# 2025-03-03,,300,共用,萌伽,娯楽,,メモです,20250303,20:03:16
# 2025-03-03,,300,共用,たう,スポーツ,,あ,20250303,20:03:27
# 2025-03-03,,400,たう,たう,飲料,,モンエナ,20250303,20:03:45
# 2025-03-03,,800,萌伽,たう,交通費,,モンエナ,20250303,20:04:07
# 2025-03-03,,700,共用,たう,家賃,,,20250303,20:04:21
# 2025-03-03,,1200,共用,萌伽,交通費,,,20250303,20:04:32
# 2025-03-03,,1500,萌伽,萌伽,食費,,,20250303,20:04:40
# 2025-03-03,,1500,萌伽,萌伽,食費,,,20250303,20:04:41
# 2025-03-03,,2000,たう,萌伽,食費,,,20250303,20:04:49
# 2025-03-03,,2300,たう,萌伽,食費,,,20250303,20:04:53
# 2025-03-03,,2300,たう,割勘,娯楽,,,20250303,20:05:03
# 2025-03-03,,2500,萌伽,割勘,娯楽,,,20250303,20:05:09
# 2025-03-03,,2300,共用,割勘,娯楽,,,20250303,20:05:15


if "categories" not in st.session_state:
    st.session_state.categories = ["食費", "飲料", "交通費", "娯楽", "日用品", "家賃", 'スポーツ', '衣類', '交際費', '光熱費', '医療費', 
                                   'サプリメント', '外食', '通信費', '漫画', '精密機器', 'サブスク', 'カフェ', '本', '手数料', "その他"]

# タブメニュー
tab1, tab2 = st.tabs(["📋 家計簿入力", "💰今月の折半金額"])

# ---------------- 家計簿入力タブ ----------------
with tab1:
    # セッションの初期化（初回のみ）
    if "amount" not in st.session_state:
        st.session_state.amount = 0
    if "category_other" not in st.session_state:
        st.session_state.category_other = ""
    if "memo" not in st.session_state:
        st.session_state.memo = ""

    with st.form("input_form"):
        date = st.date_input("支払日", value=datetime.today())
        date = date.strftime("%Y-%m-%d")  # `date` を文字列に変換
        input_YMD = datetime.now().strftime('%Y%m%d')
        payment_person = st.selectbox('支払い者', ['たう', '萌伽', '割勘'])
        name = st.selectbox("購入品使用者", ["たう", "萌伽", "共用"])
        
        # 各ウィジェットに key を設定（st.session_state に紐づける）
        amount = st.number_input("金額", min_value=0, step=100, key="amount")
        category_large = st.selectbox("カテゴリ", st.session_state.categories)
        category_other = st.text_area('その他のカテゴリ', help="カテゴリ一覧にない場合はこちらに記載してください", key="category_other")
        memo = st.text_area("メモ", height=100, help="具体的に購入したものや特記事項があれば記載してください", key="memo")

        submitted = st.form_submit_button("追加")

        if submitted:
            if amount == 0:
                st.warning('⚠️ 金額が 0 円のデータは追加できません')
            elif category_large != "その他" and category_other.strip() != "":
                st.warning('⚠️ 「その他のカテゴリ」に記載する場合は「カテゴリ」を「その他」に設定してください')
            else:
                time_now = datetime.now().strftime("%H:%M:%S")  # hh:mm:ss 形式の時刻取得
                new_data = pd.DataFrame([[date, input_YMD, time_now, amount, category_large, category_other, memo, name, payment_person]], 
                                        columns=["支払日", "入力年月日", "入力時間", "金額", "カテゴリ", "その他のカテゴリ", "メモ", "購入品使用者", "支払い者"])
                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                save_data()  # データ保存
                st.success("✅ データを追加しました！")

                # 入力値をリセット
                # st.session_state.amount = 0
                # st.session_state.category_other = ""
                # st.session_state.memo = ""

    # データ表示
    st.subheader("入力データ")

    if not st.session_state.data.empty:
        # 編集可能なデータフレーム
        edited_data = st.dataframe(st.session_state.data, height=300)

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
        st.download_button("CSVをダウンロード", data=csv, file_name="kakeibo_data.csv", mime="text/csv")

# ---------------- カテゴリ管理タブ ----------------
# with tab2:
#     st.subheader("カテゴリの管理")

#     new_category = st.text_input("新しいカテゴリを追加", value="")
#     if st.button("カテゴリを追加"):
#         if new_category and new_category not in st.session_state.categories:
#             st.session_state.categories.append(new_category)
#             st.success(f"カテゴリ '{new_category}' を追加しました")

#     remove_category = st.selectbox("削除するカテゴリ", st.session_state.categories)
#     if st.button("カテゴリを削除"):
#         if remove_category in st.session_state.categories:
#             st.session_state.categories.remove(remove_category)
#             st.success(f"カテゴリ '{remove_category}' を削除しました")

# ---------------- 2人の今月の折半金額 ----------------
with tab2:
    month = datetime.today().strftime("%Y年%m月")
    st.subheader(f"{month} の2人の折半金額")

    df = pd.read_csv(DATA_FILE)
    df_1 = df[(df['購入品使用者'] == 'たう') & (df['支払い者'] == '萌伽')]
    df_2 = df[(df['購入品使用者'] == '萌伽') & (df['支払い者'] == 'たう')]
    df_12 = df[df['購入品使用者'] == '共用']
    st.write(df)

    col1, col2 = st.columns(2)
    with col1:
        st.write(df_1)
    with col2:
        st.write(df_2)