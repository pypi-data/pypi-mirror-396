import sys

sys.path.append("..")
from wolai import WolaiClient

client = WolaiClient(
    token="54e3f0800e2496ba12ff68a29c888601c8d2864ca81a1c6d7ee6a55a4b49070c"
)

# styled_page = client.create_page_block(
#     parent_id="nKEg7pLmpn45GJAZspxDhb",
#     content=[{"title": "【202512113】记录", "type": "text"}],
#     icon={"type": "emoji", "emoji": "📄"},
#     page_cover={
#         "type": "link",
#         "url": "https://haowallpaper.com/link/common/file/previewFileImg/18037414194433408",
#     },
#     page_setting={"font_family": "kaiti"},
# )

result = client.add_database_rows(
    "nKEg7pLmpn45GJAZspxDhb",
    rows=[
        {
            "标题": "【20251214】记录",
            "起床时间": "2025-12-14 07:31",
            "睡觉时间": "2025-12-14 23:10",
            "作息符合预期": "干得漂亮",
            "总结": "效率比较低，不太符合预期",
            "关键词": "准备期末考试,保研人讲课",
            "记录": "",
            "周报": "【20251208-20251216】记录",
        }
    ],
)
