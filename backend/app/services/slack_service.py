"""Slack integration service"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
from typing import Optional


class SlackService:
    """Slack integration service"""
    
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def post_message(self, channel: str, text: str, blocks: Optional[list] = None):
        """Post a message to a Slack channel"""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return {"success": True, "ts": response["ts"]}
        except SlackApiError as e:
            return {"success": False, "error": str(e)}
    
    def post_poc_update(self, channel: str, poc_title: str, update_type: str, details: str):
        """Post POC update to Slack"""
        text = f"POC Update: {poc_title}"
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 POC Update: {poc_title}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Update Type:*\n{update_type}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Details:*\n{details}"
                    }
                ]
            }
        ]
        
        return self.post_message(channel, text, blocks)
    
    def post_poc_completion(self, channel: str, poc_title: str, success_score: int):
        """Post POC completion notification to Slack"""
        emoji = "🎉" if success_score >= 80 else "✅" if success_score >= 60 else "⚠️"
        text = f"{emoji} POC Completed: {poc_title}"
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": text
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Success Score:* {success_score}/100"
                }
            }
        ]
        
        return self.post_message(channel, text, blocks)


def get_slack_client(config_data: str) -> SlackService:
    """Get Slack client from config data"""
    config = json.loads(config_data)
    return SlackService(config["token"])
