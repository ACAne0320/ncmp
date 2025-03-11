# ncmp

ncmp(NetEase Cloud Music Partner/网易云音乐合伙人)

基于 Python 的网易云音乐-音乐合伙人任务脚本，支持本地运行和 GitHub Actions 自动执行。

## 功能特点

- 全自动完成音乐合伙人日常任务
  - 完成每日5个基础任务
  - 完成每日7个额外评分任务
- 便捷的部署方式
  - 支持本地手动运行
  - 支持 GitHub Actions 自动执行
- 完善的通知机制
  - Cookie 失效自动发送邮件提醒
- 一次配置持续使用
  - 支持自动登录账号并刷新Cookie，基于[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)

## 使用前准备

如果你从来没有接触过GitHub Actions以及Cookies相关的网络知识，请戳[ncmp 使用指北](https://blog.nyaashino.com/post/ncmp_quickstart)。

### 获取网易云音乐 Cookie

1. 登录[网易云音乐网页版](https://music.163.com/)
2. 打开浏览器开发者工具（F12）
3. 切换到 Network（网络）选项卡
4. 刷新页面，在请求中找到 cookie 中的 `MUSIC_U` 和 `__csrf` 值

### 配置邮箱通知（可选）

支持所有提供 SMTP 服务的邮箱，以下是常见邮箱的配置示例：

1. Gmail (推荐)

   ```json
   {
     "notify_email": "your.email@gmail.com",
     "email_password": "YOUR_APP_SPECIFIC_PASSWORD",
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 465
   }
   ```

   注意：Gmail 需要开启两步验证并使用应用专用密码

2. QQ邮箱

   ```json
   {
     "notify_email": "your_qq@qq.com",
     "email_password": "YOUR_AUTH_CODE",
     "smtp_server": "smtp.qq.com",
     "smtp_port": 465
   }
   ```

   注意：需要在QQ邮箱设置中开启SMTP服务并获取授权码

## 使用方法

### 方式一：本地手动执行

1. 克隆仓库到本地：

   ```bash
   git clone https://github.com/ACAne0320/ncmp.git
   cd ncmp
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 复制并编辑配置文件：

   ```bash
   cp config/setting.example.json config/setting.json
   ```

4. 编辑 `config/setting.json`，填写以下配置：

   ```json
   {
     "Cookie_MUSIC_U": "YOUR_MUSIC_U_COOKIE",
     "Cookie___csrf": "YOUR_CSRF_TOKEN",
     "notify_email": "your.email@gmail.com",
     "email_password": "YOUR_APP_SPECIFIC_PASSWORD",
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 465,
     "wait_time_min": 15,
     "wait_time_max": 20,
     "score": 3  // 评分策略：1=1-2分，2=2-3分，3=3-4分（默认），4=固定4分
   }
   ```

5. 运行测试脚本确认配置正确：

   ```bash
   python tests/test_run.py
   ```

6. 运行主程序：

   ```bash
   python main.py
   ```

### 方式二：GitHub Actions 自动执行

1. Fork 本仓库到你的 GitHub 账号

2. 配置 GitHub Secrets：
   在你 fork 的仓库中，进入 Settings -> Secrets and variables -> Actions，添加以下配置：
   - `MUSIC_U`：网易云音乐 MUSIC_U Cookie
   - `CSRF`：网易云音乐 CSRF Token
   - `NOTIFY_EMAIL`：邮箱地址（可选）
   - `EMAIL_PASSWORD`：邮箱密码（可选）
   - `SMTP_SERVER`：smtp.gmail.com（可选）
   - `SMTP_PORT`：465（可选）
   - `WAIT_TIME_MIN`：最小等待时间（可选，默认15）
   - `WAIT_TIME_MAX`：最大等待时间（可选，默认20）
   - `SCORE`：评分策略（可选，默认3）

3. 启用 GitHub Actions：
   - 进入仓库的 Actions 页面
   - 点击 "I understand my workflows, go ahead and enable them"
   - Actions 将会按照预设时间自动运行（默认北京时间1点）

## Cookie自动刷新配置

为了让Cookie自动刷新功能正常工作，您需要创建一个具有特定权限的GitHub Personal Access Token (PAT)。以下是详细步骤：

### 1. 创建GitHub Personal Access Token

1. 登录您的 GitHub 账号
2. 访问 [Token设置页面](https://github.com/settings/tokens)
3. 点击"Generate new token" > "Generate new token (classic)"
4. 在"Note"字段给您的Token起一个描述性名称，如"NCMP Cookie Refresh"
5. 设置 Token 有效期

### 2. 选择正确的权限范围

您只需要为 Token 配置最小必要的权限：

**如果是公开仓库**，选择以下权限：
- `repo` > `public_repo` (仅访问公开仓库)

**如果是私有仓库**，选择以下权限：
- `repo` (完整的仓库访问，包括私有仓库)

### 3. 使用细分权限(Fine-grained tokens)

如果使用 Fine-grained tokens (更精细的权限控制)：
1. 选择只对您的ncmp仓库有效
2. 将 "secrets" 设为 "Read and write"

### 4. 保存Token

1. 滚动到页面底部，点击"Generate token"
2. **立即复制生成的token**（离开页面后将无法再次查看）
3. 将复制的token添加到您fork的ncmp仓库的GitHub Secrets中，命名为`GH_TOKEN`

### 5. 添加额外的自动刷新Cookie所需Secrets

在仓库的Secrets中添加以下内容：
- `NETEASE_PHONE`: 您的网易云音乐账号手机号
- 网易云音乐账号密码（2选1，建议使用MD5加密密码）
  - `NETEASE_PASSWORD`: 明文密码
  - `NETEASE_MD5_PASSWORD`: MD5加密密码
- `GH_TOKEN`: 刚才创建的GitHub Token

### 6. 启用自动刷新工作流

- 确保仓库中`.github/workflows/refresh_cookie.yml`工作流已启用
- 您可以在Actions页面手动运行"Cookie Refresh"工作流测试配置是否正确

## 注意事项

- 目前仅对 Gmail/QQ邮箱 进行了验证，其他邮箱可能需要自行测试
- 邮箱密码为授权码，而非邮箱登录密码
- 任务提交默认添加了 15-20 秒的等待时间，避免被检测异常
- 建议使用 GitHub Actions 的定时任务功能，避免遗漏每日任务
- 网易云音乐的 Cookie 两周左右就会过期，建议配置邮箱以便及时收到失效通知

## 声明

- 本项目仅供学习交流使用
- 不得用于商业用途
- 使用本脚本产生的一切后果由使用者自行承担

## 致谢

- [qinglong-sign](https://github.com/KotoriMinami/qinglong-sign)
- [CloudMusicBot](https://github.com/C20C01/CloudMusicBot)
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
