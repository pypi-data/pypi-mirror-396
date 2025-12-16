"""
反馈文本编辑组件

支持图片粘贴和快捷键提交的文本编辑框。
"""

import base64
import sys
from typing import List, Dict, Any, Optional
from io import BytesIO

from PySide6.QtWidgets import QTextEdit, QApplication, QLabel, QDialog, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, QIODevice, QBuffer, QRect, QPoint, QTimer
from PySide6.QtGui import QKeyEvent, QPixmap, QTextImageFormat, QTextDocument, QTextCursor

# 尝试导入PIL库用于图片压缩
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # 不显示警告，使用Qt内置功能作为替代

# 导入指令弹窗组件
try:
    from .command_popup import CommandPopup
    COMMAND_POPUP_AVAILABLE = True
except ImportError:
    try:
        from command_popup import CommandPopup
        COMMAND_POPUP_AVAILABLE = True
    except ImportError:
        COMMAND_POPUP_AVAILABLE = False
        print("Warning: CommandPopup component not available")

# 导入指令管理器
try:
    from ..command import CommandManager
except ImportError:
    try:
        from command import CommandManager
    except ImportError:
        CommandManager = None
        print("Warning: CommandManager not available")


class ImageViewerDialog(QDialog):
    """图片查看器对话框"""
    
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片查看器")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 设置对话框大小
        self.resize(800, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        
        # 创建标签显示图片
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        
        scroll_area.setWidget(image_label)
        layout.addWidget(scroll_area)
    
    def keyPressEvent(self, event):
        """处理键盘事件，ESC键关闭对话框"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


class FeedbackTextEdit(QTextEdit):
    """反馈文本编辑框
    
    支持以下功能：
    1. Ctrl+Enter / Cmd+Enter 快捷键提交
    2. 图片粘贴支持，自动转换为base64格式，支持压缩
    3. 拖拽文件支持
    4. 图片点击放大查看
    5. 输入"/"时弹出指令列表
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pasted_images = []  # Store pasted images as base64
        self.original_images = []  # Store original pixmaps for viewing
        self.setAcceptDrops(True)
        
        # 指令弹窗相关属性
        self.command_popup = None  # 指令弹窗实例
        self.project_path = None   # 项目路径
        self.command_manager = None  # 指令管理器
        self.slash_position = -1   # "/"字符的位置
        
        # 智能延迟机制相关属性
        self.slash_check_timer = QTimer()
        self.slash_check_timer.setSingleShot(True)
        self.slash_check_timer.timeout.connect(self._delayed_check_slash)
        self.last_checked_line = ""  # 记录上次检查的行内容，避免重复检查
        
        # 智能//检测相关属性
        self.slash_timer = QTimer()
        self.slash_timer.setSingleShot(True)
        self.slash_timer.timeout.connect(self._handle_slash_timeout)
        self.pending_slash_position = -1  # 等待中的/位置
        self.current_slash_count = 0  # 当前斜杠数量
        self.waiting_for_more_slashes = False  # 是否正在等待更多斜杠
        
        # 可配置的指令选择处理器
        self.custom_command_handler = None
        
        # 连接文本变化信号，确保中文输入法输入也能触发检查
        self.textChanged.connect(self._on_text_changed)
        
    def set_project_path(self, project_path: str):
        """设置项目路径"""
        self.project_path = project_path
        if CommandManager:
            self.command_manager = CommandManager(project_path)
    
    def set_command_handler(self, handler):
        """设置自定义指令选择处理器"""
        self.custom_command_handler = handler
    
    def _on_text_changed(self):
        """文本变化时触发，确保中文输入法输入也能被检测"""
        # 启动延迟检查，确保所有文本变化（包括中文输入法）都能触发斜杠检测
        self.slash_check_timer.stop()
        self.slash_check_timer.start(100)

    def _compress_image_qt(self, pixmap: QPixmap, max_size_mb: int = 2) -> bytes:
        """使用Qt内置功能压缩图片"""
        # 目标大小（字节）
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # 首先尝试PNG格式
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        
        # 尝试不同的图片格式和质量
        formats_and_quality = [
            ("PNG", 100),  # PNG无损压缩
            ("JPEG", 90),  # JPEG高质量
            ("JPEG", 80),  # JPEG中等质量
            ("JPEG", 60),  # JPEG较低质量
            ("JPEG", 40),  # JPEG低质量
        ]
        
        original_pixmap = pixmap
        
        for format_name, quality in formats_and_quality:
            # 重置buffer
            buffer.close()
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            
            # 保存图片
            if format_name == "PNG":
                success = original_pixmap.save(buffer, format_name)
            else:
                success = original_pixmap.save(buffer, format_name, quality)
            
            if success:
                data = buffer.data().data()
                if len(data) <= max_size_bytes:
                    buffer.close()
                    return data
        
        # 如果仍然过大，尝试缩小图片尺寸
        scale_factors = [0.8, 0.6, 0.4, 0.3]
        
        for scale_factor in scale_factors:
            scaled_pixmap = original_pixmap.scaled(
                int(original_pixmap.width() * scale_factor),
                int(original_pixmap.height() * scale_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            buffer.close()
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            
            if scaled_pixmap.save(buffer, "JPEG", 60):
                data = buffer.data().data()
                if len(data) <= max_size_bytes:
                    buffer.close()
                    return data
        
        # 最后的尝试：最低质量
        buffer.close()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        original_pixmap.save(buffer, "JPEG", 30)
        data = buffer.data().data()
        buffer.close()
        return data

    def _compress_image(self, image_data: bytes, max_size_mb: int = 2) -> bytes:
        """压缩图片到指定大小以内
        
        Args:
            image_data: 原始图片字节数据
            max_size_mb: 最大文件大小（MB）
        
        Returns:
            bytes: 压缩后的图片数据
        """
        # 检查原始大小
        original_size = len(image_data)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if original_size <= max_size_bytes:
            return image_data
        
        # 如果有PIL库，优先使用PIL
        if PIL_AVAILABLE:
            try:
                # 打开图片
                image = Image.open(BytesIO(image_data))
                
                # 转换为RGB模式（如果需要）
                if image.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 计算压缩质量
                quality = 90
                while quality > 20:
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=quality, optimize=True)
                    compressed_data = output.getvalue()
                    
                    if len(compressed_data) <= max_size_bytes:
                        return compressed_data
                    
                    quality -= 10
                
                # 如果质量压缩还不够，尝试缩小图片尺寸
                width, height = image.size
                scale_factor = 0.8
                
                while scale_factor > 0.3:
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    output = BytesIO()
                    resized_image.save(output, format='JPEG', quality=70, optimize=True)
                    compressed_data = output.getvalue()
                    
                    if len(compressed_data) <= max_size_bytes:
                        return compressed_data
                    
                    scale_factor -= 0.1
                
                # 最后尝试
                output = BytesIO()
                image.save(output, format='JPEG', quality=30, optimize=True)
                return output.getvalue()
                
            except Exception as e:
                print(f"PIL图片压缩失败，使用Qt备用方案: {e}")
        
        # 使用Qt内置功能作为备用方案
        try:
            # 从字节数据创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            
            if not pixmap.isNull():
                return self._compress_image_qt(pixmap, max_size_mb)
            else:
                print("无法从数据创建QPixmap")
                return image_data
            
        except Exception as e:
            print(f"Qt图片压缩失败: {e}")
            return image_data

    def _add_image_to_editor(self, pixmap: QPixmap, image_data: bytes = None):
        """添加图片到编辑器，支持点击放大"""
        try:
            # 压缩图片数据
            if image_data is None:
                # 从pixmap获取数据
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                pixmap.save(buffer, "PNG")
                image_data = buffer.data().data()
                buffer.close()
            
            # 压缩图片
            compressed_data = self._compress_image(image_data)
            base64_image = base64.b64encode(compressed_data).decode('utf-8')
            
            # 存储原始图片用于放大查看
            self.original_images.append(pixmap)
            self.pasted_images.append(base64_image)
            
            # 创建显示用的缩放图片
            display_pixmap = pixmap.copy()
            
            # 设置显示尺寸：最大宽度50%（相对于编辑器宽度），最大高度300px
            editor_width = self.viewport().width() - 20  # 留一些边距
            max_width = min(int(editor_width * 0.5), pixmap.width())  # 50%宽度
            max_height = 300
            
            if pixmap.width() > max_width or pixmap.height() > max_height:
                display_pixmap = pixmap.scaled(
                    max_width, max_height, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
            
            # 插入图片到文档
            cursor = self.textCursor()
            cursor.insertText("\n")  # 添加换行
            
            # 创建图片格式
            image_format = QTextImageFormat()
            image_format.setWidth(display_pixmap.width())
            image_format.setHeight(display_pixmap.height())
            image_format.setName(f"image_{len(self.pasted_images)}")
            
            # 将图片添加到文档资源
            self.document().addResource(
                QTextDocument.ImageResource, 
                image_format.name(), 
                display_pixmap
            )
            
            # 插入图片
            cursor.insertImage(image_format)
            cursor.insertText("\n")  # 添加换行
            
            print(f"图片已添加，原始大小: {len(image_data)/1024:.1f}KB, 压缩后: {len(compressed_data)/1024:.1f}KB")
            
        except Exception as e:
            print(f"添加图片时出错: {e}")

    def mousePressEvent(self, event):
        """处理鼠标单击事件，执行正常的文本编辑行为"""
        # 关闭指令弹窗
        self._close_command_popup()
        # 执行默认行为（正常的光标定位和文本编辑）
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件，支持图片放大查看"""
        if event.button() == Qt.LeftButton:
            # 获取点击位置的光标
            click_pos = event.pos()
            cursor = self.cursorForPosition(click_pos)
            
            # 检查点击位置是否有图片
            char_format = cursor.charFormat()
            if char_format.isImageFormat():
                # 获取图片格式信息
                image_format = char_format.toImageFormat()
                
                # 获取光标位置的矩形
                cursor_rect = self.cursorRect(cursor)
                
                # 创建图片的实际显示区域
                image_rect = QRect(
                    cursor_rect.x(),
                    cursor_rect.y(),
                    image_format.width(),
                    image_format.height()
                )
                
                # 只有双击在图片区域内才显示预览
                if image_rect.contains(click_pos):
                    try:
                        # 从图片名称获取索引
                        image_name = image_format.name()
                        if image_name.startswith("image_"):
                            image_index = int(image_name.split("_")[1]) - 1
                            if 0 <= image_index < len(self.original_images):
                                # 显示放大的图片
                                dialog = ImageViewerDialog(self.original_images[image_index], self)
                                dialog.exec()
                                # 直接返回，不执行默认双击行为
                                event.accept()
                                return
                    except (ValueError, IndexError) as e:
                        print(f"解析图片索引时出错: {e}")
                
                # 如果双击在图片上但不在有效区域内，仍然阻止默认行为
                event.accept()
                return
        
        # 如果不是图片双击，执行默认行为
        super().mouseDoubleClickEvent(event)

    def add_image_file(self, file_path: str):
        """从文件路径添加图片"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 读取文件数据
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                self._add_image_to_editor(pixmap, image_data)
            else:
                print(f"无法加载图片文件: {file_path}")
        except Exception as e:
            print(f"添加图片文件时出错: {e}")

    def _check_slash_input(self):
        """智能检查斜杠输入以触发指令弹窗"""
        if not COMMAND_POPUP_AVAILABLE or not self.command_manager:
            return False
            
        cursor = self.textCursor()
        
        # 检查当前行的文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 如果与上次检查的行内容相同，不重复处理
        if line_text == self.last_checked_line:
            return False
        
        # 检查是否以 / 开头
        if line_text.startswith('/'):
            # 立即显示合并的指令列表
            self._cancel_slash_wait()
            cursor.movePosition(QTextCursor.StartOfLine)
            self.slash_position = cursor.position()
            
            # 获取 / 后面的内容作为过滤文本
            filter_text = line_text[1:].strip()  # 去掉开头的 / 
            
            # 显示所有指令（合并显示）
            self._show_command_popup(filter_text, "all")
            return True
        else:
            # 不是以 / 开头，关闭弹窗
            self._cancel_slash_wait()
            self._close_command_popup()
            return False
    
    def _handle_slash_timeout(self):
        """处理斜杠输入超时 - 新版本不再需要等待"""
        # 重置状态
        self.waiting_for_more_slashes = False
        self.current_slash_count = 0
        self.pending_slash_position = -1
    
    def _cancel_slash_wait(self):
        """取消斜杠等待状态"""
        self.slash_timer.stop()
        self.waiting_for_more_slashes = False
        self.current_slash_count = 0
        self.pending_slash_position = -1

    def _show_command_popup(self, filter_text: str = "", command_type: str = ""):
        """显示指令弹窗"""
        if not COMMAND_POPUP_AVAILABLE or not self.command_manager:
            print("Warning: CommandPopup or CommandManager not available")
            return

        # 如果弹窗已存在且可见，更新其内容而不是直接返回
        if self.command_popup:
            try:
                if self.command_popup.isVisible():
                    # 更新弹窗内容
                    commands = self._load_commands_by_type(command_type)
                    self.command_popup.set_commands(commands)
                    if filter_text:
                        self.command_popup.set_filter(filter_text)
                    return
            except Exception as e:
                # 如果检查可见性失败，说明对象可能已经无效，清理它
                print(f"Popup check failed: {e}")
                self.command_popup = None

        # 关闭之前的弹窗
        self._close_command_popup()

        # 直接创建新弹窗
        self._create_new_popup(filter_text, command_type)
    
    def _create_new_popup(self, filter_text: str = "", command_type: str = ""):
        """创建新的指令弹窗"""
        try:
            # 创建新的弹窗
            self.command_popup = CommandPopup(self)
            
            # 设置项目路径和指令类型
            if hasattr(self, 'project_path') and self.project_path:
                self.command_popup.set_project_path(self.project_path)
            self.command_popup.set_command_type(command_type)
            
            # 连接信号
            self.command_popup.command_selected.connect(self._on_command_selected)
            self.command_popup.popup_closed.connect(self._on_popup_closed)
            # add_command_requested 信号连接已移除
            
            # 根据类型加载指令
            commands = self._load_commands_by_type(command_type)
            self.command_popup.set_commands(commands)
            
            # 更新弹窗标题
            type_names = {
                'all': '📋 所有指令',
                'project': '📝 项目指令',
                'personal': '👤 个人指令'
            }
            title = type_names.get(command_type, '📝 选择指令')
            
            # 新版不需要触发字符提示
            self.command_popup.title_label.setText(title)
            
            # 设置过滤
            if filter_text:
                self.command_popup.set_filter(filter_text)
            
            # 计算弹窗位置（在光标下方）
            cursor_rect = self.cursorRect(self.textCursor())
            popup_position = self.mapToGlobal(QPoint(cursor_rect.x(), cursor_rect.bottom() + 5))
            
            # 显示弹窗
            self.command_popup.show_at_position(popup_position)
            
        except Exception as e:
            print(f"创建指令弹窗失败: {e}")
            self.command_popup = None

    def _load_commands_by_type(self, command_type: str) -> List[Dict[str, Any]]:
        """根据类型加载指令"""
        commands = []

        if not self.command_manager:
            return commands

        try:
            if command_type == "all":
                # 加载所有类型的指令（合并显示）
                # 1. 项目指令
                project_commands = self.command_manager.load_project_commands()
                for cmd in project_commands:
                    cmd['type'] = 'project'
                    cmd['category'] = '📝 项目指令'
                    commands.append(cmd)

                # 2. 个人指令
                personal_commands = self.command_manager.load_personal_commands()
                for cmd in personal_commands:
                    cmd['type'] = 'personal'
                    cmd['category'] = '👤 个人指令'
                    commands.append(cmd)

                # 3. 插件指令（新增）
                plugin_commands = self.command_manager.load_plugin_commands()
                for cmd in plugin_commands:
                    cmd['type'] = 'plugin'
                    # 不设置 category,因为指令标题已通过 @插件名 标注
                    commands.append(cmd)

            elif command_type == "project":
                # 加载项目指令
                project_commands = self.command_manager.load_project_commands()
                for cmd in project_commands:
                    cmd['type'] = 'project'
                    cmd['category'] = '📝 项目指令'
                    commands.append(cmd)

            elif command_type == "personal":
                # 加载个人指令
                personal_commands = self.command_manager.load_personal_commands()
                for cmd in personal_commands:
                    cmd['type'] = 'personal'
                    cmd['category'] = '👤 个人指令'
                    commands.append(cmd)

        except Exception as e:
            print(f"加载{command_type}指令时出错: {e}")

        return commands

    def _close_command_popup(self):
        """关闭指令弹窗"""
        if self.command_popup:
            try:
                # 断开信号连接，避免删除后的回调
                self.command_popup.command_selected.disconnect()
                self.command_popup.popup_closed.disconnect()
            except:
                pass  # 忽略断开连接的错误
            
            try:
                self.command_popup.close()
                self.command_popup.hide()
            except:
                pass  # 忽略关闭错误
                
            # 延迟删除，确保不会立即删除
            try:
                self.command_popup.deleteLater()
            except:
                pass
                
            self.command_popup = None
            self.slash_position = -1
            self.last_checked_line = ""  # 重置检查状态
        
        # 取消所有等待状态
        self._cancel_slash_wait()

    def _on_command_selected(self, command_content: str, command_data: dict = None):
        """处理指令选择"""
        # 先清空 /xxx 内容
        cursor = self.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText()
        
        # 如果当前行以 / 开头，清空整行
        if line_text.startswith('/'):
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        
        # 如果有自定义处理器，使用自定义处理器
        if self.custom_command_handler:
            # 传递完整的指令数据给自定义处理器
            if command_data:
                self.custom_command_handler(command_content, command_data)
            else:
                self.custom_command_handler(command_content)
        else:
            # 默认行为：插入指令内容
            cursor = self.textCursor()
            cursor.insertText(command_content)
            
        # 关闭弹窗
        self._close_command_popup()
    
    def _smart_remove_trigger_slashes(self):
        """智能删除触发弹窗的触发字符（/或、）"""
        cursor = self.textCursor()
        
        # 获取当前行文本
        cursor.select(QTextCursor.LineUnderCursor)
        line_text = cursor.selectedText().strip()
        
        # 检查是否是纯触发字符（只支持纯/或纯、，不支持混合）
        trigger_patterns = [
            "/", "//", "///",           # 英文斜杠
            "、", "、、", "、、、",      # 中文顿号
        ]
        
        if line_text in trigger_patterns:
            # 选中整行并删除
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            print(f"智能删除触发字符: '{line_text}'")

    def _on_popup_closed(self):
        """处理弹窗关闭"""
        # 简单地清空引用，让Qt自己管理对象删除
        self.command_popup = None
        self.slash_position = -1

    # 添加指令请求处理方法已移除
    # 用户需要直接编辑 .md 文件来管理指令

    def keyPressEvent(self, event: QKeyEvent):
        # 如果指令弹窗打开，让弹窗处理某些按键
        if self.command_popup and self.command_popup.isVisible():
            if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter):
                # 方向键和回车键传递给弹窗处理
                self.command_popup.keyPressEvent(event)
                return
            elif event.key() == Qt.Key_Escape:
                # ESC键关闭弹窗
                self._close_command_popup()
                return
            elif event.text().isdigit():
                # 数字键快速选择
                self.command_popup.keyPressEvent(event)
                return
            # 其他按键（如字母）继续在输入框中输入，用于过滤
        
        # ESC键处理：清空已选择的指令（当输入框有焦点时）
        if event.key() == Qt.Key_Escape:
            # 寻找有_clear_selected_command方法的父组件（通常是ChatTab）
            parent = self.parent()
            has_command = False
            while parent:
                if hasattr(parent, '_clear_selected_command'):
                    parent._clear_selected_command()
                    has_command = True
                    break
                parent = parent.parent()
            
            # 无论是否找到清空方法，都要继续传播事件以支持双击ESC
            # 让事件继续向上传播到主窗口
            event.ignore()  # 忽略事件，让它继续传播
            super().keyPressEvent(event)
            return
                
        if (event.key() == Qt.Key_Return and 
            (event.modifiers() == Qt.ControlModifier or event.modifiers() == Qt.MetaModifier)):
            # 寻找有_submit_feedback方法的父组件（通常是ChatTab）
            parent = self.parent()
            while parent:
                if hasattr(parent, '_submit_feedback'):
                    parent._submit_feedback()
                    return
                parent = parent.parent()
            return
        elif (event.key() == Qt.Key_V and 
              (event.modifiers() == Qt.ControlModifier or event.modifiers() == Qt.MetaModifier)):
            # Handle paste operation
            self._handle_paste()
        else:
            # 先执行默认键盘处理
            super().keyPressEvent(event)
            
            # 使用延迟机制检查触发字符输入，避免连续输入时被打断
            # 对于中文输入，也需要检查
            print(f"按键事件: key={event.key()}, text='{event.text()}'")
            if event.key() not in (Qt.Key_Control, Qt.Key_Meta, Qt.Key_Shift, Qt.Key_Alt):
                # 停止之前的计时器
                self.slash_check_timer.stop()
                # 启动新的延迟检查（缩短为100ms，因为智能检测有自己的500ms延迟）
                self.slash_check_timer.start(100)  # 100ms延迟
                print("启动延迟检查计时器")
    
    def _handle_paste(self):
        """处理粘贴操作，支持文本和图片"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            # Handle image paste
            image = clipboard.image()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                self._add_image_to_editor(pixmap)
                return
        
        if mime_data.hasText():
            # Handle text paste
            text = mime_data.text()
            cursor = self.textCursor()
            cursor.insertText(text)
            return
        
        # Fallback to default paste behavior
        super().paste()
    
    def get_pasted_images(self) -> List[str]:
        """获取粘贴的图片列表"""
        return self.pasted_images.copy()
    
    def clear_images(self):
        """清空图片列表"""
        self.pasted_images.clear()
        self.original_images.clear()

    def _delayed_check_slash(self):
        """延迟检查触发字符输入"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.LineUnderCursor)
        current_line = cursor.selectedText()
        print(f"延迟检查被调用，当前行内容: '{current_line}'")
        
        # 如果弹窗已经显示，更新过滤
        if self.command_popup and hasattr(self.command_popup, 'isVisible') and self.command_popup.isVisible():
            if current_line.startswith('/'):
                filter_text = current_line[1:].strip()
                self.command_popup.set_filter(filter_text)
                print(f"更新过滤文本: '{filter_text}'")
            else:
                # 不是以 / 开头，关闭弹窗
                self._close_command_popup()
        else:
            # 弹窗未显示，检查是否需要显示
            if self._check_slash_input():
                self.last_checked_line = current_line
                print("触发字符检查返回True")
            else:
                self.last_checked_line = current_line
                print("触发字符检查返回False")
    
    def _submit_feedback(self):
        """提交反馈"""
        # 实现提交反馈的逻辑
        pass 