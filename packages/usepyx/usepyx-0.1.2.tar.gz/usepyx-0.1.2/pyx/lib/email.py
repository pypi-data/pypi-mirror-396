"""
PyX Email Service
Simple email sending with SMTP support.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Union
import os


class EmailConfig:
    """Email configuration"""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = ""
    FROM_NAME: str = "PyX App"


class Email:
    """
    PyX Email Service.
    
    Usage:
        from pyx.email import email
        
        # Configure
        email.configure(
            host="smtp.gmail.com",
            port=587,
            user="your@gmail.com",
            password="app-password",
            from_email="your@gmail.com",
            from_name="My App"
        )
        
        # Send email
        email.send(
            to="recipient@example.com",
            subject="Hello",
            body="<h1>Welcome!</h1>",
            html=True
        )
    """
    
    @classmethod
    def configure(
        cls,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        from_email: str = None,
        from_name: str = None,
        use_tls: bool = True
    ):
        """
        Configure email settings.
        Reads from environment variables if not provided.
        """
        EmailConfig.SMTP_HOST = host or os.getenv("SMTP_HOST", "")
        EmailConfig.SMTP_PORT = port or int(os.getenv("SMTP_PORT", "587"))
        EmailConfig.SMTP_USER = user or os.getenv("SMTP_USER", "")
        EmailConfig.SMTP_PASSWORD = password or os.getenv("SMTP_PASSWORD", "")
        EmailConfig.FROM_EMAIL = from_email or os.getenv("FROM_EMAIL", "")
        EmailConfig.FROM_NAME = from_name or os.getenv("FROM_NAME", "PyX App")
        EmailConfig.SMTP_USE_TLS = use_tls
        
        print(f"[PyX Email] Configured: {EmailConfig.SMTP_HOST}:{EmailConfig.SMTP_PORT}")
    
    @classmethod
    def send(
        cls,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        html: bool = False,
        attachments: List[str] = None,
        cc: List[str] = None,
        bcc: List[str] = None,
        reply_to: str = None
    ) -> dict:
        """
        Send an email.
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Email body (text or HTML)
            html: If True, body is HTML
            attachments: List of file paths to attach
            cc: CC recipients
            bcc: BCC recipients
            reply_to: Reply-to address
            
        Returns:
            dict with success status and error if any
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = f"{EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>"
            msg["Subject"] = subject
            
            # Handle recipients
            if isinstance(to, list):
                msg["To"] = ", ".join(to)
                recipients = to.copy()
            else:
                msg["To"] = to
                recipients = [to]
            
            if cc:
                msg["Cc"] = ", ".join(cc)
                recipients.extend(cc)
            
            if bcc:
                recipients.extend(bcc)
            
            if reply_to:
                msg["Reply-To"] = reply_to
            
            # Add body
            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            filename = os.path.basename(filepath)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename={filename}"
                            )
                            msg.attach(part)
            
            # Connect and send
            with smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT) as server:
                if EmailConfig.SMTP_USE_TLS:
                    server.starttls()
                
                if EmailConfig.SMTP_USER and EmailConfig.SMTP_PASSWORD:
                    server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                
                server.sendmail(EmailConfig.FROM_EMAIL, recipients, msg.as_string())
            
            print(f"[PyX Email] Sent to: {to}")
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            print(f"[PyX Email] Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    def send_template(
        cls,
        to: Union[str, List[str]],
        subject: str,
        template: str,
        context: dict = {},
        **kwargs
    ) -> dict:
        """
        Send email using a template with variable substitution.
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            template: HTML template with {{variable}} placeholders
            context: Dict of variables to substitute
            
        Usage:
            email.send_template(
                to="user@example.com",
                subject="Welcome!",
                template="<h1>Hello {{name}}!</h1><p>Your code is {{code}}</p>",
                context={"name": "John", "code": "123456"}
            )
        """
        # Simple template substitution
        body = template
        for key, value in context.items():
            body = body.replace("{{" + key + "}}", str(value))
        
        return cls.send(to=to, subject=subject, body=body, html=True, **kwargs)
    
    @classmethod
    def send_welcome(cls, to: str, name: str, **kwargs) -> dict:
        """Send a welcome email (built-in template)"""
        template = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #3b82f6;">Welcome to {{app_name}}!</h1>
            <p>Hi {{name}},</p>
            <p>Thank you for signing up. We're excited to have you on board!</p>
            <p style="margin-top: 30px;">Best regards,<br>The {{app_name}} Team</p>
        </div>
        """
        return cls.send_template(
            to=to,
            subject=f"Welcome to {EmailConfig.FROM_NAME}!",
            template=template,
            context={"name": name, "app_name": EmailConfig.FROM_NAME},
            **kwargs
        )
    
    @classmethod
    def send_reset_password(cls, to: str, name: str, reset_link: str, **kwargs) -> dict:
        """Send a password reset email (built-in template)"""
        template = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #3b82f6;">Reset Your Password</h1>
            <p>Hi {{name}},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{reset_link}}" style="background: #3b82f6; color: white; padding: 12px 24px; 
                   text-decoration: none; border-radius: 6px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p style="color: #6b7280; font-size: 14px;">
                If you didn't request this, you can safely ignore this email.
            </p>
            <p style="margin-top: 30px;">Best regards,<br>The {{app_name}} Team</p>
        </div>
        """
        return cls.send_template(
            to=to,
            subject="Reset Your Password",
            template=template,
            context={"name": name, "reset_link": reset_link, "app_name": EmailConfig.FROM_NAME},
            **kwargs
        )
    
    @classmethod
    def send_verification(cls, to: str, name: str, code: str, **kwargs) -> dict:
        """Send an email verification code (built-in template)"""
        template = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #3b82f6;">Verify Your Email</h1>
            <p>Hi {{name}},</p>
            <p>Your verification code is:</p>
            <p style="text-align: center; margin: 30px 0;">
                <span style="background: #f3f4f6; padding: 16px 32px; font-size: 32px; 
                       font-weight: bold; letter-spacing: 8px; border-radius: 8px;">
                    {{code}}
                </span>
            </p>
            <p style="color: #6b7280; font-size: 14px;">
                This code will expire in 10 minutes.
            </p>
            <p style="margin-top: 30px;">Best regards,<br>The {{app_name}} Team</p>
        </div>
        """
        return cls.send_template(
            to=to,
            subject="Your Verification Code",
            template=template,
            context={"name": name, "code": code, "app_name": EmailConfig.FROM_NAME},
            **kwargs
        )


# Global instance
email = Email()
