# Providing Feedback

Your feedback is essential to the success of the POC. This guide shows you how to effectively communicate with the team and provide valuable input.

## Why Your Feedback Matters

Your perspective helps:

- Ensure the solution meets your needs
- Identify potential issues early
- Guide the POC direction
- Build a successful implementation
- Make informed decisions

## The Comments System

### Types of Comments

**External Comments** (What you see and can add):
- Visible to all POC participants
- Used for questions, feedback, and discussions
- Professional communication channel

**Internal Comments** (Hidden from you):
- Team coordination and notes
- Not visible to customers
- Used for internal planning

[Learn more about comments →](../features/comments.md)

## Adding Comments

### On Tasks

1. Open a task
2. Scroll to the **Comments** section
3. Type your comment in the text box
4. Click **Post Comment**

### Comment Structure

```
┌─────────────────────────────────────────────────────────┐
│ Comments                                                 │
├─────────────────────────────────────────────────────────┤
│ John Doe (you) • 2 hours ago                            │
│ This looks great! I tested the authentication and it    │
│ works perfectly. One question: how do we handle timeout │
│ scenarios?                                               │
│                                                          │
│ Sarah Engineer • 1 hour ago                              │
│ Great question! I've added a resource with timeout      │
│ handling examples. Let me know if that helps.           │
│                                                          │
│ [Your comment here...]                         [Post]   │
└─────────────────────────────────────────────────────────┘
```

## Types of Feedback

### ✅ Positive Feedback

**When to give:**
- Something works well
- Requirements are met
- Documentation is clear
- Process is smooth

**Example:**
```
The API integration works exactly as expected. The documentation
was clear and easy to follow. We were able to get it working
in under an hour. Excellent job!
```

### ❓ Questions

**When to ask:**
- Something is unclear
- Need more information
- Want to understand better
- Need clarification

**Example:**
```
I see the performance metrics in the dashboard, but I'm not sure
how to interpret the "throughput" value. Is this requests per
second? Can you explain what the threshold should be?
```

### ⚠️ Concerns or Issues

**When to raise:**
- Something doesn't work
- Performance issues
- Security concerns
- Missing features

**Example:**
```
I'm encountering an error when trying to upload files larger than
10MB. The system times out after 30 seconds. Is this a known
limitation? Our typical files are 15-20MB.
```

### 💡 Suggestions

**When to suggest:**
- Improvements you'd like to see
- Alternative approaches
- Additional features
- Process improvements

**Example:**
```
Would it be possible to add a bulk import feature? We have about
5,000 records to migrate, and doing them one at a time would be
time-consuming. A CSV import would be very helpful.
```

### 📊 Status Updates

**When to update:**
- You've completed a review
- Testing is done
- You're blocked on something
- Timeline has changed

**Example:**
```
I've completed the security review with our team. Everything looks
good from our perspective. We're ready to move forward to the next
phase.
```

## Effective Feedback Guidelines

### Be Specific

✅ **Good:**
```
The search feature works well, but it doesn't find results when I
search for "user-123". It works fine with "user 123" (with a space).
Can the search handle dashes?
```

❌ **Vague:**
```
The search doesn't work right.
```

### Be Timely

✅ **Good:**
- Provide feedback within 24-48 hours
- Respond to questions promptly
- Report issues as soon as you find them

❌ **Poor:**
- Wait until the end of the POC to share concerns
- Let questions go unanswered
- Delay important feedback

### Be Constructive

✅ **Good:**
```
The dashboard layout is a bit confusing for our team. Would it be
possible to rearrange the widgets so the most important metrics
(sales and inventory) are at the top? This would match our current
workflow better.
```

❌ **Not Helpful:**
```
The dashboard is terrible.
```

### Be Complete

✅ **Good:**
```
Error Details:
- What: Authentication fails
- When: After password reset
- Steps to reproduce:
  1. Request password reset
  2. Click link in email
  3. Enter new password
  4. Try to log in
- Expected: Should log in successfully
- Actual: Shows "Invalid credentials" error
- Browser: Chrome 120 on Windows
```

❌ **Incomplete:**
```
Login doesn't work after password reset.
```

## Comment Best Practices

### Do's ✅

- **Read before commenting**: Review existing comments to avoid duplication
- **Stay on topic**: Keep comments relevant to the task
- **Be professional**: Maintain business-appropriate tone
- **Provide context**: Include relevant details
- **Use formatting**: Break up long comments into paragraphs
- **Tag people if needed**: @mention relevant people (if supported)
- **Follow up**: Respond to questions directed at you
- **Acknowledge responses**: Thank people for helpful answers

### Don'ts ❌

- **Don't be vague**: Avoid unclear or ambiguous feedback
- **Don't delay**: Don't wait to report important issues
- **Don't be dismissive**: Value the team's effort
- **Don't overload**: Don't put multiple unrelated topics in one comment
- **Don't use ALL CAPS**: It comes across as shouting
- **Don't be negative**: Focus on solutions, not just problems
- **Don't ignore questions**: Respond to questions directed at you

## Responding to Questions

### When the Team Asks Questions

The POC team may ask you:

- For clarification on requirements
- To test specific features
- To provide information or access
- For feedback on implementation
- To review documentation

### Response Template

```
Question: [Restate the question]

Answer: [Your response]

Additional Context: [Any relevant details]

Next Steps: [What you'll do or need]
```

### Example Response

```
Question: Can you test the file upload with your typical file sizes?

Answer: Yes, I tested with our standard files (15-20MB PDFs). The
upload works but takes about 45 seconds per file.

Additional Context: We typically upload 50-100 files per day, so
upload time is important for our workflow.

Next Steps: Let me know if you need me to test with different file
types or if you need examples of our files for testing.
```

## Providing Technical Feedback

### Testing Results

When providing test results:

```
Test: [What you tested]
Environment: [Your setup]
Result: [Pass/Fail]
Details: [What happened]

Example:

Test: Single sign-on integration with Azure AD
Environment: Windows 11, Chrome 120, Azure AD tenant
Result: Pass
Details: Login works smoothly. Redirects correctly after authentication.
Average login time: 3 seconds. Tested with 5 different users.
```

### Bug Reports

When reporting bugs:

```
Summary: [Brief description]
Steps to Reproduce:
1. [Step one]
2. [Step two]
3. [Step three]

Expected Result: [What should happen]
Actual Result: [What actually happens]
Frequency: [Always / Sometimes / Rare]
Impact: [High / Medium / Low]
Screenshot: [If applicable]

Example:

Summary: Dashboard doesn't load on mobile
Steps to Reproduce:
1. Open POC Manager on iPhone 13
2. Navigate to Dashboard
3. Observe loading spinner

Expected Result: Dashboard should display widgets
Actual Result: Spinner continues indefinitely
Frequency: Always on mobile, never on desktop
Impact: High (can't use POC on mobile)
Screenshot: [Attached]
```

### Performance Feedback

When discussing performance:

```
Metric: [What you're measuring]
Your Experience: [Actual numbers]
Your Requirement: [What you need]
Impact: [Why it matters]

Example:

Metric: Report generation time
Your Experience: 2-3 minutes for standard monthly report
Your Requirement: Under 30 seconds preferred, 1 minute acceptable
Impact: Reports are run multiple times per day by 10 users
```

## Subject-Specific Comments

### On Documents

When commenting on documentation:

```
Section: [Which section]
Feedback: [Your input]
Suggestion: [Proposed improvement]

Example:

Section: "Installation Guide - Step 3"
Feedback: This step assumes Node.js is already installed, but that
wasn't mentioned in the prerequisites.
Suggestion: Add Node.js to the prerequisites list or include
installation instructions.
```

### On Code Examples

When reviewing code:

```
Language: [Programming language]
Location: [Which example]
Issue/Question: [Your concern]

Example:

Language: Python
Location: Authentication example in Task 3
Question: This example uses hardcoded credentials. Can you add an
example showing how to use environment variables instead? That's
our team's preferred approach.
```

## Tracking Your Feedback

### Following Up

Track your comments:

- **Open Issues**: Comments waiting for response
- **Resolved**: Issues that have been addressed
- **Pending**: Items you need to test/verify

### Example Tracking

```
My Open Feedback:
1. File upload size question (Task 4) - Awaiting response
2. Dashboard layout suggestion (Task 7) - In discussion
3. Mobile bug report (Task 2) - Being investigated

Resolved:
✓ Login timeout issue - Fixed and verified
✓ API documentation request - New doc added
✓ Export feature question - Answered
```

## Collaboration Etiquette

### Response Times

Aim to respond:

- **Urgent questions**: Within 4 hours
- **General questions**: Within 24 hours
- **Feedback requests**: Within 48 hours
- **Non-urgent items**: Within 3-5 days

### Professional Tone

Maintain professionalism:

```
✅ Good:
"I appreciate the quick response. The new documentation helps, but
I still have a question about the error handling section. Could you
provide an example of how to handle timeouts?"

❌ Less Professional:
"Thanks but still confused. More examples needed."
```

## Getting the Most Value

### Engage Throughout

Don't wait until the end:

- **Week 1**: Provide initial feedback on setup and documentation
- **Week 2**: Share testing results and technical feedback
- **Week 3**: Discuss integration and performance
- **Week 4**: Provide final assessment and recommendations

### Be Honest

The team needs honest feedback:

- Share concerns early
- Don't hide problems to be polite
- Be direct but respectful
- Focus on finding solutions

### Think Long-Term

Consider beyond the POC:

- How will this scale in production?
- What about ongoing maintenance?
- Training needs for your team?
- Integration with existing systems?

---

## FAQs

**Q: How quickly will the team respond to my comments?**  
A: Most comments receive a response within 24 hours during business days.

**Q: Can I edit my comments after posting?**  
A: This depends on your tenant's configuration. Generally, recent comments can be edited.

**Q: Should I comment on every task?**  
A: Comment when you have feedback, questions, or have completed a review. Not every task needs a comment.

**Q: What if I disagree with the team's approach?**  
A: Express your concerns professionally in a comment and suggest alternatives. Discuss to find the best solution.

**Q: Can I attach files to comments?**  
A: This depends on configuration. If file attachments aren't available, you can describe issues in detail or ask the team for an alternative way to share files.

**Q: Who sees my comments?**  
A: All POC participants see external comments. Internal team comments are not visible to customers.

---

**Next Steps:**

- [Learn about task completion →](task-completion.md)
- [Explore the comments system →](../features/comments.md)
- [View your POCs effectively →](viewing-pocs.md)
