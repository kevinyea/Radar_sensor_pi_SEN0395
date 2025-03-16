# Radar Vital Sign Monitoring System

A Python-based monitoring system that uses mmWave radar sensor technology to detect presence and vital signs of individuals, designed for health monitoring and safety applications.

## Overview

This system connects to a mmWave radar sensor via serial communication to monitor for presence and vital signs. It implements a tiered alerting system that can send email notifications when potential emergency situations are detected.

Key features:
- Real-time vital sign monitoring
- Tiered alerting system (initial and critical alerts)
- Email notifications for potential emergencies
- Configurable alert thresholds
- Logging system for monitoring activities

## Requirements

### Hardware
- Raspberry Pi (or compatible device)
- mmWave radar sensor compatible with UART/serial communication
- USB to TTL converter (if needed)

### Software Dependencies
- Python 3.6+
- Required Python packages:
  - `pyserial`
  - `python-dotenv`
  - Standard library packages: `time`, `logging`, `datetime`, `smtplib`, `email`, `os`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/radar-vital-monitoring.git
   cd radar-vital-monitoring
   ```

2. Install required Python packages:
   ```
   pip install pyserial python-dotenv
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECIPIENT=recipient_email@example.com
   ```
   Note: For Gmail, you'll need to use an App Password.

## Configuration

The following parameters can be modified in the script according to your needs:

- `SERIAL_PORT`: Set to the correct serial port for your radar sensor (default: '/dev/ttyAMA0')
- `BAUD_RATE`: Set to match your radar sensor's baud rate (default: 115200)
- `NO_MOTION_THRESHOLD`: Time in seconds before triggering a critical alert (default: 300 seconds)
- `INITIAL_ALARM_THRESHOLD`: Time in seconds before triggering an initial alert (default: 60 seconds)

## Usage

Run the monitoring system:

```
python vital_monitoring.py
```

The system will:
1. Connect to the radar sensor via serial port
2. Continuously monitor for presence and motion
3. Send an initial alert if a person is detected but no movement is detected for 1 minute
4. Send a critical alert if no movement is detected for 5 minutes
5. Log all activities to both the console and a log file

To stop the monitoring, press Ctrl+C in the terminal.

## System Operation

The system works by:
1. Reading data from the mmWave radar sensor in the format "SJYBSS,1" (presence) or "SJYBSS,0" (no presence)
2. Monitoring time since last detected movement
3. Implementing a tiered alert system:
   - Initial alert: After 60 seconds without movement
   - Critical alert: After 300 seconds (5 minutes) without movement

## Troubleshooting

### Common Issues:
- **Serial Connection Errors**: Verify the correct port and baud rate for your radar sensor
- **Email Alerts Not Sending**: Ensure your `.env` file is correctly configured and you're using an app password for Gmail
- **False Alerts**: You may need to adjust the threshold values based on your specific environment

### Logs:
Check the `vital_monitoring.log` file for detailed information about the system's operation and any errors that occur.

## License

[Add your chosen license here]

## Contributing

Contributions to improve the system are welcome. Please feel free to submit a pull request or open an issue.

## Safety Notice

This system is designed as a supplementary safety measure and should not replace professional medical monitoring. Always ensure proper medical care for individuals with health concerns.
