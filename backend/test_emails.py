# test_email.py
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def test_email():
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("❌ Email credentials not found in .env")
        return False
    
    try:
        print(f"📧 Testing email: {EMAIL_USER}")
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER  # Send to yourself
        msg['Subject'] = "Test Email from Health AI Assistant"
        
        body = "If you can read this, email is working correctly!"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(os.environ.get("EMAIL_HOST", "smtp.gmail.com"), 
                             int(os.environ.get("EMAIL_PORT", 587)))
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if EMAIL_USER and EMAIL_PASSWORD are correct")
        print("2. Make sure you're using App Password, not your regular password")
        print("3. Verify 2-Step Verification is enabled")
        print("4. Check if your account allows less secure apps (if using that)")
        return False

if __name__ == "__main__":
    test_email()