---
name: mianshiya-to-feishu
description: 整理面试鸭(mianshiya.com)的面试题并生成飞书云文档。接收一个面试鸭题目链接，用浏览器打开页面、提取问答内容、下载配图、在指定飞书知识库目录下为每道题创建一个结构化文档。当用户给出面试鸭链接并要求整理、保存、生成飞书文档时使用。
---

# 面试鸭题目整理 → 飞书文档

将面试鸭单道题目页面整理为结构化飞书云文档，包含题目、回答重点、扩展知识、面试官追问及配图。

## 前置条件

- 用户已在浏览器中登录面试鸭账号（未登录时答案会被截断）
- 飞书知识库目标目录可访问（默认目录见下方配置）

## 关键约束（必须遵守）

- **禁止任何爬取行为**：不使用 web.fetch、HTTP 请求、批量抓取等方式获取内容。只通过浏览器正常操作（打开页面、滚动、复制可见文本、下载图片）获取信息。用户曾因爬取被封号。
- **操作模拟正常用户**：每次滚动/点击后等待 1-2 秒，不快速连续操作。
- **每道题一个文档**：一个面试鸭链接对应一道题，在知识库目录下新建一个 docx 文档。
- **图片必须左对齐**：插入图片后设置为左对齐（非默认居中）。

## 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 飞书知识库目录 node_token | `QWGhwS63ziWXEokQWIxcJkREnzb` | "AI Agent 面试题"目录，可被用户指定的其他目录覆盖 |
| 飞书知识库 space_id | `7474514940640985091` | 上述目录所属知识空间 |

## 执行流程

### Step 1：浏览器打开页面

使用 `mac_computer_use_tool`（plane=`bu`）操作浏览器：

```python
import seed_browser_use as bu
bu.resync()  # 同步到当前标签页
bu.navigate("<面试鸭链接>")
bu.wait_for_load()
time.sleep(2)
```

如果弹出登录弹窗，用 `bu.find("Close")` 找到关闭按钮并点击。

### Step 2：验证登录状态

用 `bu.get_page_text()` 获取页面文本，检查：
- 不存在"点击登录查看完整内容"按钮
- 存在"隐藏答案"按钮（说明答案已展开）

如果未登录，提示用户先登录后再继续。

### Step 3：提取页面文本

```python
text = bu.get_page_text()
# 保存到工作目录的临时文件
with open("<workspace>/raw_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### Step 4：识别并下载配图

用 `bu.read_all("img", fields=["src", "alt"], limit=30)` 获取页面所有图片。

筛选正文配图（排除 logo、头像、等级图标等）：
- 正文配图域名通常为 `pic.code-nav.cn`，路径含 `question_picture`
- 记录每张配图的 URL 和在页面中的位置（回答重点后 / 某个扩展知识小节后）

用浏览器正常下载功能下载图片：

```python
record = bu.download(img_url, filename="img1.webp")
# record["path"] 为下载路径（通常在 ~/Downloads/）
```

将 webp 转为 png（飞书文档对 webp 支持不完善）：

```bash
sips -s format png input.webp --out output.png
```

获取图片尺寸：`sips -g pixelWidth -g pixelHeight output.png`

将图片复制到当前工作目录的 `images/` 子目录下。

### Step 5：整理内容为结构化 Markdown

从原始文本中提取以下部分，组织为 Markdown：

```markdown
# <题目标题>

> 题目编号：<编号> | 难度：<难度> | 标签：<标签1>、<标签2>
> 来源：[面试鸭](<原始链接>)

---

## 回答重点
<回答重点正文>

## 扩展知识
### <扩展知识小节标题1>
<内容>
### <扩展知识小节标题2>
<内容>

## 面试官追问
### 提问：<追问问题1>
回答：<回答内容>
### 提问：<追问问题2>
回答：<回答内容>
```

内容提取规则：
- 题目编号：页面中形如 `13557.` 的编号
- 难度：编号下方的"简单"/"中等"/"困难"
- 标签：难度下方的标签词
- 回答重点：从"回答重点"到"扩展知识"之间
- 扩展知识：从"扩展知识"到"面试官追问"之间，按 `###` 子标题拆分
- 面试官追问：从"面试官追问"到"作者"或"上一题"之间，每个"提问："开头为一个追问

将 Markdown 保存到工作目录，文件名如 `question_<编号>.md`。

### Step 6：创建飞书文档

在工作目录下执行：

```bash
lark-cli docs +create \
  --doc-format markdown \
  --content "@./question_<编号>.md" \
  --parent-token "<知识库目录node_token>" \
  --as user \
  --format json
```

从返回值中记录 `document_id` 和 `url`。

### Step 7：插入配图（左对齐）

图片插入使用 `docs +media-insert`（支持 `--align left`），插入到文末后再移动到目标位置：

1. 插入图片到文末：
```bash
lark-cli docs +media-insert \
  --doc "<document_id>" \
  --file "./images/<图片文件名>.png" \
  --align left \
  --width 800 \
  --caption "<图片说明>" \
  --as user --format json
```
记录返回的 `block_id`。

2. 用 `docs +fetch --scope keyword --detail with-ids` 定位目标位置的 block_id（如"扩展知识"标题、某小节最后一段）。

3. 移动图片到目标位置：
```bash
lark-cli docs +update \
  --doc "<document_id>" \
  --command block_move_after \
  --block-id "<目标anchor block_id>" \
  --src-block-ids "<图片block_id>" \
  --as user --format json
```

配图位置规则：
- "AI Agent 与直接调用大模型 API 的区别"类对比图 → 回答重点之后、扩展知识之前
- 演进路径/流程图 → 对应扩展知识小节的文字之后

### Step 8：验证

1. `lark-cli wiki +node-list --parent-node-token <目录node_token>` 确认文档已创建在正确目录下
2. `lark-cli docs +fetch --doc <document_id> --doc-format markdown` 回读验证内容完整
3. 检查图片块是否存在且位置正确

### Step 9：交付

通过 `present_files` 交付飞书文档链接。如果用户要求截图，同时交付滚动截图。

## 可选：滚动截图

如果用户要求保存网页截图：

1. 回到页面顶部：`bu.js("window.scrollTo(0, 0)")`
2. 逐屏滚动截图，每次截图后立即复制到工作目录（`bu.screenshot()` 返回的路径会被下一次覆盖）
3. 每屏之间等待 1.5 秒

```python
import shutil
for i in range(1, max_screens+1):
    shot = bu.screenshot()
    shutil.copy2(shot.path, f"<output_dir>/page_{i}.png")
    bu.scroll(500, 500, "down", amount=3)
    time.sleep(1.5)
```

## 故障排查

| 问题 | 原因 | 处理 |
|------|------|------|
| 页面重定向到 404 "Not allowed" | Playwright 被反爬检测 | 必须使用 `mac_computer_use_tool` 的真实 Chrome，不使用 Playwright |
| 答案内容被截断 | 未登录 | 提示用户在浏览器中登录面试鸭 |
| 图片插入后不显示 | webp 格式不兼容 | 转换为 png 后再插入 |
| 图片 URL 插入报错 "local/internal host" | 飞书不接受该域名的远程图片 | 先下载到本地，用 `path` 方式插入 |
| `bu.js()` 返回空对象 | 返回值序列化问题 | 改用 `bu.get_page_text()` 或 `bu.read_all()` 获取信息 |

## 相关 Skill

- 浏览器操作：`browser-use-automation-mac`
- 飞书文档创建/编辑：`lark-doc`
- 飞书知识库节点管理：`lark-wiki`
