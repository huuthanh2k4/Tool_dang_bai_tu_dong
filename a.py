# streamlit_app.py
# Author: Gemini
# Version: 18.0 (Merged Login Options)
# Chức năng: Gộp các tùy chọn đăng nhập bằng hồ sơ (profile) để tiện lợi hơn.

import streamlit as st
import time
import requests
import re
import os
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- CẤU HÌNH CỐ ĐỊNH ---
FIREBASE_URL = "https://bai-test-2ae56-default-rtdb.asia-southeast1.firebasedatabase.app/"
CHROME_PROFILE_PATH = r"D:\tool_dang_bai\tk" 
# ----------------------------------------------------

st.set_page_config(page_title="Facebook Posting Tool", layout="wide")
st.title("🚀 Công cụ Facebook Tự động All-in-One")

# --- CÁC HÀM TƯƠNG TÁC DB (Giữ nguyên) ---
@st.cache_data(ttl=60)
def load_data_from_firebase(path):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def save_account_to_firebase(name, username, password):
    try:
        safe_key = re.sub(r'[.#$\[\]]', '_', name)
        url = f"{FIREBASE_URL}/facebook_accounts/{safe_key}.json"
        data = {'name': name, 'username': username, 'password': password}
        requests.put(url, json=data).raise_for_status()
        st.cache_data.clear()
        return True, f"Đã lưu tài khoản '{name}'!"
    except Exception as e:
        return False, f"Lỗi khi lưu tài khoản: {e}"

def delete_account_from_firebase(account_name):
    try:
        safe_key = re.sub(r'[.#$\[\]]', '_', account_name)
        url = f"{FIREBASE_URL}/facebook_accounts/{safe_key}.json"
        requests.delete(url).raise_for_status()
        st.cache_data.clear()
        return True, f"Đã xóa tài khoản '{account_name}'!"
    except Exception as e:
        return False, f"Lỗi khi xóa tài khoản: {e}"

def save_group_to_firebase(name, group_url):
    try:
        safe_key = re.sub(r'[.#$\[\]]', '_', name)
        url = f"{FIREBASE_URL}/facebook_groups/{safe_key}.json"
        data = {'name': name, 'url': group_url, 'saved_at': datetime.now().isoformat()}
        requests.put(url, json=data).raise_for_status()
        st.cache_data.clear()
        return True, f"Đã lưu nhóm '{name}'!"
    except Exception as e:
        return False, f"Lỗi khi lưu nhóm: {e}"

def delete_group_from_firebase(group_name):
    try:
        safe_key = re.sub(r'[.#$\[\]]', '_', group_name)
        url = f"{FIREBASE_URL}/facebook_groups/{safe_key}.json"
        requests.delete(url).raise_for_status()
        st.cache_data.clear()
        return True, f"Đã xóa nhóm '{group_name}'!"
    except Exception as e:
        return False, f"Lỗi khi xóa nhóm: {e}"

def save_posting_history(history_data):
    try:
        url = f"{FIREBASE_URL}/posting_history.json"
        requests.post(url, json=history_data)
        return True
    except Exception:
        return False

# --- CÁC HÀM TƯƠNG TÁC VỚI SELENIUM (ĐÃ CẬP NHẬT) ---
def delete_chrome_profile(profile_path):
    if os.path.exists(profile_path):
        try:
            shutil.rmtree(profile_path)
            st.toast("Đã xóa phiên đăng nhập cũ thành công.")
            return True
        except Exception as e:
            st.error(f"Lỗi khi xóa hồ sơ cũ: {e}")
            return False
    return True

@st.cache_resource
def init_driver(use_profile=False):
    st.info("Đang khởi tạo trình duyệt Chrome...")
    chrome_options = Options()
    if use_profile:
        st.info(f"Sử dụng hồ sơ tại: {CHROME_PROFILE_PATH}")
        chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
    
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-notifications")
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Lỗi khi khởi tạo trình duyệt: {e}")
        return None

def prefill_login_credentials(driver, username, password):
    st.info("Đang điền thông tin đăng nhập...")
    try:
        wait = WebDriverWait(driver, 10)
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        pass_field = driver.find_element(By.ID, "pass")
        email_field.clear(); pass_field.clear()
        email_field.send_keys(username)
        time.sleep(0.5)
        pass_field.send_keys(password)
        st.success("✅ Đã điền sẵn thông tin.")
        st.warning("VUI LÒNG TỰ NHẤN NÚT 'Đăng nhập' trên cửa sổ Chrome.")
        return True
    except Exception as e:
        st.error(f"Lỗi khi điền thông tin đăng nhập: {e}")
        return False

def post_to_single_group(driver, group_url, post_text):
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(group_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        span_xpaths = [
            "//span[normalize-space(.)='Bạn viết gì đi...']",
            "//span[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'bạn viết gì đi')]",
        ]
        clicked = False
        for xp in span_xpaths:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                el.click()
                clicked = True; break
            except Exception: continue
        if not clicked: return False, "Không mở được cửa sổ đăng bài."
        time.sleep(2)
        content_editable = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[@role='dialog']//div[@data-lexical-editor='true']"
        )))
        content_editable.send_keys(post_text)
        time.sleep(1)
        post_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[@role='button' and .//span[text()='Đăng'] and not(@aria-disabled='true')]"
        )))
        post_button.click()
        time.sleep(8)
        return True, "Đăng bài thành công!"
    except Exception as e:
        return False, f"Lỗi trong quá trình đăng bài: {e}"

# --- GIAO DIỆN CHÍNH VỚI CÁC TAB ---
tab1, tab2, tab3 = st.tabs(["🚀 Công cụ Đăng bài", "👥 Quản lý", "📜 Lịch sử đăng bài"])

# ==============================================================================
# ================================ TAB 1: CÔNG CỤ ĐĂNG BÀI =====================
# ==============================================================================
with tab1:
    if 'driver' not in st.session_state: st.session_state.driver = None
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False

    with st.container(border=True):
        st.header("Bước 1: Mở trình duyệt và Đăng nhập")
        if st.session_state.driver is None:
            accounts_data = load_data_from_firebase("facebook_accounts")
            account_names = []
            if accounts_data:
                account_names = [details['name'] for details in accounts_data.values()]
            
            st.subheader("Chọn phương thức đăng nhập:")
            
            # Option 1: Pre-fill from Firebase
            with st.container(border=True):
                st.markdown("##### 🖊️ Đăng nhập bằng tài khoản đã lưu")
                if not account_names:
                    st.warning("Bạn chưa lưu tài khoản nào. Vui lòng vào tab 'Quản lý' để thêm.")
                else:
                    selected_account_name = st.selectbox("Chọn tài khoản:", account_names)
                    if st.button("Điền thông tin & Mở trình duyệt", key="btn_prefill"):
                        account_details = next((acc for acc in accounts_data.values() if acc['name'] == selected_account_name), None)
                        if account_details:
                            driver_instance = init_driver(use_profile=False)
                            if driver_instance:
                                driver_instance.get("http://facebook.com/")
                                prefill_login_credentials(driver_instance, account_details['username'], account_details['password'])
                                st.session_state.driver = driver_instance
                                st.rerun()

            # Option 2 & 3 Merged: Use/Create Profile
            with st.container(border=True):
                st.markdown("##### 🔄 Đăng nhập bằng hồ sơ (profile) đã lưu")
                st.caption(f"Hồ sơ sẽ được tải hoặc tạo mới tại: `{CHROME_PROFILE_PATH}`")
                
                clear_session = st.checkbox("Xóa phiên đăng nhập cũ trước khi mở", key="cb_clear_session")
                
                if st.button("Mở trình duyệt bằng hồ sơ", key="btn_launch_profile", type="primary"):
                    if clear_session:
                        delete_chrome_profile(CHROME_PROFILE_PATH)
                    
                    driver_instance = init_driver(use_profile=True)
                    if driver_instance:
                        st.session_state.driver = driver_instance
                        st.session_state.driver.get("https://www.facebook.com/")
                        st.session_state.logged_in = True 
                        st.rerun()

        else: # Driver is active
            st.success("✅ Trình duyệt đã được mở.")
            if not st.session_state.logged_in:
                 st.info("Sau khi bạn tự đăng nhập thành công, hãy nhấn nút bên dưới.")
                 if st.button("👍 Tôi đã đăng nhập xong", key="btn_loggedin"):
                    st.session_state.logged_in = True
                    st.rerun()
            else:
                st.success("👍 Trạng thái: Đã sẵn sàng để đăng bài.")

    if st.session_state.logged_in:
        # ... (Phần code còn lại của Tab 1 không thay đổi)
        with st.container(border=True):
            st.header("Bước 2: Chọn Nhóm và Soạn thảo")
            groups_data_main = load_data_from_firebase("facebook_groups")
            saved_groups_main = {}
            if groups_data_main:
                for item in sorted(groups_data_main.values(), key=lambda x: x.get('name', '')):
                    if 'name' in item and 'url' in item:
                        saved_groups_main[item['name']] = item['url']
            group_names_main = list(saved_groups_main.keys())
            selected_groups = st.multiselect("Chọn các nhóm muốn đăng bài:", group_names_main)
            post_content = st.text_area("Nội dung bài đăng:", height=200, placeholder="Nhập nội dung bạn muốn đăng vào đây...")

        with st.container(border=True):
            st.header("Bước 3: Cài đặt và Bắt đầu Đăng bài")
            delay_seconds = st.number_input("Thời gian chờ giữa các lần đăng (giây)", min_value=1, value=5)
            if st.button("🚀 Đăng lên các nhóm đã chọn!", type="primary", use_container_width=True):
                if not selected_groups: st.error("Bạn chưa chọn nhóm nào.")
                elif not post_content.strip(): st.error("Nội dung không được để trống.")
                else:
                    driver = st.session_state.driver
                    st.info(f"Chuẩn bị đăng lên {len(selected_groups)} nhóm...")
                    history_data = { 'post_count': len(selected_groups), 'posted_to_groups': {name: saved_groups_main[name] for name in selected_groups}, 'post_content': post_content, 'timestamp': datetime.now().isoformat() }
                    save_posting_history(history_data)
                    progress_bar = st.progress(0, text="Bắt đầu...")
                    status_placeholder = st.empty()
                    for i, group_name in enumerate(selected_groups):
                        group_url = saved_groups_main[group_name]
                        status_text = f"({i+1}/{len(selected_groups)}) Đang đăng: {group_name}..."
                        progress_bar.progress((i) / len(selected_groups), text=status_text)
                        with st.spinner(status_text):
                            success, message = post_to_single_group(driver, group_url, post_content)
                            if success: status_placeholder.success(f"✅ {group_name}: {message}")
                            else: status_placeholder.error(f"🔥 {group_name}: {message}")
                        if i < len(selected_groups) - 1:
                            st.write(f"Đang chờ {delay_seconds} giây...")
                            time.sleep(delay_seconds)
                    progress_bar.progress(1.0, text="Hoàn tất!")
                    st.balloons()
                    status_placeholder.success("🎉 Hoàn tất quá trình đăng bài!")

# ==============================================================================
# ============================= TAB 2: QUẢN LÝ =================================
# ==============================================================================
with tab2:
    # ... (Phần code trong Tab 2 không thay đổi)
    st.header("👥 Quản lý Tài khoản & Nhóm")
    st.error("**CẢNH BÁO:** Việc lưu mật khẩu trong Firebase là rất rủi ro. Chỉ dùng nếu bạn chấp nhận rủi ro này.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Quản lý tài khoản Facebook")
        with st.form("add_account_form", clear_on_submit=True):
            st.markdown("##### ➕ Thêm tài khoản mới")
            new_acc_name = st.text_input("Tên gợi nhớ cho tài khoản")
            new_acc_user = st.text_input("Tài khoản (Email hoặc SĐT)")
            new_acc_pass = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Lưu tài khoản"):
                if new_acc_name and new_acc_user and new_acc_pass:
                    success, message = save_account_to_firebase(new_acc_name, new_acc_user, new_acc_pass)
                    if success: st.success(message); st.rerun()
                    else: st.error(message)
                else: st.warning("Vui lòng điền đầy đủ thông tin.")
        
        st.markdown("---")
        st.markdown("##### ❌ Xóa tài khoản")
        accounts_data_del = load_data_from_firebase("facebook_accounts")
        account_names_del = []
        if accounts_data_del:
            account_names_del = [details['name'] for details in accounts_data_del.values()]
        
        if account_names_del:
            account_to_delete = st.selectbox("Chọn tài khoản cần xóa:", ["---"] + account_names_del)
            if st.button("Xóa tài khoản đã chọn", type="primary"):
                if account_to_delete != "---":
                    success, message = delete_account_from_firebase(account_to_delete)
                    if success: st.success(message); st.rerun()
                    else: st.error(message)
                else: st.warning("Vui lòng chọn một tài khoản để xóa.")
        else:
            st.info("Không có tài khoản nào để xóa.")

    with col2:
        st.subheader("Quản lý danh sách nhóm")
        groups_data_manage = load_data_from_firebase("facebook_groups")
        group_names_manage = []
        if groups_data_manage:
            group_names_manage = [details['name'] for details in groups_data_manage.values()]

        with st.form("add_group_form_manage", clear_on_submit=True):
            st.markdown("##### ➕ Thêm nhóm mới")
            new_group_name = st.text_input("Tên gợi nhớ cho nhóm")
            new_group_url = st.text_input("Dán link của nhóm (URL)")
            if st.form_submit_button("Lưu nhóm"):
                if new_group_name and new_group_url:
                    if new_group_name in group_names_manage: st.warning(f"Tên nhóm '{new_group_name}' đã tồn tại.")
                    else:
                        success, message = save_group_to_firebase(new_group_name, new_group_url)
                        if success: st.success(message); st.rerun()
                        else: st.error(message)
                else: st.warning("Vui lòng nhập cả Tên và Link.")

        st.markdown("---")
        st.markdown("##### ❌ Xóa nhóm")
        if group_names_manage:
            group_to_delete = st.selectbox("Chọn nhóm cần xóa:", ["---"] + group_names_manage, key="del_group_select")
            if st.button("Xóa nhóm đã chọn", type="primary", key="del_group_btn"):
                if group_to_delete != "---":
                    success, message = delete_group_from_firebase(group_to_delete)
                    if success: st.success(message); st.rerun()
                    else: st.error(message)
                else: st.warning("Vui lòng chọn một nhóm để xóa.")
        else:
            st.info("Không có nhóm nào để xóa.")

# ==============================================================================
# ============================ TAB 3: LỊCH SỬ ĐĂNG BÀI =========================
# ==============================================================================
with tab3:
    # ... (Phần code trong Tab 3 không thay đổi)
    st.header("📜 Lịch sử và Quản lý Bài đăng")
    with st.container(border=True):
        st.subheader("🔗 Mở Nhật ký hoạt động")
        st.info("Nhấn nút dưới đây để mở trang 'Nhật ký hoạt động' của bạn trên cửa sổ Chrome đang chạy.")
        ACTIVITY_LOG_URL = "https://www.facebook.com/me/allactivity?activity_history=false&category_key=GROUPPOSTS"
        if st.button("Mở Nhật ký hoạt động trên Facebook", key="btn_open_activity_log"):
            if 'driver' in st.session_state and st.session_state.driver is not None:
                try:
                    _ = st.session_state.driver.window_handles
                    st.session_state.driver.get(ACTIVITY_LOG_URL)
                    st.success("Đã yêu cầu trình duyệt mở Nhật ký hoạt động!")
                except Exception:
                    st.error("Lỗi: Kết nối đến trình duyệt đã bị mất. Vui lòng quay lại tab chính và khởi động lại.")
            else:
                st.error("Lỗi: Trình duyệt chưa được mở.")
    
    st.markdown("---")
    
    st.subheader("Lịch sử đăng bài (Lưu trên Firebase)")
    if st.button("🔄 Làm mới lịch sử", key="btn_refresh_history"):
        st.cache_data.clear()
        st.rerun()
    history_data = load_data_from_firebase("posting_history")
    if history_data:
        sorted_history = sorted(history_data.values(), key=lambda item: item.get('timestamp', '1970-01-01'), reverse=True)
        for entry in sorted_history:
            with st.container(border=True):
                post_time_str = entry.get('timestamp', 'N/A')
                post_count = entry.get('post_count', 0)
                if post_time_str != 'N/A':
                    try:
                        post_time_dt = datetime.fromisoformat(post_time_str)
                        st.markdown(f"**Thời gian:** {post_time_dt.strftime('%d/%m/%Y %H:%M')}")
                    except (ValueError, TypeError):
                        st.markdown(f"**Thời gian:** {post_time_str}")
                with st.expander(f"Đã đăng {post_count} bài (nhấn để xem chi tiết)"):
                    st.code(entry.get('post_content', ''), language=None)
                    posted_groups = entry.get('posted_to_groups', {})
                    if posted_groups:
                        st.markdown("**Các nhóm đã đăng:**")
                        for name, url in posted_groups.items():
                            st.markdown(f"- [{name}]({url})")
    else:
        st.info("Chưa có lịch sử đăng bài.")