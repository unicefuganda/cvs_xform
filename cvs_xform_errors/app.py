from rapidsms.apps.base import AppBase
from rapidsms.models import Connection
from script.models import ScriptProgress
from healthmodels.models.HealthProvider import HealthProvider
from rapidsms_httprouter.models import Message


class App (AppBase):
    def handle(self, message):
        # We fall to this app when xform fails to match message
        # Also added here is a special chat group to share messages
        # between members belonging to the same health facility
        groups = []
        mentions = []
        for token in message.text.split():
            if token.startswith("#"):
                groups.append(token[1:])
            if token.startswith("@"):
                mentions.append(token[1:])
        groups = [i.lower() for i in groups]
        mentions = [i.lower() for i in mentions]
        if 'chat' in groups or 'chat' in mentions:
            sender = HealthProvider.objects.filter(connection=message.connection)
            recipients = []
            if sender:
                sender = sender[0]
                facility = sender.facility
                if facility:
                    recipients = HealthProvider.objects.filter(
                        facility=sender.facility).exclude(connection__identity=None)
                    recipients = recipients.exclude(connection=sender.default_connection)
                    text = "{0}: {1}".format(sender.default_connection.identity, message.text)
                    sender_text = "sent to {0} members of {1}".format(
                        len(recipients), sender.facility)
                    conns = Connection.objects.filter(contact__in=recipients)
                    if conns:
                        Message.mass_text(text, conns, status='Q', batch_status='Q')
                        message.respond(sender_text)
                        return True

        if message.connection.contact and not ScriptProgress.objects.filter(connection=message.connection).exists():
            if message.connection.contact.healthproviderbase:
                message.respond("Thank you for your message. We have forwarded to your DHT for follow-up. If this was meant to be a weekly report, please check and resend.")
                return True
        return False
