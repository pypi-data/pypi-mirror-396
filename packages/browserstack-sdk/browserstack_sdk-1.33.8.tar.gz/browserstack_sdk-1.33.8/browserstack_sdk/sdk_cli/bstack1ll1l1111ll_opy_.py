# coding: UTF-8
import sys
bstack11111l_opy_ = sys.version_info [0] == 2
bstack111llll_opy_ = 2048
bstack111lll1_opy_ = 7
def bstack1ll111_opy_ (bstack11l_opy_):
    global bstack1l11_opy_
    bstack1111l11_opy_ = ord (bstack11l_opy_ [-1])
    bstack11l1l11_opy_ = bstack11l_opy_ [:-1]
    bstack111111_opy_ = bstack1111l11_opy_ % len (bstack11l1l11_opy_)
    bstack11ll11l_opy_ = bstack11l1l11_opy_ [:bstack111111_opy_] + bstack11l1l11_opy_ [bstack111111_opy_:]
    if bstack11111l_opy_:
        bstack11ll11_opy_ = unicode () .join ([unichr (ord (char) - bstack111llll_opy_ - (bstack11llll_opy_ + bstack1111l11_opy_) % bstack111lll1_opy_) for bstack11llll_opy_, char in enumerate (bstack11ll11l_opy_)])
    else:
        bstack11ll11_opy_ = str () .join ([chr (ord (char) - bstack111llll_opy_ - (bstack11llll_opy_ + bstack1111l11_opy_) % bstack111lll1_opy_) for bstack11llll_opy_, char in enumerate (bstack11ll11l_opy_)])
    return eval (bstack11ll11_opy_)
import os
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1lll1l_opy_,
    bstack1lllll11111_opy_,
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
from bstack_utils.constants import EVENTS
class bstack1lll11l11ll_opy_(bstack1llll1lll1l_opy_):
    bstack1l111l1l1l1_opy_ = bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠣᗚ")
    NAME = bstack1ll111_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᗛ")
    bstack1l11lll1111_opy_ = bstack1ll111_opy_ (u"ࠥ࡬ࡺࡨ࡟ࡶࡴ࡯ࠦᗜ")
    bstack1l11ll1lll1_opy_ = bstack1ll111_opy_ (u"ࠦ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠦᗝ")
    bstack11lll11llll_opy_ = bstack1ll111_opy_ (u"ࠧ࡯࡮ࡱࡷࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᗞ")
    bstack1l11lll1l1l_opy_ = bstack1ll111_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᗟ")
    bstack1l111ll11ll_opy_ = bstack1ll111_opy_ (u"ࠢࡪࡵࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡ࡫ࡹࡧࠨᗠ")
    bstack11lll11l11l_opy_ = bstack1ll111_opy_ (u"ࠣࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠧᗡ")
    bstack11lll11lll1_opy_ = bstack1ll111_opy_ (u"ࠤࡨࡲࡩ࡫ࡤࡠࡣࡷࠦᗢ")
    bstack1ll11ll1111_opy_ = bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࠦᗣ")
    bstack1l11l11ll11_opy_ = bstack1ll111_opy_ (u"ࠦࡳ࡫ࡷࡴࡧࡶࡷ࡮ࡵ࡮ࠣᗤ")
    bstack11lll11l1ll_opy_ = bstack1ll111_opy_ (u"ࠧ࡭ࡥࡵࠤᗥ")
    bstack1l1l11llll1_opy_ = bstack1ll111_opy_ (u"ࠨࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠥᗦ")
    bstack1l111l1ll11_opy_ = bstack1ll111_opy_ (u"ࠢࡸ࠵ࡦࡩࡽ࡫ࡣࡶࡶࡨࡷࡨࡸࡩࡱࡶࠥᗧ")
    bstack1l111ll1111_opy_ = bstack1ll111_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࡥࡸࡿ࡮ࡤࠤᗨ")
    bstack11lll111lll_opy_ = bstack1ll111_opy_ (u"ࠤࡴࡹ࡮ࡺࠢᗩ")
    bstack11lll11ll11_opy_: Dict[str, List[Callable]] = dict()
    bstack1l11l1ll1ll_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1ll1ll1l11l_opy_: Any
    bstack1l111l1l1ll_opy_: Dict
    def __init__(
        self,
        bstack1l11l1ll1ll_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1ll1ll1l11l_opy_: Dict[str, Any],
        methods=[bstack1ll111_opy_ (u"ࠥࡣࡤ࡯࡮ࡪࡶࡢࡣࠧᗪ"), bstack1ll111_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࠦᗫ"), bstack1ll111_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᗬ"), bstack1ll111_opy_ (u"ࠨࡱࡶ࡫ࡷࠦᗭ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l11l1ll1ll_opy_ = bstack1l11l1ll1ll_opy_
        self.platform_index = platform_index
        self.bstack1llll1l1l11_opy_(methods)
        self.bstack1ll1ll1l11l_opy_ = bstack1ll1ll1l11l_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1llll1lll1l_opy_.get_data(bstack1lll11l11ll_opy_.bstack1l11ll1lll1_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1llll1lll1l_opy_.get_data(bstack1lll11l11ll_opy_.bstack1l11lll1111_opy_, target, strict)
    @staticmethod
    def bstack11lll11l1l1_opy_(target: object, strict=True):
        return bstack1llll1lll1l_opy_.get_data(bstack1lll11l11ll_opy_.bstack11lll11llll_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1llll1lll1l_opy_.get_data(bstack1lll11l11ll_opy_.bstack1l11lll1l1l_opy_, target, strict)
    @staticmethod
    def bstack1l1lll1111l_opy_(instance: bstack1lllll11111_opy_) -> bool:
        return bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1l111ll11ll_opy_, False)
    @staticmethod
    def bstack1ll111l11l1_opy_(instance: bstack1lllll11111_opy_, default_value=None):
        return bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1l11lll1111_opy_, default_value)
    @staticmethod
    def bstack1l1llll1l1l_opy_(instance: bstack1lllll11111_opy_, default_value=None):
        return bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1l11lll1l1l_opy_, default_value)
    @staticmethod
    def bstack1l1lll1ll11_opy_(hub_url: str, bstack11lll11ll1l_opy_=bstack1ll111_opy_ (u"ࠢ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠦᗮ")):
        try:
            bstack11lll11l111_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack11lll11l111_opy_.endswith(bstack11lll11ll1l_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll111ll111_opy_(method_name: str):
        return method_name == bstack1ll111_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᗯ")
    @staticmethod
    def bstack1ll1111lll1_opy_(method_name: str, *args):
        return (
            bstack1lll11l11ll_opy_.bstack1ll111ll111_opy_(method_name)
            and bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args) == bstack1lll11l11ll_opy_.bstack1l11l11ll11_opy_
        )
    @staticmethod
    def bstack1ll111111ll_opy_(method_name: str, *args):
        if not bstack1lll11l11ll_opy_.bstack1ll111ll111_opy_(method_name):
            return False
        if not bstack1lll11l11ll_opy_.bstack1l111l1ll11_opy_ in bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args):
            return False
        bstack1l1lll111ll_opy_ = bstack1lll11l11ll_opy_.bstack1l1lll1l1l1_opy_(*args)
        return bstack1l1lll111ll_opy_ and bstack1ll111_opy_ (u"ࠤࡶࡧࡷ࡯ࡰࡵࠤᗰ") in bstack1l1lll111ll_opy_ and bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᗱ") in bstack1l1lll111ll_opy_[bstack1ll111_opy_ (u"ࠦࡸࡩࡲࡪࡲࡷࠦᗲ")]
    @staticmethod
    def bstack1ll1111l11l_opy_(method_name: str, *args):
        if not bstack1lll11l11ll_opy_.bstack1ll111ll111_opy_(method_name):
            return False
        if not bstack1lll11l11ll_opy_.bstack1l111l1ll11_opy_ in bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args):
            return False
        bstack1l1lll111ll_opy_ = bstack1lll11l11ll_opy_.bstack1l1lll1l1l1_opy_(*args)
        return (
            bstack1l1lll111ll_opy_
            and bstack1ll111_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᗳ") in bstack1l1lll111ll_opy_
            and bstack1ll111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡧࡷ࡯ࡰࡵࠤᗴ") in bstack1l1lll111ll_opy_[bstack1ll111_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᗵ")]
        )
    @staticmethod
    def bstack1l11l11l1l1_opy_(*args):
        return str(bstack1lll11l11ll_opy_.bstack1ll111l1111_opy_(*args)).lower()
    @staticmethod
    def bstack1ll111l1111_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1lll1l1l1_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack111111lll_opy_(driver):
        command_executor = getattr(driver, bstack1ll111_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᗶ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack1ll111_opy_ (u"ࠤࡢࡹࡷࡲࠢᗷ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack1ll111_opy_ (u"ࠥࡣࡨࡲࡩࡦࡰࡷࡣࡨࡵ࡮ࡧ࡫ࡪࠦᗸ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack1ll111_opy_ (u"ࠦࡷ࡫࡭ࡰࡶࡨࡣࡸ࡫ࡲࡷࡧࡵࡣࡦࡪࡤࡳࠤᗹ"), None)
        return hub_url
    def bstack1l11l11ll1l_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack1ll111_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᗺ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᗻ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack1ll111_opy_ (u"ࠢࡠࡷࡵࡰࠧᗼ")):
                setattr(command_executor, bstack1ll111_opy_ (u"ࠣࡡࡸࡶࡱࠨᗽ"), hub_url)
                result = True
        if result:
            self.bstack1l11l1ll1ll_opy_ = hub_url
            bstack1lll11l11ll_opy_.bstack1llll11l11l_opy_(instance, bstack1lll11l11ll_opy_.bstack1l11lll1111_opy_, hub_url)
            bstack1lll11l11ll_opy_.bstack1llll11l11l_opy_(
                instance, bstack1lll11l11ll_opy_.bstack1l111ll11ll_opy_, bstack1lll11l11ll_opy_.bstack1l1lll1ll11_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_]):
        return bstack1ll111_opy_ (u"ࠤ࠽ࠦᗾ").join((bstack1llll1l1111_opy_(bstack1llll11ll1l_opy_[0]).name, bstack1lllll11l11_opy_(bstack1llll11ll1l_opy_[1]).name))
    @staticmethod
    def bstack1l1llll111l_opy_(bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_], callback: Callable):
        bstack1l111l1lll1_opy_ = bstack1lll11l11ll_opy_.bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_)
        if not bstack1l111l1lll1_opy_ in bstack1lll11l11ll_opy_.bstack11lll11ll11_opy_:
            bstack1lll11l11ll_opy_.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_] = []
        bstack1lll11l11ll_opy_.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_].append(callback)
    def bstack1llll111l1l_opy_(self, instance: bstack1lllll11111_opy_, method_name: str, bstack1lllll1l1l1_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack1ll111_opy_ (u"ࠥࡷࡹࡧࡲࡵࡡࡶࡩࡸࡹࡩࡰࡰࠥᗿ")):
            return
        cmd = args[0] if method_name == bstack1ll111_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧᘀ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack11lll1l1111_opy_ = bstack1ll111_opy_ (u"ࠧࡀࠢᘁ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠢᘂ") + bstack11lll1l1111_opy_, bstack1lllll1l1l1_opy_)
    def bstack1llll11llll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll1l1lll_opy_, bstack1l111l1llll_opy_ = bstack1llll11ll1l_opy_
        bstack1l111l1lll1_opy_ = bstack1lll11l11ll_opy_.bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠢࡰࡰࡢ࡬ࡴࡵ࡫࠻ࠢࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫࠽ࡼ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࢃࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᘃ") + str(kwargs) + bstack1ll111_opy_ (u"ࠣࠤᘄ"))
        if bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.QUIT:
            if bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.PRE:
                bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1l1l11l1l_opy_.value)
                bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, EVENTS.bstack1l1l11l1l_opy_.value, bstack1ll111lllll_opy_)
                self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀࢃࠠ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࡂࢁࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠨᘅ").format(instance, method_name, bstack1llll1l1lll_opy_, bstack1l111l1llll_opy_))
        if bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.bstack1llll11ll11_opy_:
            if bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.POST and not bstack1lll11l11ll_opy_.bstack1l11ll1lll1_opy_ in instance.data:
                session_id = getattr(target, bstack1ll111_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᘆ"), None)
                if session_id:
                    instance.data[bstack1lll11l11ll_opy_.bstack1l11ll1lll1_opy_] = session_id
        elif (
            bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.bstack1lllll1111l_opy_
            and bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args) == bstack1lll11l11ll_opy_.bstack1l11l11ll11_opy_
        ):
            if bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.PRE:
                hub_url = bstack1lll11l11ll_opy_.bstack111111lll_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1lll11l11ll_opy_.bstack1l11lll1111_opy_: hub_url,
                            bstack1lll11l11ll_opy_.bstack1l111ll11ll_opy_: bstack1lll11l11ll_opy_.bstack1l1lll1ll11_opy_(hub_url),
                            bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_: int(
                                os.environ.get(bstack1ll111_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦᘇ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1l1lll111ll_opy_ = bstack1lll11l11ll_opy_.bstack1l1lll1l1l1_opy_(*args)
                bstack11lll11l1l1_opy_ = bstack1l1lll111ll_opy_.get(bstack1ll111_opy_ (u"ࠧࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᘈ"), None) if bstack1l1lll111ll_opy_ else None
                if isinstance(bstack11lll11l1l1_opy_, dict):
                    instance.data[bstack1lll11l11ll_opy_.bstack11lll11llll_opy_] = copy.deepcopy(bstack11lll11l1l1_opy_)
                    instance.data[bstack1lll11l11ll_opy_.bstack1l11lll1l1l_opy_] = bstack11lll11l1l1_opy_
            elif bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack1ll111_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧᘉ"), dict()).get(bstack1ll111_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥᘊ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1lll11l11ll_opy_.bstack1l11ll1lll1_opy_: framework_session_id,
                                bstack1lll11l11ll_opy_.bstack11lll11l11l_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.bstack1lllll1111l_opy_
            and bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args) == bstack1lll11l11ll_opy_.bstack11lll111lll_opy_
            and bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.POST
        ):
            instance.data[bstack1lll11l11ll_opy_.bstack11lll11lll1_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l111l1lll1_opy_ in bstack1lll11l11ll_opy_.bstack11lll11ll11_opy_:
            bstack1l111l1ll1l_opy_ = None
            for callback in bstack1lll11l11ll_opy_.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_]:
                try:
                    bstack1l111ll111l_opy_ = callback(self, target, exec, bstack1llll11ll1l_opy_, result, *args, **kwargs)
                    if bstack1l111l1ll1l_opy_ == None:
                        bstack1l111l1ll1l_opy_ = bstack1l111ll111l_opy_
                except Exception as e:
                    self.logger.error(bstack1ll111_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࠨᘋ") + str(e) + bstack1ll111_opy_ (u"ࠤࠥᘌ"))
                    traceback.print_exc()
            if bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.QUIT:
                if bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.POST:
                    bstack1ll111lllll_opy_ = bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, EVENTS.bstack1l1l11l1l_opy_.value)
                    if bstack1ll111lllll_opy_!=None:
                        bstack1ll1ll111ll_opy_.end(EVENTS.bstack1l1l11l1l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᘍ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᘎ"), True, None)
            if bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.PRE and callable(bstack1l111l1ll1l_opy_):
                return bstack1l111l1ll1l_opy_
            elif bstack1l111l1llll_opy_ == bstack1lllll11l11_opy_.POST and bstack1l111l1ll1l_opy_:
                return bstack1l111l1ll1l_opy_
    def bstack1llll111lll_opy_(
        self, method_name, previous_state: bstack1llll1l1111_opy_, *args, **kwargs
    ) -> bstack1llll1l1111_opy_:
        if method_name == bstack1ll111_opy_ (u"ࠧࡥ࡟ࡪࡰ࡬ࡸࡤࡥࠢᘏ") or method_name == bstack1ll111_opy_ (u"ࠨࡳࡵࡣࡵࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᘐ"):
            return bstack1llll1l1111_opy_.bstack1llll11ll11_opy_
        if method_name == bstack1ll111_opy_ (u"ࠢࡲࡷ࡬ࡸࠧᘑ"):
            return bstack1llll1l1111_opy_.QUIT
        if method_name == bstack1ll111_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᘒ"):
            if previous_state != bstack1llll1l1111_opy_.NONE:
                command_name = bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args)
                if command_name == bstack1lll11l11ll_opy_.bstack1l11l11ll11_opy_:
                    return bstack1llll1l1111_opy_.bstack1llll11ll11_opy_
            return bstack1llll1l1111_opy_.bstack1lllll1111l_opy_
        return bstack1llll1l1111_opy_.NONE