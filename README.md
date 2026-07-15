# neu_geo_works

本项目旨在分享东北大学测绘工程/遥感科学与技术作业，鄙人觉得大学不应该花大量的时间在作业上，更重要的是感受和体验。

## 下载方式:

### 1.（推荐）打开你的Agent智能体（豆包办公模式/Workbuddy/codex/claude code/opencode等等....），输入以下指令，将“工程测量学”替换为你要下载的文件夹或者文件夹/子文件夹，桌面替换为你要下载到的位置：

```text
使用github cli（如果没有则安装），将 “https://github.com/All0zy/neu_geo_works/tree/main/工程测量学” 文件夹下载到我的桌面，采用稀疏检索的方式，只要选定的文件夹即可。
```

### 2. 使用git，需要确保你的电脑上有git，打开git bash终端依次输入：

```git
## 进入仓库目录
git clone --depth 1 --filter=blob:none --sparse https://github.com/All0zy/neu_geo_works.git
cd neu_geo_works

## 稀疏检索提取
git sparse-checkout set "工程测量学"
```

### 3. 如果你电脑上安装了 SVN，在终端执行以下命令：

```SVN
svn export https://github.com/All0zy/neu_geo_works/trunk/工程测量学
```

##### 更新：20260716

新增贡献者：闻子博、陈英杰同学