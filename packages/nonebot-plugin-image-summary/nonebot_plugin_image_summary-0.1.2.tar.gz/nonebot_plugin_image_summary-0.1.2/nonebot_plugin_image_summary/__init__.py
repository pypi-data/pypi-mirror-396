import random
import aiohttp
from typing import Dict, Any, Annotated

from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

from .config import Config
from .data_manager import data_manager

__version__ = "0.1.2"

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_image_summary",
    description="图片外显管理插件，拦截所有图片消息并注入summary",
    usage="开启/关闭外显，添加/删除外显，切换外显源",
    type="application",
    homepage="https://github.com/TZJackZ2B9S/nonebot_plugin_image_summary",
    config=Config,
)

config = get_plugin_config(Config)

async def get_api_quote() -> str:
    """从配置的API列表获取文案，失败则回退到本地"""
    urls = config.image_summary_apis
    if not urls:
        return random.choice(data_manager.get_local_quotes())
    
    # 随机打乱尝试
    shuffled_urls = random.sample(urls, len(urls))
    
    async with aiohttp.ClientSession() as session:
        for url in shuffled_urls:
            try:
                if config.image_summary_debug:
                    logger.debug(f"[ImageSummary] Requesting: {url}")
                    
                async with session.get(url, timeout=5) as resp:
                    if resp.status != 200:
                        continue
                    
                    ctype = resp.headers.get("Content-Type", "").lower()
                    text = ""
                    
                    if "application/json" in ctype:
                        data = await resp.json()
                        # 尝试常见字段
                        text = data.get("content") or data.get("text") or data.get("msg") or data.get("hitokoto")
                    elif "text" in ctype:
                        text = await resp.text()
                        
                    if text and isinstance(text, str) and text.strip():
                        return text.strip()[:50] # 限制长度防止刷屏
            except Exception as e:
                if config.image_summary_debug:
                    logger.warning(f"[ImageSummary] API Error {url}: {e}")
                continue
    
    if config.image_summary_debug:
        logger.warning("[ImageSummary] All APIs failed, using local quote.")
    return random.choice(data_manager.get_local_quotes())

async def get_final_quote() -> str:
    """根据当前模式获取文案"""
    mode = data_manager.get_source_mode()
    quote = ""
    if mode == "api":
        quote = await get_api_quote()
    
    # 如果API模式获取失败，或者处于local模式，从本地取
    if not quote:
        quotes = data_manager.get_local_quotes()
        quote = random.choice(quotes) if quotes else "Image"
    
    return quote

@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: Dict[str, Any]):
    """
    拦截 OneBot API 调用。
    如果是发送群消息且包含图片，检查白名单并注入 summary。
    """
    if api not in ["send_group_msg", "send_msg"]:
        return

    # 1. 获取群号
    group_id = data.get("group_id")
    if not group_id:
        return # 忽略私聊或未知来源
    
    # 2. 检查白名单 (默认全部关闭，只有在白名单才开启)
    if not data_manager.is_group_enabled(int(group_id)):
        return

    # 3. 解析消息内容
    message = data.get("message")
    if not message:
        return

    # 将消息统一转换为 list[dict] 格式以便处理
    segments = []
    if isinstance(message, str):
        # 纯文本不需要处理
        return
    elif isinstance(message, list):
        segments = message
    elif isinstance(message, Message):
        segments = list(message)
    else:
        return

    # 4. 遍历消息段，查找图片并注入 summary
    has_modified = False
    quote = None # 懒加载，只有发现图片才获取

    for seg in segments:
        # 兼容 MessageSegment 对象和 dict
        seg_type = seg.type if hasattr(seg, "type") else seg.get("type")
        
        if seg_type == "image":
            if not quote:
                quote = await get_final_quote()
            
            # 修改数据
            if hasattr(seg, "data"):
                seg.data["summary"] = quote
            else:
                # 字典情况
                if "data" not in seg:
                    seg["data"] = {}
                seg["data"]["summary"] = quote
            
            has_modified = True

            if config.image_summary_debug:
                logger.debug(f"[ImageSummary] Injected summary: '{quote}' for Group({group_id})")

# 权限控制：仅群主或超管可用
PERM = SUPERUSER | GROUP_OWNER

cmd_toggle = on_command("开启外显", aliases={"关闭外显"}, permission=PERM, priority=10, block=True)
cmd_add = on_command("添加外显", permission=PERM, priority=10, block=True)
cmd_del = on_command("删除外显", permission=PERM, priority=10, block=True)
cmd_list = on_command("外显列表", permission=PERM, priority=10, block=True)
cmd_switch = on_command("切换外显源", permission=PERM, priority=10, block=True)

# 使用 Annotated[Message, CommandArg()] 是最标准的写法，可以避免之前的类型错误
@cmd_toggle.handle()
async def _(event: GroupMessageEvent, args: Annotated[Message, CommandArg()]):
    """开启/关闭外显 [群号/全部]"""
    # 获取原始指令判断是开启还是关闭
    raw_cmd = event.get_plaintext().split()[0]
    is_enable = "开启" in raw_cmd
    
    target = args.extract_plain_text().strip()
    group_id = event.group_id

    if target == "全部" and str(event.user_id) in event.get_session_id(): 
        pass 

    if target.isdigit():
        group_id = int(target)
    
    data_manager.set_group_state(group_id, is_enable)
    status = "开启" if is_enable else "关闭"
    await cmd_toggle.finish(f"已{status}群 {group_id} 的图片外显。")

@cmd_add.handle()
async def _(args: Annotated[Message, CommandArg()]):
    text = args.extract_plain_text().strip()
    if not text:
        await cmd_add.finish("请提供要添加的文字。")
    
    data_manager.add_quote(text)
    await cmd_add.finish(f"已添加本地外显：{text}")

@cmd_del.handle()
async def _(args: Annotated[Message, CommandArg()]):
    text = args.extract_plain_text().strip()
    if not text:
        await cmd_del.finish("请提供要删除的文字。")
    
    if data_manager.remove_quote(text):
        await cmd_del.finish(f"已删除：{text}")
    else:
        await cmd_del.finish("未找到该文案。")

@cmd_list.handle()
async def _():
    quotes = data_manager.get_local_quotes()
    mode = data_manager.get_source_mode()
    msg = f"当前模式：{mode}\n本地文案库（{len(quotes)}条）：\n"
    # 防止列表过长
    preview = "\n".join(quotes[:50])
    if len(quotes) > 50:
        preview += f"\n...还有 {len(quotes)-50} 条"
    await cmd_list.finish(msg + preview)

@cmd_switch.handle()
async def _():
    current = data_manager.get_source_mode()
    new_mode = "api" if current == "local" else "local"
    data_manager.set_source_mode(new_mode)
    await cmd_switch.finish(f"外显源已切换为：{new_mode}")
