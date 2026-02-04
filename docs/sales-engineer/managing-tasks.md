# Managing Tasks

Tasks are the building blocks of your POC. This guide covers everything you need to know about creating, organizing, and managing tasks effectively.

## Understanding Tasks

### What is a Task?

A task represents a specific activity or deliverable in your POC:

- A technical evaluation
- A feature demonstration
- A documentation review
- A test scenario
- A training session
- A milestone checkpoint

### Task Properties

Each task has:

- **Name**: Clear, concise title
- **Description**: Detailed explanation
- **Status**: Current state (Not Started, In Progress, Completed, Blocked)
- **Assignee**: Who is responsible (you or customer)
- **Due Date**: Target completion date (optional)
- **Resources**: Attached documentation, links, files
- **Comments**: Internal and external discussions
- **Success Criteria**: Link to overall POC goals

## Creating Tasks

### From Scratch

1. Navigate to your POC
2. Click **Add Task**
3. Fill in task details:
   ```
   Name: "Setup Development Environment"
   Description: "Install and configure the development tools needed for the POC"
   Status: Not Started
   Assignee: Customer
   Due Date: [Select date]
   ```
4. Click **Save**

### From Templates

If your Administrator has created task templates:

1. Click **Add from Template**
2. Browse or search for relevant templates
3. Select the template to add
4. Customize the task as needed
5. Click **Save**

!!! tip "Task Templates"
    Task templates save time by providing pre-configured tasks with resources already attached.

## Task Status

### Status Types

| Status | Meaning | When to Use |
|--------|---------|-------------|
| **Not Started** | Task hasn't begun | Initial state for new tasks |
| **In Progress** | Work is underway | Someone is actively working on it |
| **Completed** | Task is finished | All requirements met |
| **Blocked** | Cannot proceed | Waiting on dependency or resolution |

### Updating Status

1. Click on the task
2. Select new status from dropdown
3. Add a comment explaining the change (optional but recommended)
4. Click **Update**

!!! example "Status Change with Comment"
    ```
    Status: In Progress → Blocked
    Comment: "Waiting for API credentials from customer"
    ```

## Organizing Tasks

### Task Groups

Group related tasks together for better organization:

1. Click **Create Task Group**
2. Name the group (e.g., "Phase 1: Setup", "Technical Evaluation")
3. Drag and drop tasks into the group
4. Collapse/expand groups as needed

### Task Order

Arrange tasks in logical order:

- Sequential tasks (one after another)
- Parallel tasks (can be done simultaneously)
- Milestone markers
- Phase groupings

### Using Templates Groups

Task group templates provide pre-structured sets of tasks:

1. Click **Add Task Group from Template**
2. Select a template (e.g., "API Integration", "Security Review")
3. All tasks in the group are added at once
4. Customize as needed

## Adding Resources to Tasks

Resources provide context and documentation for tasks.

### Resource Types

- **Links**: URLs to documentation, tools, or resources
- **Code Snippets**: Sample code or configurations
- **Text Notes**: Instructions or explanations
- **Files**: Uploaded documents (if enabled)

### Adding a Resource

1. Open the task
2. Click **Add Resource**
3. Select resource type
4. Fill in details:
   ```
   Type: Link
   Title: "API Documentation"
   URL: https://docs.example.com/api
   Description: "Reference guide for API integration"
   ```
5. Click **Save**

[Learn more about adding resources →](adding-resources.md)

## Task Assignment

### Assigning to Yourself

Use when:
- You need to complete the task
- You're demonstrating a feature
- You're preparing materials

### Assigning to Customer

Use when:
- Customer needs to review something
- Customer needs to provide information
- Customer needs to test functionality
- Customer needs to complete an action

!!! note "Customer Visibility"
    Tasks assigned to customers are highlighted for them in their view.

## Task Comments

### Internal Comments

For team communication:

- Not visible to customers
- Use for notes, questions, coordination
- Tagged with 🔒 lock icon

### External Comments

For customer communication:

- Visible to customers
- Use for updates, questions, feedback
- Professional and clear

### Adding Comments

1. Open the task
2. Type your comment
3. Select **Internal** or **External**
4. Click **Post**

!!! tip "Comment Best Practices"
    - Keep external comments professional
    - Use internal comments for team coordination
    - Reference specific points in task description
    - Tag progress updates in comments

## Tracking Task Progress

### Individual Task View

Monitor each task:
- Current status
- Comments and activity
- Resources attached
- Time to completion

### POC-Level View

See all tasks:
- Tasks by status (Kanban view)
- Tasks by assignee
- Overdue tasks
- Completion percentage

### Dashboard Metrics

Track overall progress:
- Total tasks vs completed tasks
- Tasks by status breakdown
- Average completion time
- Blocked tasks requiring attention

[Learn more about tracking →](tracking-progress.md)

## Task Dependencies

While not explicitly modeled, you can manage dependencies:

### Documenting Dependencies

In task descriptions, note:
```
Prerequisites:
- Task #3 must be completed first
- Requires API credentials from customer

Dependencies:
- This task blocks Task #7 and #8
```

### Managing Blocked Tasks

When a task is blocked:

1. Change status to **Blocked**
2. Add comment explaining the blocker
3. Note which task or resource is needed
4. Follow up regularly on resolution

## Bulk Operations

### Moving Multiple Tasks

1. Select multiple tasks (checkbox)
2. Choose action:
   - Move to different group
   - Change status
   - Assign to different person
3. Confirm changes

### Task Templates for Bulk Adding

Use task group templates to add multiple tasks at once.

## Best Practices

### Task Creation

✅ **Do:**
- Write clear, action-oriented task names
- Include detailed descriptions
- Add relevant resources upfront
- Set realistic due dates
- Break large tasks into smaller ones

❌ **Don't:**
- Create vague or ambiguous tasks
- Overload tasks with too many objectives
- Forget to add necessary resources
- Set unrealistic timelines

### Task Management

✅ **Do:**
- Update status promptly
- Add comments when changing status
- Review tasks regularly
- Respond to customer questions quickly
- Keep resources up-to-date

❌ **Don't:**
- Leave tasks stale without updates
- Ignore blocked tasks
- Forget to communicate changes
- Neglect customer feedback

### Task Organization

✅ **Do:**
- Group related tasks
- Order tasks logically
- Use consistent naming conventions
- Create clear task groups
- Balance task granularity

❌ **Don't:**
- Create too many small tasks
- Mix unrelated tasks in groups
- Use confusing names
- Duplicate tasks unnecessarily

## Common Scenarios

### Setup Phase

```
Task Group: "Environment Setup"
├── Task 1: Review Prerequisites
├── Task 2: Install Required Software
├── Task 3: Configure Development Environment
└── Task 4: Verify Setup
```

### Evaluation Phase

```
Task Group: "Feature Evaluation"
├── Task 1: Demo Core Features
├── Task 2: Test Integration Points
├── Task 3: Review Security Controls
└── Task 4: Assess Performance
```

### Completion Phase

```
Task Group: "Wrap-up"
├── Task 1: Review Success Criteria
├── Task 2: Gather Customer Feedback
├── Task 3: Generate Final Report
└── Task 4: Schedule Follow-up
```

## Troubleshooting

### Task Not Saving

- Check required fields are filled
- Verify you have permission to edit
- Refresh page and try again
- Contact support if issue persists

### Can't Change Status

- Ensure you have necessary permissions
- Check if task is locked
- Verify POC is still active

### Resources Not Showing

- Check resource was saved correctly
- Verify permissions on shared resources
- Refresh the page

---

## FAQs

**Q: How many tasks should a POC have?**  
A: It depends on complexity, but typically 10-30 tasks is manageable.

**Q: Can customers create tasks?**  
A: No, only Sales Engineers and above can create tasks.

**Q: Can I reorder tasks after creating them?**  
A: Yes, you can drag and drop tasks to reorder them.

**Q: What happens to completed tasks?**  
A: They remain visible but are typically collapsed or filtered in views.

**Q: Can I delete tasks?**  
A: Yes, but deleted tasks cannot be recovered. Consider marking them as "Not Applicable" instead.

---

**Next Steps:**

- [Add resources to tasks →](adding-resources.md)
- [Track POC progress →](tracking-progress.md)
- [Learn about comments →](../features/comments.md)
