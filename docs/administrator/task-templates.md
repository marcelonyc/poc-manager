# Task Templates

As an **Administrator**, you create and manage reusable task and task group templates that standardize POC engagements across your organization.

## Overview

Task templates are reusable task definitions that can be used across multiple POCs. They help ensure consistency and save time when creating new POCs.

### Benefits of Templates

- ✅ Consistency across POCs
- ✅ Faster POC creation
- ✅ Standardized best practices
- ✅ Reusable resources
- ✅ Quality assurance

## Accessing Task Templates

1. Click **Task Templates** in the main navigation
2. You'll see two tabs: **Task Templates** and **Task Group Templates**

## Task Templates Tab

### Viewing Task Templates

The Task Templates section displays:

- Template cards in a grid layout
- Template title
- Description preview
- Created date
- Edit button

### Creating a Task Template

!!! example "Create Task Template Steps"
    1. Click **+ New Task Template** button
    2. Fill in the form:
        - **Task Title** (required): Clear, descriptive name
        - **Description**: Detailed instructions
    3. Click **Create Template**

#### Example Task Templates

```
✅ "Setup Development Environment"
Description: Install required software, configure development tools, 
and verify access to repositories.

✅ "Product Demo Preparation"
Description: Prepare demo environment, test key features, and create 
sample data for demonstration.

✅ "Performance Testing"
Description: Execute performance tests, document results, and compare 
against success criteria.
```

### Editing a Task Template

To modify an existing template:

1. Click **Edit** on the template card
2. A modal opens with:
   - Task details section
   - Resources section
3. Update information as needed
4. Click **Update Template**

### Task Template Details

When editing a template, you can modify:

- **Title**: Task name
- **Description**: Detailed instructions and context

## Adding Resources to Tasks

Resources provide supporting materials for tasks. You can attach multiple resources to each task template.

### Resource Types

POC Manager supports four resource types:

=== "🔗 Link"
    **Use for**: URLs to documentation, tools, or external resources
    
    **Examples**:
    
    - Documentation URLs
    - Tool registration pages
    - Support articles
    - Video tutorials
    
    **Content**: Full URL (https://example.com/docs)

=== "💻 Code"
    **Use for**: Code snippets, scripts, or configuration
    
    **Examples**:
    
    - Installation scripts
    - Configuration files
    - Sample code
    - API examples
    
    **Content**: Code with proper formatting

=== "📝 Text"
    **Use for**: Instructions, notes, or descriptions
    
    **Examples**:
    
    - Step-by-step instructions
    - Important notes
    - Troubleshooting tips
    - Prerequisites list
    
    **Content**: Plain text or formatted text

=== "📁 File"
    **Use for**: File references or paths
    
    **Examples**:
    
    - Document references
    - File paths
    - Template files
    - Configuration files
    
    **Content**: File path or reference

### Adding a Resource

!!! example "Add Resource Steps"
    1. Open the task template for editing
    2. Scroll to the **Resources** section
    3. Click **+ Add Resource**
    4. Fill in the resource form:
        - **Resource Type**: Select from dropdown
        - **Title** (required): Descriptive name
        - **Description**: Optional context
        - **Content** (required): URL, code, text, or file path
    5. Click **Add** to save

### Resource Form Fields

| Field | Required | Description |
|-------|----------|-------------|
| Resource Type | ✅ | LINK, CODE, TEXT, or FILE |
| Title | ✅ | Clear, descriptive name |
| Description | ❌ | Additional context or notes |
| Content | ✅ | The actual resource content |

### Managing Resources

Once added, resources appear in a list showing:

- Resource type (color-coded badge)
- Title
- Description
- Content preview
- Edit and Delete buttons

#### Editing a Resource

1. Click **Edit** on the resource
2. The resource form opens with current data
3. Modify any fields
4. Click **Update**

#### Deleting a Resource

1. Click **Delete** on the resource
2. Confirm the deletion
3. Resource is permanently removed

!!! warning "Deletion is Permanent"
    Deleted resources cannot be recovered. This only affects the template, not POCs that already use this template.

## Task Group Templates Tab

Task groups organize related tasks together for more complex workflows.

### Viewing Task Group Templates

The Task Group Templates section displays:

- Group cards in a grid layout
- Group title
- Description preview
- Created date
- Edit button

### Creating a Task Group Template

!!! example "Create Task Group Steps"
    1. Switch to the **Task Group Templates** tab
    2. Click **+ New Task Group Template** button
    3. Fill in the form:
        - **Group Title** (required): Clear, descriptive name
        - **Description**: Purpose and context
    4. Click **Create Template**

#### Example Task Groups

```
📁 "Initial Setup Phase"
Description: All tasks required to prepare the POC environment, 
including access, tools, and initial configuration.

📁 "Core Feature Validation"
Description: Tasks focused on testing and validating core product 
features against customer requirements.

📁 "Integration Testing"
Description: Tasks for testing integrations with customer systems 
and third-party tools.
```

### Editing Task Group Templates

Similar to task templates:

1. Click **Edit** on the group card
2. Modal opens with editable fields
3. Update title or description
4. Click **Update Template**

!!! info "Task Groups and Tasks"
    Task groups are organizational containers. The actual tasks within 
    a group are managed when creating individual POCs, not in the template.

## Best Practices

### Naming Conventions

**Tasks:**
- Use action verbs: "Setup", "Configure", "Test", "Validate"
- Be specific: "Setup Development Environment" not "Setup"
- Keep titles concise (under 50 characters)

**Task Groups:**
- Use phase or category names: "Initial Setup Phase"
- Indicate scope: "Core Feature Validation"
- Group related tasks logically

### Writing Descriptions

- ✅ Include clear objectives
- ✅ List prerequisites
- ✅ Provide step-by-step instructions
- ✅ Mention expected outcomes
- ✅ Add estimated time if applicable
- ❌ Don't assume prior knowledge
- ❌ Avoid jargon without explanation

### Resource Management

- Add comprehensive resources for each task
- Include multiple resource types for different learning styles
- Keep URLs up to date
- Test links periodically
- Provide code examples for technical tasks

### Organization

- Create templates for common POC scenarios
- Group similar templates together mentally (can't folder yet)
- Review and update templates quarterly
- Remove obsolete templates
- Standardize across the organization

## Common Template Types

### Technical Setup Tasks

- Environment setup
- Software installation
- Access configuration
- Repository setup
- API key generation

### Validation Tasks

- Feature demonstrations
- Performance testing
- Integration testing
- Security validation
- Compliance checks

### Documentation Tasks

- Creating reports
- Documenting findings
- Capturing screenshots
- Recording demos
- Writing summaries

## Troubleshooting

### Template Not Saving

If a template won't save:

- Check all required fields are filled
- Verify title is unique
- Check internet connection
- Review error messages
- Clear browser cache

### Resources Not Displaying

If resources don't show:

- Refresh the page
- Check if resource was actually saved
- Verify you're editing the correct template
- Try adding a new resource

### Cannot Delete Template

You cannot delete templates that are in use by active POCs. Consider:

- Editing instead of deleting
- Creating a new version
- Archiving (future feature)

## Next Steps

After creating templates:

- Share with Sales Engineers
- Document template usage guidelines
- Train team on new templates
- Monitor template effectiveness
- Gather feedback and improve

---

**Related Documentation:**

- [Creating POCs](creating-pocs.md) - Using templates in POCs
- [Resources Feature](../features/resources.md) - Detailed resource guide
- [Managing POCs](managing-pocs.md) - POC lifecycle management
