# ScrollIntel API Documentation

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### POST /auth/login
Authenticate and receive a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "username": "string",
    "role": "string"
  }
}
```

#### GET /auth/verify
Verify the current JWT token.

**Response:**
```json
{
  "user": {
    "id": "string",
    "username": "string",
    "role": "string"
  }
}
```

## Prophecy Endpoints

### POST /prophecy/chat
Send a message to the prophecy system.

**Request Body:**
```json
{
  "message": "string"
}
```

**Response:**
```json
{
  "response": "string",
  "forecast": {
    "prediction": "string",
    "confidence": "number",
    "timeframe": "string"
  }
}
```

## Subscription Endpoints

### POST /subscribe
Create a new subscription.

**Request Body:**
```json
{
  "tier": "string" // "seeker", "scribe", or "prophet"
}
```

**Response:**
```json
{
  "subscription_id": "string",
  "client_secret": "string"
}
```

### GET /billing
Get current subscription information.

**Response:**
```json
{
  "status": "string",
  "current_period_end": "string",
  "cancel_at_period_end": "boolean",
  "tier": "string"
}
```

### POST /cancel
Cancel current subscription.

**Response:**
```json
{
  "status": "string",
  "message": "string"
}
```

## Report Generation

### POST /report/generate
Generate a PDF report.

**Request Body:**
```json
{
  "dataset_name": "string",
  "forecast_goal": "string",
  "include_charts": "boolean",
  "include_insights": "boolean"
}
```

**Response:**
PDF file download

## Webhook Management

### POST /webhook/add
Add a new webhook endpoint.

**Request Body:**
```json
{
  "url": "string",
  "platform": "string",
  "secret": "string"
}
```

**Response:**
```json
{
  "status": "string",
  "message": "string"
}
```

### POST /webhook/broadcast
Broadcast a message to all webhooks.

**Request Body:**
```json
{
  "content": "string",
  "forecast": {
    "prediction": "string",
    "confidence": "number",
    "timeframe": "string"
  },
  "timestamp": "string"
}
```

**Response:**
```json
{
  "status": "string",
  "results": [
    {
      "platform": "string",
      "success": "boolean"
    }
  ]
}
```

## Rate Limiting

API endpoints are rate-limited based on subscription tier:

- Free: 10 requests per day
- Seeker: 100 requests per day
- Scribe: 500 requests per day
- Prophet: Unlimited requests

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: <limit>
X-RateLimit-Remaining: <remaining>
X-RateLimit-Reset: <reset_timestamp>
```

## Error Handling

All errors follow this format:

```json
{
  "detail": "string",
  "status_code": "number"
}
```

Common status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error 