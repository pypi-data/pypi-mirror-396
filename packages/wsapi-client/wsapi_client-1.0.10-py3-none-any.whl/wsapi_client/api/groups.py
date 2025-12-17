from __future__ import annotations
from typing import List, Optional
from ..http import WSApiHttp, ApiResponse
from ..models.entities.groups.group_info import GroupInfo
from ..models.entities.groups.group_created import GroupCreated
from ..models.entities.groups.group_picture_updated import GroupPictureUpdated
from ..models.entities.groups.group_invite_info import GroupInviteInfo
from ..models.entities.groups.group_invite_link import GroupInviteLink
from ..models.entities.groups.group_join_request import GroupJoinRequest
from ..models.entities.groups.group_joined import GroupJoined
from ..models.requests.groups.group_create_request import GroupCreateRequest
from ..models.requests.groups.group_update_description_request import GroupUpdateDescriptionRequest
from ..models.requests.groups.group_update_name_request import GroupUpdateNameRequest
from ..models.requests.groups.group_update_picture_request import GroupUpdatePictureRequest
from ..models.requests.groups.group_update_participants_request import GroupUpdateParticipantsRequest
from ..models.requests.groups.group_set_announce_request import GroupSetAnnounceRequest
from ..models.requests.groups.group_set_locked_request import GroupSetLockedRequest
from ..models.requests.groups.group_set_join_approval_request import GroupSetJoinApprovalRequest
from ..models.requests.groups.group_set_member_add_mode_request import GroupSetMemberAddModeRequest
from ..models.requests.groups.group_join_with_link_request import GroupJoinWithLinkRequest
from ..models.requests.groups.group_join_with_invite_request import GroupJoinWithInviteRequest
from ..models.requests.groups.group_update_requests_request import GroupUpdateRequestsRequest


class GroupsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def list(self) -> list[GroupInfo]:
        return self._http.send_json("GET", "/groups", model=list[GroupInfo])

    def get(self, group_id: str) -> GroupInfo:
        return self._http.send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def create(self, request: GroupCreateRequest) -> GroupCreated:
        return self._http.send_json("POST", "/groups", model=GroupCreated, json=request.model_dump(by_alias=True))

    def update_description(self, group_id: str, request: GroupUpdateDescriptionRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/description", model=None, json=request.model_dump(by_alias=True))

    def update_name(self, group_id: str, request: GroupUpdateNameRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/name", model=None, json=request.model_dump(by_alias=True))

    def update_picture(self, group_id: str, request: GroupUpdatePictureRequest) -> GroupPictureUpdated:
        return self._http.send_json("POST", f"/groups/{group_id}/picture", model=GroupPictureUpdated, json=request.model_dump(by_alias=True))

    def leave(self, group_id: str) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/leave", model=None)

    def delete(self, group_id: str) -> None:
        """Alias for leave() - leaves the group."""
        self.leave(group_id)

    def get_invite_link(self, group_id: str, reset: bool = False) -> GroupInviteLink:
        url = f"/groups/{group_id}/invite-link"
        if reset:
            url += "?reset=1"
        return self._http.send_json("GET", url, model=GroupInviteLink)

    def get_requests(self, group_id: str) -> List[GroupJoinRequest]:
        return self._http.send_json("GET", f"/groups/{group_id}/requests", model=list[GroupJoinRequest])

    def update_requests(self, group_id: str, request: GroupUpdateRequestsRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/requests", model=None, json=request.model_dump(by_alias=True))

    def update_participants(self, group_id: str, request: GroupUpdateParticipantsRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/participants", model=None, json=request.model_dump(by_alias=True))

    def set_announce(self, group_id: str, request: GroupSetAnnounceRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/announce", model=None, json=request.model_dump(by_alias=True))

    def set_locked(self, group_id: str, request: GroupSetLockedRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/locked", model=None, json=request.model_dump(by_alias=True))

    def set_join_approval(self, group_id: str, request: GroupSetJoinApprovalRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/join-approval", model=None, json=request.model_dump(by_alias=True))

    def set_member_add_mode(self, group_id: str, request: GroupSetMemberAddModeRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/member-add-mode", model=None, json=request.model_dump(by_alias=True))

    def join_with_link(self, request: GroupJoinWithLinkRequest) -> GroupJoined:
        return self._http.send_json("POST", "/groups/join/link", model=GroupJoined, json=request.model_dump(by_alias=True))

    def join_with_invite(self, request: GroupJoinWithInviteRequest) -> GroupJoined:
        return self._http.send_json("POST", "/groups/join/invite", model=GroupJoined, json=request.model_dump(by_alias=True))

    def get_invite_info(self, invite_code: str) -> GroupInviteInfo:
        return self._http.send_json("GET", f"/groups/invite/{invite_code}", model=GroupInviteInfo)

    # Try variants
    def try_list(self) -> ApiResponse[list[GroupInfo]]:
        return self._http.try_send_json("GET", "/groups", model=list[GroupInfo])

    def try_get(self, group_id: str) -> ApiResponse[GroupInfo]:
        return self._http.try_send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def try_create(self, request: GroupCreateRequest) -> ApiResponse[GroupCreated]:
        return self._http.try_send_json("POST", "/groups", model=GroupCreated, json=request.model_dump(by_alias=True))

    def try_update_description(self, group_id: str, request: GroupUpdateDescriptionRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/description", model=None, json=request.model_dump(by_alias=True))

    def try_update_name(self, group_id: str, request: GroupUpdateNameRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/name", model=None, json=request.model_dump(by_alias=True))

    def try_update_picture(self, group_id: str, request: GroupUpdatePictureRequest) -> ApiResponse[GroupPictureUpdated]:
        return self._http.try_send_json("POST", f"/groups/{group_id}/picture", model=GroupPictureUpdated, json=request.model_dump(by_alias=True))

    def try_leave(self, group_id: str) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/leave", model=None)

    def try_delete(self, group_id: str) -> ApiResponse[None]:
        """Alias for try_leave() - leaves the group."""
        return self.try_leave(group_id)

    def try_get_invite_link(self, group_id: str, reset: bool = False) -> ApiResponse[GroupInviteLink]:
        url = f"/groups/{group_id}/invite-link"
        if reset:
            url += "?reset=1"
        return self._http.try_send_json("GET", url, model=GroupInviteLink)

    def try_get_requests(self, group_id: str) -> ApiResponse[List[GroupJoinRequest]]:
        return self._http.try_send_json("GET", f"/groups/{group_id}/requests", model=list[GroupJoinRequest])

    def try_update_requests(self, group_id: str, request: GroupUpdateRequestsRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/requests", model=None, json=request.model_dump(by_alias=True))

    def try_update_participants(self, group_id: str, request: GroupUpdateParticipantsRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/participants", model=None, json=request.model_dump(by_alias=True))

    def try_set_announce(self, group_id: str, request: GroupSetAnnounceRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/announce", model=None, json=request.model_dump(by_alias=True))

    def try_set_locked(self, group_id: str, request: GroupSetLockedRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/locked", model=None, json=request.model_dump(by_alias=True))

    def try_set_join_approval(self, group_id: str, request: GroupSetJoinApprovalRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/join-approval", model=None, json=request.model_dump(by_alias=True))

    def try_set_member_add_mode(self, group_id: str, request: GroupSetMemberAddModeRequest) -> ApiResponse[None]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/member-add-mode", model=None, json=request.model_dump(by_alias=True))

    def try_join_with_link(self, request: GroupJoinWithLinkRequest) -> ApiResponse[GroupJoined]:
        return self._http.try_send_json("POST", "/groups/join/link", model=GroupJoined, json=request.model_dump(by_alias=True))

    def try_join_with_invite(self, request: GroupJoinWithInviteRequest) -> ApiResponse[GroupJoined]:
        return self._http.try_send_json("POST", "/groups/join/invite", model=GroupJoined, json=request.model_dump(by_alias=True))

    def try_get_invite_info(self, invite_code: str) -> ApiResponse[GroupInviteInfo]:
        return self._http.try_send_json("GET", f"/groups/invite/{invite_code}", model=GroupInviteInfo)
