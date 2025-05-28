# ScrollIntel Frontend

This is the frontend application for ScrollIntel, built with React, TypeScript, and Material-UI.

## Features

- Modern, responsive UI with Material-UI components
- Type-safe development with TypeScript
- Authentication and authorization
- Protected routes for admin and user dashboards
- Real-time scroll data visualization
- User management for administrators

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:6006

# Monitoring
REACT_APP_SENTRY_DSN=your_sentry_dsn_here
REACT_APP_LOGROCKET_ID=your_logrocket_id_here

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_MONITORING=true
```

## Development

To start the development server:

```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Testing

To run the test suite:

```bash
npm test
```

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # Reusable components
│   ├── hooks/          # Custom React hooks
│   ├── pages/          # Page components
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main application component
│   └── index.tsx       # Application entry point
├── package.json        # Project dependencies
└── tsconfig.json      # TypeScript configuration
```

## Deployment

### Backend (EC2/VPS)
1. Set up NGINX with SSL
2. Configure environment variables
3. Run with Docker Compose

### Frontend (Vercel/Netlify)
1. Connect repository
2. Set environment variables
3. Deploy

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 