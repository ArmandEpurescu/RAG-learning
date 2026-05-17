# RAG Learning

The goal of this project is to build a local assistant for personal documents.
The assistant should be able to index notes, journals, project ideas, and text files.

The MVP has three components:

1. Ingestion: reads Markdown and text files from the `data` folder.
2. Retrieval: turns every chunk into a local vector and searches for relevant chunks.
3. Answering: prints the most useful passages together with their source.

A good next step is connecting an LLM for synthesis.
The model should receive only the retrieved chunks and cite the sources in its answer.

For personal data, the project should stay explicit and controllable:
documents stay local, the index stays local, and integration with external services should be optional.
