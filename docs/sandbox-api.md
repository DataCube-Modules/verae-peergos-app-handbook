# Peergos app sandbox API

Source of truth for field-level request/response shapes:
[protocol/peergos-book-apps.md](../protocol/peergos-book-apps.md).
This page is the permission map and endpoint index used when building Verae
apps.

## Permissions

| Token | Allows |
| --- | --- |
| `STORE_APP_DATA` | Read/write `/.apps/<name>/data/` via `/peergos-api/v0/data/` and `/form/` |
| `EDIT_CHOSEN_FILE` | Overwrite the file the user opened the app on |
| `READ_CHOSEN_FOLDER` | Read the folder the user opened |
| `EXCHANGE_MESSAGES_WITH_FRIENDS` | Chat v0 and v1 |
| `USE_MAILBOX` | Encrypted mailbox |
| `ACCESS_PROFILE_PHOTO` | Friend profile thumbnails |
| `CSP_UNSAFE_EVAL` | `eval` / `new Function` in the app CSP |
| `ADMIN_INSTANCE` | Org admin console (quotas, invites, space requests). Only grant to instance admins |

An app with **no** permissions can still read its own `assets/` and call the
save / file-picker / folder-picker / print helpers.

## How calls leave the sandbox

`fetch("/peergos-api/v0/install-app/", { method: "POST", body: formData })`
is converted by the service worker (`formToJSON`) into a JSON body. The
gallery in `verae-ops/modules/peergos-apps/gallery/index.html` uses that
path to open the Install wizard.

## Data store (`STORE_APP_DATA`)

Base: `/peergos-api/v0/data/<path>`

| Method | Meaning | Success |
| --- | --- | --- |
| `GET` | File bytes, or `{files, subFolders}` for a directory. `?preview=true` returns a thumbnail | 200 |
| `POST` | Create | 201 + `Location` |
| `PUT` | Replace | 200 / 201 |
| `PATCH` | Append only (`X-Update-Range: append`) | 204 |
| `DELETE` | Delete file | 204 |

`POST /peergos-api/v0/form/<name>` stores an HTML form as a file in `data/`.

Without `/data/`, GET/PUT apply to **assets** or to the **chosen file/folder**.

## Dialogs (no extra permission)

| Call | Result |
| --- | --- |
| `PUT` or `POST /peergos-api/v0/save/filename.txt` | Save-as dialog; body is file bytes |
| `GET /peergos-api/v0/file-picker?extension=jpg,png` | File picker; 200 + `[path]` |
| `GET /peergos-api/v0/folders` (`?multiple=false`) | Folder picker; 200 + `[path]` |
| `POST /peergos-api/v0/print/` | Print preview |
| `GET /peergos-api/v0/profile/:username` | Friend profile modal |
| `GET /peergos-api/v0/profile/:username?thumbnail=true` | `{profileThumbnail}` (needs `ACCESS_PROFILE_PHOTO`) |

## Chat v0 (`EXCHANGE_MESSAGES_WITH_FRIENDS`)

See `example-apps/chat-api/`.

- `GET /peergos-api/v0/chat/` — `{chatId, title}` list
- `POST /peergos-api/v0/chat/` FormData `maxInvites` — 201 + `Location: chatId`
- `GET /peergos-api/v0/chat/:id?from=&to=` — `{messages, count}`
- `PUT /peergos-api/v0/chat/:id` FormData `text` — send

## Chat v1

See `example-apps/chat/`. Richer membership, attachments, edit/reply/delete.

- `GET /peergos-api/v1/chat/`
- `GET /peergos-api/v1/chat/:id?startIndex=`
- `POST /peergos-api/v1/chat/` — new-chat membership modal
- `POST /peergos-api/v1/chat/:id` — edit membership
- `PUT /peergos-api/v1/chat/:id` — `{createMessage|editMessage|replyMessage|deleteMessage}`
- `POST /peergos-api/v1/chat/attachment?filename=`
- `DELETE /peergos-api/v1/chat/:id`

## Mailbox (`USE_MAILBOX`)

See `example-apps/email/`. Needs the email bridge on the server for SMTP/IMAP.

- `GET /peergos-api/v0/mailbox/`
- `GET /peergos-api/v0/mailbox/{inbox,sent,:folder}`
- `POST .../move`, `.../delete`, `.../download`
- `PUT .../attachment`, `.../post`, `.../event`, `.../folder`

## Instance admin (`ADMIN_INSTANCE`)

Used by `org-admin/assets/index.html`. All calls are
`POST /peergos-api/v0/admin/<route>` with a JSON body.

| Route | Body |
| --- | --- |
| `users` | `{}` |
| `user-details` | `{username}` |
| `set-quota` | `{username, quota}` (bytes) |
| `delete-mfa-credential` | `{username, credentialIdHex}` |
| `delete-user` | `{username}` |
| `create-tokens` | `{count}` |
| `space-requests` | `{}` |
| `approve-space-request` | `{index}` |
| `audit-log` | `{since}` |

Non-admins receive an error containing `not an admin`. Do not ship this
permission on DataCube apps.

## Install from a gallery

Only valid when the sandbox is `$$app-gallery$$` (recommended-apps):

`POST /peergos-api/v0/install-app/` with FormData `path=/peergos/recommended-apps` and `appName=<folder>`.

That opens the same Install wizard as Drive → `peergos-app.json` → **Install App**.

## Built-in apps (not installable)

These ship in the Peergos web UI. They do **not** appear in recommended-apps:

Calendar (`.ics`), PDF viewer, image/video viewers, hex/editor, social, Drive.

Drive will offer **recommended** third-party viewers for `.docx`/`.odt`
(`doc-viewer`), `.sheet`/`.xlsx`/`.ods` (`luckysheet`), `.tldr` (`tldraw`),
`.drawio` (`drawio`), `.epub` (`ebookreader`) once those folders are public
under `/peergos/recommended-apps/`.
