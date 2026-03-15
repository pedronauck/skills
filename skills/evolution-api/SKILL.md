---
name: evolution-api
description: |
  Evolution API integration for WhatsApp messaging, instance management, webhooks,
  and chatbot orchestration. Use when: (1) Creating or managing WhatsApp instances
  via Evolution API, (2) Sending messages (text, media, audio, lists, buttons,
  reactions), (3) Configuring webhooks or event listeners, (4) Managing groups
  or contacts, (5) Integrating with Typebot, Chatwoot, Dify, or OpenAI through
  Evolution API. Triggers on: evolution-api, evolution api, whatsapp api, baileys,
  whatsapp integration, send whatsapp, whatsapp webhook.
---

# Evolution API

Open-source WhatsApp integration API supporting Baileys (WhatsApp Web) and official WhatsApp Business API (Cloud API). Built with Node.js + TypeScript + Express.js + Prisma.

## Authentication

All requests use the `apikey` header. Two levels of keys exist:

- **Global API Key**: Set via `AUTHENTICATION_API_KEY` env var. Has full access to all instances.
- **Instance Token**: Per-instance key returned on creation. Scoped to that instance only.

```
apikey: YOUR_API_KEY
```

Every request follows this pattern:

```bash
curl --request <METHOD> \
  --url https://<SERVER_URL>/<path>/{instanceName} \
  --header 'Content-Type: application/json' \
  --header 'apikey: <api-key>' \
  --data '<json-body>'
```

## Instance Lifecycle

### Create Instance

```bash
POST /instance/create

{
  "instanceName": "my-instance",
  "integration": "WHATSAPP-BAILEYS",
  "token": "optional-custom-token",
  "qrcode": true,
  "number": "5511999999999",
  "rejectCall": true,
  "msgCall": "I can't answer calls",
  "groupsIgnore": true,
  "alwaysOnline": true,
  "readMessages": true,
  "readStatus": true,
  "syncFullHistory": true,
  "webhook": {
    "url": "https://your-server.com/webhook",
    "byEvents": false,
    "base64": true,
    "headers": { "authorization": "Bearer token" },
    "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
  }
}
```

Response (201):

```json
{
  "instance": {
    "instanceName": "my-instance",
    "instanceId": "af6c5b7c-ee27-4f94-9ea8-192393746ddd",
    "status": "created"
  },
  "hash": { "apikey": "generated-instance-token" },
  "qrcode": { "base64": "data:image/png;base64,..." }
}
```

The `integration` field accepts:

- `WHATSAPP-BAILEYS` — Free, based on WhatsApp Web (Baileys library)
- `WHATSAPP-BUSINESS` — Official Meta Cloud API (requires Facebook App setup)

### Connect Instance (get QR code)

```
GET /instance/connect/{instanceName}
```

Returns QR code as base64 for scanning with WhatsApp mobile app.

### Check Connection State

```
GET /instance/connectionState/{instanceName}
```

Returns: `open`, `close`, or `connecting`.

### Other Instance Operations

| Method | Endpoint                           | Description               |
| ------ | ---------------------------------- | ------------------------- |
| GET    | `/instance/fetchInstances`         | List all instances        |
| PUT    | `/instance/restart/{instance}`     | Restart instance          |
| DELETE | `/instance/logout/{instance}`      | Logout (keep instance)    |
| DELETE | `/instance/delete/{instance}`      | Delete instance entirely  |
| POST   | `/instance/setPresence/{instance}` | Set online/offline status |

## Sending Messages

### Text Message

```bash
POST /message/sendText/{instanceName}

{
  "number": "5511999999999",
  "text": "Hello from Evolution API!",
  "delay": 1200,
  "linkPreview": true,
  "mentionsEveryOne": false,
  "mentioned": ["5511888888888@s.whatsapp.net"]
}
```

Response (201):

```json
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE594145F4C59B4"
  },
  "message": { "extendedTextMessage": { "text": "Hello from Evolution API!" } },
  "messageTimestamp": "1717689097",
  "status": "PENDING"
}
```

**Number format**: Use full international format without `+` sign. For groups, use the group JID (e.g., `120363025486748009@g.us`).

### Reply / Quote a Message

Add `quoted` to any send payload:

```json
{
  "number": "5511999999999",
  "text": "This is a reply",
  "quoted": {
    "key": { "id": "ORIGINAL_MESSAGE_ID" },
    "message": { "conversation": "Original message text" }
  }
}
```

### Media Message

```bash
POST /message/sendMedia/{instanceName}

{
  "number": "5511999999999",
  "mediatype": "image",
  "mimetype": "image/png",
  "caption": "Check this out",
  "media": "https://example.com/image.png"
}
```

`mediatype` options: `image`, `video`, `document`.
`media` accepts a URL or base64-encoded string.

### Audio Message

```bash
POST /message/sendWhatsAppAudio/{instanceName}

{
  "number": "5511999999999",
  "audio": "https://example.com/audio.mp3"
}
```

Audio is automatically converted to WhatsApp PTT (push-to-talk) format.

### Other Message Types

| Endpoint                                | Body fields                                                                | Notes                      |
| --------------------------------------- | -------------------------------------------------------------------------- | -------------------------- |
| `POST /message/sendLocation/{instance}` | `number`, `latitude`, `longitude`, `name`, `address`                       |                            |
| `POST /message/sendContact/{instance}`  | `number`, `contact: [{fullName, wuid, phoneNumber}]`                       |                            |
| `POST /message/sendReaction/{instance}` | `key: {remoteJid, fromMe, id}`, `reaction`                                 | Use empty string to remove |
| `POST /message/sendPoll/{instance}`     | `number`, `name`, `values[]`, `selectableCount`                            |                            |
| `POST /message/sendList/{instance}`     | `number`, `title`, `description`, `buttonText`, `footerText`, `sections[]` |                            |
| `POST /message/sendButtons/{instance}`  | `number`, `title`, `description`, `buttons[]`, `footer`                    |                            |
| `POST /message/sendSticker/{instance}`  | `number`, `sticker` (URL or base64)                                        |                            |
| `POST /message/sendStatus/{instance}`   | `type`, `content`, `statusJidList[]`, `caption`                            | Post to WhatsApp Status    |

## Webhook Configuration

### Set Webhook via API

```bash
POST /webhook/set/{instanceName}

{
  "webhook": {
    "enabled": true,
    "url": "https://your-server.com/webhook",
    "webhookByEvents": false,
    "webhookBase64": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "CONNECTION_UPDATE",
      "SEND_MESSAGE"
    ]
  }
}
```

When `webhookByEvents` is `true`, events are sent to `{url}/{EVENT_NAME}` (e.g., `/webhook/MESSAGES_UPSERT`).

### Get Webhook Config

```
GET /webhook/find/{instanceName}
```

For the complete list of available events, see [references/events.md](references/events.md).

## Chat Operations

| Method | Endpoint                                    | Body                              | Description                |
| ------ | ------------------------------------------- | --------------------------------- | -------------------------- |
| POST   | `/chat/checkIsWhatsApp/{instance}`          | `numbers: ["5511..."]`            | Verify numbers on WhatsApp |
| POST   | `/chat/findMessages/{instance}`             | `where: {key: {remoteJid}}`       | Search messages            |
| POST   | `/chat/findChats/{instance}`                | `{}`                              | List all chats             |
| POST   | `/chat/findContacts/{instance}`             | `where: {id}`                     | Search contacts            |
| POST   | `/chat/markMessageAsRead/{instance}`        | `readMessages: [{remoteJid, id}]` | Mark as read               |
| POST   | `/chat/archiveChat/{instance}`              | `chat, archive: true`             | Archive/unarchive chat     |
| DELETE | `/chat/deleteMessageForEveryone/{instance}` | `key: {remoteJid, fromMe, id}`    | Delete for everyone        |
| POST   | `/chat/updateMessage/{instance}`            | `number, text, key: {id}`         | Edit sent message          |
| POST   | `/chat/sendPresence/{instance}`             | `number, presence`                | Show typing/recording      |
| POST   | `/chat/getBase64/{instance}`                | `message: {key}`                  | Get media as base64        |

`presence` values: `composing`, `recording`, `paused`.

## Group Management

| Method | Endpoint                                     | Body / Params                      | Description                |
| ------ | -------------------------------------------- | ---------------------------------- | -------------------------- |
| POST   | `/group/create/{instance}`                   | `subject, participants[]`          | Create group               |
| GET    | `/group/fetchAllGroups/{instance}`           | query: `getParticipants=true`      | List all groups            |
| GET    | `/group/findGroupInfos/{instance}?groupJid=` | query param                        | Group details              |
| GET    | `/group/inviteCode/{instance}?groupJid=`     | query param                        | Get invite link            |
| GET    | `/group/participants/{instance}?groupJid=`   | query param                        | List members               |
| POST   | `/group/updateParticipant/{instance}`        | `groupJid, action, participants[]` | Add/remove/promote/demote  |
| POST   | `/group/updateSetting/{instance}`            | `groupJid, action`                 | Lock/unlock group settings |
| POST   | `/group/toggleEphemeral/{instance}`          | `groupJid, expiration`             | Set disappearing messages  |
| DELETE | `/group/leaveGroup/{instance}`               | `groupJid`                         | Leave group                |

`action` for participants: `add`, `remove`, `promote`, `demote`.

## Profile Settings

| Method | Endpoint                                    | Description          |
| ------ | ------------------------------------------- | -------------------- |
| POST   | `/profile/fetchProfile/{instance}`          | Fetch profile info   |
| POST   | `/profile/updateProfileName/{instance}`     | Update display name  |
| POST   | `/profile/updateProfileStatus/{instance}`   | Update status text   |
| POST   | `/profile/updateProfilePicture/{instance}`  | Update avatar        |
| DELETE | `/profile/removeProfilePicture/{instance}`  | Remove avatar        |
| GET    | `/profile/fetchPrivacySettings/{instance}`  | Get privacy settings |
| POST   | `/profile/updatePrivacySettings/{instance}` | Update privacy       |

## Integrations

Evolution API supports chatbot integrations configured per-instance:

| Integration | Endpoints prefix | Description                           |
| ----------- | ---------------- | ------------------------------------- |
| Typebot     | `/typebot/`      | Conversational bot flows              |
| Chatwoot    | `/chatwoot/`     | Help desk / CRM                       |
| OpenAI      | `/openai/`       | AI-powered bots + audio transcription |
| Dify        | `/dify/`         | AI agent platform                     |
| n8n         | `/n8n/`          | Workflow automation                   |
| Flowise     | `/flowise/`      | LLM flow builder                      |
| EvoAI       | `/evoai/`        | Evolution's own AI bot                |

Each integration follows the CRUD pattern: `create`, `find`, `update`, `delete`, `settings`, `change-status`, `fetch-session`.

## Event Delivery Channels

Beyond webhooks, Evolution API can deliver events via:

- **RabbitMQ** — `POST /rabbitmq/set/{instance}`
- **Amazon SQS** — `POST /sqs/set/{instance}`
- **WebSocket (Socket.io)** — `POST /websocket/set/{instance}`
- **Apache Kafka** — Via environment variables

## Advanced References

- **Full endpoint table**: See [references/api-endpoints.md](references/api-endpoints.md)
- **Environment variables** (self-hosted): See [references/environment-variables.md](references/environment-variables.md)
- **Webhook events catalog**: See [references/events.md](references/events.md)
