import json
from collections import defaultdict


class Templater:
    def __init__(self, jinja_env, path_to_files):
        self.jinja_env = jinja_env
        self.path_to_files = path_to_files
    
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
    
    def parse_psv(self, headers, lines):
        """
        Parse a pipe-separated value (PSV) file into a list of dictionaries.
        """
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
    
    
