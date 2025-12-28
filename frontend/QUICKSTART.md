# Quick Start Guide - Frontend

## Prerequisites
- Node.js 18+ installed
- Backend running on `http://localhost:8000`
- YOLO model trained and placed in `backend/app/model/best.pt`

## Installation (5 minutes)

### 1. Navigate to Frontend
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

This installs:
- React 19 + Vite
- TailwindCSS 4
- Axios (API calls)
- React Router (navigation)
- Recharts (charts)

### 3. Configure Backend URL
The `.env` file is already created with:
```env
VITE_API_URL=http://localhost:8000
```

If your backend runs on a different port, edit this file.

### 4. Start Development Server
```bash
npm run dev
```

The frontend will start on **http://localhost:5173**

## First Time Usage

### Test the Integration:

1. **Open Browser**: Navigate to `http://localhost:5173`

2. **Check Dashboard**: 
   - You should see the dashboard with statistics
   - If you see "Failed to fetch", ensure backend is running

3. **Test Image Detection**:
   - Click "Image Detection" in sidebar
   - Drag & drop a test image
   - Click "Detect Rickshaws"
   - View annotated result

4. **Test Video Detection**:
   - Click "Video Detection"
   - Upload a short test video (< 1 min recommended for first test)
   - Enable counting checkbox
   - Click "Process Video"
   - Wait for processing (may take 1-2 minutes)
   - View processed video with counts

5. **View Analytics**:
   - Click "Analytics"
   - See charts if you have historical data

6. **Check History**:
   - Click "History"
   - View all past detections
   - Try exporting to CSV

## Troubleshooting

### "Failed to fetch dashboard data"
**Problem**: Frontend can't reach backend

**Solutions**:
1. Check backend is running: Open `http://localhost:8000/docs`
2. Check `.env` has correct URL
3. Check browser console for CORS errors
4. Ensure backend CORS settings allow `http://localhost:5173`

### "404 Not Found" on images/videos
**Problem**: Static files not accessible

**Solutions**:
1. Check backend `outputs/` directory exists
2. Verify backend mounts `/outputs` correctly
3. Check file permissions

### Charts not showing
**Problem**: Recharts not installed

**Solution**:
```bash
npm install recharts
```

### Slow video processing
**Problem**: Large video file

**Solutions**:
1. Use shorter videos for testing (10-30 seconds)
2. Reduce video resolution before upload
3. Processing time ≈ video length × 2-3

## Building for Production

### 1. Build
```bash
npm run build
```

This creates optimized files in `frontend/dist/`

### 2. Preview Production Build
```bash
npm run preview
```

### 3. Deploy
Copy the `dist/` folder to your web server

**Environment Variables**:
- Update `VITE_API_URL` to production backend URL before building
- Example: `VITE_API_URL=https://api.example.com`

## Development Tips

### Hot Module Replacement (HMR)
- Changes to React files auto-reload
- No need to restart dev server
- CSS changes apply instantly

### Code Organization
```
src/
├── api/         # API calls (edit client.js for new endpoints)
├── components/  # Reusable UI components
├── pages/       # Main route pages
├── layouts/     # Page layouts
├── hooks/       # Custom React hooks
└── utils/       # Helper functions
```

### Adding New Features

**Example: Add a new page**

1. Create page component:
```jsx
// src/pages/NewPage.jsx
const NewPage = () => {
  return <div>New Page Content</div>;
};
export default NewPage;
```

2. Add route in App.jsx:
```jsx
<Route path="newpage" element={<NewPage />} />
```

3. Add to sidebar navigation in MainLayout.jsx

### Styling with TailwindCSS

Use utility classes directly:
```jsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Content
</div>
```

Common classes:
- Colors: `bg-blue-500`, `text-red-600`
- Spacing: `p-4`, `m-2`, `gap-4`
- Layout: `flex`, `grid`, `hidden md:block`
- Effects: `hover:bg-blue-700`, `transition-colors`

## API Integration Example

### Adding a New API Call

1. **Add function in `src/api/client.js`**:
```javascript
export const getNewData = async () => {
  const response = await apiClient.get('/api/new-endpoint');
  return response.data;
};
```

2. **Use in component**:
```jsx
import { getNewData } from '../api/client';
import useApi from '../hooks/useApi';

const MyComponent = () => {
  const { data, loading, error, execute } = useApi(getNewData);
  
  useEffect(() => {
    execute();
  }, []);
  
  if (loading) return <Loader />;
  if (error) return <div>Error: {error}</div>;
  
  return <div>{JSON.stringify(data)}</div>;
};
```

## Performance Tips

1. **Large Videos**: Process in chunks if possible
2. **Image Optimization**: Resize before upload
3. **Lazy Loading**: Components load on demand
4. **Caching**: Axios caches GET requests
5. **Debouncing**: Use for search/filter inputs

## Security Notes

- No sensitive data in localStorage
- API key should be in backend only
- CORS properly configured
- File upload size limited
- Input validation on forms

## Next Steps

After testing locally:

1. **Backend Enhancements**: See INTEGRATION_SUMMARY.md for recommendations
2. **Real-time Features**: Add WebSocket support
3. **User Authentication**: Add login system
4. **Camera Management**: CRUD for camera configs
5. **Notifications**: Toast messages for events
6. **Dark Mode**: Add theme toggle

## Support

- **Backend API Docs**: http://localhost:8000/docs
- **Frontend Docs**: See INTEGRATION_SUMMARY.md
- **TailwindCSS Docs**: https://tailwindcss.com/docs
- **React Docs**: https://react.dev
- **Recharts Docs**: https://recharts.org

## Success Indicators

✅ **Ready for Production When**:
- Dashboard loads without errors
- Image detection works
- Video processing completes
- Charts display correctly
- History table populates
- Export functions work
- No console errors
- Responsive on mobile

---

**Estimated Setup Time**: 5-10 minutes
**Estimated First Detection**: 2-3 minutes after setup

Enjoy your Smart Rickshaw Monitoring System! 🚗📊
