# parse the yaml file and return the data
from pathlib import Path

from strictyaml import load, Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, YAMLError, Bool

from document_schema import schema


def parse_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        text = file.read()

    try:
        document = load(text, schema).data
        return document
    except YAMLError as error:
        print(error)




class DocumentParser:
    def __init__(self, path_to_resources: Path, path_to_canvas_files: Path, markdown_processor: ResourceExtractor,
                 time_zone: str,
                 group_identifier=lambda x: 0):
        self.path_to_resources = path_to_resources
        self.path_to_files = path_to_canvas_files
        self.markdown_processor = markdown_processor
        self.date_formatter = lambda x: make_iso(x, time_zone)

        self.jinja_env = Environment()
        # This enables us to use the zip function in template documents

        self.jinja_env.globals.update(zip=zip, split_list=lambda sl: [s.strip() for s in sl.split(';')])

        parser = Parser()


    def parse(self, text):
        # Let's use yaml instead of BeautifulSoup
        document = []
        doc = load(text, schema).data



        return document

    def create_elements_from_template(self, element_template):
        if not (all_replacements := element_template.get("replacements", None)):
            return [element_template]

        # Element template is an object, turn it into text
        template_text = json.dumps(element_template, indent=4)

        # Use the text to create a jinja template
        template = self.jinja_env.from_string(template_text)

        elements = []
        for context in all_replacements:
            for key, value in context.items():
                context[key] = value.replace('"', '\\"')
            # For each replacement, create an object from the template
            rendered = template.render(context)
            element = json.loads(rendered)
            elements.append(element)

        # Replacements become unnecessary after creating the elements
        for element in elements:
            del element["replacements"]
        return elements

    def parse_template_data(self, template_tag):
        """
        Parses a template tag into a list of dictionaries
        Each dictionary will become a canvas object
        Converts the following:
        | header1 | header2    |
        |---------|------------|
        | first   | quiz       |
        | second  | assignment |
        into
        [
            {
                "header1": "first",
                "header2": "quiz"
            },
            {
                "header1": "second",
                "header2": "assignment"
            }
        ]
        """
        if template_tag.get("filename"):
            csv = (self.path_to_files / template_tag.get("filename")).read_text()
            headers, *lines = csv.split('\n')
        else:
            headers, separator, *lines = get_img_and_text_contents(template_tag).strip().split('\n')
            # Remove whitespace and empty headers
            headers = [h.strip() for h in headers.split('|') if h.strip()]
            lines = [line for left_bar, *line, right_bar in [line.split('|') for line in lines]]

        data = []
        for line in lines:
            line = [phrase.strip() for phrase in line]

            replacements = defaultdict(dict)
            for header, value in zip(headers, line):
                replacements[header] = value

            data.append(replacements)
        return data



if __name__ == "__main__":
    document = parse_yaml("Midterm.yaml")
    print(document)
