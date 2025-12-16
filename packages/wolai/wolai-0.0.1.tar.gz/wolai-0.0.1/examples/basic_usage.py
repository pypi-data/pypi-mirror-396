# -*- coding: utf-8 -*-

"""
Wolai Python SDK 基础使用示例
"""

from wolai import WolaiClient

# 初始化客户端
# 请替换为你的 API Token
TOKEN = "your_api_token_here"
client = WolaiClient(token=TOKEN)

# ==================== 块操作示例 ====================

# 1. 查询页面详情
print("=" * 50)
print("1. 查询页面详情")
print("=" * 50)
try:
    page = client.get_page("page_id_here")
    print(f"页面ID: {page.id}")
    print(f"页面类型: {page.type}")
    print(f"页面标题: {page.content}")
    print(f"页面图标: {page.icon}")
    print(f"页面封面: {page.page_cover}")
    print(f"页面设置: {page.page_setting}")
except Exception as e:
    print(f"查询失败: {e}")

# 1.1 查询块详情
print("\n" + "=" * 50)
print("1.1 查询块详情")
print("=" * 50)
try:
    block = client.get_block("block_id_here")
    print(f"块ID: {block.id}")
    print(f"块类型: {block.type}")
    print(f"块内容: {block.content}")
except Exception as e:
    print(f"查询失败: {e}")

# 2. 创建文本块
print("\n" + "=" * 50)
print("2. 创建文本块")
print("=" * 50)
try:
    text_block = client.create_text_block(
        parent_id="parent_block_id_here",
        content="这是一个文本块",
        text_alignment="left",
    )
    print(f"创建的文本块ID: {text_block.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 3. 创建标题块
print("\n" + "=" * 50)
print("3. 创建标题块")
print("=" * 50)
try:
    heading_block = client.create_heading_block(
        parent_id="parent_block_id_here",
        content="这是一级标题",
        level=1,
    )
    print(f"创建的标题块ID: {heading_block.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 4. 创建带样式的标题块
print("\n" + "=" * 50)
print("4. 创建带样式的标题块")
print("=" * 50)
try:
    styled_heading = client.create_heading_block(
        parent_id="parent_block_id_here",
        content={
            "title": "带颜色的标题",
            "front_color": "red",
        },
        level=2,
        text_alignment="center",
    )
    print(f"创建的标题块ID: {styled_heading.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 5. 创建待办块
print("\n" + "=" * 50)
print("5. 创建待办块")
print("=" * 50)
try:
    todo_block = client.create_todo_block(
        parent_id="parent_block_id_here",
        content="完成这个任务",
        checked=False,
    )
    print(f"创建的待办块ID: {todo_block.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 6. 创建代码块
print("\n" + "=" * 50)
print("6. 创建代码块")
print("=" * 50)
try:
    code_block = client.create_code_block(
        parent_id="parent_block_id_here",
        content='print("Hello, Wolai!")',
        language="python",
    )
    print(f"创建的代码块ID: {code_block.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 7. 创建页面块
print("\n" + "=" * 50)
print("7. 创建页面块")
print("=" * 50)
try:
    # 创建简单页面
    page_block = client.create_page_block(
        parent_id="parent_block_id_here",
        content="新页面标题",
    )
    print(f"创建的页面块ID: {page_block.id}")

    # 创建带图标和封面的页面
    styled_page = client.create_page_block(
        parent_id="parent_block_id_here",
        content="带样式的页面",
        icon={"type": "emoji", "emoji": "📄"},
        page_cover={"type": "external", "url": "https://example.com/image.jpg"},
    )
    print(f"创建的样式页面块ID: {styled_page.id}")
except Exception as e:
    print(f"创建失败: {e}")

# 8. 批量创建块
print("\n" + "=" * 50)
print("8. 批量创建块")
print("=" * 50)
try:
    blocks = client.create_block(
        parent_id="parent_block_id_here",
        blocks=[
            {
                "type": "text",
                "content": "第一段文本",
            },
            {
                "type": "heading",
                "level": 1,
                "content": {
                    "title": "标题",
                    "front_color": "blue",
                },
            },
            {
                "type": "todo_list",
                "content": "待办事项",
                "checked": False,
            },
        ],
    )
    print(f"成功创建 {len(blocks)} 个块")
    for block in blocks:
        print(f"  - {block.type}: {block.id}")
except Exception as e:
    print(f"创建失败: {e}")

# ==================== 数据库操作示例 ====================

# 9. 获取数据库数据
print("\n" + "=" * 50)
print("9. 获取数据库数据")
print("=" * 50)
try:
    database = client.get_database("database_id_here")
    column_order = database.get("column_order", [])
    rows = database.get("rows", [])
    print(f"数据库列: {column_order}")
    print(f"数据库行数: {len(rows)}")
except Exception as e:
    print(f"查询失败: {e}")

# 9. 获取数据库行数据
print("\n" + "=" * 50)
print("9. 获取数据库行数据")
print("=" * 50)
try:
    rows = client.get_database_rows("database_id_here")
    print(f"共 {len(rows)} 行数据")
    for i, row in enumerate(rows[:3], 1):  # 只显示前3行
        page_id = row.get("page_id", "")
        data = row.get("data", {})
        print(f"\n第 {i} 行:")
        print(f"  页面ID: {page_id}")
        print(f"  数据: {data}")
except Exception as e:
    print(f"查询失败: {e}")

# 11. 添加数据库记录
print("\n" + "=" * 50)
print("11. 添加数据库记录")
print("=" * 50)
try:
    result = client.add_database_rows(
        "database_id_here",
        rows=[
            {
                "标题": {
                    "type": "primary",
                    "value": "新任务",
                },
                "标签": {
                    "type": "select",
                    "value": "待完成",
                },
            }
        ],
    )
    print(f"添加成功: {result}")
except Exception as e:
    print(f"添加失败: {e}")

print("\n" + "=" * 50)
print("示例完成！")
print("=" * 50)
