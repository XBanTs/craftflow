# CraftFlow API Documentation

**Base URL:** `https://craftflow-tyl3.onrender.com`  
**Authentication:** Session-based (login via web) or HTTP Basic Auth (for Postman).

---

## Endpoints

| Method | Endpoint | Auth | Description | Status Codes |
|----------|----------|----------|----------|----------|
| GET | `/api/jobs/` | No | List all open jobs | 200 |
| POST | `/api/jobs/` | Yes | Create a new job | 201, 400 |
| GET | `/api/jobs/{id}/` | No | Job detail | 200, 404 |
| DELETE | `/api/jobs/{id}/` | Yes (owner) | Delete a job | 204, 403, 404 |
| POST | `/api/bids/` | Yes | Submit a bid | 201, 400 |
| GET | `/api/services/` | No | List all services | 200 |
| GET | `/api/services/{id}/` | No | Service detail | 200, 404 |
| GET | `/api/notifications/unread/` | Yes | Unread notifications (JSON) | 200 |

---

# Example Requests & Responses

## 1. List All Open Jobs

**Request**

```http
GET /api/jobs/
```

**Response (200 OK)**

```json
[
  {
    "id": 1,
    "title": "Build a REST API backend for mobile app",
    "budget": "2000.00",
    "category": "web_dev",
    "status": "open",
    "client": {
      "id": 2,
      "username": "alice_startup"
    },
    "bid_count": 3,
    "created_at": "2026-06-01T12:00:00Z"
  }
]
```

---

## 2. Create a Job (Requires Authentication)

**Request**

```http
POST /api/jobs/
```

**Headers**

```http
Authorization: Basic ...
Content-Type: application/json
```

**Body**

```json
{
  "title": "Design a landing page",
  "description": "Need a modern, responsive landing page.",
  "budget": "800.00",
  "category": "ui_ux"
}
```

**Response (201 Created)**

```json
{
  "id": 9,
  "title": "Design a landing page",
  "description": "Need a modern, responsive landing page.",
  "budget": "800.00",
  "category": "ui_ux",
  "status": "open",
  "client": {
    "id": 2,
    "username": "alice_startup"
  },
  "bid_count": 0,
  "created_at": "2026-06-04T14:22:00Z"
}
```

---

## 3. Delete a Job (Owner Only)

**Request**

```http
DELETE /api/jobs/9/
```

**Headers**

```http
Authorization: Basic ...
```

**Response (204 No Content)**

```text
No Content
```

**If User Is Not The Owner**

```http
403 Forbidden
```

---

## 4. Submit a Bid

**Request**

```http
POST /api/bids/
```

**Body**

```json
{
  "job": 1,
  "amount": "500.00",
  "proposal": "I have 5 years of experience building APIs..."
}
```

**Response (201 Created)**

```json
{
  "id": 12,
  "job": 1,
  "freelancer": {
    "id": 5,
    "username": "frank_python"
  },
  "amount": "500.00",
  "proposal": "I have 5 years...",
  "status": "pending",
  "created_at": "2026-06-04T14:25:00Z"
}
```

---

## 5. List Services

**Request**

```http
GET /api/services/
```

**Response (200 OK)**

```json
[
  {
    "id": 1,
    "title": "Python Backend Development",
    "price": "50.00",
    "category": "web_dev",
    "freelancer": {
      "id": 5,
      "username": "frank_python"
    }
  }
]
```

---

## 6. Unread Notifications

**Request**

```http
GET /api/notifications/unread/
```

**Response (200 OK)**

```json
{
  "count": 2,
  "notifications": [
    {
      "id": 45,
      "message": "frank_python submitted a bid on your job...",
      "link": "/jobs/1/",
      "read_url": "/notifications/45/read/",
      "created_at": "Jun 04, 2026 14:25"
    }
  ]
}
```

---

## Authentication Notes

### Session Authentication

Users authenticate through the CraftFlow web application and maintain an active session through browser cookies.

### HTTP Basic Authentication

Useful for API testing tools such as Postman.

Example Header:

```http
Authorization: Basic <base64-encoded-credentials>
```

---

## Common Status Codes

| Status Code | Meaning |
|------------|----------|
| 200 | Request successful |
| 201 | Resource created successfully |
| 204 | Resource deleted successfully |
| 400 | Invalid request data |
| 403 | Permission denied |
| 404 | Resource not found |

---

## API Workflow Example

1. Retrieve available jobs.

```http
GET /api/jobs/
```

2. Select a job.

```http
GET /api/jobs/{id}/
```

3. Submit a bid.

```http
POST /api/bids/
```

4. Check notifications.

```http
GET /api/notifications/unread/
```

5. Create new jobs (authenticated users).

```http
POST /api/jobs/
```

6. Delete owned jobs if necessary.

```http
DELETE /api/jobs/{id}/
```
````
