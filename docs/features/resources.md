# Resources

Resources are essential components of POC Manager that provide context, documentation, and materials to support POC tasks. This guide covers everything about the resource system.

## What are Resources?

Resources are attachments to tasks or task groups that provide:

- **Documentation**: Links to guides, manuals, references
- **Code**: Sample code, snippets, configurations
- **Information**: Instructions, notes, explanations
- **Files**: Documents, diagrams, presentations
- **Reference Materials**: Related content and materials

Resources help all POC participants understand what needs to be done and how to accomplish it.

## Resource Types

### Links

External URL references.

**Characteristics:**
- Points to external content
- Can be any accessible URL
- Opens in new browser tab
- Most common resource type

**Common uses:**
- Documentation websites
- API references
- Video tutorials
- Knowledge base articles
- GitHub repositories
- Tool interfaces
- Support portals

**Example:**
```
Type: Link
Title: "API Authentication Guide"
URL: https://docs.example.com/api/v2/authentication
Description: "Complete guide to implementing OAuth 2.0 
authentication with code examples and troubleshooting tips."
Tags: authentication, api, oauth
```

### Code Snippets

Executable or reference code samples.

**Characteristics:**
- Formatted with syntax highlighting
- Copy-to-clipboard functionality
- Language-specific formatting
- Inline display

**Common uses:**
- API call examples
- Configuration files
- Integration code
- Script templates
- SQL queries
- Command-line examples

**Example:**
```
Type: Code
Title: "Python Authentication Example"
Language: Python
Description: "Complete authentication flow implementation"
Code:
import requests
from datetime import datetime, timedelta

class APIAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.expires_at = None
    
    def get_token(self):
        if self.token and datetime.now() < self.expires_at:
            return self.token
        
        response = requests.post(
            "https://api.example.com/oauth/token",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
        )
        
        data = response.json()
        self.token = data["access_token"]
        self.expires_at = datetime.now() + timedelta(
            seconds=data["expires_in"]
        )
        
        return self.token

# Usage
auth = APIAuth("your_client_id", "your_client_secret")
token = auth.get_token()
print(f"Token: {token}")

Tags: authentication, python, example
```

### Text Notes

Written instructions or information.

**Characteristics:**
- Plain text or markdown formatted
- Multi-paragraph support
- Lists and formatting
- Inline display

**Common uses:**
- Step-by-step instructions
- Prerequisites lists
- Tips and best practices
- Explanations
- Troubleshooting guides
- Configuration notes

**Example:**
```
Type: Text
Title: "Setup Prerequisites"
Content:
Before beginning the integration, ensure you have:

Required:
• Node.js version 18 or higher
• Docker Desktop installed and running
• Git client configured
• At least 8GB available RAM
• Port 3000 and 5432 available

Optional but Recommended:
• Postman or similar API testing tool
• VS Code with relevant extensions
• Database management tool (pgAdmin, DBeaver)

Network Requirements:
• Access to api.example.com (port 443)
• Ability to install npm packages
• Webhook endpoint (can be ngrok for testing)

Credentials Needed:
• API client ID and secret (provided separately)
• Database connection string (will be generated)

Estimated Setup Time: 30-45 minutes

If you encounter issues, see the Troubleshooting Guide or
contact support.

Tags: setup, prerequisites, requirements
```

### Files

Uploaded documents (if enabled).

**Characteristics:**
- Stored in the system
- Various file types supported
- Download capability
- May have size limits

**Common uses:**
- PDF documentation
- Architecture diagrams
- Presentation slides
- Spreadsheets
- Images and screenshots
- Templates and forms

**Example:**
```
Type: File
Title: "System Architecture Diagram"
File: architecture-v2.pdf (2.4 MB)
Description: "High-level architecture showing all system 
components, data flows, and integration points. Version 2
includes the updated authentication flow."
Tags: architecture, diagram, reference
```

## Resource Attributes

### Core Attributes

Every resource has:

| Attribute | Required | Description |
|-----------|----------|-------------|
| **Type** | Yes | Link, Code, Text, or File |
| **Title** | Yes | Clear, descriptive name |
| **Description** | No | Additional context (recommended) |
| **Content/URL** | Yes* | The actual resource content or link |
| **Language** | No | For code snippets (enables syntax highlighting) |
| **Tags** | No | Keywords for organization and search |
| **Created By** | Auto | User who created the resource |
| **Created At** | Auto | Creation timestamp |

*Required based on type

### Extended Attributes

Additional metadata:

- **Last Updated**: When the resource was modified
- **Access Count**: How many times it's been viewed (if tracked)
- **Related Tasks**: Tasks using this resource
- **Status**: Active, deprecated, outdated
- **Version**: For versioned resources

## Resource Organization

### Color Coding

Resources are visually distinguished by type:

```
┌─────────────────────────────────────────┐
│ Resources                               │
├─────────────────────────────────────────┤
│ 🔗 API Documentation                    │
│    Link • docs.example.com              │
│                                         │
│ 💻 Authentication Example               │
│    Code • Python                        │
│                                         │
│ 📝 Setup Instructions                   │
│    Text • Prerequisites and steps       │
│                                         │
│ 📄 Architecture Diagram                 │
│    File • PDF • 2.4 MB                  │
└─────────────────────────────────────────┘
```

Color scheme:
- 🔗 **Blue**: Links
- 💻 **Green**: Code
- 📝 **Yellow/Orange**: Text
- 📄 **Purple**: Files

### Grouping

Resources can be organized:

**By task:**
- Each task has its own resource list
- Resources are contextual to the task

**By task group:**
- Shared resources for all tasks in a group
- Common prerequisites or references

**By POC:**
- POC-level resources accessible from all tasks
- General references and documentation

### Tags

Use tags for organization:

```
Common tags:
• setup, configuration, prerequisites
• api, integration, authentication
• troubleshooting, faq, help
• example, template, sample
• diagram, architecture, design
• security, compliance, audit
• performance, optimization
• testing, qa, validation
```

## Working with Resources

### Viewing Resources

**In task view:**

1. Open a task
2. Scroll to **Resources** section
3. Resources are listed with:
   - Icon indicating type
   - Title
   - Brief description
   - Quick actions (view, copy, download)

**Resource details:**

Click on any resource to see:
- Full description
- Complete content
- Metadata (created by, date, etc.)
- Tags
- Usage information

### Using Resources

**Links:**
1. Click link title or URL
2. Opens in new browser tab
3. Original tab stays on POC Manager

**Code snippets:**
1. View formatted code with syntax highlighting
2. Click **Copy** button to copy to clipboard
3. Paste into your development environment

**Text notes:**
1. Read inline in POC Manager
2. Can be copied and pasted
3. Markdown rendering (if supported)

**Files:**
1. Click **Download** to save locally
2. Opens in appropriate application
3. Can be viewed inline for some types (PDFs, images)

### Searching Resources

**Search within POC:**

1. Use search box
2. Enter keywords
3. Results include:
   - Resource title matches
   - Description matches
   - Tag matches
   - Content matches (for text/code)

**Filter resources:**

- By type (links, code, text, files)
- By task
- By tags
- By date added
- By author

## Resource Management

### Adding Resources

**During task creation:**

1. Create/edit task
2. Scroll to resources section
3. Click **Add Resource**
4. Fill in details
5. Save task (saves all resources)

**To existing task:**

1. Open task
2. Go to resources section
3. Click **Add Resource**
4. Complete form
5. Click **Save Resource**

**From templates:**

- Task templates include pre-configured resources
- When you use a template, resources are copied
- Customize as needed for specific POC

### Editing Resources

1. Open task
2. Find resource to edit
3. Click edit icon (✏️)
4. Modify fields
5. Click **Save**

**Considerations:**
- Editing affects all users viewing the resource
- Consider adding a new version instead of editing
- Update "Last Modified" information
- Notify users of significant changes

### Deleting Resources

1. Open task
2. Find resource to delete
3. Click delete icon (🗑️)
4. Confirm deletion

!!! warning "Permanent Deletion"
    Deleted resources cannot be recovered. Consider marking as
    "deprecated" or moving to an archive task instead.

### Reordering Resources

1. Open task
2. Drag resource by handle (☰)
3. Drop in desired position
4. Order saves automatically

**Recommended order:**
1. Prerequisites and setup resources first
2. Documentation links
3. Code examples
4. Troubleshooting guides
5. Advanced or optional resources last

## Resource Templates

### Creating Reusable Resources

**Resource libraries:**

1. Create task templates with common resources
2. Resources are copied when template is used
3. Maintain centralized resource library
4. Update templates to update future uses

**Common resource sets:**

```
API Integration Template:
├─ Link: API Documentation
├─ Link: API Console
├─ Code: Authentication Example
├─ Code: Basic API Call Example
├─ Text: Common API Patterns
├─ Text: Troubleshooting Guide
└─ File: API Postman Collection

Security Review Template:
├─ Link: Security Whitepaper
├─ Link: Compliance Certifications
├─ Text: Security Checklist
├─ File: Security Architecture Diagram
└─ Link: Vulnerability Disclosure Policy

Setup Template:
├─ Text: Prerequisites
├─ Link: Installation Guide
├─ Code: Configuration Template
├─ Code: Environment Variables
├─ Link: Troubleshooting Guide
└─ Text: Common Issues and Solutions
```

### Best Practices for Templates

✅ **Do:**
- Create templates for common task types
- Keep resources up-to-date
- Include comprehensive documentation
- Provide working code examples
- Add clear descriptions
- Use consistent naming

❌ **Don't:**
- Create overly generic templates
- Include outdated resources
- Duplicate resources unnecessarily
- Use broken links
- Forget to test code examples

## Advanced Features

### Resource Linking

**Link to success criteria:**

Resources can support specific success criteria:

```
Success Criterion: "System handles 1000 concurrent users"

Supporting Resources:
├─ Link: Performance Testing Guide
├─ Code: Load Test Script
├─ Text: Performance Benchmarks
└─ File: Test Results Template
```

**Cross-task resources:**

Reference the same resource in multiple tasks:
- Maintains single source of truth
- Updates propagate to all tasks
- Reduces duplication

### Resource Versioning

**Track resource changes:**

```
Resource: "API Documentation"
├─ Version 1.0 (Feb 1): Initial documentation
├─ Version 1.1 (Feb 5): Added authentication section
├─ Version 2.0 (Feb 10): Major update - new endpoints
└─ Current: Version 2.0
```

**Version management:**
- Keep history of changes
- Allow access to previous versions
- Note breaking changes
- Provide migration guides

### Resource Analytics

**Track usage:**

- View count: How often accessed
- Last accessed: When last viewed
- Most popular: Frequently used resources
- Least used: Candidates for removal

**Insights:**
- Which resources customers find most helpful
- What documentation is missing
- Where to focus improvements
- Success patterns

## Integration

### External Content

**Embed resources:**

Some resource types can be embedded:
- YouTube videos (if supported)
- Google Docs (with permissions)
- Figma designs
- Code sandboxes

### API Access

**Programmatic resource management:**

```python
# Add resource via API
resource = {
    "type": "code",
    "title": "Authentication Example",
    "language": "python",
    "code": "import requests\n...",
    "description": "OAuth 2.0 implementation",
    "tags": ["auth", "python", "example"]
}

response = requests.post(
    f"https://api.pocmanager.com/tasks/{task_id}/resources",
    json=resource,
    headers={"Authorization": f"Bearer {token}"}
)
```

## Best Practices

### Resource Creation

✅ **Do:**
- Use descriptive, clear titles
- Add comprehensive descriptions
- Verify links work before adding
- Test code examples
- Keep resources focused and relevant
- Update resources when information changes
- Tag resources appropriately
- Consider your audience

❌ **Don't:**
- Use vague titles ("Link 1", "Code")
- Add broken or outdated links
- Include untested code
- Create duplicate resources
- Overload tasks with too many resources
- Forget to maintain and update
- Use unclear or missing descriptions

### Resource Maintenance

✅ **Do:**
- Review resources periodically
- Remove outdated content
- Update links when they change
- Refresh code examples for new versions
- Mark deprecated resources
- Archive old versions
- Get feedback from users

### Resource Strategy

✅ **Do:**
- Plan resource structure
- Create resource libraries
- Standardize across POCs
- Balance quantity and quality
- Provide multiple formats
- Consider different learning styles
- Make resources discoverable

---

## FAQs

**Q: How many resources can I add to a task?**  
A: No hard limit, but 3-7 resources per task is typically optimal for usability.

**Q: Can customers add resources?**  
A: No, only Sales Engineers and above can add resources. Customers can suggest resources in comments.

**Q: What file types are supported for file uploads?**  
A: Common types include PDF, Word, Excel, PowerPoint, images (PNG, JPG), and text files. Maximum size depends on configuration.

**Q: Can I share resources between different POCs?**  
A: Resources are POC-specific, but you can use task templates to replicate common resources across POCs.

**Q: How do I know if customers are using my resources?**  
A: If analytics are enabled, you can view access statistics. Otherwise, monitor customer comments for feedback.

**Q: Can resources contain sensitive information?**  
A: Resources are visible to customers, so avoid including sensitive internal information, credentials, or competitive data.

**Q: What happens to resources when a POC ends?**  
A: Resources are preserved with the POC for reference and can be included in generated documents.

**Q: Can I embed videos directly?**  
A: This depends on configuration. You can always add links to videos hosted on YouTube, Vimeo, etc.

---

**Related Documentation:**

- [Adding resources as Sales Engineer →](../sales-engineer/adding-resources.md)
- [Managing tasks →](../sales-engineer/managing-tasks.md)
- [Viewing POCs as customer →](../customer/viewing-pocs.md)
- [Comments system →](comments.md)
