# Quiz Summary Template

After generating a quiz, ALWAYS display a summary using this exact format:

```
| # | Question Type | Topic        |
|---|---------------|--------------|
| 1 | [type] | [brief description] |
| 2 | [type] | [brief description] |
...

**Quiz Settings:**
- Shuffle answers: [yes/no]
- Allowed attempts: [number]
- Scoring policy: [policy]
- Time limit: [minutes or "None"]
```

## Example

| # | Question Type     | Topic                 |
|---|-------------------|-----------------------|
| 1 | Multiple Choice   | Capital of France     |
| 2 | True/False        | Earth's rotation      |
| 3 | Matching          | Countries to capitals |
| 4 | Fill-in-the-Blank | Chemical symbols      |
| 5 | Numerical         | Speed of light        |

**Quiz Settings:**

- Shuffle answers: yes
- Allowed attempts: 2
- Scoring policy: keep_highest
- Time limit: None