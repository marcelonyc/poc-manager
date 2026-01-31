"""Jira integration service"""
from jira import JIRA
from jira.exceptions import JIRAError
import json
from typing import Optional


class JiraService:
    """Jira integration service"""
    
    def __init__(self, url: str, email: str, api_token: str):
        self.client = JIRA(
            server=url,
            basic_auth=(email, api_token)
        )
    
    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium"
    ):
        """Create a Jira issue"""
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
                'priority': {'name': priority},
            }
            
            new_issue = self.client.create_issue(fields=issue_dict)
            return {
                "success": True,
                "issue_key": new_issue.key,
                "issue_url": f"{self.client.server_url}/browse/{new_issue.key}"
            }
        except JIRAError as e:
            return {"success": False, "error": str(e)}
    
    def create_issue_from_poc_task(
        self,
        project_key: str,
        poc_title: str,
        task_title: str,
        task_description: str
    ):
        """Create a Jira issue from a POC task"""
        summary = f"[POC: {poc_title}] {task_title}"
        description = f"POC: {poc_title}\n\nTask: {task_title}\n\n{task_description}"
        
        return self.create_issue(
            project_key=project_key,
            summary=summary,
            description=description,
            issue_type="Task"
        )
    
    def get_issue(self, issue_key: str):
        """Get a Jira issue"""
        try:
            issue = self.client.issue(issue_key)
            return {
                "success": True,
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
            }
        except JIRAError as e:
            return {"success": False, "error": str(e)}
    
    def update_issue_status(self, issue_key: str, status: str):
        """Update Jira issue status"""
        try:
            self.client.transition_issue(issue_key, status)
            return {"success": True}
        except JIRAError as e:
            return {"success": False, "error": str(e)}


def get_jira_client(config_data: str) -> JiraService:
    """Get Jira client from config data"""
    config = json.loads(config_data)
    return JiraService(
        url=config["url"],
        email=config["email"],
        api_token=config["api_token"]
    )
