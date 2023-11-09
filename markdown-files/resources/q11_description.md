Match each block of code with the pattern it demonstrates:

Code Block A:

```python
def find_optimal_venue(venues):
    optimal = None
    for venue in venues:
        if optimal is None or score(optimal) < score(venue):
            optimal = venue
    return optimal
```


Code Block B:

```python
def convert_to_metric(mileage_reports):
    new_reports = []
    for origin, destination, miles, time in mileage_reports:
        kilometers = convert_to_km(miles)
        new_reports.append((origin, destination, kilometers, time))
    return new_reports
```


Code Block C:

```python
def identify_priority_cases(cases):
    priorities = []
    for case in cases:
        if is_priority(case):
            priorities.append(case)
    return priorities
```


Code Block D:

```python
def count_points(games):
    total = 0
    for game in games:
        team1, team2, team1_points, team2_points, location, date = game
        total = total + team1_points + team2_points
    return total
```