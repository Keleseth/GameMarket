# GameMarket Frontend

## Project Structure
This is a Next.js 14 application using the App Router and TypeScript.

### Directory Structure

- **src/app/**: Next.js App Router pages and layouts
- **src/components/**: React components
  - **ui/**: Reusable UI components (Button, Card, Input, etc.)
  - **layout/**: Layout components (Header, Footer, Navigation)
  - **features/**: Feature-specific components (GameList, ShoppingCart, etc.)
- **src/lib/**: Library configurations (API client, Stripe)
- **src/hooks/**: Custom React hooks
- **src/services/**: API service functions
- **src/types/**: TypeScript type definitions
- **src/utils/**: Utility functions
- **public/**: Static assets (images, fonts)

## Setup
1. Install dependencies: `npm install`
2. Copy `.env.local.example` to `.env.local` and configure
3. Start development server: `npm run dev`
4. Build for production: `npm run build`

## Tech Stack
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Stripe (Payment processing)
- Axios (HTTP client)
- Zustand (State management)
- React Hook Form + Zod (Form handling & validation)
