"""Notification service.

SMTP credentials now come from config/env — they used to be hardcoded
(`email_password = 'senha123'`). Uses the logging module instead of `print`.
"""
import logging
import smtplib

from src.config.settings import settings

logger = logging.getLogger("taskmanager.notifications")


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.user or not self.password:
            logger.info("SMTP not configured; skipping email to %s (%s)", to, subject)
            return False
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to, f"Subject: {subject}\n\n{body}")
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as e:  # narrow logging, no crash of the request path
            logger.error("Erro ao enviar email: %s", e)
            return False

    def notify_task_assigned(self, user, task):
        self.send_email(
            user.email,
            f"Nova task atribuída: {task.title}",
            f"Olá {user.name}, a task '{task.title}' foi atribuída a você.",
        )
