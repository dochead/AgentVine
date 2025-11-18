# AgentVine Frontend

Modern, production-ready React frontend for AgentVine - a powerful multi-agent platform.

## Tech Stack

- **React 18+** - Modern React with concurrent features
- **TypeScript** - Full type safety with strict mode enabled
- **Vite** - Fast build tool with HMR
- **React Router** - Type-safe routing solution
- **Tailwind CSS v4** - Utility-first CSS framework
- **ESLint** - Code quality and consistency

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (optional for development)

## Getting Started

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev
```

The development server will start with:
- Hot Module Replacement (HMR) for instant updates
- API proxy to backend at `http://localhost:8000`
- Tailwind CSS v4 with instant compilation

### Build

```bash
# Build for production
npm run build
```

This will:
- Type-check all TypeScript files
- Build optimized production bundle
- Generate source maps for debugging
- Output to `dist/` directory

### Preview Production Build

```bash
# Preview production build locally
npm run preview
```

### Linting

```bash
# Run ESLint
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable React components
│   │   └── Navigation.tsx  # Top navigation bar
│   ├── pages/             # Page components
│   │   ├── Home.tsx       # Landing page
│   │   └── About.tsx      # About page
│   ├── App.tsx            # Main app component with React Router
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles with Tailwind directives
├── public/                # Static assets
├── .env                   # Environment variables
├── .env.example           # Environment variables template
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## Features

### Pages

1. **Home (Landing Page)**
   - Welcome message and platform description
   - Feature highlights with icons
   - Modern gradient design
   - Call-to-action buttons

2. **About Page**
   - Application name: AgentVine
   - Version: 0.01
   - Platform information
   - Key features list
   - Technology stack details

### Navigation

- Responsive top navigation bar
- Active link highlighting
- Smooth transitions
- Clean, professional design

## Configuration

### Environment Variables

Create a `.env` file (or copy from `.env.example`):

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AgentVine
VITE_APP_VERSION=0.01
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

### Vite Configuration

The `vite.config.ts` includes:
- Development server on port 3000
- API proxy to backend (`/api` → `http://localhost:8000`)
- Source maps for production debugging
- React plugin with Fast Refresh

### Tailwind Configuration

Configured to scan all relevant files:
- `./index.html`
- `./src/**/*.{js,ts,jsx,tsx}`

## Development Guidelines

### TypeScript

- Strict mode enabled for maximum type safety
- No unused locals or parameters allowed
- Full type coverage required

### Styling

- Use Tailwind utility classes
- Follow mobile-first responsive design
- Maintain consistent spacing and colors
- Use semantic color names (indigo, purple, etc.)

### Routing

- Use React Router for all navigation
- Define routes in `src/App.tsx`
- Component-based routing:
  - `/` → Home page
  - `/about` → About page

### Components

- Functional components with TypeScript
- Props typed with interfaces
- Reusable components in `src/components/`
- Page components in `src/pages/`

## API Integration

The frontend is configured to connect to the backend API at `http://localhost:8000`.

### Proxy Configuration

All requests to `/api/*` are proxied to the backend server:

```typescript
// Example API call
fetch('/api/agents')
  .then(res => res.json())
  .then(data => console.log(data));
```

For future API integration:
- Use TanStack Query for data fetching
- Create typed API client bindings
- Implement proper error handling
- Add loading states

## Performance

The application is optimized for:
- Fast initial load with code splitting
- Minimal bundle size
- Efficient re-renders with React.memo
- Route-based lazy loading (ready for implementation)

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES2022 support required
- Automatic vendor prefixing via autoprefixer

## Contributing

1. Follow TypeScript strict mode rules
2. Use Tailwind CSS for styling
3. Ensure ESLint passes before committing
4. Write semantic, accessible HTML
5. Test responsive layouts on multiple screen sizes

## Deployment

### Production Build

```bash
npm run build
```

The `dist/` directory contains:
- Optimized JavaScript bundles
- Minified CSS
- Source maps
- Static assets

### Deployment Options

1. **Static Hosting** (Netlify, Vercel, Cloudflare Pages)
   ```bash
   # Build and deploy dist/ directory
   npm run build
   ```

2. **Docker**
   ```dockerfile
   FROM nginx:alpine
   COPY dist/ /usr/share/nginx/html
   ```

3. **CDN**
   - Upload `dist/` contents to CDN
   - Configure for SPA (redirect all routes to index.html)

## Troubleshooting

### Port Already in Use

If port 3000 is taken, change it in `vite.config.ts`:
```typescript
server: {
  port: 3001, // or any available port
}
```

### API Connection Issues

- Ensure backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.ts`

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## License

See LICENSE file in the repository root.

## Support

For issues and questions, please refer to the main AgentVine repository.
