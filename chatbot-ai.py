import json
from openai import OpenAI
import streamlit as st
import os
import base64
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ai_handler import get_ai_handler  # Import AI handler module

# # Redirect to Signal Insights as homepage if available
# try:
#     # Adjust the path if your page file name differs
#     st.switch_page("pages/1_Signal_Insights.py")
# except Exception:
#     pass

load_dotenv()

# Function to convert image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set background image
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Semi-transparent overlay for better readability */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        pointer-events: none;
        z-index: -1;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Apply background image
try:
    set_png_as_page_bg('images/first_page.jpg')
except:
    st.warning("Background image not found: images/first_page.jpg")

# Global custom CSS
st.markdown("""
<style>

     /* 新建对话按钮保持绿色 */
    .new-chat> button {
        width: 100%;
        margin: 0;
        padding: 10px 15px;
        background-color: #0071b9;
        color: white;
        border-radius: 5px;
    }
    
    /* 鼠标悬停效果 */
    .stButton > button:hover {
        background-color: transparent;
    }
    
    /* 调整输入框样式 */
    [data-testid="stTextInput"] {
        max-width: 300px;
    }
    
    /* 输入框样式 - 默认无边框 */
    [data-testid="stTextInput"] input {
        background-color: white !important;
        color: black !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 8px 12px !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* 更精确的选择器 - 聚焦时显示底部边框 */
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stTextInput"] input:focus {
        border: none !important;
        border-bottom: 2px solid #0071b9 !important;
        box-shadow: none !important;
        outline: none !important;
        border-radius: 0 !important;
        background-color: #f5f5f5 !important;
    }
    
    /* 强制清除所有容器边框 */
    [data-testid="stTextInput"],
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* 按钮样式 */
    button[kind="primary"] {  
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    button[kind="tertiary"] {  
        justify-content: left !important;
        font-size: 10px !important;
    }
    
    
    /* 侧边栏整体gap设为0 */
    .stSidebar [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    /* 历史记录按钮字体更小 - 使用更具体的选择器 */
    .stSidebar button[kind="tertiary"] {
        font-size: 10px !important;
    }
    
    /* 更强的选择器 - 多种方式确保生效 */
    .stSidebar .stButton button[kind="tertiary"] {
        font-size: 12px !important;
        min-height: 20px !important;
        padding-left: 5px !important;
    }
    
    /* 针对按钮内的文本 */
    .stSidebar button[kind="tertiary"] p {
        font-size: 12px !important;
        min-height: 20px !important;
        padding-left: 5px !important;
    }
    
    /* 最强选择器 */
    div[data-testid="stSidebar"] button[kind="tertiary"] {
        font-size: 12px !important;
        min-height: 20px !important;
        padding-left: 5px !important;
    }
</style>
""", unsafe_allow_html=True)
# 使用容器和列来创建更紧凑的布局
# 只有当有消息时才显示对话名称输入框（即点击历史记录后）
if st.session_state.get('messages', []):
    # Ensure a non-empty chat name
    current_chat_name = st.session_state.get('chat_name', 'Untitled Chat')
    if not current_chat_name:
        current_chat_name = 'Untitled Chat'
    
    new_name = st.text_input(
        label="Chat Name",
        value=current_chat_name,
        key="chat_name_input",
        placeholder="Enter a chat name",
        label_visibility="collapsed",
        help="Set a name for this conversation"
    )
    
    # 只有当名称真正改变时才更新
    if new_name and new_name != current_chat_name:
        st.session_state['chat_name'] = new_name

# Show the title only when there is no message yet
# if not st.session_state.get('messages', []):
#     st.markdown("##### Hello, Girls!")
#     st.title(' I am your Yoga buddy')
    
    # # Down arrow hint to the input at the bottom
    # st.markdown("""
    # <div style="text-align: center; margin-top: 50px; margin-bottom: 100px;">
    #     <p style="font-size: 18px; color: #666; margin-bottom: 20px;">Please type your question at the bottom</p>
    #     <div style="font-size: 30px; color: #0071b9; animation: bounce 2s infinite;">
    #         ↓
    #     </div>
    # </div>
    # <style>
    # @keyframes bounce {
    #     0%, 20%, 50%, 80%, 100% {
    #         transform: translateY(0);
    #     }
    #     40% {
    #         transform: translateY(-10px);
    #     }
    #     60% {
    #         transform: translateY(-5px);
    #     }
    # }
    # </style>
    # """, unsafe_allow_html=True)

# initialize session variables at the start once

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'chat_name' not in st.session_state:
    st.session_state['chat_name'] = 'Untitled Chat'
# Save chat history with a name
def save_chat_history(messages, chat_name):
    if not os.path.exists('chat_history'):
        os.makedirs('chat_history')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history/chat_{chat_name}.json"
    
    # Save chat history with name and timestamp
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "name": chat_name,
            "messages": messages,
            "timestamp": timestamp
        }, f, ensure_ascii=False, indent=2)
    
    return filename
# Load chat histories
def load_chat_histories():
    histories = []
    if os.path.exists('chat_history'):
        for file in os.listdir('chat_history'):
            if file.startswith('chat_') and file.endswith('.json'):
                with open(f'chat_history/{file}', 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        # Use timestamp field from JSON file
                        timestamp = data.get('timestamp', '')
                        if timestamp:
                            try:
                                # Convert timestamp string to datetime
                                creation_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                            except ValueError:
                                # Skip this file if timestamp format is invalid
                                continue
                        else:
                            # Skip if timestamp field is missing
                            continue
                        
                        histories.append({
                            'filename': file,
                            'name': data.get('name', 'Untitled Chat'),
                            'messages': data.get('messages', []),
                            'creation_time': creation_time
                        })
                    except (json.JSONDecodeError, OSError):
                        continue
    return sorted(histories, key=lambda x: x['creation_time'], reverse=True)

def categorize_histories_by_time(histories):
    """Categorize histories by time"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    
    today = []
    this_week = []
    older = []
    
    for history in histories:
        if history['creation_time'] >= today_start:
            today.append(history)
        elif history['creation_time'] >= week_ago:
            this_week.append(history)
        else:
            older.append(history)
    
    return today, this_week, older

# create sidebar to adjust parameters
# st.sidebar.image("images/log.png", width=200)
# st.sidebar.title('TIC产品助手')
# add a button to clear the conversation
# Initialize session state
# if 'chat_name' not in st.session_state:
#     st.session_state['chat_name'] = 'Untitled Chat'
# if st.sidebar.button('+ New Chat', key='new_chat', use_container_width=True,type="primary"):
#     if st.session_state['messages']:
#         chat_name = st.session_state.get('chat_name', 'Untitled Chat')
#         saved_file = save_chat_history(st.session_state['messages'], chat_name)
#     st.session_state['messages'] = []
#     st.session_state['chat_name'] = ''    
#     st.rerun()
# temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
# max_tokens = st.sidebar.slider('Max Tokens', min_value=1, max_value=4096, value=256)

# st.sidebar.markdown("---")
# Load and show histories
histories = load_chat_histories()
today_histories, week_histories, older_histories = categorize_histories_by_time(histories)

# Today
if today_histories:
    st.sidebar.markdown("**Today**")
    for history in today_histories:
        if st.sidebar.button(
            f"{history['name']}", 
            key=f"today_{history['filename']}", 
            type="tertiary", 
            use_container_width=True,
        ):
            st.session_state['messages'] = history['messages']
            st.session_state['chat_name'] = history['name']
            st.rerun()

# This week
if week_histories:
    if today_histories:
        st.sidebar.markdown("")
    st.sidebar.markdown("**This week**")
    for history in week_histories:
        # Show date info
        date_str = history['creation_time'].strftime("%m/%d")
        display_name = f"{history['name']} ({date_str})"
        
        if st.sidebar.button(
            display_name, 
            key=f"week_{history['filename']}", 
            type="tertiary", 
            use_container_width=True,
        ):
            st.session_state['messages'] = history['messages']
            st.session_state['chat_name'] = history['name']
            st.rerun()

# Older
if older_histories:
    if today_histories or week_histories:
        st.sidebar.markdown("")
    st.sidebar.markdown("**Older**")
    for history in older_histories:
        # Show full date info
        date_str = history['creation_time'].strftime("%Y/%m/%d")
        display_name = f"{history['name']} ({date_str})"
        
        if st.sidebar.button(
            display_name, 
            key=f"older_{history['filename']}", 
            type="tertiary", 
            use_container_width=True,
        ):
            st.session_state['messages'] = history['messages']
            st.session_state['chat_name'] = history['name']
            st.rerun()

# update the interface with the previous messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# # create the chat interface
# if prompt := st.chat_input("You can continue asking..."):
#     # Get AI handler
#     ai_handler = get_ai_handler()
    
#     # Process user input
#     processed_prompt = ai_handler.process_user_input(prompt)
    
#     # Check if it is the first message
#     is_first_message = len(st.session_state['messages']) == 0
    
#     # If first message, set chat name to timestamp
#     if is_first_message:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         st.session_state['chat_name'] = timestamp
    
#     st.session_state['messages'].append({"role": "user", "content": processed_prompt})
#     with st.chat_message('user'):
#         st.markdown(processed_prompt)

#     # Get AI response
#     with st.chat_message('assistant'):
#         # Use AI handler to get response
#         response = ai_handler.get_ai_response(st.session_state['messages'])
        
#         # Post-process AI output
#         processed_response = ai_handler.process_ai_output(response)
    
#     st.session_state['messages'].append({"role": "assistant", "content": processed_response})
    
#     # If first message, refresh page to hide title
#     if is_first_message:
#         st.rerun()
