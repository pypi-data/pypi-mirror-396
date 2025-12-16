from uuid import uuid4
from shared_kernel.config import Config
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.logger import Logger
from shared_kernel.messaging import DataBusFactory
from shared_kernel.traceability.traceability_handler import Traceability

config = Config()
logger = Logger(config.get("APP_NAME"))

class AIChatPersistence:
    def __init__(self, session_token: str, name_space: str, org_id=None, user_id=None,  payload={}):
        self.session_token = session_token
        self.user_id = user_id
        if not self.session_token:
            raise ValueError("Session token is required")
        self.org_id = org_id
        trace_payload = {
            "title": f"AI Chat Session",
            "description": f"Chat Session for org_id: {self.org_id}",
            "organization_id": self.org_id,
            "execution_status": "Queued",
        }
        trace_obj = Traceability(payload=trace_payload)
        trace_obj.create()
        self.trace_id = trace_obj.trace_id
        self.data_bus: DataBus = DataBusFactory.create_data_bus(
            bus_type=config.get("ASYNC_EVENT_BUS_TYPE"),
            config={},
        )
        self.name_space = name_space
    def publish_event(self, data: dict):
        self.data_bus.publish_event(event_name=data.get(
            "event_name"), event_payload=data)
        return True

    
    def save_message(self, message: str, role: str, message_type: str = None):
        save_msg_payload = {
            "event_name": "SAVE_CHAT_MESSAGE",
            "event_payload": {
                "session_id": self.session_token,
                "role": role,
                "message_type": message_type,
                "message": message,
                "name_space": self.name_space
            },
           "event_meta": {
               "trace_id": self.trace_id,
               "org_id": self.org_id,
               "user_id": self.user_id
           }
        }
        self.publish_event(save_msg_payload)
        logger.info(f"chat saved successfully")

    