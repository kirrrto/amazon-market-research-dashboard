# Amazon Market Research Dashboard

一个面向亚马逊产品开发和市场调研工作的轻量级分析工具。用户上传产品数据 CSV 后，可快速得到：

- 预估月销售额
- 价格带分布
- 品牌集中度
- 评论门槛与评分差距
- 产品机会分数
- 可下载的分析结果

该项目不抓取亚马逊页面，也不绕过平台限制。数据应来自用户合法获取的公开数据、第三方工具导出或内部调研表格。

## 功能

- 自动校验 CSV 必需字段
- 兼容缺失值和异常数值
- 计算品牌销售额份额
- 生成 0–100 的机会分数
- 支持按类目和品牌筛选
- 导出处理后的 CSV
- 提供单元测试和 GitHub Actions

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

## 路线图

- [ ] 增加毛利率和广告成本模型
- [ ] 增加关键词覆盖分析
- [ ] 增加产品规格对比
- [ ] 支持 Excel 文件
- [ ] 生成可打印市场调研报告

## License

MIT
