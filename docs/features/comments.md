# Comments System

The comments system enables effective collaboration between team members and customers throughout the POC lifecycle. This guide explains how comments work and how to use them effectively.

## Overview

Comments provide:

- **Communication channel** for discussions
- **Feedback mechanism** for reviews
- **Q&A platform** for questions
- **Documentation** of decisions
- **Audit trail** of conversations

## Comment Types

### External Comments

**Visible to:** All POC participants (team and customers)

**Purpose:**
- Customer-facing communication
- Questions and answers
- Feedback and updates
- Status communication
- Professional discussions

**Example:**
```
Sarah Engineer (2 hours ago):
I've updated the authentication module based on your feedback.
The new implementation supports both OAuth and SAML. Please
review and let me know if this meets your requirements.
```

### Internal Comments

**Visible to:** Internal team members only (not customers)

**Purpose:**
- Team coordination
- Internal notes
- Planning discussions
- Issue tracking
- Private observations

**Example (with 🔒 lock icon):**
```
🔒 Mike Sales (1 hour ago - Internal):
Customer seems concerned about pricing. Need to schedule call
with account manager before next review. Also, they mentioned
competitor XYZ - need to emphasize our differentiators.
```

## Adding Comments

### Basic Comment

1. Navigate to the task or POC
2. Scroll to the **Comments** section
3. Type your comment in the text box
4. Select comment type:
   - **External** (default for customer communication)
   - **Internal** (team-only notes)
5. Click **Post Comment**

### Comment with Formatting

Use markdown for rich text:

```markdown
**Bold text** for emphasis
*Italic text* for subtle emphasis
`Code snippets` for technical terms
- Bullet points for lists
1. Numbered lists for steps
[Links](https://example.com) for references

Example:
To reproduce the issue:
1. Navigate to **Settings** > **API Keys**
2. Click `Generate New Key`
3. Copy the key and test with this code:
   `curl -H "Authorization: Bearer YOUR_KEY" https://api.example.com`
```

### Comment with Mentions

Mention users to notify them (if supported):

```
@JohnDoe Can you review the security implications of this
approach? I want to make sure we're following your team's
security policy.
```

### Comment with Subject

Add a subject line for clarity:

```
Subject: Question about Rate Limiting

I noticed the API has a 1000 requests/hour limit. For our
production use case, we expect about 2000 requests/hour.
Can we discuss options for higher limits?
```

## Comment Features

### Subjects

**What they are:**
Optional subject lines that provide context for comments.

**When to use:**
- Starting new discussion topics
- Raising specific issues
- Asking distinct questions
- Categorizing feedback

**Example:**
```
Subject: Performance Testing Results

I completed the load testing with 1000 concurrent users.
Results show:
- Average response time: 145ms
- 99th percentile: 320ms
- Error rate: 0.02%

All metrics are within acceptable ranges. Ready to proceed
to the next phase.
```

### Threading

Comments are organized by task:

```
Task 5: API Integration
├─ Comment 1 (External): Initial question
├─ Comment 2 (External): Response from team
├─ Comment 3 (Internal 🔒): Team note
├─ Comment 4 (External): Customer follow-up
└─ Comment 5 (External): Final resolution
```

### Timestamps

All comments show:
- Date and time posted
- Relative time (e.g., "2 hours ago")
- Author name and role
- Comment type (internal/external)

### Edit and Delete

**Editing comments:**
- Click edit icon (✏️) on your comments
- Make changes
- Save (edit history may be tracked)

**Deleting comments:**
- Click delete icon (🗑️) on your comments
- Confirm deletion
- Deleted comments cannot be recovered

!!! warning "Edit with Care"
    Editing comments that others have replied to can cause confusion.
    Consider adding a new comment instead for clarifications.

## Comment Etiquette

### Professional Tone

✅ **Do:**
```
Thank you for the quick response! I tested the updated feature
and it works perfectly. I appreciate how you addressed all
three concerns I raised. Looking forward to moving to the next
phase.
```

❌ **Don't:**
```
Finally! About time. Still not perfect but I guess it'll work.
```

### Clarity and Specificity

✅ **Do:**
```
I found a bug in the export feature:

Steps to reproduce:
1. Navigate to Reports > Export
2. Select "Last 30 days"
3. Choose CSV format
4. Click Export

Expected: File downloads
Actual: Error message "Export failed"
Browser: Chrome 120 on Windows 11
```

❌ **Don't:**
```
Export doesn't work.
```

### Constructive Feedback

✅ **Do:**
```
The dashboard layout is good, but our team finds it challenging
to locate the export button. Would it be possible to move it
to the top right corner near the other action buttons? This
would align with our team's workflow expectations.
```

❌ **Don't:**
```
Terrible UI. No one can find anything.
```

## Use Cases

### Asking Questions

**Template:**
```
Subject: Question about [Topic]

[Context about what you're trying to do]

Question: [Your specific question]

[Any additional relevant information]

Example:

Subject: Question about API Authentication

I'm trying to integrate the API with our existing system.

Question: Does the API support API key authentication, or is
OAuth required? Our system currently uses API keys for all
integrations.

We're flexible and can implement OAuth if needed, but wanted
to check if there's a simpler option first.
```

### Reporting Issues

**Template:**
```
Subject: Issue with [Feature]

Description: [What's wrong]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Behavior: [What should happen]
Actual Behavior: [What actually happens]

Environment:
- Browser: [Browser and version]
- OS: [Operating system]
- User role: [Your role]

Additional Notes: [Any other relevant information]
```

### Providing Updates

**Template:**
```
Subject: Update on [Task/Topic]

Status: [Current status]

Progress:
- [Completed item 1]
- [Completed item 2]
- [In progress item]

Next Steps:
- [What's coming next]

ETA: [Expected completion date]

Questions/Blockers: [Any issues or questions]
```

### Requesting Reviews

**Template:**
```
Subject: Review Request: [What to review]

I've completed [task/deliverable] and it's ready for your review.

What to review:
- [Item 1]
- [Item 2]
- [Item 3]

Specific questions:
1. [Question 1]
2. [Question 2]

Timeline: Please review by [date] if possible.

Thank you!
```

### Confirming Completion

**Template:**
```
Subject: [Task] Completed

I've completed [task name] and verified:
✓ [Requirement 1 met]
✓ [Requirement 2 met]
✓ [Requirement 3 met]

Testing:
- [Test 1]: Passed
- [Test 2]: Passed
- [Test 3]: Passed

Ready to proceed to [next step].

Thanks for the support on this!
```

## Comment Management

### Finding Comments

**Search comments:**
1. Use search box at top of comments
2. Enter keywords
3. Results highlight matching comments
4. Filter by author, date, or type

**Filter comments:**
- Show only external
- Show only internal
- Show only my comments
- Show only unread
- Show comments with subjects

### Following Conversations

**Track important discussions:**
1. Click "Follow" on a task
2. Receive notifications for new comments
3. Comments appear in your activity feed
4. Unfollow when no longer needed

### Marking as Read

Comments you haven't seen are highlighted:

```
┌─────────────────────────────────────────┐
│ 🔵 New Comment                          │
│ Jane Smith • 10 minutes ago             │
│ I've answered your question about...   │
└─────────────────────────────────────────┘

[Mark All as Read]
```

## Notifications

### Comment Notifications

Get notified when:
- Someone comments on your POC
- Someone replies to your comment
- Someone mentions you
- Someone comments on a followed task
- Customer adds a comment (for team members)
- Team responds (for customers)

### Notification Settings

Configure comment notifications:

1. **Frequency:**
   - Real-time: Immediate notifications
   - Daily digest: One email per day
   - Weekly summary: One email per week

2. **Channels:**
   - In-app notifications
   - Email notifications
   - Both

3. **Filters:**
   - All comments
   - Only mentions
   - Only customer comments
   - Only certain POCs

## Best Practices

### For Sales Engineers

✅ **Do:**
- Respond to customer questions within 24 hours
- Use external comments for customer communication
- Use internal comments for team coordination
- Add context to your responses
- Acknowledge customer feedback
- Thank customers for their input
- Proactively provide updates

❌ **Don't:**
- Leave customer questions unanswered
- Put sensitive information in external comments
- Use internal comments for customer-facing info
- Write overly technical external comments
- Ignore negative feedback
- Make promises you can't keep

### For Customers

✅ **Do:**
- Ask questions when unclear
- Provide detailed feedback
- Report issues promptly
- Acknowledge responses
- Be specific and constructive
- Include relevant context
- Follow up on unresolved items

❌ **Don't:**
- Wait too long to respond
- Provide vague feedback
- Ignore questions directed at you
- Be overly negative or aggressive
- Assume team knows unstated requirements
- Forget to thank helpful responses

### For Teams

✅ **Do:**
- Use internal comments for coordination
- Keep customers informed
- Document decisions
- Track action items
- Maintain professional tone
- Respond promptly
- Close the loop on discussions

❌ **Don't:**
- Discuss customers negatively in internal comments
- Leave internal comments accidentally visible
- Let discussions go unresolved
- Forget to follow up on action items
- Use comments as the only communication channel

## Advanced Features

### Comment Templates

Create templates for common responses:

**Setup:**
1. Go to Settings > Comment Templates
2. Create new template
3. Add title and content
4. Save template

**Usage:**
1. Click "Insert Template"
2. Select template
3. Customize as needed
4. Post comment

### Bulk Actions

Manage multiple comments:

1. Select comments (checkboxes)
2. Choose action:
   - Mark as read
   - Delete
   - Change type (internal/external)
3. Confirm action

### Export Comments

Export comment history:

1. Go to POC or task
2. Click "Export Comments"
3. Choose format (PDF, CSV, Markdown)
4. Download file

Use cases:
- Audit trail
- Customer records
- Compliance documentation
- Project retrospectives

## Integration

### Email Integration

Comments can trigger emails:

**For customers:**
- New external comments
- Responses to their comments
- Important updates

**For team:**
- Customer comments
- Urgent issues
- Mentions

### Slack Integration

If configured by Tenant Admin:
- Comments posted to Slack channels
- Slack messages create comments
- Real-time synchronization

### API Access

Programmatic comment access:
- Create comments via API
- Retrieve comment history
- Update or delete comments
- Search comments

## Troubleshooting

### Comment Not Posting

- Check internet connection
- Verify comment isn't empty
- Ensure you have permission
- Try refreshing page
- Clear browser cache

### Can't See Internal Comments

- Verify you're logged in
- Check your role (customers can't see internal)
- Refresh the page
- Verify comment wasn't deleted

### Notifications Not Working

- Check notification settings
- Verify email address
- Check spam folder
- Ensure notifications are enabled
- Contact support

---

## FAQs

**Q: Can I edit comments after posting?**  
A: Yes, you can edit your own comments. Click the edit icon next to your comment.

**Q: Can I delete someone else's comment?**  
A: Only admins can delete other users' comments. Regular users can only delete their own.

**Q: What happens to comments when a POC is completed?**  
A: Comments are preserved for reference and can be included in final documentation.

**Q: Can customers see internal comments?**  
A: No, internal comments are only visible to your team members.

**Q: How do I know if someone replied to my comment?**  
A: You'll receive a notification based on your notification settings.

**Q: Can I attach files to comments?**  
A: File attachments depend on configuration. Use resources feature for sharing files.

**Q: Is there a character limit for comments?**  
A: Comments can typically be several thousand characters. For longer content, consider creating a resource.

---

**Related Documentation:**

- [Providing feedback as a customer →](../customer/providing-feedback.md)
- [Managing tasks as Sales Engineer →](../sales-engineer/managing-tasks.md)
- [Dashboard features →](dashboard.md)
- [Resources system →](resources.md)
