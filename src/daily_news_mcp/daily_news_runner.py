import asyncio
import json
import os
import logging
from typing import List

from daily_news_mcp.api_client import NewsAPIClient
from daily_news_mcp.telegram_client import TelegramClient

# Configure logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')
logger = logging.getLogger(__name__)

async def run_news_task():
    \"\"\"
    Main task to fetch news and send to Telegram.
    \"\"\"
    # Load configuration
    config_path = \"config_runtime.json\"
    if os.path.exists(config_path):
        with open(config_path, \"r\", encoding=\"utf-8\") as f:
            config = json.load(f)
    else:
        # Fallback to environment variables
        config = {
            \"telegram_bot_token\": os.environ.get(\"TELEGRAM_TOKEN\"),
            \"telegram_chat_id\": os.environ.get(\"TELEGRAM_CHAT_ID\"),
            \"news_categories\": [\"crypto\", \"tech\", \"finance\"], # Default categories
            \"api_base_url\": os.environ.get(\"DAILY_NEWS_API_BASE\", \"https://ai.6551.io\")
        }

    token = config.get(\"telegram_bot_token\")
    chat_id = config.get(\"telegram_chat_id\")
    configured_categories = config.get(\"news_categories\", [\"crypto\", \"tech\", \"finance\"])
    api_base_url = config.get(\"api_base_url\", \"https://ai.6551.io\")

    if not token or not chat_id:
        logger.error(\"Telegram token or chat ID not found in configuration.\")
        return

    logger.info(f\"Starting news task for configured categories: {configured_categories}\")
    
    api_client = NewsAPIClient(base_url=api_base_url)
    tg_client = TelegramClient(token=token)

    try:
        all_news_summary = \"📰 *今日新闻推送* 📰\\n\\n\"
        news_found = False

        # First, try to get news from configured categories
        for category in configured_categories:
            logger.info(f\"Attempting to fetch hot news for category: {category}\")
            try:
                news_data = await api_client.get_free_hot(category=category)
                if news_data.get(\"success\") and news_data.get(\"data\"):
                    items = news_data[\"data\"][:5]  # Get top 5 items
                    if items:
                        all_news_summary += f\"🔹 *{category.upper()} 热门新闻*\\n\"
                        for item in items:
                            title = item.get(\"title\", \"No Title\")
                            desc = item.get(\"description\") or item.get(\"summary\") or \"\"
                            if desc:
                                desc = (desc[:100] + \"...\") if len(desc) > 100 else desc
                                all_news_summary += f\"• *{title}*\\n_{desc}_\\n\"
                            else:
                                all_news_summary += f\"• *{title}*\\n\"
                        all_news_summary += \"\\n\"
                        news_found = True
                        break # Found news, no need to check other configured categories
                else:
                    logger.warning(f\"No news found for category: {category} from API. Trying next category.\")
            except Exception as e:
                logger.error(f\"Error fetching news for {category}: {e}. Trying next category.\")

        # If no news found from configured categories, try to get from all available categories
        if not news_found:
            logger.info(\"No news found in configured categories. Attempting to fetch from all available categories.\")
            try:
                categories_response = await api_client.get_free_categories()
                if categories_response.get(\"success\") and categories_response.get(\"data\"):
                    available_categories = [cat[\"name\"] for cat in categories_response[\"data\"]]
                    logger.info(f\"Available categories from API: {available_categories}\")
                    for category in available_categories:
                        if category not in configured_categories: # Avoid re-checking already checked categories
                            logger.info(f\"Attempting to fetch hot news for available category: {category}\")
                            news_data = await api_client.get_free_hot(category=category)
                            if news_data.get(\"success\") and news_data.get(\"data\"):
                                items = news_data[\"data\"][:5]
                                if items:
                                    all_news_summary += f\"🔹 *{category.upper()} 热门新闻*\\n\"
                                    for item in items:
                                        title = item.get(\"title\", \"No Title\")
                                        desc = item.get(\"description\") or item.get(\"summary\") or \"\"
                                        if desc:
                                            desc = (desc[:100] + \"...\") if len(desc) > 100 else desc
                                            all_news_summary += f\"• *{title}*\\n_{desc}_\\n\"
                                        else:
                                            all_news_summary += f\"• *{title}*\\n\"
                                    all_news_summary += \"\\n\"
                                    news_found = True
                                    break # Found news, stop searching
                            else:
                                logger.warning(f\"No news found for available category: {category}.\")
                else:
                    logger.warning(\"Could not fetch available categories from API.\")
            except Exception as e:
                logger.error(f\"Error fetching available categories or news from them: {e}\")

        if not news_found:
            all_news_summary += \"暂时没有获取到最新新闻。请检查 API 状态或配置。\"

        # Send to Telegram
        logger.info(\"Sending summary to Telegram...\")
        resp = tg_client.send_message(chat_id=chat_id, text=all_news_summary)
        
        if resp.get(\"ok\"):
            logger.info(\"News sent successfully!\")
        else:
            logger.error(f\"Failed to send news: {resp}\")

    finally:
        await api_client.close()

if __name__ == \"__main__\":
    # Set PYTHONPATH to include src directory
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), \"../../\"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    asyncio.run(run_news_task()))
