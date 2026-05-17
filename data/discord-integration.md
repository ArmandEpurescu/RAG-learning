# Discord Integration Plan

Discord integration should start as a bot that can answer in a private server or selected channels.

Suggested first version:

1. Create a Discord application and bot in the Discord Developer Portal.
2. Store the bot token in an environment variable named `DISCORD_BOT_TOKEN`.
3. Keep Discord code optional so the local chat UI still works without Discord.
4. Start with read-only commands such as `/ask`, `/status`, and `/sources`.
5. Send user questions to the local RAG API at `http://127.0.0.1:8000`.

Important rules:

1. Never commit the Discord token.
2. Do not allow the bot to execute shell commands at first.
3. Limit the bot to specific channels or a private test server.
4. Log retrieval sources so answers stay auditable.
