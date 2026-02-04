# Inviting Customers

One of the most important steps in managing a POC is inviting your customers to participate. This guide covers everything you need to know about customer invitations.

## Understanding Customer Invitations

Customer invitations allow you to:

- Grant external users access to specific POCs
- Control what customers can see and do
- Enable customer feedback and collaboration
- Track customer engagement

## How to Invite a Customer

### Step 1: Navigate to Your POC

1. Go to the **POCs** page
2. Click on the POC you want to invite customers to
3. Click the **Invite Customer** button

### Step 2: Enter Customer Details

Fill in the invitation form:

- **Email Address**: Customer's business email (required)
- **First Name**: Customer's first name (optional)
- **Last Name**: Customer's last name (optional)
- **Role/Title**: Customer's role in their organization (optional)
- **Personal Message**: Custom message included in the invitation email

!!! example "Sample Invitation Message"
    ```
    Hi John,
    
    I'm excited to invite you to participate in our POC for the XYZ project.
    You'll be able to review our progress, provide feedback, and track
    completion of all tasks.
    
    Looking forward to working with you!
    
    Best regards,
    Sarah
    ```

### Step 3: Send the Invitation

1. Review the invitation details
2. Click **Send Invitation**
3. The system will send an email to the customer

## What Customers Receive

When you send an invitation, the customer receives an email containing:

1. **Welcome Message**: Introduction to the POC
2. **POC Details**: Basic information about the POC
3. **Your Personal Message**: The custom message you included
4. **Access Link**: Unique link to access the POC
5. **Instructions**: How to get started

### Sample Email Format

```
Subject: You've been invited to participate in [POC Name]

Hello [Customer Name],

You've been invited to participate in a Proof of Concept engagement.

POC: [POC Name]
Invited by: [Your Name]
Organization: [Your Tenant Name]

[Your Personal Message]

To get started, click the link below:
[Access Link]

If you don't have an account, you'll be prompted to create one.

Best regards,
The POC Manager Team
```

## Customer Onboarding

### First-Time Users

If the customer doesn't have an account:

1. They click the invitation link
2. They're prompted to create a password
3. They complete their profile
4. They're automatically logged in and taken to the POC

### Existing Users

If the customer already has an account:

1. They click the invitation link
2. They're logged in automatically (or prompted to log in)
3. The POC is added to their accessible POCs
4. They're taken directly to the POC

## Managing Invitations

### Viewing Sent Invitations

To see all invitations for a POC:

1. Navigate to your POC
2. Click on the **Participants** or **Invitations** tab
3. View the list of sent invitations with their status

### Invitation Status

| Status | Description | Action |
|--------|-------------|--------|
| **Pending** | Invitation sent, not yet accepted | Can resend or cancel |
| **Accepted** | Customer has accessed the POC | Active participant |
| **Expired** | Invitation link expired | Resend invitation |
| **Cancelled** | Invitation was cancelled | Can create new invitation |

### Resending Invitations

If a customer didn't receive the invitation:

1. Go to the invitations list
2. Find the pending invitation
3. Click **Resend Invitation**
4. A new email will be sent with a fresh link

### Cancelling Invitations

To cancel a pending invitation:

1. Go to the invitations list
2. Find the invitation to cancel
3. Click **Cancel Invitation**
4. The invitation link will be invalidated

## Best Practices

### Before Sending Invitations

✅ **Do:**
- Ensure the POC is properly set up with tasks and resources
- Add a welcoming personal message
- Verify the customer's email address
- Set clear expectations for participation

❌ **Don't:**
- Invite customers before the POC is ready
- Use generic invitation messages
- Forget to introduce the POC objectives

### Timing

- **Early Engagement**: Invite customers early for collaborative planning
- **Structured Approach**: Invite after initial setup for more guided experience
- **Milestone-Based**: Invite at specific milestones for phased engagement

### Communication

- Include clear instructions in your message
- Mention the expected time commitment
- Provide contact information for questions
- Set expectations for response times

### Follow-Up

- Check if customers have accepted invitations
- Send reminder emails for pending invitations
- Reach out via other channels if needed
- Provide support during onboarding

## Multiple Customers

You can invite multiple customers to the same POC:

1. Send individual invitations to each customer
2. Each customer gets their own access link
3. All customers can see the same POC content
4. Customer comments are visible to all participants

!!! tip "Team Invitations"
    For large customer teams, consider inviting key stakeholders first,
    then adding additional team members as needed.

## Security Considerations

### Email Verification

- Customers must verify their email address
- Invitation links are unique and single-use
- Links expire after a set period (typically 7 days)

### Access Control

- Customers can only access POCs they're invited to
- They cannot see other POCs in your tenant
- They have read-only access to POC structure
- They can add comments and mark tasks complete

### Data Privacy

- Customer email addresses are not shared with other customers
- Customers cannot see internal comments
- Access can be revoked at any time

## Troubleshooting

### Customer Didn't Receive Email

1. **Check spam folder**: Ask customer to check spam/junk
2. **Verify email address**: Ensure the email is correct
3. **Resend invitation**: Use the resend feature
4. **Check email server**: Verify no email delivery issues
5. **Alternative contact**: Reach out via phone or other channels

### Invitation Link Not Working

1. **Check expiration**: Links expire after 7 days
2. **Resend invitation**: Generate a fresh link
3. **Clear browser cache**: Ask customer to clear cache
4. **Try different browser**: Test with another browser

### Customer Can't Access POC

1. **Verify acceptance**: Check if invitation was accepted
2. **Check permissions**: Ensure customer has correct role
3. **Contact support**: Escalate to Tenant Admin if needed

---

## FAQs

**Q: Can I invite multiple customers to one POC?**  
A: Yes, you can invite as many customers as needed.

**Q: Can customers invite other people?**  
A: No, only Sales Engineers and above can send invitations.

**Q: How long are invitation links valid?**  
A: Invitation links typically expire after 7 days for security.

**Q: Can I customize the invitation email?**  
A: You can add a personal message, but the email template is managed by your Tenant Admin.

**Q: What if a customer changes their email?**  
A: Contact your Tenant Admin to update their email address.

---

**Next Steps:**

- [Learn about managing tasks →](managing-tasks.md)
- [Track customer engagement →](tracking-progress.md)
- [Add resources for customers →](adding-resources.md)
