# Critiq Client

A Next.js application that provides a user interface for the Critiq AI code review service.

## Features

- Submit GitHub pull requests for AI-powered code review
- Support for private repositories with GitHub token
- Real-time task status monitoring
- Multiple analysis types (style, bug, security, performance)

## Tech Stack

- Next.js 13+ with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui Components
- React Hook Form + Zod
- Axios for API calls

## Development

First, install dependencies:

```bash
npm install
```

Create a `.env.local` file with:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## Project Structure

- `/app` - Next.js app router pages and layouts
- `/components` - React components
  - `/ui` - shadcn/ui components
- `/lib` - Utilities and API client
- `/public` - Static assets

## Environment Variables

- `NEXT_PUBLIC_API_URL` - URL of the Critiq API server

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
