# nonebot-plugin-image-summary

<p><img src="https://img.shields.io/badge/NoneBot-v2-red.svg"> <img src="https://img.shields.io/badge/python-3.8+-blue.svg"> <img src="https://img.shields.io/badge/plugin-nonebot_plugin_image_summary-yellow.svg"></p> </div>

# 📖 简介
NoneBot2 图片外显更改

这是一个能够拦截Nonebot2发送的所有图片消息，并自动在图片下方注入 summary（外显）字段的插件。

支持API 获取和本地文案两种模式，且拥有群白名单管理机制。

# 💿 安装
1.使用nb安装
```
#进入你的nb文件夹
nb plugin install nonebot-plugin-image-summary
```
2.手动clone
```
cd path/to/your/site-packages
git clone https://github.com/TZJackZ2B9S/nonebot_plugin_image_summary.git
#网络环境差请自行使用加速站
```
确保目录结构正确：
```
lib/python3.11/site-packages/nonebot_plugin_image_summary/
├── __init__.py
├── config.py
└── data_manager.py
```


并且到`pyproject.toml`中添加代码
```
plugins =["nonebot_plugin_image_summary"]
```
# ⚙️ 配置
在 `.env` 或 `.env.prod` 中添加以下配置（可选）：

 配置项 | 类型 | 默认值 | 说明
 ----- | ---- | ---- | ----
 IMAGE_SUMMARY_APIS | List[str] | (见下方) | 获取外显文案的 API 列表，插件会随机抽取一个请求。
 IMAGE_SUMMARY_DEBUG | bool | False | 是否开启调试模式，开启后控制台会输出详细的 API 请求和注入日志。

默认 API 列表：
```
[
  "https://v1.hitokoto.cn/?encode=text",
  "https://api.shadiao.pro/du",
  "https://api.shadiao.pro/chp"
]
```
# 🎮 使用指令
以下指令仅 **超级用户** 或 **群主**  可用。

指令 | 格式 | 说明
---- | ---- | ----
开启外显| `开启外显 [群号]` | 开启当前群（或指定群）的图片外显功能。
关闭外显 |`关闭外显 [群号]`|关闭当前群（或指定群）的图片外显功能。
切换外显源|`切换外显源`|在 `local` (本地库) 和 `api` (网络接口) 模式之间切换。
外显列表|`外显列表`|查看当前模式及本地文案库的前 50 条预览。
添加外显|`添加外显 <内容>`|向本地文案库添加一条新内容。
删除外显|`删除外显 <内容>`|从本地文案库删除指定内容。

**提示**：插件默认对所有群关闭，必须手动开启才会生效。

# 📂 数据存储

插件的数据（白名单群号、本地文案、当前模式）保存在机器人运行目录下的： `data/image_summary/data.json`

你可以手动编辑该文件，修改后无需重启，下一次指令调用或消息发送时会自动读取最新数据。

# 特别感谢
[astrbot_plugin_image_summary](https://github.com/Zhalslar/astrbot_plugin_image_summary)

