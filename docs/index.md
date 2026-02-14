# POC Manager User Guide

<div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #6366f1 100%); border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 2rem; color: white; position: relative; overflow: hidden;" markdown>

<div style="position: absolute; top: -20px; right: -20px; width: 200px; height: 200px; background: rgba(255,255,255,0.08); border-radius: 50%;"></div>
<div style="position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>

<div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
<span style="font-size: 2.5rem;">🤖</span>
<div>
<span style="background: rgba(255,255,255,0.2); color: #fbbf24; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.7rem; border-radius: 1rem; letter-spacing: 0.05em;">✨ NEW — BETA</span>
<h2 style="margin: 0.3rem 0 0 0; font-size: 1.75rem; font-weight: 800; color: white;">AI Assistant</h2>
</div>
</div>

<p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1rem; opacity: 0.95;">
Ask questions about your POCs in <strong>plain English</strong>. The AI Assistant retrieves live data from your projects, tasks, and resources — giving you instant, context-aware answers powered by LLMs and MCP tools.
</p>

<div style="display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 1.5rem;">
<span style="background: rgba(255,255,255,0.15); padding: 0.35rem 0.85rem; border-radius: 2rem; font-size: 0.85rem;">💬 Natural Language Queries</span>
<span style="background: rgba(255,255,255,0.15); padding: 0.35rem 0.85rem; border-radius: 2rem; font-size: 0.85rem;">⚡ Real-Time Data Retrieval</span>
<span style="background: rgba(255,255,255,0.15); padding: 0.35rem 0.85rem; border-radius: 2rem; font-size: 0.85rem;">🔒 Role-Based Access</span>
<span style="background: rgba(255,255,255,0.15); padding: 0.35rem 0.85rem; border-radius: 2rem; font-size: 0.85rem;">🔑 Bring Your Own Model</span>
</div>

[**Explore AI Assistant →**](features/ai-assistant.md){ style="display: inline-block; background: white; color: #4f46e5; font-weight: 700; padding: 0.6rem 1.5rem; border-radius: 0.5rem; text-decoration: none; transition: transform 0.2s;" }
&nbsp;&nbsp;
[Setup Guide →](tenant-admin/ai-assistant.md){ style="display: inline-block; background: rgba(255,255,255,0.15); color: white; font-weight: 600; padding: 0.6rem 1.5rem; border-radius: 0.5rem; text-decoration: none; border: 1px solid rgba(255,255,255,0.3);" }

</div>

Welcome to the **POC Manager** - a comprehensive platform for managing Proof of Concept (POC) engagements across your organization.

## What is POC Manager?

POC Manager is a multi-tenant web application designed to streamline the entire POC lifecycle, from planning and execution to customer collaboration and reporting. It helps sales teams, engineers, and customers work together seamlessly on proof of concept projects.

## Key Features

### 🎯 **Multi-Tenant Architecture**
- Separate workspaces for different organizations
- Custom branding per tenant
- Isolated data and user management

### 👥 **Role-Based Access Control**
- **Platform Admin**: Manages tenants and platform configuration
- **Tenant Admin**: Manages tenant settings and users
- **Administrator**: Creates POC templates and manages POC library
- **Sales Engineer**: Creates and manages POC engagements
- **Customer**: Participates in POCs and provides feedback

### 📋 **Task Management**
- Reusable task and task group templates
- Progress tracking with visual indicators
- Status management (Not Started, In Progress, Completed, Blocked)
- Task assignment to POC participants
- Clear ownership and accountability

### 📚 **Resource Management**
- Attach multiple resources to tasks (links, code snippets, text notes, files)
- Color-coded resource types for easy identification
- Shared resources across POC participants

### 💬 **Collaboration**
- Internal and external comments on tasks
- Real-time feedback from customers
- Communication history for each task

### 🤖 **AI Assistant**
- Intelligent Q&A about your POCs and tasks
- Natural language queries powered by LLMs
- Real-time data retrieval using MCP tools
- Secure, role-based access to information

### 📊 **Reporting & Analytics**
- POC dashboard with key metrics
- Progress tracking and completion rates
- Success criteria monitoring
- Document generation (PDF, Markdown)

## Quick Navigation

=== "Getting Started"

    New to POC Manager? Start here:
    
    - [Overview](getting-started/overview.md) - Learn the basics
    - [Login & Authentication](getting-started/login.md) - Access your account
    - [User Roles](getting-started/roles.md) - Understand permissions

=== "By Role"

    Jump to documentation for your role:
    
    - [Platform Admin](platform-admin/tenants.md)
    - [Tenant Admin](tenant-admin/users.md) | [Manage Public Links](tenant-admin/public-share-links.md)
    - [Administrator](administrator/task-templates.md)
    - [Sales Engineer](sales-engineer/poc-overview.md)
    - [Customer](customer/viewing-pocs.md) | [Access Public POCs](customer/accessing-public-pocs.md)

=== "Features"

    Explore specific features:
    
    - [Dashboard](features/dashboard.md)
    - [AI Assistant](features/ai-assistant.md)
    - [Comments System](features/comments.md)
    - [Resources](features/resources.md)
    - [Task Assignment](features/task-assignment.md)
    - [Public Share Links](features/public-share-links.md)
    - [Document Generation](features/documents.md)

## Getting Help

If you need assistance:

- Check the relevant section in this documentation
- Contact your tenant administrator
- Reach out to support

---

**Ready to get started?** Head to [Getting Started > Overview](getting-started/overview.md) to begin your journey!
