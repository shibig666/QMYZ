# 🚀🚀🚀 青马易战自动刷题

本项目旨在实现高速自动刷题、自动AI对战和自动爬取题库，仅供学习交流，严禁用于商业用途。

## 🌟 上手指南

### ⚙️ 开发前的配置要求

在开始使用本项目之前，请确保已安装以下依赖项：

1. **Python 3.x**
2. **Requests**
3. **pycryptodome**

安装依赖：

```bash
pip install -r ./requirements.txt
```

### 📜 程序说明

本项目包含以下几个功能：

- **`qm_cli`**：自动刷题程序，通过命令行进行操作。
  - `-u` 登录URL（请加引号）
  - `-i` 课程ID
  - `-c` 题库路径
  - `-n` 答题量，默认为无限
  - `-a` 准确度，默认为100

- **`fight`**：自动AI对战答题程序，支持自动补充题库（推荐使用此程序来爬取题目）。
  
- **`qm_auto`**：交互式答题程序。

**注意**：默认题库可能不是最新的，您可以在此基础上爬取新题目，并贡献更新的题库。

### 📝 使用指南

1. **获取 URL**  
   获取登录 URL 的方法是：打开易班青马易战，进入首页（含视频的页面），点击右上角复制地址。如果 URL 很长，那么就是需要的 URL。

2. **获取课程 ID**  
   获取课程 ID 的方法是：进入某个课程的答题页面，URL 中会包含该课程的 ID。

### ⚡️ 示例

```bash
# 使用 `qm_cli` 自动刷题
python qm_cli.py -u "http://your-login-url" -i 12 -c "qmyz/12.csv" -n 100 -a 90

# 使用 `fight` 进行自动AI对战并爬取新题目(需要在文件中填写参数)
python fight.py

# 使用 `qmauto` 进行交互式答题
python qm_auto.py
```

## 👨‍💻 作者

**shibig666**

## 📜 版权说明

该项目遵循 [GPLv3 许可证](./LICENSE.txt)，详情请参阅 `LICENSE.txt`。
