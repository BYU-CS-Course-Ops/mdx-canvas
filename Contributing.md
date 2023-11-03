We'd love for you to add to the project! Current tasks include adding support for all question types and options. A thorough survey of canvas content also needs to be conducted, so that we can accurately track our progress in our ability to post and store content. Before contributing, please read how the tool works. You may also consider reading the [README](https://github.com/beanlab/md-canvas/blob/main/README.md).

## The goal

The goal of the tool is to store Canvas content in local documents. Canvas is a LMS, or Learning Management system, used by many schools and universities in the US. For people who manage content, one of its major draws is its API, or Application Programming Interface. APIs enable programmers to interact with websites and databases automatically. Automatic interaction saves time interacting with a website as long as the available tools are easy to use.



## Understanding the Tool

After reading this document, you should understand:
- How quiz documents are parsed as a whole (turning text into structured data)
- How 


## Document Parsing

A user should easily be able to create a simple quiz, like this example:

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

The CanvasTo help with that, we parse the document ourselves. 

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

A document can have multiple high-level `Tag`s, such as an assignment and an override. This is an especially useful combination, since overrides specify exceptions to assignment due dates and visibility.

After getting the tag, the document parser identifies the appropriate element parser to use.

```python
	parser = self.element_processors.get(tag.name, None)  
	if parser:  
	    elements = parser.parse(tag)
```

The element parsers are defined  when the Document Parser is constructed. Each element parser corresponds to a high-level `Tag`. 

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

## A note on File extensions

The file's extension is customizable for viewing convenience. File extensions such as .md, .xml, or .jinja are not necessary; they only change how the text is displayed when editing. XML and HTML are particularly useful for matching opening and closing tags.

XML / HTML:

```xml
<question> </question>
```

MD: [Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)

| Header 1| Header 2|
| --- | --- |
| cell 1 | cell 2|

Jinja: [Jinja templating guide](https://jinja.palletsprojects.com/en/3.1.x/templates/)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Webpage</title>
</head>
<body>
    <ul id="navigation">
    {% for item in navigation %}
        <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
    {% endfor %}
    </ul>

    <h1>My Webpage</h1>
    {{ a_variable }}

    {# a comment #}
</body>
</html>
```

## Template Parsing
Each element in a document can be used as a template to generate similar documents in Canvas. This is useful for the common scenario where an assignment shares many similarities with a whole class of  assignments, with a few small changes. 

Template arguments are specified using a markdown-style table, inside a replacements tag:
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

Dates need to be passed to the Canvas API in ISO format:

```cpp
2013-01-23T23:59:00-07:00
```

Conveniently, we can use the datetime module to convert other date formats to ISO.

```python
from datetime import datetime
```

Our algorithm takes a date and returns a string. If the date is:
- None
	- We return None
- A datetime object
	- We use `datetime.isoformat(date)` to convert the date to a string
- A string in ISO format
	- ISO format is one of the acceptable formats
- A string in another acceptable format
	- We use `date = datetime.strptime(date, input_format)` to convert date to a datetime object, then to ISO format
- A string that is not a date
	- We return the string as is.
- A string that looks like a date, but in a format we can't convert
	- Raise an Exception

Canvas stores dates with timezones. We add a timezone so that Canvas can properly compare new dates with existing dates. 

```python
		# If the date doesn't have  a time zone, add one  
		if not "-" in date:  
			date = date + time_zone
		# Example time_zone: ' -0600'   (mountain time)
```

We check if the string matches several input formats. If it doesn't match, we raise an exception.

Current date formats are the following:
```js
"%b %d, %Y, %I:%M %p %z",  
"%b %d %Y %I:%M %p %z",  
"%Y-%m-%dT%H:%M:%S%z"
```

To interpret the formats, see [this website.](https://www.programiz.com/python-programming/datetime/strptime) 

## Canvas Course Objects

The Canvas Python API provides Course objects. Course objects are specific to a class, and need authorization to be retrieved. 

```python
canvas = Canvas(api_url, api_token)  
course: Course = canvas.get_course(course_id)
```

The user provides authorization (an api token) as a parameter to the `Canvas()` constructor. 

The user creates an API token on canvas by navigating this path:
Account -> Settings -> Approved Integrations -> New Access Token

The course id is found in the url of the course.

## Using the Canvas API to Create a Quiz

Once we have the Course object, creating a quiz is simple.

```python
canvas_quiz = course.create_quiz(quiz=element["settings"])
```

The `create_quiz()` function takes a keyword parameter `quiz`, which is expected to be a dictionary of quiz settings.

When parsing each quiz or other element, we store the necessary settings in a `<settings>` tag. 

The full list of settings the user can use are found here:
[https://canvas.instructure.com/doc/api/quizzes.html#Quiz](https://canvas.instructure.com/doc/api/quizzes.html#Quiz)

## Using the Canvas API to Add Questions to a Quiz

Questions must be added individually to a quiz. The `create_quiz()` function returns a `Quiz` object which we store for later use. The `create_question` function takes a keyword parameter `question`, which is expected to be a dictionary of question attributes.

```python
for question in questions:
    canvas_quiz.create_question(question=question)
```

The question attributes can be found in this reference: 
[https://canvas.instructure.com/doc/api/quiz_questions.html](https://canvas.instructure.com/doc/api/quiz_questions.html)

The user does not interact directly with the quiz questions API. Instead, we provide an easier format for creating quiz questions, and our parser does the rest of the work.

Each question type expects a different set of attributes. For example, a matching question requires:
- Question text
- Question type
- Points possible
- Comments if a student selects a correct answer
- Comments if a student selects an incorrect answer
- A list of answers, where each answer has:
	- A left match
	- A right match
	- An answer weight (Always 100 for matching questions)
- A new-line separated string of incorrect right matches

This is the expected structure for a question dictionary:

```python
question = {  
    "question_text": question_text,  
    "question_type": 'matching_question',  
    "points_possible": get_points(question_tag),  
    "correct_comments": get_correct_comments(question_tag),  
    "incorrect_comments": get_incorrect_comments(question_tag),  
    "answers": [  
        {  
            "answer_match_left": answer_left,  
            "answer_match_right": answer_right,  
            "answer_weight": 100  
        } for answer_left, answer_right in matches  
    ],  
    "matching_answer_incorrect_matches": distractor_text  
}
```

## Resources

The official guide to the Canvas Python API is found here: [https://canvasapi.readthedocs.io/en/stable/getting-started.html](https://canvasapi.readthedocs.io/en/stable/getting-started.html)

The Python API does not fully explain the parameters each function requires. You will need to consult the [REST API](https://canvas.instructure.com/doc/api/assignments.html) for that information.

The jinja documentation is found here: 
- Writing templates
	- [Jinja templating guide](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- Creating more features
	- [https://jinja.palletsprojects.com/en/3.1.x/]( https://jinja.palletsprojects.com/en/3.1.x/)

Markdown syntax:
- [Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)
