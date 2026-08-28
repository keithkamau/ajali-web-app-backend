import logging

from django.conf import settings

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail as SendGridMail
except ImportError:
    SendGridAPIClient = None
    SendGridMail = None

try:
    import africastalking as _africastalking
except ImportError:
    _africastalking = None

from .models import Notification, NotificationPreference

logger = logging.getLogger(__name__)

STATUS_LABELS = {
    "draft": "Draft",
    "under_investigation": "Under Investigation",
    "rejected": "Rejected",
    "resolved": "Resolved",
    "under_review": "Under Review",
    "in_progress": "In Progress",
    "reported": "Reported",
}


def create_notification(user, notification_type, title, message):
    return Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
    )


def send_email(user, subject, html_body):
    api_key = getattr(settings, "SENDGRID_API_KEY", "")
    if not api_key:
        logger.warning("SENDGRID_API_KEY not set, skipping email to %s", user.email)
        return False
    try:
        from_email = getattr(settings, "SENDGRID_FROM_EMAIL", "noreply@ajali.app")
        message = SendGridMail(
            from_email=from_email,
            to_emails=user.email,
            subject=subject,
            html_content=html_body,
        )
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as exc:
        logger.error("Email send failed for %s: %s", user.email, exc)
        return False


def send_sms(user, message_text):
    api_key = getattr(settings, "AFRICASTALKING_API_KEY", "")
    if not api_key:
        logger.warning("AFRICASTALKING_API_KEY not set, skipping SMS")
        return False
    if not user.phone_number:
        logger.warning("User %s has no phone number, skipping SMS", user.email)
        return False
    try:
        username = getattr(settings, "AFRICASTALKING_USERNAME", "sandbox")
        _africastalking.initialize(username, api_key)
        sms = _africastalking.SMS
        sms.send(message_text, [user.phone_number])
        return True
    except Exception as exc:
        logger.error("SMS send failed for %s: %s", user.email, exc)
        return False


def _get_preferences(user):
    pref, _ = NotificationPreference.objects.get_or_create(user=user)
    return pref


def notify_incident_created(incident, user):
    notification = create_notification(
        user=user,
        notification_type="incident_created",
        title="Incident Report Received",
        message=f"Your incident '{incident.title}' has been received and is under review.",
    )
    pref = _get_preferences(user)
    if pref.email_enabled:
        send_email(
            user,
            "Ajali! — Incident Report Received",
            _incident_created_html(incident, user),
        )
    return notification


def notify_status_change(incident, old_status, new_status, reporter):
    old_label = STATUS_LABELS.get(old_status, old_status)
    new_label = STATUS_LABELS.get(new_status, new_status)
    notification = create_notification(
        user=reporter,
        notification_type="status_change",
        title="Incident Status Updated",
        message=(
            f"Your incident '{incident.title}' status changed "
            f"from {old_label} to {new_label}."
        ),
    )
    pref = _get_preferences(reporter)
    if pref.email_enabled:
        send_email(
            reporter,
            "Ajali! — Incident Status Update",
            _status_email_html(incident, old_label, new_label),
        )
    if pref.sms_enabled:
        send_sms(
            reporter,
            f"Ajali! Update: Your incident '{incident.title}' is now {new_label}.",
        )
    return notification


def _incident_created_html(incident, user):
    return f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#e53e3e">Ajali!</h2>
      <p>Hello {user.full_name},</p>
      <p>Your incident report has been received and is currently under review.</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0">
        <tr style="background:#f7f7f7">
          <td style="padding:8px;font-weight:bold">Title</td>
          <td style="padding:8px">{incident.title}</td>
        </tr>
        <tr>
          <td style="padding:8px;font-weight:bold">Status</td>
          <td style="padding:8px">Reported</td>
        </tr>
      </table>
      <p>We will notify you of any status changes.</p>
      <p>— Ajali! Team</p>
    </div>
    """


def _status_email_html(incident, old_label, new_label):
    return f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#e53e3e">Ajali!</h2>
      <p>Your incident status has been updated.</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0">
        <tr style="background:#f7f7f7">
          <td style="padding:8px;font-weight:bold">Incident</td>
          <td style="padding:8px">{incident.title}</td>
        </tr>
        <tr>
          <td style="padding:8px;font-weight:bold">Previous Status</td>
          <td style="padding:8px">{old_label}</td>
        </tr>
        <tr style="background:#f7f7f7">
          <td style="padding:8px;font-weight:bold">New Status</td>
          <td style="padding:8px">{new_label}</td>
        </tr>
      </table>
      <p>— Ajali! Team</p>
    </div>
    """
