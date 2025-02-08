import streamlit as st
from PIL import Image
import os
import uuid

# 确保 "uploads" 目录存在
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Streamlit 标题
st.title("📷 Upload your images and vote anonymously!")

# 使用 st.session_state 保存投票计数和已上传的图片列表
if 'vote_count' not in st.session_state:
    st.session_state.vote_count = {}

if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []

if 'voted_images' not in st.session_state:
    st.session_state.voted_images = set()

# 用户输入文件名称
file_name = st.text_input("Enter a name for the image (optional):")

# 上传文件
uploaded_file = st.file_uploader("Choose the image", type=["jpg", "jpeg", "png"])

# 上传文件并保存
if uploaded_file is not None:
    # 如果用户没有输入文件名，则使用上传文件的原始名称
    if not file_name:
        file_name = uploaded_file.name

    # 为图片生成唯一编码（匿名名称）
    unique_id = str(uuid.uuid4())  # 生成唯一编码
    encoded_name = f"image_{unique_id}"  # 为图片生成匿名名称

    # 创建新的文件路径
    file_path = os.path.join(UPLOAD_FOLDER, encoded_name)

    # 将文件保存到指定路径
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 将上传的文件记录到 session_state 中
    st.session_state.uploaded_images.append(encoded_name)
    st.success(f"✅ {encoded_name} uploaded successfully!")

# **实时** 显示所有上传的图片（6列布局）
st.subheader("📸 Uploaded Images")
uploaded_files = sorted(st.session_state.uploaded_images, reverse=True)  # 按时间倒序排列

if uploaded_files:
    # 创建6个列的布局，并存入列表
    cols = st.columns(6)

    for i, file in enumerate(uploaded_files):
        img_path = os.path.join(UPLOAD_FOLDER, file)
        try:
            img = Image.open(img_path)
        except Exception as e:
            st.error(f"无法加载 {file}: {e}")
            continue

        # 为每张图片生成一个唯一编号
        image_number = f"Image {i+1}"

        # 通过取模运算选择对应的列展示图片
        col = cols[i % 6]
        with col:
            st.image(img, caption=image_number, use_container_width=True)

            # 初始化投票计数（如果该文件还没有投票数据）
            if file not in st.session_state.vote_count:
                st.session_state.vote_count[file] = {"upvotes": 0}

            # 赞同按钮（仅当未投票时可见）
            if file not in st.session_state.voted_images:
                upvote_button = st.button(f"👍 Upvote {image_number}", key=f"upvote_{file}")
                if upvote_button:
                    st.session_state.vote_count[file]["upvotes"] += 1
                    st.session_state.voted_images.add(file)
                    st.success(f"✅ You upvoted {image_number}!")
            else:
                st.warning(f"❌ You have already voted for {image_number}.")

            # 显示投票结果
            st.write(f"Upvotes: {st.session_state.vote_count[file]['upvotes']}")

# 显示所有投票结果
st.subheader("📊 Voting Results")
for file, votes in st.session_state.vote_count.items():
    # 对应的图片编号
    image_number = f"Image {uploaded_files.index(file) + 1}"
    st.write(f"{image_number} - Upvotes: {votes['upvotes']}")
