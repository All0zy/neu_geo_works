# 🎓 neu_geo_works

**项目初衷**：本项目旨在分享东北大学测绘工程/遥感科学与技术专业的课程作业。 大学不应该花大量的时间在重复性作业上，更重要的是去**感受**和**体验**生活与学习的过程。希望这些资料能为你节省时间，去探索更广阔的世界

## 📥 下载方式

根据你的技术偏好，选择最适合你的下载方式：

### 1. 🤖 使用 AI 智能体 (推荐)

如果你习惯使用 AI 编程助手（如豆包、Workbuddy、Codex、Claude Code、Opencode 等），可以直接让 AI 帮你下载指定文件夹。

**指令示例：**

```
使用 github cli（如果没有则安装），将 `https://github.com/All0zy/neu_geo_works/tree/main/工程测量学` 文件夹下载到我的桌面，采用稀疏检索的方式，只要选定的文件夹即可。
```

*(注意：请将指令中的“工程测量学”替换为你需要的具体课程文件夹名称)*

### 2. 💻 使用 Git (稀疏检出)

如果你只需要仓库中的**部分文件夹**，而不是克隆整个仓库（节省空间和时间），请使用 Git 的稀疏检出功能。

**操作步骤：**

```bash
# 1. 克隆仓库（仅拉取元数据，不下载文件内容）
git clone --depth 1 --filter=blob:none --sparse https://github.com/All0zy/neu_geo_works.git 
# 2. 进入仓库目录
cd neu_geo_works 
# 3. 配置稀疏检出规则（将 "工程测量学" 替换为你需要的文件夹名）
git sparse-checkout set "工程测量学" 
# 4. 拉取指定文件
git pull 
```

### 3. 📦 使用 SVN

如果你电脑上安装了 SVN 客户端，这是下载单个文件夹最简单的方法，无需克隆整个 Git 仓库。

**命令格式：**

```bash
svn export https://github.com/All0zy/neu_geo_works/trunk/文件夹名称
```

## 🤝 贡献者

感谢以下同学对本项目的贡献：

- **All0zy** (张洋) - 项目发起人
- **闻子博**
- **陈英杰**
