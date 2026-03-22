import requests

class TelegramClient:
    def __init__(self, token):
        self.token = token

    def send_message(self, chat_id, message):
        try:
            response = requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage', json={'chat_id': chat_id, 'text': message})
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_data = response.json()
            if not response_data.get('ok', False):
                print(f"Error in API response: {response_data.get('description')}")
            else:
                print("Message sent successfully!")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        except ValueError as e:
            print(f"JSON decoding failed: {e}")