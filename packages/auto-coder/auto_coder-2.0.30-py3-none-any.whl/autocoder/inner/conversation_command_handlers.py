import os
import json
import uuid
from typing import Optional, Union, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime

from autocoder.common.international import get_message, get_message_with_format
from autocoder.common.ac_style_command_parser import create_config, parse_typed_query
from autocoder.common.v2.agent.agentic_edit_types import AgenticEditConversationConfig
from autocoder.common.conversations.get_conversation_manager import (
    get_conversation_manager,
)
from loguru import logger as global_logger
from autocoder.common.save_formatted_log import save_formatted_log


class ConversationNewCommandHandler:
    """处理 new 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _create_config(self):
        """创建 new 命令的类型化配置"""
        if self._config is None:
            self._config = (
                create_config()
                .collect_remainder("query")
                .command("new")
                .max_args(0)
                .command("name")
                .positional("value", required=True)
                .max_args(1)
                .build()
            )
        return self._config

    def handle_new_command(
        self, query: str, conversation_config: AgenticEditConversationConfig
    ) -> Optional[Union[str, None]]:
        """
        处理 new 指令的主入口

        Args:
            query: 查询字符串，例如 "/new /name my-conversation create new task"
            conversation_config: 对话配置对象

        Returns:
            None: 表示处理了 new 指令，应该返回而不继续执行
            其他值: 表示没有处理 new 指令，应该继续执行
        """
        # 解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 new 命令
        if not result.has_command("new"):
            return "continue"  # 不是 new 指令，继续执行

        # 设置对话动作
        conversation_config.action = "new"

        # 处理名称参数
        conversation_name = "New Conversation"  # 默认名称
        if result.has_command("name"):
            conversation_name = result.name

        # 处理查询内容
        task_query = result.query.strip() if result.query else ""

        # 创建新对话
        conversation_manager = get_conversation_manager()
        conversation_id = conversation_manager.create_conversation(
            name=conversation_name, description=conversation_name
        )
        conversation_manager.set_current_conversation(conversation_id)
        conversation_config.conversation_id = conversation_id
        conversation_config.query = task_query

        global_logger.info(
            f"Created new conversation: {conversation_name} (ID: {conversation_id})"
        )

        if task_query:
            return "continue"

        return None  # 处理完成


class ConversationExportCommandHandler:
    """处理 export 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _create_config(self):
        """创建 export 命令的类型化配置"""
        if self._config is None:
            self._config = (
                create_config()
                .command("export")
                .positional("conversation_id_or_name", required=False)
                .positional("file_path", required=False)
                .max_args(2)
                .build()
            )
        return self._config

    def _find_conversation_by_name_or_id(self, name_or_id: str) -> Optional[str]:
        """
        通过名字或ID查找对话

        Args:
            name_or_id: 对话名字或ID

        Returns:
            Optional[str]: 对话ID，如果找不到或有重复返回None
        """
        conversation_manager = get_conversation_manager()

        # 先尝试作为ID查找
        try:
            conversations = conversation_manager.list_conversations()
            for conv in conversations:
                if conv.get("conversation_id") == name_or_id:
                    return name_or_id
        except:
            pass

        # 作为名字查找
        conversations = conversation_manager.list_conversations()
        matched_conversations = [
            conv for conv in conversations if conv.get("name") == name_or_id
        ]

        if len(matched_conversations) == 0:
            return None
        elif len(matched_conversations) == 1:
            return matched_conversations[0].get("conversation_id")
        else:
            # 找到多个匹配，名字重复
            self.console.print(
                Panel(
                    get_message_with_format(
                        "conversation_duplicate_name",
                        name=name_or_id,
                        count=len(matched_conversations),
                    ),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            # 显示所有匹配的对话
            table = Table(
                title=get_message_with_format(
                    "conversation_duplicate_list", name=name_or_id
                )
            )
            table.add_column(
                get_message("conversation_table_id"), style="cyan", no_wrap=True
            )
            table.add_column(get_message("conversation_table_name"), style="green")

            for conv in matched_conversations:
                table.add_row(
                    conv.get("conversation_id") or "-", conv.get("name") or "-"
                )

            self.console.print(table)
            self.console.print(
                Panel(
                    get_message("conversation_use_id_instead"),
                    border_style="yellow",
                )
            )
            return None

    def _export_conversation_to_markdown(
        self, conversation_id: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        将对话导出为 Markdown 文件

        Args:
            conversation_id: 对话ID
            output_path: 输出文件路径，如果为None则使用默认路径

        Returns:
            Optional[str]: 导出文件的路径，如果失败返回None
        """
        try:
            # 获取对话管理器
            conversation_manager = get_conversation_manager()

            # 获取对话内容
            conversation_data = conversation_manager.get_conversation(conversation_id)
            if not conversation_data:
                self.console.print(
                    Panel(
                        get_message_with_format(
                            "conversation_not_found", conversation_id=conversation_id
                        ),
                        title=get_message("conversation_error"),
                        border_style="red",
                    )
                )
                return None

            # 获取对话消息
            messages = conversation_data.get("messages", [])
            if not messages:
                self.console.print(
                    Panel(
                        get_message("conversation_export_no_messages"),
                        title=get_message("conversation_export_title"),
                        border_style="yellow",
                    )
                )
                return None

            # 将对话数据转换为JSON格式
            conversation_json = json.dumps(messages, ensure_ascii=False, indent=2)

            # 确定输出路径
            if output_path is None:
                # 使用当前目录
                project_root = os.getcwd()
                # 生成文件名
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"{now}_{unique_id}_conversation_{conversation_id[:8]}.md"
                output_path = os.path.join(project_root, filename)
            else:
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

            # 使用 save_formatted_log 函数保存为markdown
            filepath = save_formatted_log(
                project_root=os.path.dirname(output_path) if output_path else ".",
                json_text=conversation_json,
                suffix=f"conversation_{conversation_id[:8]}",
                conversation_id=conversation_id,
                log_subdir="",  # 不使用子目录，直接保存到指定目录
            )

            if filepath:
                self.console.print(
                    Panel(
                        get_message_with_format(
                            "conversation_export_success",
                            conversation_id=conversation_id,
                            filepath=filepath,
                        ),
                        title=get_message("conversation_export_title"),
                        border_style="green",
                    )
                )
                global_logger.info(f"Conversation exported to: {filepath}")
                return filepath
            else:
                self.console.print(
                    Panel(
                        get_message("conversation_export_failed"),
                        title=get_message("conversation_export_title"),
                        border_style="red",
                    )
                )
                return None

        except Exception as e:
            self.console.print(
                Panel(
                    get_message_with_format("conversation_export_error", error=str(e)),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            global_logger.error(f"Export conversation failed: {str(e)}")
            return None

    def handle_export_command(
        self, query: str, conversation_config: AgenticEditConversationConfig
    ) -> Optional[Union[str, None]]:
        """
        处理 export 指令的主入口

        Args:
            query: 查询字符串，例如 "/export" 或 "/export conv-123" 或 "/export conv-123 /path/to/file.md"
            conversation_config: 对话配置对象

        Returns:
            None: 表示处理了 export 指令，应该返回而不继续执行
            其他值: 表示没有处理 export 指令，应该继续执行
        """
        # 解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 export 命令
        if not result.has_command("export"):
            return "continue"  # 不是 export 指令，继续执行

        # 获取要导出的对话ID或名称和文件路径
        export_cmd = result.get_command("export")
        conversation_id_or_name = None
        file_path = None

        # 处理位置参数
        if export_cmd and export_cmd.args:
            # 第一个参数：对话ID或名称
            if len(export_cmd.args) >= 1:
                conversation_id_or_name = export_cmd.args[0]
            # 第二个参数：文件路径
            if len(export_cmd.args) >= 2:
                file_path = export_cmd.args[1]

        # 确定要导出的对话ID
        conversation_id = None
        if conversation_id_or_name:
            # 通过名字或ID查找对话
            conversation_id = self._find_conversation_by_name_or_id(
                conversation_id_or_name
            )
            if conversation_id is None:
                # 没有找到对话（或名字重复，已经在 _find_conversation_by_name_or_id 中显示错误）
                if not any(
                    conv.get("name") == conversation_id_or_name
                    for conv in get_conversation_manager().list_conversations()
                ):
                    # 只有在不是名字重复的情况下才显示"未找到"错误
                    self.console.print(
                        Panel(
                            get_message_with_format(
                                "conversation_not_found_by_name_or_id",
                                name_or_id=conversation_id_or_name,
                            ),
                            title=get_message("conversation_error"),
                            border_style="red",
                        )
                    )
                return None
        else:
            # 没有指定对话ID，使用当前对话
            conversation_manager = get_conversation_manager()
            conversation_id = conversation_manager.get_current_conversation_id()
            if not conversation_id:
                self.console.print(
                    Panel(
                        get_message("conversation_export_no_current"),
                        title=get_message("conversation_error"),
                        border_style="red",
                    )
                )
                return None

        # 执行导出
        self._export_conversation_to_markdown(conversation_id, file_path)

        return None  # 处理完成


class ConversationResumeCommandHandler:
    """处理 resume 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _create_config(self):
        """创建 resume 命令的类型化配置"""
        if self._config is None:
            self._config = (
                create_config()
                .collect_remainder("query")
                .command("resume")
                .positional("conversation_id_or_name", required=True)
                .max_args(1)
                .build()
            )
        return self._config

    def _find_conversation_by_name_or_id(self, name_or_id: str) -> Optional[str]:
        """
        通过名字或ID查找对话

        Args:
            name_or_id: 对话名字或ID

        Returns:
            Optional[str]: 对话ID，如果找不到或有重复返回None
        """
        conversation_manager = get_conversation_manager()

        # 先尝试作为ID查找
        try:
            # 检查是否存在该ID的对话
            conversations = conversation_manager.list_conversations()
            for conv in conversations:
                if conv.get("conversation_id") == name_or_id:
                    return name_or_id
        except:
            pass

        # 作为名字查找
        conversations = conversation_manager.list_conversations()
        matched_conversations = [
            conv for conv in conversations if conv.get("name") == name_or_id
        ]

        if len(matched_conversations) == 0:
            # 没有找到
            return None
        elif len(matched_conversations) == 1:
            # 找到唯一匹配
            return matched_conversations[0].get("conversation_id")
        else:
            # 找到多个匹配，名字重复
            self.console.print(
                Panel(
                    get_message_with_format(
                        "conversation_duplicate_name",
                        name=name_or_id,
                        count=len(matched_conversations),
                    ),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            # 显示所有匹配的对话
            from rich.table import Table

            table = Table(
                title=get_message_with_format(
                    "conversation_duplicate_list", name=name_or_id
                )
            )
            table.add_column(
                get_message("conversation_table_id"), style="cyan", no_wrap=True
            )
            table.add_column(get_message("conversation_table_name"), style="green")

            for conv in matched_conversations:
                table.add_row(
                    conv.get("conversation_id") or "-", conv.get("name") or "-"
                )

            self.console.print(table)
            self.console.print(
                Panel(
                    get_message("conversation_use_id_instead"),
                    border_style="yellow",
                )
            )
            return None

    def handle_resume_command(
        self, query: str, conversation_config: AgenticEditConversationConfig
    ) -> Optional[Union[str, None]]:
        """
        处理 resume 指令的主入口

        Args:
            query: 查询字符串，例如 "/resume conv-123 continue with task" 或 "/resume my-conversation continue"
            conversation_config: 对话配置对象

        Returns:
            None: 表示处理了 resume 指令，应该返回而不继续执行
            其他值: 表示没有处理 resume 指令，应该继续执行
        """
        # 解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 resume 命令
        if not result.has_command("resume"):
            return "continue"  # 不是 resume 指令，继续执行

        # 设置对话动作
        conversation_config.action = "resume"

        # 获取对话ID或名字
        resume_cmd = result.get_command("resume")
        if not resume_cmd or not resume_cmd.args:
            self.console.print(
                Panel(
                    get_message("conversation_provide_id_or_name"),
                    title=get_message("conversation_param_error"),
                    border_style="red",
                )
            )
            return None

        name_or_id = resume_cmd.args[0]

        # 通过名字或ID查找对话
        conversation_id = self._find_conversation_by_name_or_id(name_or_id)

        if conversation_id is None:
            # 没有找到对话（或名字重复，已经在 _find_conversation_by_name_or_id 中显示错误）
            if not any(
                conv.get("name") == name_or_id
                for conv in get_conversation_manager().list_conversations()
            ):
                # 只有在不是名字重复的情况下才显示"未找到"错误
                self.console.print(
                    Panel(
                        get_message_with_format(
                            "conversation_not_found_by_name_or_id",
                            name_or_id=name_or_id,
                        ),
                        title=get_message("conversation_error"),
                        border_style="red",
                    )
                )
            return None

        conversation_config.conversation_id = conversation_id

        # 处理查询内容
        task_query = result.query.strip() if result.query else ""
        conversation_config.query = task_query

        # 验证对话是否存在并设置为当前对话
        conversation_manager = get_conversation_manager()
        try:
            conversation_manager.set_current_conversation(conversation_id)
            global_logger.info(
                f"Resumed conversation: {conversation_id} (from input: {name_or_id})"
            )
            # 设置完对话后，如果用户还添加了query，直接返回 continue,这样后续
            # 会基于指定的会话继续新的 query
            if task_query:
                return "continue"
        except Exception as e:
            self.console.print(
                Panel(
                    get_message_with_format(
                        "conversation_not_found", conversation_id=conversation_id
                    ),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            return None

        return None  # 处理完成


class ConversationRenameCommandHandler:
    """处理 rename 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _create_config(self):
        """创建 rename 命令的类型化配置"""
        if self._config is None:
            self._config = (
                create_config()
                .command("rename")
                .positional("conversation_id_or_name", required=False)
                .positional("new_name", required=True)
                .max_args(2)
                .build()
            )
        return self._config

    def _find_conversation_by_name_or_id(self, name_or_id: str) -> Optional[str]:
        """
        通过名字或ID查找对话

        Args:
            name_or_id: 对话名字或ID

        Returns:
            Optional[str]: 对话ID，如果找不到或有重复返回None
        """
        conversation_manager = get_conversation_manager()

        # 先尝试作为ID查找
        try:
            conversations = conversation_manager.list_conversations()
            for conv in conversations:
                if conv.get("conversation_id") == name_or_id:
                    return name_or_id
        except:
            pass

        # 作为名字查找
        conversations = conversation_manager.list_conversations()
        matched_conversations = [
            conv for conv in conversations if conv.get("name") == name_or_id
        ]

        if len(matched_conversations) == 0:
            return None
        elif len(matched_conversations) == 1:
            return matched_conversations[0].get("conversation_id")
        else:
            # 找到多个匹配，名字重复
            self.console.print(
                Panel(
                    get_message_with_format(
                        "conversation_duplicate_name",
                        name=name_or_id,
                        count=len(matched_conversations),
                    ),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            # 显示所有匹配的对话
            table = Table(
                title=get_message_with_format(
                    "conversation_duplicate_list", name=name_or_id
                )
            )
            table.add_column(
                get_message("conversation_table_id"), style="cyan", no_wrap=True
            )
            table.add_column(get_message("conversation_table_name"), style="green")

            for conv in matched_conversations:
                table.add_row(
                    conv.get("conversation_id") or "-", conv.get("name") or "-"
                )

            self.console.print(table)
            self.console.print(
                Panel(
                    get_message("conversation_use_id_instead"),
                    border_style="yellow",
                )
            )
            return None

    def handle_rename_command(
        self, query: str, conversation_config: AgenticEditConversationConfig
    ) -> Optional[Union[str, None]]:
        """
        处理 rename 指令的主入口

        Args:
            query: 查询字符串，例如 "/rename new-conversation-name" 或 "/rename conv-123 new-name"
            conversation_config: 对话配置对象

        Returns:
            None: 表示处理了 rename 指令，应该返回而不继续执行
            其他值: 表示没有处理 rename 指令，应该继续执行
        """
        # 解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 rename 命令
        if not result.has_command("rename"):
            return "continue"  # 不是 rename 指令，继续执行

        # 获取参数
        rename_cmd = result.get_command("rename")
        if not rename_cmd or not rename_cmd.args:
            self.console.print(
                Panel(
                    get_message("conversation_provide_new_name"),
                    title=get_message("conversation_param_error"),
                    border_style="red",
                )
            )
            return None

        # 获取对话管理器
        conversation_manager = get_conversation_manager()

        # 处理位置参数
        conversation_id_or_name = None
        new_name = None

        if len(rename_cmd.args) == 1:
            # 只有一个参数：修改当前会话的名称
            new_name = rename_cmd.args[0]
            conversation_id = conversation_manager.get_current_conversation_id()

            if not conversation_id:
                self.console.print(
                    Panel(
                        get_message("conversation_no_current"),
                        title=get_message("conversation_error"),
                        border_style="red",
                    )
                )
                return None

        elif len(rename_cmd.args) == 2:
            # 两个参数：第一个为会话ID/名称，第二个为新名称
            conversation_id_or_name = rename_cmd.args[0]
            new_name = rename_cmd.args[1]

            # 通过名字或ID查找对话
            conversation_id = self._find_conversation_by_name_or_id(
                conversation_id_or_name
            )
            if conversation_id is None:
                # 没有找到对话（或名字重复，已经在 _find_conversation_by_name_or_id 中显示错误）
                if not any(
                    conv.get("name") == conversation_id_or_name
                    for conv in get_conversation_manager().list_conversations()
                ):
                    # 只有在不是名字重复的情况下才显示"未找到"错误
                    self.console.print(
                        Panel(
                            get_message_with_format(
                                "conversation_not_found_by_name_or_id",
                                name_or_id=conversation_id_or_name,
                            ),
                            title=get_message("conversation_error"),
                            border_style="red",
                        )
                    )
                return None
        else:
            self.console.print(
                Panel(
                    get_message("conversation_provide_new_name"),
                    title=get_message("conversation_param_error"),
                    border_style="red",
                )
            )
            return None

        # 执行重命名
        try:
            success = conversation_manager.update_conversation(
                conversation_id, name=new_name
            )

            if success:
                self.console.print(
                    Panel(
                        get_message_with_format(
                            "conversation_rename_success",
                            old_id=conversation_id,
                            new_name=new_name,
                        ),
                        title=get_message("conversation_rename_title"),
                        border_style="green",
                    )
                )
                global_logger.info(
                    f"Renamed conversation {conversation_id} to '{new_name}'"
                )
            else:
                self.console.print(
                    Panel(
                        get_message("conversation_rename_failed"),
                        title=get_message("conversation_error"),
                        border_style="red",
                    )
                )

        except Exception as e:
            self.console.print(
                Panel(
                    get_message_with_format("conversation_rename_error", error=str(e)),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )

        return None  # 处理完成


class ConversationCommandCommandHandler:
    """处理 command 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _create_config(self):
        """创建 command 命令的类型化配置

        支持格式：
        1. /command /dryrun hello.md name="name"
        2. /command hello.md name="name" query="query"
        """
        if self._config is None:
            self._config = (
                create_config()
                .command("command")
                .positional("file_path", required=True)
                # command 命令不限制键值对参数，接受任意键值对
                .command("dryrun")
                .max_args(0)  # dryrun 是标志命令，不接受参数
                .build()
            )
        return self._config

    def _render_command_file_with_variables(self, parsed_command: Any) -> str:
        """
        使用 CommandManager 加载并渲染命令文件

        Args:
            parsed_command: 类型化解析后的 command 命令对象（ParsedCommand）

        Returns:
            str: 渲染后的文件内容

        Raises:
            ValueError: 当参数不足或文件不存在时
            Exception: 当渲染过程出现错误时
        """
        from autocoder.common.command_file_manager import CommandManager

        try:
            # 从类型化解析结果中获取文件路径（第一个位置参数）
            if not parsed_command.args:
                raise ValueError("未提供文件路径参数")

            file_path = parsed_command.args[0]  # file_path 位置参数

            # 获取关键字参数作为渲染参数
            kwargs = parsed_command.kwargs or {}
            args = parsed_command.args[1:] or []

            render_variables = {
                "kwargs":kwargs,
                "args":args,
                **kwargs,
            }

            # 初始化 CommandManager
            command_manager = CommandManager()

            # 使用 read_command_file_with_render 直接读取并渲染命令文件
            rendered_content = command_manager.read_command_file_with_render(
                file_path, render_variables
            )
            if rendered_content is None:
                raise ValueError(f"无法读取或渲染命令文件: {file_path}")

            global_logger.info(f"成功渲染命令文件: {file_path}, 使用参数: {render_variables}")
            return rendered_content

        except Exception as e:
            global_logger.error(
                f"render_command_file_with_variables 执行失败: {str(e)}"
            )
            raise

    def handle_command_command(
        self, query: str, conversation_config, command_infos: dict
    ) -> Optional[Union[str, None]]:
        """
        处理 command 指令的主入口

        Args:
            query: 查询字符串
            conversation_config: 对话配置对象
            command_infos: parse_query 返回的命令信息（兼容性参数，不再使用）

        Returns:
            None: 表示处理了 command 指令且是 dryrun，应该返回
            "continue": 表示处理了 command 指令但不是 dryrun，应该继续执行
            其他值: 表示没有处理 command 指令，应该继续执行
        """
        # 使用类型化解析器解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 command 命令
        if not result.has_command("command"):
            return "continue"  # 不是 command 指令，继续执行

        # 渲染命令文件
        try:
            # 获取 command 命令的 ParsedCommand 对象
            command_parsed = result.get_command("command")
            if not command_parsed:
                raise ValueError("无法获取 command 命令的解析结果")

            # 使用类型化解析结果渲染命令文件
            task_query = self._render_command_file_with_variables(command_parsed)
            conversation_config.query = task_query

            # 判断是否是 dryrun 模式
            is_dryrun = result.has_command("dryrun")

            if is_dryrun:
                # dryrun 模式，只显示渲染结果，不执行
                self.console.print(task_query)
                global_logger.info("Command executed in dryrun mode")
                return None  # 返回 None 表示处理完成，不继续执行
            else:
                # 非 dryrun 模式，继续执行
                global_logger.info(f"Command rendered, continuing execution")
                return "continue"  # 返回 continue 表示继续执行后续逻辑

        except Exception as e:
            self.console.print(
                Panel(
                    get_message_with_format(
                        "conversation_command_render_error", error=str(e)
                    ),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )
            return None  # 出错时返回 None


class ConversationListCommandHandler:
    """处理 list 对话指令相关的操作"""

    def __init__(self):
        self.console = Console()
        self._config = None

    def _format_timestamp(self, timestamp: Optional[Union[float, int, str]]) -> str:
        """
        格式化时间戳为可读的日期时间字符串

        Args:
            timestamp: Unix时间戳，可以是float、int或str类型

        Returns:
            str: 格式化后的时间字符串
        """
        if not timestamp:
            return "-"

        try:
            # 如果是字符串，尝试转换为float
            if isinstance(timestamp, str):
                try:
                    timestamp = float(timestamp)
                except ValueError:
                    return str(timestamp)

            # 转换为datetime对象
            dt = datetime.fromtimestamp(timestamp)
            # 格式化为易读的字符串
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError, OverflowError, TypeError):
            # 如果时间戳无效，返回原始值
            return str(timestamp)

    def _create_config(self):
        """创建 list 命令的类型化配置"""
        if self._config is None:
            self._config = create_config().command("list").max_args(0).build()
        return self._config

    def handle_list_command(
        self, query: str, conversation_config: AgenticEditConversationConfig
    ) -> Optional[Union[str, None]]:
        """
        处理 list 指令的主入口

        Args:
            query: 查询字符串，例如 "/list"
            conversation_config: 对话配置对象

        Returns:
            None: 表示处理了 list 指令，应该返回而不继续执行
            其他值: 表示没有处理 list 指令，应该继续执行
        """
        # 解析命令
        config = self._create_config()
        result = parse_typed_query(query, config)

        # 检查是否包含 list 命令
        if not result.has_command("list"):
            return "continue"  # 不是 list 指令，继续执行

        # 设置对话动作
        conversation_config.action = "list"

        try:
            # 获取对话列表和当前对话ID
            conversation_manager = get_conversation_manager()
            conversations = conversation_manager.list_conversations()
            current_conversation_id = conversation_manager.get_current_conversation_id()

            # 保留所有需要的字段，包括时间信息
            filtered_conversations = []
            for conv in conversations:
                filtered_conv = {
                    "conversation_id": conv.get("conversation_id"),
                    "name": conv.get("name"),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                }
                filtered_conversations.append(filtered_conv)

            if not filtered_conversations:
                self.console.print(
                    Panel(
                        get_message("conversation_list_no_conversations"),
                        title=get_message("conversation_list_title"),
                        border_style="yellow",
                    )
                )
                return None

            # 创建表格显示对话列表 - 优化列宽度以适应标准终端
            table = Table(
                title=get_message("conversation_list_title"),
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column(
                get_message("conversation_table_status"),
                style="yellow",
                width=3,
                no_wrap=True,
            )
            table.add_column(
                get_message("conversation_table_id"),
                style="cyan",
                no_wrap=True,
                min_width=36,
                overflow="ignore",  # UUID长度36字符，禁止截断确保完整显示
            )
            table.add_column(
                get_message("conversation_table_name"),
                style="green",
                no_wrap=True,
                width=12,
                overflow="fold",
            )
            table.add_column(
                get_message("conversation_table_time"),
                style="yellow",
                no_wrap=True,
                width=16,
            )
            table.add_column(
                get_message("conversation_table_created_at"),
                style="blue",
                no_wrap=True,
                width=16,
            )
            table.add_column(
                get_message("conversation_table_updated_at"),
                style="magenta",
                no_wrap=True,
                width=16,
            )

            # 添加对话行
            for conv in filtered_conversations:
                conv_id = conv["conversation_id"] or "-"
                # 检查是否是当前对话
                is_current = conv_id == current_conversation_id
                status = (
                    get_message("conversation_status_current") if is_current else ""
                )

                # 格式化创建时间和更新时间
                created_at = self._format_timestamp(conv.get("created_at"))
                updated_at = self._format_timestamp(conv.get("updated_at"))

                # 计算会话时间：优先显示更新时间，如果没有则显示创建时间
                conversation_time = updated_at if updated_at != "-" else created_at

                table.add_row(
                    status,
                    conv_id,
                    conv["name"] or "-",
                    conversation_time,
                    created_at,
                    updated_at,
                )

            self.console.print(table)

            # 显示汇总信息，包含当前对话
            summary_text = get_message_with_format(
                "conversation_list_summary", total=len(filtered_conversations)
            )
            if current_conversation_id:
                # 找到当前对话的名字
                current_name = None
                for conv in filtered_conversations:
                    if conv["conversation_id"] == current_conversation_id:
                        current_name = conv["name"]
                        break

                if current_name:
                    summary_text += "\n" + get_message_with_format(
                        "conversation_current_info",
                        name=current_name,
                        id=current_conversation_id,
                    )

            self.console.print(
                Panel(
                    summary_text,
                    title="📊 Summary",
                    border_style="blue",
                )
            )

        except Exception as e:
            self.console.print(
                Panel(
                    get_message_with_format("conversation_list_error", error=str(e)),
                    title=get_message("conversation_error"),
                    border_style="red",
                )
            )

        return None  # 处理完成
