# parse the yaml file and return the data

from strictyaml import load, Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, YAMLError, Bool

# Define the schema for the yaml file
schema = Map({
    "title": Str(),
    "type": Enum(["assignment", "quiz", "page"]),
    Optional("due_at"): Str(),
    Optional("available_from"): Str(),
    Optional("available_to"): Str(),
    Optional("assignment_group"): Str(),
    Optional("shuffle_answers"): Bool(),
    Optional("time_limit"): Int(),
    Optional("allowed_attempts"): Int(),
    Optional("show_correct_answers_at"): Str(),
    Optional("hide_correct_answers_at"): Str(),
    Optional("access_code"): Str(),
    "description": Str(),
    Optional("questions"): Seq(
        Map({
            "type": Enum(["intro_text", "text", "multiple-choice", "matching", "multiple-answers"]),
            "text": Str(),
            Optional("answers"): Map({
                Optional("correct"): Seq(Str()),
                Optional("incorrect"): Seq(Str()),
                Optional("pairs"): Seq(
                    Map({
                        "left": Str(),
                        "right": Str()
                    })
                )
            })
        })
    )
})


def parse_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        text = file.read()

    try:
        document = load(text, schema).data
        return document
    except YAMLError as error:
        print(error)


if __name__ == "__main__":
    document = parse_yaml("Midterm.yaml")
    print(document)
