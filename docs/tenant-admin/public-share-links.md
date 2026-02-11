# Managing Public Share Links

As a Tenant Admin, you have the ability to create and manage public links that allow customers and stakeholders to access specific POCs without authentication. This guide walks you through the process.

## Creating a Public Link

### Step-by-Step

1. **Navigate to a POC**
   - Go to your POC list and select the POC you want to share
   - Click on the POC to open its detail page

2. **Click "Create Share Link"**
   - Look for the green **"🔗 Create Share Link"** button in the top-right area
   - This button only appears for Tenant Admins

3. **Review the Security Warning**
   - A modal will appear with a ⚠️ warning
   - Read the important points:
     - "This link will allow anyone with the URL to access this POC without requiring login"
     - No authentication required
     - Limited to customer role for this POC only
     - Share carefully with trusted parties only
     - You can delete the link at any time

4. **Confirm Creation**
   - Click the **"Create Link"** button to generate the public link
   - The system will create a unique, secure token

5. **Copy the Link**
   - After creation, the Link Management modal appears
   - Click the **"Copy"** button to copy the URL to your clipboard
   - You'll see a confirmation toast: "Link copied to clipboard!"

### Example Link

A public link looks like this:
```
https://poc-manager.example.com/share/rA5k_xY2pQ8jM1nL_Z9vW4bK3tH6cJ0
```

## Managing Existing Links

### Viewing Your Current Link

Once a public link exists for a POC:

1. Go to the POC detail page
2. The button changes to **"🔗 Manage Share Link"** (blue badge)
3. Click the button to open the Link Management modal

### Link Management Modal

The modal displays:
- **Share Link** - The full public URL
- **Copy Button** - Click to copy the link to clipboard
- **Creation Date** - When the link was created
- **Close Button** - Close the modal without changes
- **Delete Link Button** - Permanently revoke access (see below)

## Deleting a Public Link

### When to Delete

Delete a public link when:
- You want to revoke stakeholder access
- The POC should no longer be publicly visible
- The stakeholder no longer needs access
- The POC is complete and should be archived

### How to Delete

1. Click **"🔗 Manage Share Link"** on the POC detail page
2. The Link Management modal opens showing your current link
3. Click the red **"Delete Link"** button at the bottom
4. A confirmation dialog appears: "Are you sure you want to delete this public link? Anyone with the link will no longer be able to access the POC."
5. Click **"OK"** to confirm deletion
6. The link is immediately revoked
   - Anyone trying to access the old link will see an error
   - The modal closes and the button returns to **"🔗 Create Share Link"**

### After Deletion

- The link becomes immediately inaccessible
- Users visiting the old link see: "Invalid or expired public link"
- You can create a new link for the same POC anytime
- Previously shared links cannot be reactivated

## Important Considerations

### Security ⚠️

- **Public Access** - Anyone with the link can view the POC, regardless of location or authentication
- **No Expiration** - Links remain valid indefinitely until you delete them
- **No Rate Limiting** - Public endpoints are not rate-limited
- **No Analytics** - You cannot see who accessed the link or when

**Best Practice:** Only share links with trusted stakeholders. If you're unsure whether someone should have access, don't share the link.

### One Link Per POC

- Each POC can have **only one active public link**
- If you try to create a second link while one exists, you'll get an error
- To create a new token for the same POC: delete the old link, then create a new one

### What Customers Can See

Customers with a public link can view:
- ✅ POC title, description, dates
- ✅ Customer company name and logo
- ✅ Executive summary and objectives
- ✅ All tasks and task groups
- ✅ Success criteria and task status
- ✅ Task assignments
- ✅ Comments and discussions

Customers **cannot**:
- ❌ Create or modify POCs
- ❌ Create or modify tasks
- ❌ Change task status
- ❌ Modify success criteria
- ❌ Manage tenant settings
- ❌ Access admin features

## Common Scenarios

### Scenario 1: Customer Demo
```
Customer Request: "Can you give me a demo of the POC progress?"
Your Action:
1. Open the POC detail page
2. Click "Create Share Link"
3. Confirm the warning
4. Copy the link
5. Send via email: "Here's your demo link: [URL]"
6. Customer clicks link, no login needed
7. Customer reviews their POC progress
```

### Scenario 2: Revoking Access
```
Situation: Customer has completed their POC review
Your Action:
1. Open the POC detail page
2. Click "Manage Share Link"
3. Click "Delete Link"
4. Confirm deletion
5. Send email: "Your access link has been revoked"
6. Old link now shows error if accessed
```

### Scenario 3: Creating New Link After Deletion
```
Situation: You accidentally deleted a link, need to recreate it
Your Action:
1. Open the POC detail page
2. Button shows "Create Share Link" (since old one was deleted)
3. Click and confirm to create a new link
4. This is a NEW token (different from the previous one)
5. Old link still doesn't work
6. Share new link with stakeholders
```

## Troubleshooting

### "A public link already exists for this POC"
- A link already exists for this POC
- Click "Manage Share Link" to view and copy the existing link
- Delete the link first if you want to create a new token

### Link is not copying to clipboard
- Try again - sometimes browser permissions block clipboard access
- Manually select and copy the URL from the Link Management modal
- Try a different browser

### Customers say the link doesn't work
- Verify the link hasn't been deleted
- Check that you sent them the full URL (including domain)
- Confirm they're using an active internet connection
- Links work in any browser, no special requirements

### Can I see who accessed the public link?
- Currently, no access analytics are available
- The system only tracks creation date and creator
- For usage tracking, you may need to request feedback directly from stakeholders

## API Information for Developers

### Create Link
```bash
curl -X POST \
  'http://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json'
```

### Get Link
```bash
curl -X GET \
  'http://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Delete Link
```bash
curl -X DELETE \
  'http://api.example.com/pocs/123/public-link' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

## See Also

- [Features: Public Share Links Overview](../features/public-share-links.md)
- [Customer: Accessing Public POCs](../customer/accessing-public-pocs.md)
- [POC Management](./managing-pocs.md)
