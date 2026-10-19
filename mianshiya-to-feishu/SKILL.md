---
name: mianshiya-to-feishu
description: 整理面试鸭(mianshiya.com)的面试题并生成飞书云文档。接收一个面试鸭题目链接，用浏览器打开页面、提取问答内容、下载配图、在指定飞书知识库目录下为每道题创建一个结构化文档。当用户给出面试鸭链接并要求整理、保存、生成飞书文档时使用。浏览器层环境无关，按「浏览器适配层」选择当前环境的实现。
---

# 面试鸭题目整理 → 飞书文档

将面试鸭单道题目页面整理为结构化飞书云文档，包含题目、回答重点、扩展知识、面试官追问（如有）及配图（如有）。

本 skill 的流程与飞书操作是环境无关的；只有浏览器操作需要按「浏览器适配层」选择当前环境的实现。

## 前置条件

- 用户已在浏览器中登录面试鸭账号（未登录时答案会被截断）
- 当前环境可用 `lark-cli`（已登录，`--as user` 可用）
- 飞书知识库目标目录可访问（默认目录见下方配置）

## 关键约束（必须遵守，适用于所有环境）

- **禁止任何爬取行为**：不使用 web.fetch、HTTP 请求、curl、Playwright、无头浏览器、批量抓取等方式获取页面内容。只通过真实浏览器的正常操作（打开页面、滚动、复制可见文本、下载已显示的图片）获取信息。用户曾因爬取被封号。
- **只用真实浏览器**：必须使用带用户登录态的真实浏览器。若当前环境没有任何真实浏览器自动化工具，**停止并询问用户**，不得降级为 HTTP 请求或无头浏览器。
- **操作模拟正常用户**：每次滚动/点击后等待 1-2 秒，不快速连续操作。
- **每道题一个文档**：一个面试鸭链接对应一道题，在知识库目录下新建一个 docx 文档。
- **图片必须左对齐**：插入图片后设置为左对齐（非默认居中）。

## 浏览器适配层

本 skill 的浏览器操作只涉及以下 6 个原语，执行流程中的步骤均以原语指代：

| 原语 | 语义 |
|------|------|
| `open(url)` | 打开链接，等待加载完成后停顿约 2 秒 |
| `read_text()` | 获取页面可见文本 |
| `list_images()` | 获取页面所有 `<img>` 的 src/alt |
| `download(url)` | 下载单张已显示的正文配图到本地 |
| `run_js(expr)` | 在页面内执行一小段 JavaScript（如滚动） |
| `screenshot()` | 当前视口截图 |

按环境选择实现：

### 豆包工作（mac_computer_use_tool，plane=bu）

```python
import seed_browser_use as bu
import time, shutil

bu.resync()                      # 同步到当前标签页
bu.navigate("<面试鸭链接>")       # open()
bu.wait_for_load(); time.sleep(2)
text = bu.get_page_text()        # read_text()
imgs = bu.read_all("img", fields=["src", "alt"], limit=30)  # list_images()
record = bu.download(img_url, filename="img1.webp")          # download()，record["path"] 在 ~/Downloads/
bu.js("window.scrollTo(0, document.body.scrollHeight)")      # run_js()
shot = bu.screenshot()           # screenshot()，路径会被下一次截图覆盖，用完立即复制
```

相关 Skill：`browser-use-automation-mac`。

### ZCode / ego-browser（2026-10-19 实测可用）

通过 `ego-browser nodejs <<'EOF' ... EOF` 运行 ESM 脚本（Bash/Zsh heredoc）：

```js
const task = await taskSpace("mianshiya <题名>");   // 一个目标只用一个 space
const page = task.page("p1");
await page.goto("<面试鸭链接>");                    // open()
await page.waitForLoadState();
await page.waitForTimeout(2000);

const text = await page.evaluate(() => document.body.innerText);   // read_text()
const imgs = await page.evaluate(() =>                              // list_images()
  [...document.querySelectorAll("img")].map(n => ({ src: n.currentSrc || n.src, alt: n.alt })));
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));  // run_js()

const fs = await import("node:fs/promises");        // 脚本不在 shell cwd 运行，文件一律绝对路径
await fs.writeFile("/abs/path/raw_text.txt", text, "utf-8");
await page.screenshot({ path: "/abs/path/page_1.png" });  // screenshot()，path 必须绝对
// download()：对单张已显示的正文配图，在页面上下文保存（等同浏览器另存图片）：
await page.fetch(img_url, { saveAs: "/abs/path/images/img1.png" });
// 若下载由点击触发，则改为 arm 事件后点击：page.waitForEvent("download") + download.saveAs(绝对路径)

await task.finish({ keep: [] });                    // 全部完成后关闭，之后不得再操作任何 Page
```

详细用法以 `ego-browser skill` 的输出为准；`ego-browser upgrade` 后需重新执行该命令。

### 其他环境

把 6 个原语映射到当前环境的真实浏览器工具（映射方式参考上面两组），禁止映射到 HTTP 客户端、web.fetch 或 Playwright。无法确定是否存在真实浏览器工具时，停止并询问用户。

## 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 飞书知识库目录 node_token | `FI4lw1Tr7iCXhfkqjM4cg9nRngh` | "Spark 面试题"节点（当前默认，2026-10-19 起） |
| 备用目录 node_token | `QWGhwS63ziWXEokQWIxcJkREnzb` | "AI Agent 面试题"目录（原默认，豆包工作时期使用） |
| 飞书知识库 space_id | `7474514940640985091` | 上述两节点同属此知识空间 |

> 用户指定新目录时以 Step 0 的解析结果为准，不要沿用本表写死的 space_id。用户未指定目录时同样先走 Step 0 的提示流程，确认"用默认"后才使用本表默认值。

## 执行流程

### Step 0：确定目标目录

- 用户给出了飞书 wiki/docx 链接：先解析再使用，以解析结果覆盖配置表：

```bash
lark-cli wiki +node-get --node-token "<用户给的URL或token>" --as user --format json
```

从返回的 `data.space_id`、`data.node_token` 取值。目标节点既可以是目录，也可以是普通 docx 文档节点——两者都能作为 `--parent-token` 创建子节点。

- 用户未指定目录：**不要静默落到默认目录**，先向用户提示并给出建议，确认后再继续：
  1. 从题目标签推导建议目录名：`"<主标签> 面试题"`。优先取具体技术标签——如标签为"大数据、Spark"时建议 "Spark 面试题"，而不是 "大数据 面试题"。
  2. 在知识空间中查找是否已有同名节点（`wiki +node-list --space-id <space_id>` 从根节点逐层列出比对标题）。
  3. 已存在 → 提示"建议挂到已有节点 '<名称>'"；不存在 → 提示"建议新建 '<名称>' 节点"（`wiki +node-create`）。用户改指其他目录时回到上一分支重新解析。
  4. 仅当用户明确回复"用默认"时，才使用配置表的当前默认 node_token。

### Step 1：查重（已整理过则跳过）

1. 从面试鸭链接取出题目 id：路径 `question/<id>` 中的 `<id>`。
2. 用 Step 0 的 node_token 与 space_id 列出目标目录已有文档（节点列表含 `title` 与 `obj_token`）：

```bash
lark-cli wiki +node-list --space-id <space_id> --parent-node-token <node_token> --as user --format json
```

3. 目录为空 → 直接进入 Step 2。
4. 否则逐个回读子文档的“来源”行，比对题目 id（不开浏览器即可判定；已打开页面时，节点标题与题目标题完全一致也可直接判定）：

```bash
lark-cli docs +fetch --doc <obj_token> --as user --format json -q '.data.document.content' | grep -o 'question/[0-9]*'
```

5. 已存在同一道题 → 向用户提示"该题已整理过：<标题>（wiki 链接用 node_token 拼接）"，**跳过后续所有步骤**；仅当用户明确要求重新整理时才继续，并先与用户确认是删旧建新还是保留旧文档。

### Step 2：浏览器打开页面

`open(<面试鸭链接>)`。如果弹出登录弹窗，找到 Close 关闭按钮并点击。

### Step 3：验证登录状态

`read_text()` 获取页面文本，检查：
- 不存在"点击登录查看完整内容"按钮
- 存在"隐藏答案"按钮（说明答案已展开）

如果未登录，提示用户先登录后再继续。

### Step 4：提取页面文本与格式信息

`read_text()` 保存到工作目录 `raw_text.txt`。

纯文本会丢失三类格式信息，需再用 DOM 查询（ego-browser 用 `page.evaluate`）补齐：
- 行内代码：遍历正文 `code` 元素（排除 `pre` 内的代码块、评论区和 markdown 语法帮助浮层），记录每处代码及其所在句子的上下文
- 列表类型：遍历正文 `ol`/`ul`，记录每个列表的首项文本，用于还原有序/无序
- 小节标号：确认编号的准确字形（半角 `1)` 还是全角 `1）`、有无空格、末尾有无冒号）

### Step 5：识别并下载配图

1. `list_images()` 获取页面所有图片。
2. 筛选正文配图（排除 logo、头像、等级图标等）：正文配图域名通常为 `pic.code-nav.cn`，路径含 `question_picture`；记录每张配图的 URL 和在页面中的位置（回答重点后 / 某个扩展知识小节后）。
3. **若没有任何符合条件的配图（纯文字题很常见），判定为本题无配图，跳过 Step 8。**
4. `download(<img_url>)` 下载。
5. webp 转 png（飞书文档对 webp 支持不完善）：

```bash
sips -s format png input.webp --out output.png      # macOS
magick input.webp output.png                        # Linux/ImageMagick
```

6. 获取图片尺寸并统一复制到工作目录 `images/` 子目录下。

### Step 6：整理内容为结构化 Markdown

从原始文本中提取以下部分，组织为 Markdown：

```markdown
# <题目标题>

> 题目编号：<编号> | 难度：<难度> | 标签：<标签1>、<标签2>
> 来源：[面试鸭](<原始链接>)

---

## 回答重点
<回答重点正文>

## 扩展知识
1) **<原文小节标题>**：
<内容>
2) **<原文小节标题>**：
<内容>

## 面试官追问
### 提问：<追问问题1>
回答：<回答内容>
```

内容提取规则：
- 题目编号：页面中形如 `13557.` 的编号
- 难度：编号下方的"简单"/"中等"/"困难"
- 标签：难度下方的标签词
- 回答重点：从"回答重点"到"扩展知识"之间
- 扩展知识：从“扩展知识”到“面试官追问”（无追问小节时到“作者”或“上一题”）之间，按小节拆分。**小节标号逐字符还原原文**（面试鸭通常为半角 `1) ` + 标题，标题加粗、末尾全角冒号），写作正文段落而非 `###` 标题；不得丢弃、改写或重新编号。原文小节无编号时才用 `###` 标题
- 面试官追问：从“面试官追问”到“作者”或“上一题”之间，每个“提问：”开头为一个追问。**页面没有“面试官追问”小节时直接省略该节，不算异常。**
- 行内代码：原答案中的代码名词（如 `map`、`filter`、`reduceByKey`）保留行内代码格式。注意纯文本提取不含此信息，需按 Step 4 的 DOM 查询核对。
- 列表类型：各小节内容的有序/无序列表按原文还原（innerText 看不出列表标记，同样需 DOM 查询）。

将 Markdown 保存到工作目录，文件名如 `question_<编号>.md`。

### Step 7：创建飞书文档

`--content "@file"` 只接受当前工作目录的相对路径（绝对路径报 unsafe file path），先 cd 到工作目录再执行：

```bash
lark-cli docs +create \
  --doc-format markdown \
  --content "@./question_<编号>.md" \
  --parent-token "<目标node_token>" \
  --as user \
  --format json
```

**扩展知识小节带 `N)` 编号时必须改用 XML 创建**（去掉 `--doc-format markdown`）：markdown 行首的 `1) ` 会被解析为有序列表，丢掉字面标号。XML 内容要点：`<title>` 置标题；小节用 `<p>1) <b>标题</b>：</p>`；代码名词用 `<code>`；列表按原文用 `<ol>`/`<ul>`；代码块用 `<pre lang="python"><code>…</code></pre>`，块内换行写 `<br/>`。完整语法见 `lark-cli skills read lark-doc`（markdown 正文的转义规范也在此文档）。

从返回值中记录 `document_id` 和 `url`。

### Step 8：插入配图（左对齐）

**本题无配图时跳过本步。**

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
- 概念对比图 → 回答重点之后、扩展知识之前
- 演进路径/流程图 → 对应扩展知识小节的文字之后

### Step 9：验证

1. `lark-cli wiki +node-list --space-id <space_id> --parent-node-token <目标node_token>` 确认文档已创建在正确目录下（**`--space-id` 必填**，节点列表在返回的 `data.nodes[]` 中）
2. `lark-cli docs +fetch --doc <document_id>` 回读验证内容完整，且小节标号、行内代码、列表类型与原文一致
3. 有配图时检查图片块存在且位置正确

### Step 10：交付

以当前 agent 的常规方式交付飞书文档链接（如 Markdown 链接）。如果用户要求截图，同时交付滚动截图。

## 可选：滚动截图

如果用户要求保存网页截图：

1. `run_js("window.scrollTo(0, 0)")` 回到页面顶部
2. 逐屏滚动截图，每屏之间等待 1.5 秒；截图返回的临时路径可能被下一次覆盖，**每次截图后立即复制到工作目录**
3. 滚动到底后停止，不要多屏循环

## 故障排查

| 问题 | 原因 | 处理 |
|------|------|------|
| 页面重定向到 404 "Not allowed" | 反爬检测（常见于 Playwright/无头浏览器） | 按浏览器适配层改用真实浏览器 |
| 答案内容被截断 | 未登录 | 提示用户在浏览器中登录面试鸭 |
| 图片插入后不显示 | webp 格式不兼容 | 转换为 png 后再插入 |
| 图片 URL 插入报错 "local/internal host" | 飞书不接受该域名的远程图片 | 先下载到本地，用 `--file` 方式插入 |
| `wiki +node-list` 报 required flag "space-id" | 缺少必填参数 | 补 `--space-id <space_id>` |
| `docs +create --content @文件` 报 unsafe file path | @file 只接受 cwd 相对路径 | cd 到工作目录后用 `@./相对路径` |
| 豆包工作：`bu.js()` 返回空对象 | 返回值序列化问题 | 改用 `bu.get_page_text()` 或 `bu.read_all()` 获取信息 |

## 相关 Skill

- 浏览器操作：按环境选择（豆包工作 `browser-use-automation-mac`；ZCode `ego-browser`，运行 `ego-browser skill` 获取当前版用法）
- 飞书文档创建/编辑：`lark-doc`
- 飞书知识库节点管理：`lark-wiki`
