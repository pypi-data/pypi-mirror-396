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
import json
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1lllll11111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11111l1l_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
class bstack1ll1l1l11ll_opy_(bstack1ll1ll1l1l1_opy_):
    bstack1l11l111lll_opy_ = bstack1ll111_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤ࡯࡮ࡪࡶࠥᏈ")
    bstack1l11l1ll1l1_opy_ = bstack1ll111_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡳࡵࡣࡵࡸࠧᏉ")
    bstack1l11l1l1l11_opy_ = bstack1ll111_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡲࡴࠧᏊ")
    def __init__(self, bstack1lll1ll11l1_opy_):
        super().__init__()
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1llll11ll11_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11l1111ll_opy_)
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l1lll11l11_opy_)
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.POST), self.bstack1l11l11llll_opy_)
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.POST), self.bstack1l11l1l111l_opy_)
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.QUIT, bstack1lllll11l11_opy_.POST), self.bstack1l11l1l11l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1111ll_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣᏋ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack1ll111_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥᏌ")), str):
                    url = kwargs.get(bstack1ll111_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᏍ"))
                elif hasattr(kwargs.get(bstack1ll111_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᏎ")), bstack1ll111_opy_ (u"ࠪࡣࡨࡲࡩࡦࡰࡷࡣࡨࡵ࡮ࡧ࡫ࡪࠫᏏ")):
                    url = kwargs.get(bstack1ll111_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᏐ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack1ll111_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᏑ"))._url
            except Exception as e:
                url = bstack1ll111_opy_ (u"࠭ࠧᏒ")
                self.logger.error(bstack1ll111_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡵࡳ࡮ࠣࡪࡷࡵ࡭ࠡࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾࢁࠧᏓ").format(e))
            self.logger.info(bstack1ll111_opy_ (u"ࠣࡔࡨࡱࡴࡺࡥࠡࡕࡨࡶࡻ࡫ࡲࠡࡃࡧࡨࡷ࡫ࡳࡴࠢࡥࡩ࡮ࡴࡧࠡࡲࡤࡷࡸ࡫ࡤࠡࡣࡶࠤ࠿ࠦࡻࡾࠤᏔ").format(str(url)))
            self.bstack1l11l1111l1_opy_(instance, url, f, kwargs)
            self.logger.info(bstack1ll111_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥࡾࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࡿࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࢂࡀࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁ࡫ࡸࡣࡵ࡫ࡸࢃࠢᏕ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1l1lll11l11_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1llll11l1ll_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l111lll_opy_, False):
            return
        if not f.bstack1llll11lll1_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_):
            return
        platform_index = f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_)
        if f.bstack1ll1111lll1_opy_(method_name, *args) and len(args) > 1:
            bstack111ll1ll1_opy_ = datetime.now()
            hub_url = bstack1lll11l11ll_opy_.hub_url(driver)
            self.logger.warning(bstack1ll111_opy_ (u"ࠥ࡬ࡺࡨ࡟ࡶࡴ࡯ࡁࠧᏖ") + str(hub_url) + bstack1ll111_opy_ (u"ࠦࠧᏗ"))
            bstack1l11l1l1111_opy_ = args[1][bstack1ll111_opy_ (u"ࠧࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᏘ")] if isinstance(args[1], dict) and bstack1ll111_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᏙ") in args[1] else None
            bstack1l11l11l11l_opy_ = bstack1ll111_opy_ (u"ࠢࡢ࡮ࡺࡥࡾࡹࡍࡢࡶࡦ࡬ࠧᏚ")
            if isinstance(bstack1l11l1l1111_opy_, dict):
                bstack111ll1ll1_opy_ = datetime.now()
                r = self.bstack1l11l11111l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠ࡫ࡱ࡭ࡹࠨᏛ"), datetime.now() - bstack111ll1ll1_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack1ll111_opy_ (u"ࠤࡶࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨ࠼ࠣࠦᏜ") + str(r) + bstack1ll111_opy_ (u"ࠥࠦᏝ"))
                        return
                    if r.hub_url:
                        f.bstack1l11l11ll1l_opy_(instance, driver, r.hub_url)
                        f.bstack1llll11l11l_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l111lll_opy_, True)
                except Exception as e:
                    self.logger.error(bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥᏞ"), e)
    def bstack1l11l11llll_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1lll11l11ll_opy_.session_id(driver)
            if session_id:
                bstack1l11l11lll1_opy_ = bstack1ll111_opy_ (u"ࠧࢁࡽ࠻ࡵࡷࡥࡷࡺࠢᏟ").format(session_id)
                bstack1ll1ll111ll_opy_.mark(bstack1l11l11lll1_opy_)
    def bstack1l11l1l111l_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llll11l1ll_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l1ll1l1_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1lll11l11ll_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack1ll111_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡪࡸࡦࡤࡻࡲ࡭࠿ࠥᏠ") + str(hub_url) + bstack1ll111_opy_ (u"ࠢࠣᏡ"))
            return
        framework_session_id = bstack1lll11l11ll_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࡀࠦᏢ") + str(framework_session_id) + bstack1ll111_opy_ (u"ࠤࠥᏣ"))
            return
        if bstack1lll11l11ll_opy_.bstack1l11l11l1l1_opy_(*args) == bstack1lll11l11ll_opy_.bstack1l11l11ll11_opy_:
            bstack1l11l1ll11l_opy_ = bstack1ll111_opy_ (u"ࠥࡿࢂࡀࡥ࡯ࡦࠥᏤ").format(framework_session_id)
            bstack1l11l11lll1_opy_ = bstack1ll111_opy_ (u"ࠦࢀࢃ࠺ࡴࡶࡤࡶࡹࠨᏥ").format(framework_session_id)
            bstack1ll1ll111ll_opy_.end(
                label=bstack1ll111_opy_ (u"ࠧࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳ࠼ࡳࡳࡸࡺ࠭ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠣᏦ"),
                start=bstack1l11l11lll1_opy_,
                end=bstack1l11l1ll11l_opy_,
                status=True,
                failure=None
            )
            bstack111ll1ll1_opy_ = datetime.now()
            r = self.bstack1l11l111l11_opy_(
                ref,
                f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡳࡵࡣࡵࡸࠧᏧ"), datetime.now() - bstack111ll1ll1_opy_)
            f.bstack1llll11l11l_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l1ll1l1_opy_, r.success)
    def bstack1l11l1l11l1_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llll11l1ll_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l1l1l11_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1lll11l11ll_opy_.session_id(driver)
        hub_url = bstack1lll11l11ll_opy_.hub_url(driver)
        bstack111ll1ll1_opy_ = datetime.now()
        r = self.bstack1l11l111ll1_opy_(
            ref,
            f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡲࡴࠧᏨ"), datetime.now() - bstack111ll1ll1_opy_)
        f.bstack1llll11l11l_opy_(instance, bstack1ll1l1l11ll_opy_.bstack1l11l1l1l11_opy_, r.success)
    @measure(event_name=EVENTS.bstack11lll11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l11llll11l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢࡻࡪࡨࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯࡫ࡷ࠾ࠥࠨᏩ") + str(req) + bstack1ll111_opy_ (u"ࠤࠥᏪ"))
        try:
            r = self.bstack1lll1l11lll_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࡸࡻࡣࡤࡧࡶࡷࡂࠨᏫ") + str(r.success) + bstack1ll111_opy_ (u"ࠦࠧᏬ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᏭ") + str(e) + bstack1ll111_opy_ (u"ࠨࠢᏮ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1l11ll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l11l11111l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack1ll111_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤᏯ") + str(req) + bstack1ll111_opy_ (u"ࠣࠤᏰ"))
        try:
            r = self.bstack1lll1l11lll_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࡷࡺࡩࡣࡦࡵࡶࡁࠧᏱ") + str(r.success) + bstack1ll111_opy_ (u"ࠥࠦᏲ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᏳ") + str(e) + bstack1ll111_opy_ (u"ࠧࠨᏴ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1l1l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l11l111l11_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1ll111_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡥࡷࡺ࠺ࠡࠤᏵ") + str(req) + bstack1ll111_opy_ (u"ࠢࠣ᏶"))
        try:
            r = self.bstack1lll1l11lll_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥ᏷") + str(r) + bstack1ll111_opy_ (u"ࠤࠥᏸ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᏹ") + str(e) + bstack1ll111_opy_ (u"ࠦࠧᏺ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1l1ll1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l11l111ll1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1ll111_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡲࡴ࠿ࠦࠢᏻ") + str(req) + bstack1ll111_opy_ (u"ࠨࠢᏼ"))
        try:
            r = self.bstack1lll1l11lll_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤᏽ") + str(r) + bstack1ll111_opy_ (u"ࠣࠤ᏾"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢ᏿") + str(e) + bstack1ll111_opy_ (u"ࠥࠦ᐀"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11lll1l1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l11l1111l1_opy_(self, instance: bstack1lllll11111_opy_, url: str, f: bstack1lll11l11ll_opy_, kwargs):
        bstack1l11l11l1ll_opy_ = version.parse(f.framework_version)
        bstack1l11l111l1l_opy_ = kwargs.get(bstack1ll111_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᐁ"))
        bstack1l11l11l111_opy_ = kwargs.get(bstack1ll111_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᐂ"))
        bstack1l1l1111111_opy_ = {}
        bstack1l11l1ll111_opy_ = {}
        bstack1l11l1l1lll_opy_ = None
        bstack1l11l111111_opy_ = {}
        if bstack1l11l11l111_opy_ is not None or bstack1l11l111l1l_opy_ is not None: # check top level caps
            if bstack1l11l11l111_opy_ is not None:
                bstack1l11l111111_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ᐃ")] = bstack1l11l11l111_opy_
            if bstack1l11l111l1l_opy_ is not None and callable(getattr(bstack1l11l111l1l_opy_, bstack1ll111_opy_ (u"ࠢࡵࡱࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᐄ"))):
                bstack1l11l111111_opy_[bstack1ll111_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࡡࡤࡷࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫᐅ")] = bstack1l11l111l1l_opy_.to_capabilities()
        response = self.bstack1l11llll11l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11l111111_opy_).encode(bstack1ll111_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᐆ")))
        if response is not None and response.capabilities:
            bstack1l1l1111111_opy_ = json.loads(response.capabilities.decode(bstack1ll111_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᐇ")))
            if not bstack1l1l1111111_opy_: # empty caps bstack1l11lll111l_opy_ bstack1l11lll1l11_opy_ bstack1l11llll111_opy_ bstack1ll1llll11l_opy_ or error in processing
                return
            bstack1l11l1l1lll_opy_ = f.bstack1ll1ll1l11l_opy_[bstack1ll111_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡣࡴࡶࡴࡪࡱࡱࡷࡤ࡬ࡲࡰ࡯ࡢࡧࡦࡶࡳࠣᐈ")](bstack1l1l1111111_opy_)
        if bstack1l11l111l1l_opy_ is not None and bstack1l11l11l1ll_opy_ >= version.parse(bstack1ll111_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫᐉ")):
            bstack1l11l1ll111_opy_ = None
        if (
                not bstack1l11l111l1l_opy_ and not bstack1l11l11l111_opy_
        ) or (
                bstack1l11l11l1ll_opy_ < version.parse(bstack1ll111_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬᐊ"))
        ):
            bstack1l11l1ll111_opy_ = {}
            bstack1l11l1ll111_opy_.update(bstack1l1l1111111_opy_)
        self.logger.info(bstack11111l1l_opy_)
        if os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠥᐋ")).lower().__eq__(bstack1ll111_opy_ (u"ࠣࡶࡵࡹࡪࠨᐌ")):
            kwargs.update(
                {
                    bstack1ll111_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᐍ"): f.bstack1l11l1ll1ll_opy_,
                }
            )
        if bstack1l11l11l1ll_opy_ >= version.parse(bstack1ll111_opy_ (u"ࠪ࠸࠳࠷࠰࠯࠲ࠪᐎ")):
            if bstack1l11l11l111_opy_ is not None:
                del kwargs[bstack1ll111_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᐏ")]
            kwargs.update(
                {
                    bstack1ll111_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᐐ"): bstack1l11l1l1lll_opy_,
                    bstack1ll111_opy_ (u"ࠨ࡫ࡦࡧࡳࡣࡦࡲࡩࡷࡧࠥᐑ"): True,
                    bstack1ll111_opy_ (u"ࠢࡧ࡫࡯ࡩࡤࡪࡥࡵࡧࡦࡸࡴࡸࠢᐒ"): None,
                }
            )
        elif bstack1l11l11l1ll_opy_ >= version.parse(bstack1ll111_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧᐓ")):
            kwargs.update(
                {
                    bstack1ll111_opy_ (u"ࠤࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᐔ"): bstack1l11l1ll111_opy_,
                    bstack1ll111_opy_ (u"ࠥࡳࡵࡺࡩࡰࡰࡶࠦᐕ"): bstack1l11l1l1lll_opy_,
                    bstack1ll111_opy_ (u"ࠦࡰ࡫ࡥࡱࡡࡤࡰ࡮ࡼࡥࠣᐖ"): True,
                    bstack1ll111_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡢࡨࡪࡺࡥࡤࡶࡲࡶࠧᐗ"): None,
                }
            )
        elif bstack1l11l11l1ll_opy_ >= version.parse(bstack1ll111_opy_ (u"࠭࠲࠯࠷࠶࠲࠵࠭ᐘ")):
            kwargs.update(
                {
                    bstack1ll111_opy_ (u"ࠢࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᐙ"): bstack1l11l1ll111_opy_,
                    bstack1ll111_opy_ (u"ࠣ࡭ࡨࡩࡵࡥࡡ࡭࡫ࡹࡩࠧᐚ"): True,
                    bstack1ll111_opy_ (u"ࠤࡩ࡭ࡱ࡫࡟ࡥࡧࡷࡩࡨࡺ࡯ࡳࠤᐛ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack1ll111_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᐜ"): bstack1l11l1ll111_opy_,
                    bstack1ll111_opy_ (u"ࠦࡰ࡫ࡥࡱࡡࡤࡰ࡮ࡼࡥࠣᐝ"): True,
                    bstack1ll111_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡢࡨࡪࡺࡥࡤࡶࡲࡶࠧᐞ"): None,
                }
            )