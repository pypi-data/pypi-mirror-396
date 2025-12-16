from typing import List
import strawberry
from fastyr.services.interfaces.pipeline_service import PipelineService
from fastyr.domain.models.audio_process import AudioProcess
from fastyr.core.contracts.auth import AuthData

@strawberry.type
class AudioProcessResolver:
    @strawberry.field
    async def get_process(self, id: int, info) -> AudioProcess:
        service = info.context["pipeline_service"]
        auth = info.context["auth"]
        return await service.get_by_id(id, auth)
    
    @strawberry.field
    async def list_processes(
        self,
        info,
        page: int = 1,
        limit: int = 10
    ) -> List[AudioProcess]:
        service = info.context["pipeline_service"]
        auth = info.context["auth"]
        return await service.get_all(page, limit, auth)
    
    @strawberry.mutation
    async def process_audio(
        self,
        info,
        file: strawberry.Upload
    ) -> AudioProcess:
        service = info.context["pipeline_service"]
        auth = info.context["auth"]
        audio_data = await file.read()
        return await service.process(audio_data, auth) 