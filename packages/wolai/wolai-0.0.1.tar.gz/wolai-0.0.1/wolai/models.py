# -*- coding: utf-8 -*-

"""
Wolai 块类型定义

定义了所有支持的 Wolai 块类型及其数据结构
"""

from typing import List, Optional, Dict, Any, Union


class Block:
    """
    Wolai Block对象, 用于表示Wolai中的一个块结构

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容，可以是字符串或内容字典列表
        children (`list`): 子块对象列表
        type (`str`): 块类型
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List["Block"]] = None,
        type: str = "block",
    ):
        self.id = block_id
        self.parent_id = parent_id
        self.page_id = page_id
        self.parent_type = parent_type
        self.type = type
        # 支持content为字符串或list[dict]
        if isinstance(content, str):
            self.content = content
        elif isinstance(content, list):
            self.content = "".join([c.get("title", "") for c in content])
        else:
            self.content = str(content)
        self.children = children if children is not None else []

    def __repr__(self):
        return (
            f"Block(id={self.id!r}, type={self.type!r}, "
            f"parent_id={self.parent_id!r}, page_id={self.page_id!r}, "
            f"parent_type={self.parent_type!r}, content={self.content!r})"
        )

    def __str__(self):
        return (
            f"Wolai Block:\n"
            f"  id: {self.id}\n"
            f"  type: {self.type}\n"
            f"  parent_id: {self.parent_id}\n"
            f"  page_id: {self.page_id}\n"
            f"  parent_type: {self.parent_type}\n"
            f"  content: {self.content}\n"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        将块对象转换为字典格式

        Returns:
            `dict`: 块的字典表示
        """
        return {
            "id": self.id,
            "type": self.type,
            "parent_id": self.parent_id,
            "page_id": self.page_id,
            "parent_type": self.parent_type,
            "content": self.content,
        }


class Page(Block):
    """
    Wolai Page对象, 用于表示Wolai中的一个页面

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 页面标题（CreateRichText格式）
        children (`list`): 子块对象列表
        icon (`dict`): 图标，LinkIcon 或 EmojiIcon 格式
        page_cover (`dict`): 页面封面，LinkCover 格式
        page_setting (`dict`): 页面设置，PageSetting 格式
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
        icon: Optional[Dict[str, Any]] = None,
        page_cover: Optional[Dict[str, Any]] = None,
        page_setting: Optional[Dict[str, Any]] = None,
        _client: Optional[Any] = None,
    ):
        super().__init__(
            block_id, parent_id, page_id, parent_type, content, children, type="page"
        )
        self.icon = icon
        self.page_cover = page_cover
        self.page_setting = page_setting
        self._client = _client  # 保存客户端引用，用于 update 方法

    def to_dict(self) -> Dict[str, Any]:
        """
        将页面对象转换为字典格式

        Returns:
            `dict`: 页面的字典表示
        """
        result = super().to_dict()
        if self.icon is not None:
            result["icon"] = self.icon
        if self.page_cover is not None:
            result["page_cover"] = self.page_cover
        if self.page_setting is not None:
            result["page_setting"] = self.page_setting
        return result

    def __str__(self):
        return f"Page(id={self.id}, type={self.type}, parent_id={self.parent_id}, page_id={self.page_id}, parent_type={self.parent_type}, content={self.content}, icon={self.icon}, page_cover={self.page_cover}, page_setting={self.page_setting})"


class Heading(Block):
    """
    Wolai Heading对象, 用于表示Wolai中的一个标题

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
        level (`int`): 标题级别 (1-6)
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
        level: int = 1,
    ):
        super().__init__(
            block_id, parent_id, page_id, parent_type, content, children, type="heading"
        )
        self.level = level

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["level"] = self.level
        return result


class Text(Block):
    """
    Wolai Text对象, 用于表示Wolai中的一个文本块

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
    ):
        super().__init__(
            block_id, parent_id, page_id, parent_type, content, children, type="text"
        )


class BullList(Block):
    """
    Wolai BullList对象, 用于表示Wolai中的一个无序列表

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
    ):
        super().__init__(
            block_id,
            parent_id,
            page_id,
            parent_type,
            content,
            children,
            type="bull_list",
        )


class TodoList(Block):
    """
    Wolai TodoList对象, 用于表示Wolai中的一个待办列表

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
        checked (`bool`): 是否已完成
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
        checked: bool = False,
    ):
        super().__init__(
            block_id,
            parent_id,
            page_id,
            parent_type,
            content,
            children,
            type="todo_list",
        )
        self.checked = checked

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["checked"] = self.checked
        return result


class EnumList(Block):
    """
    Wolai EnumList对象, 用于表示Wolai中的一个有序列表

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
    ):
        super().__init__(
            block_id,
            parent_id,
            page_id,
            parent_type,
            content,
            children,
            type="enum_list",
        )


class Code(Block):
    """
    Wolai Code对象, 用于表示Wolai中的一个代码块

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
        language (`str`): 编程语言
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
        language: str = "",
    ):
        super().__init__(
            block_id, parent_id, page_id, parent_type, content, children, type="code"
        )
        self.language = language

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["language"] = self.language
        return result


class Image(Block):
    """
    Wolai Image对象, 用于表示Wolai中的一个图片块

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
        url (`str`): 图片URL
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
        url: str = "",
    ):
        super().__init__(
            block_id, parent_id, page_id, parent_type, content, children, type="image"
        )
        self.url = url

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["url"] = self.url
        return result


class Database(Block):
    """
    Wolai Database对象, 用于表示Wolai中的一个数据库块

    Args:
        block_id (`str`): 块的唯一ID
        parent_id (`str`): 父块ID
        page_id (`str`): 所属页面ID
        parent_type (`str`): 父块类型
        content (`str` | `list[dict]`): 块内容
        children (`list`): 子块对象列表
    """

    def __init__(
        self,
        block_id: str,
        parent_id: str = "",
        page_id: str = "",
        parent_type: str = "",
        content: Union[str, List[Dict[str, Any]]] = "",
        children: Optional[List[Block]] = None,
    ):
        super().__init__(
            block_id,
            parent_id,
            page_id,
            parent_type,
            content,
            children,
            type="database",
        )
