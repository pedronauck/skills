# Bookmark Filters

Use this reference only when building `GET /bookmarks` requests with filters or pagination.

## Query Parameters

- `limit`: integer page size
- `cursor`: string pagination cursor
- `is_unread_only`: boolean filter
- `hide_archived`: boolean filter
- `media_type`: string filter
- `author`: string filter
- `tag`: string filter
- `posted_from`: date-time filter
- `posted_to`: date-time filter
- `bookmarked_from`: date-time filter
- `bookmarked_to`: date-time filter
- `sort_by`: string sort selector
- `sort_cursor`: string sort cursor
- `q`: full-text query string
- `vector_search_term`: semantic search string

## Practical Notes

- Use `cursor` from a previous response’s `meta.next_cursor` for classic pagination.
- Use `limit` explicitly when deterministic page sizing matters.
- Prefer URL encoding through `scripts/build-bookmarks-url.py` instead of manual concatenation when multiple filters are present.
- Keep date-time values in ISO 8601 form to avoid ambiguous parsing.
