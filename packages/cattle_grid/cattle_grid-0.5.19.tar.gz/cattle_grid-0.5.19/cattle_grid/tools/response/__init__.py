from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated
from bovine.activitystreams.utils import as_list
from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse

from cattle_grid.activity_pub.actor.requester import (
    ActorNotFound,
    is_valid_requester_for_obj,
)

from cattle_grid.dependencies.fastapi import SqlSession
from cattle_grid.tools.fastapi import ActivityPubHeaders, ShouldServe, ContentType


def get_html_link(obj: dict) -> str | None:
    urls = as_list(obj.get("url", []))
    for x in urls:
        if x is None:
            continue
        if isinstance(x, str):
            return x
        if x.get("mediaType").startswith("text/html"):
            return x.get("href")


@dataclass
class ActivityPubResponderClass:
    session: SqlSession
    ap_headers: ActivityPubHeaders
    should_serve: ShouldServe

    def _handle_non_activity_pub(self, obj):
        if ContentType.html in self.should_serve:
            link = get_html_link(obj)
            if link:
                return RedirectResponse(link)
        raise HTTPException(406)

    async def __call__(
        self, obj: dict, parent: dict | None = None
    ) -> dict | RedirectResponse:
        if ContentType.activity_pub not in self.should_serve:
            return self._handle_non_activity_pub(obj)

        if not self.ap_headers.x_cattle_grid_requester:
            raise HTTPException(401)

        if self.ap_headers.x_ap_location != obj.get("id"):
            raise HTTPException(404)

        try:
            if not await is_valid_requester_for_obj(
                self.session,
                self.ap_headers.x_cattle_grid_requester,
                parent if parent else obj,
            ):
                raise HTTPException(401)
        except ActorNotFound:
            raise HTTPException(status_code=410, detail="Activity no longer available")

        return obj


ActivityPubResponder = Annotated[
    Callable[..., Awaitable[dict]], Depends(ActivityPubResponderClass)
]
