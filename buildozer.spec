[app]

# 应用名称
title = 消个箭头

# 包名（唯一标识）
package.name = arrowblast
package.domain = com.arrowblast

# 源码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# 版本
version = 1.0.0
version.code = 1

# 需求
requirements = python3,kivy==2.3.1

# Android 权限
android.permissions = VIBRATE

# 屏幕方向（竖屏锁定）
android.orientation = portrait

# 适配所有屏幕尺寸
android.allow_backup = true
android.window_soft_input_mode = adjustResize

# 目标 API 级别
android.api = 34
android.minapi = 21
android.sdk = 34

# 编译选项
android.ndk = 27
android.gradle_dependencies = 

# 打包类型
android.arch = arm64-v8a

# 启用 Java 8
android.java_compiler = javac

# 图标（如果存在）
# android.icon = icon.png

# 启动画面
# android.presplash_color = #0D0D1A

# 签署（发布版需要）
# android.release_artifact = aab
# android.keystore = 