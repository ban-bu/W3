import streamlit as st
import random

st.set_page_config(page_title="天黑请闭眼：HR 教学版", layout="centered")

st.title("天黑请闭眼：Night Falls, Time to Leave")
st.markdown("本系统模拟H&M店铺中的员工KPI状况，请主持人引导找出破坏团队的“杀手”。")

# 初始化状态
if "players" not in st.session_state:
    st.session_state.players = {}
if "player_count" not in st.session_state:
    st.session_state.player_count = 0
if "roles_assigned" not in st.session_state:
    st.session_state.roles_assigned = False

# 步骤 1：设置玩家人数
player_count = st.number_input("请输入参与学生人数（建议 6-20 人）", min_value=4, max_value=30, value=8)
if st.button("确认人数"):
    st.session_state.player_count = player_count
    st.session_state.players = {
        f"{i+1:03d}": {
            "KPI": random.randint(60, 100),
            "status": "在岗",
            "role": "未分配"
        }
        for i in range(player_count)
    }
    st.session_state.roles_assigned = False
    st.success(f"已创建 {player_count} 名员工，请继续分配角色。")

# 步骤 2：分配角色
if st.button("分配角色"):
    n = st.session_state.player_count
    roles_pool = ["杀手", "侦探", "医生"] + ["平民"] * (n - 3)
    random.shuffle(roles_pool)
    for i, pid in enumerate(st.session_state.players):
        st.session_state.players[pid]["role"] = roles_pool[i]
    st.session_state.roles_assigned = True
    st.success("角色分配完成，主持人可选择查看。")

# 步骤 3：公屏展示
st.subheader("【 公屏信息 - 员工KPI 状态看板 】")
for pid, info in st.session_state.players.items():
    st.markdown(f"- 员工 {pid} | KPI：{info['KPI']} | 当前状态：**{info['status']}**")

# 步骤 4：主持人查看所有身份
if st.checkbox("（仅主持人）点击查看全部身份"):
    st.subheader("【主持人信息】角色一览")
    for pid, info in st.session_state.players.items():
        st.markdown(f"- 员工 {pid} | 角色：**{info['role']}**")

# 步骤 5：主持人可更新状态（如被杀/被救）
st.subheader("【主持人操作面板】")
with st.form("update_form"):
    target_id = st.text_input("请输入员工编号（例如：005）")
    new_status = st.selectbox("选择新状态", ["在岗", "已淘汰", "被救", "弃权"])
    submitted = st.form_submit_button("更新该员工状态")
    if submitted:
        if target_id in st.session_state.players:
            st.session_state.players[target_id]["status"] = new_status
            st.success(f"员工 {target_id} 状态已更新为：{new_status}")
        else:
            st.warning("员工编号不存在，请检查输入。")

st.markdown("---")
st.caption("Designed for Talent Management class - Powered by Streamlit")
