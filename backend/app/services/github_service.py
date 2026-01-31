"""GitHub integration service"""
from github import Github, GithubException
import json
from typing import Optional


class GitHubService:
    """GitHub integration service"""
    
    def __init__(self, token: str):
        self.client = Github(token)
    
    def get_gist(self, gist_id: str):
        """Get a GitHub Gist"""
        try:
            gist = self.client.get_gist(gist_id)
            files = {}
            for filename, file_obj in gist.files.items():
                files[filename] = {
                    "content": file_obj.content,
                    "language": file_obj.language,
                    "size": file_obj.size,
                }
            
            return {
                "success": True,
                "id": gist.id,
                "description": gist.description,
                "files": files,
                "url": gist.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}
    
    def create_gist(self, description: str, files: dict, public: bool = False):
        """Create a GitHub Gist"""
        try:
            from github import InputFileContent
            
            gist_files = {}
            for filename, content in files.items():
                gist_files[filename] = InputFileContent(content)
            
            user = self.client.get_user()
            gist = user.create_gist(public, gist_files, description)
            
            return {
                "success": True,
                "id": gist.id,
                "url": gist.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}
    
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ):
        """Create a pull request"""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            return {
                "success": True,
                "number": pr.number,
                "url": pr.html_url,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}
    
    def get_repository(self, repo_name: str):
        """Get repository information"""
        try:
            repo = self.client.get_repo(repo_name)
            return {
                "success": True,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}


def get_github_client(config_data: str) -> GitHubService:
    """Get GitHub client from config data"""
    config = json.loads(config_data)
    return GitHubService(config["token"])
