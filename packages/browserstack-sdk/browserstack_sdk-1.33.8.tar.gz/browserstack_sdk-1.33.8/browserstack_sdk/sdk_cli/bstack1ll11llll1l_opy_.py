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
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1lllll11111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from typing import Tuple, Callable, Any
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import traceback
import os
import time
class bstack1ll1ll1lll1_opy_(bstack1ll1ll1l1l1_opy_):
    bstack1ll111ll1ll_opy_ = False
    def __init__(self):
        super().__init__()
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l1lll11l11_opy_)
    def is_enabled(self) -> bool:
        return True
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
        hub_url = f.hub_url(driver)
        if f.bstack1l1lll1ll11_opy_(hub_url):
            if not bstack1ll1ll1lll1_opy_.bstack1ll111ll1ll_opy_:
                self.logger.warning(bstack1ll111_opy_ (u"ࠣ࡮ࡲࡧࡦࡲࠠࡴࡧ࡯ࡪ࠲࡮ࡥࡢ࡮ࠣࡪࡱࡵࡷࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡩ࡯ࡨࡵࡥࠥࡹࡥࡴࡵ࡬ࡳࡳࡹࠠࡩࡷࡥࡣࡺࡸ࡬࠾ࠤኄ") + str(hub_url) + bstack1ll111_opy_ (u"ࠤࠥኅ"))
                bstack1ll1ll1lll1_opy_.bstack1ll111ll1ll_opy_ = True
            return
        command_name = f.bstack1ll111l1111_opy_(*args)
        bstack1l1lll111ll_opy_ = f.bstack1l1lll1l1l1_opy_(*args)
        if command_name and command_name.lower() == bstack1ll111_opy_ (u"ࠥࡪ࡮ࡴࡤࡦ࡮ࡨࡱࡪࡴࡴࠣኆ") and bstack1l1lll111ll_opy_:
            framework_session_id = f.session_id(driver)
            locator_type, locator_value = bstack1l1lll111ll_opy_.get(bstack1ll111_opy_ (u"ࠦࡺࡹࡩ࡯ࡩࠥኇ"), None), bstack1l1lll111ll_opy_.get(bstack1ll111_opy_ (u"ࠧࡼࡡ࡭ࡷࡨࠦኈ"), None)
            if not framework_session_id or not locator_type or not locator_value:
                self.logger.warning(bstack1ll111_opy_ (u"ࠨࡻࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࢃ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠢࡲࡶࠥࡧࡲࡨࡵ࠱ࡹࡸ࡯࡮ࡨ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡹࡿࡰࡦࡿࠣࡳࡷࠦࡡࡳࡩࡶ࠲ࡻࡧ࡬ࡶࡧࡀࠦ኉") + str(locator_value) + bstack1ll111_opy_ (u"ࠢࠣኊ"))
                return
            def bstack1lllll11l1l_opy_(driver, bstack1l1lll1l11l_opy_, *args, **kwargs):
                from selenium.common.exceptions import NoSuchElementException
                try:
                    result = bstack1l1lll1l11l_opy_(driver, *args, **kwargs)
                    response = self.bstack1l1lll1l1ll_opy_(
                        framework_session_id=framework_session_id,
                        is_success=True,
                        locator_type=locator_type,
                        locator_value=locator_value,
                    )
                    if response and response.execute_script:
                        driver.execute_script(response.execute_script)
                        self.logger.info(bstack1ll111_opy_ (u"ࠣࡵࡸࡧࡨ࡫ࡳࡴ࠯ࡶࡧࡷ࡯ࡰࡵ࠼ࠣࡰࡴࡩࡡࡵࡱࡵࡣࡹࡿࡰࡦ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡹࡿࡰࡦࡿࠣࡰࡴࡩࡡࡵࡱࡵࡣࡻࡧ࡬ࡶࡧࡀࠦኋ") + str(locator_value) + bstack1ll111_opy_ (u"ࠤࠥኌ"))
                    else:
                        self.logger.warning(bstack1ll111_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶ࠱ࡳࡵ࠭ࡴࡥࡵ࡭ࡵࡺ࠺ࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫࠽ࡼ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡷࡽࡵ࡫ࡽࠡ࡮ࡲࡧࡦࡺ࡯ࡳࡡࡹࡥࡱࡻࡥ࠾ࡽ࡯ࡳࡨࡧࡴࡰࡴࡢࡺࡦࡲࡵࡦࡿࠣࡶࡪࡹࡰࡰࡰࡶࡩࡂࠨኍ") + str(response) + bstack1ll111_opy_ (u"ࠦࠧ኎"))
                    return result
                except NoSuchElementException as e:
                    locator = (locator_type, locator_value)
                    return self.__1l1lll1l111_opy_(
                        driver, bstack1l1lll1l11l_opy_, e, framework_session_id, locator, *args, **kwargs
                    )
            bstack1lllll11l1l_opy_.__name__ = command_name
            return bstack1lllll11l1l_opy_
    def __1l1lll1l111_opy_(
        self,
        driver,
        bstack1l1lll1l11l_opy_: Callable,
        exception,
        framework_session_id: str,
        locator: Tuple[str, str],
        *args,
        **kwargs,
    ):
        try:
            locator_type, locator_value = locator
            response = self.bstack1l1lll1l1ll_opy_(
                framework_session_id=framework_session_id,
                is_success=False,
                locator_type=locator_type,
                locator_value=locator_value,
            )
            if response and response.execute_script:
                driver.execute_script(response.execute_script)
                self.logger.info(bstack1ll111_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡸࡶࡪ࠳ࡨࡦࡣ࡯࡭ࡳ࡭࠭ࡵࡴ࡬࡫࡬࡫ࡲࡦࡦ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࠧ኏") + str(locator_value) + bstack1ll111_opy_ (u"ࠨࠢነ"))
                bstack1l1lll11lll_opy_ = self.bstack1l1lll11ll1_opy_(
                    framework_session_id=framework_session_id,
                    locator_type=locator_type,
                )
                self.logger.info(bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡺࡸࡥ࠮ࡪࡨࡥࡱ࡯࡮ࡨ࠯ࡵࡩࡸࡻ࡬ࡵ࠼ࠣࡰࡴࡩࡡࡵࡱࡵࡣࡹࡿࡰࡦ࠿ࡾࡰࡴࡩࡡࡵࡱࡵࡣࡹࡿࡰࡦࡿࠣࡰࡴࡩࡡࡵࡱࡵࡣࡻࡧ࡬ࡶࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࢁࠥ࡮ࡥࡢ࡮࡬ࡲ࡬ࡥࡲࡦࡵࡸࡰࡹࡃࠢኑ") + str(bstack1l1lll11lll_opy_) + bstack1ll111_opy_ (u"ࠣࠤኒ"))
                if bstack1l1lll11lll_opy_.success and args and len(args) > 1:
                    args[1].update(
                        {
                            bstack1ll111_opy_ (u"ࠤࡸࡷ࡮ࡴࡧࠣና"): bstack1l1lll11lll_opy_.locator_type,
                            bstack1ll111_opy_ (u"ࠥࡺࡦࡲࡵࡦࠤኔ"): bstack1l1lll11lll_opy_.locator_value,
                        }
                    )
                    return bstack1l1lll1l11l_opy_(driver, *args, **kwargs)
                elif os.environ.get(bstack1ll111_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡎࡥࡄࡆࡄࡘࡋࠧን"), False):
                    self.logger.info(bstack1lll11ll11l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡸࡶࡪ࠳ࡨࡦࡣ࡯࡭ࡳ࡭࠭ࡳࡧࡶࡹࡱࡺ࠭࡮࡫ࡶࡷ࡮ࡴࡧ࠻ࠢࡶࡰࡪ࡫ࡰࠩ࠵࠳࠭ࠥࡲࡥࡵࡶ࡬ࡲ࡬ࠦࡹࡰࡷࠣ࡭ࡳࡹࡰࡦࡥࡷࠤࡹ࡮ࡥࠡࡤࡵࡳࡼࡹࡥࡳࠢࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࠥࡲ࡯ࡨࡵࠥኖ"))
                    time.sleep(300)
            else:
                self.logger.warning(bstack1ll111_opy_ (u"ࠨࡦࡢ࡫࡯ࡹࡷ࡫࠭࡯ࡱ࠰ࡷࡨࡸࡩࡱࡶ࠽ࠤࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࡀࡿࡱࡵࡣࡢࡶࡲࡶࡤࡺࡹࡱࡧࢀࠤࡱࡵࡣࡢࡶࡲࡶࡤࡼࡡ࡭ࡷࡨࡁࢀࡲ࡯ࡤࡣࡷࡳࡷࡥࡶࡢ࡮ࡸࡩࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠾ࠤኗ") + str(response) + bstack1ll111_opy_ (u"ࠢࠣኘ"))
        except Exception as err:
            self.logger.warning(bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱࡻࡲࡦ࠯࡫ࡩࡦࡲࡩ࡯ࡩ࠰ࡶࡪࡹࡵ࡭ࡶ࠽ࠤࡪࡸࡲࡰࡴ࠽ࠤࠧኙ") + str(err) + bstack1ll111_opy_ (u"ࠤࠥኚ"))
        raise exception
    @measure(event_name=EVENTS.bstack1l1lll1ll1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l1lll1l1ll_opy_(
        self,
        framework_session_id: str,
        is_success: bool,
        locator_type: str,
        locator_value: str,
        platform_index=bstack1ll111_opy_ (u"ࠥ࠴ࠧኛ"),
    ):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AISelfHealStepRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.is_success = is_success
        req.test_name = bstack1ll111_opy_ (u"ࠦࠧኜ")
        req.locator_type = locator_type
        req.locator_value = locator_value
        try:
            r = self.bstack1lll1l11lll_opy_.AISelfHealStep(req)
            self.logger.info(bstack1ll111_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢኝ") + str(r) + bstack1ll111_opy_ (u"ࠨࠢኞ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧኟ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤአ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1lll11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1l1lll11ll1_opy_(self, framework_session_id: str, locator_type: str, platform_index=bstack1ll111_opy_ (u"ࠤ࠳ࠦኡ")):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AISelfHealGetRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_session_id = framework_session_id
        req.locator_type = locator_type
        try:
            r = self.bstack1lll1l11lll_opy_.AISelfHealGetResult(req)
            self.logger.info(bstack1ll111_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧኢ") + str(r) + bstack1ll111_opy_ (u"ࠦࠧኣ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥኤ") + str(e) + bstack1ll111_opy_ (u"ࠨࠢእ"))
            traceback.print_exc()
            raise e