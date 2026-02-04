# Nexus App Setup Guide

This guide explains how to set up and run the Nexus React application that connects to Open WebUI.

## Prerequisites

- Node.js 18+ and npm/yarn installed
- Open WebUI running at `http://localhost:3000`
- Nexus MoA pipeline enabled in Open WebUI
- Open WebUI API key (from Settings → Account)

## Installation

### Step 1: Install Dependencies

Navigate to the `nexus-app` directory and install dependencies:

```bash
cd nexus-app
npm install
```

### Step 2: Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and set your Open WebUI API key:

```env
VITE_OPEN_WEBUI_URL=http://localhost:3000
VITE_OPEN_WEBUI_API_KEY=your_actual_api_key_here
VITE_NEXUS_MODEL=Nexus MoA
```

**Getting Your API Key:**
1. Open Open WebUI in your browser (`http://localhost:3000`)
2. Go to **Settings** → **Account**
3. Copy your API key
4. Paste it into the `.env` file

### Step 3: Start the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Usage

1. **First Launch**: If no API key is configured, you'll see a setup screen where you can enter your API key
2. **Chat Interface**: Once configured, you'll see the chat interface
3. **Send Messages**: Type a message and press Enter (or click Send) to send it to the Nexus MoA pipeline
4. **Loading Indicator**: A loading indicator will show while Nexus is processing your request

## Project Structure

```
nexus-app/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # React components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   └── LoadingIndicator.tsx
│   ├── services/           # API services
│   │   └── openWebUIApi.ts
│   ├── styles/            # CSS styles
│   │   ├── theme.css
│   │   └── components.css
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env                    # Environment variables (create from .env.example)
```

## Troubleshooting

### API Key Not Working

- Verify the API key in Open WebUI Settings → Account
- Check that the API key is correctly set in `.env` file
- Ensure `.env` file is in the `nexus-app` directory
- Restart the dev server after changing `.env`

### Connection Errors

- **"Failed to fetch"**: Check that Open WebUI is running at `http://localhost:3000`
- **"401 Unauthorized"**: Verify your API key is correct
- **"403 Forbidden"**: Check Open WebUI API settings and authentication

### Model Not Found

- Ensure "Nexus MoA" pipeline is enabled in Open WebUI
- Check that the pipeline container is running: `docker ps | findstr pipelines`
- Verify the connection in Open WebUI Admin → Settings → Connections

### CORS Errors

If you see CORS errors, ensure Open WebUI allows requests from `http://localhost:5173`. This should work by default for localhost.

## Building for Production

To build the app for production:

```bash
npm run build
```

The built files will be in the `dist/` directory. You can serve them with any static file server.

## Development Notes

- The app uses Vite for fast development and hot module replacement
- TypeScript is used for type safety
- React Markdown is used to render assistant responses with markdown formatting
- The theme follows the Minimalist Neo-Future design from the PRD
- API key is stored in localStorage for convenience (can be cleared via browser settings)

## Next Steps

Once the MVP is working:
- Add Council Header component
- Add Confidence Meter visualization
- Add SRE Terminal component
- Add Council Deliberation view
- Enhance with real-time metrics
