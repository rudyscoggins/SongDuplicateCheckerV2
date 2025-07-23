# SongDuplicateCheckerV2

This project now serves as a very small FastAPI application for exploring the
music library. All previous UI elements and endpoints were removed. When the
root page (`/`) is requested the app performs a recursive search starting from
`NAS_PATH` and returns the path of the first audio file found. If no files are
available the page simply displays "No files found".
