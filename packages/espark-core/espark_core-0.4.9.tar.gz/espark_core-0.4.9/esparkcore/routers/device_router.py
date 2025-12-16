from json import dumps
from os import getenv

from aiomqtt import Client
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import ENV_MQTT_HOST, ENV_MQTT_PORT, TOPIC_DEVICE
from ..data.models import Device
from ..data.repositories import DeviceRepository
from ..utils import log_debug
from .base_router import BaseRouter


class DeviceRouter(BaseRouter):
    def __init__(self, repo: DeviceRepository = None) -> None:
        self.repo : DeviceRepository = repo or DeviceRepository()

        super().__init__(Device, self.repo, '/api/v1/devices', ['device'])

    async def _publish_update(self, entity: Device) -> None:
        log_debug(f'Publishing parameters update for device {entity.id}: {entity.parameters}')

        async with Client(getenv(ENV_MQTT_HOST, 'localhost'), int(getenv(ENV_MQTT_PORT, '1883'))) as client:
            await client.publish(f'{TOPIC_DEVICE}/{entity.id}', payload=dumps(entity.parameters) if entity.parameters else None, qos=1, retain=True)

    async def _after_update(self, entity: Device, session: AsyncSession) -> None:
        await super()._after_update(entity, session)

        await self._publish_update(entity)
