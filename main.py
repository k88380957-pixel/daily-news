#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目名称：Daily Crypto News Summary

本脚本用于定期抓取加密货币相关新闻，通过简单的自然语言处理将新闻划分为利好、利空或中性。

工作流程：
1. 指定若干新闻源的 RSS 链接，使用 feedparser 解析各类新闻条目。
2. 合并并遍历每条新闻，截取标题与摘要组成待分析文本。
3. 使用 VaderSentiment 提供的情感分析器计算情感分数，并根据阈值判定新闻倾向：
   - 得分 ≥ 0.05 判定为利好；
   - 得分 ≤ -0.05 判定为利空；
   - 其余则为中性。
4. 生成简要摘要（截取前 n 个单词）并输出分类结果。

依赖：请在运行前安装 requirements.txt 中列出的依赖包。
"""

import sys
import logging
from typing import List, Dict, Tuple

import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ------------------------- 配置 -------------------------

# 定义要抓取的 RSS 源列表。可根据实际需求增删。
RSS_FEEDS: List[str] = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/?output=xml",
    "https://cointelegraph.com/rss",
    "https://www.theblock.co/rss"
]

# 摘要中保留的最大单词数
SUMMARY_MAX_WORDS: int = 30

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_news(feeds: List[str]) -> List[Dict[str, str]]:
    """从给定的 RSS 源抓取新闻条目。

    Args:
        feeds: RSS 链接列表。

    Returns:
        包含每条新闻信息的字典列表。
    """
    entries: List[Dict[str, str]] = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            logger.warning(f"解析 RSS 源 {url} 失败: {exc}")
            continue
        for entry in feed.entries:
            entries.append(
                {
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get("summary", entry.get("description", "")).strip(),
                    "link": entry.get("link", "").strip(),
                }
            )
    logger.info(f"共抓取到 {len(entries)} 条新闻")
    return entries


def summarize(text: str, max_words: int = SUMMARY_MAX_WORDS) -> str:
    """简易摘要：截取前 max_words 个单词。

    Args:
        text: 原始文本。
        max_words: 最大保留的单词数。

    Returns:
        生成的摘要字符串。
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def classify_sentiment(text: str, analyzer: SentimentIntensityAnalyzer) -> str:
    """根据情感分数分类新闻利好、利空、中性。

    使用 VaderSentiment 的 polarity_scores 结果中 compound 分数：
    - ≥ 0.05 视为利好。
    - ≤ -0.05 视为利空。
    - 介于其间视为中性。

    Args:
        text: 待分析文本。
        analyzer: SentimentIntensityAnalyzer 实例。

    Returns:
        分类标签："利好"、"利空" 或 "中性"。
    """
    scores = analyzer.polarity_scores(text)
    compound = scores.get("compound", 0.0)
    if compound >= 0.05:
        return "利好"
    if compound <= -0.05:
        return "利空"
    return "中性"


def generate_report(entries: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    """生成报告，将新闻划分为利好、利空和中性。

    Args:
        entries: 抓取的新闻条目列表。

    Returns:
        三个列表，分别包含利好新闻、利空新闻和中性新闻。每个元素是一个字典，含标题、链接、摘要、情感。
    """
    analyzer = SentimentIntensityAnalyzer()
    positive: List[Dict[str, str]] = []
    negative: List[Dict[str, str]] = []
    neutral: List[Dict[str, str]] = []
    for entry in entries:
        text = f"{entry.get('title', '')}. {entry.get('summary', '')}"
        sentiment = classify_sentiment(text, analyzer)
        summary = summarize(text, SUMMARY_MAX_WORDS)
        item = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": summary,
            "sentiment": sentiment,
        }
        if sentiment == "利好":
            positive.append(item)
        elif sentiment == "利空":
            negative.append(item)
        else:
            neutral.append(item)
    return positive, negative, neutral


def print_report(positive: List[Dict[str, str]], negative: List[Dict[str, str]], neutral: List[Dict[str, str]]) -> None:
    """打印报告到控制台。"""
    print("=== 📈 利好消息 ===")
    for item in positive:
        print(f"• {item['title']}\n  摘要: {item['summary']}\n  链接: {item['link']}\n")
    print("=== 📉 利空消息 ===")
    for item in negative:
        print(f"• {item['title']}\n  摘要: {item['summary']}\n  链接: {item['link']}\n")
    print("=== 📌 中性消息 ===")
    for item in neutral:
        print(f"• {item['title']}\n  摘要: {item['summary']}\n  链接: {item['link']}\n")


def main() -> None:
    """脚本主入口。"""
    entries = fetch_news(RSS_FEEDS)
    if not entries:
        logger.warning("未抓取到任何新闻。请检查 RSS 源是否可用。")
        sys.exit(0)
    positive, negative, neutral = generate_report(entries)
    print_report(positive, negative, neutral)


if __name__ == "__main__":
    main()