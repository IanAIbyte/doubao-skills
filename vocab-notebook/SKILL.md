---
name: vocab-notebook
description: 把英语单词收录进个人"英语单词本"。当用户说"加入到单词本"、"加入单词本"、"记录/存到单词本"、"把这个词加到单词本"、"帮我记一下这个单词"等时触发；单词可能在同一句话中给出，也可能指代对话中刚查询/刚讨论过的英文单词（例如刚解释完 essentially 后说"加入到单词本"）。负责补全概述、词性、英美音标、常见搭配和例句，按固定的 H1 段落式 Markdown（单词为 H1 标题，标题与解释间空行）同步写入两处：①当前项目目录下的本地文件「英语单词本.md」；②飞书在线文档「英语单词.md」(https://my.feishu.cn/wiki/FTMBwNBA4iF23Mksk4BcYrtfnzb)。纯单词查询/翻译不触发，用户要求收录时才触发。
---

# 英语单词本收录流程

## 固定目标

- **本地文件**：当前项目目录下 `英语单词本.md`（不存在则创建，直接以单词 H1 开头，无总标题）
- **飞书文档**：`https://my.feishu.cn/wiki/FTMBwNBA4iF23Mksk4BcYrtfnzb`（知识库节点标题保持「英语单词.md」）

## 单词条目格式（每个单词一个 H1 小节，小节之间空行分隔）

```markdown
# essentially

最常见的意思是本质上、基本上，用来强调事物的核心实质，常用于正式表达、面试陈述。

- 词性：副词 (adv.)
- 音标：英 /ɪˈsenʃəli/，美 /ɪˈsenʃəli/
- 常见搭配：
  - essentially the same（本质上一样）
  - essentially a ...（基本上是一个……，用来概括事物本质）
- 例句：This platform is essentially a RAG system for enterprise search.（这个平台本质上是一个用于企业搜索的检索增强生成系统。）
```

要点：单词独占 H1（`# 单词`）；H1 与概述句之间必须空一行；概述句直接以「最常见的意思是…」开头，不再用引号内联单词。

## 步骤

### 1. 确定单词

- 优先取触发消息中给出的单词；没有则取对话里最近查询/讨论的英文单词。
- 一次给多个词则逐个处理；无法确定时向用户确认，不要猜测。

### 2. 整理内容

优先沿用对话中已确认的信息，缺失则补全：

- **概述句**：中文，说明最常见意思、用途、使用场景
- **词性**：中文全称加缩写，如「副词 (adv.)」「动词 (v.)」
- **音标**：英、美 IPA
- **常见搭配**：约 2 个，格式 `英文搭配（中文含义）`
- **例句**：一句自然英文（面试/技术场景优先），句末附 `（中文译文。）`

### 3. 写入本地文件

用本 skill 目录下的脚本（自动生成 H1、空行、查重）：

```bash
python3 '<本skill目录>/scripts/add_word.py' \
  --file '<当前项目目录>/英语单词本.md' \
  --word 'essentially' \
  --summary '最常见的意思是本质上、基本上，用来强调事物的核心实质，常用于正式表达、面试陈述。' \
  --pos '副词 (adv.)' \
  --phonetic-uk '/ɪˈsenʃəli/' \
  --phonetic-us '/ɪˈsenʃəli/' \
  --collocation 'essentially the same（本质上一样）' \
  --collocation 'essentially a ...（基本上是一个……，用来概括事物本质）' \
  --example 'This platform is essentially a RAG system for enterprise search.（这个平台本质上是一个用于企业搜索的检索增强生成系统。）'
```

- 返回 `"status": "duplicate"` → 告知用户该词已存在并跳过飞书写入。
- `"created"` / `"added"` → 继续步骤 4。

### 4. 写入飞书文档（文末追加同一 H1 小节）

1. 把**单个条目**完整内容（以 `# 单词` H1 开头）写入项目目录下临时文件 `_entry.md`。
2. 用 `append` 追加（不要用 `overwrite`）：
   ```bash
   lark-cli docs +update --doc 'https://my.feishu.cn/wiki/FTMBwNBA4iF23Mksk4BcYrtfnzb' --command append --doc-format markdown --content @./_entry.md --as user --format json
   ```
   `@file` 只接受当前工作目录下的相对路径；完成后删除 `_entry.md`。
3. **标题保护**：`append` 不会用 H1 同步文档标题；但 `overwrite`/导入会把首个 H1 当作文档标题，故追加单词时禁止使用。节点标题须保持「英语单词.md」；若被改动，恢复：
   ```bash
   lark-cli drive +update-title --url 'https://my.feishu.cn/wiki/FTMBwNBA4iF23Mksk4BcYrtfnzb' --title '英语单词.md' --as user
   ```

### 5. 验证并汇报

- 重新 `docs +fetch` 确认飞书文档新 H1 小节存在、节点标题正确；检查本地文件。
- 用一句话汇报结果并给出飞书链接；本地 `英语单词本.md` 通过 `present_files` 交付。

## 规则

- 所有 `lark-cli` 命令带 `--as user`。
- 已存在的单词（同名 H1）不重复收录。
- 本地与飞书的条目内容保持一致。
