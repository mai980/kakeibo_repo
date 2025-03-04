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
        pd.DataFrame(columns=["支払日", "金額", "支払い者", "購入品使用者", "カテゴリ", "その他のカテゴリ", "メモ", "入力年月日", "入力時間"]).to_csv(DATA_FILE, index=False)

# カテゴリリスト
if "categories" not in st.session_state:
    st.session_state.categories = ["食費", "飲料", "交通費", "娯楽", "日用品", "家賃", 'スポーツ', '衣類', '交際費', '光熱費', '医療費', 
                                   'サプリメント', '外食', '通信費', '漫画', '精密機器', 'サブスク', 'カフェ', '本', '手数料', "その他"]

# **リセット用コールバック関数**
# def reset_input_fields():
#     st.session_state["amount"] = 0
#     st.session_state["category_other"] = "記載なし"
#     st.session_state["memo"] = "記載なし"

# セッションの初期化（リセットのためのデフォルト値）
if "amount" not in st.session_state:
    st.session_state.amount = 0
if "category_other" not in st.session_state:
    st.session_state.category_other = ""
if "memo" not in st.session_state:
    st.session_state.memo = ""

# タブメニュー
tab1, tab2, tab3 = st.tabs(["📋 家計簿入力", "💰今月の折半金額", "サマリ"])

# ---------------- 家計簿入力タブ ----------------
with tab1:
    with st.form("input_form", clear_on_submit = True):
        date = st.date_input("支払日", value=datetime.today())
        date = date.strftime("%Y-%m-%d")  # `date` を文字列に変換
        input_YMD = datetime.now().strftime('%Y%m%d')
        payment_person = st.selectbox('支払い者', ['たう', '萌伽', '割勘'])
        user_name = st.selectbox("購入品使用者", ["たう", "萌伽", "共用"])
        
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
                new_data = pd.DataFrame([[date, amount, payment_person, user_name, category_large, category_other, memo, input_YMD, time_now]], 
                                        columns=["支払日", "金額", "支払い者", "購入品使用者", "カテゴリ", "その他のカテゴリ", "メモ", "入力年月日", "入力時間"])
                st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                save_data()  # データ保存
                st.success("✅ データを追加しました！")

                # 入力値をリセット（デフォルト値に戻す）
                # st.session_state.amount = 0
                # st.session_state.category_other = ""
                # st.session_state.memo = ""
                # reset_input_fields()

                # 画面をリフレッシュしてリセットを即時反映
                # st.rerun()

    # データ表示
    st.subheader("入力データ")

    if not st.session_state.data.empty:
        st.dataframe(st.session_state.data, height=300)

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


# ---------------- 2人の今月の折半金額 ----------------
with tab2:
    # month = datetime.today().strftime("%Y年%m月")

    # 現在の年月を取得
    current_year = datetime.today().year
    current_month = datetime.today().month

    # 選択肢を生成（過去5年分 + 未来1年分）
    years = list(range(current_year - 0, current_year + 2))
    months = list(range(1, 13))  # 1月〜12月
    # 「yyyy年mm月」の形式でリストを作成
    month_options = [f"{year}年{month:02d}月" for year in years for month in months]

    # 現在の年月をデフォルト選択
    # Streamlitのselectboxで年月を選択
    
    default_value = f"{current_year}年{current_month:02d}月"
    selected_month = st.selectbox("年月を選択", month_options, index=month_options.index(default_value))

    # 選択した年月を数値型の yyyymm に変換
    selected_year = int(selected_month[:4])  # yyyy
    selected_month_num = int(selected_month[5:7])  # mm
    selected_yyyymm = selected_year * 100 + selected_month_num  # 数値型の yyyymm

    st.subheader(f"{selected_month} の2人の折半金額")

    df = pd.read_csv(DATA_FILE)
    df['支払日'] = pd.to_datetime(df['支払日'])

    # データフレームをフィルタリング（該当する年月のデータのみ抽出）
    df = df[(df["支払日"].dt.year == selected_year) & (df["支払日"].dt.month == selected_month_num)]

    # 使う人がTさんで、支払った人がMさんの場合、そのデータフレームの金額をTさんが全額払う
    df_1 = df[(df['購入品使用者'] == 'たう') & (df['支払い者'] == '萌伽')]
    T_payment = df_1['金額'].sum()

    # 使う人がMさんで、支払った人がTさんの場合、そのデータフレームの金額をMさんが全額払う
    df_2 = df[(df['購入品使用者'] == '萌伽') & (df['支払い者'] == 'たう')]
    M_payment = df_2['金額'].sum()

    # 使う人はTさんMさんの共用で、支払った人がTさんの場合、Mさんに半分の金額を支払う
    df_12 = df[(df['購入品使用者'] == '共用') & (df['支払い者'] == 'たう')]
    # 使う人はTさんMさんの共用で、支払った人がMさんの場合、Mさんに半分の金額を支払う
    df_21 = df[(df['購入品使用者'] == '共用') & (df['支払い者'] == '萌伽')]

    # T_paymentとM_paymentにそれぞれ折半する金額をプラス
    T_payment += df_12['金額'].sum()//2
    M_payment += df_21['金額'].sum()//2

    col1, col2 = st.columns(2)
    with col1:
        st.write('たうが萌伽に支払う金額')
        st.write(f"<p style='font-size:36px; font-weight:bold;'>{T_payment}円</p>", unsafe_allow_html=True)
        
    with col2:
        st.write('萌伽がたうに支払う金額')
        st.write(f"<p style='font-size:36px; font-weight:bold;'>{M_payment}円</p>", unsafe_allow_html=True)
        # st.write(df_2)
    if T_payment > M_payment:
        st.write(f"<p style='font-size:36px; font-weight:bold;'>たうが萌伽に{T_payment - M_payment}円支払う</p>", unsafe_allow_html=True)
    elif T_payment > M_payment:
        st.write(f"<p style='font-size:36px; font-weight:bold;'>萌伽がたうに{M_payment - T_payment}円支払う</p>", unsafe_allow_html=True)
    else:
        st.write('お互いに支払う金額はない')
    
    # データフレームを表示
    if st.button('選択した年月の家計簿データを表示'):
        st.write(f"選択された年月の家計簿データ: {selected_month}")
        # 文字列型に変更
        df['支払日'] = df['支払日'].dt.strftime('%Y-%m-%d')
        st.dataframe(df.fillna('未入力'))