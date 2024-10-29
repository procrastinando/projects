import requests
import yaml
import time
import bcrypt
import secrets

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def save_config(config):
    with open("config.yaml", "w") as file:
        yaml.dump(config, file)

# Send a message to a user via Telegram
def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")

# Check for new messages or callbacks
def get_updates(token, offset=None):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        return {"result": []}  # Return an empty result to continue the loop

# Handle new message and user interaction
def handle_message(token, config, update, waiting_for_password):
    if "message" in update:  # Regular message handling
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        user_id = str(chat_id)

        # If we are waiting for password input, update the password
        if waiting_for_password.get(user_id):
            hashed_pw = bcrypt.hashpw(text.encode(), bcrypt.gensalt()).decode()
            config["credentials"]["usernames"][user_id]["password"] = hashed_pw
            save_config(config)
            send_message(token, chat_id, "Password has been updated!")
            waiting_for_password[user_id] = False  # Reset the flag after updating the password
        else:
            # Check if user exists in config
            if user_id in config["credentials"]["usernames"]:
                if text == "/get_id":
                    send_message(token, chat_id, f"Your ID is: {user_id}")
                elif text == "/password":
                    send_message(token, chat_id, "Choose a new password:")
                    waiting_for_password[user_id] = True
                else:
                    send_message(token, chat_id, "Unknown command. Use /get_id or /password.")
            else:
                config['credentials']['usernames'][user_id] = {"name": update["message"]["chat"]["first_name"], "email": "", "password": ""}
                save_config(config)
                send_message(token, chat_id, f"Welcome {update['message']['chat']['first_name']}!, this is Carlos,\nyour ID is: {user_id}. Please choose a password:")
                waiting_for_password[user_id] = True

    elif "callback_query" in update:  # Handle callback query
        print("callback received")

# Main loop for checking updates
def main():
    config = load_config()
    if config['token'] != "":
        if config['cookie']['key'] == "":
            config['cookie']['key'] = secrets.token_hex(16)
            save_config(config)

        offset = None
        waiting_for_password = {}  # Dictionary to track which user is entering a password

        while True:
            updates = get_updates(config['token'], offset)
            if updates["result"]:
                for update in updates["result"]:
                    handle_message(config['token'], config, update, waiting_for_password)
                    offset = update["update_id"] + 1
            time.sleep(1)  # Polling interval
    else:
        time.sleep(5)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait before retrying in case of unexpected errors
