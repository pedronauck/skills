# Evolution API - Webhook Events

All events that can be subscribed to via webhook, RabbitMQ, SQS, or WebSocket.

## Connection Events

| Event                 | Description                                                         |
| --------------------- | ------------------------------------------------------------------- |
| `APPLICATION_STARTUP` | Application initialized; used for environment setup                 |
| `CONNECTION_UPDATE`   | Connection status changed (connecting, reconnecting, disconnecting) |
| `LOGOUT_INSTANCE`     | Instance logged out                                                 |
| `REMOVE_INSTANCE`     | Instance removed from the system                                    |
| `QRCODE_UPDATED`      | QR code refreshed (new code available for scanning)                 |

## Message Events

| Event             | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `MESSAGES_UPSERT` | New message received or sent (most common event to listen to) |
| `MESSAGES_UPDATE` | Existing message modified (status change, read receipt, etc.) |
| `MESSAGES_DELETE` | Message deleted                                               |
| `MESSAGES_SET`    | Initial message state during history synchronization          |
| `MESSAGES_EDITED` | Message content edited                                        |
| `SEND_MESSAGE`    | Message sent from the API (outbound confirmation)             |

## Chat Events

| Event          | Description                               |
| -------------- | ----------------------------------------- |
| `CHATS_UPSERT` | Chat created or updated                   |
| `CHATS_UPDATE` | Chat metadata changed                     |
| `CHATS_DELETE` | Chat deleted                              |
| `CHATS_SET`    | Initial chat state during synchronization |

## Contact Events

| Event             | Description                             |
| ----------------- | --------------------------------------- |
| `CONTACTS_UPSERT` | Contact added or updated                |
| `CONTACTS_UPDATE` | Contact information changed             |
| `CONTACTS_SET`    | Initial contacts during synchronization |

## Group Events

| Event                       | Description                                        |
| --------------------------- | -------------------------------------------------- |
| `GROUPS_UPSERT`             | Group created or updated                           |
| `GROUP_UPDATE`              | Group settings or metadata changed                 |
| `GROUP_PARTICIPANTS_UPDATE` | Group members added, removed, promoted, or demoted |

## Label Events

| Event                | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `LABELS_EDIT`        | Label created, modified, or deleted                  |
| `LABELS_ASSOCIATION` | Label associated with or removed from a chat/message |

## Other Events

| Event             | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `CALL`            | Call event (received, started, ended)                      |
| `PRESENCE_UPDATE` | User presence changed (typing, recording, online, offline) |

## Bot Events

| Event                   | Description                    |
| ----------------------- | ------------------------------ |
| `TYPEBOT_START`         | Typebot session started        |
| `TYPEBOT_CHANGE_STATUS` | Typebot session status changed |
| `ERRORS`                | API error events               |
| `ERRORS_WEBHOOK`        | Webhook delivery errors        |

## Webhook Payload Structure

Every webhook payload follows this structure:

```json
{
  "event": "MESSAGES_UPSERT",
  "instance": "my-instance",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "3EB0A0C2F5F2C1B4D8"
    },
    "pushName": "Contact Name",
    "message": {
      "conversation": "Hello!"
    },
    "messageType": "conversation",
    "messageTimestamp": 1717689097
  }
}
```

The `data` field varies by event type. For media messages, `data.message` contains
the media type key (`imageMessage`, `videoMessage`, `audioMessage`, `documentMessage`)
with metadata like `mimetype`, `fileLength`, `caption`, and optionally `base64`
(if `webhookBase64` is enabled).
