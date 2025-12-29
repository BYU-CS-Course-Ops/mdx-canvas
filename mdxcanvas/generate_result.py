import json
import sys


class DeploymentReport:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.json = {
            "deployed_content": [],
            "content_to_review": [],
            "error": ""
        }

    def add_deployed_content(self, rtype: str, content_name: str, content_url: str = None):
        self.json["deployed_content"].append((rtype, content_name, content_url))

    def add_content_to_review(self, quiz_name: str, link_to_quiz: str):
        self.json["content_to_review"].append([quiz_name, link_to_quiz])

    def get_content_to_review(self):
        return self.json["content_to_review"]

    def add_error(self, error: Exception):
        error_type = type(error).__name__
        error_msg = str(error)
        self.json["error"] = f"{error_type}: {error_msg}"

    def output(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(json.dumps(self.json, indent=4))

    def print(self):
        print(json.dumps(self.json, indent=4) + '\n')
