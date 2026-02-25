#!/bin/bash
# Deployment script for mdxcanvas - sources token from .env file
# Usage: ./run_mdxcanvas.sh <env_file> <course_info> <content_path>
# Example: ./run_mdxcanvas.sh ~/.env course_info.json content/quizzes/quiz1.canvas.md.xml

ENV_FILE="$1"
COURSE_INFO="$2"
CONTENT_PATH="$3"

# Validate arguments
if [ -z "$ENV_FILE" ] || [ -z "$COURSE_INFO" ] || [ -z "$CONTENT_PATH" ]; then
    echo "Usage: $0 <env_file> <course_info> <content_path>"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found: $ENV_FILE"
    exit 1
fi

if [ ! -f "$COURSE_INFO" ]; then
    echo "Error: course_info file not found: $COURSE_INFO"
    exit 1
fi

# Source the API token from the .env file (token stays out of command arguments)
source "$ENV_FILE"

# Run mdxcanvas with the provided paths
mdxcanvas --course-info "$COURSE_INFO" $CONTENT_PATH
