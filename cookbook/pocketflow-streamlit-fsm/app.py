import streamlit as st
import base64
from flow import create_generation_flow

st.title("PocketFlow 图像生成 HITL")

# 初始化会话状态以共享存储
if 'stage' not in st.session_state:
    st.session_state.stage = "initial_input"
    st.session_state.task_input = ""
    st.session_state.generated_image = ""
    st.session_state.final_result = ""
    st.session_state.error_message = ""

# 调试信息
with st.expander("会话状态"):
    st.json({k: v for k, v in st.session_state.items() if not k.startswith("_")})

# 基于状态的 UI
if st.session_state.stage == "initial_input":
    st.header("1. 生成图像")
    
    prompt = st.text_area("输入图像提示:", value=st.session_state.task_input, height=100)
    
    if st.button("生成图像"):
        if prompt.strip():
            st.session_state.task_input = prompt
            st.session_state.error_message = ""
            
            try:
                with st.spinner("正在生成图像..."):
                    flow = create_generation_flow()
                    flow.run(st.session_state)
                st.rerun()
            except Exception as e:
                st.session_state.error_message = str(e)
        else:
            st.error("请输入提示")

elif st.session_state.stage == "user_feedback":
    st.header("2. 审查生成的图像")
    
    if st.session_state.generated_image:
        # 显示图像
        image_bytes = base64.b64decode(st.session_state.generated_image)
        st.image(image_bytes, caption=f"提示: {st.session_state.task_input}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("批准", use_container_width=True):
                st.session_state.final_result = st.session_state.generated_image
                st.session_state.stage = "final"
                st.rerun()
        
        with col2:
            if st.button("重新生成", use_container_width=True):
                try:
                    with st.spinner("正在重新生成图像..."):
                        flow = create_generation_flow()
                        flow.run(st.session_state)
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = str(e)

elif st.session_state.stage == "final":
    st.header("3. 最终结果")
    st.success("图像已批准！")
    
    if st.session_state.final_result:
        image_bytes = base64.b64decode(st.session_state.final_result)
        st.image(image_bytes, caption=f"最终批准的图像: {st.session_state.task_input}")
    
    if st.button("重新开始", use_container_width=True):
        st.session_state.stage = "initial_input"
        st.session_state.task_input = ""
        st.session_state.generated_image = ""
        st.session_state.final_result = ""
        st.session_state.error_message = ""
        st.rerun()

# 显示错误
if st.session_state.error_message:
    st.error(st.session_state.error_message)

