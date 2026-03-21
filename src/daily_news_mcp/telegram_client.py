import requests

class TelegramClient:
    def __init__(self, token):
        self.token = token

    def send_message(self, chat_id, text):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        response = requests.post(url, data=data)
        return response.json()

    def format_news_summary(self, news_data):
        summary = "Here are your news summaries:\n"
        for article in news_data:
            summary += f"- {article['title']}: {article['description']}\n"
        return summary.strip()  

# Example usage:
# if __name__ == '__main__':
#     bot = TelegramClient('YOUR_BOT_TOKEN')
#     news_data = [
#         {'title': 'Breaking News', 'description': 'Summary of breaking news...'},
#         {'title': 'Daily Update', 'description': 'Summary of daily updates...'}
#     ]
#     formatted_summary = bot.format_news_summary(news_data)
#     bot.send_message('CHAT_ID', formatted_summary)
