# Creating POCs

As an **Administrator** or **Sales Engineer**, you can create new POC (Proof of Concept) engagements.

## Overview

A POC represents a structured engagement with a customer to demonstrate your product or solution. Each POC includes objectives, tasks, success criteria, and timelines.

## POC Creation Workflow

```mermaid
graph LR
    A[Create POC] --> B[Add Tasks]
    B --> C[Invite Customer]
    C --> D[Execute & Track]
    D --> E[Complete & Report]
```

## Creating a New POC

### Accessing POC Creation

1. Navigate to **POCs** in the main menu
2. Click **+ New POC** button (top right)

### Basic Information

!!! example "Create POC Steps"
    Fill in the following information:
    
    **Required Fields:**
    
    - **Title**: Clear, descriptive name for the POC
    - **Customer Company Name**: Customer's organization name
    - **Start Date**: When the POC begins
    - **End Date**: Expected completion date
    
    **Optional Fields:**
    
    - **Description**: Overview of the POC
    - **Executive Summary**: High-level summary for stakeholders
    - **Objectives**: What you aim to achieve
    - **Products**: Associated products (if configured)

### Form Guidelines

**Title Examples:**
```
✅ "Acme Corp - Cloud Migration POC"
✅ "TechStart - API Integration Validation"
✅ "GlobalBank - Security Assessment POC"

❌ "POC" (too generic)
❌ "Test123" (not descriptive)
```

**Description Best Practices:**

- Explain the purpose and scope
- Mention key stakeholders
- Note any special requirements
- Include background context

**Setting Dates:**

- Start date should be realistic
- Allow adequate time for completion
- Consider customer availability
- Include buffer time for issues

### Creating the POC

1. Fill in all required fields
2. Add optional information as needed
3. Click **Create POC**
4. You'll be redirected to the POC detail page

## After Creation

Once created, you can:

1. **Add Tasks**: From templates or create custom tasks
2. **Add Task Groups**: Organize tasks into groups
3. **Define Success Criteria**: Set measurable goals
4. **Add Resources**: Attach documentation and materials
5. **Invite Customer**: Give customer access to view progress

## Adding Tasks

### From Templates

If your organization uses task templates:

1. In the POC detail page, find the **Tasks** section
2. Click **Add Task from Template**
3. Select a template from the list
4. Task is automatically added with template content

### Custom Tasks

To create a custom task:

1. Click **Add Custom Task**
2. Fill in:
   - **Title** (required)
   - **Description**
   - **Status** (Not Started, In Progress, Completed, Blocked)
3. Click **Add Task**

### Task Management

Each task includes:

- Title and description
- Status indicator
- Assignment capability
- Progress tracking
- Comment section

## Adding Task Groups

Task groups help organize related tasks:

1. Navigate to **Task Groups** section
2. Click **Add Task Group**
3. Choose from template or create custom
4. Fill in group details
5. Add individual tasks to the group

## Defining Success Criteria

Success criteria are measurable outcomes that determine POC success:

1. Go to **Success Criteria** section
2. Click **Add Success Criterion**
3. Define:
   - **Criterion**: What will be measured
   - **Target**: Expected outcome
   - **Status**: Met/Not Met/In Progress
4. Save the criterion

### Example Success Criteria

```
📊 "API response time under 100ms"
📊 "Successfully process 10,000 transactions per second"
📊 "Integration completed with existing CRM system"
📊 "Zero security vulnerabilities in audit"
📊 "User satisfaction score above 8/10"
```

## POC Configuration

### Visibility Settings

Control who can see the POC:

- **Internal Only**: Only your team can view
- **Customer Access**: Customer can view when invited

### Notification Settings

Configure notifications for:

- Task completion
- Status changes
- New comments
- Milestone achievements

## Best Practices

### Planning

- ✅ Define clear objectives upfront
- ✅ Set realistic timelines
- ✅ Align with customer expectations
- ✅ Plan for contingencies

### Task Organization

- Group related tasks together
- Create dependencies where needed
- Assign clear owners
- Set priorities

### Communication

- Keep descriptions clear and concise
- Update status regularly
- Document decisions and changes
- Maintain comment history

## Common POC Types

### Technical Integration

- API integration tasks
- Data migration
- System compatibility testing
- Performance validation

### Product Evaluation

- Feature demonstrations
- Use case validation
- User acceptance testing
- Competitive comparison

### Security Assessment

- Security scanning
- Compliance validation
- Penetration testing
- Access control review

## Troubleshooting

### POC Not Creating

If POC creation fails:

- Check all required fields
- Verify date ranges are valid
- Ensure start date is before end date
- Check internet connection

### Cannot Add Tasks

If you can't add tasks:

- Verify POC was created successfully
- Check you have proper permissions
- Refresh the page
- Try creating a simpler task first

## Next Steps

After creating a POC:

1. [Add resources](../sales-engineer/adding-resources.md) to tasks
2. [Invite the customer](../sales-engineer/inviting-customers.md)
3. Begin [managing tasks](../sales-engineer/managing-tasks.md)
4. [Track progress](../sales-engineer/tracking-progress.md)

---

**Related Documentation:**

- [Managing POCs](managing-pocs.md) - Ongoing POC management
- [Task Templates](task-templates.md) - Creating reusable templates
- [POC Overview](../sales-engineer/poc-overview.md) - Sales engineer perspective
