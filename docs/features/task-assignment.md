# Task Assignment

## Overview

The Task Assignment feature allows Sales Engineers and Administrators to assign POC participants to specific tasks. This helps clarify responsibilities, track ownership, and improve accountability during POC execution.

## Features

- **Multi-participant assignment**: Assign one or more participants to each task
- **Visual indicators**: Assignees are displayed as badges on tasks
- **Easy management**: Simple modal interface for selecting participants
- **Real-time updates**: Assignment changes are immediately reflected in the UI
- **Customer visibility**: Customers can see who is assigned to each task (read-only)

## User Roles

### Sales Engineer / Administrator
- Can assign participants to tasks in their POCs
- Can view all assigned participants
- Can modify or remove assignments

### Customer
- Can view assigned participants (read-only)
- Cannot modify assignments

## How to Use

### Assigning Participants to a Task

1. **Navigate to POC Details**: Open the POC you want to work with
2. **Go to Tasks Tab**: Click on the "Tasks" tab in the navigation
3. **Locate the Task**: Find the task you want to assign participants to
4. **Click "👥 Assign" Button**: This opens the assignment modal
5. **Select Participants**: Check the boxes next to participants you want to assign
   - Participants are filtered to show only active members (joined or invited)
   - You can see participant roles (Sales Engineer, Customer) and status
6. **Save Assignment**: Click "Assign" to save your selection
7. **View Assignees**: The task now displays assigned participants as blue badges

### Viewing Assigned Participants

**In POC Form (Sales Engineer/Admin view):**
- Assignees appear below the task description
- Displayed as blue badges with format: "👤 [Name]"
- Hover over a badge to see the participant's email

**In Customer View:**
- Assignees are shown in the same format
- Visible in both task list and expanded task groups

### Unassigning Participants

To remove all assignments from a task:
1. Click the "👥 Assign" button on the task
2. Uncheck all participants
3. Click "Assign" to save

The modal shows how many participants are currently selected, including 0 if none are selected.

## API Endpoints

### Assign Participants to Task
```
POST /tasks/pocs/{poc_id}/tasks/{task_id}/assign
```

**Request Body:**
```json
{
  "participant_ids": [1, 2, 3]
}
```

**Response:**
```json
[
  {
    "id": 1,
    "participant_id": 1,
    "participant_name": "John Doe",
    "participant_email": "john@example.com",
    "assigned_at": "2024-02-07T20:30:00Z"
  }
]
```

**Notes:**
- Replaces all existing assignments with the new list
- Validates that all participant IDs belong to the POC
- Returns 404 if POC or task not found
- Returns 400 if participant IDs are invalid

### Get Task Assignees
```
GET /tasks/pocs/{poc_id}/tasks/{task_id}/assignees
```

**Response:**
```json
[
  {
    "id": 1,
    "participant_id": 1,
    "participant_name": "John Doe",
    "participant_email": "john@example.com",
    "assigned_at": "2024-02-07T20:30:00Z"
  }
]
```

### Remove All Assignees
```
DELETE /tasks/pocs/{poc_id}/tasks/{task_id}/assign
```

**Response:**
```json
{
  "message": "All assignees removed"
}
```

### List POC Tasks (with assignees)
```
GET /tasks/pocs/{poc_id}/tasks
```

**Response:**
Each task now includes an `assignees` array:
```json
[
  {
    "id": 1,
    "title": "Setup Environment",
    "description": "Configure the development environment",
    "status": "in_progress",
    "assignees": [
      {
        "id": 1,
        "participant_id": 1,
        "participant_name": "John Doe",
        "participant_email": "john@example.com",
        "assigned_at": "2024-02-07T20:30:00Z"
      }
    ]
  }
]
```

## Database Schema

### poc_task_assignees Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| poc_task_id | Integer | Foreign key to poc_tasks |
| participant_id | Integer | Foreign key to poc_participants |
| assigned_at | DateTime | Timestamp of assignment |
| assigned_by | Integer | Foreign key to users (who made the assignment) |

**Constraints:**
- Unique constraint on (poc_task_id, participant_id)
- Foreign key constraints ensure referential integrity
- Cascade deletes when parent records are removed

## Implementation Details

### Backend Components

1. **Model**: `POCTaskAssignee` in [backend/app/models/task.py](../../backend/app/models/task.py)
   - Defines the database structure
   - Relationships to POCTask, POCParticipant, and User

2. **Schemas**: [backend/app/schemas/task.py](../../backend/app/schemas/task.py)
   - `POCTaskAssignee`: Response schema for assignee data
   - `POCTaskAssignRequest`: Request schema for assignment operations
   - Updated `POCTask` to include assignees list

3. **Endpoints**: [backend/app/routers/tasks.py](../../backend/app/routers/tasks.py)
   - Three new endpoints for manage assignments
   - Modified `list_poc_tasks()` to populate assignees

### Frontend Components

1. **TaskAssignmentModal**: [frontend/src/components/TaskAssignmentModal.tsx](../../frontend/src/components/TaskAssignmentModal.tsx)
   - Reusable modal component
   - Multi-select interface with checkboxes
   - Displays participant roles and status
   - Handles assignment API calls

2. **POCForm Updates**: [frontend/src/components/POCForm.tsx](../../frontend/src/components/POCForm.tsx)
   - Added "👥 Assign" button to each task
   - Displays assignee badges below task descriptions
   - Integrates TaskAssignmentModal
   - Refreshes task data after assignment changes

3. **CustomerPOCView Updates**: [frontend/src/components/CustomerPOCView.tsx](../../frontend/src/components/CustomerPOCView.tsx)
   - Read-only display of assignees
   - Same badge format as POCForm
   - Visible in both task lists and task groups

## Best Practices

### When to Assign Tasks

- **During POC Planning**: Assign tasks when setting up the POC
- **As Participants Join**: Update assignments when new team members join
- **Role-based Assignment**: Assign tasks based on participant expertise
- **Balanced Workload**: Distribute tasks evenly across participants

### Assignment Guidelines

1. **Clear Ownership**: Assign at least one person to critical tasks
2. **Team Tasks**: Use multiple assignees for collaborative tasks
3. **Customer Involvement**: Assign customers to tasks requiring their input
4. **Update Status**: Remind assignees to update task status as they progress

## Troubleshooting

### Cannot Assign Participants

**Issue**: The assignment modal shows "No participants available"

**Solution**: 
- Ensure participants have been added to the POC
- Check that participants have "joined" or "invited" status
- Declined or removed participants won't appear

### Assignments Not Showing

**Issue**: Assigned participants don't appear on tasks

**Solution**:
- Refresh the page to ensure latest data is loaded
- Check browser console for API errors
- Verify the participant is still part of the POC

### Permission Denied

**Issue**: Cannot access assignment functionality

**Solution**:
- Only Sales Engineers and Administrators can assign tasks
- Customers have read-only access
- Check your user role in the system

## Future Enhancements

Potential improvements for future versions:

- **Email Notifications**: Notify participants when assigned to tasks
- **Assignment History**: Track who assigned tasks and when
- **Workload View**: Dashboard showing task distribution per participant
- **Bulk Assignment**: Assign multiple tasks at once
- **Task Filters**: Filter tasks by assignee
- **Assignment Comments**: Add notes when assigning tasks
