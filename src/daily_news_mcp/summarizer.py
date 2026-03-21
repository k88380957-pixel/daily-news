import requests

class NewsSummarizer:
    def __init__(self, api_key):
        self.api_key = api_key

    def summarize_news(self, news_items, category):
        # Assuming Google Gemini API accepts formatted JSON for summarization
        summaries = []
        for news in news_items:
            response = requests.post('https://api.google.com/gemini/summarize', json={
                'text': news['content'],
                'category': category,
                'api_key': self.api_key
            })
            if response.status_code == 200:
                summaries.append(response.json()['summary'])
            else:
                summaries.append('Error summarizing news.')
        return summaries

# Example usage:
# api_key = 'your_api_key_here'
# summarizer = NewsSummarizer(api_key)
# summaries = summarizer.summarize_news(news_items, 'technology')
# print(summaries)