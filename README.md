# jubilant-broccoli
Damage Inspection system

# Damage Inspection System

A modular backend system for vehicle damage inspection workflow built with Flask, MySQL, and JWT authentication.

## 🏗️ Project Structure

```
damage_inspection_system/
├── app/
│   ├── __init__.py                 # Application factory
│   ├── extensions.py               # Initialize extensions
│   ├── config.py                   # Configuration
│   │
│   ├── users/                      # User management module
│   │   ├── __init__.py
│   │   ├── models.py               # User model
│   │   └── schemas.py              # User validation schemas
│   │
│   ├── inspections/                # Inspection management module
│   │   ├── __init__.py
│   │   ├── models.py               # Inspection model
│   │   ├── routes.py               # Inspection API endpoints
│   │   ├── schemas.py              # Inspection validation schemas
│   │   └── services.py             # Inspection business logic
│   │
│   ├── auth/                       # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py               # Login/signup endpoints
│   │   ├── services.py             # Auth business logic
│   │   └── utils.py                # JWT utilities
│   │
│   └── core/                       # Core/shared functionality
│       ├── __init__.py
│       └── logger.py               # Request logging
│
├── migrations/                     # Database migrations
├── tests/                          # Test files
│   ├── conftest.py
│   ├── test_user/
│   ├── test_inspection/
│   └── test_auth/
├── requirements.txt
├── .env
├── run.py
└── README.md
```

## 🚀 Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **Inspection Management**: Create, read, update vehicle damage inspections
- **Image Validation**: Validates image URLs for proper format (.jpg, .jpeg, .png)
- **Status Tracking**: Track inspection status (pending, reviewed, completed)
- **Request Logging**: Comprehensive logging of all API requests
- **Error Handling**: Proper error handling with meaningful error messages
- **Modular Architecture**: Clean separation of concerns with modular design

## 🛠️ Tech Stack

- **Backend Framework**: Flask
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Validation**: Marshmallow
- **ORM**: SQLAlchemy
- **Environment Management**: python-decouple

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package installer)

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Nimanita/jubilant-broccoli.git
cd damage_inspection_system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=damage_inspection_db
DB_USER=your-db-username
DB_PASSWORD=your-db-password
```

### 5. Database Setup

Create the MySQL database:

```sql
CREATE DATABASE damage_inspection_db;
```

Run the database migrations:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Or manually create tables using the provided SQL:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20),
    inspected_by INT,
    damage_report TEXT,
    status ENUM('pending', 'reviewed', 'completed') DEFAULT 'pending',
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspected_by) REFERENCES users(id)
);
```

### 6. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## 🔌 API Endpoints

### Authentication Endpoints

#### 1. User Registration
- **Endpoint**: `POST /api/signup`
- **Description**: Register a new user
- **Authentication**: Not required

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "created_at": "2025-01-15T10:30:00"
    }
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric and underscores only
- Password: 6-128 characters

#### 2. User Login
- **Endpoint**: `POST /api/login`
- **Description**: Authenticate user and get JWT token
- **Authentication**: Not required

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "created_at": "2025-01-15T10:30:00"
    }
}
```

#### 3. Get User Profile
- **Endpoint**: `GET /api/profile`
- **Description**: Get current user profile
- **Authentication**: Required (JWT token)

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200 OK):**
```json
{
    "message": "Profile retrieved successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "created_at": "2025-01-15T10:30:00"
    }
}
```

### Inspection Endpoints

#### 1. Create Inspection
- **Endpoint**: `POST /api/inspection`
- **Description**: Create a new inspection entry
- **Authentication**: Required (JWT token)

**Headers:**
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "vehicle_number": "DL01AB1234",
    "damage_report": "Broken tail light on the rear left side",
    "image_url": "https://example.com/damage-image.jpg"
}
```

**Response (201 Created):**
```json
{
    "message": "Inspection created successfully",
    "inspection": {
        "id": 1,
        "vehicle_number": "DL01AB1234",
        "damage_report": "Broken tail light on the rear left side",
        "status": "pending",
        "image_url": "https://example.com/damage-image.jpg",
        "inspected_by": 1,
        "inspector_username": "john_doe",
        "created_at": "2025-01-15T11:00:00"
    }
}
```

**Validation Rules:**
- Vehicle number: 5-20 characters
- Damage report: 10-1000 characters
- Image URL: Must be valid URL ending with .jpg, .jpeg, or .png

#### 2. Get Inspection by ID
- **Endpoint**: `GET /api/inspection/<id>`
- **Description**: Fetch inspection details (only if created by logged-in user)
- **Authentication**: Required (JWT token)

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200 OK):**
```json
{
    "inspection": {
        "id": 1,
        "vehicle_number": "DL01AB1234",
        "damage_report": "Broken tail light on the rear left side",
        "status": "pending",
        "image_url": "https://example.com/damage-image.jpg",
        "inspected_by": 1,
        "inspector_username": "john_doe",
        "created_at": "2025-01-15T11:00:00"
    }
}
```

#### 3. Update Inspection Status
- **Endpoint**: `PATCH /api/inspection/<id>`
- **Description**: Update inspection status to reviewed or completed
- **Authentication**: Required (JWT token)

**Headers:**
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "status": "reviewed"
}
```

**Response (200 OK):**
```json
{
    "message": "Inspection status updated successfully",
    "inspection": {
        "id": 1,
        "vehicle_number": "DL01AB1234",
        "damage_report": "Broken tail light on the rear left side",
        "status": "reviewed",
        "image_url": "https://example.com/damage-image.jpg",
        "inspected_by": 1,
        "inspector_username": "john_doe",
        "created_at": "2025-01-15T11:00:00"
    }
}
```

**Valid Status Values:**
- `reviewed`
- `completed`
- `pending`

#### 4. Get All Inspections (with optional filtering)
- **Endpoint**: `GET /api/inspection`
- **Description**: Fetch all inspections for the logged-in user with optional status filtering
- **Authentication**: Required (JWT token)

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `reviewed`, `completed`)

**Examples:**
- Get all inspections: `GET /api/inspection`
- Get pending inspections: `GET /api/inspection?status=pending`
- Get reviewed inspections: `GET /api/inspection?status=reviewed`

**Response (200 OK):**
```json
{
    "inspections": [
        {
            "id": 1,
            "vehicle_number": "DL01AB1234",
            "damage_report": "Broken tail light on the rear left side",
            "status": "pending",
            "image_url": "https://example.com/damage-image.jpg",
            "inspected_by": 1,
            "inspector_username": "john_doe",
            "created_at": "2025-01-15T11:00:00"
        },
        {
            "id": 2,
            "vehicle_number": "MH12CD5678",
            "damage_report": "Dented front bumper",
            "status": "reviewed",
            "image_url": "https://example.com/damage-image2.png",
            "inspected_by": 1,
            "inspector_username": "john_doe",
            "created_at": "2025-01-15T12:00:00"
        }
    ],
    "count": 2
}
```

## 🔒 Authentication

All inspection endpoints require JWT authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Get the JWT token by calling the `/api/login` endpoint with valid credentials.

## ❌ Error Responses

### Common Error Formats

**400 Bad Request:**
```json
{
    "error": "Validation error message"
}
```

**401 Unauthorized:**
```json
{
    "error": "Invalid username or password"
}
```

**404 Not Found:**
```json
{
    "error": "Inspection not found or access denied"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error"
}
```

## 🧪 Testing

Run the tests using pytest:

```bash
python -m pytest
```



## 📝 Logging

The application logs all requests with timestamps and route information. Logs include:
- Request method and endpoint
- User authentication status
- Database operations
- Error details


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

