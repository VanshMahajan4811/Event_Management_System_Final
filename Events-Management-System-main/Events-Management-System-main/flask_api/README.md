# Flask API Service

This directory contains a standalone Flask API service that can run alongside the Django EventManager project.

## Running the Flask API

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Flask app:

```bash
python app.py
```

The Flask API will be available at `http://localhost:5000/api/hello`.

You can also access the root URL at `http://localhost:5000/` which redirects to the API endpoint.

Example to test the API using curl:

```bash
curl http://localhost:5000/api/hello
```

## Integration Notes

- This Flask API runs independently of the Django project.
- You can call the Flask API endpoints from the Django app or other clients as needed.
- For production, consider using a reverse proxy to route requests to Django and Flask appropriately.
curl http://localhost:5000/api/hello
