import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import threading
import json
from datetime import datetime
from spirems.image_io.adaptor import cvimg2sms, sms2cvimg, pcl2sms
from spirems.msg_helper import get_all_msg_types, get_all_msg_schemas, get_all_foxglove_schemas, def_msg
import cv2


class AddressTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("smsbag -> mcap 转包工具")
        self.root.geometry("800x600")  # 设置窗口初始大小
        
        # 存储左右列表数据
        self.left_addresses = []
        self.right_addresses = []

        # 存储时间范围
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.rec_time_start = 0.0
        
        # 创建主布局
        self.create_widgets()
    
    def validate_float(self, value):
        """验证输入是否为浮点数字或空值"""
        if value == "":  # 允许空输入
            return True
        try:
            float(value)  # 尝试转换为浮点数
            return True
        except ValueError:
            return False
        
    def create_widgets(self):
        # 顶部路径输入区域
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X, expand=False)
        
        # 输入文件夹路径
        ttk.Label(top_frame, text="smsbag地址:").pack(side=tk.LEFT, padx=5)
        self.source_path_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.source_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="选择smsbag文件夹", command=self.load_source_path).pack(side=tk.LEFT, padx=5)
        
        # 中间地址列表和操作按钮区域（关键修改：使用网格布局确保左右列表高度一致）
        mid_frame = ttk.Frame(self.root, padding="10")
        mid_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧列表区域（含标签）
        left_label = ttk.Label(mid_frame, text="可选话题列表")
        left_label.grid(row=0, column=0, sticky=tk.W, padx=5)  # 标签放第0行第0列
        
        left_frame = ttk.Frame(mid_frame)
        left_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5)  # 列表放第1行第0列，拉伸填充
        mid_frame.grid_rowconfigure(1, weight=1)  # 第1行允许拉伸（关键：让列表高度随窗口变化）
        mid_frame.grid_columnconfigure(0, weight=1)  # 第0列允许拉伸
        
        self.left_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, width=30)
        self.left_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.left_listbox.yview)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_listbox.config(yscrollcommand=left_scrollbar.set)
        
        # 中间操作按钮
        button_frame = ttk.Frame(mid_frame, padding="10")
        button_frame.grid(row=1, column=1, sticky=tk.N, padx=5)  # 按钮放第1行第1列，顶部对齐
        
        self.add_btn = ttk.Button(button_frame, text="→", command=self.add_to_right)
        self.add_btn.pack(fill=tk.X, pady=5)
        
        self.remove_btn = ttk.Button(button_frame, text="←", command=self.remove_from_right)
        self.remove_btn.pack(fill=tk.X, pady=5)
        
        # 右侧列表区域（含标签）
        right_label = ttk.Label(mid_frame, text="已选话题列表")
        right_label.grid(row=0, column=2, sticky=tk.W, padx=5)  # 标签放第0行第2列
        
        right_frame = ttk.Frame(mid_frame)
        right_frame.grid(row=1, column=2, sticky=tk.NSEW, padx=5)  # 列表放第1行第2列，拉伸填充
        mid_frame.grid_columnconfigure(2, weight=1)  # 第2列允许拉伸（与左侧列权重一致）
        
        self.right_listbox = tk.Listbox(right_frame, selectmode=tk.SINGLE, width=30)
        self.right_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.right_listbox.yview)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_listbox.config(yscrollcommand=right_scrollbar.set)


        # 第一行：时间范围输入（放在mcap输出路径上方）
        time_frame = ttk.Frame(self.root, padding="10")
        time_frame.pack(fill=tk.X, expand=False)  # 与下一行保持间距
        
        ttk.Label(time_frame, text="起始时间（单位s）：").pack(side=tk.LEFT, padx=5)
        start_time_entry = ttk.Entry(time_frame, textvariable=self.start_time_var, width=15)
        start_time_entry.pack(side=tk.LEFT, padx=5)
        start_time_entry.config(validate="key", validatecommand=(self.root.register(self.validate_float), '%P'))
        
        ttk.Label(time_frame, text="结束时间（单位s）：").pack(side=tk.LEFT, padx=15)
        end_time_entry = ttk.Entry(time_frame, textvariable=self.end_time_var, width=15)
        end_time_entry.pack(side=tk.LEFT, padx=5)
        end_time_entry.config(validate="key", validatecommand=(self.root.register(self.validate_float), '%P'))

        self.png_checkbox_var = tk.BooleanVar()
        # 设置默认值为未选中（False）
        self.png_checkbox_var.set(False)
        ttk.Checkbutton(time_frame, text="输出png", variable=self.png_checkbox_var).pack(side=tk.LEFT, padx=5)


        # 底部输出路径和进度区域
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X, expand=False)
        
        # 输出路径
        ttk.Label(bottom_frame, text="mcap输出路径:").pack(side=tk.LEFT, padx=5)
        self.output_path_var = tk.StringVar()
        ttk.Entry(bottom_frame, textvariable=self.output_path_var, width=40).pack(side=tk.LEFT, padx=5)
        self.checkbox_var = tk.BooleanVar()
        # 设置默认值为未选中（False）
        self.checkbox_var.set(False)
        ttk.Checkbutton(bottom_frame, text="生成消息质量", variable=self.checkbox_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="开始转包", command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X, expand=False)
        
        ttk.Label(progress_frame, text="转换进度:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=600
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT, padx=5)
    
    # 以下方法与之前一致，省略...
    def load_source_path(self):
        path = filedialog.askdirectory(title="选择源文件夹")
        if path:
            self.source_path_var.set(path)
            try:
                if not os.path.basename(path).startswith("smsbag_"):
                    raise ValueError("请打开以smsbag_开头的文件夹")
                meta_info_fn = os.path.join(path, "metadata.json")
                if os.path.isfile(meta_info_fn):
                    print(meta_info_fn)
                else:
                    subdirs = sorted(
                        [entry.name for entry in os.scandir(path) if entry.is_dir()],
                        key=lambda x: x.lower()
                    )
                    if len(subdirs) > 0 and os.path.isfile(os.path.join(path, subdirs[0], "metadata.json")):
                        meta_info_fn = os.path.join(path, subdirs[0], "metadata.json")
                        print(meta_info_fn)
                    else:
                        raise ValueError("找不到metadata.json")
                # items = os.listdir(path)
                # self.left_addresses = items
                # self.update_left_list()
                with open(meta_info_fn, 'r', encoding='utf-8') as f:
                    # json.load() 直接将 JSON 内容转换为 dict
                    data_dict = json.load(f)
                self.left_addresses = [t for t in data_dict["topics_with_message_count"].keys()]
                self.update_left_list()

                self.start_time_var.set(0)
                self.end_time_var.set(data_dict["duration"] / 1000)
                self.rec_time_start = data_dict["starting_time"] / 1000
            except Exception as e:
                messagebox.showerror("错误", f"{str(e)}")
    
    def update_left_list(self):
        self.left_listbox.delete(0, tk.END)
        for item in self.left_addresses:
            self.left_listbox.insert(tk.END, item)
    
    def update_right_list(self):
        self.right_listbox.delete(0, tk.END)
        for item in self.right_addresses:
            self.right_listbox.insert(tk.END, item)
    
    def add_to_right(self):
        selected_indices = self.left_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先在左侧列表选择一个地址")
            return
        index = selected_indices[0]
        selected_item = self.left_addresses[index]
        if selected_item not in self.right_addresses:
            self.right_addresses.append(selected_item)
            self.update_right_list()
    
    def remove_from_right(self):
        selected_indices = self.right_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先在右侧列表选择一个地址")
            return
        index = selected_indices[0]
        del self.right_addresses[index]
        self.update_right_list()
    
    def start_conversion(self):
        output_path = self.output_path_var.get()
        if not output_path:
            # messagebox.showinfo("提示", "请输入输出路径")
            # return
            output_path = self.source_path_var.get()
            self.output_path_var.set(self.source_path_var.get())
        if not self.right_addresses:
            messagebox.showinfo("提示", "请先选择要转换的地址")
            return
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                messagebox.showerror("错误", f"创建输出路径失败: {str(e)}")
                return
        self.add_btn.config(state=tk.DISABLED)
        self.remove_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.perform_conversion, daemon=True).start()
    
    def perform_conversion(self):
        total = len(self.right_addresses)
        from spirems import SMSBagPlayer
        from mcap.writer import Writer
        import base64
        smsbag_dir = self.source_path_var.get()
        player = SMSBagPlayer(smsbag_dir)
        urls = {}
        schemas = {}
        # print(self.right_addresses)
        json_schemas = get_all_foxglove_schemas()
        now = datetime.now()
        interval = {}
        with open(os.path.join(self.output_path_var.get(), now.strftime("smsmcap_%Y-%m-%d_%H-%M-%S.mcap")), "wb") as f:
            writer = Writer(f)
            writer.start()
            while 1:
                msg = player.next()
                if msg is None:
                    break
                url = msg['msg']['url']
                if url not in self.right_addresses:
                    continue
                
                progress = player.get_progress() * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{int(progress)}%")

                if not (self.rec_time_start + float(self.start_time_var.get()) < msg['msg']['timerec'] < self.rec_time_start + float(self.end_time_var.get())):
                    continue

                if msg['msg']['type'] == "memory_msgs::RawImage":
                    msg_jpg = cvimg2sms(msg['raw'], frame_id=msg['msg']['frame_id'], timestamp=msg['msg']['timestamp'])
                    msg['msg'].update(msg_jpg)

                    if self.png_checkbox_var.get():
                        png_dir = os.path.join(smsbag_dir, 'png' + url.replace('/', '-'))
                        if not os.path.exists(png_dir):
                            os.makedirs(png_dir, exist_ok=True)
                        if os.path.isdir(png_dir):
                            cv2.imwrite(
                                os.path.join(png_dir, str(int(msg['msg']['timestamp'] * 1000))) + '.png', 
                                msg['raw'], 
                                [cv2.IMWRITE_PNG_COMPRESSION, 3]
                            )

                elif msg['msg']['type'] == "memory_msgs::PointCloud":
                    msg_pcl = pcl2sms(
                        msg['raw'],
                        fields=msg['msg']['fields'],
                        frame_id=msg['msg']['frame_id'],
                        timestamp=msg['msg']['timestamp']
                    )
                    msg['msg'].update(msg_pcl)

                msg_type = msg['msg']['type']
                if url not in urls:
                    if msg_type.startswith("sensor_msgs::") or msg_type.startswith("geometry_msgs::"):
                        msg_type = 'foxglove.' + msg_type.split('::')[-1]
                    if msg_type in json_schemas:
                        schema_id = writer.register_schema(
                            name=msg_type,
                            encoding="jsonschema",
                            data=json.dumps(json_schemas[msg_type]).encode(),
                        )
                    else:
                        schema_id = writer.register_schema(
                            name=msg_type,
                            encoding="jsonschema",
                            data=json.dumps(
                                {
                                    "type": "object",
                                    "properties": {},
                                }
                            ).encode(),
                        )
                    channel_id = writer.register_channel(
                        schema_id=schema_id,
                        topic=url,
                        message_encoding="json",
                    )
                    urls[url] = channel_id
                else:
                    channel_id = urls[url]

                if msg['msg']['timestamp'] == 0:
                    msg['msg']['timestamp'] = msg['msg']['timerec']
                msg_delay = msg['msg']['timerec'] - msg['msg']['timestamp']
                # print("T1", msg['msg']['timestamp'])
                # print("T2", msg['msg']['timerec'])
                if url not in interval:
                    msg_interval = 0
                    interval[url] = msg['msg']['timerec']  # msg['msg']['timestamp']
                else:
                    msg_interval = msg['msg']['timerec'] - interval[url]
                    interval[url] = msg['msg']['timerec']

                # 序列化 JSON 数据为二进制（utf-8 编码）
                json_bytes = json.dumps(msg['msg'], ensure_ascii=False).encode("utf-8")

                # 时间戳（纳秒，此处用示例数据中的 timestamp 乘以 1e9 转换为纳秒）
                timestamp_ns = int(msg['msg']["timestamp"] * 1e9)

                # 写入消息（log_time 和 publish_time 可设为同一时间戳）
                writer.add_message(
                    channel_id=channel_id,
                    data=json_bytes,
                    log_time=timestamp_ns,
                    publish_time=timestamp_ns,
                )

                if self.checkbox_var.get():
                    msg_quality_url = url + "/quality"
                    if msg_quality_url not in urls:
                        schema_id = writer.register_schema(
                            name="std_msgs::Null",
                            encoding="jsonschema",
                            data=json.dumps(
                                {
                                    "type": "object",
                                    "properties": {},
                                }
                            ).encode(),
                        )
                        channel_id = writer.register_channel(
                            schema_id=schema_id,
                            topic=msg_quality_url,
                            message_encoding="json",
                        )
                        urls[msg_quality_url] = channel_id
                    else:
                        channel_id = urls[msg_quality_url]
                    
                    msg_quality = def_msg("std_msgs::Null")
                    msg_quality['msg_interval'] = msg_interval
                    msg_quality['msg_delay'] = msg_delay

                    json_bytes = json.dumps(msg_quality, ensure_ascii=False).encode("utf-8")

                    writer.add_message(
                        channel_id=channel_id,
                        data=json_bytes,
                        log_time=timestamp_ns,
                        publish_time=timestamp_ns,
                    )


            writer.finish()

        progress = 100
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}%")
        self.root.after(0, lambda: self.add_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.remove_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: messagebox.showinfo("完成", "转换已完成！"))

if __name__ == "__main__":
    root = tk.Tk()
    app = AddressTransferApp(root)
    root.mainloop()