import platform
import os
import win32com.client


class CONFIG:
    def __init__(self):
        system = platform.system()
        if system == "Windows":
            self._config_path = os.path.expanduser("~\\.tschm\\")
        else:
            raise NotImplementedError("目前仅支持Windows系统的任务计划管理")

    def open_dir(self):
        """
        打开配置文件目录

        在文件资源管理器中打开配置文件所在的目录。
        如果目录不存在，会自动创建。

        Raises:
            NotImplementedError: 当前系统不是 Windows 时抛出
        """
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if platform.system() == "Windows":
            os.startfile(config_dir)
        else:
            raise NotImplementedError("目前仅支持Windows系统的任务计划管理")

    def init(self):
        """
        初始化配置文件目录和任务计划程序文件夹

        执行以下操作：
        1. 创建配置文件目录（如果不存在）
        2. 从 templates 目录复制模板文件到配置目录 如果配置目录已存在同名文件则不操作
        3. 在 Windows 任务计划程序中创建 \\tschm 文件夹

        如果 \\tschm 文件夹已存在，会跳过创建步骤。

        Raises:
            ImportError: 未安装 pywin32 模块时抛出
            Exception: 其他执行错误
        """
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 将 templates 目录下的所有文件复制到配置文件目录下
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(current_dir)
        templates_dir = os.path.join(current_dir, "templates")
        print(templates_dir)
        for filename in os.listdir(templates_dir):
            src_file = os.path.join(templates_dir, filename)
            dst_file = os.path.join(config_dir, filename)
            if not os.path.exists(dst_file):
                with open(src_file, "rb") as fsrc:
                    with open(dst_file, "wb") as fdst:
                        fdst.write(fsrc.read())
        print(f"已初始化配置文件，路径: {self._config_path}")

        try:
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # 尝试获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder("\\tschm")
                print("提示: \\tschm 文件夹已存在，无需重复创建。")
                return
            except Exception:
                pass  # 文件夹不存在，继续创建

            # 获取根文件夹
            rootFolder = scheduler.GetFolder("\\")
            # 创建 \tschm 文件夹
            tschmFolder = rootFolder.CreateFolder("tschm", "")  # noqa: F841
            print("成功: 已创建 \\tschm 文件夹。")

        except ImportError:
            print("错误: 请先安装pywin32模块")
            print("安装命令: pip install pywin32")
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback

            traceback.print_exc()

    def list(self):
        """
        列出配置文件目录中的所有文件和子目录

        显示配置目录中每个项目的详细信息，包括：
        - 文件：显示文件名、大小（字节）和修改时间
        - 目录：显示目录名

        如果配置目录不存在或为空，会显示相应提示信息。

        Raises:
            PermissionError: 没有访问目录的权限时抛出
            Exception: 其他列出文件时的错误
        """
        # 确保配置目录存在
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            print(f"配置目录不存在: {config_dir}")
            return

        # 列出目录中的所有文件和子目录
        try:
            items = os.listdir(config_dir)
            if not items:
                print(f"配置目录为空: {config_dir}")
                return

            print(f"配置目录内容 ({config_dir}):")
            print("-" * 50)

            for i, item in enumerate(items, 1):
                item_path = os.path.join(config_dir, item)
                if os.path.isfile(item_path):
                    # 获取文件大小
                    size = os.path.getsize(item_path)
                    # 获取文件修改时间
                    mtime = os.path.getmtime(item_path)
                    import datetime

                    mod_time = datetime.datetime.fromtimestamp(mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    print(
                        f"{i:2d}. [文件] {item:<30} 大小: {size:>8} 字节  修改时间: {mod_time}"
                    )
                elif os.path.isdir(item_path):
                    print(f"{i:2d}. [目录] {item}")

            print("-" * 50)
            print(f"总计: {len(items)} 项")

        except PermissionError:
            print(f"权限不足，无法访问目录: {config_dir}")
        except Exception as e:
            print(f"列出文件时发生错误: {str(e)}")

    def add_file(self, source_path: str):
        """
        将指定文件复制到配置文件目录

        Args:
            source_path: 源文件的完整路径

        如果配置目录不存在，会自动创建。
        复制后的文件保持原文件名。

        Raises:
            Exception: 文件不存在或复制过程中发生错误
        """
        # 确保配置目录存在
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if not os.path.isfile(source_path):
            print(f"源文件不存在: {source_path}")
            return

        filename = os.path.basename(source_path)
        dest_path = os.path.join(config_dir, filename)

        try:
            with open(source_path, "rb") as fsrc:
                with open(dest_path, "wb") as fdst:
                    fdst.write(fsrc.read())
            print(f"已将文件复制到配置目录: {dest_path}")
        except Exception as e:
            print(f"复制文件时发生错误: {str(e)}")

    def del_file(self, filename: str):
        """
        删除配置文件目录下的指定文件

        Args:
            filename: 要删除的文件名（不包含路径）

        如果文件不存在，会显示提示信息。

        Raises:
            Exception: 删除文件时发生错误
        """
        config_dir = os.path.dirname(self._config_path)
        file_path = os.path.join(config_dir, filename)

        if not os.path.isfile(file_path):
            print(f"文件不存在: {file_path}")
            return

        try:
            os.remove(file_path)
            print(f"已删除文件: {file_path}")
        except Exception as e:
            print(f"删除文件时发生错误: {str(e)}")

    def del_all_files(self):
        """
        删除配置文件目录下的所有文件

        仅删除文件，不删除子目录。
        如果配置目录不存在，会显示提示信息。

        Raises:
            Exception: 删除文件时发生错误
        """
        config_dir = os.path.dirname(self._config_path)

        if not os.path.exists(config_dir):
            print(f"配置目录不存在: {config_dir}")
            return

        try:
            for filename in os.listdir(config_dir):
                file_path = os.path.join(config_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"已删除配置目录下的所有文件: {config_dir}")
        except Exception as e:
            print(f"删除文件时发生错误: {str(e)}")
