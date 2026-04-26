# Update Frontend API URL

## ✅ Already Updated!

The frontend has been configured to use environment-based API URLs:

- **Development**: `http://localhost:5000/api` (for local testing)
- **Production**: `https://medisense-ai-m0gw.onrender.com/api` (for deployed backend)

## How It Works

1. **Environment Files Created:**
   - `src/environments/environment.ts` - Development (localhost)
   - `src/environments/environment.prod.ts` - Production (Render URL)

2. **API Service Updated:**
   - `api.service.ts` now uses `environment.apiUrl`
   - Automatically switches based on build configuration

## Build Commands

### Development (uses localhost):
```bash
ng serve
# or
npm start
```

### Production (uses Render URL):
```bash
ng build --configuration production
```

## Important: Update Backend CORS

Make sure your Render backend has the correct CORS origins set:

1. Go to Render Dashboard → Your Service → Environment
2. Update `CORS_ORIGINS` environment variable:
   ```
   https://your-frontend-url.com,http://localhost:4200
   ```
   Replace `your-frontend-url.com` with your actual frontend deployment URL

## Testing

1. **Test Backend Health:**
   ```bash
   curl https://medisense-ai-m0gw.onrender.com/api/health
   ```

2. **Test from Frontend:**
   - Open browser console
   - Check Network tab for API calls
   - Should see requests to `https://medisense-ai-m0gw.onrender.com/api/...`

## Troubleshooting

### CORS Errors
- Verify `CORS_ORIGINS` in Render includes your frontend URL
- Check browser console for specific CORS error messages

### Connection Errors
- Verify backend is running (check Render dashboard)
- Test backend health endpoint directly
- Check if backend is in sleep mode (free tier)

