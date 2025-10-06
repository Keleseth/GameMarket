# README for backend
# GameMarket Backend

## Project Structure
This project follows Domain-Driven Design (Clean Architecture) principles:

- **domain/**: Business logic and entities
  - **entities/**: Domain entities (User, Game, Order, Payment)
  - **value_objects/**: Value objects (Email, Money)
  - **services/**: Domain services
  - **exceptions/**: Domain exceptions

- **ports/**: Interfaces (contracts)
  - **repositories/**: Repository interfaces
  - **services/**: Service interfaces

- **adapters/**: Infrastructure implementations
  - **repositories/**: SQLAlchemy repository implementations
  - **services/**: Service implementations
  - **stripe/**: Stripe payment integration

- **api/**: API layer
  - **v1/routers/**: FastAPI routers
  - **v1/schemas/**: Pydantic schemas
  - **v1/dependencies/**: Dependency injection
  - **middlewares/**: Custom middlewares

- **core/**: Application core
  - **config.py**: Configuration management
  - **database.py**: Database connection and session
  - **security.py**: Security utilities

- **tests/**: Test suite
  - **unit/**: Unit tests
  - **integration/**: Integration tests

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run migrations: `alembic upgrade head`
4. Start server: `uvicorn main:app --reload`
