import rapidsms
from rapidsms.apps.base import AppBase
class App (AppBase):
    def handle (self, message):
        # We fall to this app when xform fails to match message
        if message.connection.contact.healthproviderbase:
            message.respond("Thank you for your message. We have forwarded to your DHT for follow-up. If this was meant to be a weekly report, please check and resend.")
            return True
        return False

