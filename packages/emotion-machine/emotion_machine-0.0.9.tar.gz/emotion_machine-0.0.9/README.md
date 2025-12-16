# Emotion Machine Python SDK

Official Python helper for the Emotion Machine Companion API. It wraps the `/v1` endpoints
documented in `docs/client-companion-api-plan.md` so you can provision companions, ingest
knowledge, and chat/stream with them in just a few lines of code.

## Installation

```bash
pip install emotion-machine
```

The client depends on `httpx` and targets Python 3.9+.

## Quickstart

1. **Export your project API key** (project-scoped):

```bash
export EM_API_KEY="emk_prod_...."
export EM_API_BASE_URL="https://api.emotionmachine.ai"  # or http://localhost:8100 for local dev
```

2. **Bootstrap a companion, ingest curated knowledge, and chat:**

```python
from emotion_machine import EmotionMachine

client = EmotionMachine()  # reads EM_API_KEY / EM_API_BASE_URL

# Create a fresh companion
companion = client.create_companion(
    name="Luteal Support Coach",
    description="Helps users track luteal phase cravings",
    config={
        "system_prompt": {
            "full_system_prompt": "You are an encouraging health coach."
        }
    },
)
companion_id = companion["id"]

# Optionally shape the profile schema for per-user traits
client.upsert_profile_schema(
    companion_id,
    schema={
        "type": "object",
        "properties": {
            "craving_intensity": {"type": "integer", "minimum": 0, "maximum":5}
        },
    },
)

# Ingest curated luteal-phase knowledge via the built-in key
job = client.ingest_knowledge(
    companion_id,
    payload_type="json",
    key="data_id_x",
)
job_result = client.wait_for_job(job["id"], timeout=20)
assert job_result["status"] == "succeeded", job_result

# Or upload & ingest your own JSON/Markdown/TXT file in one step.
# The helper uploads the file, kicks off ingestion, waits for completion,
# and raises if the job fails.
result = client.ingest_knowledge_file(
    companion_id,
    file_path="important_app_related_knowledge.jsonl",
    payload_type="json",
)
print(result["job"]["status"])  # -> "succeeded"

# Run a synchronous chat completion
completion = client.chat_completion(
    companion_id,
    message="Hi! I'm feeling intense salt cravings today, what should I know?",
       external_user_id="user-123",
   )

print(completion["choices"][0]["message"]["content"])

# Stream responses (Server-Sent Events) and collect message chunks
stream = client.chat_stream(
    companion_id,
    message="Can you summarise key luteal phase symptoms?",
    external_user_id="user-123",
)
for event in stream:
    if event["event"] == "delta":
        chunk = event["data"]["choices"][0]["delta"].get("content", "")
        if chunk:
            print(chunk, end="", flush=True)
    elif event["event"] == "done":
         conversation_id = event["data"]["conversation_id"]

# Retrieve the full conversation transcript
transcript = client.get_conversation(conversation_id)
for message in transcript["messages"]:
    print(f"{message['role']}: {message['content']}")

# Upload an image and ask about it
image_result = client.upload_image(
    companion_id,
    conversation_id,
    file_path="food_photo.jpg",
)
image_id = image_result["image_id"]
print(f"Image description: {image_result['description']}")

# Send a message referencing the image
response = client.chat_completion(
    companion_id,
    message="What do you think about this meal?",
    external_user_id="user-123",
    conversation_id=conversation_id,
    image_ids=[image_id],
)
print(response["choices"][0]["message"]["content"])

# List the most recent conversations for a specific tester/user cohort
recent_sessions = client.list_conversations(
    companion_id,
    limit=25,
    external_user_id="user-123",
)
print(f"Found {len(recent_sessions)} saved sessions for user-123")

# Filter options include `external_user_prefix="beta-"` for cohort-level filtering.

# Create a voice session for real-time audio
session = client.create_session(
    companion_id,
    voice_config={
        "pipeline_type": "openai-realtime",
        "voice_name": "alloy",
        "temperature": 0.7,
        "realtimeModel": "gpt-realtime-mini-2025-10-06",
    },
)
print(f"Connect to WebSocket: {session['ws_url']}")
# Use a WebSocket library (e.g., websockets) to stream PCM audio
```

3. **Tidy up when finished:**

```python
client.close()
```

   or use `with EmotionMachine() as client:` to auto-close the HTTP session.

## Knowledge management tips

- One call for ingestion: use `client.ingest_knowledge(...)` for inline text/markdown/json, or `client.ingest_knowledge_file(...)` to upload a file and ingest in one step.
- `client.search_knowledge(..., mode="semantic" | "keyword" | "hybrid")` lets you compare retrieval strategies against the same dataset.
- `client.wait_for_job()` and `client.ingest_knowledge_file()` raise `KnowledgeJobFailed` if OpenAI reports the ingestion job as `failed`, so you can catch mistakes early in CI.

## API Coverage

| Resource        | Method                                           | SDK helper                                   |
|-----------------|---------------------------------------------------|----------------------------------------------|
| Companions      | `GET /v1/companions`                              | `client.list_companions()`                   |
|                 | `POST /v1/companions`                             | `client.create_companion(...)`               |
|                 | `GET /v1/companions/{id}`                         | `client.get_companion(id)`                   |
|                 | `PATCH /v1/companions/{id}`                       | `client.update_companion(...)`               |
|                 | `DELETE /v1/companions/{id}`                      | `client.delete_companion(id)`                |
| Profile Schema  | `PUT /v1/companions/{id}/profile-schema`          | `client.upsert_profile_schema(...)`          |
|                 | `GET /v1/companions/{id}/profile-schema`          | `client.get_profile_schema(...)`             |
| Knowledge       | `POST /v1/companions/{id}/knowledge`              | `client.ingest_knowledge(...)`, `client.ingest_knowledge_file(...)`               |
|                 | `GET /v1/knowledge-jobs/{job_id}`                 | `client.knowledge.get_job(job_id)`           |
| Chat            | `POST /v1/companions/{id}/chat`                   | `client.chat_completion(...)`                |
| Chat (stream)   | `POST /v1/companions/{id}/chat/stream`            | `client.chat_stream(...)`                    |
| Conversations   | `GET /v1/companions/{id}/conversations`           | `client.list_conversations(...)`             |
| Conversations   | `GET /v1/conversations/{conversation_id}`         | `client.get_conversation(...)`               |
| Images          | `POST /v1/companions/{id}/conversations/{id}/images` | `client.upload_image(...)`                |
|                 | `GET /v1/companions/{id}/conversations/{id}/images`  | `client.list_images(...)`                 |
| Voice Sessions  | `POST /v1/sessions`                                  | `client.create_session(...)`              |
|                 | `PATCH /v1/sessions/{id}`                            | `client.update_session(...)`              |

All helpers raise `emotion_machine.APIError` on non-success HTTP codes. Inspect
`e.status_code` and `e.payload` for diagnostics.

## Development

```bash
cd packages/pip-emotion-machine
pip install -e .[dev]
```

The package ships from `src/emotion_machine`. Update `pyproject.toml` to bump versions.
