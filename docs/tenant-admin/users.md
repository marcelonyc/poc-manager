# User Management

As a **Tenant Admin**, you manage users within your organization's tenant. This includes inviting new users and managing their access.

## Overview

User management allows you to:

- Invite new users to your tenant
- Assign roles (Administrator or Sales Engineer)
- Activate or deactivate users
- View user information

## Accessing User Management

1. Click **Users** in the main navigation
2. You'll see a list of all users in your tenant

## Viewing Users

The Users page displays:

- **Name**: User's full name
- **Email**: User's email address
- **Role**: User's assigned role
- **Status**: Active or Inactive
- **Actions**: Activate/Deactivate toggle

### User List Features

- View all users in your tenant
- See user roles at a glance
- Quick status management

## Inviting New Users

!!! example "Invite User Steps"
    1. Click **+ Invite User** button (top right)
    2. Fill in the invitation form:
        - **First Name** (required)
        - **Last Name** (required)
        - **Email** (required)
        - **Role** (required): Select Administrator or Sales Engineer
    3. Click **Send Invitation**

### User Roles You Can Assign

=== "Administrator"
    **Best for**: Team members who manage POC templates
    
    **Permissions**:
    
    - Create task and task group templates
    - Add resources to templates
    - View all POCs
    - Cannot manage users
    
    **Use cases**:
    
    - Pre-sales engineers who create templates
    - Technical leads who standardize POC processes
    - Team members who maintain the POC library

=== "Sales Engineer"
    **Best for**: Team members who run POC engagements
    
    **Permissions**:
    
    - Create and manage POCs
    - Invite customers
    - Manage tasks and progress
    - Add comments and resources
    - Cannot create templates
    
    **Use cases**:
    
    - Sales engineers running customer POCs
    - Solution architects managing engagements
    - Account executives overseeing POCs

### Form Validation

The invite form validates:

- ✅ All required fields are filled
- ✅ Email format is correct
- ✅ Email is unique (not already in the system)
- ✅ A role is selected

### After Invitation

Once invited:

1. User receives an email with login credentials
2. User can log in immediately
3. User appears in the user list as **Active**

## Managing Existing Users

### Viewing User Details

The user list shows key information:

- Full name
- Email address
- Assigned role
- Current status

### Activating/Deactivating Users

To change a user's status:

1. Find the user in the list
2. Click the **Activate** or **Deactivate** toggle

**Active Users:**
- ✅ Can log in
- ✅ Full access to permitted features
- ✅ Appear in user selections

**Inactive Users:**
- ❌ Cannot log in
- ❌ No access to the system
- ❌ Hidden from most lists
- ✅ Data remains in the system

!!! warning "Deactivation Impact"
    When you deactivate a user:
    
    - They are immediately logged out
    - Cannot log in again until reactivated
    - Their POCs and tasks remain intact
    - Can be reactivated at any time

## User Roles and Permissions

### Cannot Change Roles

!!! info "Role Assignment"
    Currently, user roles cannot be changed after creation. If a user needs a different role:
    
    1. Deactivate the old account
    2. Create a new invitation with the correct role
    3. Notify the user of the new credentials

### Managing Your Own Role

As a Tenant Admin:

- You cannot change your own role
- You cannot deactivate yourself
- Contact a Platform Admin for changes to your account

## Best Practices

### Inviting Users

- ✅ Use work email addresses
- ✅ Verify email spelling before sending
- ✅ Assign the most appropriate role
- ✅ Notify users to check spam folders
- ❌ Don't share invitation links publicly

### User Management

- Regularly review active users
- Deactivate users who leave the organization
- Keep contact information updated
- Document role assignments

### Security

- Only invite users who need access
- Review user list periodically
- Deactivate unused accounts
- Use strong passwords (educate users)

## Common Scenarios

### New Team Member Onboarding

1. Invite user with appropriate role
2. Send welcome email with system overview
3. Provide link to relevant documentation
4. Assign a mentor or point of contact

### Team Member Leaving

1. Deactivate their account immediately
2. Reassign their active POCs if needed
3. Document any ongoing work
4. Archive or transfer important data

### Temporary Access

For contractors or temporary staff:

1. Invite with appropriate role
2. Set a reminder to deactivate on end date
3. Deactivate promptly when access no longer needed

## Troubleshooting

### User Didn't Receive Invitation

If a user reports not receiving an invitation:

1. Check the email address for typos
2. Ask them to check spam/junk folders
3. Verify the email was sent successfully
4. Resend if necessary (deactivate and re-invite)

### User Can't Log In

If an active user can't log in:

1. Verify their account status is Active
2. Confirm they're using the correct email
3. Check if password needs reset
4. Verify they're accessing the correct tenant URL

### Wrong Role Assigned

If a user has the wrong role:

1. Deactivate the incorrect account
2. Send a new invitation with correct role
3. Notify the user of the change
4. They'll need new login credentials

## Next Steps

After inviting users:

- **Administrators** can proceed to [create task templates](../administrator/task-templates.md)
- **Sales Engineers** can start [creating POCs](../sales-engineer/poc-overview.md)
- Configure [tenant settings](settings.md) for branding and integrations

---

**Related Documentation:**

- [User Roles](../getting-started/roles.md) - Detailed role permissions
- [Task Templates](../administrator/task-templates.md) - For Administrators
- [POC Overview](../sales-engineer/poc-overview.md) - For Sales Engineers
