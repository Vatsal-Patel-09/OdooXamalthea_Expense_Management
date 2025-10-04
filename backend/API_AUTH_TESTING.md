# Authentication API - Testing Guide

## Available Endpoints

### 1. Admin Signup (POST /api/auth/signup)
Creates a new admin user and company.

**Request:**
```json
POST http://localhost:5000/api/auth/signup
Content-Type: application/json

{
  "email": "admin@mycompany.com",
  "password": "SecurePass123",
  "name": "John Admin",
  "company_name": "My Company Inc.",
  "currency": "USD"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Admin account created successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "admin@mycompany.com",
    "name": "John Admin",
    "role": "admin",
    "company_id": "company-uuid",
    "is_active": true,
    "created_at": "2025-10-04T...",
    "updated_at": "2025-10-04T..."
  },
  "company": {
    "id": "company-uuid",
    "name": "My Company Inc.",
    "currency": "USD",
    "created_by": "uuid",
    "created_at": "2025-10-04T...",
    "updated_at": "2025-10-04T..."
  }
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

---

### 2. User Login (POST /api/auth/login)
Login with email and password.

**Request:**
```json
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "admin@mycompany.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "admin@mycompany.com",
    "name": "John Admin",
    "role": "admin",
    "company_id": "company-uuid",
    "is_active": true,
    "created_at": "2025-10-04T...",
    "updated_at": "2025-10-04T..."
  }
}
```

---

### 3. Get Current User (GET /api/auth/me)
Get authenticated user's information.

**Request:**
```
GET http://localhost:5000/api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "admin@mycompany.com",
    "name": "John Admin",
    "role": "admin",
    "company_id": "company-uuid",
    "manager_id": null,
    "is_active": true,
    "created_at": "2025-10-04T...",
    "updated_at": "2025-10-04T..."
  }
}
```

---

## Testing with cURL

### 1. Signup:
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"SecurePass123\",\"name\":\"Test Admin\",\"company_name\":\"Test Company\"}"
```

### 2. Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"SecurePass123\"}"
```

### 3. Get Current User:
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Testing with PowerShell

### 1. Signup:
```powershell
$body = @{
    email = "admin@test.com"
    password = "SecurePass123"
    name = "Test Admin"
    company_name = "Test Company"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/signup" -Method POST -Body $body -ContentType "application/json"
```

### 2. Login:
```powershell
$loginBody = @{
    email = "admin@test.com"
    password = "SecurePass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = $response.token
```

### 3. Get Current User:
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/me" -Method GET -Headers $headers
```

---

## Error Responses

### 400 - Bad Request
```json
{
  "success": false,
  "message": "Missing required fields: email, password"
}
```

### 401 - Unauthorized
```json
{
  "success": false,
  "message": "Invalid email or password"
}
```

### 403 - Forbidden
```json
{
  "success": false,
  "message": "Account is deactivated. Contact your administrator."
}
```

### 409 - Conflict
```json
{
  "success": false,
  "message": "User with this email already exists"
}
```

### 500 - Server Error
```json
{
  "success": false,
  "message": "Server error: [error details]"
}
```

---

## JWT Token Details

- **Algorithm:** HS256
- **Expiration:** 24 hours
- **Payload includes:**
  - user_id
  - email
  - role (admin, manager, employee)
  - company_id
  - exp (expiration timestamp)
  - iat (issued at timestamp)

**Use the token in all authenticated requests:**
```
Authorization: Bearer <your_token_here>
```
