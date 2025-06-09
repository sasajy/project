import streamlit as st
from datetime import datetime

def render_task_card(task, index, key_prefix):
    done = task.get("done", False)
    name = task.get("name", "No Name")
    detail = task.get("detail", "")
    key_done = f"{key_prefix}_done_{index}"
    
    # 現在の状態をセッションから取得
    if key_done not in st.session_state:
        st.session_state[key_done] = task.get("done", False)

    cols = st.columns([0.1, 0.9])
    tf = 0
    with cols[0]:
        done = st.checkbox("",value=st.session_state.get(key_done, False), key=key_done)

    with cols[1]:
        with st.expander(task["name"]):
            st.text(task["detail"])

    # Checkbox reflecting task done status

    return done

def render_task_card1(task, index, key_prefix):
    done = task.get("done", False)
    name = task.get("name", "No Name")
    done_by = task.get("done_by", "")
    detail = task.get("detail", "")
    key_done = f"{key_prefix}_done_{index}"
    
    # 現在の状態をセッションから取得
    if key_done not in st.session_state:
        st.session_state[key_done] = task.get("done", False)

    cols = st.columns([0.1, 0.9])
    tf = 0
    with cols[0]:
        done = st.checkbox("",value=st.session_state.get(key_done, False), key=key_done)

    with cols[1]:
        st.write(f"{name} — {done_by}")

    # Checkbox reflecting task done status

    return done



