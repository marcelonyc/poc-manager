# Tenant Settings

As a **Tenant Admin**, you can configure various settings for your organization's workspace, including branding and integrations.

## Overview

Tenant settings allow you to customize:

- Branding (logo, colors)
- Integration configurations
- Tenant information

## Accessing Settings

1. Click **Settings** in the main navigation
2. Navigate to the relevant settings tab

## Branding

!!! info "Coming Soon"
    Branding customization features are planned for future releases, including:
    
    - Custom logo upload
    - Brand color schemes
    - Custom domain
    - Email templates

## AI Assistant

Enable and configure the **AI Assistant** feature for your tenant.

### What is it?

The AI Assistant is an intelligent chatbot that helps users query POC data using natural language. It's powered by cloud-hosted language models and integrated with POC Manager using MCP tools.

### Key Configuration

- **Enable/Disable**: Control whether the feature is available to users
- **API Key**: Provide credentials for the cloud service

### Setup Instructions

See the complete setup guide: **[AI Assistant Configuration](ai-assistant.md)**

Quick steps:
1. Go to **Settings** → **AI Assistant**
2. Click **Enable AI Assistant** toggle
3. Review the requirements warning
4. Click **I Understand, Enable**
5. Enter your **API Key**
6. Save settings

!!! info "Cloud-Hosted Models"
    The AI Assistant uses cloud-hosted language models. No local installation or server setup is required—you only need to provide the API key for authentication.

## Integrations

Configure integrations with external services to enhance your POC workflow.

### Available Integrations

POC Manager supports integration with:

- **Slack**: Notifications and updates
- **Jira**: Task synchronization
- **GitHub**: Repository linking
- **Email**: Custom email notifications

### Setting Up Integrations

!!! info "Coming Soon"
    Integration configuration is planned for future releases. This will include:
    
    - OAuth authentication
    - API key management
    - Webhook configuration
    - Integration testing

## Tenant Information

### Updating Tenant Details

To update your tenant's basic information:

1. Navigate to Settings
2. Go to the Tenant Info section
3. Update:
   - Organization name
   - Description
   - Contact information
4. Save changes

### What You Can Modify

- Organization name (displayed throughout the app)
- Description
- Primary contact email
- Billing information (if applicable)

### What You Cannot Modify

- Tenant ID (system-generated)
- Creation date
- Platform-level configurations

## User Preferences

Each user can configure their own preferences:

- Language preference
- Timezone
- Notification settings
- Display options

!!! tip "User Settings vs Tenant Settings"
    - **Tenant Settings**: Apply to all users in the organization
    - **User Settings**: Personal preferences for each individual

## Security Settings

### Password Policies

Configure password requirements:

- Minimum length
- Complexity requirements
- Expiration policies
- Reset procedures

!!! info "Coming Soon"
    Advanced security settings are planned for future releases.

### Two-Factor Authentication

!!! info "Coming Soon"
    2FA support is planned for future releases, including:
    
    - SMS verification
    - Authenticator app support
    - Backup codes

## Notification Settings

Configure how and when users receive notifications:

- Email notifications
- In-app notifications
- Slack notifications (if integrated)
- Notification frequency

!!! info "Coming Soon"
    Comprehensive notification settings are planned for future releases.

## Data Management

### Data Retention

Configure data retention policies:

- POC archival rules
- Comment history retention
- Document storage limits
- Backup schedules

!!! info "Coming Soon"
    Data management features are planned for future releases.

### Export Options

Export your tenant data:

- POC reports
- User lists
- Activity logs
- Configuration backup

!!! info "Coming Soon"
    Data export features are planned for future releases.

## Best Practices

### Regular Review

- Review settings quarterly
- Update branding as needed
- Test integrations regularly
- Monitor notification effectiveness

### Documentation

- Document custom configurations
- Keep integration credentials secure
- Track changes to settings
- Share updates with team

### Security

- Use strong API keys
- Rotate credentials regularly
- Limit integration permissions
- Monitor integration usage

## Troubleshooting

### Settings Not Saving

If settings won't save:

1. Check your internet connection
2. Verify you have Tenant Admin role
3. Ensure all required fields are filled
4. Clear browser cache and try again

### Integration Issues

If an integration isn't working:

1. Verify credentials are correct
2. Check API key permissions
3. Review integration logs
4. Test connection
5. Contact support if needed

## Next Steps

After configuring settings:

- Inform users of any changes
- Test integrations
- Monitor for issues
- Keep documentation updated

---

**Related Documentation:**

- [AI Assistant Configuration](ai-assistant.md) - Complete AI Assistant setup and troubleshooting
- [User Management](users.md) - Managing tenant users
- [User Roles](../getting-started/roles.md) - Understanding permissions
