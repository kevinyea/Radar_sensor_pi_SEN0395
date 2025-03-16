import serial
import time
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("vital_monitoring.log"), logging.StreamHandler()]
)

# Configuration
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200

# Detection thresholds
NO_MOTION_THRESHOLD = 300  # 5 minutes without ANY motion (including breathing)
INITIAL_ALARM_THRESHOLD = 60  # First alarm after 1 minute

# Email configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


def setup_radar():
    """Set up connection to the mmWave radar sensor."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        logging.info("Successfully connected to radar sensor")
        return ser
    except serial.SerialException as e:
        logging.error(f"Error connecting to radar: {e}")
        return None


def send_email_alert(subject, message):
    """Send email alert with the specified subject and message."""
    try:
        # Check if email credentials are configured
        if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
            logging.error("Email configuration incomplete. Check your .env file.")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject

        # Add timestamp to message body
        full_message = f"{message}\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(full_message, 'plain'))

        # Connect to server and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
        server.quit()

        logging.info(f"Email alert sent: {subject}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False


def vital_sign_monitoring(ser):
    """Monitor for vital signs, with tiered alerts for potential medical emergency."""
    last_movement_time = time.time()
    last_presence_time = time.time()
    presence_detected = False
    initial_alarm_sent = False
    critical_alarm_sent = False
    last_critical_alert_time = 0

    logging.info("Starting vital sign monitoring...")

    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='replace').strip()

                # Parse the specific format (SJYBSS,1 or SJYBSS,0)
                if data.startswith("SJYBSS,"):
                    status = data.split(",")[1]
                    current_time = time.time()

                    if status == "1":  # Presence detected
                        if not presence_detected:
                            logging.info("Presence detected")
                            presence_detected = True

                        # Update last presence time
                        last_presence_time = current_time

                        # Any data change implies some movement (even minimal)
                        last_movement_time = current_time

                        # Reset alarm flags if movement is detected
                        if initial_alarm_sent or critical_alarm_sent:
                            logging.info("Movement detected - resetting alarm status")
                            initial_alarm_sent = False
                            critical_alarm_sent = False

                    elif status == "0":  # No presence detected
                        if presence_detected:
                            logging.info("No presence detected")
                            presence_detected = False

                            # Reset alarm flags when no presence
                            initial_alarm_sent = False
                            critical_alarm_sent = False

                # Calculate time since last movement and presence
                time_since_movement = current_time - last_movement_time

                # Tiered alerting system
                if presence_detected:
                    # Initial alert
                    if time_since_movement > INITIAL_ALARM_THRESHOLD and not initial_alarm_sent:
                        alert_msg = f"INITIAL ALERT: Person present but no vital signs detected for {int(time_since_movement)} seconds"
                        logging.warning(alert_msg)

                        # Send email for initial alert
                        send_email_alert(
                            "Motion Sensor - Initial Alert",
                            f"A person has been detected with no movement for {int(time_since_movement)} seconds.\n"
                            f"This may indicate a person is unconscious or in need of assistance."
                        )
                        initial_alarm_sent = True

                    # Critical alert - no movement for extended period
                    # Only send every 10 minutes to avoid email flooding
                    if (time_since_movement > NO_MOTION_THRESHOLD and
                            (not critical_alarm_sent or current_time - last_critical_alert_time > 600)):
                        alert_msg = f"EMERGENCY: No vital signs detected for {int(time_since_movement)} seconds!"
                        logging.critical(alert_msg)

                        # Send email for critical alert
                        send_email_alert(
                            "EMERGENCY - Potential Medical Emergency Detected",
                            f"URGENT: A person has been detected with absolutely no movement for {int(time_since_movement)} seconds.\n"
                            f"This may indicate a serious medical emergency requiring immediate attention."
                        )
                        critical_alarm_sent = True
                        last_critical_alert_time = current_time

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")


def main():
    # Verify email configuration
    if not os.path.exists('.env'):
        logging.warning(".env file not found. Email alerts will not be sent.")
        logging.info("Create a .env file with EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT variables.")

    ser = setup_radar()
    if ser:
        try:
            vital_sign_monitoring(ser)
        finally:
            ser.close()
    else:
        logging.error("Failed to connect to radar sensor")


if __name__ == "__main__":
    main()