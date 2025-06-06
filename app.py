import streamlit as st
import datetime
import calendar
from db import init_db, get_chores_for_day, save_chores_for_date, load_all_chores_from_csv
import requests
from ui import render_task_card

init_db()

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    username = st.text_input("Enter your username:")
    if username:
        st.session_state.user = username
else:
    username = st.session_state.user
# 入力がない場合は処理を中断
if not username:
    st.warning("Please enter your username to proceed.")
    st.stop()

# ここから先は、username があるときだけ実行される
st.success(f"Welcome, {username}!")


today = datetime.date.today()
first_day = datetime.date(today.year, 1, 1)
today_number = (today - first_day).days + 1
year = datetime.date.today().year
is_leap = calendar.isleap(year)  # Trueならうるう年

days_in_year = 366 if is_leap else 365
nextday_number = (today_number+1) if today_number != days_in_year else 1

# 日付が変わったら家事リストを再読込
if "app_date" not in st.session_state or st.session_state.app_date != today_number:
    st.session_state.app_date = today_number

    # DBに今日の家事があれば取得
    chores = get_chores_for_day(today_number)

    if not chores:
        # なければCSVから読み込み＆初期化
        chores = load_all_chores_from_csv()
    st.session_state.chores = chores
    
    chores1 = get_chores_for_day(nextday_number)
    if not chores1:
        # なければCSVから読み込み＆初期化
        chores1 = load_all_chores_from_csv()
    st.session_state.chores1 = chores1

if "page" not in st.session_state:
    st.session_state.page = "今日の予定"

with st.sidebar:
    if st.button("今日の予定"):
        st.session_state.page = "今日の予定"
    if st.button("家事一覧"):
        st.session_state.page = "家事一覧"
    if st.button("タスク履歴"):
        st.session_state.page = "タスク履歴"

page = st.session_state.page    
day_number_bunkai = []
for i in range(2,today_number):
    day_number0 = today_number
    shisu = 0
    while day_number0 % i == 0:
        day_number0 //= i
        shisu += 1
    if shisu:
        day_number_bunkai.append([i,shisu])

            


def superscript(n):
    sup_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(sup_map)

formatted_terms = [
    f"{base}" if exp == 1 else f"{base}{superscript(exp)}"
    for base, exp in day_number_bunkai
]

output = " × ".join(formatted_terms)
output = "= " + output 
if not day_number_bunkai:
    output = "Prime Number"
def get_hourly_weather_with_precip(city):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        res = requests.get(url)
        data = res.json()
        weather_today = data["weather"][0]
        date_str = weather_today["date"]
        hourly_data = weather_today["hourly"]

        results = []
        for hour in hourly_data:
            time_str = hour["time"]  # '0', '300', '600' (単位は分)
            hour_int = int(time_str) // 100
            temp = hour["tempC"]
            desc = hour["weatherDesc"][0]["value"]
            chance_rain = hour.get("chanceofrain", "0")

            results.append(
                f"{hour_int}:00 - {desc},  気温: {temp}℃,  降水確率: {chance_rain}%"
            )
        return "\n".join(results)
    except Exception as e:
        return f"天気情報取得エラー: {e}"
if page == "今日の予定":

    # UI表示
    st.title("Tasks")
    st.text(f"{today_number} is {output} / {today_number % 7} mod 7")
    city = "Yokohama"
    st.markdown(f"**{today_number}_{city}_天気予報:**\n")

    weather_text = get_hourly_weather_with_precip(city)
    st.text(weather_text)
    st.markdown(f"**Tasks for {today_number}**")
    for i, task in enumerate(st.session_state.chores):
        if st.session_state.chores[i]["done"]:
            continue
        if today_number % st.session_state.chores[i]["mod"] != st.session_state.chores[i]["amari"]:
            continue
        done = render_task_card(task, i,"task")
        st.session_state.chores[i]["done"] = done
        if done:
            st.session_state.chores[i]["done_by"] = username
        else:
            st.session_state.chores[i]["done_by"] = ""
            

    st.markdown(f"**Tasks for {nextday_number}**")
    for i, task in enumerate(st.session_state.chores1):
        if st.session_state.chores1[i]["done"]:
            continue
        if nextday_number % st.session_state.chores1[i]["mod"] != st.session_state.chores1[i]["amari"]:
            continue
        done = render_task_card(task, i,"task1")
        st.session_state.chores1[i]["done"] = done
        if done:
            st.session_state.chores1[i]["done_by"] = username
        else:
            st.session_state.chores1[i]["done_by"] = ""


                
                
    if st.button("Save"):
        save_chores_for_date(today_number, st.session_state.chores)
        save_chores_for_date(nextday_number, st.session_state.chores1)
        
        st.success("Saved!")
        

elif page == "家事一覧":
    st.subheader("家事一覧")
    chores = st.session_state.chores
    for i in chores:
        with st.expander(i["name"]):
            st.write(str(i["detail"]) + "\n" + f"{i["amari"]}mod{i["mod"]}")
            

elif page == "タスク履歴":
    st.header("Task History")
    search_date = st.date_input("検索したい日付を選んでください", value=datetime.date.today())
    search_date_number = (search_date - first_day).days + 1
    tasks = get_chores_for_day(search_date_number)

    if tasks:
        for t in tasks:
            if search_date_number % t["mod"] != t["amari"]:
                continue
            done_status = "✓" if t["done"] else "×"
            st.write(f"{done_status} {t['name']} — {t["done_by"]}")
    else:
        st.write("No tasks found for this date.")
