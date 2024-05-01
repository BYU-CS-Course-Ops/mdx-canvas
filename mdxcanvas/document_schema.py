from strictyaml import Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, Bool
from .question_schema import question_schema

# Define the schema for the yaml file
document_schema = Seq(Map({
    "title": Str(),
    "type": Enum(["assignment", "quiz", "page"]),
    "description": Str(),

    # Quiz specific fields
    Optional("quiz_type"): Enum(["practice_quiz", "assignment", "graded_survey", "survey"]),
    Optional("assignment_group"): Str(),
    Optional("time_limit"): Int(),
    Optional("shuffle_answers"): Bool(),
    Optional("hide_results"): Enum(["always", "until_after_last_attempt"]),
    Optional("show_correct_answers"): Bool(),
    Optional("show_correct_answers_last_attempt"): Bool(),
    Optional("show_correct_answers_at"): Str(),
    Optional("hide_correct_answers_at"): Str(),
    Optional("allowed_attempts"): Int(),
    Optional("scoring_policy"): Enum(["keep_highest", "keep_latest"]),
    Optional("one_question_at_a_time"): Bool(),
    Optional("cant_go_back"): Bool(),
    Optional("access_code"): Str(),
    Optional("ip_filter"): Str(),
    Optional("due_at"): Str(),
    Optional("lock_at"): Str(),
    Optional("unlock_at"): Str(),
    Optional("published"): Bool(),
    Optional("one_time_results"): Bool(),
    Optional("only_visible_to_overrides"): Bool(),
    Optional("questions"): Seq(question_schema),

    # Assignment specific fields
    Optional("position"): Int(),
    Optional("submission_types"): Seq(Enum(["online_quiz", "none", "on_paper", "discussion_topic", "external_tool", "online_upload", "online_text_entry", "online_url", "media_recording", "student_annotation"])),
    Optional("allowed_extensions"): Seq(Str()),
    Optional("turnitin_enabled"): Bool(),
    Optional("vericite_enabled"): Bool(),
    Optional("turnitin_settings"): Str(),
    Optional("integration_data"): Str(),
    Optional("integration_id"): Str(),
    Optional("peer_reviews"): Bool(),
    Optional("automatic_peer_reviews"): Bool(),
    Optional("notify_of_update"): Bool(),
    Optional("group_category_id"): Int(),
    Optional("grade_group_students_individually"): Bool(),
    Optional("external_tool_tag_attributes"): Str(),
    Optional("points_possible"): Int(),
    Optional("grading_type"): Enum(["pass_fail", "percent", "letter_grade", "gpa_scale", "points", "not_graded"]),
    Optional("description"): Str(),
    Optional("assignment_group_id"): Int(),
    Optional("assignment_overrides"): Seq(MapPattern(Str(), Any())),
    Optional("published"): Bool(),
    Optional("grading_standard_id"): Int(),
    Optional("omit_from_final_grade"): Bool(),
    Optional("hide_in_gradebook"): Bool(),
    Optional("quiz_lti"): Bool(),
    Optional("moderated_grading"): Bool(),
    Optional("grader_count"): Int(),
    Optional("final_grader_id"): Int(),
    Optional("grader_comments_visible_to_graders"): Bool(),
    Optional("graders_anonymous_to_graders"): Bool(),
    Optional("graders_names_visible_to_final_grader"): Bool(),
    Optional("anonymous_grading"): Bool(),
    Optional("allowed_attempts"): Int(),
    Optional("annotatable_attachment_id"): Int(),

    # Page specific fields
    Optional("body"): Str(),
    Optional("editing_roles"): Enum(["teachers", "students", "members", "public"]),
    Optional("notify_of_update"): Bool(),
    Optional("published"): Bool(),
    Optional("front_page"): Bool(),
    Optional("publish_at"): Str()

}))

