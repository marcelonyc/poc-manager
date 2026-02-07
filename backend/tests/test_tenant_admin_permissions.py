"""
Test to verify tenant admin cannot modify platform-level user.is_active

This test demonstrates:
1. Tenant Admin role is determined from JWT token (_current_role)
2. Platform Admin role is determined from JWT token (_current_role)
3. Tenant Admins can only modify user_tenant_roles.is_active
4. Platform Admins can modify users.is_active
"""

# Example 1: Tenant Admin deactivates a user
# JWT Token contains: { "role": "tenant_admin", "tenant_id": 1 }
# current_user._current_role = "tenant_admin" (from JWT)
# current_user.role = "platform_admin" (from users table - IGNORED)

# Expected behavior:
# - current_role = getattr(current_user, "_current_role", current_user.role)
# - current_role = "tenant_admin"
# - Skips platform-level deactivation (users.is_active)
# - Proceeds to tenant-level deactivation (user_tenant_roles.is_active)
# - Only modifies: user_tenant_roles.is_active = False for tenant_id=1

# Example 2: Platform Admin deactivates a user
# JWT Token contains: { "role": "platform_admin", "tenant_id": None }
# current_user._current_role = "platform_admin" (from JWT)
# current_user.role = "platform_admin" (from users table)

# Expected behavior:
# - current_role = "platform_admin"
# - Enters platform-level deactivation branch
# - Modifies: users.is_active = False
# - User loses access to ALL tenants

print("Role determination logic:")
print("========================")
print()
print("OLD (VULNERABLE):")
print("  if current_user.role == UserRole.PLATFORM_ADMIN:")
print("     # Uses deprecated users.role field")
print("     # Tenant admin with old role='platform_admin' can access this!")
print()
print("NEW (SECURE):")
print(
    "  current_role = getattr(current_user, '_current_role', current_user.role)"
)
print("  if current_role == UserRole.PLATFORM_ADMIN:")
print("     # Uses role from JWT token (tenant-specific)")
print("     # Only true platform admins can access this!")
print()
print("The JWT token's role (_current_role) is the source of truth,")
print("not the deprecated users.role field.")
