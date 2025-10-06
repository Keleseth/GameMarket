# GameMarket

A full-stack game marketplace application built with FastAPI and Next.js.

## Project Structure

```
GameProject/
├── backend/          # FastAPI + SQLAlchemy async backend
│   ├── domain/       # Business logic & entities (DDD)
│   ├── ports/        # Interfaces/contracts
│   ├── adapters/     # Infrastructure implementations
│   ├── api/          # FastAPI routers & schemas
│   ├── core/         # Config, database, security
│   ├── tests/        # Test suite
│   └── migrations/   # Alembic migrations
│
└── frontend/         # Next.js 14 frontend
    └── src/
        ├── app/         # Next.js App Router
        ├── components/  # React components
        ├── lib/         # Library configs
        ├── hooks/       # Custom hooks
        ├── services/    # API services
        ├── types/       # TypeScript types
        └── utils/       # Utilities
```

## Architecture

### Backend (Domain-Driven Design)
- **Domain Layer**: Core business logic and entities
- **Ports**: Interfaces for repositories and external services
- **Adapters**: Infrastructure implementations (SQLAlchemy, Stripe)
- **API Layer**: FastAPI routers and Pydantic schemas
- **Core**: Configuration, database, and security utilities

### Frontend (Next.js)
- **App Router**: Modern Next.js routing
- **Component-based**: Reusable UI components
- **Type-safe**: Full TypeScript support
- **State Management**: Zustand for global state
- **Styling**: Tailwind CSS

## Features
- 🎮 Game marketplace
- 🛒 Shopping cart
- 💳 Stripe payment integration
- 🔐 User authentication & authorization
- 📦 Order management
- 🎨 Modern, responsive UI

## Getting Started

### Backend Setup
```bash
cd GameProject/backend
pip install -r requirements.txt
cp .env.example .env
# Configure .env file
alembic upgrade head
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd GameProject/frontend
npm install
cp .env.local.example .env.local
# Configure .env.local file
npm run dev
```

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Alembic
- Stripe
- Pydantic

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Stripe.js
- Axios
- Zustand

## License
MIT
