from datetime import datetime
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
ADD_COMMENTS = False
SET_METADATA_PARENTS = False
ADD_TIMESTAMP = False
# TIMESTAMP = datetime(2025, 6, 29, 23, 59, 59).strftime('%Y-%m-%dT%H:%M:%SZ')
TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
ISSUE_LIST_SHEET_NAME = "comments"