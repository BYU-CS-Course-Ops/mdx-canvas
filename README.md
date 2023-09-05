# md-canvas
Storing canvas content in markdown files for easy editing, sharing, and version control.

# Installation

```
pip install md-canvas
```



## Quizzes

See [sample-quiz.md](markdown-files/sample-quiz.md) for a quiz example.

The basic structure is as follows:
```xml
<quiz>
    <question type="free-response">
        What is the capital of France?
        <right>Paris</right>
    </question>
    <question type="multiple-choice">
        What is the capital of Germany?
        <wrong>Bonn</wrong>
        <right>Berlin</right>
    </question>
    <question type="matching">
        Match the following countries with their corresponding capitals.
		<left>France</left>
		<right>Paris</right>
		
		<left>Germany</left>
		<right>Berlin</right>
    </question>
</quiz>
```

