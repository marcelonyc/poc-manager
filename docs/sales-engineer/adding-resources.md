# Adding Resources

Resources provide essential context, documentation, and materials for your POC tasks. This guide covers how to effectively add and manage resources.

## What are Resources?

Resources are attachments to tasks that provide:

- **Documentation**: Links to guides, manuals, API docs
- **Code**: Sample code, snippets, configurations
- **Information**: Notes, instructions, explanations
- **Files**: Documents, diagrams, presentations (if enabled)

Resources help customers and team members understand what needs to be done and how to do it.

## Resource Types

### Links

URL references to external resources.

**Best for:**
- Documentation pages
- Video tutorials
- GitHub repositories
- External tools
- Reference materials

**Example:**
```
Type: Link
Title: "API Documentation"
URL: https://docs.example.com/api/v2
Description: "Complete API reference guide"
```

### Code Snippets

Executable or reference code samples.

**Best for:**
- Configuration examples
- API call samples
- Script templates
- Integration code
- Test cases

**Example:**
```
Type: Code
Title: "Authentication Example"
Language: Python
Code:
import requests

response = requests.post(
    "https://api.example.com/auth",
    json={"username": "demo", "password": "demo123"}
)
token = response.json()["token"]
```

### Text Notes

Written instructions or information.

**Best for:**
- Step-by-step instructions
- Explanations
- Prerequisites
- Tips and tricks
- Context and background

**Example:**
```
Type: Text
Title: "Setup Instructions"
Content:
1. Download the SDK from the link above
2. Extract to your projects directory
3. Run: npm install
4. Configure API key in .env file
5. Test with: npm test
```

### Files

Uploaded documents (if file uploads are enabled).

**Best for:**
- PDF guides
- Architecture diagrams
- Presentations
- Spreadsheets
- Custom documents

## Adding Resources

### From Task View

1. Open the task
2. Scroll to the **Resources** section
3. Click **Add Resource**
4. Select resource type
5. Fill in details
6. Click **Save**

### From Task Creation

While creating a task:

1. Fill in task details
2. Click **Add Resource** in the task form
3. Add resource details
4. Continue adding more resources
5. Save the task (saves all resources)

### From Templates

Task templates can include pre-configured resources:

1. Select a task template
2. Resources are automatically included
3. Review and customize as needed
4. Save the task

## Resource Details

### Required Fields

- **Type**: Link, Code, Text, or File
- **Title**: Clear, descriptive name

### Optional Fields

- **Description**: Additional context
- **URL**: For link resources
- **Code/Content**: For code or text resources
- **Language**: For code snippets (for syntax highlighting)
- **File**: For file uploads

### Color Coding

Resources are color-coded by type for easy identification:

- 🔗 **Blue**: Links
- 💻 **Green**: Code
- 📝 **Yellow**: Text
- 📄 **Purple**: Files

## Best Practices

### Resource Creation

✅ **Do:**
- Use descriptive titles
- Add context in descriptions
- Verify links work before saving
- Test code snippets
- Keep resources relevant to the task
- Update resources as needed

❌ **Don't:**
- Use vague titles like "Link 1"
- Add broken or outdated links
- Include untested code
- Overload tasks with too many resources
- Forget to explain why the resource is relevant

### Resource Organization

✅ **Do:**
- Order resources logically (e.g., documentation first, then code)
- Group related resources
- Remove outdated resources
- Keep resources concise and focused

❌ **Don't:**
- Duplicate resources across tasks unnecessarily
- Mix unrelated resources
- Keep outdated information

### Resource Content

✅ **Do:**
- Keep code snippets focused and complete
- Include language/syntax specification
- Add comments in code
- Provide context for links
- Use official documentation sources

❌ **Don't:**
- Include incomplete code
- Use shortened URLs (use full URLs)
- Link to internal/inaccessible resources for customers
- Forget to update examples when APIs change

## Resource Visibility

### Who Can See Resources?

- **Internal Users**: All users in your tenant can see all resources
- **Customers**: Customers can see resources on tasks in their POCs
- **External vs Internal**: Currently all resources are visible to customers (consider this when adding)

### Sharing Resources

Resources attached to:
- **Tasks**: Visible to anyone who can see the task
- **Task Templates**: Copied when template is used
- **Task Group Templates**: Copied with all tasks in the group

## Managing Resources

### Editing Resources

1. Open the task
2. Find the resource to edit
3. Click the edit icon (✏️)
4. Update details
5. Click **Save**

### Deleting Resources

1. Open the task
2. Find the resource to delete
3. Click the delete icon (🗑️)
4. Confirm deletion

!!! warning "Deletion is Permanent"
    Deleted resources cannot be recovered. Consider updating instead of deleting.

### Reordering Resources

1. Open the task
2. Drag and drop resources to reorder
3. Changes save automatically

## Resource Examples

### Example 1: API Integration Task

```
Task: "Integrate Authentication API"

Resources:
1. Link - "API Documentation"
   URL: https://docs.example.com/auth
   Description: Official authentication guide

2. Code - "Python Authentication Example"
   Language: Python
   Content: [Complete working example]
   Description: Copy-paste ready authentication code

3. Text - "Common Issues and Solutions"
   Content: [Troubleshooting guide]
   Description: Solutions to frequent integration problems

4. Link - "Postman Collection"
   URL: https://www.postman.com/collections/12345
   Description: Pre-configured API requests for testing
```

### Example 2: Setup Task

```
Task: "Configure Development Environment"

Resources:
1. Text - "Prerequisites"
   Content: 
   - Node.js 18 or higher
   - Docker Desktop
   - Git client
   - 8GB RAM minimum

2. Link - "Installation Guide"
   URL: https://setup.example.com
   Description: Step-by-step installation instructions

3. Code - "Environment Configuration"
   Language: Bash
   Content: [.env file template]
   Description: Configuration file template

4. Link - "Troubleshooting Guide"
   URL: https://support.example.com/setup
   Description: Common setup issues and solutions
```

### Example 3: Review Task

```
Task: "Review Security Features"

Resources:
1. Link - "Security Whitepaper"
   URL: https://security.example.com/whitepaper.pdf
   Description: Comprehensive security documentation

2. Link - "Compliance Certifications"
   URL: https://trust.example.com
   Description: SOC 2, ISO 27001, GDPR compliance info

3. Text - "Security Checklist"
   Content: [Detailed checklist]
   Description: Items to verify during review

4. Link - "Security Demo Video"
   URL: https://youtu.be/example
   Description: 15-minute overview of security features
```

## Advanced Topics

### Resource Templates

Create reusable resource sets:

1. Define common resources for frequent tasks
2. Save as task templates
3. Reuse across POCs

### Dynamic Resources

For resources that change:

1. Use descriptive titles indicating they're dynamic
2. Update regularly
3. Add "Last Updated" dates in descriptions
4. Notify customers of important updates

### Success Criteria Linkage

Link resources to success criteria:

1. Tag resources with relevant success criteria
2. Show how the resource helps achieve goals
3. Track which criteria have supporting resources

## Troubleshooting

### Link Not Opening

- Verify URL is correct and complete
- Check if URL requires authentication
- Test link in private/incognito browser
- Ensure URL is publicly accessible for customers

### Code Not Displaying Correctly

- Check code formatting
- Verify language is set correctly
- Look for special characters that need escaping
- Test code in actual environment

### Resource Not Saving

- Check all required fields are filled
- Verify resource isn't too large (for files)
- Ensure you have permission to add resources
- Try refreshing and adding again

---

## FAQs

**Q: How many resources can I add to a task?**  
A: There's no hard limit, but 3-6 resources per task is typically optimal.

**Q: Can customers add resources?**  
A: No, only Sales Engineers and above can add resources to tasks.

**Q: Can I share resources between tasks?**  
A: Currently, resources are task-specific. Use task templates for common resource sets.

**Q: What file types are supported for uploads?**  
A: This depends on your tenant configuration. Common types include PDF, Word, Excel, images.

**Q: Can I add resources to task groups?**  
A: Yes, task groups can have their own resources that apply to all tasks in the group.

**Q: How do I know if a customer has viewed a resource?**  
A: Currently, resource views are not tracked. Monitor customer comments for feedback.

---

**Next Steps:**

- [Track customer engagement with resources →](tracking-progress.md)
- [Learn about the comments system →](../features/comments.md)
- [Explore more about resources →](../features/resources.md)
