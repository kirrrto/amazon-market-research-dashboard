# Amazon Market Research Dashboard

一个面向亚马逊产品开发和市场调研工作的轻量级分析工具。用户上传 CSV、XLSX 或 XLS 产品调研表后，可通过字段映射完成标准化，并快速得到：

- 预估月销售额
- 价格带分布
- 品牌集中度
- 评论门槛与评分差距
- 产品机会分数
- 可下载的分析结果

该项目不抓取亚马逊页面，也不绕过平台限制。数据应来自用户合法获取的公开数据、第三方工具导出或内部调研表格。

## 功能

- 支持 CSV、XLSX、XLS 和多工作表选择
- 自动推荐中英文字段映射，并允许人工修正
- 输出行级错误、警告及标准化 Excel 工作簿
- 自动校验必需字段
- 解析 `$79.99`、`1,234`、`4.5 out of 5` 等常见导出格式
- 汇报无效行、重复 ASIN、空品牌和异常数值的清洗结果
- 兼容缺失值和异常数值
- 计算品牌销售额份额
- 生成 0–100 的机会分数
- 支持按类目和品牌筛选
- 导出处理后的 CSV
- 提供单元测试和 GitHub Actions

## 表格导入流程

```text
上传文件 → 选择工作表 → 预览 → 字段映射 → 数据校验 → 分析与导出
```

详细说明见 [`docs/import-workflow.md`](docs/import-workflow.md)。

## 输入字段

CSV 至少应包含：

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

## 本地运行

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

安装依赖并运行：

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 运行测试

```bash
pytest
```

## 机会分数说明

机会分数综合考虑：

- 月销量需求
- 评论竞争门槛
- 评分改善空间
- 品牌集中度
- 价格可操作空间

该分数用于初筛，不应替代完整的供应链、合规、专利、广告成本和利润分析。


## 数据清洗规则

导入 CSV 时，系统会执行以下处理：

- 字段名称会去除首尾空格并转换为小写
- ASIN 会转换为大写，并按 ASIN 去重
- `$`、千分位逗号和文本评分会转换为数值
- 缺少 ASIN 或关键数值无效的行会被移除
- 负价格、负评论数和负月销量会归零
- 评分会限制在 `0–5` 范围内
- 空品牌会标记为 `Unknown`
- 空类目会标记为 `Uncategorized`

页面会显示本次导入中被移除或自动修正的数据数量，便于检查原始调研表质量。

## 利润模型

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
= estimated unit net profit × monthly sales
```

当前版本对全部产品使用同一组成本假设，因此适合市场机会初筛，不替代正式财务核算。

## Troubleshooting

### Missing required columns

检查 CSV 是否包含 README 中列出的全部必需字段。字段大小写和首尾空格可以自动处理，但字段名称本身必须一致。

### No valid product rows remain after cleaning

说明所有行都缺少 ASIN，或 `price`、`rating`、`reviews`、`monthly_sales` 中存在无法识别的数据。请检查原始导出表。

### Invalid profit assumptions

平台费率、广告费率和退货率之和必须低于 100%，产品成本和物流成本不能为负数。

### ModuleNotFoundError

请在项目根目录运行：

```bash
streamlit run app.py
```

不要直接进入 `src` 目录启动程序。


## 路线图

- [ ] 增加毛利率和广告成本模型
- [ ] 增加关键词覆盖分析
- [ ] 增加产品规格对比
- [ ] 支持 Excel 文件
- [ ] 生成可打印市场调研报告

## License

MIT
