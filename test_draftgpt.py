import os
import requests
from urllib.parse import urlparse, parse_qs


from urllib.parse import urlparse, parse_qs

def parse_slack_message_link(link):
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    channel_id = parsed_url.path.split('/')[2]  # Extract the channel ID from the path
    return channel_id


def retrieve_slack_message(channel_id, slack_token):
    headers = {
        "Authorization": f"Bearer {slack_token}",
    }
    # Construct the API URL with the channel ID
    API_URL = f"https://slack.com/api/conversations.history?token={slack_token}&channel={channel_id}&limit=1"
    response = requests.get(API_URL, headers=headers)
    try:
        response_json = response.json()
        # Extract the text of the first message
        message_text = response_json["messages"][0]["text"]
        return message_text
    except (KeyError, IndexError):
        print("Error: No messages found in response.")
        return ""


def draft_gpt(user_input, openai_api_key=os.environ["OPENAI_API_KEY"], gpt_model=os.environ["GPT_MODEL"]):

    if openai_api_key is None:
        raise ValueError("OpenAI API key is not set in environment variables.")

    '''
    with open("incident_descriptions/incident_description.txt", "r") as file:
        incident_desc = file.read().replace("\n", "")
    '''

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    data = {
        "model": gpt_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": user_input,
            },
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    # Check if the request was successful
    if response.status_code == 200:
        print("Response from OpenAI:", response.json())
        print("\n")
        print(response.json()["choices"][0]["message"]["content"])

        file = open("report.txt", 'w')
        file.write(response.json()["choices"][0]["message"]["content"])
        file.close()

    else:
        print("Error:", response.status_code, response.text)

    return response.status_code

    '''
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    '''


def test_draft_gpt():
    test_inputs = [
            "What is the capital of Sweden?",
            "Please solve this math problem: 1+1"
            ]

    for user_input in test_inputs:
        response = draft_gpt(user_input)

        assert response != "", f"Response for input '{user_input}' should not be empty"


if __name__ == "__main__":
    slack_message_link = os.getenv("MESSAGE_LINK")
    slack_token = os.getenv("SLACK_TOKEN")
    if slack_message_link and slack_token:
        slack_channel_id = parse_slack_message_link(slack_message_link)
        print("Slack channel ID:", slack_channel_id)  # Add this line for debugging
        user_input = retrieve_slack_message(slack_channel_id, slack_token)
        if user_input:
            response = draft_gpt(user_input)
            if response:
                print("GPT response:", response)
            else:
                print("Failed to get GPT response.")
        else:
            print("Failed to retrieve user input from Slack channel.")
    else:
        print("MESSAGE_LINK or SLACK_TOKEN environment variable not set.")
