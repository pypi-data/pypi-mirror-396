from racerapi.core.decorators import Controller, Get, Post, Put, Delete
from .service import SystemService
from .schema import (
    SystemCreate,
    SystemUpdate,
    SystemOut,
)


@Controller("system")
class SystemController:
    """
    System HTTP Controller
    Handles transport-level concerns only.
    """

    def __init__(self):
        self.service = SystemService()

    # ----------------------------
    # LIST
    # GET /system
    # ----------------------------
    @Get("/")
    async def list(self) -> list[SystemOut]:
        return await self.service.list()

    # ----------------------------
    # GET BY ID
    # GET /system/{id}
    # ----------------------------
    @Get("/{id}")
    async def get(self, id: int) -> SystemOut:
        return await self.service.get(id)

    # ----------------------------
    # CREATE
    # POST /system
    # ----------------------------
    @Post("/")
    async def create(self, payload: SystemCreate) -> SystemOut:
        return await self.service.create(payload)

    # ----------------------------
    # UPDATE
    # PUT /system/{id}
    # ----------------------------
    @Put("/{id}")
    async def update(
        self,
        id: int,
        payload: SystemUpdate,
    ) -> SystemOut:
        return await self.service.update(id, payload)

    # ----------------------------
    # DELETE
    # DELETE /system/{id}
    # ----------------------------
    @Delete("/{id}")
    async def delete(self, id: int) -> None:
        await self.service.delete(id)