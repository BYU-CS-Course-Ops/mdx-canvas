We'd love for you to add to the project! Current tasks include adding support for all question types and options. A thorough survey of canvas content also needs to be conducted, so that we can accurately track our progress in our ability to post and store content. Before contributing, please read how the tool works. You might also consider reading the [README](https://github.com/beanlab/md-canvas/blob/main/README.md).

## Document Parsing

Practical quiz creation is dependent on functional and seamless parsing. A simple quiz should be easily created in a document:
```xml
<quiz>
	<settings title="Sample Quiz" points_possible="40">
	</settings>
	
	<question type = "multiple-choice">
		What is 2 + 3?
		<correct>5</correct>
		<incorrect>4</incorrect>
	</question>
</quiz>
```

To help with ease of use, the file's extension is customizable. Adding a .md, .xml, or .jinja extension to the file is not necessary for the parser to function, but each could optimize highlighting in the text editor of a user's choice. XML and HTML are particularly useful for matching opening and closing tags.

```xml
<question> </question>
```

The html parser `Beautiful Soup` is used to process the tags and interpret quiz structure. 

```python
from bs4 import BeautifulSoup  
from bs4.element import Tag
```

Beautiful Soup is explicitly used in a single method—the parse method of the Document Parser class—but all lower Parser classes expect a `Tag` as a parameter. All documents are passed to a Document Parser as text. Beautiful Soup then identifies all of the highest level `Tag` objects in the document.

```python
def parse(self, text):
	document = []  
	soup = BeautifulSoup(text, "html.parser")  
	for tag in soup.children: # Highest Tags
```

If `parse()` was run on the example quiz above, tag would take the value of the `quiz` tag. Other possible high-level tags include `assignment` and `module`. 

After getting the tag, the document parser identifies the appropriate element parser to use.

```python
	parser = self.element_processors.get(tag.name, None)  
	if parser:  
	    elements = parser.parse(tag)
```

The element parsers are defined  when the Document Parser is constructed. Each element parser corresponds to a high-level `Tag`. A document can have multiple high-level `Tag`s, such as an assignment and an override. This is an especially useful combination, since overrides specify exceptions to assignment due dates and visibility.

```python
self.element_processors = {  
    "quiz": QuizParser(self.markdown_processor, group_indexer, self.date_formatter),  
    "assignment": AssignmentParser(self.markdown_processor, group_indexer, self.date_formatter),  
    "page": PageParser(self.markdown_processor, self.date_formatter),  
    "module": ModuleParser(),  
    "override": OverrideParser(self.date_formatter)  
}
```

Each parser needs certain functions as arguments. Most take a `markdown_processor` function, which takes in markdown text and converts it to html. The `group_indexer` function should take the name of an assignment group (e.g. Projects, Labs) and return the index of that group within Canvas. The date formatter should take a string and conform it to ISO format, which is the standard Canvas supports.

Each element parser takes in a tag (quiz, assignment, etc.) and returns a list of Python objects that mimics the structure the Canvas API expects. These objects are eventually required as dictionaries, so each high-level parser returns a dictionary or list of dictionaries.

```python
def parse(self, text):
	document = []  
	soup = BeautifulSoup(text, "html.parser")  
	for tag in soup.children: # Highest Tags
		elements = parser.parse(tag)
		if not isinstance(elements, list):  
			elements = [elements]  
		for element in elements:  
			new_elements = self.create_elements_from_template(element)  
			document.extend(new_elements)
```

## Template Parsing
Each element in a document can be used as a template to generate similar documents in Canvas. This is useful for the common scenario where an assignment shares many similarities with a whole class of  assignments, with a few small changes. 

Template arguments are specified using a markdown table, inside a replacements tag:
```xml
<quiz>  
<replacements>
|Title|Due|
|---|---|
|Lab 1a Quiz|Sep 12|
|Lab 1b Quiz|Sep 14|
|Lab 1c Quiz|Sep 19|
|Lab 2a Quiz|Sep 21|
|Lab 2b Quiz|Sep 26|
|Lab 2c Quiz|Sep 28|
|Lab 2d Quiz|Oct 03|
|Lab 3a Quiz|Oct 05|
|Lab 3b Quiz|Oct 10|
|Lab 3c Quiz|Oct 12|
|Lab 3d Quiz|Oct 17|
|Lab 3e Quiz|Oct 19|
|Lab 3f Quiz|Oct 24|
|Lab 4a Quiz|Nov 02|
|Lab 4b Quiz|Nov 07|
|Lab 4c Quiz|Nov 09|
|Lab 4d Quiz|Nov 14|
|Lab 4e Quiz|Nov 16|
|Lab 4f Quiz|Nov 21|
|Lab 5a Quiz|Nov 30|
|Lab 5b Quiz|Dec 05|
|Lab 5c Quiz|Dec 07|
|Lab 5d Quiz|Dec 12|
|Lab 6a Quiz|Dec 14|
|Lab 6b Quiz|Dec 16|
<replacements>

<settings title="{{Title}}" {{due_at="Due, 2023, 8:00 AM"}} points_possible="10" assignment_group="Labs" shuffle_answers="False" allowed_attempts="-1">
</settings>
</quiz>
```

The replacements are processed manually by splitting each row on the pipe `|` character. Each row will eventually become a separate item in Canvas. 

The templating (generating separate pieces of text for each replacement) is done using jinja. Jinja works efficiently, using minimal lines of code.

A Jinja environment is initialized in the Document Parser constructor:
```python
from jinja2 import Environment

self.jinja_env = Environment()
# This enables us to use the zip function in template documents
self.jinja_env.globals.update(zip=zip)
```

Jinja is then used in Document Parser's `create_elements_from_template()` method:
```python
# Element template is an object, turn it into text  
template_text = json.dumps(element_template, indent=4)  
  
# Use the text to create a jinja template  
template = self.jinja_env.from_string(template_text)  
  
elements = []  
for context in all_replacements:  
    # For each replacement, create an object from the template  
    elements.append(json.loads(template.render(context)))
```

The specifics of jinja's syntax can be found in [their documentation.]( https://jinja.palletsprojects.com/en/3.1.x/)
Some of jinja's most powerful features are accessed when the context contains lists and dictionaries. 

```html
{% for name, link in zip(Videos.names, Videos.links) %}  
<div class="bs-col-md kl_solid_border kl_border_radius_5">  
    <p><a class="ytp-share-panel-link" title="Share link" href="{{ link }}">{{ name }}</a></p>  
</div>  
{% endfor %}
```

The first and last lines define a `for` loop. `Videos` is a dictionary, containing `'names': [a list of video names]` and `'links': [a list of video links]`. 

Our tool supports lists and dictionaries through specific header formats.
  
| Day_Name | list: Videos.names                      | list: Videos.links                                         |  
|----------|-----------------------------------------|------------------------------------------------------------|  
| Day 1    | My Introduction, Introduction to CS 110 | https://youtu.be/14WS_bHXm_M, https://youtu.be/uVlKzVlNbjM |  
| Day 2    | Introduction to Bit                     | https://youtu.be/7Lo8A69q9gA                               |  

Any cell that is a list should have a header that begins with `list: `. To create a dictionary, the user should use headers like `Videos.names` and `Videos.links`. Videos will be created as a dictionary, with `names` and `links` as keys.

```python
replacements = defaultdict(dict)  
for header, value in zip(headers, line):  
    if header.startswith("list:"):  
        header = header[5:].strip()  # Remove 'list: ' from header  
        value = value.split(",")     # Split the value into a list  
  
    if "." in header:  
        # Interpret the header as "object.attribute"  
        obj, attribute = header.split(".")  
        replacements[obj][attribute] = value  
    else:  
        replacements[header] = value
```

## Date Parsing

Dates are 
