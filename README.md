# 消个箭头 🎯

迷宫解谜小游戏。点击箭头 → 沿方向滑出屏幕 → 清掉所有箭头过关。

## 玩法

1. 每关地图上有多个箭头（↑↓←→）
2. **点击一个箭头**，它会沿着指向方向滑动，直到滑出屏幕消失
3. 滑动途中撞到其他箭头：**扣 1 点生命**，必须按顺序逐个消除
4. **清掉所有箭头即过关**

## 难度系统（100关）

| 关卡 | 难度 | 网格 | 箭头数 | 生命 | 提示 | 锤子 |
|------|------|------|--------|------|------|------|
| 1-20 | 简单 | 5×5~6×6 | 8~15 | ❤5 | ∞ | 5 |
| 21-40 | 普通 | 7×7~8×8 | 18~30 | ❤3 | 3 | 3 |
| 41-60 | 困难 | 9×9~10×10 | 35~60 | ❤2 | 1 | 1 |
| 61-100 | 地狱 | 11×11~13×13 | 70~120 | ❤1 | 0 | 0 |

- **提示 💡**：高亮当前可消除的箭头
- **锤子 🔨**：直接消除一个箭头
- **生命 ❤**：点错被挡住会扣血，归零游戏结束

## 获取 APK

### 方式一：GitHub Actions（推荐，无需本地环境）

1. 把代码推送到 GitHub 仓库
2. 进入仓库 Actions 页面 → 点击 "Build APK" → "Run workflow"
3. 等待约 20 分钟 → 下载生成的 APK 文件

### 方式二：本地 WSL/Ubuntu 打包

```bash
# 安装 Buildozer
pip install buildozer

# 安装 Android SDK 依赖
sudo apt install git zip unzip openjdk-17-jdk python3-pip autoconf libtool build-essential ccache

# 打包
buildozer android debug

# APK 在 bin/ 目录下
```

## 文件结构

```
我的安卓小游戏/
├── main.py              # 游戏主程序（Kivy）
├── generator.py         # 关卡生成引擎
├── buildozer.spec       # Buildozer 打包配置
├── .github/workflows/   # GitHub Actions 自动打包配置
└── README.md
```

## 技术说明

- 使用 **Kivy** 框架，适配所有尺寸的 Android 设备（手机、平板）
- 竖屏锁定，自动适配分辨率（华为等各品牌平板）
- 关卡生成引擎：严格分层结构、强制连通性、保证唯一解
