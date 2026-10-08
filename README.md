<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ nonebot-plugin-yukikaze ✨
[![LICENSE](https://img.shields.io/github/license/hyouryo/nonebot-plugin-yukikaze.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-yukikaze.svg)](https://pypi.python.org/pypi/nonebot-plugin-yukikaze)
[![python](https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/package%20manager-uv-black?style=flat-square&logo=uv)](https://github.com/astral-sh/uv)
<br/>
[![ruff](https://img.shields.io/badge/code%20style-ruff-black?style=flat-square&logo=ruff)](https://github.com/astral-sh/ruff)
[![pre-commit](https://results.pre-commit.ci/badge/github/hyouryo/nonebot-plugin-yukikaze/master.svg)](https://results.pre-commit.ci/latest/github/hyouryo/nonebot-plugin-yukikaze/master)

</div>

## 📖 介绍

自用的雪风机器人，把几个常用小功能打包成一个插件：

| 功能 | 说明 |
| :--- | :--- |
| `poke` | 被戳一戳时回一张随机表情包 |
| `get_song` | 点歌，发网易云音乐卡片 |
| `no_talking_laughing` | 有人被禁言时随机说一句风凉话 |

每个功能都是独立的**子插件**，可以通过配置项单独开关，也可以在
`雪风帮助` 里看到当前启用了哪些。

> ⚠️ 三个功能都基于 OneBot v11 的扩展事件（`PokeNotifyEvent` /
> `GroupBanNoticeEvent` / 自定义音乐卡片），因此**只支持 OneBot v11**
> （如 Lagrange、NapCat 等）。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-yukikaze --upgrade
使用 **pypi** 源安装

    nb plugin install nonebot-plugin-yukikaze --upgrade -i "https://pypi.org/simple"
使用**清华源**安装

    nb plugin install nonebot-plugin-yukikaze --upgrade -i "https://pypi.tuna.tsinghua.edu.cn/simple"


</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details open>
<summary>uv</summary>

    uv add nonebot-plugin-yukikaze
安装仓库 master 分支

    uv add git+https://github.com/hyouryo/nonebot-plugin-yukikaze@master
</details>

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-yukikaze
安装仓库 master 分支

    pdm add git+https://github.com/hyouryo/nonebot-plugin-yukikaze@master
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-yukikaze
安装仓库 master 分支

    poetry add git+https://github.com/hyouryo/nonebot-plugin-yukikaze@master
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_yukikaze"]

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加下表中的配置项。
**配置名就是字段名的大写形式**，全部可选。

| 配置项 | 必填 | 默认值 | 说明 |
| :--- | :---: | :---: | :--- |
| `YUKIKAZE_POKE_ENABLED` | 否 | `true` | 是否启用戳一戳回图 |
| `YUKIKAZE_SONG_ENABLED` | 否 | `true` | 是否启用点歌 |
| `YUKIKAZE_NO_TALKING_LAUGHING_ENABLED` | 否 | `true` | 是否启用禁言播报 |
| `YUKIKAZE_SONG_LEVEL` | 否 | `exhigh` | 点歌音质，可选 `standard`/`higher`/`exhigh`/`lossless`/`hires`/`sky` |
| `YUKIKAZE_SONG_COOKIE` | 否 | 空 | 网易云 cookie（`MUSIC_U=...`）。留空为匿名，只能取到无需会员的歌曲 |
| `YUKIKAZE_NO_TALKING_LAUGHING_TEXTS` | 否 | 空 | 禁言播报的文案，JSON 数组，如 `["哈哈","笑死"]`。留空用内置 4 条 |

例如只保留点歌、并且用无损音质：

```dotenv
YUKIKAZE_POKE_ENABLED=false
YUKIKAZE_NO_TALKING_LAUGHING_ENABLED=false
YUKIKAZE_SONG_LEVEL=lossless
```

## 🎉 使用

### 指令表

| 指令 | 权限 | 需要@ | 范围 | 说明 |
| :--- | :---: | :---: | :---: | :--- |
| `雪风帮助` / `帮助` | 群员 | 否 | 群聊/私聊 | 列出当前已启用的功能 |
| `点歌 <歌曲名>` | 群员 | 否 | 群聊/私聊 | 搜索并发送网易云音乐卡片 |
| 戳一戳机器人 | 群员 | 是 | 群聊/私聊 | 回一张随机表情包（需 @ 或私聊） |
| 群成员被禁言 | — | 是 | 群聊 | 自动播报一句风凉话（需 @ 或私聊） |

### 🎨 效果图
点歌会发送自定义音乐卡片；戳一戳回复 `plugins/poke/src/gif/` 下的表情包。
