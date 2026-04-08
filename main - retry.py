import sys, os
import ssl
import configparser
import os.path
import random
import re
import threading
import time
from datetime import datetime
from urllib.parse import quote_plus

import requests
import urllib3
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, ttk

# ----------------------------------------------------------------------------------------------------------------------
# 全局配置与状态管理
# ----------------------------------------------------------------------------------------------------------------------
class Course :
    id          = '0'
    class_id    = '0'
    check_list  = []
    class_list  = []

# 用于控制监听线程的停止信号
stop_event  = threading.Event()

# 微信OAuth授权链接
AUTH_URL    = (
    "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx1b5650884f657981&"
    "redirect_uri=https://www.duifene.com/_FileManage/PdfView.aspx?file=https%3A%2F%2Ffs.duifene.com%2F"
    "res%2Fr2%2Fu6106199%2F%E5%AF%B9%E5%88%86%E6%98%93%E7%99%BB%E5%BD%95_876c9d439ca68ead389c.pdf&"
    "response_type=code&scope=snsapi_userinfo&connect_redirect=1#wechat_redirect"
)

def log_message(msg) :
    """ 线程安全的日志记录函数 """
    def _update() :
        if text_box.winfo_exists() :
            text_box.insert(tk.END, msg)
            text_box.see(tk.END)
    root.after(0, _update)

def on_combo_change(event) :
    className = combo_var.get()
    for i in Course.class_list :
        if i["CourseName"] == className :
            Course.id       = i["CourseID"]
            Course.class_id = i["TClassID"]
            log_message(f"[系统] 课程已切换为：{className}\n")

def copy_auth_link() :
    """ 复制授权链接到剪贴板 """
    root.clipboard_clear()
    root.clipboard_append(AUTH_URL)
    root.update()
    messagebox.showinfo("复制成功", "链接已复制！\n请发送给微信'文件传输助手'并点击，然后复制跳转后的链接。")

def login_by_account(loginname, password, is_auto_reconnect=False) :
    """ 使用账号密码直接请求登录接口，支持初始登录或断线重连 """
    try :
        url         = host + "/AppCode/LoginInfo.ashx"
        headers     = {
            "Content-Type"      : "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With"  : "XMLHttpRequest",
            "Referer"           : host + "/"
        }
        
        # 对账密进行 URL 编码，防止包含特殊字符导致表单解析失败
        safe_user   = quote_plus(loginname)
        safe_pwd    = quote_plus(password)
        payload     = f"action=login&loginname={safe_user}&password={safe_pwd}&issave=false&guid=D14235ECE342D7C6"
        
        x.cookies.clear()
        _r          = x.post(url=url, data=payload, headers=headers, timeout=10)

        if _r.status_code == 200 :
            _json = _r.json()
            if _json.get("msg") == "1" :
                # 核心修复：账号密码默认是PC端Session，必须访问一次移动端主页来激活MB上下文状态！
                x.get(url=host + "/_UserCenter/MB/index.aspx", timeout=10)
                
                get_class_list()
                if not is_auto_reconnect :
                    log_message("\n[系统] 账号密码登录成功！请在右侧选择课程。\n")
                return True
            else :
                msg = _json.get('msgbox', '未知错误')
                log_message(f"\n[错误] 登录失败，服务器返回：{msg}\n")
    except Exception as e :
        log_message(f"\n[异常] 登录请求发生异常：{e}\n")
    return False

def on_account_login_click() :
    """ UI 界面的账号登录按钮触发事件 """
    user    = account_entry.get()
    pwd     = password_entry.get()
    if not user or not pwd :
        messagebox.showwarning("提示", "账号和密码不能为空！")
        return
        
    if login_by_account(user, pwd) :
        # 登录成功后保存到配置文件，方便下次直连
        config['SETTING']['loginname']  = user
        config['SETTING']['password']   = pwd
        save_setting(show_msg=False)

def login_link() :
    """ 手动填入链接后的旧版微信登录逻辑 """
    try :
        link = link_entry.get()
        if not link.startswith("http") :
            raise ValueError("链接格式不正确")

        code = re.search(r"(?<=code=)\S{32}", link)
        if code is None :
            raise ValueError("链接中未找到授权码 (code=...)")

        x.cookies.clear()
        _r = x.get(url=host + f"/P.aspx?authtype=1&code={code.group(0)}&state=1", timeout=10)

        if _r.status_code == 200 :
            get_class_list()
            log_message("\n[系统] 微信授权登录成功！请在右侧选择课程。\n")
        else :
            raise ConnectionError(f"登录请求失败，状态码：{_r.status_code}")
    except Exception as e :
        messagebox.showerror("登录失败", str(e))
        log_message(f"\n[登录错误] {str(e)}\n")

def get_user_id() :
    try :
        _r = x.get(url=host + "/_UserCenter/MB/index.aspx", timeout=10)
        if _r.status_code == 200 :
            soup    = BeautifulSoup(_r.text, "html.parser")
            val     = soup.find(id="hidUID")
            if val :
                return val.get("value")
    except Exception :
        pass
    return None

def sign(sign_code) :
    """ 签到核心逻辑：处理常规数字签到与二维码签到的状态拦截！"""
    try :
        # 数字/普通签到 (通常为4位数)
        if len(sign_code) == 4 :
            headers = {
                "Content-Type"  : "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer"       : host + "/_CheckIn/MB/CheckInStudent.aspx?moduleid=16&pasd="
            }
            uid = get_user_id()
            if not uid :
                return False

            params  = f"action=studentcheckin&studentid={uid}&checkincode={sign_code}"
            _r      = x.post(url=host + "/_CheckIn/CheckIn.ashx", data=params, headers=headers, timeout=10)

            if _r.status_code == 200 :
                try :
                    msg = _r.json().get("msgbox", "未知状态")
                    log_message(f"\t[数字签到] {msg}\n\n")
                    if msg == "签到成功！" :
                        return True
                except :
                    log_message("\t[数字签到] 响应解析失败\n")
                    
        # 二维码签到
        else :
            # 请求移动端二维码验证接口
            _r_mb = x.get(url=host + "/_CheckIn/MB/QrCodeCheckOK.aspx?state=" + sign_code, timeout=10)
            if _r_mb.status_code == 200 :
                soup    = BeautifulSoup(_r_mb.text, "html.parser")
                div_ok  = soup.find(id="DivOK")
                
                if div_ok :
                    actual_msg = div_ok.get_text(strip=True)
                    if "签到成功" in actual_msg :
                        log_message(f"\t[二维码端] {actual_msg}\n\n")
                        return True
                    else :
                        log_message(f"\t[MB端拦截] 返回结果: {actual_msg}\n")
                        log_message("\t[安全分析] 检测到服务端拒绝了无微信身份的请求！\n")
                        log_message("\t[解决方案] 请使用界面下方的【备用：微信链接登录】重新获取带有 OpenID 的 Cookie！\n\n")
                        
    except Exception as e :
        log_message(f"\t[签到异常] 发生错误：{e}\n")
        
    return False

def sign_location(longitude, latitude) :
    try :
        # 增加随机偏移防检测
        longitude   = str(round(float(longitude) + random.uniform(-0.000089, 0.000089), 8))
        latitude    = str(round(float(latitude) + random.uniform(-0.000089, 0.000089), 8))

        headers     = {
            "Content-Type"  : "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer"       : host + "/_CheckIn/MB/CheckInStudent.aspx?moduleid=16&pasd="
        }
        uid         = get_user_id()
        params      = f"action=signin&sid={uid}&longitude={longitude}&latitude={latitude}"

        _r          = x.post(url=host + "/_CheckIn/CheckInRoomHandler.ashx", data=params, headers=headers, timeout=10)
        if _r.status_code == 200 :
            msg = _r.json().get("msgbox", "未知")
            log_message(f"\t{msg}\n\n")
            if msg == "签到成功！" :
                return True
    except Exception as e :
        log_message(f"\t[定位签到异常] {e}\n")
    return False

def get_arrival_count(ciid) :
    try :
        ajax_url    = host + "/_CheckIn/MBCount.ashx"
        params      = {
            "action"    : "getcheckintotalbyciid",
            "ciid"      : ciid,
            "t"         : "cking"
        }

        response        = x.get(ajax_url, params=params, timeout=5)
        data            = response.json()
        arrival_count   = data.get("TotalNumber", 0) - data.get("AbsenceNumber", 0)
        total_count     = data.get("TotalNumber", 1)
        
        if total_count == 0 : 
            total_count = 1

        percent_setting = int(signed_percent.get()) / 100
        if (arrival_count / total_count) >= percent_setting :
            return True, arrival_count
        else :
            return False, arrival_count
    except Exception :
        return False, 0

def watching_task() :
    """ 运行在独立线程中的监控任务 """
    log_message(f"监控线程已启动... 正在监听课程 ID: {Course.class_id}\n")

    while not stop_event.is_set() :
        try :
            # 检查登录状态，断线自动重连核心逻辑
            if not is_login() :
                log_message("\n[警告] Session过期或断线，正在尝试自动重连...\n")
                user = config['SETTING'].get('loginname', '')
                pwd  = config['SETTING'].get('password', '')

                if user and pwd :
                    if login_by_account(user, pwd, is_auto_reconnect=True) :
                        log_message(f"[系统] 自动重连成功！恢复原有监控状态 (课程ID: {Course.class_id})\n\n")
                        continue  # 重连成功后直接进入下一轮循环，无缝衔接
                    else :
                        log_message("[致命] 自动重连失败，10秒后再次尝试...\n")
                        time.sleep(10)
                        continue
                else :
                    log_message("[致命] 没有保存账号密码，无法自动重连，被迫停止监听！\n")
                    break

            current_time    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            url             = (host + f"/_CheckIn/MB/TeachCheckIn.aspx?classid={Course.class_id}"
                               f"&temps=0&checktype=1&isrefresh=0&timeinterval=0&roomid=0&match=")
                               
            # 添加移动端的 Referer 防止后端拦截
            headers         = {
                "Referer"   : host + f"/_UserCenter/MB/Module.aspx?data={Course.id}"
            }
            _r              = x.get(url=url, headers=headers, timeout=10)

            if _r.status_code == 200 and "HFChecktype" in _r.text :
                soup = BeautifulSoup(_r.text, "html.parser")

                def safe_get_val(elem_id) :
                    el = soup.find(id=elem_id)
                    return el.get("value") if el else None

                HFSeconds   = safe_get_val("HFSeconds")
                HFChecktype = safe_get_val("HFChecktype")
                HFCheckInID = safe_get_val("HFCheckInID")
                HFClassID   = safe_get_val("HFClassID")
                status      = False

                if HFClassID and (Course.class_id in HFClassID) :
                    if HFCheckInID and (HFCheckInID not in Course.check_list) :
                        signable, signed_count = get_arrival_count(HFCheckInID)
                        log_prefix = f"\n{current_time} [监测中] ID:{HFCheckInID}"

                        if HFChecktype == '1' :
                            sign_code = safe_get_val("HFCheckCodeKey")
                            if signable :
                                log_message(f"{log_prefix} -> 触发数字签到: {sign_code}\n")
                                status = sign(sign_code)
                            else :
                                log_message(f"{log_prefix} 等待比例 ({signed_count}人已签) | 倒计时: {HFSeconds}s\n")
                        elif HFChecktype == '2' :
                            if signable :
                                log_message(f"{log_prefix} -> 触发二维码签到\n")
                                status = sign(HFCheckInID)
                            else :
                                log_message(f"{log_prefix} 等待比例 ({signed_count}人已签) | 倒计时: {HFSeconds}s\n")
                        elif HFChecktype == '3' :
                            lng = safe_get_val("HFRoomLongitude")
                            lat = safe_get_val("HFRoomLatitude")
                            if lng and lat and signable :
                                log_message(f"{log_prefix} -> 触发定位签到\n")
                                status = sign_location(lng, lat)
                            else :
                                log_message(f"{log_prefix} 等待比例 ({signed_count}人已签) | 倒计时: {HFSeconds}s\n")

                        if status :
                            Course.check_list.append(HFCheckInID)
                else :
                    log_message(f"{current_time} 暂无本班签到活动...\n")
            else :
                log_message(f"{current_time} 暂无活动 (No HFChecktype)\n")

        except requests.exceptions.RequestException :
            log_message(f"{datetime.now().strftime('%H:%M:%S')} [网络错误] 连接超时或断开，重试中...\n")
        except Exception as e :
            log_message(f"{datetime.now().strftime('%H:%M:%S')} [未知错误] {str(e)}\n")

        time.sleep(2)

def go_sign() :
    if not combo.get() :
        messagebox.showerror("错误提示", "请先登录并选择课程！")
        return

    if not stop_event.is_set() and threading.active_count() > 2 :
        return

    stop_event.clear()
    headers = { "Referer": host + "/_UserCenter/MB/index.aspx" }

    try :
        _r = x.get(url=host + "/_UserCenter/MB/Module.aspx?data=" + Course.id, headers=headers, timeout=10)
        if _r.status_code == 200 and Course.id in _r.text :
            text_box.delete("1.0", "end")
            soup        = BeautifulSoup(_r.text, "html.parser")
            el          = soup.find(id="CourseName")
            course_name = el.text if el else "未知课程"

            text_box.insert(tk.END, f"正在监听【{course_name}】的签到活动\n\n")
            t = threading.Thread(target=watching_task, daemon=True)
            t.start()
    except Exception as e :
        messagebox.showerror("启动失败", str(e))

def stop_sign() :
    stop_event.set()
    log_message("\n[系统] 正在停止监听...\n")

def get_class_list() :
    headers = {
        "Content-Type"  : "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer"       : host + "/_UserCenter/PC/CenterStudent.aspx"
    }
    params  = "action=getstudentcourse&classtypeid=2"

    try :
        _r = x.post(url=host + "/_UserCenter/CourseInfo.ashx", data=params, headers=headers, timeout=10)
        if _r.status_code == 200 :
            _json = _r.json()
            if isinstance(_json, dict) and "msgbox" in _json :
                messagebox.showerror("失效", f"{_json['msgbox']} 请重新登录。")
                x.cookies.clear()
            elif isinstance(_json, list) :
                class_name_list = []
                for i in _json :
                    class_name_list.append(i["CourseName"])
                combo['values'] = tuple(class_name_list)
                if class_name_list :
                    combo.set(class_name_list[0])
                    Course.id           = _json[0]['CourseID']
                    Course.class_id     = _json[0]["TClassID"]
                    Course.class_list   = _json
    except Exception as e :
        messagebox.showerror("获取课程失败", f"网络或解析错误: {e}")

def is_login() :
    headers = {
        "Referer"       : host + "/_UserCenter/PC/CenterStudent.aspx",
        "Content-Type"  : "application/x-www-form-urlencoded; charset=UTF-8"
    }
    try :
        _r = x.get(host + "/AppCode/LoginInfo.ashx", data="Action=checklogin", headers=headers, timeout=5)
        if _r.status_code == 200 :
            if _r.json().get("msg") == "1" :
                return True
    except :
        pass
    return False

def save_setting(show_msg=True) :
    config['SETTING']['signed_percent'] = signed_percent.get()
    config['SETTING']['loginname']      = account_entry.get()
    config['SETTING']['password']       = password_entry.get()
    try :
        with open(filename, 'w', encoding='utf-8') as configfile :
            config.write(configfile)
        if show_msg :
            messagebox.showinfo("提示", "设置保存成功！")
    except Exception as e :
        messagebox.showerror("保存失败", f"错误信息：{str(e)}")

def read_setting(filename) :
    if not os.path.exists(filename) :
        config['SETTING'] = {
            'signed_percent'    : '50',
            'loginname'         : '',
            'password'          : ''
        }
        try :
            with open(filename, 'w', encoding='utf-8') as configfile :
                config.write(configfile)
        except Exception as e :
            messagebox.showerror("创建配置失败", f"错误信息：{str(e)}")
    try :
        config.read(filename, encoding='utf-8')
        if 'signed_percent' not in config['SETTING'] : config['SETTING']['signed_percent']  = '50'
        if 'loginname' not in config['SETTING'] :      config['SETTING']['loginname']       = ''
        if 'password' not in config['SETTING'] :       config['SETTING']['password']        = ''
    except Exception as e :
        messagebox.showerror("读取配置失败", f"错误信息：{str(e)}")

# ----------------------------------------------------------------------------------------------------------------------
# 主程序入口
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    try :
        host    = "https://www.duifene.com"
        
        # 伪装成微信内置浏览器，防止移动端页面拦截PC端会话！
        UA      = 'Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 MicroMessenger/8.0.37.2380(0x2800255B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN'
        urllib3.disable_warnings()

        x                   = requests.Session()
        x.headers['User-Agent'] = UA
        x.verify            = False

        config              = configparser.ConfigParser()
        filename            = 'duifenyi.ini'
        read_setting(filename)

        # 创建主窗口
        root = tk.Tk()
        root.title("对分易自动签到 v4.0 (网安特供免断线增强版)")
        root.geometry("900x700")
        root.resizable(True, True)

        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=3)
        root.grid_columnconfigure(1, weight=1)

        style = ttk.Style()
        style.theme_use('clam')
        font_style = ('微软雅黑', 10)
        style.configure('TButton', font=font_style, padding=5)
        style.configure('Accent.TButton', font=('微软雅黑', 11), foreground='white', background='#2196F3')
        style.map('Accent.TButton', background=[('active', '#1976D2')])

        # 选项卡控件
        tab_control = ttk.Notebook(root)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text="登录")
        tab_control.add(tab2, text="设置")
        tab_control.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # === 登录页内容 ===
        login_frame = ttk.Frame(tab1)
        
        # 1. 账号密码直连模块 (新增)
        step_account_frame = ttk.LabelFrame(login_frame, text="✨ 推荐：账号密码登录 (支持断线自动重连)")
        step_account_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(step_account_frame, text="账号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        account_entry = ttk.Entry(step_account_frame, width=25)
        account_entry.insert(0, config['SETTING']['loginname'])
        account_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(step_account_frame, text="密码:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        password_entry = ttk.Entry(step_account_frame, width=25, show="*")
        password_entry.insert(0, config['SETTING']['password'])
        password_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Button(step_account_frame, text="立即直连", command=on_account_login_click, style='Accent.TButton').grid(row=0, column=4, padx=15, pady=5)
        
        # 2. 微信旧版本模块
        step1_frame = ttk.LabelFrame(login_frame, text="备用：微信链接登录 - 第1步：获取授权")
        step1_frame.pack(fill=tk.X, padx=5, pady=(15, 5))
        auth_link_entry = ttk.Entry(step1_frame)
        auth_link_entry.insert(0, AUTH_URL)
        auth_link_entry.configure(state='readonly')
        auth_link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        ttk.Button(step1_frame, text="复制链接", command=copy_auth_link, width=10).pack(side=tk.RIGHT, padx=5)
        
        step2_frame = ttk.LabelFrame(login_frame, text="备用：微信链接登录 - 第2步：填入链接")
        step2_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(step2_frame, text="请将上方链接发给微信传输助手并点击，然后粘贴跳转后的链接：", font=('微软雅黑', 9), foreground='gray').pack(pady=(5,0), anchor=tk.W, padx=5)
        link_entry = ttk.Entry(step2_frame, width=50)
        link_entry.pack(pady=5, padx=5, fill=tk.X)
        ttk.Button(step2_frame, text="解析链接并登录", command=login_link, width=20).pack(pady=5)
        
        login_frame.pack(pady=10, fill=tk.X, padx=10)

        # === 设置页内容 ===
        setting_frame = ttk.Frame(tab2)
        help_text = """设置说明：
        1. 当签到人数达到班级总人数的设定比例时，程序才会执行签到。
        2. 建议使用【账号密码登录】模式，程序在Cookie失效时会自动触发无感重连。
        3. 如果本课程频繁使用二维码签到，请务必使用【微信链接登录】获取权限。"""
        ttk.Label(setting_frame, text=help_text, font=font_style, justify=tk.LEFT).pack(pady=10, anchor=tk.W)

        form_frame = ttk.Frame(setting_frame)
        ttk.Label(form_frame, text="签到百分比:", width=10).grid(row=0, column=0, sticky='e', padx=5)
        signed_percent = ttk.Entry(form_frame, width=8)
        signed_percent.insert(0, config['SETTING']['signed_percent'])
        signed_percent.grid(row=0, column=1, sticky='w', pady=5)

        ttk.Button(form_frame, text="保存所有设置", command=save_setting, width=18).grid(row=1, columnspan=2, pady=15)
        form_frame.pack(pady=10)
        setting_frame.pack(fill=tk.BOTH, expand=True)

        # === 右侧控制面板 ===
        control_frame = ttk.Frame(root)
        control_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        ttk.Label(control_frame, text="当前课程", font=('微软雅黑', 12)).pack(pady=8)
        combo_var = tk.StringVar()
        combo = ttk.Combobox(control_frame, textvariable=combo_var, state="readonly", width=18)
        combo.pack(pady=5, ipady=2)
        combo.bind("<<ComboboxSelected>>", on_combo_change)

        start_btn = ttk.Button(control_frame, text="开始监听", command=go_sign, style='Accent.TButton', width=16)
        start_btn.pack(pady=5)

        stop_btn = ttk.Button(control_frame, text="停止监听", command=stop_sign, width=16)
        stop_btn.pack(pady=5)

        # === 日志输出 ===
        log_frame = ttk.Frame(root)
        text_box = tk.Text(log_frame, wrap=tk.WORD, font=('微软雅黑', 9), undo=True, maxundo=100)
        scroll = ttk.Scrollbar(log_frame, command=text_box.yview)
        text_box.configure(yscrollcommand=scroll.set)

        text_box.grid(row=0, column=0, sticky='nsew')
        scroll.grid(row=0, column=1, sticky='ns')
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='nsew')

        root.mainloop()

    except Exception as e :
        import traceback
        traceback.print_exc()
        print("\n" + "="*50)
        print("程序发生严重错误！")
        print(f"错误信息: {e}")
        print("请截图联系开发者，或检查网络/配置。")
        print("="*50)
        input("按回车键退出...")