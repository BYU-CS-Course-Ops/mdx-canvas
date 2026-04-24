import json
import sys


class DeploymentReport:
    def __init__(self, output_file: str | None = None):
        self.output_file = output_file
        self.report = {
            "deployed_content": [],
            "content_to_review": [],
            "error": ""
        }

    def add_deployed_content(self, rtype: str, content_name: str, content_url: str | None = None):
        self.report["deployed_content"].append((rtype, content_name, content_url))

    def get_deployed_content(self):
        return self.report["deployed_content"]

    def add_content_to_review(self, quiz_name: str, link_to_quiz: str):
        if [quiz_name, link_to_quiz] not in self.report["content_to_review"]:
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
        DETAIL_THRESHOLD = 20

        deployed = self.report['deployed_content']
        if deployed:
            type_counts = {}
            for rtype, _, _ in deployed:
                type_counts[rtype] = type_counts.get(rtype, 0) + 1

            print(' Deployed Content '.center(60, '-'))
            type_width = max(len('Type'), max(len(t) for t in type_counts))
            count_width = max(len('Count'), max(len(str(c)) for c in type_counts.values()))
            print(f'{"Type".ljust(type_width)}  {"Count".rjust(count_width)}')
            print(f'{"-" * type_width}  {"-" * count_width}')
            for rtype in sorted(type_counts):
                print(f'{rtype.ljust(type_width)}  {str(type_counts[rtype]).rjust(count_width)}')
            print(f'{"Total".ljust(type_width)}  {str(len(deployed)).rjust(count_width)}')

            if len(deployed) <= DETAIL_THRESHOLD:
                groups = {}
                for rtype, rid, url in deployed:
                    groups.setdefault(url, []).append((rtype, rid))
                print()
                for url, resources in groups.items():
                    resources_str = ', '.join(rid for _, rid in resources)
                    print(f'{resources_str}: {url}')

        if self.report['content_to_review']:
            print(' Content to Review '.center(60, '-'))
            for name, url in self.report['content_to_review']:
                print(f'{name}: {url}')

        if self.report['error']:
            print(file=sys.stderr)
            print(self.report['error'], file=sys.stderr)
