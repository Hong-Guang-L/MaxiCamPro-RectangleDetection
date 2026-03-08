# GitHub 发表指南

## 📋 文件清单

### ✅ 需要上传的文件（核心代码和文档）

```
MaxiCamPro/
├── main.py                      # 主程序（v2.4.0）
├── test.py                      # 测试代码
├── app.yaml                     # 应用配置
├── app.png                      # 应用图标
├── README.md                    # GitHub 项目说明
├── DEV_LOG.md                   # 开发日志
├── rectangle_detection_blog.md  # CSDN 博客原文
├── .gitignore                   # Git 忽略文件配置
└── micu_uart_lib/               # UART 通信库
    ├── __init__.py
    ├── config.py
    ├── simple_uart.py
    └── utils.py
```

### ❌ 不需要上传的文件（已通过 .gitignore 过滤）

```
MaxiCamPro/
├── dist/                        # 打包文件目录（包含多个 .zip 文件）
│   ├── maix-combo-v1.0.0.zip
│   ├── maix-combo-v1.0.1.zip
│   ├── maix-jgcar-v1.0.0.zip
│   ├── maix-jgcar-v1.0.1.zip
│   └── maix-jgcar-v1.0.2.zip
└── micu_uart_lib/
    └── __pycache__/             # Python 编译缓存
        ├── __init__.cpython-313.pyc
        ├── config.cpython-313.pyc
        ├── simple_uart.cpython-313.pyc
        └── utils.cpython-313.pyc
```

---

## 🚀 GitHub 上传步骤

### 方法一：网页上传（推荐新手）

#### 步骤 1：创建新仓库
1. 访问你的 GitHub：https://github.com/Hong-Guang-L
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `MaxiCamPro-RectangleDetection`
   - **Description**: `基于 MaxiCamPro 的矩形识别系统 | 2025 电赛 E 题解决方案`
   - **Public**（公开）
   - ✅ 勾选 "Add a README file"
   - **License**: MIT
4. 点击 "Create repository"

#### 步骤 2：上传文件
1. 在新仓库页面，点击 "uploading an existing file"
2. **只上传以下文件**：
   ```
   ✅ main.py
   ✅ test.py
   ✅ app.yaml
   ✅ app.png
   ✅ README.md
   ✅ DEV_LOG.md
   ✅ rectangle_detection_blog.md
   ✅ .gitignore
   ✅ micu_uart_lib/ 文件夹（包含 4 个 .py 文件）
   ```
3. **不要上传**：
   ```
   ❌ dist/ 文件夹（打包文件）
   ❌ __pycache__/ 文件夹（编译缓存）
   ```
4. Commit 信息：`Initial commit: 矩形识别系统 v2.4.0`
5. 点击 "Commit changes"

---

### 方法二：Git 命令行（推荐熟练用户）

#### 步骤 1：初始化 Git 仓库
```bash
cd c:\Users\24048\Desktop\MaxiCamPro
git init
```

#### 步骤 2：添加远程仓库
```bash
git remote add origin https://github.com/Hong-Guang-L/MaxiCamPro-RectangleDetection.git
```

#### 步骤 3：添加文件（.gitignore 会自动过滤）
```bash
# 添加所有文件（.gitignore 会自动过滤不需要的文件）
git add .

# 查看将要提交的文件
git status
```

#### 步骤 4：提交更改
```bash
git commit -m "Initial commit: 矩形识别系统 v2.4.0"
```

#### 步骤 5：推送到 GitHub
```bash
git branch -M main
git push -u origin main
```

---

## 📝 上传后检查清单

### 1. 检查文件是否正确上传
```
✅ main.py 存在
✅ micu_uart_lib/ 文件夹存在（包含 4 个 .py 文件）
✅ README.md 显示正常
✅ .gitignore 文件存在
❌ dist/ 文件夹不存在（正确）
❌ __pycache__/ 文件夹不存在（正确）
```

### 2. 检查 README.md 显示
```
✅ 标题显示正常
✅ 图片显示正常（如果有）
✅ 代码块语法高亮
✅ 链接可点击
```

### 3. 添加 Topics 标签
在仓库主页点击 "About" 旁边的设置图标，添加标签：
```
opencv, computer-vision, rectangle-detection, 
image-processing, embedded-systems, python, 
maxicampro, perspective-transform, real-time
```

### 4. 添加仓库描述
```
基于 MaxiCamPro 的矩形识别系统 | 四级过滤 + 透视变换 | 2025 电赛 E 题解决方案
```

---

## ⚠️ 重要注意事项

### 1. 敏感信息检查
```
✅ 已检查 main.py：无密码、密钥等敏感信息
✅ 已检查 app.yaml：无敏感配置
✅ 已检查 micu_uart_lib/：无敏感信息
```

### 2. 文件大小限制
```
✅ 单个文件 < 100 MB
✅ 总仓库大小 < 1 GB
✅ dist/ 文件夹已过滤（避免上传大文件）
```

### 3. 许可证
```
✅ 已选择 MIT License
✅ 在 README.md 中声明开源协议
```

### 4. 版权声明
```
✅ 在代码文件头部添加版权声明
✅ 在 README.md 中声明原创
✅ 在 CSDN 博客中声明转载需注明出处
```

---

## 🔗 CSDN 与 GitHub 关联

### 在 CSDN 文章中添加 GitHub 链接
```markdown
## 附录 A：完整代码获取

本项目完整代码已开源至 GitHub：
- 仓库地址：https://github.com/Hong-Guang-L/MaxiCamPro-RectangleDetection
- 授权协议：MIT License

⭐ 如果这个项目对你有帮助，欢迎给个 Star 支持一下！
```

### 在 README.md 中添加 CSDN 链接
```markdown
## 📖 技术博客

详细的技术博客已发表至 CSDN：
- [基于 MaxiCamPro 的矩形识别系统实战详解](CSDN文章链接)

欢迎阅读、评论和收藏！
```

---

## 📊 推广时间表

### 第 1 天：GitHub 准备
- ✅ 创建仓库
- ✅ 上传代码
- ✅ 完善 README
- ✅ 添加 Topics 标签

### 第 2 天：CSDN 发表
- ✅ 发表技术博客
- ✅ 添加 GitHub 链接
- ✅ 设置标签和分类

### 第 3-7 天：多平台推广
- ✅ 知乎投稿
- ✅ 掘金投稿
- ✅ B站发布演示视频（可选）

---

## ✅ 最终检查

在上传之前，请确认：

```
□ 已创建 .gitignore 文件
□ 已检查所有文件无敏感信息
□ 已准备好 README.md
□ 已准备好仓库描述
□ 已准备好 Topics 标签
□ 已准备好 CSDN 博客链接
```

---

**祝你发表顺利！** 🎉

如有任何问题，请随时联系。
