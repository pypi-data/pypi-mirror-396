# -*- coding: utf-8 -*-

"""
Wolai API 客户端

提供完整的 Wolai API 接口封装
"""

import requests
from typing import List, Dict, Any, Optional, Union
from .models import (
    Block,
    Page,
    Heading,
    Text,
    BullList,
    TodoList,
    EnumList,
    Code,
    Image,
    Database,
)


class WolaiClient:
    """
    Wolai API 客户端类

    Args:
        token (`str`): Wolai API Token
        base_url (`str`): API 基础URL，默认为 https://openapi.wolai.com
    """

    def __init__(self, token: str, base_url: str = "https://openapi.wolai.com"):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "authorization": self.token,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method (`str`): HTTP方法 (GET, POST, PUT, DELETE)
            endpoint (`str`): API端点路径
            data (`dict`): 请求体数据
            params (`dict`): URL查询参数

        Returns:
            `dict`: API响应数据

        Raises:
            `requests.RequestException`: 请求失败时抛出异常
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # 提供更详细的错误信息
            error_msg = f"Wolai API 请求失败: {e}"
            try:
                error_detail = response.json()
                if "message" in error_detail:
                    error_msg += f"\n错误详情: {error_detail['message']}"
                    # 针对常见错误提供更详细的提示
                    if (
                        "UUID" in error_detail.get("message", "")
                        or "uuid" in error_detail.get("message", "").lower()
                    ):
                        error_msg += "\n提示: 请检查 parent_id 是否为有效的 UUID 格式"
                elif "error" in error_detail:
                    error_msg += f"\n错误详情: {error_detail['error']}"
                else:
                    error_msg += f"\n响应内容: {error_detail}"
            except:
                error_msg += f"\n响应状态码: {response.status_code}"
                error_msg += f"\n响应内容: {response.text[:500]}"

            # 针对 500 错误提供额外提示
            if response.status_code == 500:
                error_msg += (
                    "\n提示: 服务器内部错误，可能是请求参数格式不正确，请检查："
                )
                error_msg += "\n  - parent_id 是否为有效的 UUID 格式"
                error_msg += (
                    "\n  - content 格式是否正确（字符串或 CreateRichText 格式）"
                )
                error_msg += "\n  - 其他参数是否符合 API 要求"

            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Wolai API 请求失败: {e}")

    def _parse_block(self, data: Dict[str, Any]) -> Block:
        """
        解析块数据为Block对象

        Args:
            data (`dict`): 块数据字典

        Returns:
            `Block`: 解析后的块对象
        """
        block_type = data.get("type", "block")
        common_kwargs = {
            "block_id": data.get("id", ""),
            "parent_id": data.get("parent_id", ""),
            "page_id": data.get("page_id", ""),
            "parent_type": data.get("parent_type", ""),
            "content": data.get("content", ""),
        }

        # 递归解析子块
        children_ids = data.get("children", {}).get("ids", [])
        if children_ids:
            # 注意：这里需要先获取子块数据，但为了避免递归调用API，暂时设为空列表
            # 实际使用时可以通过 get_block 方法获取子块
            common_kwargs["children"] = []

        if block_type == "page":
            return Page(
                **common_kwargs,
                icon=data.get("icon"),
                page_cover=data.get("page_cover"),
                page_setting=data.get("page_setting"),
            )
        elif block_type == "heading":
            return Heading(**common_kwargs, level=data.get("level", 1))
        elif block_type == "text":
            return Text(**common_kwargs)
        elif block_type == "bull_list":
            return BullList(**common_kwargs)
        elif block_type == "todo_list":
            return TodoList(**common_kwargs, checked=data.get("checked", False))
        elif block_type == "enum_list":
            return EnumList(**common_kwargs)
        elif block_type == "code":
            return Code(**common_kwargs, language=data.get("language", ""))
        elif block_type == "image":
            return Image(**common_kwargs, url=data.get("url", ""))
        elif block_type == "database":
            return Database(**common_kwargs)
        else:
            return Block(**common_kwargs, type=block_type)

    # ==================== 块操作接口 ====================

    def get_page(self, page_id: str) -> Page:
        """
        查询页面详情

        Args:
            page_id (`str`): 页面的ID

        Returns:
            `Page`: 页面对象，包含以下属性：
                - icon: 图标（LinkIcon 或 EmojiIcon）
                - page_cover: 页面封面（LinkCover）
                - page_setting: 页面设置（PageSetting）
                - content: 页面标题（CreateRichText）

        示例:
            ```python
            page = client.get_page("page_id")
            print(page.content)  # 页面标题
            print(page.icon)  # 图标
            print(page.page_cover)  # 页面封面
            print(page.page_setting)  # 页面设置
            ```
        """
        result = self._request("GET", f"/v1/blocks/{page_id}")
        block_data = result.get("data", {})
        block = self._parse_block(block_data)

        # 确保返回的是Page对象
        if isinstance(block, Page):
            # 设置客户端引用，以便后续使用 update 方法
            block._client = self
            return block
        else:
            raise ValueError(f"指定的ID不是页面类型，而是 {block.type} 类型")

    def get_block(self, block_id: str) -> Block:
        """
        查询块详情

        Args:
            block_id (`str`): 块的ID

        Returns:
            `Block`: 块对象

        示例:
            ```python
            block = client.get_block("block_id")
            print(block.content)
            ```
        """
        result = self._request("GET", f"/v1/blocks/{block_id}")
        block_data = result.get("data", {})
        return self._parse_block(block_data)

    def create_block(
        self,
        parent_id: str,
        blocks: List[Dict[str, Any]],
    ) -> List[Block]:
        """
        创建块

        参考: https://www.wolai.com/wolai/oyKuZbAmufkA3r7ocrBxW2

        Args:
            parent_id (`str`): 父块ID（必须是有效的 UUID 格式）
            blocks (`list[dict]`): 要创建的块列表，每个块需要指定type和content

        Returns:
            `list[Block]`: 创建的块对象列表

        示例:
            ```python
            blocks = client.create_block(
                parent_id="有效的UUID格式的父块ID",
                blocks=[
                    {
                        "type": "text",
                        "content": "Hello, Wolai!",
                        "text_alignment": "center"
                    },
                    {
                        "type": "heading",
                        "level": 1,
                        "content": {
                            "title": "标题",
                            "front_color": "red"
                        },
                        "text_alignment": "center"
                    }
                ]
            )
            ```
        """
        data = {"parent_id": parent_id, "blocks": blocks}
        try:
            result = self._request("POST", "/v1/blocks", data=data)
            created_blocks = result.get("data", {}).get("blocks", [])
            return [self._parse_block(block_data) for block_data in created_blocks]
        except Exception as e:
            error_msg = str(e)
            if "UUID" in error_msg or "uuid" in error_msg.lower():
                raise Exception(
                    f"创建块失败: {error_msg}\n"
                    f"提示: parent_id '{parent_id}' 不是有效的 UUID 格式。\n"
                    "请使用有效的 UUID 作为父块ID，例如通过 client.get_page() 或 client.get_block() 获取的块ID。"
                )
            raise

    def create_text_block(
        self,
        parent_id: str,
        content: str,
        text_alignment: str = "left",
    ) -> Block:
        """
        创建文本块

        Args:
            parent_id (`str`): 父块ID
            content (`str`): 文本内容
            text_alignment (`str`): 文本对齐方式 (left, center, right)

        Returns:
            `Block`: 创建的文本块对象
        """
        blocks = [
            {
                "type": "text",
                "content": content,
                "text_alignment": text_alignment,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_heading_block(
        self,
        parent_id: str,
        content: Union[str, Dict[str, Any]],
        level: int = 1,
        text_alignment: str = "left",
    ) -> Block:
        """
        创建标题块

        Args:
            parent_id (`str`): 父块ID
            content (`str` | `dict`): 标题内容，可以是字符串或包含title和front_color的字典
            level (`int`): 标题级别 (1-6)
            text_alignment (`str`): 文本对齐方式 (left, center, right)

        Returns:
            `Block`: 创建的标题块对象
        """
        if isinstance(content, str):
            content_dict = {"title": content}
        else:
            content_dict = content

        blocks = [
            {
                "type": "heading",
                "level": level,
                "content": content_dict,
                "text_alignment": text_alignment,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_todo_block(
        self,
        parent_id: str,
        content: str,
        checked: bool = False,
    ) -> Block:
        """
        创建待办块

        Args:
            parent_id (`str`): 父块ID
            content (`str`): 待办内容
            checked (`bool`): 是否已完成

        Returns:
            `Block`: 创建的待办块对象
        """
        blocks = [
            {
                "type": "todo_list",
                "content": content,
                "checked": checked,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_bull_list_block(
        self,
        parent_id: str,
        content: str,
    ) -> Block:
        """
        创建无序列表块

        Args:
            parent_id (`str`): 父块ID
            content (`str`): 列表项内容

        Returns:
            `Block`: 创建的无序列表块对象
        """
        blocks = [
            {
                "type": "bull_list",
                "content": content,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_enum_list_block(
        self,
        parent_id: str,
        content: str,
    ) -> Block:
        """
        创建有序列表块

        Args:
            parent_id (`str`): 父块ID
            content (`str`): 列表项内容

        Returns:
            `Block`: 创建的有序列表块对象
        """
        blocks = [
            {
                "type": "enum_list",
                "content": content,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_code_block(
        self,
        parent_id: str,
        content: str,
        language: str = "",
    ) -> Block:
        """
        创建代码块

        Args:
            parent_id (`str`): 父块ID
            content (`str`): 代码内容
            language (`str`): 编程语言

        Returns:
            `Block`: 创建的代码块对象
        """
        blocks = [
            {
                "type": "code",
                "content": content,
                "language": language,
            }
        ]
        result = self.create_block(parent_id, blocks)
        return result[0] if result else None

    def create_page_block(
        self,
        parent_id: str,
        content: Optional[Union[str, List[Dict[str, Any]]]] = None,
        icon: Optional[Dict[str, Any]] = None,
        page_cover: Optional[Dict[str, Any]] = None,
        page_setting: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """
        创建页面块

        Args:
            parent_id (`str`): 父块ID（必须是有效的 UUID 格式）
            content (`str` | `list[dict]`): 页面标题（CreateRichText格式），可选
            icon (`dict`): 图标（LinkIcon 或 EmojiIcon），可选
            page_cover (`dict`): 页面封面（LinkCover），可选
            page_setting (`dict`): 页面设置（PageSetting），可选

        Returns:
            `Page`: 创建的页面块对象

        示例:
            ```python
            # 创建简单页面
            page = client.create_page_block(
                parent_id="有效的UUID格式的父块ID",
                content="页面标题"
            )

            # 创建带图标和封面的页面
            page = client.create_page_block(
                parent_id="有效的UUID格式的父块ID",
                content=[{"title": "页面标题", "type": "text"}],
                icon={"type": "emoji", "emoji": "📄"},
                page_cover={"type": "link", "url": "https://example.com/image.jpg"},
                page_setting={"font_family": "kaiti"}
            )
            ```
        """
        block_data = {
            "type": "page",
        }
        if content is not None:
            block_data["content"] = content
        if icon is not None:
            block_data["icon"] = icon
        if page_cover is not None:
            block_data["page_cover"] = page_cover
        if page_setting is not None:
            block_data["page_setting"] = page_setting

        blocks = [block_data]
        result = self.create_block(parent_id, blocks)
        created_block = result[0] if result else None

        # 确保返回的是Page对象
        if isinstance(created_block, Page):
            return created_block
        elif created_block and created_block.type == "page":
            # 如果解析出来不是Page对象，重新解析为Page
            return Page(
                block_id=created_block.id,
                parent_id=created_block.parent_id,
                page_id=created_block.page_id,
                parent_type=created_block.parent_type,
                content=created_block.content,
                children=created_block.children,
                icon=icon,
                page_cover=page_cover,
                page_setting=page_setting,
            )
        else:
            raise ValueError("创建页面块失败")

    # ==================== 数据库操作接口 ====================

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """
        获取数据库数据

        Args:
            database_id (`str`): 数据库ID

        Returns:
            `dict`: 数据库数据，包含column_order和rows

        示例:
            ```python
            database = client.get_database("database_id")
            rows = database.get("rows", [])
            for row in rows:
                print(row.get("page_id"))
                print(row.get("data"))
            ```
        """
        result = self._request("GET", f"/v1/databases/{database_id}")
        return result.get("data", {})

    def get_database_rows(self, database_id: str) -> List[Dict[str, Any]]:
        """
        获取数据库的所有行数据

        Args:
            database_id (`str`): 数据库ID

        Returns:
            `list[dict]`: 行数据列表，每个元素包含page_id和data字段

        示例:
            ```python
            rows = client.get_database_rows("database_id")
            for row in rows:
                page_id = row.get("page_id")
                data = row.get("data", {})
                title = data.get("标题", {}).get("value", "")
                print(f"{page_id}: {title}")
            ```
        """
        database = self.get_database(database_id)
        return database.get("rows", [])

    def add_database_rows(
        self,
        database_id: str,
        rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        向数据库添加记录

        Args:
            database_id (`str`): 数据库ID
            rows (`list[dict]`): 要添加的记录列表，每个记录是一个字典

        Returns:
            `dict`: API响应数据

        示例:
            ```python
            client.add_database_rows(
                "database_id",
                rows=[
                    {
                        "标题": {
                            "type": "primary",
                            "value": "新任务"
                        },
                        "标签": {
                            "type": "select",
                            "value": "待完成"
                        }
                    }
                ]
            )
            ```
        """
        data = {"rows": rows}
        result = self._request("POST", f"/v1/databases/{database_id}/rows", data=data)
        return result.get("data", {})
