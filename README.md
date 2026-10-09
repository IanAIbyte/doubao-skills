# Doubao Work Skills

本仓库收集在豆包办公（Doubao Work）中使用的可复用 Skill。每个 Skill 一个目录，包含 `SKILL.md` 及相关资源。

## Skill 列表

### [mianshiya-to-feishu](./mianshiya-to-feishu/)

**面试鸭题目整理 → 飞书云文档**

接收一个面试鸭（mianshiya.com）题目链接，自动整理为结构化飞书云文档。

**触发场景：**
- 用户给出面试鸭链接，要求整理、保存、生成飞书文档
- 批量整理面试题到知识库

**功能：**
- 用浏览器打开页面（需已登录面试鸭）
- 提取题目、回答重点、扩展知识、面试官追问
- 下载页面配图并插入文档（左对齐）
- 在指定飞书知识库目录下为每道题创建一个文档

**使用方法：**
1. 确保浏览器中已登录面试鸭账号
2. 给豆包发送面试鸭题目链接，例如：
   ```
   帮我整理这道面试题：https://www.mianshiya.com/bank/xxx/question/xxx
   ```
3. 豆包会自动完成提取、整理和飞书文档创建

**输出结构：**
```
题目标题
├── 题目信息（编号/难度/标签/来源）
├── 回答重点
├── 扩展知识（含配图）
└── 面试官追问
```

**默认配置：**
- 飞书知识库目录："AI Agent 面试题"
- 可通过对话指定其他目标目录

**注意事项：**
- 禁止使用爬取方式获取内容，仅通过浏览器正常操作
- 未登录时答案会被截断，需先登录
- 图片统一左对齐

---

## 目录结构

```
doubao-skills/
├── README.md
└── mianshiya-to-feishu/
    └── SKILL.md
```

## 安装方法

将 Skill 目录复制到豆包办公的 user_skills 目录下：

```bash
cp -r mianshiya-to-feishu ~/.doubaowork/agent_mode/workspace/.user_skills/
```

重启豆包办公后即可使用。
