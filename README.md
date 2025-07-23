# SongDuplicateCheckerV2

SongDuplicateCheckerV2 is a small FastAPI service that will eventually scan a
music library for newly added tracks and highlight possible duplicates. The
scanner identifies matches using simple heuristics such as file size and title
similarity and will provide options for how to handle each song when a
duplicate is found.

At the moment the project exposes a minimal endpoint. When the root page (`/`)
is requested, the app performs a recursive search starting from `NAS_PATH` and
returns the path of the first audio file found. If no files are available the
page simply displays "No files found".
