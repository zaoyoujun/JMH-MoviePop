# JMH-MoviePop

一个小型桌面播放器项目，计划使用 Vue 前端、Python 后端，并通过 Electron 打包为桌面软件。

## 目录规划

```text
backend/                 Python 后端
  app/
    api/                 HTTP/WebSocket 接口
    core/                配置、启动、公共基础能力
    models/              数据模型
    services/            播放、扫描、文件、字幕等业务逻辑
  tests/                 后端测试

frontend/                Vue 前端
  public/                静态公共资源
  src/
    assets/              图片、样式、字体等资源
    components/          通用组件
    router/              路由
    services/            调后端接口的封装
    stores/              状态管理
    views/               页面级视图

electron/                Electron 桌面端
  main/                  主进程
  preload/               预加载脚本
  resources/
    icons/               应用图标、安装包资源

shared/                  前后端共享约定
  contracts/             API 契约、接口说明
  types/                 共享类型定义

docs/                    项目文档
scripts/                 开发、构建、打包脚本
build/                   打包输出或构建辅助目录
```

