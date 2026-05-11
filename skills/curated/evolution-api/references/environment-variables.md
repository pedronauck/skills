# Evolution API - Environment Variables

Reference for self-hosted Evolution API configuration. See the full example at
`Docker/.env.example` in the official repository.

## Server

| Variable      | Description                                                   | Example                   |
| ------------- | ------------------------------------------------------------- | ------------------------- |
| `SERVER_TYPE` | Server protocol                                               | `http`                    |
| `SERVER_PORT` | Server port                                                   | `8080`                    |
| `SERVER_URL`  | Public server URL (used for internal requests, webhook links) | `https://api.example.com` |

## Authentication

| Variable                                   | Description                      | Example                            |
| ------------------------------------------ | -------------------------------- | ---------------------------------- |
| `AUTHENTICATION_API_KEY`                   | Global API key for all instances | `429683C4C977415CAAFCCE10F7D57E11` |
| `AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES` | Show instances in fetch endpoint | `true`                             |

## Database (Prisma)

| Variable                          | Description                                        | Example                                           |
| --------------------------------- | -------------------------------------------------- | ------------------------------------------------- |
| `DATABASE_ENABLED`                | Enable persistent storage                          | `true`                                            |
| `DATABASE_PROVIDER`               | DB provider (`postgresql` or `mysql`)              | `postgresql`                                      |
| `DATABASE_CONNECTION_URI`         | Connection string                                  | `postgresql://user:pass@localhost:5432/evolution` |
| `DATABASE_CONNECTION_CLIENT_NAME` | Client name (separates installations sharing a DB) | `evolution_exchange`                              |

### Data Persistence Flags (true/false)

| Variable                         | Saves           |
| -------------------------------- | --------------- |
| `DATABASE_SAVE_DATA_INSTANCE`    | Instance data   |
| `DATABASE_SAVE_DATA_NEW_MESSAGE` | New messages    |
| `DATABASE_SAVE_MESSAGE_UPDATE`   | Message updates |
| `DATABASE_SAVE_DATA_CONTACTS`    | Contacts        |
| `DATABASE_SAVE_DATA_CHATS`       | Chats           |
| `DATABASE_SAVE_DATA_LABELS`      | Labels          |
| `DATABASE_SAVE_DATA_HISTORIC`    | Event history   |

## Cache (Redis)

| Variable                     | Description                                         | Example                    |
| ---------------------------- | --------------------------------------------------- | -------------------------- |
| `CACHE_REDIS_ENABLED`        | Enable Redis cache                                  | `true`                     |
| `CACHE_REDIS_URI`            | Redis connection URI                                | `redis://localhost:6379/6` |
| `CACHE_REDIS_PREFIX_KEY`     | Key prefix (separates installations)                | `evolution`                |
| `CACHE_REDIS_SAVE_INSTANCES` | Save WhatsApp credentials in Redis                  | `false`                    |
| `CACHE_LOCAL_ENABLED`        | Enable local in-memory cache (alternative to Redis) | `false`                    |

## Global Webhook

| Variable                           | Description                           | Example                       |
| ---------------------------------- | ------------------------------------- | ----------------------------- |
| `WEBHOOK_GLOBAL_ENABLED`           | Enable global webhooks                | `false`                       |
| `WEBHOOK_GLOBAL_URL`               | URL that receives all webhook events  | `https://webhook.example.com` |
| `WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS` | Route by event name (`{url}/{EVENT}`) | `false`                       |

Per-event toggles: `WEBHOOK_EVENTS_APPLICATION_STARTUP`, `WEBHOOK_EVENTS_QRCODE_UPDATED`,
`WEBHOOK_EVENTS_MESSAGES_UPSERT`, `WEBHOOK_EVENTS_MESSAGES_UPDATE`, `WEBHOOK_EVENTS_MESSAGES_DELETE`,
`WEBHOOK_EVENTS_SEND_MESSAGE`, `WEBHOOK_EVENTS_CONTACTS_UPSERT`, `WEBHOOK_EVENTS_CONTACTS_UPDATE`,
`WEBHOOK_EVENTS_PRESENCE_UPDATE`, `WEBHOOK_EVENTS_CHATS_UPSERT`, `WEBHOOK_EVENTS_CHATS_UPDATE`,
`WEBHOOK_EVENTS_CHATS_DELETE`, `WEBHOOK_EVENTS_GROUPS_UPSERT`, `WEBHOOK_EVENTS_GROUPS_UPDATE`,
`WEBHOOK_EVENTS_GROUP_PARTICIPANTS_UPDATE`, `WEBHOOK_EVENTS_CONNECTION_UPDATE`,
`WEBHOOK_EVENTS_LABELS_EDIT`, `WEBHOOK_EVENTS_LABELS_ASSOCIATION`, `WEBHOOK_EVENTS_CALL`,
`WEBHOOK_EVENTS_TYPEBOT_START`, `WEBHOOK_EVENTS_TYPEBOT_CHANGE_STATUS`, `WEBHOOK_EVENTS_ERRORS`.

## WhatsApp Business API (Cloud API)

| Variable                    | Description                        | Example                      |
| --------------------------- | ---------------------------------- | ---------------------------- |
| `WA_BUSINESS_TOKEN_WEBHOOK` | Token to validate Facebook webhook | `evolution`                  |
| `WA_BUSINESS_URL`           | WhatsApp Business API URL          | `https://graph.facebook.com` |
| `WA_BUSINESS_VERSION`       | API version                        | `v20.0`                      |
| `WA_BUSINESS_LANGUAGE`      | Default language                   | `en_US`                      |

## RabbitMQ

| Variable                  | Description     | Example            |
| ------------------------- | --------------- | ------------------ |
| `RABBITMQ_ENABLED`        | Enable RabbitMQ | `false`            |
| `RABBITMQ_URI`            | Connection URI  | `amqp://localhost` |
| `RABBITMQ_EXCHANGE_NAME`  | Exchange name   | `evolution`        |
| `RABBITMQ_GLOBAL_ENABLED` | Enable globally | `false`            |

Per-event toggles follow the pattern `RABBITMQ_EVENTS_{EVENT_NAME}` (same events as webhook).

## Amazon SQS

| Variable                | Description    |
| ----------------------- | -------------- |
| `SQS_ENABLED`           | Enable SQS     |
| `SQS_ACCESS_KEY_ID`     | AWS access key |
| `SQS_SECRET_ACCESS_KEY` | AWS secret key |
| `SQS_ACCOUNT_ID`        | AWS account ID |
| `SQS_REGION`            | AWS region     |

## WebSocket

| Variable                  | Description          | Example |
| ------------------------- | -------------------- | ------- |
| `WEBSOCKET_ENABLED`       | Enable WebSocket     | `false` |
| `WEBSOCKET_GLOBAL_EVENTS` | Enable global events | `false` |

## Integrations

| Variable                                  | Description                                    | Example  |
| ----------------------------------------- | ---------------------------------------------- | -------- |
| `CHATWOOT_ENABLED`                        | Enable Chatwoot                                | `false`  |
| `CHATWOOT_MESSAGE_READ`                   | Mark messages read when replying from Chatwoot | `true`   |
| `CHATWOOT_MESSAGE_DELETE`                 | Mirror deletes to Chatwoot                     | `true`   |
| `CHATWOOT_IMPORT_DATABASE_CONNECTION_URI` | Chatwoot DB URI for message import             |          |
| `OPENAI_ENABLED`                          | Enable OpenAI integration                      | `false`  |
| `DIFY_ENABLED`                            | Enable Dify integration                        | `false`  |
| `TYPEBOT_API_VERSION`                     | Typebot API version                            | `latest` |

## Amazon S3 / MinIO

| Variable        | Description       | Example            |
| --------------- | ----------------- | ------------------ |
| `S3_ENABLED`    | Enable S3 storage | `false`            |
| `S3_ACCESS_KEY` | Access key        |                    |
| `S3_SECRET_KEY` | Secret key        |                    |
| `S3_BUCKET`     | Bucket name       | `evolution`        |
| `S3_PORT`       | Port              | `443`              |
| `S3_ENDPOINT`   | Endpoint          | `s3.amazonaws.com` |
| `S3_USE_SSL`    | Use SSL           | `true`             |

## Logging

| Variable      | Description           | Example                                           |
| ------------- | --------------------- | ------------------------------------------------- |
| `LOG_LEVEL`   | Log levels to display | `ERROR,WARN,DEBUG,INFO,LOG,VERBOSE,DARK,WEBHOOKS` |
| `LOG_COLOR`   | Colorize logs         | `true`                                            |
| `LOG_BAILEYS` | Baileys log level     | `error`                                           |

## Session & QR Code

| Variable                      | Description                                             | Example         |
| ----------------------------- | ------------------------------------------------------- | --------------- |
| `CONFIG_SESSION_PHONE_CLIENT` | Name shown on smartphone                                | `Evolution API` |
| `CONFIG_SESSION_PHONE_NAME`   | Browser name                                            | `Chrome`        |
| `QRCODE_LIMIT`                | QR code expiry (seconds)                                | `30`            |
| `QRCODE_COLOR`                | QR code color                                           | `#175197`       |
| `DEL_INSTANCE`                | Auto-delete unconnected instances (minutes, or `false`) | `false`         |

## Misc

| Variable           | Description          | Example               |
| ------------------ | -------------------- | --------------------- |
| `LANGUAGE`         | API language         | `en`                  |
| `TELEMETRY`        | Enable telemetry     | `true`                |
| `CORS_ORIGIN`      | Allowed origins      | `*`                   |
| `CORS_METHODS`     | Allowed HTTP methods | `GET,POST,PUT,DELETE` |
| `CORS_CREDENTIALS` | Allow cookies        | `true`                |
