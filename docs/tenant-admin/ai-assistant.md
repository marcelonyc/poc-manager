# AI Assistant Configuration

As a **Tenant Admin**, you manage the AI Assistant setup for your organization. This guide explains how to enable and configure the feature.

## Overview

The AI Assistant uses **cloud-hosted language models** through an Ollama-compatible API. Configuration requires:

1. A valid **API key** for the cloud service
2. Tenant Admin access to enable the feature

Once configured, all eligible team members (not customers) can use the AI Assistant to query POC data. No local installation or infrastructure is required.

## Prerequisites

Before enabling the AI Assistant, ensure you have:

### API Key

You'll need a valid **API key** for the cloud-hosted model service. This is provided by the service provider and configured by your Tenant Admin in POC Manager settings.

No local installation, servers, or infrastructure setup is required—the AI Assistant connects to cloud-hosted models directly.

## Enabling AI Assistant

### Step 1: Open Tenant Settings

1. Log in as **Tenant Admin**
2. Navigate to **Settings** (gear icon in top navigation)
3. Scroll to the **AI Assistant** section

### Step 2: Review Requirements

You'll see a warning dialog explaining:

!!! warning
    The AI Assistant uses cloud-hosted language models. You must provide a valid API key for the service. Chat messages will be processed by the cloud service.

Review and confirm:
- ☑️ You have a valid API key for the cloud service
- ☑️ You understand that chat messages will be processed by the cloud service

### Step 3: Toggle Enable

1. Click the **Enable AI Assistant** toggle
2. Confirmation dialog appears
3. Click **I Understand, Enable** to confirm

### Step 4: Enter API Key

1. The **API Key** field becomes visible
2. Enter your API key in the text field
   - Keys are securely encrypted before storage
   - Leave blank on future edits to keep existing key
3. Click **Save AI Assistant Settings**

You'll see a success message: *"AI Assistant settings saved successfully"*

### Step 5: Verify Configuration

The AI Assistant is now enabled. Users will see:
- ✅ **Active** badge next to AI Assistant in settings
- 💬 **AI Assistant** button in the bottom-right corner (when they next log in)

!!! success
    Your AI Assistant is ready to use!

## Configuration

### Updating API Key

To update the API key for an existing configuration:

1. Go to **Settings** → **AI Assistant**
2. Scroll to **API Key** field
3. Enter the **new API key**
   - Tip: Leave blank if you just want to verify, don't submit the form
4. Click **Save AI Assistant Settings**

!!! note "Key Update Behavior"
    - **Enter a new key**: Updates to the new key
    - **Leave blank**: Keeps existing key unchanged
    - **This helps** when you want to change only other settings

### Environment Variables (for Deployment)

If you're deploying POC Manager, the `.env` file configures the model and features:

```bash
# Model Configuration
OLLAMA_BASE_URL=https://ollama.com              # Cloud service endpoint
OLLAMA_MODEL=gemini-3-flash-preview:cloud       # Tested production model
MCP_TOOLS=list_pocs,list_poc_tasks,list_users   # Tools available to AI
```

### Disabling AI Assistant

To turn off the AI Assistant:

1. In **Tenant Settings** → **AI Assistant**
2. Click the **Enable AI Assistant** toggle to turn **OFF**
3. Click **Save AI Assistant Settings**

Effects:
- 🚫 Users see "AI Assistant is not enabled" message
- 💬 AI Assistant button disappears from interface
- 🔒 Existing sessions end immediately
- 📊 Feature is available again when re-enabled

## Supported Models

The AI Assistant works with cloud-hosted language models through an Ollama-compatible API.

### Recommended Models

| Model | Speed | Quality | Recommendation |
|-------|-------|---------|----------------|
| **gemini-3-flash-preview:cloud** | Medium | Excellent | ✅ **Production (Tested & Recommended)** |
| **gpt-oss:120b-cloud** | Slow | Good | ⚠️ Testing only (not recommended for production) |

!!! success "Tested Production Model"
    **gemini-3-flash-preview:cloud** has been tested and validated for production use. This model provides the best balance of accuracy, response time, and reliability.

!!! warning "Testing Models"
    **gpt-oss:120b-cloud** can be used for testing and development but is **not recommended for production** due to slower response times.

### Changing Models

To use a different model:

1. Contact your platform administrator
2. They will update the `OLLAMA_MODEL` environment variable
3. Restart the POC Manager service
4. The new model will be used for all future AI Assistant sessions

## Monitoring and Troubleshooting

### Health Checks

Verify the cloud service is accessible:

```bash
# Test API key and connectivity
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://ollama.com/api/models
```

### Common Issues

#### Issue: "API key is incorrect or expired"

**Troubleshooting:**
1. Verify the API key is correct (copy from provider)
2. Check if key is still active (not revoked or expired)
3. Verify API key format matches provider requirements
4. Test key independently: `curl -H "Authorization: Bearer YOUR_KEY" ...`

**Solution:** Update the API key in Tenant Settings

#### Issue: "Connection timeout" or "Cannot reach service"

**Troubleshooting:**
1. Check your internet connection
2. Verify the API key is valid and not expired
3. Check the cloud provider status page for service issues
4. Verify POC Manager can reach the cloud service (no firewall restrictions)

**Solution:** Contact cloud provider support if service is down

#### Issue: "Model not found"

**Troubleshooting:**
1. Verify the model name is correct (case-sensitive)
2. Check if the cloud provider supports the model you configured
3. Verify the field `OLLAMA_MODEL` in `.env` matches available models

**Solution:** Use a supported model or contact cloud provider

#### Issue: "Rate limited" or "Too many requests"

**Troubleshooting:**
1. Check if the cloud provider has rate limiting enabled
2. Review cloud provider dashboard for usage/limits
3. Reduce simultaneous AI Assistant sessions
4. Check provider pricing tier for rate limit capacity

**Solution:** Upgrade provider plan or reduce usage

#### Issue: Users see "Not configured" despite settings being saved

**Troubleshooting:**
1. Verify API key was actually saved (check success message)
2. Check browser cache (clear cookies/cache)
3. Have user log out and log back in
4. Verify tenant settings are properly loading

**Solution:** Re-enter API key and save, then have user refresh

### Monitoring Usage

!!! note "Usage Monitoring"
    POC Manager does not currently track AI Assistant usage metrics. To monitor:
    
    - Review cloud provider dashboard for API usage
    - Monitor API key usage/costs with provider
    - Check for unusual activity or failed requests
    - Ask users for feedback on feature usage

## Data Privacy & Security

### Data Flow

When a user sends a message:

```
1. User: Types message in POC Manager
   ↓
2. POC Manager Backend: Validates user auth, adds to session
   ↓
3. Message Sent to Cloud Service: "User's message + conversation context"
   ↓
4. Cloud LLM: Processes message, may fetch POC data via MCP tools
   ↓
5. Response Returned: LLM-generated response
   ↓
6. User: Receives response in POC Manager
```

### Where Is Data Stored?

- **Conversation History**: Stored in-memory on POC Manager server (per-session, 10-minute timeout)
- **Chat Messages**: Sent to cloud LLM service for processing
- **Long-term Storage**: NOT stored in POC Manager—history is session-based only
- **Cloud Service**: Data handling depends on your cloud provider's policies

### Security Recommendations

1. **API Key Security**
   - Store in secure secrets manager
   - Rotate keys regularly
   - Never commit keys to version control
   - Use strong, random keys

2. **Encrypt in Transit**
   - All connections to cloud service use HTTPS
   - Verify SSL certificates
   - POC Manager uses encrypted storage for API keys

3. **Cloud Provider Trust**
   - Review provider's security practices
   - Check data residency policies
   - Verify encryption at rest
   - Review data retention policies

4. **Monitor Access**
   - Review cloud provider access logs
   - Monitor for unauthorized API calls
   - Set up alerts for suspicious activity

5. **Compliance**
   - Ensure cloud provider meets your compliance requirements
   - Review terms of service for data handling
   - Verify GDPR/HIPAA compliance if needed

!!! warning "Sensitive Data"
    Do NOT include actual customer data, passwords, or secrets in POC definitions. The AI Assistant can access these if they're in your POC data, so POC Manager data should never contain sensitive information regardless.

## Best Practices

### ✅ Do

- **Use production model**: Configure gemini-3-flash-preview:cloud for best results
- **Secure API key**: Store in secrets manager, rotate regularly
- **Monitor usage**: Check cloud provider dashboard for costs and usage
- **Test with team**: Have users provide feedback on accuracy and usefulness
- **Keep key secure**: Never commit API keys to repositories
- **Review cloud provider**: Understand their data handling and security practices

### ❌ Don't

- **Use testing models in production**: gpt-oss:120b-cloud is for development only
- **Hardcode API keys**: Always use environment variables or secrets manager
- **Share API credentials**: Each instance should have unique keys
- **Skip security review**: Understand provider's security and compliance
- **Ignore usage costs**: Monitor cloud provider billing
- **Store sensitive data in POCs**: Assume AI Assistant can access all POC data

## Rollback / Disabling

If you need to temporarily or permanently disable the AI Assistant:

### Temporary Disable (for maintenance)

1. Go to **Settings** → **AI Assistant**
2. Toggle **Enable AI Assistant** to **OFF**
3. Save settings
4. Fix any issues
5. Re-enable when ready

### Permanent Disable

1. In **Settings** → **AI Assistant**, toggle OFF
2. Save settings
3. The feature will no longer be available to users

## Support & Help

If you encounter issues:

1. **Check this guide** - Your question may be answered above
2. **Verify API key**: Ensure key is correct and not expired
3. **Check cloud provider status**: Service may be experiencing issues
4. **Review logs**: Check for error messages in POC Manager or cloud provider
5. **Contact support**: Include error message and setup details

---

**Last Updated**: February 2026
**Version**: 1.0
**Status**: Production Ready
