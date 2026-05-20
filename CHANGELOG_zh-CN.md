# 变更日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [1.3.0] - 2026-05-20

### 新增

- 新增 Gradio 网页 UI，可在浏览器中生成视频
- Web UI 支持在页面中选择 Veo 视频模型和 Gemini 参考视频分析模型
- Web UI 支持 Google AI Studio API Key 与 Gemini Enterprise / Service Account 两种认证方式
- 新增 Veo 与 Gemini 模型默认目录，并同步到 `config.json.example`
- 新增基础测试覆盖配置合并、模型选择、输出路径和认证参数构造

### 变更

- 将视频输出路径固定到项目根目录下的 `output` 文件夹
- 优化 `VeoClient`，支持运行时传入认证信息、模型和代理配置
- 改进配置加载逻辑，缺少 `config.json` 时使用内置默认配置
- 禁用当前 Veo 3.1 preview API 不支持的 GUI 人物生成参数，避免误导用户

### 文档

- 更新中英文 README，补充 Web UI、认证方式、模型选择和 Gradio 依赖说明
- 更新 `.env.example`，补充 AI Studio 与 Enterprise 两套认证配置示例

## [1.2.0] - 2026-01-24

### 新增

- 参考视频分析功能，可从现有视频生成视频提示词
- 文件上传状态轮询，确保文件就绪后再进行处理
- 项目专用临时目录 (`.temp`) 用于存储临时文件

### 变更

- 将 `run_gui.py` 重命名为 `gui.py` 以保持一致性
- 移除 `config.example.json` 文件

### 文档

- 添加中英文变更日志文件
- 更新项目文档

## [1.1.0] - 2025-12-22

### 新增

- 支持自定义 Google GenAI API 基础 URL 配置
- 可在 `config.json` 中配置 API 端点

### 文档

- 更新模型选择说明，反映 GUI 下拉菜单和 `config.json` 的使用方式

## [1.0.0] - 2025-12-13

### 新增

- 初始化 Google Veo 视频生成项目
- 视频生成图形用户界面 (GUI)
- 命令行界面 (CLI) 支持
- Google GenAI API 集成支持
- 通过 `config.json` 进行配置管理
- GUI 中的模型选择下拉菜单
- 提示词和负向提示词输入字段
- 宽高比和人物生成设置
- 基于种子的可复现生成
- 视频输出管理

### 变更

- 将项目重构为 `app` 包结构
- 采用 `uv` 进行依赖管理
- 更新文档和核心逻辑文件
