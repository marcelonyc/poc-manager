# Tenant Logo Feature

## Overview
Tenant Admins can upload a custom logo for their tenant. The logo will be displayed in the navigation bar instead of the default "POC Manager" text, providing tenant-specific branding.

## Features

### Backend API Endpoints

#### Upload Tenant Logo
- **Endpoint**: `POST /tenants/{tenant_id}/logo`
- **Auth Required**: Yes (Tenant Admin only)
- **Content-Type**: `multipart/form-data`
- **File Parameter**: `file`
- **Restrictions**:
  - Maximum file size: 2 MB
  - Allowed formats: JPEG, PNG, GIF, WebP
  - Only one logo per tenant

**Request Example**:
```bash
curl -X POST "http://localhost:8000/tenants/1/logo" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/logo.png"
```

**Response**:
```json
{
  "message": "Logo uploaded successfully",
  "logo_url": "http://localhost:8000/uploads/logos/acme-corp-abc123.png"
}
```

#### Delete Tenant Logo
- **Endpoint**: `DELETE /tenants/{tenant_id}/logo`
- **Auth Required**: Yes (Tenant Admin only)

**Response**:
```json
{
  "message": "Logo deleted successfully"
}
```

### Frontend UI

#### Tenant Settings Page
Located at `/settings` for Tenant Admins, includes:
- Current logo preview (if exists)
- File upload input with format/size restrictions
- Live preview of selected file before upload
- Upload and Cancel buttons
- Delete logo option for existing logos

#### Navigation Bar
- Displays tenant logo in the top-left corner for tenant users
- Falls back to "POC Manager" text if no logo is set
- Platform Admins always see "POC Manager" text
- Logo auto-refreshes when updated

## Technical Implementation

### Database Schema
Added `logo_url` column to `tenants` table:
- Type: VARCHAR (nullable)
- Stores the URL path to the uploaded logo file
- Migration: `20260130_2034-6fe79fa706ee_add_tenant_logo_url.py`

### File Storage
- Files stored in: `backend/uploads/logos/`
- Naming convention: `{tenant_slug}-{uuid}.{extension}`
- Old logos automatically deleted when new one is uploaded
- Served via FastAPI StaticFiles mounted at `/uploads`

### Frontend Components Updated
1. **TenantSettings.tsx**:
   - Added logo upload form
   - File validation (client-side)
   - Preview functionality
   - Upload/delete handlers

2. **Layout.tsx**:
   - Fetches tenant logo on mount
   - Displays logo instead of text when available
   - Only shown for non-Platform Admin users

### Security Considerations
- Only Tenant Admins can upload/delete logos for their tenant
- File type validation prevents non-image uploads
- File size limit prevents large uploads
- Unique filenames prevent overwrites
- API endpoints check tenant ownership

## Usage

### For Tenant Admins

1. Navigate to Settings page
2. Scroll to "Tenant Logo" section
3. Click "Choose File" and select your logo
4. Preview will appear showing the logo
5. Click "Upload" to save the logo
6. Logo will immediately appear in navigation bar
7. To change logo, repeat steps 3-5
8. To remove logo, click "Delete Logo"

### Best Practices
- Use transparent PNG for best results
- Recommended dimensions: 200x50 pixels (4:1 aspect ratio)
- Keep file size under 500 KB for fast loading
- Use high-contrast colors for visibility
- Test logo appearance on different screen sizes

## API Integration Example

### TypeScript/React
```typescript
// Upload logo
const uploadLogo = async (file: File, tenantId: number) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post(`/tenants/${tenantId}/logo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  
  return response.data.logo_url
}

// Delete logo
const deleteLogo = async (tenantId: number) => {
  await api.delete(`/tenants/${tenantId}/logo`)
}
```

## Troubleshooting

### Logo Not Displaying
- Check browser console for errors
- Verify logo_url in tenant settings API response
- Ensure static files are mounted correctly
- Check file permissions on uploads directory

### Upload Fails
- Verify file size is under 2 MB
- Check file format (must be JPEG/PNG/GIF/WebP)
- Ensure user has Tenant Admin role
- Check backend logs for errors

### Logo Quality Issues
- Use higher resolution source image
- Ensure proper aspect ratio (wider than tall)
- Save as PNG with transparency for best quality
- Avoid overly complex designs

## Future Enhancements
- [ ] Logo cropping/editing in UI
- [ ] Multiple logo variants (light/dark theme)
- [ ] Favicon upload for branded browser tabs
- [ ] Logo preview in tenant list for Platform Admins
- [ ] Image optimization/compression on upload
