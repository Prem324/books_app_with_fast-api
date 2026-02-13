# Books API Project

Full-stack Bookshelf app with a FastAPI backend and a React (Vite) frontend. Users can register, log in, manage their book collection, search, and upload cover images.

## Features
- User registration and login (JWT auth)
- Create, read, update, delete books
- Search by title, author, year, ISBN
- Optional cover image upload (Supabase Storage)

## Tech Stack
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT
- Frontend: React, Vite, Axios

## Project Structure
- `backend/` FastAPI app, database models, API routes
- `frontend/` React app (Vite)
- `DEPLOY.md` deployment notes

## Prerequisites
- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- A database supported by SQLAlchemy (SQLite/Postgres/MySQL, etc.)

## Backend Setup
1. Create a `.env` file in `backend/`:
```env
DATABASE_URL=sqlite:///./books.db
SECRET_KEY=change_this_secret

# Optional: only needed for image upload
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=your-bucket-name
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run the API:
```bash
uvicorn backend.main:app --reload
```

The API will run at `http://localhost:8000`.

## Frontend Setup
1. Create a `.env` file in `frontend/` (optional):
```env
VITE_API_BASE_URL=http://localhost:8000
```

2. Install dependencies:
```bash
npm install --prefix frontend
```

3. Run the frontend:
```bash
npm run --prefix frontend dev
```

The app will run at `http://localhost:5173` by default.

## API Overview
- `POST /users/register` Create a new user
- `POST /users/login` Authenticate and return JWT token
- `GET /books` List books (supports query filters)
- `POST /books` Add a new book
- `PUT /books/{book_id}` Update a book
- `DELETE /books/{book_id}` Delete a book
- `POST /books/{book_id}/image` Upload book cover

## Notes
- Books are always scoped to the authenticated user.
- Image upload requires Supabase configuration in `backend/.env`.

## Next Steps
- Add tests
- Add pagination to the books list
- Improve error handling and validation UX
