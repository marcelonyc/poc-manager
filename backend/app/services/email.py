"""Email service"""
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from app.config import settings
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


def get_mail_config(tenant: Tenant = None) -> ConnectionConfig:
    """Get email configuration (tenant-specific or default)"""
    if tenant and tenant.custom_mail_server:
        return ConnectionConfig(
            MAIL_USERNAME=tenant.custom_mail_username,
            MAIL_PASSWORD=tenant.custom_mail_password,
            MAIL_FROM=tenant.custom_mail_from,
            MAIL_PORT=tenant.custom_mail_port,
            MAIL_SERVER=tenant.custom_mail_server,
            MAIL_STARTTLS=tenant.custom_mail_tls,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
    else:
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_TLS,
            MAIL_SSL_TLS=settings.MAIL_SSL,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )


async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    tenant: Tenant = None,
    html: bool = False
):
    """Send an email"""
    config = get_mail_config(tenant)
    
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html" if html else "plain",
    )
    
    fm = FastMail(config)
    await fm.send_message(message)


async def send_invitation_email(
    recipient: str,
    full_name: str,
    token: str,
    invited_by: str,
):
    """Send Platform Admin invitation email"""
    try:
        # Get frontend URL from environment or use default
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        invitation_url = f"{frontend_url}/accept-invitation?token={token}"
        
        subject = "Invitation to Join as Platform Admin"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">You've Been Invited!</h2>
                <p>Hello {full_name},</p>
                <p><strong>{invited_by}</strong> has invited you to join as a <strong>Platform Administrator</strong> for POC Manager.</p>
                <p>As a Platform Admin, you will have access to manage tenants and platform-wide settings.</p>
                <div style="margin: 30px 0;">
                    <a href="{invitation_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Accept Invitation
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{invitation_url}">{invitation_url}</a>
                </p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This invitation will expire in 7 days.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, tenant=None, html=True)
        logger.info(f"Successfully sent platform admin invitation email to {recipient}")
    except Exception as e:
        # Log error but don't crash the background task
        logger.error(f"Failed to send invitation email to {recipient}: {str(e)}", exc_info=True)


async def send_user_invitation_email(
    email: str,
    full_name: str,
    role: str,
    temp_password: str,
    tenant: Tenant = None
):
    """Send user invitation email (for non-Platform Admin users)"""
    subject = "Invitation to POC Manager"
    body = f"""
    Hello {full_name},
    
    You have been invited to join POC Manager as a {role}.
    
    Your login credentials:
    Email: {email}
    Temporary Password: {temp_password}
    
    Please log in and change your password immediately.
    
    Best regards,
    POC Manager Team
    """
    
    await send_email([email], subject, body, tenant)


async def send_poc_update_notification(
    recipients: List[str],
    poc_title: str,
    update_type: str,
    tenant: Tenant = None
):
    """Send POC update notification"""
    subject = f"POC Update: {poc_title}"
    body = f"""
    A {update_type} has been made to POC: {poc_title}
    
    Please log in to POC Manager to view the details.
    
    Best regards,
    POC Manager Team
    """
    
    await send_email(recipients, subject, body, tenant)


async def send_poc_invitation_email(
    recipient: str,
    full_name: str,
    poc_title: str,
    token: str,
    invited_by_name: str,
    personal_message: str = None,
    tenant: Tenant = None
):
    """Send POC invitation email"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        invitation_url = f"{frontend_url}/poc-invitation?token={token}"
        
        subject = f"Invitation to Join POC: {poc_title}"
        
        personal_msg_html = ""
        if personal_message:
            personal_msg_html = f"""
            <div style="background-color: #F3F4F6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <p style="margin: 0; font-style: italic; color: #374151;">"{personal_message}"</p>
            </div>
            """
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">You've Been Invited to Join a POC!</h2>
                <p>Hello {full_name},</p>
                <p><strong>{invited_by_name}</strong> has invited you to participate in the following Proof of Concept:</p>
                <div style="background-color: #EEF2FF; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #4F46E5;">{poc_title}</h3>
                </div>
                {personal_msg_html}
                <p>As a participant, you'll be able to:</p>
                <ul>
                    <li>View POC objectives and success criteria</li>
                    <li>Track progress and milestones</li>
                    <li>Provide feedback and updates</li>
                    <li>Collaborate with the team</li>
                </ul>
                <div style="margin: 30px 0;">
                    <a href="{invitation_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Accept Invitation
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{invitation_url}">{invitation_url}</a>
                </p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This invitation will expire in 24 hours.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, tenant, html=True)
        logger.info(f"Successfully sent POC invitation email to {recipient} for POC: {poc_title}")
        return True
    except Exception as e:
        error_msg = f"Failed to send POC invitation email to {recipient}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False


async def send_poc_invitation_email_with_tracking(
    invitation_id: int,
    recipient: str,
    full_name: str,
    poc_title: str,
    token: str,
    invited_by_name: str,
    personal_message: str = None,
    tenant: Tenant = None
):
    """
    Send POC invitation email and update the database with delivery status.
    This wrapper function should be used in background tasks to ensure proper tracking.
    """
    from app.database import SessionLocal
    from app.models.poc_invitation import POCInvitation, POCInvitationStatus
    
    # Send the email
    success = await send_poc_invitation_email(
        recipient=recipient,
        full_name=full_name,
        poc_title=poc_title,
        token=token,
        invited_by_name=invited_by_name,
        personal_message=personal_message,
        tenant=tenant
    )
    
    # Update the invitation record
    db = SessionLocal()
    try:
        invitation = db.query(POCInvitation).filter(POCInvitation.id == invitation_id).first()
        if invitation:
            invitation.email_sent = success
            if success:
                invitation.email_error = None
                logger.info(f"Updated invitation {invitation_id} - email sent successfully")
            else:
                invitation.email_error = "Failed to send email - check logs for details"
                invitation.status = POCInvitationStatus.FAILED
                logger.error(f"Updated invitation {invitation_id} - marked as FAILED")
            db.commit()
        else:
            logger.warning(f"Could not find invitation {invitation_id} to update email status")
    except Exception as e:
        logger.error(f"Failed to update invitation {invitation_id} email status: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def send_password_reset_email(
    recipient: str,
    full_name: str,
    token: str,
    tenant: Tenant = None
):
    """Send password reset email"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        subject = "Password Reset Request"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">Password Reset Request</h2>
                <p>Hello {full_name},</p>
                <p>We received a request to reset your password for your POC Manager account.</p>
                <p>Click the button below to reset your password:</p>
                <div style="margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{reset_url}">{reset_url}</a>
                </p>
                <p style="color: #DC2626; font-size: 14px; margin-top: 30px;">
                    <strong>Important:</strong> This link will expire in 1 hour for security reasons.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, tenant, html=True)
        logger.info(f"Successfully sent password reset email to {recipient}")
        return True
    except Exception as e:
        error_msg = f"Failed to send password reset email to {recipient}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False


async def send_demo_verification_email(
    recipient: str,
    name: str,
    token: str,
):
    """Send email verification for demo account request"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        verification_url = f"{frontend_url}/verify-demo-email?token={token}"
        
        subject = "Verify Your Demo Account Request"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">Welcome to POC Manager!</h2>
                <p>Hello {name},</p>
                <p>Thank you for requesting a demo account. Please verify your email address to continue setting up your account.</p>
                <div style="margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{verification_url}">{verification_url}</a>
                </p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This verification link will expire in 24 hours.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, None, html=True)
        logger.info(f"Successfully sent demo verification email to {recipient}")
        return True
    except Exception as e:
        error_msg = f"Failed to send demo verification email to {recipient}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False


async def send_demo_welcome_email(
    recipient: str,
    name: str,
    company_name: str,
    tenant_slug: str,
):
    """Send welcome email after demo account setup"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        login_url = f"{frontend_url}/login"
        
        subject = "Welcome to Your POC Manager Demo Account!"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">Your Demo Account is Ready! 🎉</h2>
                <p>Hello {name},</p>
                <p>Your demo account for <strong>{company_name}</strong> has been successfully created and is ready to use!</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #4F46E5;">What's Included in Your Demo:</h3>
                    <ul style="line-height: 1.8;">
                        <li>Pre-configured users across all roles (Tenant Admin, Administrator, Sales Engineers, Customers)</li>
                        <li>Sample task templates and task groups ready to use</li>
                        <li>2 complete POC examples with success criteria</li>
                        <li>Full access to all POC management features</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h3 style="margin-top: 0; color: #856404;">Demo Account Limits:</h3>
                    <ul style="line-height: 1.8; color: #856404;">
                        <li><strong>Maximum 2 POCs</strong></li>
                        <li><strong>Maximum 20 tasks</strong></li>
                        <li><strong>Maximum 20 task groups</strong></li>
                        <li><strong>Maximum 10 resources/uploads total</strong></li>
                    </ul>
                    <p style="margin-bottom: 0; color: #856404;">
                        <strong>Ready to grow?</strong> You can request to convert your demo account to a full account at any time from your tenant settings.
                    </p>
                </div>
                
                <div style="margin: 30px 0;">
                    <a href="{login_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        Access Your Demo Account
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Your tenant identifier: <strong>{tenant_slug}</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, None, html=True)
        logger.info(f"Successfully sent demo welcome email to {recipient}")
        return True
    except Exception as e:
        error_msg = f"Failed to send demo welcome email to {recipient}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False


async def send_demo_conversion_request_email(
    admin_email: str,
    tenant_name: str,
    requested_by_name: str,
    requested_by_email: str,
    reason: str,
    request_id: int,
):
    """Send demo conversion request to platform admin"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        approval_url = f"{frontend_url}/admin/demo-conversions/{request_id}"
        
        subject = f"Demo Conversion Request: {tenant_name}"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">Demo Account Conversion Request</h2>
                <p>A demo account has requested conversion to a full account:</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Tenant:</strong> {tenant_name}</p>
                    <p style="margin: 5px 0;"><strong>Requested By:</strong> {requested_by_name} ({requested_by_email})</p>
                    {f'<p style="margin: 5px 0;"><strong>Reason:</strong> {reason}</p>' if reason else ''}
                </div>
                
                <div style="margin: 30px 0;">
                    <a href="{approval_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Review Request
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Click the button above to approve or reject this conversion request.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    POC Manager Platform Administration
                </p>
            </body>
        </html>
        """
        
        await send_email([admin_email], subject, body, None, html=True)
        logger.info(f"Successfully sent demo conversion request email to {admin_email} for tenant {tenant_name}")
        return True
    except Exception as e:
        error_msg = f"Failed to send demo conversion request email: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False


async def send_existing_account_notification_email(
    recipient: str,
    full_name: str,
):
    """Send notification to existing account holder that someone tried to create a demo with their email"""
    try:
        from app.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        login_url = f"{frontend_url}/login"
        reset_password_url = f"{frontend_url}/forgot-password"
        
        subject = "Demo Account Request Notification"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4F46E5;">Account Already Exists</h2>
                <p>Hello {full_name},</p>
                
                <p>We received a request to create a demo account using your email address. 
                However, an account with this email already exists in our system.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ If this was you:</strong></p>
                    <p style="margin: 10px 0 0 0;">You can log in to your existing account using the button below.</p>
                </div>
                
                <div style="margin: 30px 0;">
                    <a href="{login_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Log In to Your Account
                    </a>
                </div>
                
                <div style="background-color: #e7f3ff; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🔑 Forgot your password?</strong></p>
                    <p style="margin: 10px 0 0 0;">
                        No problem! You can reset it here: 
                        <a href="{reset_password_url}" style="color: #2196F3;">Reset Password</a>
                    </p>
                </div>
                
                <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #f44336; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🚨 If this was NOT you:</strong></p>
                    <p style="margin: 10px 0 0 0;">
                        Someone may have tried to use your email address. Your account is secure, 
                        but we recommend changing your password as a precaution.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    If you have any questions or concerns, please contact our support team.<br><br>
                    Best regards,<br>
                    POC Manager Team
                </p>
            </body>
        </html>
        """
        
        await send_email([recipient], subject, body, None, html=True)
        logger.info(f"Successfully sent existing account notification email to {recipient}")
        return True
    except Exception as e:
        error_msg = f"Failed to send existing account notification email: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False
