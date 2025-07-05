# MDXCanvas

_MDXCanvas allows you to store canvas content in source code to the specified canvas instance_

## Installation 

To install MDXCanvas, use pip:

```bash
pip install mdxcanvas
```

Additionally, you will need a Canvas API Token 

## Usage

_fill_

To deploy content to Canvas run:

```bash 
mdxcanvas --course-info <course_info> <content_file>
```

**`course_info`**

```json

```

**`content_file.xml`**
```xml
<quiz title="Example Quiz">

<description>
    _include md_
</description>
    
<questions>
    <question type="multiple-choice">
        
    </question>
    <question type="true-false">
        
    </question>
</questions>
</quiz>
```

## Tutorials

### Course Info 

#### Group Weights

#### Title, etc.

### Supported Tags

- modules
- module items
- pages
- assignments
- quiz
- syllabus
- override
- announcement
- 

### Special Tags

- include
- zip
- file
- course-link

### Jinja Template

#### Global Args

#### Template Args

### CSS

### Demo Course

_link to demo course folder content_
