# Daily Crypto News Summary

该仓库用于自动抓取加密货币行业的主要新闻，并通过简易情感分析将其划分为利好、利空或中性。它可以由 GitHub Actions 每日自动运行，并在工作流日志中输出分类好的新闻列表。

## 主要功能

- **新闻抓取**：从预设的多个主流加密媒体 RSS 源获取最新新闻，包括 CoinDesk、Cointelegraph 和 The Block。
- **情感分析**：借助 [VaderSentiment](https://github.com/cjhutto/vaderSentiment) 模型，对新闻标题和摘要进行情感分析，判定新闻倾向。
- **自动分类**：根据情感分数将新闻分类为 *利好*、*利空* 或 *中性*。
- **简易摘要**：截取新闻标题和摘要的前若干个单词形成简要描述，方便快速阅读。
- **GitHub Actions**：通过 `.github/workflows/daily-news.yml` 工作流，每日自动运行脚本并输出结果。

## 使用说明

1. 克隆或 Fork 此仓库。
2. 根据需要修改 `daily-news/main.py` 中的 `RSS_FEEDS` 列表，添加或删除新闻源链接。
3. 安装依赖：

   ```bash
   pip install -r daily-news/requirements.txt
   ```

4. 运行脚本查看效果：

   ```bash
   python daily-news/main.py
   ```

5. 若要启用自动化，每日运行脚本，请确保仓库启用了 GitHub Actions，并根据需要调整 `.github/workflows/daily-news.yml` 中的 `cron` 表达式。

## 工作原理

脚本使用 `feedparser` 解析各个 RSS 源，合并得到的新闻列表，并利用 `vaderSentiment` 对文本计算综合情感评分（compound）。得分大于等于 0.05 视为正面（利好），小于等于 -0.05 视为负面（利空），其余归为中性。随后将分类及摘要结果输出到终端（或 GitHub Actions 日志）。

## 自定义

- **添加或替换新闻源**：编辑 `RSS_FEEDS` 列表即可。
- **调整摘要长度**：修改 `SUMMARY_MAX_WORDS` 常量。
- **更换情感分析模型**：当前使用的是 VaderSentiment，如需更复杂的分析，可在 `classify_sentiment` 函数中引入其他 NLP 库（如 transformers）。

## 注意事项

- 脚本执行依赖网络访问 RSS 源。若在 GitHub Actions 运行时出现网络问题，可更换或增添 RSS 源，或通过使用代理解决。
- 情感分析只是基于标题和摘要的简单模型，结果仅供参考，不构成投资建议。