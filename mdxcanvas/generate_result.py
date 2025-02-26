class MDXCanvasResult:
    def __init__(self):
        self.json = {
            "deployed_content": {},
            "content_to_review": []
        }

    def add_deployed_content(self, rtype: str, content_name: str):
        if rtype not in self.json["deployed_content"]:
            self.json["deployed_content"][rtype] = []
        self.json["deployed_content"][rtype].append(content_name)

    def has_deployed_content(self):
        return bool(self.json["deployed_content"])

    def add_content_to_review(self, quiz_name: str, link_to_quiz: str):
        self.json["content_to_review"].append([quiz_name, link_to_quiz])

    def has_content_to_review(self):
        return bool(self.json["content_to_review"])

    def get_content_to_review(self):
        return self.json["content_to_review"]

    def output(self):
        return self.json