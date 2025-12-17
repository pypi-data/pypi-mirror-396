#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
空明码查询 TUI 应用
使用 textual 库开发的文本用户界面，可以查询编码和中文的对应关系
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, DataTable, Header, Footer, Label
from textual.binding import Binding
from textual import on
import re
from pathlib import Path
from typing import Dict, List, Tuple
import time


class CodeDict:
    """编码字典类，用于加载和查询词库"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.code_to_chinese: Dict[str, List[str]] = {}  # 编码 -> 中文列表
        self.chinese_to_codes: Dict[str, List[str]] = {}  # 中文 -> 编码列表
        self.loaded = False
        
    def load(self) -> Tuple[int, float]:
        """加载词库文件"""
        start_time = time.time()
        count = 0
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n\r')
                    if not line:
                        continue
                    
                    # 分割编码和中文部分
                    parts = line.split(' ', 1)
                    if len(parts) < 2:
                        continue
                    
                    code = parts[0]
                    chinese = parts[1]
                    
                    # 存储编码 -> 中文
                    if code not in self.code_to_chinese:
                        self.code_to_chinese[code] = []
                    self.code_to_chinese[code].append(chinese)
                    
                    # 存储中文 -> 编码（每个中文字词都建立索引）
                    chinese_words = chinese.split()
                    for word in chinese_words:
                        if word not in self.chinese_to_codes:
                            self.chinese_to_codes[word] = []
                        if code not in self.chinese_to_codes[word]:
                            self.chinese_to_codes[word].append(code)
                    
                    count += 1
                    
            self.loaded = True
            load_time = time.time() - start_time
            return count, load_time
        except Exception as e:
            raise Exception(f"加载词库失败: {e}")
    
    def search_by_code(self, code: str) -> List[Tuple[str, str]]:
        """根据编码搜索（精确匹配）"""
        if not code:
            return []
        
        results = []
        
        # 精确匹配
        if code in self.code_to_chinese:
            for chinese in self.code_to_chinese[code]:
                results.append((code, chinese))
        
        return results
    
    def search_by_chinese(self, chinese: str) -> List[Tuple[str, str]]:
        """根据中文搜索（精确匹配）"""
        if not chinese:
            return []
        
        results = []
        found_codes = set()
        
        # 精确匹配
        if chinese in self.chinese_to_codes:
            for code in self.chinese_to_codes[chinese]:
                if code not in found_codes:
                    found_codes.add(code)
                    if code in self.code_to_chinese:
                        for chinese_text in self.code_to_chinese[code]:
                            results.append((code, chinese_text))
        
        return results


class KMSearchApp(App):
    """空明码查询应用主类"""
    
    CSS = """
    Screen {
        background: #282a36;
    }
    
    #input_container {
        margin: 1;
        padding: 1;
        border: solid #bd93f9;
    }
    
    #input_label {
        width: 18;
        height: 3;
        text-align: right;
        margin-right: 2;
        padding: 0 1;
        content-align: right middle;
        color: #bd93f9;
        text-style: bold;
        border: solid #ff79c6;
        background: #44475a;
    }
    
    #search_input {
        height: 3;
        background: #44475a;
        color: #f8f8f2;
        border: solid #8be9fd;
    }
    
    #search_input:focus {
        border: solid #50fa7b;
    }
    
    #result_table {
        margin: 1;
        border: solid #bd93f9;
        background: #282a36;
    }
    
    #result_table > .datatable--cursor {
        background: #44475a;
    }
    
    #result_table > .datatable--header {
        background: #44475a;
        color: #bd93f9;
        text-style: bold;
    }
    
    #status_label {
        margin: 1;
        padding: 1;
        background: #44475a;
        color: #f8f8f2;
        border: solid #6272a4;
    }
    
    Header {
        background: #44475a;
        color: #bd93f9;
        text-style: bold;
    }
    
    Footer {
        background: #44475a;
        color: #8be9fd;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出", priority=True),
        Binding("ctrl+c", "quit", "退出"),
        Binding("f1", "help", "帮助"),
    ]
    
    def __init__(self, dict_file: str):
        super().__init__()
        self.dict_file = dict_file
        self.code_dict = CodeDict(dict_file)
        self.current_results: List[Tuple[str, str]] = []
    
    def compose(self) -> ComposeResult:
        """创建界面组件"""
        yield Header(show_clock=True)
        
        with Container(id="input_container"):
            with Horizontal():
                yield Label("输入编码/中文:", id="input_label")
                yield Input(
                    placeholder="输入编码（如：9W）或中文（如：物质）进行搜索...",
                    id="search_input"
                )
        
        yield DataTable(id="result_table")
        
        yield Label("就绪 | 按 F1 查看帮助 | 按 Q 退出", id="status_label")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """应用启动时执行"""
        self.title = "空明码查询工具"
        
        # 设置表格列
        table = self.query_one("#result_table", DataTable)
        table.add_columns("编码", "中文")
        table.cursor_type = "row"
        
        # 加载词库
        status = self.query_one("#status_label", Label)
        status.update("正在加载词库，请稍候...")
        self.set_timer(0.1, self.load_dictionary)
    
    def load_dictionary(self) -> None:
        """加载词库"""
        try:
            count, load_time = self.code_dict.load()
            status = self.query_one("#status_label", Label)
            status.update(f"词库加载完成！共 {count:,} 条记录，耗时 {load_time:.2f} 秒 | 按 F1 查看帮助 | 按 Q 退出")
        except Exception as e:
            status = self.query_one("#status_label", Label)
            status.update(f"错误: {e}")
    
    @on(Input.Submitted, "#search_input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交"""
        query = event.value.strip()
        if not query:
            return
        
        # 判断输入是编码还是中文
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', query))
        
        status = self.query_one("#status_label", Label)
        table = self.query_one("#result_table", DataTable)
        
        if not self.code_dict.loaded:
            status.update("词库尚未加载完成，请稍候...")
            return
        
        # 清空表格
        table.clear()
        
        # 搜索
        if is_chinese:
            status.update(f"正在搜索中文: {query}...")
            results = self.code_dict.search_by_chinese(query)
            search_type = "中文"
        else:
            status.update(f"正在搜索编码: {query}...")
            results = self.code_dict.search_by_code(query)
            search_type = "编码"
        
        self.current_results = results
        
        # 显示结果
        if results:
            for index, (code, chinese) in enumerate(results):
                # 使用索引确保每行都有唯一的 key
                table.add_row(code, chinese, key=f"{code}_{index}")
            status.update(f"找到 {len(results)} 条结果（搜索{search_type}: {query}）| 按 ↑↓ 浏览 | 按 Q 退出")
        else:
            status.update(f"未找到结果（搜索{search_type}: {query}）| 按 Q 退出")
        
        # 重新聚焦到输入框，以便继续输入
        search_input = self.query_one("#search_input", Input)
        search_input.focus()
    
    @on(Input.Changed, "#search_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        """输入内容改变时实时搜索（可选，如果文件很大可能会慢）"""
        # 可以在这里实现实时搜索，但为了性能，我们只在提交时搜索
        pass
    
    def action_quit(self) -> None:
        """退出应用"""
        self.exit()
    
    def action_help(self) -> None:
        """显示帮助"""
        status = self.query_one("#status_label", Label)
        status.update("帮助: 输入编码（如 9W）查找中文，输入中文（如 物质）查找编码 | 按 Q 退出")


def main():
    """主函数"""
    import sys
    import os
    
    # 获取词库文件路径
    # 如果是 PyInstaller 打包后的程序，从临时目录读取
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_path = sys._MEIPASS
        dict_file = os.path.join(base_path, 'MasterDit.shp')
    else:
        # 开发环境，从当前目录读取
        dict_file = "MasterDit.shp"
    
    # 如果临时目录没有，尝试从可执行文件所在目录读取
    if not Path(dict_file).exists():
        if getattr(sys, 'frozen', False):
            # 尝试从可执行文件所在目录读取
            exe_dir = os.path.dirname(sys.executable)
            dict_file = os.path.join(exe_dir, 'MasterDit.shp')
        else:
            dict_file = "MasterDit.shp"
    
    if not Path(dict_file).exists():
        print(f"错误: 找不到词库文件 MasterDit.shp")
        if getattr(sys, 'frozen', False):
            print(f"搜索路径: {sys._MEIPASS}")
            print(f"可执行文件目录: {os.path.dirname(sys.executable)}")
        else:
            print("请确保 MasterDit.shp 文件在当前目录")
        sys.exit(1)
    
    # 运行应用
    app = KMSearchApp(dict_file)
    app.run()


if __name__ == "__main__":
    main()

