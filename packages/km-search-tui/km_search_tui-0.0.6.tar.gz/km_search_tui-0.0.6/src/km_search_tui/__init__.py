#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
空明码查询 TUI 应用
使用 textual 库开发的文本用户界面，可以查询编码和中文的对应关系
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, DataTable, Header, Footer, Label, TabbedContent, TabPane, Button
from textual.binding import Binding
from textual import on
from textual import events
import re
from pathlib import Path
from typing import Dict, List, Tuple
import time
import duckdb
import os
from datetime import datetime


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
    /* 输入容器样式 */
    #input_container {
        margin: 1;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    /* 输入标签样式 */
    #input_label {
        width: 18;
        height: 3;
        text-align: right;
        margin-right: 2;
        padding: 0 1;
        content-align: right middle;
        border: solid $accent;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    /* 搜索输入框样式 */
    #search_input {
        height: 3;
        border-left: solid $accent;
        border-top: solid $accent;
        border-bottom: solid $accent;
        border-right: none;
        background: $surface;
    }

    #search_input:focus {
        border-left: solid $accent;
        border-top: solid $accent;
        border-bottom: solid $accent;
        border-right: none;
        background: $surface-lighten-1;
    }

    /* 结果表格样式 */
    #result_table {
        margin: 1;
        background: $surface;
    }

    #result_table > .datatable--header {
        background: $primary;
        color: $text;
        text-style: bold;
        border-bottom: solid $accent;
    }

    #result_table > .datatable--odd-row {
        background: $surface;
    }

    #result_table > .datatable--even-row {
        background: $surface-lighten-1;
    }

    #result_table > .datatable--cursor {
        background: $accent;
        color: $text;
    }

    /* 历史表格样式 */
    #history_container {
        height: 85%;
    }

    #history_table {
        margin: 0;
        height: 85%;
        background: $surface;
    }

    #history_table > .datatable--header {
        background: $primary;
        color: $text;
        text-style: bold;
        border-bottom: solid $accent;
    }

    #history_table > .datatable--odd-row {
        background: $surface;
    }

    #history_table > .datatable--even-row {
        background: $surface-lighten-1;
    }

    #history_table > .datatable--cursor {
        background: $accent;
        color: $text;
    }

    /* 状态标签样式 */
    #status_label {
        margin: 1;
        padding: 1;
        background: $surface;
        color: $text;
        text-align: center;
        border-top: solid $primary;
    }

    #history_status_label {
        margin: 1;
        padding: 0 1;
        background: $surface;
        color: $text;
        text-align: center;
        border-top: solid $primary;
        border-left: solid $accent;
        border-right: solid $accent;
        border-bottom: solid $accent;
    }

    #export_button {
        margin: 1;
        padding: 0 1;
        background: $surface;
        color: $text;
        text-align: center;
        border-top: solid $primary;
        border-left: solid $accent;
        border-right: solid $accent;
        border-bottom: solid $accent;
    }


    /* 状态容器样式 */
    #status_container {
        height: 15%;
    }

    /* 标签页容器样式 */
    TabbedContent {
        height: 100%;
        background: $background;
    }

    TabPane {
        padding: 0;
        background: $background;
    }

    TabbedContent > .tabs {
        background: $panel;
        border-bottom: solid $primary;
    }

    TabbedContent > .tabs > .tab--active {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    TabbedContent > .tabs > .tab {
        background: $surface;
        color: $text-secondary;
    }

    TabbedContent > .tabs > .tab:hover {
        background: $surface-lighten-1;
        color: $text;
    }

    /* 按钮和提示信息样式 */
    .help-text {
        color: $text-secondary;
        text-style: italic;
    }

    /* 垂直滚动条样式 */
    .vertical-scroll {
        background: $surface;
    }

    /* 水平滚动条样式 */
    .horizontal-scroll {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "退出", priority=True),
        Binding("ctrl+c", "quit", "退出"),
        Binding("f1", "focus_tab('search')", "查询页"),
        Binding("f2", "focus_tab('history')", "历史页"),
        Binding("e", "export_history", "导出历史"),
    ]

    def __init__(self, dict_file: str):
        super().__init__()
        self.dict_file = dict_file
        self.code_dict = CodeDict(dict_file)
        self.current_results: List[Tuple[str, str]] = []

        # 初始化查询历史数据库
        self.init_history_db()

    def init_history_db(self) -> None:
        """初始化查询历史数据库"""
        # 获取用户数据目录
        if os.name == 'nt':  # Windows
            data_dir = os.environ.get('APPDATA', '')
            data_dir = os.path.join(data_dir, 'km-search-tui')
        else:  # Unix-like
            data_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'km-search-tui')

        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 数据库文件路径
        self.history_db_path = os.path.join(data_dir, 'search_history.duckdb')

        # 初始化数据库连接，确保使用读写模式
        self.history_conn = duckdb.connect(self.history_db_path, read_only=False)

        # 创建查询历史表（如果不存在）
        self.history_conn.sql("""
            CREATE TABLE IF NOT EXISTS search_history (
                query TEXT NOT NULL,
                query_type TEXT NOT NULL,
                search_count INTEGER DEFAULT 1,
                last_search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_codes TEXT,  -- 存储查询结果中的编码，JSON格式
                PRIMARY KEY (query, query_type)
            )
        """)

        # 创建索引以提高查询性能
        try:
            self.history_conn.sql("CREATE INDEX IF NOT EXISTS idx_search_count ON search_history(search_count DESC)")
        except:
            pass  # 索引可能已存在

    def record_search_history(self, query: str, query_type: str, results: List[Tuple[str, str]] = None) -> None:
        """记录查询历史"""
        import json

        try:
            # 将查询结果转换为JSON字符串，只取编码部分
            result_codes = None
            if results:
                # 提取所有编码，去重并限制数量（避免存储太多）
                codes = list(set([code for code, chinese in results[:10]]))
                result_codes = json.dumps(codes, ensure_ascii=False)

            # 检查记录是否已存在
            exists_result = self.history_conn.sql("""
                SELECT COUNT(*) FROM search_history
                WHERE query = ? AND query_type = ?
            """, params=[query, query_type])

            exists = exists_result.fetchone()[0] > 0

            if exists:
                # 记录存在，更新计数、时间和编码结果
                self.history_conn.sql("""
                    UPDATE search_history
                    SET search_count = search_count + 1,
                        last_search_time = CURRENT_TIMESTAMP,
                        result_codes = ?
                    WHERE query = ? AND query_type = ?
                """, params=[result_codes, query, query_type])
            else:
                # 记录不存在，插入新记录
                self.history_conn.sql("""
                    INSERT INTO search_history (query, query_type, search_count, last_search_time, result_codes)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP, ?)
                """, params=[query, query_type, result_codes])

        except Exception as e:
            # 记录错误但不中断主流程
            print(f"记录查询历史失败: {e}")

    def load_search_history(self) -> None:
        """加载并显示查询历史（分页）"""
        import json

        try:
            # 获取当前页码和每页记录数
            current_page = getattr(self, '_current_history_page', 1)
            page_size = 30

            # 查询总记录数
            count_result = self.history_conn.sql("SELECT COUNT(*) FROM search_history")
            total_records = count_result.fetchone()[0]
            total_pages = (total_records + page_size - 1) // page_size

            # 计算偏移量
            offset = (current_page - 1) * page_size

            # 查询当前页的历史记录
            result = self.history_conn.sql(f"""
                SELECT query, query_type, search_count, result_codes,
                       strftime(last_search_time, '%Y-%m-%d %H:%M:%S') as formatted_time
                FROM search_history
                ORDER BY search_count DESC, last_search_time DESC
                LIMIT {page_size} OFFSET {offset}
            """)

            # 更新历史记录表格
            history_table = self.query_one("#history_table", DataTable)
            history_table.clear()

            # 将结果转换为列表遍历
            rows = result.fetchall()
            if rows:
                for row in rows:
                    query, query_type, count, result_codes, time = row

                    # 解析编码JSON数据
                    codes_str = ""
                    if result_codes:
                        try:
                            codes = json.loads(result_codes)
                            codes_str = " | ".join(codes[:5])  # 使用 | 分隔，只显示前5个编码
                            if len(codes) > 5:
                                codes_str += "..."
                        except:
                            codes_str = ""

                    history_table.add_row(query, codes_str, query_type, str(count), time)

                # 更新状态，显示分页信息
                start_record = offset + 1
                end_record = min(offset + page_size, total_records)
                if total_pages > 1:
                    history_status = self.query_one("#history_status_label", Label)
                    history_status.update(f"查询历史 {start_record}-{end_record}/{total_records} (第{current_page}/{total_pages}页) | F1 切换到查询页 | Backspace 删除记录 | ← → 翻页")
                else:
                    history_status = self.query_one("#history_status_label", Label)
                    history_status.update(f"查询历史 (共{total_records}条) | F1 切换到查询页 | Backspace 删除记录 | ← → 翻页")
            else:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("暂无查询历史 | F1 切换到查询页 | Backspace 删除记录 | ← → 翻页")
        except Exception as e:
            history_status = self.query_one("#history_status_label", Label)
            history_status.update(f"加载查询历史失败: {e}")

    def on_key(self, event) -> None:
        """处理键盘输入"""
        # 处理删除键（Backspace和Delete）
        if event.key == "backspace" or event.key == "delete":
            # 调用删除功能
            self.delete_record_direct()
            return

        # 处理翻页键（左右方向键）
        if event.key == "left":
            # 上一页
            try:
                current_page = getattr(self, '_current_history_page', 1)
                if current_page > 1:
                    self._current_history_page = current_page - 1
                    self.load_search_history()
                    # 聚焦到历史表格
                    history_table = self.query_one("#history_table", DataTable)
                    self.set_focus(history_table)
            except Exception as e:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update(f"翻页失败: {e} | ← → 翻页")
            return

        if event.key == "right":
            # 下一页
            try:
                current_page = getattr(self, '_current_history_page', 1)
                # 查询总页数
                count_result = self.history_conn.sql("SELECT COUNT(*) FROM search_history")
                total_records = count_result.fetchone()[0]
                total_pages = (total_records + 29) // 30  # 每页30条（因为前面已修改为30）

                if current_page < total_pages:
                    self._current_history_page = current_page + 1
                    self.load_search_history()
                    # 聚焦到历史表格
                    history_table = self.query_one("#history_table", DataTable)
                    self.set_focus(history_table)
            except Exception as e:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update(f"翻页失败: {e} | ← → 翻页")
            return

        # 处理确认删除的按键
        if hasattr(self, '_pending_deletion') and self._pending_deletion:
            if event.key == 'y' or event.key == 'Y':
                # 确认删除
                try:
                    query = self._pending_deletion['query']
                    query_type = self._pending_deletion['query_type']

                    # 从数据库中删除记录
                    self.history_conn.sql("""
                        DELETE FROM search_history
                        WHERE query = ? AND query_type = ?
                    """, params=[query, query_type])

                    # 重新加载历史表格以反映删除
                    self.load_search_history()

                    # 清除待删除记录
                    delattr(self, '_pending_deletion')

                    # 更新状态
                    history_status = self.query_one("#history_status_label", Label)
                    history_status.update(f"已删除记录 | F2 查看历史 | Backspace 删除记录 | ← → 翻页")

                except Exception as e:
                    history_status = self.query_one("#history_status_label", Label)
                    history_status.update(f"删除记录失败: {e} | ← → 翻页")

            elif event.key == 'n' or event.key == 'N':
                # 取消删除
                if hasattr(self, '_pending_deletion'):
                    delattr(self, '_pending_deletion')
                history_status = self.query_one("#history_status_label", Label)
                history_status.update(f"已取消删除 | F2 查看历史 | Backspace 删除记录 | ← → 翻页")

    def delete_record_direct(self) -> None:
        """直接触发删除选中的历史记录（不通过binding）"""
        try:
            # 检查当前是否在历史标签页
            tabbed_content = self.query_one(TabbedContent)
            if tabbed_content.active != "history_tab":
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("请先切换到历史页 | F2 切换到历史页 | ← → 翻页")
                return

            # 获取历史记录表格
            history_table = self.query_one("#history_table", DataTable)

            # 检查是否有选中的行
            cursor_row = history_table.cursor_row
            if cursor_row is None:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("请先选中要删除的记录 | Backspace 删除记录 | F2 查看历史 | ← → 翻页")
                return

            # 获取选中行的数据
            row_data = history_table.get_row_at(cursor_row)
            if not row_data:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("无法获取选中记录的数据")
                return

            # 提取查询词和查询类型
            query = row_data[0]  # 查询词
            query_type = row_data[2]  # 类型

            # 保存要删除的记录信息
            self._pending_deletion = {
                'query': query,
                'query_type': query_type
            }

            # 显示确认提示
            history_status = self.query_one("#history_status_label", Label)
            history_status.update(f"确认删除: '{query}' ({query_type})? 按 Y 确认删除，按 N 取消 | ← → 翻页")

        except Exception as e:
            history_status = self.query_one("#history_status_label", Label)
            history_status.update(f"删除记录失败: {e}")

  
    def compose(self) -> ComposeResult:
        """创建界面组件"""
        yield Header(show_clock=True)

        with TabbedContent():
            with TabPane("查询", id="search_tab"):
                with Container(id="input_container"):
                    with Vertical():
                        with Horizontal():
                            yield Label("输入编码/中文:", id="input_label")
                            yield Input(
                                placeholder="输入编码（如：9W）或中文（如：物质）进行搜索...",
                                id="search_input"
                            )
                        yield DataTable(id="result_table")
                        yield Label("就绪 | F1 切换到查询页 | F2 切换到历史页", id="status_label")
            with TabPane("查询历史", id="history_tab"):
                with Container():
                    with Vertical():
                        yield DataTable(id="history_table")
                        with Horizontal():
                            yield Label("F1 切换到查询页 | Backspace 删除记录 ", id="history_status_label")
                            yield Button("导出所有字词", id="export_button")

        yield Footer()

    def on_mount(self) -> None:
        """应用启动时执行"""
        self.title = "空明码查询工具"
        self.theme = "dracula"

        # 设置查询结果表格列
        search_table = self.query_one("#result_table", DataTable)
        search_table.add_columns("编码", "中文")
        search_table.cursor_type = "row"

        # 设置历史记录表格列
        history_table = self.query_one("#history_table", DataTable)
        history_table.add_columns("查询词", "编码", "类型", "查询次数", "最后查询时间")
        history_table.cursor_type = "row"

        # 初始加载历史记录
        self.load_search_history()

        # 加载词库
        status = self.query_one("#status_label", Label)
        status.update("正在加载词库，请稍候...")

        # 加载词库
        self.set_timer(0.1, self.load_dictionary)

    def load_dictionary(self) -> None:
        """加载词库"""
        try:
            count, load_time = self.code_dict.load()
            status = self.query_one("#status_label", Label)
            status.update(f"词库加载完成！共 {count:,} 条记录，耗时 {load_time:.2f} 秒 | F2 查看历史 | Backspace 删除记录 | ← → 翻页")

            # 词库加载完成后，聚焦到搜索输入框
            search_input = self.query_one("#search_input", Input)
            search_input.focus()

            # 打开 Command Palette
            self.set_timer(0.2, self._open_command_palette)

        except Exception as e:
            status = self.query_one("#status_label", Label)
            status.update(f"错误: {e}")

    def _open_command_palette(self) -> None:
        """打开 Command Palette"""
        try:
            # 使用 Textual 的 action_command_palette 方法
            self.action_command_palette()

            # 延迟一点时间确保 Command Palette 打开，然后模拟 Enter 按键
            self.set_timer(0.1, self._press_enter_in_palette)
        except Exception as e:
            print(f"打开 Command Palette 失败: {e}")

    def _press_enter_in_palette(self) -> None:
        """在 Command Palette 中按下 Enter 键"""
        try:
            # 参考示例代码创建按键事件
            enter_event = events.Key(self, "enter", char="\n")
            self.post_message(enter_event)

        except Exception as e:
            print(f"模拟 Enter 按键失败: {e}")

    @on(Input.Submitted, "#search_input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交"""
        query = event.value.strip()
        if not query:
            return

        # 判断输入是编码还是中文
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', query))
        search_type = "中文" if is_chinese else "编码"

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
        else:
            status.update(f"正在搜索编码: {query}...")
            results = self.code_dict.search_by_code(query)

        self.current_results = results

        # 记录查询历史
        self.record_search_history(query, search_type, results)

        # 显示结果
        if results:
            for index, (code, chinese) in enumerate(results):
                # 使用索引确保每行都有唯一的 key
                table.add_row(code, chinese, key=f"{code}_{index}")
            status.update(f"找到 {len(results)} 条结果（搜索{search_type}: {query}）| 按 ↑↓ 浏览 | F2 查看历史")
        else:
            status.update(f"未找到结果（搜索{search_type}: {query}）| F2 查看历史")

        # 重新聚焦到输入框，以便继续输入
        search_input = self.query_one("#search_input", Input)
        search_input.focus()

    @on(Input.Changed, "#search_input")
    def on_input_changed(self, event: Input.Changed) -> None:
        """输入内容改变时实时搜索（可选，如果文件很大可能会慢）"""
        # 可以在这里实现实时搜索，但为了性能，我们只在提交时搜索
        pass

    @on(Button.Pressed, "#export_button")
    def on_export_button_pressed(self, event: Button.Pressed) -> None:
        """处理导出按钮点击事件"""
        self.action_export_history()

    def action_quit(self) -> None:
        """退出应用"""
        # 关闭数据库连接
        if hasattr(self, 'history_conn'):
            self.history_conn.close()
        self.exit()

    def action_focus_tab(self, tab_name: str) -> None:
        """切换到指定标签页"""
        tabbed_content = self.query_one(TabbedContent)
        if tab_name == "search":
            tabbed_content.active = "search_tab"
            # 聚焦到搜索输入框
            search_input = self.query_one("#search_input", Input)
            search_input.focus()
        elif tab_name == "history":
            tabbed_content.active = "history_tab"
            # 加载历史记录
            self.load_search_history()
            # 聚焦到历史表格
            history_table = self.query_one("#history_table", DataTable)
            # 使用set_focus方法聚焦到表格
            self.set_focus(history_table)

    def action_export_history(self) -> None:
        """导出DuckDB数据库中所有字词到txt文件"""
        try:
            # 检查是否在历史标签页
            tabbed_content = self.query_one(TabbedContent)
            if tabbed_content.active != "history_tab":
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("请先切换到历史页进行导出 | F2 切换到历史页 | ← → 翻页")
                return

            # 查询数据库中的所有唯一查询词
            result = self.history_conn.sql("""
                SELECT DISTINCT query
                FROM search_history
                ORDER BY query COLLATE NOCASE
            """)

            # 收集所有查询词
            all_queries = set()
            for row in result.fetchall():
                query = row[0]
                if query:
                    all_queries.add(query)

            if not all_queries:
                history_status = self.query_one("#history_status_label", Label)
                history_status.update("数据库中没有可导出的字词 | ← → 翻页")
                return

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"km_search_all_words_{timestamp}.txt"

            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                # 使用中文逗号作为分隔符
                f.write("，".join(sorted(all_queries)))

            history_status = self.query_one("#history_status_label", Label)
            history_status.update(f"数据库中所有字词已导出到: {filename}")

        except Exception as e:
            history_status = self.query_one("#history_status_label", Label)
            history_status.update(f"导出失败: {e}")


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
