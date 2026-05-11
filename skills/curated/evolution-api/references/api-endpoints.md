# Evolution API - Complete Endpoint Reference

Base URL: `https://<SERVER_URL>`
Auth header: `apikey: <api-key>`

## Instance Controller

| Method | Endpoint                               | Description                            |
| ------ | -------------------------------------- | -------------------------------------- |
| POST   | `/instance/create`                     | Create a new instance                  |
| GET    | `/instance/fetchInstances`             | List all instances (or filter by name) |
| GET    | `/instance/connect/{instance}`         | Get QR code for connection             |
| PUT    | `/instance/restart/{instance}`         | Restart instance                       |
| GET    | `/instance/connectionState/{instance}` | Check connection state                 |
| DELETE | `/instance/logout/{instance}`          | Logout (keep config)                   |
| DELETE | `/instance/delete/{instance}`          | Delete instance permanently            |
| POST   | `/instance/setPresence/{instance}`     | Set online/offline presence            |

## Message Controller

| Method | Endpoint                                | Description                      |
| ------ | --------------------------------------- | -------------------------------- |
| POST   | `/message/sendText/{instance}`          | Send plain text message          |
| POST   | `/message/sendMedia/{instance}`         | Send image/video/document        |
| POST   | `/message/sendWhatsAppAudio/{instance}` | Send audio (auto PTT conversion) |
| POST   | `/message/sendSticker/{instance}`       | Send sticker                     |
| POST   | `/message/sendLocation/{instance}`      | Send location pin                |
| POST   | `/message/sendContact/{instance}`       | Send contact card                |
| POST   | `/message/sendReaction/{instance}`      | Send/remove reaction emoji       |
| POST   | `/message/sendPoll/{instance}`          | Send poll                        |
| POST   | `/message/sendList/{instance}`          | Send interactive list            |
| POST   | `/message/sendButtons/{instance}`       | Send button message              |
| POST   | `/message/sendStatus/{instance}`        | Post to WhatsApp Status          |

## Chat Controller

| Method | Endpoint                                    | Description                       |
| ------ | ------------------------------------------- | --------------------------------- |
| POST   | `/chat/checkIsWhatsApp/{instance}`          | Verify if numbers are on WhatsApp |
| POST   | `/chat/markMessageAsRead/{instance}`        | Mark messages as read             |
| POST   | `/chat/markMessageAsUnread/{instance}`      | Mark message as unread            |
| POST   | `/chat/archiveChat/{instance}`              | Archive or unarchive a chat       |
| DELETE | `/chat/deleteMessageForEveryone/{instance}` | Delete message for everyone       |
| POST   | `/chat/updateMessage/{instance}`            | Edit a sent message               |
| POST   | `/chat/sendPresence/{instance}`             | Send typing/recording indicator   |
| POST   | `/chat/updateBlockStatus/{instance}`        | Block/unblock a contact           |
| POST   | `/chat/fetchProfilePictureUrl/{instance}`   | Get profile picture URL           |
| POST   | `/chat/getBase64/{instance}`                | Get media message as base64       |
| POST   | `/chat/findContacts/{instance}`             | Search contacts                   |
| POST   | `/chat/findMessages/{instance}`             | Search messages                   |
| POST   | `/chat/findStatusMessage/{instance}`        | Find status messages              |
| POST   | `/chat/findChats/{instance}`                | List all chats                    |

## Group Controller

| Method | Endpoint                                                  | Description                       |
| ------ | --------------------------------------------------------- | --------------------------------- |
| POST   | `/group/create/{instance}`                                | Create a new group                |
| POST   | `/group/updateGroupPicture/{instance}`                    | Update group avatar               |
| POST   | `/group/updateGroupSubject/{instance}`                    | Update group name                 |
| POST   | `/group/updateGroupDescription/{instance}`                | Update group description          |
| GET    | `/group/inviteCode/{instance}?groupJid=`                  | Get group invite link             |
| POST   | `/group/revokeInviteCode/{instance}`                      | Revoke invite link                |
| POST   | `/group/sendInviteUrl/{instance}`                         | Send invite link to a number      |
| GET    | `/group/findGroupInfoByInviteCode/{instance}?inviteCode=` | Find group by invite code         |
| GET    | `/group/findGroupInfoByJid/{instance}?groupJid=`          | Find group by JID                 |
| GET    | `/group/fetchAllGroups/{instance}?getParticipants=`       | List all groups                   |
| GET    | `/group/participants/{instance}?groupJid=`                | List group members                |
| POST   | `/group/updateParticipant/{instance}`                     | Add/remove/promote/demote members |
| POST   | `/group/updateSetting/{instance}`                         | Lock/unlock group settings        |
| POST   | `/group/toggleEphemeral/{instance}`                       | Set disappearing messages         |
| DELETE | `/group/leaveGroup/{instance}`                            | Leave a group                     |

## Profile Settings

| Method | Endpoint                                    | Description             |
| ------ | ------------------------------------------- | ----------------------- |
| POST   | `/profile/fetchBusinessProfile/{instance}`  | Fetch business profile  |
| POST   | `/profile/fetchProfile/{instance}`          | Fetch profile info      |
| POST   | `/profile/updateProfileName/{instance}`     | Update display name     |
| POST   | `/profile/updateProfileStatus/{instance}`   | Update status text      |
| POST   | `/profile/updateProfilePicture/{instance}`  | Update profile picture  |
| DELETE | `/profile/removeProfilePicture/{instance}`  | Remove profile picture  |
| GET    | `/profile/fetchPrivacySettings/{instance}`  | Get privacy settings    |
| POST   | `/profile/updatePrivacySettings/{instance}` | Update privacy settings |

## Webhook

| Method | Endpoint                   | Description               |
| ------ | -------------------------- | ------------------------- |
| POST   | `/webhook/set/{instance}`  | Configure webhook         |
| GET    | `/webhook/find/{instance}` | Get webhook configuration |

## Settings

| Method | Endpoint                    | Description              |
| ------ | --------------------------- | ------------------------ |
| POST   | `/settings/set/{instance}`  | Update instance settings |
| GET    | `/settings/find/{instance}` | Get instance settings    |

## Integrations - Typebot

| Method | Endpoint                            | Description                |
| ------ | ----------------------------------- | -------------------------- |
| POST   | `/typebot/set/{instance}`           | Create typebot integration |
| POST   | `/typebot/start/{instance}`         | Start typebot session      |
| GET    | `/typebot/find/{instance}`          | Find typebot config        |
| GET    | `/typebot/fetch/{instance}`         | Fetch typebot details      |
| PUT    | `/typebot/update/{instance}`        | Update typebot             |
| DELETE | `/typebot/delete/{instance}`        | Delete typebot             |
| POST   | `/typebot/changeStatus/{instance}`  | Change session status      |
| GET    | `/typebot/fetchSessions/{instance}` | List sessions              |
| POST   | `/typebot/settings/{instance}`      | Update typebot settings    |
| GET    | `/typebot/findSettings/{instance}`  | Get typebot settings       |

## Integrations - OpenAI

| Method | Endpoint                          | Description            |
| ------ | --------------------------------- | ---------------------- |
| POST   | `/openai/create/{instance}`       | Create OpenAI bot      |
| GET    | `/openai/find/{instance}`         | Find single bot        |
| GET    | `/openai/fetch/{instance}`        | List all bots          |
| PUT    | `/openai/update/{instance}`       | Update bot             |
| DELETE | `/openai/delete/{instance}`       | Delete bot             |
| POST   | `/openai/creds/{instance}`        | Set OpenAI credentials |
| GET    | `/openai/findCreds/{instance}`    | Get credentials        |
| DELETE | `/openai/deleteCreds/{instance}`  | Delete credentials     |
| POST   | `/openai/settings/{instance}`     | Update settings        |
| GET    | `/openai/findSettings/{instance}` | Get settings           |
| POST   | `/openai/changeStatus/{instance}` | Change bot status      |
| GET    | `/openai/findSessions/{instance}` | List sessions          |

## Integrations - Chatwoot

| Method | Endpoint                    | Description         |
| ------ | --------------------------- | ------------------- |
| POST   | `/chatwoot/set/{instance}`  | Configure Chatwoot  |
| GET    | `/chatwoot/find/{instance}` | Get Chatwoot config |

## Integrations - Dify

| Method | Endpoint                        | Description       |
| ------ | ------------------------------- | ----------------- |
| POST   | `/dify/create/{instance}`       | Create Dify bot   |
| GET    | `/dify/find/{instance}`         | Find Dify bots    |
| GET    | `/dify/findBot/{instance}`      | Find specific bot |
| PUT    | `/dify/update/{instance}`       | Update bot        |
| POST   | `/dify/settings/{instance}`     | Set Dify settings |
| GET    | `/dify/findSettings/{instance}` | Get settings      |
| POST   | `/dify/changeStatus/{instance}` | Change bot status |
| GET    | `/dify/findStatus/{instance}`   | Get bot status    |

## Integrations - n8n

| Method | Endpoint                       | Description       |
| ------ | ------------------------------ | ----------------- |
| POST   | `/n8n/create/{instance}`       | Create n8n bot    |
| GET    | `/n8n/find/{instance}`         | Find n8n bots     |
| PUT    | `/n8n/update/{instance}`       | Update bot        |
| POST   | `/n8n/settings/{instance}`     | Set n8n settings  |
| GET    | `/n8n/findSettings/{instance}` | Get settings      |
| POST   | `/n8n/changeStatus/{instance}` | Change bot status |
| GET    | `/n8n/findStatus/{instance}`   | Get bot status    |

## Integrations - Event Delivery

| Method | Endpoint                     | Description          |
| ------ | ---------------------------- | -------------------- |
| POST   | `/rabbitmq/set/{instance}`   | Configure RabbitMQ   |
| GET    | `/rabbitmq/find/{instance}`  | Get RabbitMQ config  |
| POST   | `/sqs/set/{instance}`        | Configure Amazon SQS |
| GET    | `/sqs/find/{instance}`       | Get SQS config       |
| POST   | `/websocket/set/{instance}`  | Configure WebSocket  |
| GET    | `/websocket/find/{instance}` | Get WebSocket config |
