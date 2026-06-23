# OpenSea Collection Download Tool

A Python FastAPI service for running collection metadata download jobs and calculating trait distribution / rarity information for NFT collections.

## Purpose

The service is organized around long-running jobs. A client starts a collection download, polls the job status, and then fetches the computed distribution data once the job has finished.

## Example workflow

```python
job_id = post("http://localhost:8000/api/collections/<collection-name>/download")

status = get(f"http://localhost:8000/api/jobs/{job_id}").status
while status != "FINISHED":
    status = get(f"http://localhost:8000/api/jobs/{job_id}").status

distribution = get("http://localhost:8000/api/collections/<collection-name>/distribution")
```

## Expected stack

- Python
- FastAPI
- MongoDB
- Background/asynchronous job execution

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn main:app --reload
```

If the current entry point is different, update the command with the correct module name.

## API overview

| Endpoint | Purpose |
| --- | --- |
| `POST /api/collections/<collection-name>/download` | Start a collection metadata download job. |
| `GET /api/jobs/<job-id>` | Poll job status. |
| `GET /api/collections/<collection-name>/distribution` | Retrieve computed trait and token distribution data. |

## Status

Experimental service. Validate endpoint names and setup commands against the current code before deployment.

## License

No license has been selected yet.
