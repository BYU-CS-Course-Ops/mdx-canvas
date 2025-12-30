import json
import sys


class DeploymentReport:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.report = {
            "deployed_content": [],
            "content_to_review": [],
            "error": ""
        }

    def add_deployed_content(self, rtype: str, content_name: str, content_url: str = None):
        self.report["deployed_content"].append((rtype, content_name, content_url))

    def get_deployed_content(self):
        return self.report["deployed_content"]

    def add_content_to_review(self, quiz_name: str, link_to_quiz: str):
        self.report["content_to_review"].append([quiz_name, link_to_quiz])

    def get_content_to_review(self):
        return self.report["content_to_review"]

    def add_error(self, error: Exception):
        error_type = type(error).__name__
        error_msg = str(error)
        self.report["error"] = f"{error_type}: {error_msg}"

    def save_report(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(json.dumps(self.report, indent=4))

    def print_report(self):
        # TODO: Do we want to print to stderr instead?
        print(json.dumps(self.report, indent=4) + '\n')
