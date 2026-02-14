# AI Assistant

The AI Assistant is an intelligent, context-aware chat interface that helps you get instant answers about your POCs, tasks, resources, and project data. Powered by LLMs and integrated with your existing POC data, it streamlines information retrieval and decision-making.

!!! info "Beta Feature"
    The AI Assistant is currently in **Beta**. Features and APIs may change. We welcome your feedback!

## Overview

The AI Assistant provides:

- **Natural language queries** about POCs, tasks, and resources
- **Instant data retrieval** across all your POC information
- **Context-aware responses** based on your role and access permissions
- **Tool integration** with POC Manager APIs through MCP (Model Context Protocol)
- **Secure sessions** with automatic timeouts and role-based access control

## Getting Started

### Prerequisites

Before using the AI Assistant, your Tenant Admin must:

1. **Enable AI Assistant** in tenant settings
2. **Configure the API key** for secure communication

!!! info "Cloud-Hosted Models"
    The AI Assistant uses cloud-hosted language models through an Ollama-compatible API. Your Tenant Admin manages the API key configuration. No local installation is required.


## Getting an Ollama API Key

### Step 1: Create an Ollama Account

1. Visit [ollama.com](https://ollama.com)
2. Click **Sign Up** in the top-right corner
3. Enter your email address and create a password
4. Verify your email by clicking the link sent to your inbox
5. Complete your profile information

### Step 2: Generate an API Key

1. Log in to your Ollama account
2. Navigate to **Account Settings** → **API Keys**
3. Click **Create New API Key**
4. Give it a descriptive name (e.g., "POC Manager")
5. Select the appropriate permissions for the AI Assistant
6. Click **Generate**
7. Copy the API key immediately—you won't be able to see it again

!!! warning "Secure Your API Key"
    - Store it in a password manager or secure secrets vault
    - Never commit it to version control
    - Never share it with team members directly
    - Regenerate it if you suspect it's been compromised

### Step 3: Add to POC Manager

Once you have your API key, follow the [Enabling AI Assistant](#enabling-ai-assistant) instructions above to configure it in your tenant settings.


### Opening the AI Assistant

1. Look for the **AI Assistant button** (💬 with "AI Assistant" label) in the bottom-right corner of the screen
2. Click to open the chat interface
3. You'll see the AI Assistant status:
   - **✅ Ready**: AI Assistant is enabled and configured
   - **❌ Not Enabled**: Contact your Tenant Admin to enable it
   - **⚠️ Not Configured**: API key is not set (Tenant Admin action required)

### Starting a Conversation

1. Click in the **message input field** at the bottom of the chat window
2. Type your question or request
3. Press **Enter** or click **Send** to submit
4. The AI Assistant will process your query and provide a response

The conversation history is maintained in your current **session** (10-minute inactive timeout).

## Available to User Roles

| Role | Access |
|------|--------|
| **Platform Admin** | ❌ Not available |
| **Tenant Admin** | ✅ Yes |
| **Administrator** | ✅ Yes |
| **Sales Engineer** | ✅ Yes |
| **Customer** | ❌ Not available |

!!! note
    Customers and Platform Admins cannot access the AI Assistant. The feature is designed for internal team members who manage POCs.

## Enabling AI Assistant

### For Tenant Admins

To enable the AI Assistant for your tenant:

1. Navigate to **Tenant Settings** (admin only)
2. Scroll to **AI Assistant** section
3. Click the **Enable AI Assistant** toggle
4. A warning dialog will appear. Review the requirements:
   - You have a valid API key for the cloud service
   - You understand that chat messages are processed by the cloud service
5. Click **I Understand, Enable** to confirm
6. Enter your **API Key** in the provided field
   - Leave blank if updating an existing key
7. Click **Save AI Assistant Settings**

!!! info "Cloud-Hosted Models"
    The AI Assistant uses cloud-hosted language models. Your Tenant Admin manages the API key configuration for secure access. No local installation or infrastructure is required.

## Using the AI Assistant

### Example Queries

Here are common types of questions you can ask:

#### POC Information
```
"What POCs are currently in progress?"
"Show me all POCs for Acme Corp"
"How many customers have completed their POCs?"
```

#### Task Management
```
"What tasks are assigned to me?"
"Which tasks in the Marketing POC are blocked?"
"List all incomplete tasks from this quarter"
```

#### Resource Discovery
```
"Find all code snippets related to authentication"
"Show me resources linked to API integration tasks"
"What documentation do we have for the payment module?"
```

#### Progress & Metrics
```
"What's the overall completion rate for active POCs?"
"Which POCs are at risk of missing their end date?"
"How many participants does the Analytics POC have?"
```

#### Participant Information
```
"Who are the participants in the CRM POC?"
"List all sales engineers assigned to active POCs"
"What customers are currently engaged?"
```

### Chat Features

#### Markdown Support
Responses are rendered with full markdown support, including:
- **Bold text** and *italic text*
- Code snippets with syntax highlighting
- Bullet points and numbered lists
- Links and tables
- Quotes and blockquotes

#### Copy Responses
Each response includes a **Copy** button to quickly copy the content to your clipboard.

#### Session Management
- **Conversation history** is maintained within a session
- Sessions **auto-timeout after 10 minutes** of inactivity
- Click **New Chat** to start a fresh conversation
- Your session is **private to your user account**

#### Message History
The AI Assistant remembers recent messages in your conversation to provide contextual responses. Use this to build on previous queries:
```
User: "How many active POCs do we have?"
AI: [responds with list]

User: "Who are the participants in the first one?"
AI: [responds with participants from first POC]
```

## How It Works

### Architecture

The AI Assistant combines several technologies:

```
┌─────────────────┐
│  Chat Interface │ (Your browser)
│ (React Component)│
└────────┬────────┘
         │
         │ HTTP/REST
         ▼
┌─────────────────────────┐
│  POC Manager Backend    │
│  - Session Management   │
│  - Role-based Access    │
│  - Security/JWT Auth    │
└────────┬────────────────┘
         │
         ├─────────────┬──────────────┐
         ▼             ▼              ▼
    ┌────────┐   ┌──────────┐   ┌─────────┐
    │ Ollama │   │   MCP    │   │Database │
    │  LLM   │   │  Tools   │   │Content  │
    └────────┘   └──────────┘   └─────────┘
```

### Behind the Scenes

1. **You send a message** to the chat interface
2. **Session validated** - your message is added to conversation history
3. **LLM receives prompt** - your question + system instructions + tools catalog
4. **Tool execution** - if needed, the LLM calls MCP tools to fetch real data
   - MCP tools use your auth token to ensure RBAC
   - Only data you can access is returned
5. **Response generated** - the LLM synthesizes a natural language response
6. **Response sent back** - rendered in chat with markdown formatting

### Role-Based Access Control

The AI Assistant respects your **role-based permissions**:

- You can only query data you have access to
- MCP tools verify your roles before returning data
- Responses only include POCs, tasks, and resources in your tenant
- Tenant data is completely isolated

## Conversation Tips

### Be Specific
```
✅ Good:   "What are the blocked tasks in the 'API Integration' POC?"
❌ Poor:   "Show me tasks"
```

### Use Context
```
✅ Good:   "How many participants does the Acme Corp POC have?"
❌ Poor:   "participants?" (unclear which POC)
```

### Break Down Complex Queries
```
✅ Better: 
  1. "List all POCs with status = 'In Progress'"
  2. "How many tasks does the first POC have?"
  3. "Show me any blocked tasks"

❌ Complex:
  "Show me all in-progress POCs with their task counts and blocked tasks"
```

### Don't Ask for Sensitive Data
```
❌ "What is the admin password?"
❌ "Show me all user email addresses"

The AI Assistant won't share sensitive information outside your access level.
```

## Session Management

### Session Timeout

- **Timeout Duration**: 10 minutes of inactivity
- **What happens**: Automatic logout, chat history cleared
- **Reset**: Start a new chat

### Manual Controls

| Action | Effect |
|--------|--------|
| **Close Chat** | Session remains active in background |
| **New Chat** | Creates new session, clears message history |
| **Page Refresh** | Session persists (within timeout) |
| **Logout** | All sessions end |
| **Timeout** | Toast notification, automatic closure |

### Using Multiple Sessions

You can open the AI Assistant in multiple browser tabs/windows. Each session:
- Is independent
- Has its own 10-minute timeout
- Maintains separate conversation history
- Uses your current user credentials

## Configuration (Tenant Admin)

### Ollama API Key Management

!!! warning "Important"
    - API keys are **encrypted** before storage
    - Keys are **only used for AI Assistant** sessions
    - Never share your API key with others
    - Store keys in a **secure secrets manager**

### Updating Settings

To modify AI Assistant settings:

1. Go to **Tenant Settings** → **AI Assistant**
2. Make changes:
   - Toggle AI Assistant on/off
   - Update Ollama API key (leave blank to keep existing)
   - Change any configuration options
3. Click **Save AI Assistant Settings**
4. See confirmation message

### Disabling AI Assistant

To turn off the feature:

1. In **Tenant Settings** → **AI Assistant**
2. Click the **Enable AI Assistant** toggle to **OFF**
3. Click **Save AI Assistant Settings**
4. Users will see "AI Assistant is not enabled" message

All existing sessions will end, and the button will disappear from the interface.

## MCP Tools

The AI Assistant can use **MCP Tools** to query POC data in real-time. These tools are automatically discovered from the POC Manager backend.

### Available Tools (Example)

When enabled, the AI Assistant has access to tools like:

- `list_pocs` - Get information about POCs
- `list_poc_tasks` - Retrieve tasks for a specific POC
- `list_participants` - Find POC participants
- `list_users` - Look up user information
- `get_poc` - Get detailed POC information

!!! note
    Tools available depend on your Tenant Admin configuration (via `MCP_TOOLS` environment variable).

### What the LLM Does with Tools

The LLM automatically decides whether to use tools:

```
User Query: "What tasks are in the Auth POC?"

LLM Decision Flow:
1. Parse query: "Find tasks in Auth POC"
2. Determine tools needed: list_pocs (to find Auth POC), list_poc_tasks (get tasks)
3. Call tools with appropriate parameters
4. Receive structured data
5. Format response in natural language:
   "The Auth POC has 5 tasks: Authentication..."
```

You never see the technical details—just the natural language response!

## Limitations

| Limitation | Details |
|-----------|---------|
| **No Data Modification** | The AI Assistant is read-only. It cannot create, update, or delete POCs, tasks, etc. Make changes directly in POC Manager. |
| **Model Availability** | Responses depend on your Ollama service being available and responsive. |
| **Knowledge Cutoff** | The LLM has a training cutoff date and may not know about recent features. |
| **Context Limits** | Long conversations may be summarized to stay within token limits. |
| **Hallucination Risk** | While MCP tools help, the LLM may occasionally provide inaccurate information if tools don't fully answer the question. |
| **No Real-Time Events** | The AI Assistant reflects current database state; it's not aware of live updates from other users. |

## Troubleshooting

### "AI Assistant is not enabled"

**Solution**: Contact your Tenant Admin and ask them to enable the AI Assistant in Tenant Settings.

### "AI Assistant is enabled but Ollama API key is not configured"

**Solution**: Your Tenant Admin needs to add the Ollama API key in Tenant Settings → AI Assistant.

### Response is taking too long

**Solution**:
1. Check if your Ollama service is running
2. Check network connectivity to Ollama endpoint
3. Try a simpler query first
4. Wait up to 2 minutes (default timeout)

### "I'm having trouble processing your request"

**Possible causes**:
- Ollama service is down
- API key is incorrect or expired
- Network connectivity issue
- LLM model not available on Ollama service

**Solution**:
1. Notify your Tenant Admin
2. Verify Ollama service is running: `curl https://OLLAMA_URL/api/models`
3. Verify API key is correct
4. Try again in a few moments

### Chat messages are not appearing

**Solution**:
1. Check your internet connection
2. Verify browser console for errors (press F12)
3. Try closing and reopening the AI Assistant
4. Refresh the page
5. Clear browser cache if issues persist

### Session timed out unexpectedly

**Solution**:
1. This is normal after 10 minutes of inactivity
2. Click **New Chat** to start a fresh conversation
3. If you need longer sessions, keep the chat window active

## Best Practices

### ✅ Do

- **Start simple** - Ask one thing at a time
- **Be specific** - Include POC names, dates, or other identifiers
- **Verify results** - Check responses against POC Manager for accuracy
- **Use feedback** - Report issues to improve the AI Assistant
- **Keep sessions short** - Start new chats for different topics

### ❌ Don't

- **Ask for sensitive data** - Passwords, API keys, etc. (you shouldn't have access anyway)
- **Rely entirely on AI** - Use POC Manager as the source of truth
- **Leave sensitive responses visible** - Copy-paste responses to others carefully
- **Share API keys** - Never include your Ollama API key in conversations

## FAQ

**Q: Who can see my conversations?**
A: Only you can see your chat history. Sessions are user-specific and encrypted in transit. Your Tenant Admin can see that the feature is being used but not conversation content.

**Q: Can the AI Assistant modify my POC data?**
A: No, it's read-only. It can only retrieve and display information. Make changes directly in POC Manager.

**Q: Is my data sent to OpenAI or other external services?**
A: No, your data is sent only to your Ollama API endpoint, which you control. It's a bring-your-own-model feature.

**Q: Can I use any LLM with the AI Assistant?**
A: Yes, as long as it's compatible with Ollama. Your Tenant Admin configures the model in settings.

**Q: How much does the AI Assistant cost?**
A: Costs depend on your Ollama setup. If you self-host, it's free (hardware costs only). If using a cloud provider, pricing varies by provider and usage.

**Q: What happens to my chat history?**
A: History is stored in your session during the 10-minute window. After timeout, it's automatically deleted. We do not retain chat history between sessions.

**Q: Can I export chat history?**
A: Currently, no built-in export. You can manually copy responses using the Copy button.

**Q: What's the maximum message length?**
A: The AI Assistant handles typical messages (< 4,000 characters). Extremely long messages may be truncated.

## Support

If you encounter issues or have feedback:

1. **Check this documentation** - Your question may be answered here
2. **Contact your Tenant Admin** - They can verify settings and enable features
3. **Report bugs** - Include what you asked and what response you got
4. **Request features** - Suggest what would make the AI Assistant more helpful

---

**Last Updated**: February 2024  
**Status**: Beta  
**Feedback**: We'd love to hear from you! This feature is actively being improved based on user input.
