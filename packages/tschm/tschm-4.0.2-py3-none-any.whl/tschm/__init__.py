import fire
import win32com.client
from datetime import datetime
from .config import CONFIG
import os


class ENTRY(object):
    """
    Windows 定时任务管理器 - 支持休眠唤醒的任务调度工具

    可用命令:
        list        - 列出所有任务
        add_task    - 添加新任务
        del_task    - 删除任务
        kill_task   - 终止正在运行的任务
    """

    def __init__(self):
        self.config = CONFIG()
        pass

    def list(self):
        """列出 Windows 任务计划程序中 \\tschm 目录下的所有任务

        显示任务的详细信息，包括：
        - 任务名称和状态
        - 下次运行时间
        - 上次运行结果
        - 是否启用/隐藏
        - 执行的命令

        Examples:
            tsm list

        """
        self.list_from_tschm()

    def list_from_tschm(self):
        """使用 win32com 模块列出 \\tschm 目录下的所有任务

        内部方法，由 list() 调用。
        显示任务名称、状态、下次运行时间和上次运行结果。
        """
        try:
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder("\\tschm")
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请确保任务计划程序中存在 \\tschm 文件夹")
                return []

            # 使用 1 标志来包含隐藏任务
            # 0 = 只显示非隐藏任务
            # 1 = 显示所有任务（包括隐藏任务）
            tasks = tschmFolder.GetTasks(1)

            if tasks.Count == 0:
                print("\\tschm 文件夹中没有任务")
                return []

            print(f"\n找到 {tasks.Count} 个任务:\n")
            print("-" * 100)

            task_list = []
            for task in tasks:
                # 获取任务状态
                state_map = {
                    0: "未知",
                    1: "已禁用",
                    2: "已排队",
                    3: "就绪",
                    4: "正在运行",
                }
                state = state_map.get(task.State, "未知")

                # 获取上次运行结果
                last_result = task.LastTaskResult
                result_status = (
                    "成功" if last_result == 0 else f"失败(0x{last_result:X})"
                )

                # 格式化下次运行时间
                next_run = task.NextRunTime
                try:
                    # 如果是有效的日期时间
                    if next_run and str(next_run) != "1899-12-30 00:00:00":
                        next_run_str = str(next_run)
                    else:
                        next_run_str = "未计划"
                except:  # noqa: E722
                    next_run_str = "未计划"

                # 获取任务是否隐藏
                is_hidden = False
                try:
                    is_hidden = task.Definition.Settings.Hidden
                except Exception as e:  # noqa: F841
                    # 如果无法获取隐藏状态，默认为 False
                    pass

                # 获取任务执行的命令
                command_info = "未知"
                try:
                    actions = task.Definition.Actions
                    if actions.Count > 0:
                        action = actions.Item(1)  # COM 集合索引从 1 开始
                        if hasattr(action, "Path"):
                            command_path = action.Path
                            command_args = getattr(action, "Arguments", "")
                            if command_args:
                                command_info = f"{command_path} {command_args}"
                            else:
                                command_info = command_path
                except Exception:
                    pass

                task_info = {
                    "name": task.Name,
                    "state": state,
                    "next_run": next_run_str,
                    "last_result": result_status,
                    "enabled": task.Enabled,
                    "hidden": is_hidden,
                    "command": command_info,
                }
                task_list.append(task_info)

                # 打印任务信息
                print(f"任务名称: {task.Name}")
                print(
                    f"  状态: {state} | 启用: {'是' if task.Enabled else '否'} | 隐藏: {'是' if is_hidden else '否'}"
                )
                print(f"  下次运行: {next_run_str}")
                print(f"  上次结果: {result_status}")
                print(f"  运行命令: {command_info}")
                print("-" * 100)

            return
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback

            traceback.print_exc()
            return []

    def add_task(
        self,
        name: str,
        script: str,
        schedule: str = "DAILY",
        time: str = "12:00",
        hidden: bool = True,
    ):
        """在 \\tschm 目录下创建新的定时任务

        Args:
            name: 任务名称
            script: 要执行的脚本文件名（支持 .ps1, .bat, .cmd 等格式）
            schedule: 执行频率，可选值: DAILY（每天）, WEEKLY（每周）, MONTHLY（每月）
            time: 执行时间，格式为 HH:MM（24小时制），例如 "14:30"
            hidden: 是否在任务计划程序界面中隐藏任务，默认为 True

        Returns:
            bool: 成功返回 True，失败返回 False

        脚本文件查找规则:
            1. 优先在当前目录查找脚本文件
            2. 如果找到，复制到配置目录（如已存在同名文件则报错）
            3. 如果当前目录没有，则在配置目录查找
            4. 都找不到则报错

        特性:
            - 支持唤醒计算机执行任务
            - 允许在使用电池时运行
            - 错过计划时间会在下次可用时立即运行

        Examples:
            add_task("backup", "backup.ps1", "DAILY", "02:00")
            add_task("weekly_report", "report.bat", "WEEKLY", "09:00", hidden=False)
            tsm add-task test xxx.ps1 DAILY --time=21:00
        """
        try:
            # 获取当前工作目录
            current_dir = os.getcwd()
            config_dir = os.path.dirname(self.config._config_path)

            # 确保配置目录存在
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # 确定脚本文件的最终路径
            script_path_in_current = os.path.join(current_dir, script)
            script_path_in_config = os.path.join(config_dir, script)
            final_script_path = None

            # 检查当前目录是否存在脚本文件
            if os.path.isfile(script_path_in_current):
                # 检查配置目录是否已存在同名文件
                if os.path.exists(script_path_in_config):
                    print(f"错误: 配置目录下已存在同名文件 '{script}'")
                    print(f"路径: {script_path_in_config}")
                    return False

                # 复制文件到配置目录
                try:
                    import shutil

                    shutil.copy2(script_path_in_current, script_path_in_config)
                    print(f"已将脚本复制到配置目录: {script_path_in_config}")
                    final_script_path = script_path_in_config
                except Exception as e:
                    print(f"错误: 复制文件失败 - {str(e)}")
                    return False
            else:
                # 当前目录不存在，检查配置目录
                if os.path.isfile(script_path_in_config):
                    final_script_path = script_path_in_config
                    print(f"使用配置目录中的脚本: {script_path_in_config}")
                else:
                    print(f"错误: 找不到脚本文件 '{script}'")
                    print("已检查路径:")
                    print(f"  - {script_path_in_current}")
                    print(f"  - {script_path_in_config}")
                    return False

            # 验证时间格式
            try:
                hour, minute = time.split(":")
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:  # noqa: E722
                print(f"错误: 时间格式无效 '{time}'，应为 HH:MM (24小时制)")
                return False

            # 验证 schedule 参数
            schedule = schedule.upper()
            if schedule not in ["DAILY", "WEEKLY", "MONTHLY"]:
                print(
                    f"错误: schedule 参数无效 '{schedule}'，可选值为 DAILY, WEEKLY, MONTHLY"
                )
                return False

            # 创建任务计划
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder("\\tschm")
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False

            # 创建任务定义
            taskDef = scheduler.NewTask(0)

            # 设置注册信息
            regInfo = taskDef.RegistrationInfo
            regInfo.Description = f"由 tschm 创建的定时任务: {name}"
            regInfo.Author = "tschm"

            # 设置主体（运行账户）
            principal = taskDef.Principal
            principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN

            # 设置任务设置
            settings = taskDef.Settings
            settings.Enabled = True  # 启用任务，允许任务按计划运行
            settings.StartWhenAvailable = (
                False  # 如果错过了计划时间，则在下次可用时也不能运行
            )
            settings.Hidden = hidden  # 控制任务在任务计划程序界面中是否可见
            settings.WakeToRun = True  # 唤醒计算机以运行此任务
            settings.DisallowStartIfOnBatteries = False  # 允许在使用电池时启动任务
            settings.StopIfGoingOnBatteries = False  # 切换到电池供电时不停止任务

            # 创建触发器
            triggers = taskDef.Triggers
            trigger = triggers.Create(2)  # 2 = TASK_TRIGGER_DAILY

            # 设置开始时间
            start_time = datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")

            # 根据 schedule 设置触发器
            if schedule == "DAILY":
                trigger.DaysInterval = 1
            elif schedule == "WEEKLY":
                trigger = triggers.Create(3)  # 3 = TASK_TRIGGER_WEEKLY
                trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                trigger.WeeksInterval = 1
                trigger.DaysOfWeek = 127  # 每天 (1111111 in binary)
            elif schedule == "MONTHLY":
                trigger = triggers.Create(4)  # 4 = TASK_TRIGGER_MONTHLY
                trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                trigger.MonthsOfYear = 0xFFF  # 所有月份
                trigger.DaysOfMonth = 1  # 每月第一天

            # 创建操作（执行脚本）
            actions = taskDef.Actions
            action = actions.Create(0)  # 0 = TASK_ACTION_EXEC

            # 根据脚本扩展名确定执行方式
            script_ext = os.path.splitext(final_script_path)[1].lower()
            if script_ext == ".ps1":
                # 使用 cmd /c start /min 来最小化窗口启动 PowerShell
                action.Path = "cmd.exe"
                action.Arguments = f'/c start /min "" powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "{final_script_path}"'
            elif script_ext in [".bat", ".cmd"]:
                action.Path = "cmd.exe"
                action.Arguments = f'/c start /min "" "{final_script_path}"'
            else:
                # 默认使用 powershell 执行
                action.Path = "cmd.exe"
                action.Arguments = f'/c start /min "" powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "{final_script_path}"'

            # 注册任务
            tschmFolder.RegisterTaskDefinition(
                name,
                taskDef,
                6,  # TASK_CREATE_OR_UPDATE
                None,  # 使用当前用户
                None,  # 不需要密码
                3,  # TASK_LOGON_INTERACTIVE_TOKEN
                "",
            )

            print(f"成功: 已创建任务 '{name}'")
            print(f"  脚本: {final_script_path}")
            print(f"  计划: {schedule}")
            print(f"  时间: {time}")
            print(f"  唤醒计算机: 是")  # noqa: F541
            return True

        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def del_task(self, name: str):
        """删除 \\tschm 目录下的指定任务

        Args:
            name: 要删除的任务名称

        Returns:
            bool: 成功返回 True，失败返回 False

        Examples:
            del_task("backup")
            del_task("weekly_report")

            tsm del-task xxx
        """
        try:
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder("\\tschm")
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False

            # 删除指定任务
            try:
                tschmFolder.DeleteTask(name, 0)
                print(f"成功: 已删除任务 '{name}'")
                return True
            except Exception:
                print(f"错误: 任务 '{name}' 不存在")
                return False

        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def kill_task(self, name: str):
        """终止正在运行的任务进程

        如果指定的任务当前正在运行，则立即停止其执行。
        如果任务未在运行，会显示当前状态信息。

        Args:
            name: 要终止的任务名称

        Returns:
            bool: 成功终止返回 True，任务未运行或失败返回 False

        Examples:
            kill_task("backup")
            kill_task("long_running_task")

            tsm kill-task xxx
        """
        try:
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder("\\tschm")
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False

            # 获取指定任务
            try:
                task = tschmFolder.GetTask(name)
            except Exception:
                print(f"错误: 任务 '{name}' 不存在")
                return False

            # 检查任务是否正在运行
            if task.State != 4:  # 4 = 正在运行
                print(f"提示: 任务 '{name}' 当前未在运行")
                state_map = {
                    0: "未知",
                    1: "已禁用",
                    2: "已排队",
                    3: "就绪",
                    4: "正在运行",
                }
                print(f"当前状态: {state_map.get(task.State, '未知')}")
                return False

            # 停止任务
            task.Stop(0)
            print(f"成功: 已终止任务 '{name}' 的运行进程")
            return True

        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def main() -> None:
    fire.Fire(ENTRY)
