from datetime import datetime, timedelta, timezone
from typing import Sequence

from fastapi import Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..data.models import Telemetry
from ..data.repositories import DeviceRepository, TelemetryRepository
from .base_router import BaseRouter


class TelemetryRouter(BaseRouter):
    def __init__(self, repo: TelemetryRepository = None) -> None:
        self.repo : TelemetryRepository = repo or TelemetryRepository()

        super().__init__(Telemetry, self.repo, '/api/v1/telemetry', ['telemetry'])

    def _setup_routes(self) -> None:
        @self.router.get('/recent', response_model=Sequence[Telemetry])
        async def list_recent(response: Response, session: AsyncSession = Depends(BaseRouter._get_session), offset: int = Query(..., min=0)) -> Sequence[Telemetry]:
            from_date   = datetime.now(timezone.utc) - timedelta(seconds=offset)
            device_repo = DeviceRepository()
            # pylint: disable=no-member
            devices     = await device_repo.list(session)
            results     = []

            for device in devices:
                capabilities = device.capabilities.split(',') if device.capabilities else []
                for data_type in capabilities:
                    if not data_type.startswith('action_'):
                        telemetry = await self.repo.get_latest_for_device(session, device.id, data_type)
                        if telemetry:
                            if telemetry.timestamp.tzinfo is None:
                                telemetry.timestamp = telemetry.timestamp.replace(tzinfo=timezone.utc)

                            if telemetry.timestamp >= from_date:
                                results.append(telemetry)

            response.headers['X-Total-Count'] = str(len(results))

            results.sort(key=lambda result: result.timestamp, reverse=True)

            return results

        super()._setup_routes()
