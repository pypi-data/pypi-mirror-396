"""
Notification Utilities - Slack, Discord, Email notifications
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import logging

import httpx

if TYPE_CHECKING:
    from assetpipe.core.pipeline import PipelineResult

logger = logging.getLogger(__name__)


def send_slack_notification(
    webhook: str,
    result: "PipelineResult",
    on_events: List[str] = ["error", "complete"],
) -> bool:
    """
    Send notification to Slack webhook.
    
    Args:
        webhook: Slack webhook URL
        result: Pipeline result to report
        on_events: Events to notify on (error, complete, warning)
        
    Returns:
        True if notification sent successfully
    """
    # Check if we should send
    should_send = False
    if "complete" in on_events:
        should_send = True
    if "error" in on_events and result.error_count > 0:
        should_send = True
    if "warning" in on_events and result.warning_count > 0:
        should_send = True
    
    if not should_send:
        return False
    
    # Build message
    if result.error_count > 0:
        color = "#ef4444"  # Red
        status = "❌ Failed"
    elif result.warning_count > 0:
        color = "#f59e0b"  # Yellow
        status = "⚠️ Completed with warnings"
    else:
        color = "#4ade80"  # Green
        status = "✅ Completed"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"AssetPipe {status}",
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Processed:*\n{result.success_count}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Failed:*\n{result.error_count}"
                },
            ]
        }
    ]
    
    if result.errors:
        error_text = "\n".join(f"• {e}" for e in result.errors[:5])
        if len(result.errors) > 5:
            error_text += f"\n... and {len(result.errors) - 5} more"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Errors:*\n{error_text}"
            }
        })
    
    payload = {
        "attachments": [
            {
                "color": color,
                "blocks": blocks,
            }
        ]
    }
    
    try:
        response = httpx.post(webhook, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


def send_discord_notification(
    webhook: str,
    result: "PipelineResult",
    on_events: List[str] = ["error", "complete"],
) -> bool:
    """
    Send notification to Discord webhook.
    
    Args:
        webhook: Discord webhook URL
        result: Pipeline result to report
        on_events: Events to notify on (error, complete, warning)
        
    Returns:
        True if notification sent successfully
    """
    # Check if we should send
    should_send = False
    if "complete" in on_events:
        should_send = True
    if "error" in on_events and result.error_count > 0:
        should_send = True
    if "warning" in on_events and result.warning_count > 0:
        should_send = True
    
    if not should_send:
        return False
    
    # Build embed
    if result.error_count > 0:
        color = 0xef4444  # Red
        status = "❌ Failed"
    elif result.warning_count > 0:
        color = 0xf59e0b  # Yellow
        status = "⚠️ Completed with warnings"
    else:
        color = 0x4ade80  # Green
        status = "✅ Completed"
    
    fields = [
        {
            "name": "Processed",
            "value": str(result.success_count),
            "inline": True,
        },
        {
            "name": "Failed",
            "value": str(result.error_count),
            "inline": True,
        },
    ]
    
    if result.errors:
        error_text = "\n".join(f"• {e}" for e in result.errors[:5])
        if len(result.errors) > 5:
            error_text += f"\n... and {len(result.errors) - 5} more"
        
        fields.append({
            "name": "Errors",
            "value": error_text,
            "inline": False,
        })
    
    payload = {
        "embeds": [
            {
                "title": f"AssetPipe {status}",
                "color": color,
                "fields": fields,
                "footer": {
                    "text": "AssetPipe Pipeline"
                }
            }
        ]
    }
    
    try:
        response = httpx.post(webhook, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False


def send_email_notification(
    smtp_host: str,
    smtp_port: int,
    from_addr: str,
    to_addrs: List[str],
    result: "PipelineResult",
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_tls: bool = True,
) -> bool:
    """
    Send notification via email.
    
    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port
        from_addr: Sender email address
        to_addrs: List of recipient email addresses
        result: Pipeline result to report
        username: SMTP username (optional)
        password: SMTP password (optional)
        use_tls: Whether to use TLS
        
    Returns:
        True if email sent successfully
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Build subject
    if result.error_count > 0:
        subject = f"[AssetPipe] ❌ Pipeline Failed - {result.error_count} errors"
    elif result.warning_count > 0:
        subject = f"[AssetPipe] ⚠️ Pipeline Completed with {result.warning_count} warnings"
    else:
        subject = f"[AssetPipe] ✅ Pipeline Completed - {result.success_count} assets processed"
    
    # Build body
    body = f"""AssetPipe Pipeline Report
========================

Status: {'Failed' if result.error_count > 0 else 'Completed'}
Processed: {result.success_count}
Failed: {result.error_count}
Warnings: {result.warning_count}
"""
    
    if result.errors:
        body += "\nErrors:\n"
        for error in result.errors:
            body += f"  • {error}\n"
    
    if result.warnings:
        body += "\nWarnings:\n"
        for warning in result.warnings:
            body += f"  • {warning}\n"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        if use_tls:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
        
        if username and password:
            server.login(username, password)
        
        server.sendmail(from_addr, to_addrs, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False
