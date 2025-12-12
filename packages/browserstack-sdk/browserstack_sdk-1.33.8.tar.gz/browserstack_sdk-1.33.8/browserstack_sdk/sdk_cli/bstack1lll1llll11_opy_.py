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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1lllll11111_opy_,
)
from bstack_utils.helper import  bstack11111l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l1lll1_opy_, bstack1ll1l1ll1ll_opy_, bstack1lll1l1llll_opy_, bstack1ll1ll1llll_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1l11ll1l1_opy_ import bstack1ll111l111_opy_
from browserstack_sdk.sdk_cli.bstack1lll11111l1_opy_ import bstack1lll11lll1l_opy_
from bstack_utils.percy import bstack11lllll11_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1ll1l111111_opy_(bstack1ll1ll1l1l1_opy_):
    def __init__(self, bstack1l1l111l1ll_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1l111l1ll_opy_ = bstack1l1l111l1ll_opy_
        self.percy = bstack11lllll11_opy_()
        self.bstack11111ll1l_opy_ = bstack1ll111l111_opy_()
        self.bstack1l1l111l1l1_opy_()
        bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l1l111ll11_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST), self.bstack1ll11l111l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll11l1l1_opy_(self, instance: bstack1lllll11111_opy_, driver: object):
        bstack1l1l1llll11_opy_ = TestFramework.bstack1llll11111l_opy_(instance.context)
        for t in bstack1l1l1llll11_opy_:
            bstack1l1l11ll111_opy_ = TestFramework.bstack1llll11l1ll_opy_(t, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
            if any(instance is d[1] for d in bstack1l1l11ll111_opy_) or instance == driver:
                return t
    def bstack1l1l111ll11_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1lll11l11ll_opy_.bstack1ll111ll111_opy_(method_name):
                return
            platform_index = f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0)
            bstack1l1ll111l11_opy_ = self.bstack1l1ll11l1l1_opy_(instance, driver)
            bstack1l1l1111ll1_opy_ = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1l1l111111l_opy_, None)
            if not bstack1l1l1111ll1_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡰࡰࡢࡴࡷ࡫࡟ࡦࡺࡨࡧࡺࡺࡥ࠻ࠢࡵࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥࡧࡳࠡࡵࡨࡷࡸ࡯࡯࡯ࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡼࡩࡹࠦࡳࡵࡣࡵࡸࡪࡪࠢጹ"))
                return
            driver_command = f.bstack1ll111l1111_opy_(*args)
            for command in bstack1ll1l11l11_opy_:
                if command == driver_command:
                    self.bstack11lll11l1_opy_(driver, platform_index)
            bstack11ll1111_opy_ = self.percy.bstack1ll1l1lll1_opy_()
            if driver_command in bstack1llll11ll1_opy_[bstack11ll1111_opy_]:
                self.bstack11111ll1l_opy_.bstack1l1ll1ll_opy_(bstack1l1l1111ll1_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠣࡱࡱࡣࡵࡸࡥࡠࡧࡻࡩࡨࡻࡴࡦ࠼ࠣࡩࡷࡸ࡯ࡳࠤጺ"), e)
    def bstack1ll11l111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
        bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦጻ") + str(kwargs) + bstack1ll111_opy_ (u"ࠥࠦጼ"))
            return
        if len(bstack1l1l11ll111_opy_) > 1:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࢁ࡬ࡦࡰࠫࡨࡷ࡯ࡶࡦࡴࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨጽ") + str(kwargs) + bstack1ll111_opy_ (u"ࠧࠨጾ"))
        bstack1l1l1111lll_opy_, bstack1l1l1111l11_opy_ = bstack1l1l11ll111_opy_[0]
        driver = bstack1l1l1111lll_opy_()
        if not driver:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡶࡨࡷࡹࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢጿ") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣፀ"))
            return
        bstack1l1l11111ll_opy_ = {
            TestFramework.bstack1l1llll11l1_opy_: bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࠦ࡮ࡢ࡯ࡨࠦፁ"),
            TestFramework.bstack1ll11l111ll_opy_: bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺࠠࡶࡷ࡬ࡨࠧፂ"),
            TestFramework.bstack1l1l111111l_opy_: bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࠡࡴࡨࡶࡺࡴࠠ࡯ࡣࡰࡩࠧፃ")
        }
        bstack1l1l11111l1_opy_ = { key: f.bstack1llll11l1ll_opy_(instance, key) for key in bstack1l1l11111ll_opy_ }
        bstack1l1l111l11l_opy_ = [key for key, value in bstack1l1l11111l1_opy_.items() if not value]
        if bstack1l1l111l11l_opy_:
            for key in bstack1l1l111l11l_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࠢፄ") + str(key) + bstack1ll111_opy_ (u"ࠧࠨፅ"))
            return
        platform_index = f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0)
        if self.bstack1l1l111l1ll_opy_.percy_capture_mode == bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣፆ"):
            bstack1l11l1l1l1_opy_ = bstack1l1l11111l1_opy_.get(TestFramework.bstack1l1l111111l_opy_) + bstack1ll111_opy_ (u"ࠢ࠮ࡶࡨࡷࡹࡩࡡࡴࡧࠥፇ")
            bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1l1l111ll1l_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack1l11l1l1l1_opy_,
                bstack11lllll1l1_opy_=bstack1l1l11111l1_opy_[TestFramework.bstack1l1llll11l1_opy_],
                bstack1ll11l11l_opy_=bstack1l1l11111l1_opy_[TestFramework.bstack1ll11l111ll_opy_],
                bstack1lllll111_opy_=platform_index
            )
            bstack1ll1ll111ll_opy_.end(EVENTS.bstack1l1l111ll1l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣፈ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠤ࠽ࡩࡳࡪࠢፉ"), True, None, None, None, None, test_name=bstack1l11l1l1l1_opy_)
    def bstack11lll11l1_opy_(self, driver, platform_index):
        if self.bstack11111ll1l_opy_.bstack1l1llllll1_opy_() is True or self.bstack11111ll1l_opy_.capturing() is True:
            return
        self.bstack11111ll1l_opy_.bstack1lll1l111l_opy_()
        while not self.bstack11111ll1l_opy_.bstack1l1llllll1_opy_():
            bstack1l1l1111ll1_opy_ = self.bstack11111ll1l_opy_.bstack1l1ll1lll1_opy_()
            self.bstack1l1l1lll1l_opy_(driver, bstack1l1l1111ll1_opy_, platform_index)
        self.bstack11111ll1l_opy_.bstack1l111l111_opy_()
    def bstack1l1l1lll1l_opy_(self, driver, bstack1l1l11ll11_opy_, platform_index, test=None):
        from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
        bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack111l11lll_opy_.value)
        if test != None:
            bstack11lllll1l1_opy_ = getattr(test, bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨፊ"), None)
            bstack1ll11l11l_opy_ = getattr(test, bstack1ll111_opy_ (u"ࠫࡺࡻࡩࡥࠩፋ"), None)
            PercySDK.screenshot(driver, bstack1l1l11ll11_opy_, bstack11lllll1l1_opy_=bstack11lllll1l1_opy_, bstack1ll11l11l_opy_=bstack1ll11l11l_opy_, bstack1lllll111_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1l1l11ll11_opy_)
        bstack1ll1ll111ll_opy_.end(EVENTS.bstack111l11lll_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧፌ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠨ࠺ࡦࡰࡧࠦፍ"), True, None, None, None, None, test_name=bstack1l1l11ll11_opy_)
    def bstack1l1l111l1l1_opy_(self):
        os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬፎ")] = str(self.bstack1l1l111l1ll_opy_.success)
        os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞ࡥࡃࡂࡒࡗ࡙ࡗࡋ࡟ࡎࡑࡇࡉࠬፏ")] = str(self.bstack1l1l111l1ll_opy_.percy_capture_mode)
        self.percy.bstack1l1l1111l1l_opy_(self.bstack1l1l111l1ll_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1l111l111_opy_(self.bstack1l1l111l1ll_opy_.percy_build_id)