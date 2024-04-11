import os
import requests
from slack import WebClient
from slackeventsapi import SlackEventAdapter

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events")

@slack_events_adapter.on("message")
def message(event_data):
    message = event_data["event"]
    user_id = message.get("user")
    text = message.get("text")

    if user_id and text:
        # Call gpt function with user message
        response = draft_gpt(text)

        # Send response back to slack
        slack_client.chat_postMessage(channel=message["channel"], text=response)
        



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
    '''
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

def test_draft_gpt():
    test_inputs = [
            "What is the capital of Sweden?",
            "Please solve this math problem: 1+1"
            ]

    for user_input in test_inputs:
        response = draft_gpt(user_input)

        assert response != "", f"Response for input '{user_input}' should not be empty"
        


if __name__ == "__main__":
    # draft_gpt()
    slack_events_adapter.start(port=3000)
