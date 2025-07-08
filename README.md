# MDXCanvas

MDXCanvas allows you to store canvas content in source code to the specified canvas instance=

## Installation 

To install MDXCanvas, use pip:

```bash
pip install mdxcanvas
```

Additionally, you will need a Canvas API Token which can be generated from your Canvas account settings and should be
stored as an environment variable named `CANVAS_API_TOKEN`.

## Usage

To deploy content to Canvas run:

```bash 
mdxcanvas --course-info <course_info> <content_file>
```

### `course_info`

The `course_info` argument is a JSON file that contains the course information and settings. It should include
the canvas api url: `CANVAS_API_URL`, course id: `CANVAS_COURSE_ID`, and the local time zone: `LOCAL_TIME_ZONE`.

See the below example: 

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver"
}
```

To see the full list of options, see the in-depth documentation on the [course info](#course-info-) section.

### `content_file`

There are several different file types that can be used as the `content_file`. 

Such as:
- `md`
- `xml`
- `html`
- `jinja
`
Below is an example of an XML file with a simple quiz.

```xml
<quiz title="Example Quiz">

<description>
    # Attention
    
    The following questions are aimed to test your understanding of the wizzarding world of **Harry Potter**.
</description>
    
<questions>
    
    <question type="multiple-choice">
        Who is the author of the Harry Potter series?
        
        <correct>J.K. Rowling</correct>
        <incorrect>J.R.R. Tolkien</incorrect>
        <incorrect>George R.R. Martin</incorrect>
        <incorrect>Stephen King</incorrect>
    </question>
    
    <question type="true-false" answer="true">
        Is Harry Potter a wizard?        
    </question>
    
</questions>
</quiz>
```

As seen in the example above, you can use `MD` to style the content.

See the [demo course](documents/demo_course) for more examples of content files.

## Tutorials

The following tutorials will show the full capabilities of MDXCanvas and how to use it to deploy content to Canvas and 
ultimately create a course.

### Course Info 

The `course_info` file is a JSON file that contains the course information and settings as previously mentioned. There
are additional options that can be included in the file to customize the course deployment. 

#### `COURSE_NAME`

Customize the name of the course 

```json
{
  "COURSE_NAME" : "Example Course"
}
```

#### `COURSE_CODE`

Customize the course code. This is often used to identify the course in a more concise manner.

```json
{
  "COURSE_CODE" : "EXAMPLE 101"
}
```

#### `COURSE_IMAGE`

Customize the course thumbnail, the image seen in the canvas dashboard. This should be an image file type such as PNG.

```json
{
  "COURSE_IMAGE" : "example_course_image.png"
}
```

#### `COURSE_INFO` Example

So a complete `course_info` file might look like this:

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver",
  "COURSE_NAME": "Example Course",
  "COURSE_CODE": "EXAMPLE 101",
  "COURSE_IMAGE": "example_course_image.png"
}
```

### Supported Tags

The following tags are supported in the content files to assist in creating the course content as you see fit.

#### `<item>` Tag

The `<item>` tag is used to define the items in a module. Each item can represent different types of content such as
assignments, quizzes, pages, etc. The type of item is determined by the `type` attribute of the `<item>` tag.

The `type` attribute can be one of the following:
- `subheader`
- `externalurl`
- `page`
- `assignment`
- `quiz`
- `file`

An `<item>` tag can look like the following:

```xml
<item type="page" title="Example Page"/>
```

Then also contain additional attributes such as `indent` to indicate the hierarchy of the item within the module.

```xml
<item type="assignment" title="Example Assignment" indent="1"/>
```

#### `<module>` Tag

The `<module>` tag is used to define the modules in the course. Each module tag contains `<item>` tags that represent 
the items in the module.

A `<module>` make look like the following:

```xml
<module title="Example Module 1">
    <item type="page" title="Introduction to the Course" />
    <item type="assignment" title="First Assignment" indent="1" />
    <item type="quiz" title="Module Quiz" indent="1" />
</module>
```

#### `<page>` Tag

The `<page>` tag is used create a page in the course. It can contain `MD`, `HTML`, or other content types.

A `<page>` tag can look like the following:

```xml
<page title="Example Page">
    # Welcome to the Example Page
    
    Things like headers and `MD` formatting can be used here.
    
    ## Code Example
    
    ```python
    def example_function():
        print("This is an example function.")
    ```
    
    ## Links
    You can also include links to other resources, such as 
    [Canvas Documentation](https://canvas.instructure.com/doc/api/).
    
    ## Table Example
    
    | Header 1 | Header 2 |
    |----------|----------|
    | Row 1    | Row 2    |
    | Row 3    | Row 4    |
</page>
```

#### `<assignment>` Tag

The `<assignment>` tag is used to create an assignment in the course which contains various attributes as well as a
description.

##### Attributes

###### `title`

The `title` attribute is as expected, it is the title of the assignment.

```xml
<assignment title="Example Assignment">

</assignment>
```

###### `due_at` 

The `due_at` attribute is used to set the due date and time for the assignment.

```xml
<assignment title="Example Assignment" 
            due_at="Jan 1, 2025, 11:59 PM">

</assignment>
```

###### `available_from` 

The `available_from` attribute is used to set the date and time when the assignment becomes available to students.

```xml
<assignment title="Example Assignment" 
            available_from="Jan 1, 2025, 9:00 AM">
    
</assignment>
```

###### `available_to`

The `available_to` attribute is used to set the date and time when the assignment is no longer available to students.

```xml
<assignment title="Example Assignment" 
            available_to="Jan 1, 2025, 11:59 PM">
            
</assignment>
```

###### `points_possible` 

The `points_possible` attribute is used to set the maximum points possible for the assignment.

```xml
<assignment title="Example Assignment" 
            points_possible="100">
            
</assignment>
```

###### `assignment_group` 

The `assignment_group` attribute is used to specify the assignment group that the assignment belongs to.

```xml
<assignment title="Example Assignment" 
            assignment_group="Example Group">

</assignment>
```

###### `submission_types` 

The `submission_types` attribute is used to specify the types of submissions allowed for the assignment. 

```xml
<assignment title="Example Assignment" 
            submission_types="external_tool">

</assignment>
```

For other submission types, see the 
[Canvas API documentation](https://canvas.instructure.com/doc/api/assignments.html#Assignment).

###### `external_tool_tag_attributes`

The `external_tool_tag_attributes` attribute is used to specify the attributes for the external tool used in the 
assignment.

It is used with the `submission_types` attribute set to `external_tool`. 

```xml
<assignment title="Example Assignment" 
            submission_types="external_tool"
            external_tool_tag_attributes="url=https://lti.int.turnitin.com/launch/gs-proxy">
           
</assignment>
```

Again, for more information on the attributes, see the 
Canvas API documentation](https://canvas.instructure.com/doc/api/assignments.html#Assignment).

##### Description

The description of the assignment is contained as a child tag within the `<assignment>` tag. It can formated in `MD` 
or `HTML`. 

```xml
<assignment title="Example Assignment">
    <description>
        # Example Assignment
        
        This is an example assignment description. You can use **Markdown** or _HTML_ to format the content.
        
        ## Instructions
        
        1. Read the assignment carefully.
        2. Complete the tasks as outlined.
        3. Submit your work by the due date.
    </description>
</assignment>
```

##### Assignment Example

The following example is a common assignment template we have used in CS courses:

```xml
<assignment
    title="Example Homework"
    due_at="Jan 1, 2025, 11:59 PM"
    available_from="Jan 1, 2025, 9:00 AM"
    available_to="Jan 1, 2025, 11:59 PM"
    points_possible="30"
    assignment_group="Homework" 
    submission_types="external_tool"
    external_tool_tag_attributes="url=https://lti.int.turnitin.com/launch/gs-proxy">

<description>

Complete the homework by following [these instructions](instructions).

Then upload your `.py` files to Gradescope.

</description>
</assignment>
```

#### `<quiz>` Tag

The `<quiz>` tag is used to create a quiz in the course. It can contain various attributes and child tags to define
the quiz structure, questions, and settings.

##### Attributes

There are several attributes that are also used in the `<assignment>` tag that can be used in the `<quiz>` tag. 

They include:
- `title`
- `due_at`
- `available_from`
- `available_to`
- `assignment_group`

Please see the [assignment section](#assignment-tag) for more information on these attributes.

The following are additional attributes that can be used in the `<quiz>` tag

###### `shuffle_answers`

By default, the answers to the quiz questions are not shuffled. To enable answer shuffling, set the `shuffle_answers`
attribute to `true`.

```xml
<quiz title="Example Quiz" 
      shuffle_answers="true">

</quiz>
```

###### `time_limit`

The `time_limit` attribute is used to set the time limit for the quiz in minutes. 

```xml
<quiz title="Example Quiz" 
      time_limit="30">
</quiz>
```

When not specified, the quiz will not have a time limit.

###### `allowed_attempts`

The `allowed_attempts` attribute is used to set the number of attempts allowed for the quiz. 

```xml
<quiz title="Example Quiz" 
      allowed_attempts="3">
</quiz>
```

To allow unlimited attempts, set the `allowed_attempts` attribute to `-1`.

###### `access_code`

THe `access_code` attribute is used to set an access code for the quiz. 

```xml
<quiz title="Example Quiz" 
      access_code="example_access_code">
</quiz>
```

When not specified, the quiz will not have an access code.

##### Description

The description of the quiz is contained similarly to the `<assignment>` tag, see the [assignment section](#assignment-tag)
for more information.

##### Questions

The questions of the quiz are contained within the `<questions>` tag, which is a child tag of the `<quiz>` tag. Each
question is defined using a `<question>` tag, which can have various attributes and child tags to define the question.

The following are the different-supported question types

###### `text`

The `text` question type is used to create a description or instruction for following questions. It does not require
an answer and is typically used to provide context or instructions for the quiz.

```xml
<quiz title="Example Quiz">
    <description>
        # Quiz Instructions
        
        Please read the following instructions carefully before attempting the quiz.
    </description>
    
    <questions>
        <question type="text">
            This is a text question that provides instructions for the subsequent questions.
        </question>
    </questions>
</quiz>
```

###### `true-false`

The `true-false` question type is used to create a true/false question. It requires an `answer` attribute to specify
the correct answer, which can be either `true` or `false`.

```xml
<quiz title="Example Quiz">
    <description>
        # True/False Question
        
        Please answer the following question.
    </description>
    
    <questions>
        <question type="true-false" answer="true">
            Is the sky blue?
        </question>
    </questions>
</quiz>
```

###### `multiple-choice`

The `multiple-choice` question type is used to create a multiple-choice question. It requires at least one
`correct` answer and can have multiple `incorrect` answers. The `correct` answer is the one that is considered correct
for the question.

```xml
<quiz title="Example Quiz">
    <description>
        # Multiple Choice Question
        
        Please select the correct answer from the options below.
    </description>
    
    <questions>
        <question type="multiple-choice">
            What is the capital of France?
            
            <correct>Paris</correct>
            <incorrect>London</incorrect>
            <incorrect>Berlin</incorrect>
            <incorrect>Madrid</incorrect>
        </question>
    </questions>
</quiz>
```

###### `multiple-answers`

The `multiple-answers` question type is used to create a question that allows multiple correct answers. It requires
at least one `correct` answer and can have multiple `incorrect` answers. The student can select more than one answer.

```xml
<quiz title="Example Quiz">
    <description>
        # Multiple Answers Question
        
        Please select all the correct answers from the options below.
    </description>
    
    <questions>
        <question type="multiple-answers">
            Which of the following are programming languages?
            
            <correct>Python</correct>
            <correct>JavaScript</correct>
            <incorrect>HTML</incorrect>
            <incorrect>CSS</incorrect>
        </question>
    </questions>
</quiz>
```

###### `matching`

The `matching` question type is used to create a question that requires students to match items from two lists.

You can also include distractors, which are incorrect options that students can select but are not part of the 
correct matches.

```xml
<quiz title="Example Quiz">
    <description>
        # Matching Question
        
        Please match the items from the left column to the items in the right column.
    </description>
    
    <questions>
        <question type="matching">
            Match the following countries with their capitals.
            
            <pair left="France" right="Paris"/>
            <pair left="Germany" right="Berlin"/>
            <pair left="Spain" right="Madrid"/>
            
            <distractors>
                <distractor>London</distractor>
                <distractor>Rome</distractor>
                <distractor>Lisbon</distractor>
            </distractors>
        </question>
    </questions>
</quiz>
```

###### `multiple-tf`

The `multiple-tf` question type is used to create a question that allows students to select multiple true/false
statements. It requires at least one `correct` answer and can have multiple `incorrect` answers.

```xml
<quiz title="Example Quiz">
    <description>
        # Multiple True/False Question
        
        Please select all the statements that are true.
    </description>
    
    <questions>
        <question type="multiple-tf">
            Which of the following statements are true?
            
            <correct>Python is a programming language.</correct>
            <incorrect>HTML is a programming language.</incorrect>
            <correct>JavaScript can be used for web development.</correct>
            <incorrect>CSS is a programming language.</incorrect>
        </question>
    </questions>
</quiz>
```

###### `fill-in-the-blank`

The `fill-in-the-blank` question type is used to create a question that requires students to fill in the missing
words or phrases in a sentence. It can have multiple blanks that need to be filled in.

```xml
<quiz title="Example Quiz">
    <description>
        # Fill in the Blank Question
        
        Please fill in the missing words in the sentence below.
    </description>
    
    <questions>
        <question type="fill-in-the-blank">
            The capital of France is [blank].
            
            <correct text="Paris" />
        </question>
    </questions>
</quiz>
```

###### `fill-in-multiple-blanks`

The `fill-in-multiple-blanks` question type is used to create a question that requires students to fill in
multiple blanks in a sentence. Each blank can have its own correct answer.

```xml
<quiz title="Example Quiz">
    <description>
        # Fill in Multiple Blanks Question
        
        Please fill in the missing words in the sentence below.
    </description>
    
    <questions>
        <question type="fill-in-multiple-blanks">
            The U.S. flag has [stripes] stripes and [stars] stars.
            <correct text="13" blank="stripes" />
            <correct text="50" blank="stars" />
        </question>
    </questions>
</quiz>
```

###### `fill-in-multiple-blanks-filled-answers`

The `fill-in-multiple-blanks-filled-answers` question type is similar to the `fill-in-multiple-blanks` type, but it
allows you to specify the correct answers directly in the question text. 

```xml
<quiz title="Example Quiz">
    <description>
        # Fill in Multiple Blanks with Filled Answers Question
        
        Please fill in the missing words in the sentence below.
    </description>
    
    <questions>
        <question type="fill-in-multiple-blanks-filled-answers">
            The U.S. flag has [13] stripes and [50] stars.
        </question>
    </questions>
</quiz>
```

###### `essay`

The `essay` question type is used to create a question that requires students to write an essay or a long-form
response. It does not require an answer and is typically used for open-ended questions.

```xml
<quiz title="Example Quiz">
    <description>
        # Essay Question
        
        Please write an essay on the following topic.
    </description>
    
    <questions>
        <question type="essay">
            Discuss the impact of technology on modern education.
        </question>
    </questions>
</quiz>
```

###### `file-upload`

The `file-upload` question type is used to create a question that requires students to upload a file as their
answer. It does not require an answer and is typically used for assignments that require file submissions.

```xml
<quiz title="Example Quiz">
    <description>
        # File Upload Question
        
        Please upload a file as your answer to the following question.
    </description>
    
    <questions>
        <question type="file-upload">
            Upload your project files for review.
        </question>
    </questions>
</quiz>
```

###### `numerical`

The `numerical` question type is used to create a question that requires students to provide a numerical answer.

There are several attributes that can be used to specify the correct answer and the acceptable range of answers.

**Exact Answer**

The `exact_answer` attribute is used to specify the exact answer for the question. 

```xml
<quiz title="Example Quiz">
    <description>
        # Numerical Question
        
        Please provide the exact answer to the following question.
    </description>
    
    <questions>
        <question type='numerical' numerical_answer_type="exact">
            Give one possible value for x. The margin of error is +- 0.0001.
    
            (x - pi)^2 = (x - pi)
    
            <correct answer_exact='3.14159' answer_error_margin='0.0001' />
    
            <correct answer_exact='4.14159' answer_error_margin='0.0001' />
        </question>
    </questions>
</quiz>
```

**Range Answer**

The `range_answer` attribute is used to specify a range of acceptable answers for the question. 

```xml
<quiz title="Example Quiz">
    <description>
        # Numerical Question
        
        Please provide a value within the specified range.
    </description>
    
    <questions>
        <question type='numerical' numerical_answer_type="range">
            Give one possible value for x.
    
            1 &lt;= x^2 &lt;= 100
    
            <correct answer_range_start='1' answer_range_end='10' />
    
            <correct answer_range_start='-10' answer_range_end='-1' />
        </question>
    </questions>
</quiz>
```

**Precision Answer**

The `precision_answer` attribute is used to specify the precision of the answer for the question. 

```xml
<quiz title="Example Quiz">
    <description>
        # Numerical Question
        
        Please provide a value with the specified precision.
    </description>
    
    <questions>
        <question type='numerical' numerical_answer_type="precision">
            What is the value of pi?
    
            Ensure your answer gives at least 5 digits.
    
            <correct answer_approximate='3.14159' answer_precision='5' />
        </question>
    </questions>
</quiz>
```

##### Quiz Example

The following is an example of a quiz that includes various question types:

```xml
<quiz title="Example Quiz" 
      due_at="Jan 1, 2025, 11:59 PM"
      available_from="Jan 1, 2025, 9:00 AM"
      available_to="Jan 1, 2025, 11:59 PM"
      assignment_group="Quizzes" 
      shuffle_answers="true"
      time_limit="30"
      allowed_attempts="3">
      
    <description>
        This is an example quiz that includes various question types.
    </description>

    <questions>
        <question type="text">
            This is a text question that provides instructions for the subsequent questions.
        </question>
        
        <question type="true-false" answer="true">
            Is the sky blue?
        </question>
        
        <question type="multiple-choice">
            What is the capital of France?
            
            <correct>Paris</correct>
            <incorrect>London</incorrect>
            <incorrect>Berlin</incorrect>
            <incorrect>Madrid</incorrect>
        </question>
        
        <question type="multiple-answers">
            Which of the following are programming languages?
            
            <correct>Python</correct>
            <correct>JavaScript</correct>
            <incorrect>HTML</incorrect>
            <incorrect>CSS</incorrect>
        </question>
        
        <question type="matching">
            Match the following countries with their capitals.
            
            <pair left="France" right="Paris"/>
            <pair left="Germany" right="Berlin"/>
            <pair left="Spain" right="Madrid"/>
            
            <distractors>
                <distractor>London</distractor>
                <distractor>Rome</distractor>
                <distractor>Lisbon</distractor>
            </distractors>
        </question>
    
        <question type="multiple-tf">
            Which of the following statements are true?
            
            <correct>Python is a programming language.</correct>
            <incorrect>HTML is a programming language.</incorrect>
            <correct>JavaScript can be used for web development.</correct>
            <incorrect>CSS is a programming language.</incorrect>
        </question>
    
        <question type="fill-in-the-blank">
            The capital of France is [blank].
            
            <correct text="Paris" />
        </question>
    </questions>
</quiz>
```    

#### `<syllabus>` Tag

The `<syllabus>` tag is used to create a syllabus page in the course it is automatically stored in the course as the
syllabus page. 

```xml
<syllabus>
    This is the **epic** syllabus. :)
</syllabus>
```

#### `<override>` Tag

_fill_

#### `<announcement>` Tag

_fill_

### Special Tags

The following tags are used to include additional content or files in the course or to create more complex structures.

#### `<include>` Tag

The `<include>` tag is used to include content from another file into the current file. This is useful for
reusing content across multiple files or for organizing content into smaller, manageable pieces.

Say you have a file named `example.md` that contains the following content:

```md
# Example Instruction

This is an example of how to include content from another file using the `<include>` tag.
This content can be reused in multiple places without duplicating it.
You can also include code snippets, images, or any other content that you want to share across multiple files.
```
You can include this content in another file using the `<include>` tag like this:

```xml
<assignment title="Example Assignment">
    <description>
        <include file="example.md" />
    </description>
</assignment>
```

#### `<zip>` Tag

The `<zip>` tag is used to include a zip file in the course. This is useful for including multiple files or resources
that are related to a specific topic or assignment.

The `zip` tag has several attributes that can be used to customize the zip file inclusion:
- `name`: The name of the zip file to be included in the course.
- `path`: The path to the zip file that you want to include in the course.
- `additional_files`: Additional files that should be included in the zip file.
- `priority_path`: A path that should be prioritized when including files from the zip file.
- `exclude`: A regular expression pattern to exclude certain files from the zip file.

```xml
<assignment title="Example Homework">
    <description>
        Please download the following zip file for the assignment resources.
        
        <zip 
                name="example_homework.zip" 
                path="zip_target" 
                additional_files="more_file" 
                priority_path="zip_priority" 
                exclude="no_.*"
        />
    </description>
</assignment>
```

#### `<file>` Tag

The `<file>` tag is used to include a file in the course. This is useful for including files such as images,
documents, or other resources that are related to a specific topic or assignment. It is similar to the `<zip>` tag,
but it is used for single files rather than zip files.

```xml
<assignment title="Example Assignment">
    <description>
        Please download the following file for the assignment resources.
        
        <file name="example_file.pdf" path="path/to/example_file.pdf" />
    </description>
</assignment>
```

#### `<course-link>` Tag

_file_

### Jinja Template

A big part of MDXCanvas is the ability to use Jinja templates to create dynamic content. Which aids in creating 
content such as homeworks, project, or other course materials that have a generic structure but have minor variations, 
such as different due dates, assignment names, or other parameters.

Templating allows you to define a structure for your content and then fill in the specific details using variables.

The base for each template is some content tag such as `<assignment>`, `<quiz>`, or `<page>`. Which can then be
filled in with Jinja variables and logic to create dynamic content.

#### Jinja Example

```xml
<assignment title="{{ assignment_name }}"
            due_at="{{ due_date }}"
            available_from="{{ available_from }}"
            available_to="{{ available_to }}"
            points_possible="{{ points_possible }}"
            assignment_group="{{ assignment_group }}">

    <description>
        # {{ assignment_name }}
        
        Please complete the assignment by the due date.
        
        ## Instructions
        
        {{ instructions }}
    </description>
</assignment>
```

#### Global Args



#### Template Args

### CSS

### Demo Course

_link to demo course folder content_
