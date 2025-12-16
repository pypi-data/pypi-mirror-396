import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class AudioProcess:
    id: int
    status: str
    audio_url: str
    created_at: datetime

@strawberry.type
class Query:
    @strawberry.field
    async def get_process(self, id: int) -> Optional[AudioProcess]:
        # For testing, return mock data
        return AudioProcess(
            id=id,
            status="completed",
            audio_url="https://example.com/audio/123",
            created_at=datetime.now()
        )

    @strawberry.field
    async def list_processes(self) -> List[AudioProcess]:
        # For testing, return mock data
        return [
            AudioProcess(
                id=1,
                status="completed",
                audio_url="https://example.com/audio/123",
                created_at=datetime.now()
            )
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def process_audio(self, file: str) -> AudioProcess:
        # For testing, return mock data
        return AudioProcess(
            id=1,
            status="processing",
            audio_url="",
            created_at=datetime.now()
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)