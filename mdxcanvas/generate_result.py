import json
import sys


class MDXCanvasResult:
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

    def add_error(self, error: str):
        self.json["error"] = error

    def output(self):
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(json.dumps(self.json, indent=4))

    def print(self):
        if self.json['deployed_content']:
            groups = {}
            for rtype, rid, url in self.json['deployed_content']:
                if url not in groups:
                    groups[url] = []
                groups[url].append((rtype, rid))

            print(' Deployed Content '.center(60, '-'))
            for url, resources in groups.items():
                resources_str = ', '.join(rid for _, rid in resources)
                print(f'{resources_str}: {url}')

        if self.json['content_to_review']:
            print(' Content to Review '.center(60, '-'))
            for rtype, rid, url in self.json['content_to_review']:
                print(f'{rid}: {url}')

        if self.json['error']:
            print(file=sys.stderr)
            print(self.json['error'], file=sys.stderr)
