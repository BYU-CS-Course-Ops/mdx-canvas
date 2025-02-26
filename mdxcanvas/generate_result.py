class MDXCanvasResult:
    def __init__(self):
        self.json = {
            "deployed_content": {},
            "updated_quizzes": [],
            "message": "",
            "status": "success"
        }

    def add_deployed_content(self, rtype: str, content_name: str):
        if rtype not in self.json["deployed_content"]:
            self.json["deployed_content"][rtype] = []
        self.json["deployed_content"][rtype].append(content_name)

    def has_deployed_content(self):
        return bool(self.json["deployed_content"])

    def add_updated_quiz(self, quiz_name: str, link_to_quiz: str):
        self.json["updated_quizzes"].append([quiz_name, link_to_quiz])

    def has_updated_quizzes(self):
        return bool(self.json["updated_quizzes"])

    def set_message(self, message: str):
        self.json["message"] = message

    def set_status(self, status: str):
        self.json["status"] = status

    def output(self):
        return self.json