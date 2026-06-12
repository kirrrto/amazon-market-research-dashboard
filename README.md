# Amazon Market Research Dashboard

## Live Demo

Try the dashboard online:

[Open Amazon Market Research Dashboard](https://kirrrto-amazon-market-research.streamlit.app)

## Overview

一个面向亚马逊产品开发、跨境硬件产品调研和市场机会评估的轻量级数据工作台。

用户可以通过 CSV、XLSX、XLS 或公开产品页面 URL 导入数据，完成字段映射、数据清洗、市场分析、利润测算和标准化 Excel 导出。

该项目的目标不是替代 Helium 10、Jungle Scout、Keepa 等专业数据源，而是把不同来源的数据统一到一个可审计、可复用、适合硬件产品开发的分析流程中。

## Current Capabilities

### Spreadsheet Import

- 支持 CSV、XLSX 和 XLS 文件
- 支持 Excel 多工作表选择
- 自动推荐中英文字段映射
- 支持人工修正字段映射
- 拦截重复源字段映射
- 输出行级错误和警告
- 导出标准化 Excel 工作簿

### Public Product Page Connector

- 支持批量粘贴公开产品页面 URL
- 顺序抓取公开 HTML 页面
- 记录来源 URL、域名、状态码和采集时间
- 提取 JSON-LD Product 数据
- 提取 HTML 规格表和 `<dl><dt><dd>` 结构
- 提取页面标题、图片链接和文档链接
- 输出 Products、Raw Specifications、Fetch Logs 和 Issues 工作表

详细说明见 [`docs/product-page-connector.md`](docs/product-page-connector.md)。

### Market and Profit Analysis

- 预估月销售额
- 价格带分布
- 品牌集中度
- 评论门槛与评分差距
- 产品机会分数
- 单位毛利润和净利润
- 净利率
- 盈亏平衡售价
- 预估月净利润
- 可下载分析结果

## Data Source Policy

该项目不绕过登录、验证码、付费墙或访问限制。

市场数据和网页数据应来自：

- 用户合法获取的公开数据
- 第三方工具导出的 CSV / Excel
- 内部调研表格
- 用户明确提供的公开供应商或品牌产品页面 URL
- 后续获得授权的官方 API 或第三方 API

当前版本**不以 Amazon 商品页面 HTML 抓取为核心功能**。Amazon 相关数据建议优先通过合法导出文件、授权 API 或第三方数据工具导入。

## Spreadsheet Import Workflow

```text
上传文件 → 选择工作表 → 预览 → 字段映射 → 数据校验 → 分析与导出
```

详细说明见 [`docs/import-workflow.md`](docs/import-workflow.md)。

## Product Page Connector Workflow

```text
粘贴产品页面 URL → 抓取公开 HTML → 解析 JSON-LD 与规格表
→ 查看抓取日志和问题 → 下载 Excel → 后续进入规格分析
```

当前连接器适合结构清晰的供应商官网、品牌官网和普通公开产品页。对于 JavaScript 渲染页面、登录页面、验证码页面、Amazon 商品页和 PDF 内容解析，后续会通过独立模块处理。

## Required Spreadsheet Fields

市场分析至少需要以下标准字段：

| 字段 | 说明 |
|---|---|
| asin | 产品标识 |
| title | 产品标题 |
| brand | 品牌 |
| price | 售价 |
| rating | 星级 |
| reviews | 评论数 |
| monthly_sales | 预估月销量 |
| category | 类目 |

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Run Tests

```bash
python -m pytest -q
```

## Opportunity Score

机会分数综合考虑：

- 月销量需求
- 评论竞争门槛
- 评分改善空间
- 品牌集中度
- 价格可操作空间

该分数用于初筛，不应替代完整的供应链、合规、专利、广告成本和利润分析。

## Data Cleaning Rules

导入表格数据时，系统会执行以下处理：

- 字段名称去除首尾空格并转换为标准字段
- ASIN 转换为大写并按 ASIN 去重
- `$`、千分位逗号和文本评分会转换为数值
- 缺少 ASIN 或关键数值无效的行会被移除
- 负价格、负评论数和负月销量会归零
- 评分会限制在 `0–5` 范围内
- 空品牌会标记为 `Unknown`
- 空类目会标记为 `Uncategorized`

页面会显示本次导入中被移除或自动修正的数据数量，便于检查原始调研表质量。

## Profit Model

利润估算使用以下输入：

- Product cost：单位产品成本
- Shipping cost：单位物流成本
- Platform fee rate：平台费用占售价的比例
- Advertising cost rate：广告费用占售价的比例
- Return rate：退货损失占售价的比例

计算公式：

```text
Contribution rate
= 1 - platform fee rate - advertising cost rate - return rate

Estimated unit net profit
= price × contribution rate - product cost - shipping cost

Estimated net margin
= estimated unit net profit ÷ price

Break-even price
= (product cost + shipping cost) ÷ contribution rate

Estimated monthly net profit
= unrounded estimated unit net profit × monthly sales
```

当前版本对全部产品使用同一组成本假设，因此适合市场机会初筛，不替代正式财务核算。

## Troubleshooting

### Missing required columns

检查 CSV 或 Excel 是否包含全部必需字段。字段大小写、首尾空格和常见中英文字段别名可以自动处理，但字段语义必须明确。

### No valid product rows remain after cleaning

说明所有行都缺少 ASIN，或 `price`、`rating`、`reviews`、`monthly_sales` 中存在无法识别的数据。请检查原始导出表。

### Product URL fetch failed

检查页面是否为公开 HTML 页面。当前连接器不支持登录页面、验证码页面、PDF 内容解析或 JavaScript 完全渲染页面。

### Invalid profit assumptions

平台费率、广告费率和退货率之和必须低于 100%，产品成本和物流成本不能为负数。

### ModuleNotFoundError

请在项目根目录安装依赖并运行：

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Roadmap

- [ ] 安防摄像头规格模板
- [ ] 车载影像规格模板
- [ ] 规格字段别名和单位标准化
- [ ] 竞品规格矩阵
- [ ] 参数缺失和冲突检测
- [ ] 供应商评分模型
- [ ] 合规矩阵
- [ ] PDF 规格书解析
- [ ] Word / PDF 调研报告导出

## License

MIT
