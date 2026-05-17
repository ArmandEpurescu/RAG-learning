# Capabilities Roadmap

Current capabilities:

1. Index Markdown and text files from the `data` folder.
2. Retrieve relevant chunks from a local SQLite index.
3. Answer through a local Ollama model.
4. Expose a local HTTP API.
5. Serve a browser chat UI with voice input and browser speech output.

Near-term capabilities:

1. Add private local context in `data/private`, which is ignored by Git.
2. Add Discord integration through a bot token stored outside the repository.
3. Add safe local tools such as reading notes, creating notes, running tests, and checking Git status.
4. Add gaming helpers for Path of Exile builds, notes, trade searches, and leveling plans.

Safety rules:

1. Never commit secrets or tokens.
2. Prefer read-only integrations first.
3. Log what external action is about to happen before doing it.
4. Keep destructive actions behind explicit confirmation.
