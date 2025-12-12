# broker/factory.py


def get_broker():
    from ..config import TasksRunnerSettings
    setting = TasksRunnerSettings()

    if setting.BROKER_TYPE == "none":
        return None
    elif setting.BROKER_TYPE == "local":
        from .local import LocalBroker
        return LocalBroker()
    elif setting.BROKER_TYPE == "memory":
        from .memory import InMemoryBroker
        return InMemoryBroker()
    elif setting.BROKER_TYPE == "rabbitmq":
        from .rabbitmq import RabbitMQBroker
        rabbitmq_url = getattr(setting, "BROKER_DSN", None)
        if not rabbitmq_url:
            raise ValueError("BROKER_DSN must be set when BROKER_TYPE='rabbitmq'")
        return RabbitMQBroker(rabbitmq_url=rabbitmq_url)
    elif setting.BROKER_TYPE == "postgres":
        from .postgres import PostgresBroker
        # Database URL is resolved by the broker via fastpluggy.core.database
        return PostgresBroker()
    else:
        raise ValueError(f"Unsupported broker scheme: {setting.BROKER_TYPE}")
