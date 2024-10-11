from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
import hashlib
import os

class Util:
    @staticmethod
    def send_email(request, user, email, token, websitetype, type, subject,new_password=None):
        """
        Sends an email to the user for various purposes like password reset or email verification.

        Args:
            request: HTTP request object.
            user: User instance.
            email: Email address of the recipient.
            token: Token for email verification or password reset.
            websitetype: Type of website sending the email.
            type: Type of email (password_reset or email_verification).
            subject: Subject of the email.
        """
        current_site = get_current_site(request).domain
        uidb64 = urlsafe_base64_encode(user.pk.bytes)

        # Generate absolute URL based on the type of email
        if type == 'password_reset':
            current_site = get_current_site(request)
            absurl = f'http://{current_site.domain}/#/reset-password/{uidb64}/{token}?new_password={new_password}'
            email_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Password Reset</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; color: #333; }}
                    .container {{ max-width: 600px; margin: 20px auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                    .header {{ text-align: center; padding: 10px 0; border-bottom: 1px solid #ddd; }}
                    .header h1 {{ margin: 0; color: #4CAF50; }}
                    .content {{ padding: 20px; }}
                    .content p {{ margin: 10px 0; line-height: 1.6; }}
                    .reset-button {{ display: block; width: 200px; margin: 20px auto; padding: 10px 0; text-align: center; background-color: #4CAF50; color: #fff; text-decoration: none; border-radius: 5px; font-size: 16px; }}
                    .footer {{ text-align: center; padding: 10px 0; border-top: 1px solid #ddd; margin-top: 20px; color: #888; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user.first_name},</p>
                        <p>Click the button below to reset your password:</p>
                        <a href="{absurl}" class="reset-button">Reset Password</a>

                        <p>or click on the link below</p>
                        <a>{absurl}</a>
                        <p>If you did not request this email, please ignore it.</p>
                    </div>
                    <div class="footer">
                        <p>Thank you for using our service!</p>
                    </div>
                </div>
            </body>
            </html>
            """
        elif type == 'email_verification':
            current_site = get_current_site(request)
            absurl = f'http://{current_site.domain}/#/verify-email/{uidb64}/{token}/'
            email_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Email Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; color: #333; }}
                    .container {{ max-width: 600px; margin: 20px auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                    .header {{ text-align: center; padding: 10px 0; border-bottom: 1px solid #ddd; }}
                    .header h1 {{ margin: 0; color: #4CAF50; }}
                    .content {{ padding: 20px; }}
                    .content p {{ margin: 10px 0; line-height: 1.6; }}
                    .verify-button {{ display: block; width: 200px; margin: 20px auto; padding: 10px 0; text-align: center; background-color: #4CAF50; color: #fff; text-decoration: none; border-radius: 5px; font-size: 16px; }}
                    .footer {{ text-align: center; padding: 10px 0; border-top: 1px solid #ddd; margin-top: 20px; color: #888; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email Verification</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user.first_name},</p>
                        <p>Click the link below to verify your email address:</p>
                        <a href="{absurl}" class="verify-button">Verify Email</a>
                        <p>or click on the link below</p>
                        <a>{absurl}</a>
                        <p>If you did not request this email, please ignore it.</p>
                    </div>
                    <div class="footer">
                        <p>Thank you for using our service!</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            current_site = get_current_site(request)
            absurl = f'http://{current_site.domain}/#/verify-email/{uidb64}/{token}/'
            email_body = f'Hi,\nUse link below to verify your email \n{absurl}'

        # Create and send email message
        try:
            email_subject = subject
            email_to = [email]
            email = EmailMessage(
                email_subject,
                email_body,
                websitetype,
                email_to,
            )
            email.send(fail_silently=False)
        except Exception as e:
            print(e)
            return False
        return True
    
    
    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = os.urandom(16)  # Generate a random salt
        
        # Encode the password and salt
        encoded_password = password.encode('utf-8')
        
        # Hash the combined bytes using SHA-256
        hashed = hashlib.sha256(encoded_password + salt).hexdigest()
        
        # Return the salt and hashed password as a string
        return f'{salt.hex()}${hashed}'

    @staticmethod
    def verify_password(stored_password, provided_password):
        # Split the stored password into salt and hashed password
        salt_hex, stored_hash = stored_password.split('$')
        
        # Decode the salt from hexadecimal to bytes
        salt = bytes.fromhex(salt_hex)
        
        # Hash the provided password with the same salt
        computed_hash = hashlib.sha256((provided_password.encode('utf-8') + salt)).hexdigest()
        
        # Compare the stored hash with the computed hash
        return stored_hash == computed_hash
