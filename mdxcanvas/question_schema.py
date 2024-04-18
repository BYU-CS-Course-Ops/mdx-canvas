from strictyaml import Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, Bool

# Define the schema for the yaml file
question_schema = Map({
    "type": Enum(["multiple_choice", "multiple_answers", "text", "matching", "true_false", "multiple_tf"]),
    "text": Str(),
    Optional("points"): Int(),
    Optional("answers"): Seq(Map({
        Optional("correct"): Str(),
        Optional("incorrect"): Str(),
        Optional("left"): Str(),
        Optional("right"): Str(),
        Optional("distractor"): Str()
    })),
    Optional("correct"): Bool()
})