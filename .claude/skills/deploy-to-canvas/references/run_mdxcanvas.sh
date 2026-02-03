#!/bin/bash
# Deployment script for mdxcanvas - sources token from .env file
# Usage: ./run_mdxcanvas.sh <env_file> <course_info> <content_path>

ENV_FILE="$1"
COURSE_INFO="$2"
CONTENT_PATH="$3"

# Source the API token from the .env file
source "$ENV_FILE"

# Run mdxcanvas
mdxcanvas --course-info "$COURSE_INFO" "$CONTENT_PATH"

