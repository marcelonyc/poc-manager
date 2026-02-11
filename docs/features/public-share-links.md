# Public Share Links

## Overview

Public Share Links allow Tenant Admins to create unique, secure links that enable customers and other stakeholders to access a specific POC without requiring authentication or creating user accounts. This feature is ideal for sharing POCs with external stakeholders who need limited, read-only access.

## Key Features

✅ **No Authentication Required** - Customers access POCs via public links without login
✅ **Secure Tokens** - Cryptographically secure, unguessable 256-bit URL-safe tokens
✅ **One Link Per POC** - Only one active public link per POC (prevents link proliferation)
✅ **Easy Management** - Create, view, copy, and delete links from the POC detail page
✅ **Read-Only Access** - Public users cannot modify POCs, only view them
✅ **Revocation** - Tenant admins can immediately revoke access by deleting the link
✅ **Warning System** - Admins receive security warnings before creating public links

## How It Works

### For Tenant Admins
1. Navigate to a POC detail page
2. Click the **"🔗 Create Share Link"** button
3. Review the security warning (confirms "anyone with the link will have access without authentication")
4. Click **"Create Link"** to generate the public link
5. Copy the link and share it with customers
6. Anytime: Click **"🔗 Manage Share Link"** to view, copy, or delete the link

### For Customers
1. Receive a public link from the Tenant Admin
2. Click the link (works in any browser, anywhere)
3. View the POC details, tasks, task groups, and success criteria
4. Cannot modify anything (read-only access)
5. If the link is revoked, access is denied immediately

## Security Model

### What's Protected
- Only Tenant Admins can create/delete public links
- Links are unique and verified before granting access
- One link per POC (prevents duplicate link creation)
- Soft deletes preserve audit trail

### What's Accessible
- POC details (title, description, dates, objectives, etc.)
- Task and task group listings
- Success criteria
- Task status and assignments
- Comments (depending on configuration)

### What's NOT Accessible
- POC creation/editing
- Task modification
- User management
- Tenant settings
- Any admin features

## Use Cases

- **Customer Demos** - Share POC status with external customers without creating accounts
- **Stakeholder Reviews** - Allow executives/partners to monitor POC progress
- **Sales Enablement** - Demo POCs to prospects or partners
- **Compliance & Audits** - Grant temporary access to auditors or regulators
- **Cross-Org Collaboration** - Share status with partner organizations

## Access URL Format

```
https://your-domain.com/share/{access_token}
```

Example:
```
https://poc-manager.example.com/share/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0
```

## API Endpoints

### Create Public Link
```
POST /pocs/{poc_id}/public-link
```
**Auth Required:** Tenant Admin
**Response:**
```json
{
  "id": 1,
  "poc_id": 123,
  "access_token": "rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "access_url": "https://domain.com/share/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0",
  "created_at": "2026-02-11T20:00:00Z",
  "created_by": 5
}
```

### Get Public Link
```
GET /pocs/{poc_id}/public-link
```
**Auth Required:** Tenant Admin
**Response:** Same as Create (if link exists)

### Delete Public Link
```
DELETE /pocs/{poc_id}/public-link
```
**Auth Required:** Tenant Admin
**Status Code:** 204 No Content

### Access Public POC (No Auth)
```
GET /public/pocs/{access_token}
```
**Auth Required:** None
**Response:** Full POC details

## Best Practices

1. **Share with Caution** - Only share public links with trusted stakeholders
2. **Communicate Scope** - Let recipients know they're viewing a public/demo environment
3. **Monitor Usage** - Check creation and deletion timestamps
4. **Rotate Links** - Consider deleting and recreating links periodically
5. **Revoke Immediately** - Delete links when stakeholder should no longer have access
6. **Use Descriptively** - Remember which customers have which links

## Limitations

- Only one public link per POC
- No access restrictions (anyone with URL can view)
- No usage analytics (no tracking of who accessed the link)
- No expiration dates (links remain valid until deleted)
- No rate limiting on public endpoints

## See Also

- [Tenant Admin: Managing Public Links](../tenant-admin/public-share-links.md)
- [Customer: Accessing Public POCs](../customer/accessing-public-pocs.md)
