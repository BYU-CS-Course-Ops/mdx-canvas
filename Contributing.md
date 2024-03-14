We'd love for you to add to the project! Current tasks include adding support for all question types and options. A thorough survey of canvas content also needs to be conducted, so that we can accurately track our progress in our ability to post and store content. Before contributing, please read this document to understand how the tool works. You may also consider reading the [README](https://github.com/beanlab/md-canvas/blob/main/README.md). 

## Purpose

The goal of the local-canvas tool is to store Canvas content in local documents. Canvas is an LMS, or Learning Management system, used by many schools and universities in the US. Canvas provides several types of content:
- Quizzes
- Assignments
- Pages
- Discussions
- Files

For simplicity, this document will refer to these content elements as pages, since they are displayed as webpages in Canvas.

Canvas is an excellent solution for content managers due to its high-functioning API, or Application Programming Interface. APIs enable programmers to interact with websites and databases automatically. Automatic interaction saves time **as long as the available tools are easy to use**.

Local-canvas aims to be a simple, intuitive, and powerful way to interact with the Canvas API. As a wrapper, it does significant work behind-the-scenes. 

#### Sequential Information Flow
1. A content creator creates a set of local documents on their computer.
	-  These could be quizzes, assignments, discussions, etc.
2. A content manager points local-canvas to the documents, as well as the appropriate course.
3. Local-canvas reads the file as a text.
	1. Local-canvas parses the text, interpreting nested and sequential text as structured data.
	2. Templating allows local-canvas to turn one document into several pages.
	3. The structured data is reformatted:
		1. Dates are converted to ISO format.
		2. Images are uploaded to canvas, assigned to folders, and linked.
	4. The data is restructured to match the parameters of the Canvas API.
4. The Canvas API accepts the data, and modifies the course as requested.

## Understanding local-canvas

Parsing means turning text into structured data.

**After reading this document, you should understand:**
- How we parse local documents using Beautiful Soup
- How we parse individual elements by extracting elements from Tags
- How we parse page templates using jinja
- How we manually parse template arguments
- How we convert text elements to objects in Python
- How we provide dictionaries of attributes as arguments to the Canvas API

## Document Parsing

A user should easily be able to create quizzes. To help the user, we offer a simple syntax, as shown in this example:

```xml
<quiz>
	<settings title="Example Quiz" points_possible="40">
	</settings>
	
	<question type = "multiple-choice">
		What is 2 + 3?
		<correct>5</correct>
		<incorrect>4</incorrect>
	</question>
</quiz>
```

We parse the document in pieces, giving us the flexibility to offer this syntax. The basic building block is a tag, which is commonly used in other formats like html.

A tag element has this structure:

```xml
<quiz (attributes)> # Opening tag
Content
<quiz> # Closing tag
```

`Beautiful Soup` is a Python Library that is typically used to interpret html used in a webpage. We use it to understand the structure of tags in the document. We import `Beautiful Soup` from `bs4` and `Tag` from `bs4.element`. A `Tag` is a specific object type with certain useful attributes.

All documents are passed to a Document Parser as text. Beautiful Soup then identifies all of the highest level `Tag` objects in the document.

```python
def parse(self, text):
	document = []  
	soup = BeautifulSoup(text, "html.parser")  
	for tag in soup.children: # Highest Tags
```

If `parse()` was run on the example quiz above, tag would take the value of the `quiz` tag. Other possible high-level tags include `assignment`, `module`, and `override`.

A document could contain multiple tags, such as an assignment and an override. This is an especially useful combination, since overrides specify exceptions to assignment due dates and visibility, and a content creator might design an assignment for a specific section of their class.

After getting the tag, the document parser identifies the appropriate element parser to use, then calls the parser's `parse` function on the `Tag`.

```python
    parser = self.child_walkers.get(tag.name, None)
if parser:
	elements = parser.parse(tag)
```

The element parsers are defined  when the Document Parser is constructed. Each element parser corresponds to a different `Tag`.

```python
self.child_walkers = {
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

Each element in a document can be used as a template to generate similar documents in Canvas. This is useful for the common scenario where an assignment shares many similarities with several other assignments, with a few small changes. 

Template arguments are specified using a [markdown-style table](https://www.markdownguide.org/cheat-sheet/), inside a `<replacements>` tag:
```xml
<override>  
<template-arguments>  
  
| Day_Name | Due_At |  
|----------|--------|  
| Day 1    | Sep 5  |  
| Day 2    | Sep 7  |  
| Day 3    | Sep 12 |  
| Day 4    | Sep 14 |  
| Day 5    | Sep 19 |  
  
</template-arguments>  
<section>How to Program (TESTING)</section>  
<assignment title="{{ Day_Name }}" due_at="{{ Due_At }}, 2023, 11:59 PM"></assignment>  
</override>
```

Here, the `Day_Name` and `Due_At` variables are replaced with the different values in the table.

The replacements are processed manually by splitting each row on the pipe `|` character. Each row will eventually become a separate item in Canvas. 

The templating (generating separate pieces of text for each replacement) is done using jinja. Jinja is a python library specifically used for templating, and it works on documents with a syntax similar to python. Jinja provides access to variables, expressions, and loops within a document, and is especially targeted towards created templated webpages using html. Since our document structure is similar to html, jinja is perfect for templating canvas pages.

Specifically, jinja acts on this section of the override template:
```xml
<override>
<section>How to Program (TESTING)</section>
<assignment title="{{ Day_Name }}" due_at="{{ Due_At }}, 2023, 11:59 PM"></assignment>
</override>
```

Here, `{{ Day_Name }}` is a variable. When we provide the template with context, such as `{"Day_Name": "Day 2"}`, jinja will replace `{{ Day_Name }}` with `Day 2`.

We use jinja in the Document Parser's `create_elements_from_template()` method. This method receives a Python object from an element parser. We turn the element into a string using json, then jinja creates a template from that string.
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

The `template.render()` expression accepts a context, which is how we replace variables in the document with specific pieces of text. The `.render()` method replaces each template argument appropriately, returning a string with everything replaced. Then `json.loads()` function takes that string and returns a Python object representing the structured data.

The specifics of jinja's syntax can be found in [their documentation.]( https://jinja.palletsprojects.com/en/3.1.x/)
Some of jinja's most powerful features are accessed when the context contains lists and dictionaries. 

```html
{% for name, link in zip(Videos.names, Videos.links) %}  
<div class="bs-col-md kl_solid_border kl_border_radius_5">  
    <p><a class="ytp-share-panel-link" title="Share link" href="{{ link }}">{{ name }}</a></p>  
</div>  
{% endfor %}
```

The first and last lines frame a `for` loop. This for loop creates multiple div blocks, one for each name-link pair in Videos. `Videos` is a dictionary, containing `'names': [a list of video names]` and `'links': [a list of video links]`. We zip the two lists together, so that we can iterate through both lists at the same time.

Our tool supports lists and dictionaries through specific header formats.
  
| Headers>| list: Videos.names                      | list: Videos.links                                         |  
|----------|-----------------------------------------|------------------------------------------------------------|  
| Day 1    | My Introduction, Introduction to CS 110 | https://youtu.be/14WS_bHXm_M, https://youtu.be/uVlKzVlNbjM |  
| Day 2    | Introduction to Bit                     | https://youtu.be/7Lo8A69q9gA                               |  

Any cell that contains a list should have a header that begins with `list: `. To create a relationship between columns, the user should use headers like `Videos.names` and `Videos.links`. Videos will be  interpreted as an object, with `names` and `links` as attributes.

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

## A note on File extensions

The file's extension is customizable for to help the user view their file. File extensions such as .md, .xml, or .jinja are not necessary for parsing, but modern text editors highlight text differently depending on the file extension. 

##### XML / HTML:
XML and HTML are particularly useful for viewing matches between opening and closing tags.

```xml
<question> </question>
```

##### Markdown:
Markdown is useful for displaying tables, and for creating course content. The markdown processor function will convert all markdown into html, which canvas renders.
[Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)

```md
| Header 1| Header 2|
| --- | --- |
| cell 1 | cell 2|
```

| Header 1| Header 2|
| --- | --- |
| cell 1 | cell 2|

##### Jinja
We use jinja to process page templates.
[Jinja templating guide](https://jinja.palletsprojects.com/en/3.1.x/templates/)

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

## Date Parsing

Dates need to be passed to the Canvas API in ISO format, or as datetime objects:

```cpp
2013-01-23T23:59:00-07:00
```

We use the datetime module to convert other date formats to ISO.

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

To interpret these and other formats, see [this date tutorial.](https://www.programiz.com/python-programming/datetime/strptime) 

# Using the Canvas API
## Canvas Course Objects

The Canvas Python API provides Course objects. Course objects are specific to a class, and need authorization to be retrieved. 

```python
canvas = Canvas(api_url, api_token)  
course: Course = canvas.get_course(course_id)
```

The user provides authorization (an api token) as a parameter to the `Canvas()` constructor. 

The user can create an API token on Canvas by navigating this path:
Account -> Settings -> Approved Integrations -> New Access Token

The course id is found in the url of the course.

## Creating a Page

We follow a similar process to create each type of page. Quizzes are more complicated, since they require additional information pertaining to each question and answer. Quizzes are explained in the next section.

## Creating a Quiz

Once we have the Course object, creating a quiz is simple.

```python
canvas_quiz = course.create_quiz(quiz=element["settings"])
```

The `create_quiz()` function takes a keyword parameter `quiz`, which is expected to be a dictionary of quiz settings.

When parsing each quiz or other element, we store the necessary settings in a `<settings>` tag. 

The full list of settings the user can use are found here:
[https://canvas.instructure.com/doc/api/quizzes.html#Quiz](https://canvas.instructure.com/doc/api/quizzes.html#Quiz)

## Adding Questions to a Quiz

Questions must be added individually to a quiz. The `create_quiz()` function returns a `Quiz` object which we store for later use. The `create_question` function takes a keyword parameter `question`, which is expected to be a dictionary of question attributes.

```python
for question in questions:
    canvas_quiz.create_question(question=question)
```

The full attribute list for a question can be found in this reference: 
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

This is the expected structure for a matching question dictionary:

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

Again, the full attribute list for a question can be found in this reference: 
[https://canvas.instructure.com/doc/api/quiz_questions.html](https://canvas.instructure.com/doc/api/quiz_questions.html)

# Resources

The official guide to the Canvas Python API is found here: [https://canvasapi.readthedocs.io/en/stable/getting-started.html](https://canvasapi.readthedocs.io/en/stable/getting-started.html)

The Python API does not fully explain the parameters each function requires. You will need to consult the [REST API](https://canvas.instructure.com/doc/api/assignments.html) for that information.

##### Jinja documentation
- Writing templates
	- [Jinja templating guide](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- Adding features
	- [https://jinja.palletsprojects.com/en/3.1.x/]( https://jinja.palletsprojects.com/en/3.1.x/)

##### Markdown syntax:
- [Markdown cheat sheet](https://www.markdownguide.org/cheat-sheet/)

##### ISO format:
- [Python dateTime documentation](https://docs.python.org/3/library/datetime.html#format-codes)

##### Json conversion from string to objects:
- [Tutorial](https://www.w3schools.com/python/python_json.asp)
- [Documentation](https://docs.python.org/3/library/json.html)

# Contact Information

### Preston Raab - Primary Developer
- Email: [phr23@byu.edu](mailto:phr23@byu.edu)
### Gordon Bean - Advisor
- Email: [gbean@cs.byu.edu](mailto:gbean@cs.byu.edu)
