# Tenant Management

As a **Platform Admin**, you have the ability to create and manage tenants across the entire POC Manager platform.

## Overview

Tenants represent separate organizations using POC Manager. Each tenant has:

- Isolated data and users
- Custom branding
- Independent configuration
- Separate workspace

## Accessing Tenant Management

1. Click **Tenants** in the main navigation
2. You'll see a list of all tenants on the platform

## Viewing Tenants

The Tenants page displays:

- **Tenant Name**: Organization name
- **Status**: Active or Inactive
- **Created Date**: When the tenant was created
- **Actions**: Edit button

### Tenant List Features

- Search and filter tenants
- Sort by name or date
- Quick access to edit

## Creating a New Tenant

!!! example "Create Tenant Steps"
    1. Click **+ New Tenant** button (top right)
    2. Fill in the tenant information:
        - **Name** (required): Organization name
        - **Description**: Brief description of the tenant
    3. Click **Create Tenant**

### Tenant Form Fields

| Field | Required | Description |
|-------|----------|-------------|
| Name | ✅ | The organization's name |
| Description | ❌ | Additional details about the tenant |

### After Creation

Once created:

- The tenant is immediately active
- You can add a tenant administrator
- Tenant admin can configure settings and invite users

## Editing a Tenant

To modify an existing tenant:

1. Click **Edit** next to the tenant name
2. A modal opens with the tenant details
3. Update the information:
   - Name
   - Description
4. Click **Update Tenant**

!!! warning "Important"
    - Changing a tenant name affects how it appears throughout the system
    - Users will see the updated name immediately

## Tenant Status

### Active Tenants
- Can log in and use the system
- All features available
- Can create POCs and manage data

### Inactive Tenants
Currently, all tenants are active. Future versions may support:

- Temporarily suspending tenants
- Deactivating tenants
- Archiving old tenants

## Best Practices

### Naming Conventions
- Use clear, recognizable organization names
- Be consistent with naming (e.g., "Acme Corp" not "ACME" or "acme")
- Avoid special characters

### Tenant Descriptions
- Include key information like industry or use case
- Note the primary contact if applicable
- Add creation date or business context

### Regular Maintenance
- Periodically review tenant list
- Verify active tenants
- Clean up test or demo tenants

## Common Tasks

### Onboarding a New Organization

1. Create the tenant
2. Note the tenant ID
3. Create the first tenant admin user
4. Provide login credentials to the tenant admin
5. Tenant admin can then invite additional users

### Managing Multiple Tenants

When managing many tenants:

- Use descriptive names
- Keep tenant descriptions updated
- Document tenant-specific configurations
- Monitor tenant activity

## Troubleshooting

### Cannot Create Tenant

If you can't create a tenant:

- Verify you're logged in as Platform Admin
- Check for error messages in the form
- Ensure all required fields are filled
- Contact system support if issues persist

### Tenant Not Appearing

If a newly created tenant doesn't appear:

- Refresh the page
- Check your internet connection
- Verify the creation was successful (look for success message)

## Next Steps

After creating a tenant:

1. Create a tenant administrator account
2. Provide access credentials
3. Tenant admin can configure settings and invite users
4. Monitor tenant usage and activity

---

**Related Documentation:**

- [User Management](../tenant-admin/users.md) - How tenant admins manage users
- [Tenant Settings](../tenant-admin/settings.md) - Configuring tenant options
