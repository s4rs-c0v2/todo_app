# Flask Todo Application

A simple, yet functional Todo application built with Flask and PostgreSQL. This application allows users to create, update, and delete tasks while persisting data in a PostgreSQL database.

## Features

- Create new tasks
- Mark tasks as complete/incomplete
- Delete tasks
- Automatic timestamp creation for tasks
- PostgreSQL database integration
- Docker-ready configuration

## Prerequisites

- Python 3.x
- PostgreSQL
- Docker (optional)
- pip (Python package manager)

## Environment Variables

The application uses the following environment variables (with default values):

- `POSTGRES_USER` (default: "postgres")
- `POSTGRES_PASSWORD` (default: "postgres")
- `POSTGRES_DB` (default: same as POSTGRES_USER)
- `POSTGRES_HOST` (default: "db")
- `POSTGRES_PORT` (default: "5432")

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd todo-app
```

2. Install required packages:
```bash
pip install flask psycopg2
```

3. Set up PostgreSQL database:
- Ensure PostgreSQL is running
- Create a database
- Update environment variables if needed

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Access the application at:
```
http://localhost:5000
```

## Docker Support

The application is configured to work with Docker. To run with Docker:

1. Ensure Docker is installed and running
2. Configure the PostgreSQL connection details in environment variables
3. Build and run your container

## Database Schema

The application creates a `tasks` table with the following structure:

- `id`: SERIAL PRIMARY KEY
- `content`: TEXT NOT NULL
- `is_done`: BOOLEAN NOT NULL DEFAULT FALSE
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

## API Endpoints

- `GET /`: Display all tasks
- `POST /`: Create a new task
- `POST /update/<task_id>`: Update task status
- `POST /delete/<task_id>`: Delete a task

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
