# RAM Monitoring System Documentation

## Overview

This project is a **RAM Monitoring System** built using **FastAPI**. It continuously logs RAM usage data and provides an API for retrieving the data, calculating statistics, and storing new data entries. The system also includes endpoints to retrieve a report of RAM usage and add RAM data manually.

## Installation

To set up the project, follow these steps:

1. **Install dependencies:**
   You need to have Python 3.10 or higher. Install the required packages using:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

All configuration variables are stored in `monitor/conf.py`:

- `DATABASE_URL`: The URL for the SQLite database.
- `TABLE_NAME`: The name of the table used to store RAM data.
- `SLEEP_TIME`: Time interval (in seconds) between automatic logging of RAM data.
- `DEFAULT_SORT`, `DEFAULT_ORDER_BY`, `DEFAULT_N`: Default sorting, ordering, and limit values for retrieving RAM data.

---

## Database

The database structure consists of the following fields:

- `id`: Auto-incrementing primary key
- `total_mb`: Total RAM in megabytes
- `free_mb`: Free RAM in megabytes
- `timestamp`: Timestamp when the data was recorded
- `device`: Identifier for the device (internal or external)

---

## Models

The project uses **Pydantic** models for data validation:

- **RamMonitorIn**: Represents the input model for adding RAM data.
- **RamMonitorOut**: Extends `RamMonitorIn` and includes an `id` field and a computed `used_mb` property.
- **Report**: A model for generating reports on RAM usage.

---

## Testing

Run porject test via:

```bash
pytest test
```

---

## API Endpoints

### Root - Report

- **Description**: Generate a report containing the average free RAM and the total count of records.
- **URL**: `/`
- **Method**: `GET`
- **Response**:

  ```json
  {
    "start_time": "2023-09-01T00:00:00Z",
    "end_time": "2023-09-30T23:59:59Z",
    "avg_free": 3650.5,
    "count": 100
  }
  ```

- **Parameters**:
  - `start_time` (optional): Start of the time limit for the report.
  - `end_time` (optional): End of the time limit for the report.

---

### Get RAM Data

- **Description**: Retrieve the latest `n` records of RAM data.
- **URL**: `/ram/`
- **Method**: `GET`
- **Response**:

  ```json
  [
    {
      "id": 1,
      "total_mb": 8000,
      "free_mb": 4000,
      "used_mb": 4000,
      "timestamp": "2023-09-29T10:00:00Z"
    }
  ]
  ```

- **Parameters**:
  - `n`: Number of latest records to retrieve (default: 5).
  - `order`: Sorting order (`ASC` or `DESC`).
  - `order_by`: Field to sort the records by (default: `timestamp`).
  - `start_time`: Start time limit for the records.
  - `end_time`: End time limit for the records.

---

### Create RAM Data

- **Description**: Add a new record of RAM data.
- **URL**: `/`
- **Method**: `POST`
- **Payload**:

  ```json
  {
    "total_mb": 16000,
    "free_mb": 8000,
    "timestamp": "2023-09-29T12:00:00Z"
  }
  ```

- **Response**: HTTP 201 Created on success.

---

## Running the Application

To run the application, use the following command:

```bash
uvicorn monitor:app --reload
```

This will start the FastAPI application on `localhost:8000`.

## Postman Collection

You can find project Postman Collection [here](https://lunar-crescent-604002.postman.co/workspace/hi~42345065-0ef2-4ead-ae24-83545f605834/collection/31890069-a8c640df-e5b3-4924-93da-c6cd5d8a3a4f?action=share&creator=31890069).
