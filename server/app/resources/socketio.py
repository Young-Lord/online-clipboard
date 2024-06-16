from typing import Required, TypedDict
from flask import current_app
from flask_socketio import SocketIO, join_room, leave_room, emit, Namespace

socketio = SocketIO(
    cors_allowed_origins=current_app.config["CORS_ORIGINS"],
    path=current_app.config["WEBSOCKET_PATH_FOR_SERVER"],
)


class WebSocketPacket(TypedDict, total=False):
    name: Required[str]
    authorization: Required[str]
    client_id: Required[str]
    data: Required[dict]


def get_room(data: WebSocketPacket) -> str:
    return "sync_room_" + data["name"] + data["authorization"]


instant_sync_namespace_name = "/instant_sync"


class InstantSyncNamespace(Namespace):
    def is_room_exist(self, name: str) -> bool:
        # WARNING: This is a private method, and is supposed to change.
        return name in socketio.server.manager.rooms[instant_sync_namespace_name]  # type: ignore

    def on_join(self, data):
        room = get_room(data)
        if not self.is_room_exist(room):
            emit("enable_save")
        join_room(room)

    def on_leave(self, data):
        leave_room(get_room(data))

    def on_diff(self, data):
        emit(
            "diff",
            {"data": data["data"], "client_id": data["client_id"]},
            broadcast=True,
            to=get_room(data),
        )


socketio.on_namespace(InstantSyncNamespace(instant_sync_namespace_name))
