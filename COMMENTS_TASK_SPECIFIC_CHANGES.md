# Comments Task/Task Group Specific Implementation

## Overview
Changed the comment implementation to associate comments with specific POC tasks or task groups instead of being associated directly with the entire POC. This provides better organization and context for comments within POC workflow.

## Database Changes

### Migration: `20260211_2300-make_comments_task_specific.py`
- **Deletes** any existing POC-level comments (without task or task group association)
- **Makes `poc_id` nullable** in the comments table
- **Adds constraint** to ensure comments have either `poc_task_id` OR `poc_task_group_id` (not both, not neither)

## Backend Model Changes

### `app/models/comment.py`
- **Changed**: `poc_id` column from `nullable=False` to `nullable=True`
- **Updated**: `__repr__()` method to reflect task/task group context
- **Comment**: Comments are now derived from task/task group's POC relationship

## Backend Schema Changes

### `app/schemas/other.py`
- **CommentCreate**: Added validation method `validate_at_least_one_task()` to ensure either `poc_task_id` or `poc_task_group_id` is provided
- **Comment**: Changed `poc_id` from required (`int`) to optional (`Optional[int]`)

## API Endpoint Changes

### `app/routers/poc_components.py`

#### POST `/pocs/{poc_id}/comments` (Create Comment)
- **Now requires**: `task_id` OR `task_group_id` as query parameters
- **Validates**: The task/task group exists and belongs to the specified POC
- **Error handling**: Returns 400 if neither or both task_id/task_group_id are provided
- **Sets**: `poc_id` automatically from the POC

#### GET `/pocs/{poc_id}/comments` (List Comments)
- **Now requires**: `task_id` OR `task_group_id` as query parameters (was optional)
- **Validates**: At least one filter is specified
- **Validates**: The task/task group exists and belongs to the specified POC
- **Returns**: Only comments for the specified task or task group
- **Behavior**: No longer returns all POC comments

#### PUT `/pocs/{poc_id}/comments/{comment_id}` (Update Comment)
- **No breaking changes**: Still validates comment belongs to specified POC
- **Note**: Works with optional `poc_id` due to schema changes

#### DELETE `/pocs/{poc_id}/comments/{comment_id}` (Delete Comment)
- **No breaking changes**: Still validates comment belongs to specified POC

### `app/routers/public_pocs.py`

#### GET `/{access_token}/comments` (Get Public POC Comments)
- **Now requires**: `poc_task_id` OR `poc_task_group_id` as query parameters
- **Validates**: At least one filter is specified
- **Validates**: The task/task group exists and belongs to the specified POC
- **Returns**: Only non-internal comments for the specified task or task group

#### POST `/{access_token}/comments` (Create Public Comment)
- **Now requires**: Either `poc_task_id` or `poc_task_group_id` in request body
- **Validates**: The task/task group exists and belongs to the specified POC
- **Error handling**: Returns 400 if neither or both task/task group are provided

#### GuestCommentCreate Schema
- **Updated**: Added validation method `validate_task_or_taskgroup()` to enforce task/task group requirement

## Frontend Changes

### `frontend/src/components/CommentsModal.tsx`
- **Validation**: Checks that either `taskId` or `taskGroupId` is provided
- **API call updates**:
  - `fetchComments()`: Now properly constructs query string with `task_id` or `task_group_id`
  - `handleCreateComment()`: Now includes task/task group parameters in URL
  - Public API: Adjusts query parameter names for public endpoints
- **Error handling**: Shows error if neither task nor task group is specified

## Breaking Changes
1. **Comments can no longer be created at POC level** - must be associated with a task or task group
2. **List comments endpoint now requires filtering** by task or task group
3. **Existing POC-level comments will be deleted** during migration
4. **API clients must update** to provide `task_id` or `task_group_id` when:
   - Creating comments
   - Listing comments
   - Accessing public comments

## Migration Path

### For existing data:
1. Run migration: `alembic upgrade head`
   - This will delete all POC-level comments
   - Make poc_id nullable
   - Add constraint for task/task group

### For API consumers:
1. **Update comment creation**: Must provide `task_id` or `task_group_id`
2. **Update comment listing**: Add `task_id` or `task_group_id` as query parameter
3. **Update frontend**: Ensure CommentsModal receives taskId or taskGroupId

## Benefits
- **Better organization**: Comments are now contextual to specific tasks
- **Improved filtering**: Can view comments by task or task group
- **Enhanced collaboration**: Team members can focus on task-specific discussions
- **Flexible structure**: Maintains ability to comment on either tasks or task groups

## Testing Recommendations
1. Test creating comments with valid task_id
2. Test creating comments with valid task_group_id
3. Test error when neither task_id nor task_group_id is provided
4. Test error when both task_id and task_group_id are provided
5. Test listing comments by task_id
6. Test listing comments by task_group_id
7. Test error when listing without task_id or task_group_id
8. Test public comments work with new structure
9. Test migration preserves comment data for task-associated comments
10. Test migration deletes POC-level comments
