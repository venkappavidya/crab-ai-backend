# Crab-AI Backend

Crab-AI Backend is a Python-based backend service designed to support the Crab-AI application. It manages data processing, user interactions, and integrates with various AI models to deliver intelligent responses.

## Features

- **Database Management**: Handles data storage and retrieval operations.
- **API Routing**: Manages endpoints for client-server communication.
- **AI Model Integration**: Interfaces with AI models to process and generate responses.
- **Logging**: Implements logging mechanisms for monitoring and debugging.

## Project Structure

- `database/`: Contains database connection and query handling modules.
- `models/`: Includes data models and schemas.
- `routes/`: Defines API endpoints and request handling logic.
- `utils/`: Provides utility functions and helpers.
- `logging_config.py`: Sets up logging configurations.
- `main.py`: Entry point of the application.
- `requirements.txt`: Lists project dependencies.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/vidyavenkappa/crab-ai-backend.git
   ```


2. **Navigate to the Project Directory**:

   ```bash
   cd crab-ai-backend
   ```


3. **Create a Virtual Environment** (Optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```


4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```


## Usage

1. **Set Up Environment Variables**:

   Configure necessary environment variables for database connections, API keys, etc.

2. **Run the Application**:

   ```bash
   python main.py
   ```


   The server will start and listen for incoming requests as defined in the `routes/` modules.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**.
2. **Create a New Branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```


3. **Make Your Changes**.
4. **Commit Your Changes**:

   ```bash
   git commit -m "Add your commit message here"
   ```


5. **Push to Your Fork**:

   ```bash
   git push origin feature/your-feature-name
   ```


6. **Submit a Pull Request**.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable support.


## Configuration

Copy `.env.example` to `.env` and fill it in. `DATABASE_URL` is the only
required variable.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `GEMINI_API_KEY` | for reviews | Gemini key used by the review pipeline |
| `ALLOWED_ORIGINS` | no | Comma-separated browser origins. Defaults to `*` |
| `ADMIN_TOKEN` | no | When set, `POST /conference/create` requires an `X-Admin-Token` header |
| `PORT` | no | Defaults to 10000 |

## Health checks

| Endpoint | Meaning |
| --- | --- |
| `GET /health` | Liveness. Never touches the database |
| `GET /health/db` | Readiness. Reports whether the database is reachable |

Check `/health/db` first when the API misbehaves; it returns the underlying
driver error verbatim.

## Startup behaviour

The database connection is created lazily and tables are prepared inside the
FastAPI lifespan handler. An unreachable database no longer prevents the
process from starting: the service boots, `/health` answers, and data
endpoints return `503 Database unavailable` until the database recovers.

This matters on hosted platforms. When the app crashed during import it never
bound a port, so the platform router had nothing to forward to and requests
hung until they timed out, with no error to read.

## Deploying

Any host that runs a Python web service works. Set the environment variables
above, then:

```
Build:  pip install -r requirements.txt
Start:  uvicorn main:app --host 0.0.0.0 --port $PORT
```

Dependency versions are pinned in `requirements.txt` so a redeploy installs
the same versions that were tested.

### A note on free PostgreSQL

Render's free PostgreSQL instances expire 30 days after creation and are
deleted after a further 14-day grace period, taking their data with them. If
the API stops responding after a few months of quiet, check whether the
database still exists before debugging anything else.


## Conferences

Conferences are data, not code. There is no fixed list: the `conferences`
table holds a name and an optional free-text `guidelines` field that is fed to
the review prompt, so each conference can carry its own review criteria.

Create one:

```bash
curl -X POST "$API/conference/create" \
  -H 'Content-Type: application/json' \
  -d '{"name": "ICML 2026"}'
```

`GET /conference/get-list` returns `200 []` when none exist. It does not
return 404: an empty collection is not a missing endpoint, and clients that
treat any non-2xx response as an error render nothing instead of an empty
state.
