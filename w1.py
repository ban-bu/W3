import streamlit as st
from PIL import Image
import os
import uuid
import json
from collections import defaultdict

# 配置常量和路径
UPLOAD_FOLDER = "uploads"
METADATA_PATH = os.path.join(UPLOAD_FOLDER, "metadata.json")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化全局数据结构
@st.cache_resource
def load_global_data():
    """加载持久化的图片元数据和投票数据"""
    try:
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
        return {
            'vote_count': {item['filename']: item['upvotes'] for item in metadata},
            'uploaded_images': metadata
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {'vote_count': defaultdict(int), 'uploaded_images': []}

def save_metadata(metadata):
    """保存元数据到文件"""
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f)

# 初始化全局状态
global_data = load_global_data()

# Streamlit 应用界面
st.title("📷 Upload your images and vote anonymously!")

# 用户会话状态管理
if 'voted_images' not in st.session_state:
    st.session_state.voted_images = set()

# 清空所有数据的按钮
if st.button("Clear All Images and Votes"):
    global_data['uploaded_images'] = []
    global_data['vote_count'] = defaultdict(int)
    save_metadata(global_data['uploaded_images'])
    st.session_state.voted_images = set()  # 清空投票记录
    st.success("All images and votes have been cleared!")
    st.rerun()  # 清空后重新运行页面

# 文件上传组件
with st.form("upload_form"):
    file_name = st.text_input("Image display name (optional):")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if st.form_submit_button("Upload Image"):
        if uploaded_file:
            # 生成唯一文件名
            unique_id = f"image_{uuid.uuid4()}"
            display_name = file_name or f"Image {len(global_data['uploaded_images']) + 1}"  # 自动编号
            
            # 保存图片文件
            with open(os.path.join(UPLOAD_FOLDER, unique_id), "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 更新全局状态
            new_item = {
                "filename": unique_id,
                "display_name": display_name,
                "upvotes": 0
            }
            global_data['uploaded_images'].append(new_item)
            global_data['vote_count'][unique_id] = 0
            save_metadata(global_data['uploaded_images'])
            st.success("Image uploaded successfully!")

# 图片展示和投票功能
st.subheader("📸 Gallery")
cols = st.columns(6)
for idx, item in enumerate(reversed(global_data['uploaded_images'])):
    col = cols[idx % 6]
    with col:
        try:
            img = Image.open(os.path.join(UPLOAD_FOLDER, item['filename']))
            st.image(img, use_container_width=True)
            
            # 显示名称和投票数
            st.markdown(f"**{item['display_name']}**")
            st.caption(f"Votes: {global_data['vote_count'][item['filename']]}")

            # 投票按钮
            if item['filename'] not in st.session_state.voted_images:
                if st.button("👍 Vote", key=f"vote_{item['filename']}"):
                    global_data['vote_count'][item['filename']] += 1
                    st.session_state.voted_images.add(item['filename'])
                    save_metadata(global_data['uploaded_images'])
                    st.rerun()  # 使用新的 rerun 方法
            else:
                st.warning("You've already voted for this")
                
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")

# 实时投票排行榜
st.subheader("🏆 Leaderboard")
sorted_items = sorted(global_data['uploaded_images'], 
                     key=lambda x: global_data['vote_count'][x['filename']], 
                     reverse=True)
for rank, item in enumerate(sorted_items[:10], 1):
    st.write(f"{rank}. {item['display_name']} - {global_data['vote_count'][item['filename']]} votes")
