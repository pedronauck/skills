# TweetSmash API Reference

This reference was cross-checked against the TweetSmash docs on April 3, 2026.

Source pages:
- `https://www.tweetsmash.com/api-docs/getting-started`
- `https://www.tweetsmash.com/api-docs/fetch-saved-posts`
- `https://www.tweetsmash.com/api-docs/manage-labels`
- `https://www.tweetsmash.com/api-docs/add-labels`
- `https://www.tweetsmash.com/api-docs/remove-labels`

## Authentication

- Header: `Authorization: Bearer <API_KEY>`
- Base URL: `https://api.tweetsmash.com/v1`
- API key flow:
  - Open the TweetSmash API integration page from the docs.
  - Generate a new API key.
  - Keep the key secret and pass it as a bearer token.

## Rate Limit

- 100 requests per hour per API key

## Error Codes

- `401 Unauthorized`: missing or invalid API key
- `402 Subscription Required`: plan upgrade required
- `429 Too Many Requests`: rate limit exceeded
- `500 Internal Server Error`: unexpected server-side failure

## Endpoints

### GET `/bookmarks`

Purpose:
- Retrieve bookmarked posts with optional filtering, search, and pagination.

Required headers:
- `Authorization`

Response shape:
- `status`: boolean
- `data`: array of bookmarks
- `meta.next_cursor`: string cursor for the next page
- `meta.limit`: effective page size
- `meta.total_count`: total matching bookmarks

Bookmark fields commonly shown in docs:
- `post_id`
- `tweet_details.text`
- `tweet_details.link`
- `tweet_details.posted_at`
- `tweet_details.attachments`
- `tweet_details.quoted_tweet`
- `tweet_details.meta`
- `author_id`
- `author_username`
- `author_details.name`
- `author_details.username`
- `author_details.profile_image`
- `tags`
- `is_read`
- `is_archived`
- `imported_at`
- `sort_index`

### GET `/labels`

Purpose:
- Retrieve all labels for the authenticated account with usage counts.

Required headers:
- `Authorization`

Response shape:
- `status`: boolean
- `data`: array of label records

Label fields shown in docs:
- `id`
- `label_name`
- `metadata`
- `count`

### POST `/labels/add`

Purpose:
- Add labels to one or more bookmarked tweets.

Required headers:
- `Authorization`

Body fields:
- `tweet_ids`: array, required
- `label_id`: string, optional
- `label_name`: string, optional

Response shape:
- `status`: boolean
- `message`: success text for label addition

### POST `/labels/remove`

Purpose:
- Remove a label from one or more bookmarked tweets.

Required headers:
- `Authorization`

Body fields:
- `tweet_ids`: array, required
- `label_name`: string, required

Response shape:
- `status`: boolean
- `message`: success text for label removal
