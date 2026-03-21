import generativeai


def summarize_article(article_text):
    # Initialize the Generative AI client
    client = generativeai.Client()
    
    # Call the summarize function from the generativeai library
    summary = client.summarize(article_text)
    
    return summary


if __name__ == "__main__":
    # Example usage:
    article = "News article text here."
    summary = summarize_article(article)
    print(summary)