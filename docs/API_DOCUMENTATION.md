# 📘 API Documentation

Base URL: `http://localhost:5000/api`

All endpoints except `/auth/login` and `/auth/signup` require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication

### POST /auth/signup
Create a new user account (employee or manager).

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe",
  "role": "employee",
  "manager_id": "manager-uuid" // Optional, required for employees
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User created successfully",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "employee",
    "company_id": "company-uuid"
  }
}
```

### POST /auth/login
Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "employee",
    "company_id": "company-uuid"
  }
}
```

---

## 👥 Users

### GET /users
List all users in the company (Admin/Manager only).

**Query Parameters:**
- `role` (optional): Filter by role (admin, manager, employee)

**Response (200):**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "employee",
      "company_id": "company-uuid",
      "manager_id": "manager-uuid",
      "created_at": "2025-10-04T10:00:00Z"
    }
  ]
}
```

### POST /users
Create new user (Admin only).

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "Jane Smith",
  "role": "manager"
}
```

---

## 📂 Categories

### GET /categories
List all expense categories.

**Response (200):**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "data": [
    {
      "id": "category-uuid",
      "name": "Travel",
      "description": "Travel expenses",
      "company_id": "company-uuid",
      "created_at": "2025-10-04T10:00:00Z"
    }
  ]
}
```

### POST /categories
Create new category (Admin only).

**Request Body:**
```json
{
  "name": "Office Supplies",
  "description": "Office supplies and equipment"
}
```

---

## 💰 Expenses

### GET /expenses
List expenses (employees see own, managers/admins see all).

**Query Parameters:**
- `status` (optional): Filter by status (draft, submitted, approved, rejected)
- `category_id` (optional): Filter by category

**Response (200):**
```json
{
  "success": true,
  "message": "Expenses retrieved successfully",
  "data": [
    {
      "id": "expense-uuid",
      "user_id": "user-uuid",
      "category_id": "category-uuid",
      "title": "Client Lunch",
      "description": "Business lunch with client",
      "amount": "150.00",
      "currency_code": "USD",
      "expense_date": "2025-10-04",
      "receipt_url": "https://...",
      "status": "submitted",
      "submitted_at": "2025-10-04T12:00:00Z",
      "created_at": "2025-10-04T10:00:00Z"
    }
  ]
}
```

### POST /expenses
Create new expense.

**Request Body:**
```json
{
  "category_id": "category-uuid",
  "title": "Client Lunch",
  "description": "Business lunch with potential client",
  "amount": 150.00,
  "currency_code": "USD",
  "expense_date": "2025-10-04",
  "receipt_url": "https://..." // Optional
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Expense created successfully",
  "data": {
    "id": "expense-uuid",
    "status": "draft",
    ...
  }
}
```

### GET /expenses/:id
Get single expense details.

**Response (200):**
```json
{
  "success": true,
  "message": "Expense retrieved successfully",
  "data": {
    "id": "expense-uuid",
    "user_id": "user-uuid",
    "user": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "category": {
      "name": "Travel"
    },
    ...
  }
}
```

### PUT /expenses/:id
Update expense (draft status only).

**Request Body:** Same as POST, all fields optional.

### DELETE /expenses/:id
Delete expense (draft status only).

**Response (200):**
```json
{
  "success": true,
  "message": "Expense deleted successfully"
}
```

### POST /expenses/:id/submit
Submit expense for approval.

**Response (200):**
```json
{
  "success": true,
  "message": "Approval workflow triggered - 1 approver(s) assigned",
  "data": {
    "id": "expense-uuid",
    "status": "submitted",
    "approval_status": {
      "total_approvers": 1,
      "approved_count": 0,
      "rejected_count": 0,
      "pending_count": 1
    }
  }
}
```

### GET /expenses/stats
Get expense statistics.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_count": 10,
    "draft_count": 2,
    "submitted_count": 3,
    "approved_count": 4,
    "rejected_count": 1
  }
}
```

---

## ✅ Approvals

### GET /approvals
List approvals for current manager/admin.

**Query Parameters:**
- `status` (optional): Filter by status (pending, approved, rejected)

**Response (200):**
```json
{
  "success": true,
  "message": "Approvals retrieved successfully",
  "data": [
    {
      "id": "approval-uuid",
      "expense_id": "expense-uuid",
      "rule_id": "rule-uuid",
      "approver_user_id": "manager-uuid",
      "status": "pending",
      "expense": {
        "title": "Client Lunch",
        "amount": "150.00",
        "currency_code": "USD",
        "user": {
          "name": "John Doe"
        }
      },
      "created_at": "2025-10-04T12:00:00Z"
    }
  ]
}
```

### POST /approvals/:id/approve
Approve an expense.

**Request Body:**
```json
{
  "comment": "Approved - Valid business expense" // Optional
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Expense approved successfully",
  "data": {
    "id": "approval-uuid",
    "status": "approved",
    "approved_at": "2025-10-04T13:00:00Z"
  }
}
```

### POST /approvals/:id/reject
Reject an expense.

**Request Body:**
```json
{
  "comment": "Please provide more details" // Required
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Expense rejected successfully",
  "data": {
    "id": "approval-uuid",
    "status": "rejected",
    "rejected_at": "2025-10-04T13:00:00Z"
  }
}
```

### GET /approvals/stats
Get approval statistics for current approver.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_count": 10,
    "pending_count": 3,
    "approved_count": 6,
    "rejected_count": 1
  }
}
```

---

## ⚙️ Approval Rules

### GET /approval-rules
List all approval rules (requires authentication).

**Query Parameters:**
- `is_active` (optional): Filter by active status (true/false)
- `category_id` (optional): Filter by category

**Response (200):**
```json
{
  "success": true,
  "message": "Approval rules retrieved successfully",
  "data": [
    {
      "id": "rule-uuid",
      "name": "Manager Approval for $100+",
      "description": "Approval rule for expenses over $100",
      "currency_code": "USD",
      "min_amount": "100.00",
      "max_amount": null,
      "priority": 1,
      "is_sequential": false,
      "approval_percentage": 100,
      "is_active": true,
      "approvers": [
        {
          "approver_user_id": "manager-uuid",
          "order_index": 0,
          "users": {
            "name": "Manager Name",
            "email": "manager@example.com"
          }
        }
      ]
    }
  ]
}
```

### POST /approval-rules
Create new approval rule (Admin only).

**Request Body:**
```json
{
  "name": "Manager Approval for $100+",
  "description": "Approval rule for expenses over $100",
  "currency_code": "USD",
  "min_amount": 100,
  "max_amount": null,
  "priority": 1,
  "is_sequential": false,
  "approval_percentage": 100,
  "approver_user_ids": ["manager-uuid-1", "manager-uuid-2"]
}
```

### PUT /approval-rules/:id
Update approval rule (Admin only).

### DELETE /approval-rules/:id
Delete approval rule (Admin only).

---

## 💱 Currency

### GET /currencies
List all available currencies.

**Response (200):**
```json
{
  "success": true,
  "message": "Currencies retrieved successfully",
  "data": [
    {
      "code": "USD",
      "name": "United States Dollar",
      "symbol": "$"
    },
    {
      "code": "EUR",
      "name": "Euro",
      "symbol": "€"
    }
  ]
}
```

### GET /countries
List all countries with currencies.

**Response (200):**
```json
{
  "success": true,
  "message": "Countries retrieved successfully",
  "data": [
    {
      "id": "country-uuid",
      "name": "United States",
      "currency_code": "USD"
    }
  ]
}
```

---

## 📤 File Upload

### POST /upload
Upload receipt file to Supabase Storage.

**Request:** multipart/form-data with `file` field

**Response (200):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "url": "https://...supabase.co/storage/v1/object/public/receipts/..."
}
```

---

## ❌ Error Responses

All endpoints return consistent error responses:

**401 Unauthorized:**
```json
{
  "success": false,
  "message": "Authentication token is missing"
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "message": "Admin access required"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Resource not found"
}
```

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": ["field1 is required", "field2 must be positive"]
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Internal server error"
}
```

---

## 📊 Status Codes

- `200` - OK (successful GET, PUT, DELETE)
- `201` - Created (successful POST)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server error)

---

## 🔄 Workflow States

### Expense Status Flow:
```
draft → submitted → approved/rejected
```

- **draft**: Created but not submitted
- **submitted**: Waiting for approval
- **approved**: All required approvers approved
- **rejected**: At least one approver rejected

### Approval Status:
- **pending**: Waiting for approver action
- **approved**: Approver approved
- **rejected**: Approver rejected

---

For more details on the system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md)
