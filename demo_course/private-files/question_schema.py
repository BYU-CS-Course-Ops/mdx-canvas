from strictyaml import Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, Bool

# Define the schema for the yaml file
question_schema = Map({
    "type": Enum(["multiple_choice", "multiple_answers", "text", "matching"]),
    "text": Str(),
    Optional("points"): Int(),
    Optional("answers"): Map({
        Optional("correct"): Seq(Str()),
        Optional("incorrect"): Seq(Str()),
        Optional("pairs"): Seq(Map({
            "left": Str(),
            "right": Str()
        }))
    })
})