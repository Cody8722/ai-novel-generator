# AI 小说生成器

> 🤖 基于矽基流动 API 和 Qwen2.5 模型的智能长篇小说生成系统

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/Cody8722/ai-novel-generator/releases/tag/v0.1.0)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Test](https://img.shields.io/badge/test-passing-success.svg)](STRESS_TEST_REPORT.md)

## ✨ 特性

- 🚀 **快速生成**: 平均 34 秒/章，10 章小说仅需 6 分钟
- 💰 **成本极低**: 100 章长篇小说仅需 ¥0.24
- 📖 **剧情连贯**: AI 智能维护角色一致性和情节逻辑（92/100 分）
- 🔧 **错误自愈**: 自动重试机制，100% 成功率
- 📊 **实时监控**: Token 使用和成本实时追踪
- 🎯 **高度可控**: 支持自定义类型、主题、章节数

## 🎯 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**:
- `requests>=2.31.0` - HTTP 请求
- `python-dotenv>=1.0.0` - 环境变量管理

### 2. 配置 API Key

创建 `.env` 文件：

```bash
SILICONFLOW_API_KEY=your_api_key_here
```

获取 API Key: [矽基流动官网](https://siliconflow.cn/)

### 3. 测试连接

```bash
python novel_generator.py --test-api
```

### 4. 生成小说

**交互式生成**:
```bash
python novel_generator.py
```

然后按提示输入：
- 小说标题
- 类型（科幻/武侠/都市等）
- 核心主题
- 章节数

**自动化测试** (3 章):
```bash
python test_generate.py
```

**压力测试** (10 章):
```bash
python test_stress.py
```

## 📊 性能指标

### 实测数据（10 章压力测试）

| 指标 | 数值 | 评级 |
|------|------|------|
| **生成速度** | 33.7 秒/章 | ⭐⭐⭐⭐⭐ |
| **成功率** | 100% (10/10) | ⭐⭐⭐⭐⭐ |
| **成本** | ¥0.0024/章 | ⭐⭐⭐⭐⭐ |
| **剧情连贯性** | 92/100 | ⭐⭐⭐⭐⭐ |
| **平均字数** | 3,166 字/章 | ⭐⭐⭐⭐ |

**详细测试报告**: [STRESS_TEST_REPORT.md](STRESS_TEST_REPORT.md)

### 规模化能力预测

| 规模 | 耗时 | 成本 | 总字数 |
|------|------|------|--------|
| 10 章 | 6 分钟 | ¥0.024 | 31,658 |
| 20 章 | 11 分钟 | ¥0.048 | 63,316 |
| 50 章 | 28 分钟 | ¥0.119 | 158,290 |
| 100 章 | 56 分钟 | ¥0.238 | 316,580 |

## 🏗️ 系统架构

```
AI 小说生成器/
├── core/                      # 核心模块
│   ├── api_client.py         # API 客户端（重试、成本追踪）
│   └── generator.py          # 小说生成器（大纲、章节）
├── utils/                     # 工具模块
│   └── json_parser.py        # JSON 容错解析（5 策略）
├── templates/                 # 提示词管理
│   └── prompts.py            # 提示词模板（防 AI 遗忘）
├── novel_generator.py        # CLI 主程序
├── test_generate.py          # 自动化测试（3 章）
├── test_stress.py            # 压力测试（10 章）
└── config.py                 # 配置文件
```

## 💡 核心技术

### 1. 智能提示词管理
- **每次重建提示词**: 防止 AI 遗忘规则
- **上下文自动注入**: 传递上一章结尾（1000 字）
- **差异化策略**: 首章/中间章/末章使用不同提示词

### 2. 强大的 JSON 容错
5 策略级联解析，应对 AI 不规范输出：
1. 标准 JSON 解析
2. 提取 `` ```json `` `` 代码块
3. 提取任意 `` ``` `` 代码块
4. 暴力提取 `{...}`
5. 暴力提取 `[...]`

### 3. 自动重试机制
- 最多重试 3 次
- 指数退避策略（2^attempt 秒）
- 超时自动恢复

### 4. 精确成本追踪
- Token 级别计数（输入/输出分别统计）
- 实时成本计算
- 累积统计报告

## 🎨 示例输出

### 生成的小说目录结构
```
novel_时空裂痕_20260104_143140/
├── metadata.json              # 项目元数据
├── outline.txt                # 故事大纲 (916 字)
├── chapter_001.txt            # 第 1 章 (3,704 字)
├── chapter_002.txt            # 第 2 章 (3,514 字)
├── ...
├── chapter_010.txt            # 第 10 章 (2,163 字)
└── full_novel.txt             # 完整小说 (31,658 字)
```

### 统计报告示例
```
📊 生成统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
专案目录............ novel_时空裂痕_20260104_143140
已生成章节.......... 10/10
总字数.............. 31,658 字
总 Token 使用........ 34,821
  ├─ 输入........... 16,029
  └─ 输出........... 18,792
总成本.............. ¥0.0238
平均每章成本........ ¥0.0024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📖 文档

- [开发者指南](README_DEV.md) - 详细的开发和使用文档
- [实作完成报告](IMPLEMENTATION_REPORT.md) - MVP 完整实现记录
- [压力测试报告](STRESS_TEST_REPORT.md) - 10 章长篇测试详细分析
- [变更日志](CHANGELOG.md) - 版本历史
- [完整技术文档](AI小說生成器完整技術文檔.md) - 原始设计文档

## 🚀 支持的模型

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|---------|---------|---------|
| Qwen2.5-7B-Instruct ✅ | ¥0.0007/1K | ¥0.0007/1K | 测试开发、日常创作 |
| Qwen2.5-14B-Instruct | ¥0.0014/1K | ¥0.0014/1K | 正式出版 |
| Qwen2.5-32B-Instruct | ¥0.0035/1K | ¥0.0035/1K | 专业级创作 |
| Qwen2.5-72B-Instruct | ¥0.0070/1K | ¥0.0070/1K | 旗舰级品质 |

## 🧪 测试验证

### ✅ 3 章基础测试
- **标题**: 星际边缘
- **成功率**: 100% (3/3)
- **总字数**: 9,719 字
- **总成本**: ¥0.0078
- **剧情连贯性**: 95/100

### ✅ 10 章压力测试
- **标题**: 时空裂痕
- **成功率**: 100% (10/10)
- **总字数**: 31,658 字
- **总成本**: ¥0.0238
- **剧情连贯性**: 92/100
- **性能**: 比预期快 68%

## 🛠️ 技术栈

- **语言**: Python 3.11+
- **API**: 矽基流动 (SiliconFlow)
- **模型**: Qwen2.5-7B-Instruct
- **依赖**: requests, python-dotenv

## 📝 待开发功能（Phase 2-3）

### Phase 2 - 上下文管理
- [ ] 分卷管理系统
- [ ] RAG 检索增强
- [ ] 向量数据库集成
- [ ] 智能上下文压缩

### Phase 3 - 质量提升
- [ ] 剧情一致性自动检查
- [ ] 角色档案自动维护
- [ ] 缓存系统优化
- [ ] 可视化统计面板

### Phase 4 - 用户体验
- [ ] Web UI 界面
- [ ] 实时生成预览
- [ ] 多模型并行生成
- [ ] 云端部署支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [矽基流动](https://siliconflow.cn/) - 提供高性价比 AI API 服务
- [阿里云通义千问团队](https://tongyi.aliyun.com/) - Qwen2.5 模型开发
- [Claude Code](https://claude.com/claude-code) - 开发辅助工具

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/Cody8722/ai-novel-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cody8722/ai-novel-generator/discussions)

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐

---

**🎉 开始你的 AI 小说创作之旅！**

*最后更新: 2026-01-04 | 版本: v0.1.0 MVP*
