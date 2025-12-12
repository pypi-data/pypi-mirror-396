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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1llll1llll1_opy_ import bstack1llll1l11ll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11l1l11l_opy_ import bstack11llll111l1_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll1l1lll1_opy_,
    bstack1ll1l1ll1ll_opy_,
    bstack1lll1l1llll_opy_,
    bstack1l1111l1111_opy_,
    bstack1ll1ll1llll_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1ll11l1ll_opy_
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1111l_opy_ import bstack1lll11l1l11_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1llll_opy_ import bstack1llllll111l_opy_
bstack1l1l1lllll1_opy_ = bstack1l1ll11l1ll_opy_()
bstack1l1l1llll1l_opy_ = bstack1ll111_opy_ (u"࡙ࠥࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠯ࠥᒌ")
bstack1l1111l11ll_opy_ = bstack1ll111_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᒍ")
bstack11llll1lll1_opy_ = bstack1ll111_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᒎ")
bstack11llll11lll_opy_ = 1.0
_1l1ll1l11l1_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l11111111l_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᒏ")
    bstack1l1111lll1l_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࠧᒐ")
    bstack1l1111l1l11_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᒑ")
    bstack11lllll11ll_opy_ = bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࠦᒒ")
    bstack1l11111l1l1_opy_ = bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᒓ")
    bstack1l11111llll_opy_: bool
    bstack1lllll1llll_opy_: bstack1llllll111l_opy_  = None
    bstack1l111111l1l_opy_ = [
        bstack1lll1l1lll1_opy_.BEFORE_ALL,
        bstack1lll1l1lll1_opy_.AFTER_ALL,
        bstack1lll1l1lll1_opy_.BEFORE_EACH,
        bstack1lll1l1lll1_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lll1llll1_opy_: Dict[str, str],
        bstack1l1llllll11_opy_: List[str]=[bstack1ll111_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᒔ")],
        bstack1lllll1llll_opy_: bstack1llllll111l_opy_ = None,
        bstack1lll1l11lll_opy_=None
    ):
        super().__init__(bstack1l1llllll11_opy_, bstack11lll1llll1_opy_, bstack1lllll1llll_opy_)
        self.bstack1l11111llll_opy_ = any(bstack1ll111_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᒕ") in item.lower() for item in bstack1l1llllll11_opy_)
        self.bstack1lll1l11lll_opy_ = bstack1lll1l11lll_opy_
    def track_event(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1lll1l1lll1_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1l111111l1l_opy_:
            bstack11llll111l1_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll1l1lll1_opy_.NONE:
            self.logger.warning(bstack1ll111_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡪࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࠢᒖ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠢࠣᒗ"))
            return
        if not self.bstack1l11111llll_opy_:
            self.logger.warning(bstack1ll111_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠾ࠤᒘ") + str(str(self.bstack1l1llllll11_opy_)) + bstack1ll111_opy_ (u"ࠤࠥᒙ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1ll111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᒚ") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧᒛ"))
            return
        instance = self.__1l111111ll1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1ll111_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡧࡲࡨࡵࡀࠦᒜ") + str(args) + bstack1ll111_opy_ (u"ࠨࠢᒝ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111111l1l_opy_ and test_hook_state == bstack1lll1l1llll_opy_.PRE:
                bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1l1lll111l_opy_.value)
                name = str(EVENTS.bstack1l1lll111l_opy_.name)+bstack1ll111_opy_ (u"ࠢ࠻ࠤᒞ")+str(test_framework_state.name)
                TestFramework.bstack11llllll1ll_opy_(instance, name, bstack1ll111lllll_opy_)
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵࠤࡵࡸࡥ࠻ࠢࡾࢁࠧᒟ").format(e))
        try:
            if test_framework_state == bstack1lll1l1lll1_opy_.TEST:
                if not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack11lllll1l11_opy_) and test_hook_state == bstack1lll1l1llll_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__1l1111lll11_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡯ࡳࡦࡪࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᒠ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠥࠦᒡ"))
                if test_hook_state == bstack1lll1l1llll_opy_.PRE and not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack1l1l111lll1_opy_):
                    TestFramework.bstack1llll11l11l_opy_(instance, TestFramework.bstack1l1l111lll1_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__11llll11l1l_opy_(instance, args)
                    self.logger.debug(bstack1ll111_opy_ (u"ࠦࡸ࡫ࡴࠡࡶࡨࡷࡹ࠳ࡳࡵࡣࡵࡸࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᒢ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠧࠨᒣ"))
                elif test_hook_state == bstack1lll1l1llll_opy_.POST and not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack1l1ll1l1l11_opy_):
                    TestFramework.bstack1llll11l11l_opy_(instance, TestFramework.bstack1l1ll1l1l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1ll111_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡧࡱࡨࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᒤ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠢࠣᒥ"))
            elif test_framework_state == bstack1lll1l1lll1_opy_.STEP:
                if test_hook_state == bstack1lll1l1llll_opy_.PRE:
                    PytestBDDFramework.__11lllllllll_opy_(instance, args)
                elif test_hook_state == bstack1lll1l1llll_opy_.POST:
                    PytestBDDFramework.__11lll1ll1ll_opy_(instance, args)
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG and test_hook_state == bstack1lll1l1llll_opy_.POST:
                PytestBDDFramework.__11lllll1ll1_opy_(instance, *args)
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG_REPORT and test_hook_state == bstack1lll1l1llll_opy_.POST:
                self.__11llll11l11_opy_(instance, *args)
                self.__1l1111l1ll1_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1l111111l1l_opy_:
                self.__1l1111l111l_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᒦ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠤࠥᒧ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llll1l1ll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111111l1l_opy_ and test_hook_state == bstack1lll1l1llll_opy_.POST:
                name = str(EVENTS.bstack1l1lll111l_opy_.name)+bstack1ll111_opy_ (u"ࠥ࠾ࠧᒨ")+str(test_framework_state.name)
                bstack1ll111lllll_opy_ = TestFramework.bstack1l1111ll1ll_opy_(instance, name)
                bstack1ll1ll111ll_opy_.end(EVENTS.bstack1l1lll111l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᒩ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᒪ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᒫ").format(e))
    def bstack1l1l1ll1ll1_opy_(self):
        return self.bstack1l11111llll_opy_
    def __1l1111l11l1_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᒬ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l11l11l1_opy_(rep, [bstack1ll111_opy_ (u"ࠣࡹ࡫ࡩࡳࠨᒭ"), bstack1ll111_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᒮ"), bstack1ll111_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥᒯ"), bstack1ll111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᒰ"), bstack1ll111_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠨᒱ"), bstack1ll111_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧᒲ")])
        return None
    def __11llll11l11_opy_(self, instance: bstack1ll1l1ll1ll_opy_, *args):
        result = self.__1l1111l11l1_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll1l11_opy_ = None
        if result.get(bstack1ll111_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᒳ"), None) == bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᒴ") and len(args) > 1 and getattr(args[1], bstack1ll111_opy_ (u"ࠤࡨࡼࡨ࡯࡮ࡧࡱࠥᒵ"), None) is not None:
            failure = [{bstack1ll111_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᒶ"): [args[1].excinfo.exconly(), result.get(bstack1ll111_opy_ (u"ࠦࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠥᒷ"), None)]}]
            bstack1llllll1l11_opy_ = bstack1ll111_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᒸ") if bstack1ll111_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᒹ") in getattr(args[1].excinfo, bstack1ll111_opy_ (u"ࠢࡵࡻࡳࡩࡳࡧ࡭ࡦࠤᒺ"), bstack1ll111_opy_ (u"ࠣࠤᒻ")) else bstack1ll111_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᒼ")
        bstack1l1111ll11l_opy_ = result.get(bstack1ll111_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᒽ"), TestFramework.bstack1l1111111ll_opy_)
        if bstack1l1111ll11l_opy_ != TestFramework.bstack1l1111111ll_opy_:
            TestFramework.bstack1llll11l11l_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l11111l11l_opy_(instance, {
            TestFramework.bstack1l11ll1l11l_opy_: failure,
            TestFramework.bstack1l1111llll1_opy_: bstack1llllll1l11_opy_,
            TestFramework.bstack1l11l1lll11_opy_: bstack1l1111ll11l_opy_,
        })
    def __1l111111ll1_opy_(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1lll1l1lll1_opy_.SETUP_FIXTURE:
            instance = self.__1l1111ll1l1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l111111l11_opy_ bstack1l11111l111_opy_ this to be bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᒾ")
            if test_framework_state == bstack1lll1l1lll1_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11llll1ll1l_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1ll111_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᒿ"), None), bstack1ll111_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᓀ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1ll111_opy_ (u"ࠢ࡯ࡱࡧࡩࠧᓁ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack1ll111_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᓂ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1llll111ll1_opy_(target) if target else None
        return instance
    def __1l1111l111l_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l1111ll111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, PytestBDDFramework.bstack1l1111lll1l_opy_, {})
        if not key in bstack1l1111ll111_opy_:
            bstack1l1111ll111_opy_[key] = []
        bstack1l111l1l111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, PytestBDDFramework.bstack1l1111l1l11_opy_, {})
        if not key in bstack1l111l1l111_opy_:
            bstack1l111l1l111_opy_[key] = []
        bstack11llll11111_opy_ = {
            PytestBDDFramework.bstack1l1111lll1l_opy_: bstack1l1111ll111_opy_,
            PytestBDDFramework.bstack1l1111l1l11_opy_: bstack1l111l1l111_opy_,
        }
        if test_hook_state == bstack1lll1l1llll_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack1ll111_opy_ (u"ࠤ࡮ࡩࡾࠨᓃ"): key,
                TestFramework.bstack1l1111l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack11lll1lllll_opy_: TestFramework.bstack11llllll1l1_opy_,
                TestFramework.bstack1l111l11ll1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11lllll1lll_opy_: [],
                TestFramework.bstack11llll1llll_opy_: hook_name,
                TestFramework.bstack1l111l11lll_opy_: bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()
            }
            bstack1l1111ll111_opy_[key].append(hook)
            bstack11llll11111_opy_[PytestBDDFramework.bstack11lllll11ll_opy_] = key
        elif test_hook_state == bstack1lll1l1llll_opy_.POST:
            bstack11llll1l11l_opy_ = bstack1l1111ll111_opy_.get(key, [])
            hook = bstack11llll1l11l_opy_.pop() if bstack11llll1l11l_opy_ else None
            if hook:
                result = self.__1l1111l11l1_opy_(*args)
                if result:
                    bstack11lll1lll1l_opy_ = result.get(bstack1ll111_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᓄ"), TestFramework.bstack11llllll1l1_opy_)
                    if bstack11lll1lll1l_opy_ != TestFramework.bstack11llllll1l1_opy_:
                        hook[TestFramework.bstack11lll1lllll_opy_] = bstack11lll1lll1l_opy_
                hook[TestFramework.bstack11llllllll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l111l11lll_opy_] = bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()
                self.bstack1l111l1111l_opy_(hook)
                logs = hook.get(TestFramework.bstack11lll1ll1l1_opy_, [])
                self.bstack1l1l1ll111l_opy_(instance, logs)
                bstack1l111l1l111_opy_[key].append(hook)
                bstack11llll11111_opy_[PytestBDDFramework.bstack1l11111l1l1_opy_] = key
        TestFramework.bstack1l11111l11l_opy_(instance, bstack11llll11111_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢ࡬ࡴࡵ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡰ࡫ࡹࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࡃࡻࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࡽࠡࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠿ࠥᓅ") + str(bstack1l111l1l111_opy_) + bstack1ll111_opy_ (u"ࠧࠨᓆ"))
    def __1l1111ll1l1_opy_(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l11l11l1_opy_(args[0], [bstack1ll111_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓇ"), bstack1ll111_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᓈ"), bstack1ll111_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᓉ"), bstack1ll111_opy_ (u"ࠤ࡬ࡨࡸࠨᓊ"), bstack1ll111_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᓋ"), bstack1ll111_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᓌ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack1ll111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᓍ")) else fixturedef.get(bstack1ll111_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓎ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1ll111_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᓏ")) else None
        node = request.node if hasattr(request, bstack1ll111_opy_ (u"ࠣࡰࡲࡨࡪࠨᓐ")) else None
        target = request.node.nodeid if hasattr(node, bstack1ll111_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᓑ")) else None
        baseid = fixturedef.get(bstack1ll111_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᓒ"), None) or bstack1ll111_opy_ (u"ࠦࠧᓓ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1ll111_opy_ (u"ࠧࡥࡰࡺࡨࡸࡲࡨ࡯ࡴࡦ࡯ࠥᓔ")):
            target = PytestBDDFramework.__1l111l111ll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1ll111_opy_ (u"ࠨ࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠣᓕ")) else None
            if target and not TestFramework.bstack1llll111ll1_opy_(target):
                self.__11llll1ll1l_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡱࡳࡩ࡫࠽ࡼࡰࡲࡨࡪࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᓖ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠣࠤᓗ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1ll111_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡦࡨࡪࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᓘ") + str(target) + bstack1ll111_opy_ (u"ࠥࠦᓙ"))
            return None
        instance = TestFramework.bstack1llll111ll1_opy_(target)
        if not instance:
            self.logger.warning(bstack1ll111_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡦࡦࡹࡥࡪࡦࡀࡿࡧࡧࡳࡦ࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᓚ") + str(target) + bstack1ll111_opy_ (u"ࠧࠨᓛ"))
            return None
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, PytestBDDFramework.bstack1l11111111l_opy_, {})
        if os.getenv(bstack1ll111_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡌࡉ࡙ࡖࡘࡖࡊ࡙ࠢᓜ"), bstack1ll111_opy_ (u"ࠢ࠲ࠤᓝ")) == bstack1ll111_opy_ (u"ࠣ࠳ࠥᓞ"):
            bstack11llll1l111_opy_ = bstack1ll111_opy_ (u"ࠤ࠽ࠦᓟ").join((scope, fixturename))
            bstack11lll1lll11_opy_ = datetime.now(tz=timezone.utc)
            bstack11llll1ll11_opy_ = {
                bstack1ll111_opy_ (u"ࠥ࡯ࡪࡿࠢᓠ"): bstack11llll1l111_opy_,
                bstack1ll111_opy_ (u"ࠦࡹࡧࡧࡴࠤᓡ"): PytestBDDFramework.__11lllll1111_opy_(request.node, scenario),
                bstack1ll111_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪࠨᓢ"): fixturedef,
                bstack1ll111_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᓣ"): scope,
                bstack1ll111_opy_ (u"ࠢࡵࡻࡳࡩࠧᓤ"): None,
            }
            try:
                if test_hook_state == bstack1lll1l1llll_opy_.POST and callable(getattr(args[-1], bstack1ll111_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᓥ"), None)):
                    bstack11llll1ll11_opy_[bstack1ll111_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᓦ")] = TestFramework.bstack1l1l1l1l11l_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1l1llll_opy_.PRE:
                bstack11llll1ll11_opy_[bstack1ll111_opy_ (u"ࠥࡹࡺ࡯ࡤࠣᓧ")] = uuid4().__str__()
                bstack11llll1ll11_opy_[PytestBDDFramework.bstack1l111l11ll1_opy_] = bstack11lll1lll11_opy_
            elif test_hook_state == bstack1lll1l1llll_opy_.POST:
                bstack11llll1ll11_opy_[PytestBDDFramework.bstack11llllllll1_opy_] = bstack11lll1lll11_opy_
            if bstack11llll1l111_opy_ in bstack1l11111l1ll_opy_:
                bstack1l11111l1ll_opy_[bstack11llll1l111_opy_].update(bstack11llll1ll11_opy_)
                self.logger.debug(bstack1ll111_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࠧᓨ") + str(bstack1l11111l1ll_opy_[bstack11llll1l111_opy_]) + bstack1ll111_opy_ (u"ࠧࠨᓩ"))
            else:
                bstack1l11111l1ll_opy_[bstack11llll1l111_opy_] = bstack11llll1ll11_opy_
                self.logger.debug(bstack1ll111_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࢀࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࢁࠥࡺࡲࡢࡥ࡮ࡩࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࠤᓪ") + str(len(bstack1l11111l1ll_opy_)) + bstack1ll111_opy_ (u"ࠢࠣᓫ"))
        TestFramework.bstack1llll11l11l_opy_(instance, PytestBDDFramework.bstack1l11111111l_opy_, bstack1l11111l1ll_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࡾࡰࡪࡴࠨࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠬࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᓬ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠤࠥᓭ"))
        return instance
    def __11llll1ll1l_opy_(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1llll1l11ll_opy_.create_context(target)
        ob = bstack1ll1l1ll1ll_opy_(ctx, self.bstack1l1llllll11_opy_, self.bstack11lll1llll1_opy_, test_framework_state)
        TestFramework.bstack1l11111l11l_opy_(ob, {
            TestFramework.bstack1l1lllll1ll_opy_: context.test_framework_name,
            TestFramework.bstack1l1ll1111ll_opy_: context.test_framework_version,
            TestFramework.bstack11llll111ll_opy_: [],
            PytestBDDFramework.bstack1l11111111l_opy_: {},
            PytestBDDFramework.bstack1l1111l1l11_opy_: {},
            PytestBDDFramework.bstack1l1111lll1l_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll11l11l_opy_(ob, TestFramework.bstack11lll1ll111_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll11l11l_opy_(ob, TestFramework.bstack1ll11ll1111_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡨࡺࡸ࠯࡫ࡧࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥᓮ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack1ll111_opy_ (u"ࠦࠧᓯ"))
        return ob
    @staticmethod
    def __11llll11l1l_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1ll111_opy_ (u"ࠬ࡯ࡤࠨᓰ"): id(step),
                bstack1ll111_opy_ (u"࠭ࡴࡦࡺࡷࠫᓱ"): step.name,
                bstack1ll111_opy_ (u"ࠧ࡬ࡧࡼࡻࡴࡸࡤࠨᓲ"): step.keyword,
            })
        meta = {
            bstack1ll111_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࠩᓳ"): {
                bstack1ll111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᓴ"): feature.name,
                bstack1ll111_opy_ (u"ࠪࡴࡦࡺࡨࠨᓵ"): feature.filename,
                bstack1ll111_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩᓶ"): feature.description
            },
            bstack1ll111_opy_ (u"ࠬࡹࡣࡦࡰࡤࡶ࡮ࡵࠧᓷ"): {
                bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᓸ"): scenario.name
            },
            bstack1ll111_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᓹ"): steps,
            bstack1ll111_opy_ (u"ࠨࡧࡻࡥࡲࡶ࡬ࡦࡵࠪᓺ"): PytestBDDFramework.__1l1111lllll_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l111111111_opy_: meta
            }
        )
    def bstack1l111l1111l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1ll111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡐࡳࡱࡦࡩࡸࡹࡥࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡴ࡫ࡰ࡭ࡱࡧࡲࠡࡶࡲࠤࡹ࡮ࡥࠡࡌࡤࡺࡦࠦࡩ࡮ࡲ࡯ࡩࡲ࡫࡮ࡵࡣࡷ࡭ࡴࡴ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡗ࡬࡮ࡹࠠ࡮ࡧࡷ࡬ࡴࡪ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡃࡩࡧࡦ࡯ࡸࠦࡴࡩࡧࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢ࡬ࡲࡸ࡯ࡤࡦࠢࢁ࠳࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠳࡚ࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡉࡳࡷࠦࡥࡢࡥ࡫ࠤ࡫࡯࡬ࡦࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠭ࠢࡵࡩࡵࡲࡡࡤࡧࡶࠤ࡚ࠧࡥࡴࡶࡏࡩࡻ࡫࡬ࠣࠢࡺ࡭ࡹ࡮ࠠࠣࡊࡲࡳࡰࡒࡥࡷࡧ࡯ࠦࠥ࡯࡮ࠡ࡫ࡷࡷࠥࡶࡡࡵࡪ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡌࡪࠥࡧࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡶ࡫ࡩࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡ࡯ࡤࡸࡨ࡮ࡥࡴࠢࡤࠤࡲࡵࡤࡪࡨ࡬ࡩࡩࠦࡨࡰࡱ࡮࠱ࡱ࡫ࡶࡦ࡮ࠣࡪ࡮ࡲࡥ࠭ࠢ࡬ࡸࠥࡩࡲࡦࡣࡷࡩࡸࠦࡡࠡࡎࡲ࡫ࡊࡴࡴࡳࡻࠣࡳࡧࡰࡥࡤࡶࠣࡻ࡮ࡺࡨࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱࡙ࠥࡩ࡮࡫࡯ࡥࡷࡲࡹ࠭ࠢ࡬ࡸࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡰࡴࡩࡡࡵࡧࡧࠤ࡮ࡴࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮࠲ࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠢࡥࡽࠥࡸࡥࡱ࡮ࡤࡧ࡮ࡴࡧࠡࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠨࠠࡸ࡫ࡷ࡬ࠥࠨࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭࠱ࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠣ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡖ࡫ࡩࠥࡩࡲࡦࡣࡷࡩࡩࠦࡌࡰࡩࡈࡲࡹࡸࡹࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡤࡶࡪࠦࡡࡥࡦࡨࡨࠥࡺ࡯ࠡࡶ࡫ࡩࠥ࡮࡯ࡰ࡭ࠪࡷࠥࠨ࡬ࡰࡩࡶࠦࠥࡲࡩࡴࡶ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡇࡲࡨࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࡫ࡳࡴࡱ࠺ࠡࡖ࡫ࡩࠥ࡫ࡶࡦࡰࡷࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹࠡࡥࡲࡲࡹࡧࡩ࡯࡫ࡱ࡫ࠥ࡫ࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡪࡷࠥࡧ࡮ࡥࠢ࡫ࡳࡴࡱࠠࡪࡰࡩࡳࡷࡳࡡࡵ࡫ࡲࡲ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡭ࡵ࡯࡬ࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡓࡥࡹ࡮ࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡘࡪࡹࡴࡍࡧࡹࡩࡱࠦ࡭ࡰࡰ࡬ࡸࡴࡸࡩ࡯ࡩ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡥࡹ࡮ࡲࡤࡠ࡮ࡨࡺࡪࡲ࡟ࡧ࡫࡯ࡩࡸࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡒࡤࡸ࡭ࠦ࡯ࡣ࡬ࡨࡧࡹࡹࠠࡧࡴࡲࡱࠥࡺࡨࡦࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠦ࡭ࡰࡰ࡬ࡸࡴࡸࡩ࡯ࡩ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣᓻ")
        global _1l1ll1l11l1_opy_
        platform_index = os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᓼ")]
        bstack1l1l1l11lll_opy_ = os.path.join(bstack1l1l1lllll1_opy_, (bstack1l1l1llll1l_opy_ + str(platform_index)), bstack1l1111l11ll_opy_)
        if not os.path.exists(bstack1l1l1l11lll_opy_) or not os.path.isdir(bstack1l1l1l11lll_opy_):
            return
        logs = hook.get(bstack1ll111_opy_ (u"ࠦࡱࡵࡧࡴࠤᓽ"), [])
        with os.scandir(bstack1l1l1l11lll_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll1l11l1_opy_:
                    self.logger.info(bstack1ll111_opy_ (u"ࠧࡖࡡࡵࡪࠣࡥࡱࡸࡥࡢࡦࡼࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡪࠠࡼࡿࠥᓾ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1ll111_opy_ (u"ࠨࠢᓿ")
                    log_entry = bstack1ll1ll1llll_opy_(
                        kind=bstack1ll111_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᔀ"),
                        message=bstack1ll111_opy_ (u"ࠣࠤᔁ"),
                        level=bstack1ll111_opy_ (u"ࠤࠥᔂ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1l1111l_opy_=entry.stat().st_size,
                        bstack1l1l1ll1111_opy_=bstack1ll111_opy_ (u"ࠥࡑࡆࡔࡕࡂࡎࡢ࡙ࡕࡒࡏࡂࡆࠥᔃ"),
                        bstack1111lll_opy_=os.path.abspath(entry.path),
                        bstack1l11111ll1l_opy_=hook.get(TestFramework.bstack1l1111l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll1l11l1_opy_.add(abs_path)
        platform_index = os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᔄ")]
        bstack11lll1ll11l_opy_ = os.path.join(bstack1l1l1lllll1_opy_, (bstack1l1l1llll1l_opy_ + str(platform_index)), bstack1l1111l11ll_opy_, bstack11llll1lll1_opy_)
        if not os.path.exists(bstack11lll1ll11l_opy_) or not os.path.isdir(bstack11lll1ll11l_opy_):
            self.logger.info(bstack1ll111_opy_ (u"ࠧࡔ࡯ࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡨࡲࡹࡳࡪࠠࡢࡶ࠽ࠤࢀࢃࠢᔅ").format(bstack11lll1ll11l_opy_))
        else:
            self.logger.info(bstack1ll111_opy_ (u"ࠨࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡧࡴࡲࡱࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᔆ").format(bstack11lll1ll11l_opy_))
            with os.scandir(bstack11lll1ll11l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll1l11l1_opy_:
                        self.logger.info(bstack1ll111_opy_ (u"ࠢࡑࡣࡷ࡬ࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡰࡳࡱࡦࡩࡸࡹࡥࡥࠢࡾࢁࠧᔇ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1ll111_opy_ (u"ࠣࠤᔈ")
                        log_entry = bstack1ll1ll1llll_opy_(
                            kind=bstack1ll111_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦᔉ"),
                            message=bstack1ll111_opy_ (u"ࠥࠦᔊ"),
                            level=bstack1ll111_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠣᔋ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1l1111l_opy_=entry.stat().st_size,
                            bstack1l1l1ll1111_opy_=bstack1ll111_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧᔌ"),
                            bstack1111lll_opy_=os.path.abspath(entry.path),
                            bstack1l1l11lllll_opy_=hook.get(TestFramework.bstack1l1111l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll1l11l1_opy_.add(abs_path)
        hook[bstack1ll111_opy_ (u"ࠨ࡬ࡰࡩࡶࠦᔍ")] = logs
    def bstack1l1l1ll111l_opy_(
        self,
        bstack1l1ll111l11_opy_: bstack1ll1l1ll1ll_opy_,
        entries: List[bstack1ll1ll1llll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡔࡇࡖࡗࡎࡕࡎࡠࡋࡇࠦᔎ"))
        req.platform_index = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1ll11ll1111_opy_)
        req.execution_context.hash = str(bstack1l1ll111l11_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll111l11_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll111l11_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1l1lllll1ll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1l1ll1111ll_opy_)
            log_entry.uuid = entry.bstack1l11111ll1l_opy_ if entry.bstack1l11111ll1l_opy_ else TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1ll11l111ll_opy_)
            log_entry.test_framework_state = bstack1l1ll111l11_opy_.state.name
            log_entry.message = entry.message.encode(bstack1ll111_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢᔏ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1ll111_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦᔐ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1l1111l_opy_
                log_entry.file_path = entry.bstack1111lll_opy_
        def bstack1l1ll111ll1_opy_():
            bstack111ll1ll1_opy_ = datetime.now()
            try:
                self.bstack1lll1l11lll_opy_.LogCreatedEvent(req)
                bstack1l1ll111l11_opy_.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠢᔑ"), datetime.now() - bstack111ll1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1ll111_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡼࡿࠥᔒ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1llll_opy_.enqueue(bstack1l1ll111ll1_opy_)
    def __1l1111l1ll1_opy_(self, instance) -> None:
        bstack1ll111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡏࡳࡦࡪࡳࠡࡥࡸࡷࡹࡵ࡭ࠡࡶࡤ࡫ࡸࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡨ࡫ࡹࡩࡳࠦࡴࡦࡵࡷࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡸࡥࡢࡶࡨࡷࠥࡧࠠࡥ࡫ࡦࡸࠥࡩ࡯࡯ࡶࡤ࡭ࡳ࡯࡮ࡨࠢࡷࡩࡸࡺࠠ࡭ࡧࡹࡩࡱࠦࡣࡶࡵࡷࡳࡲࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇࡺࡹࡴࡰ࡯ࡗࡥ࡬ࡓࡡ࡯ࡣࡪࡩࡷࠦࡡ࡯ࡦࠣࡹࡵࡪࡡࡵࡧࡶࠤࡹ࡮ࡥࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠣࡷࡹࡧࡴࡦࠢࡸࡷ࡮ࡴࡧࠡࡵࡨࡸࡤࡹࡴࡢࡶࡨࡣࡪࡴࡴࡳ࡫ࡨࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥᔓ")
        bstack11llll11111_opy_ = {bstack1ll111_opy_ (u"ࠨࡣࡶࡵࡷࡳࡲࡥ࡭ࡦࡶࡤࡨࡦࡺࡡࠣᔔ"): bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()}
        TestFramework.bstack1l11111l11l_opy_(instance, bstack11llll11111_opy_)
    @staticmethod
    def __11lllllllll_opy_(instance, args):
        request, bstack1l111l11111_opy_ = args
        bstack11lllllll1l_opy_ = id(bstack1l111l11111_opy_)
        bstack11lllll11l1_opy_ = instance.data[TestFramework.bstack1l111111111_opy_]
        step = next(filter(lambda st: st[bstack1ll111_opy_ (u"ࠧࡪࡦࠪᔕ")] == bstack11lllllll1l_opy_, bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᔖ")]), None)
        step.update({
            bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᔗ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᔘ")]) if st[bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧᔙ")] == step[bstack1ll111_opy_ (u"ࠬ࡯ࡤࠨᔚ")]), None)
        if index is not None:
            bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᔛ")][index] = step
        instance.data[TestFramework.bstack1l111111111_opy_] = bstack11lllll11l1_opy_
    @staticmethod
    def __11lll1ll1ll_opy_(instance, args):
        bstack1ll111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡼ࡮ࡥ࡯ࠢ࡯ࡩࡳࠦࡡࡳࡩࡶࠤ࡮ࡹࠠ࠳࠮ࠣ࡭ࡹࠦࡳࡪࡩࡱ࡭࡫࡯ࡥࡴࠢࡷ࡬ࡪࡸࡥࠡ࡫ࡶࠤࡳࡵࠠࡦࡺࡦࡩࡵࡺࡩࡰࡰࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡣࡵ࡫ࡸࠦࡡࡳࡧࠣ࠱ࠥࡡࡲࡦࡳࡸࡩࡸࡺࠬࠡࡵࡷࡩࡵࡣࠊࠡࠢࠣࠤࠥࠦࠠࠡ࡫ࡩࠤࡦࡸࡧࡴࠢࡤࡶࡪࠦ࠳ࠡࡶ࡫ࡩࡳࠦࡴࡩࡧࠣࡰࡦࡹࡴࠡࡸࡤࡰࡺ࡫ࠠࡪࡵࠣࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥᔜ")
        bstack1l111l111l1_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l111l11111_opy_ = args[1]
        bstack11lllllll1l_opy_ = id(bstack1l111l11111_opy_)
        bstack11lllll11l1_opy_ = instance.data[TestFramework.bstack1l111111111_opy_]
        step = None
        if bstack11lllllll1l_opy_ is not None and bstack11lllll11l1_opy_.get(bstack1ll111_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᔝ")):
            step = next(filter(lambda st: st[bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬᔞ")] == bstack11lllllll1l_opy_, bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᔟ")]), None)
            step.update({
                bstack1ll111_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩᔠ"): bstack1l111l111l1_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack1ll111_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᔡ"): bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᔢ"),
                bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨᔣ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack1ll111_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨᔤ"): bstack1ll111_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᔥ"),
                })
        index = next((i for i, st in enumerate(bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩᔦ")]) if st[bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧᔧ")] == step[bstack1ll111_opy_ (u"ࠬ࡯ࡤࠨᔨ")]), None)
        if index is not None:
            bstack11lllll11l1_opy_[bstack1ll111_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᔩ")][index] = step
        instance.data[TestFramework.bstack1l111111111_opy_] = bstack11lllll11l1_opy_
    @staticmethod
    def __1l1111lllll_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack1ll111_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩᔪ")):
                examples = list(node.callspec.params[bstack1ll111_opy_ (u"ࠨࡡࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡥࡹࡣࡰࡴࡱ࡫ࠧᔫ")].values())
            return examples
        except:
            return []
    def bstack1l1l1ll1l11_opy_(self, instance: bstack1ll1l1ll1ll_opy_, bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]):
        bstack1l111l11l11_opy_ = (
            PytestBDDFramework.bstack11lllll11ll_opy_
            if bstack1llll11ll1l_opy_[1] == bstack1lll1l1llll_opy_.PRE
            else PytestBDDFramework.bstack1l11111l1l1_opy_
        )
        hook = PytestBDDFramework.bstack11lllll1l1l_opy_(instance, bstack1l111l11l11_opy_)
        entries = hook.get(TestFramework.bstack11lllll1lll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack11llll111ll_opy_, []))
        return entries
    def bstack1l1l1llllll_opy_(self, instance: bstack1ll1l1ll1ll_opy_, bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]):
        bstack1l111l11l11_opy_ = (
            PytestBDDFramework.bstack11lllll11ll_opy_
            if bstack1llll11ll1l_opy_[1] == bstack1lll1l1llll_opy_.PRE
            else PytestBDDFramework.bstack1l11111l1l1_opy_
        )
        PytestBDDFramework.bstack1l1111111l1_opy_(instance, bstack1l111l11l11_opy_)
        TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack11llll111ll_opy_, []).clear()
    @staticmethod
    def bstack11lllll1l1l_opy_(instance: bstack1ll1l1ll1ll_opy_, bstack1l111l11l11_opy_: str):
        bstack1l1111l1lll_opy_ = (
            PytestBDDFramework.bstack1l1111l1l11_opy_
            if bstack1l111l11l11_opy_ == PytestBDDFramework.bstack1l11111l1l1_opy_
            else PytestBDDFramework.bstack1l1111lll1l_opy_
        )
        bstack11llll11ll1_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1l111l11l11_opy_, None)
        bstack11llllll111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1l1111l1lll_opy_, None) if bstack11llll11ll1_opy_ else None
        return (
            bstack11llllll111_opy_[bstack11llll11ll1_opy_][-1]
            if isinstance(bstack11llllll111_opy_, dict) and len(bstack11llllll111_opy_.get(bstack11llll11ll1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l1111111l1_opy_(instance: bstack1ll1l1ll1ll_opy_, bstack1l111l11l11_opy_: str):
        hook = PytestBDDFramework.bstack11lllll1l1l_opy_(instance, bstack1l111l11l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11lllll1lll_opy_, []).clear()
    @staticmethod
    def __11lllll1ll1_opy_(instance: bstack1ll1l1ll1ll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1ll111_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡥࡲࡶࡩࡹࠢᔬ"), None)):
            return
        if os.getenv(bstack1ll111_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡏࡓࡌ࡙ࠢᔭ"), bstack1ll111_opy_ (u"ࠦ࠶ࠨᔮ")) != bstack1ll111_opy_ (u"ࠧ࠷ࠢᔯ"):
            PytestBDDFramework.logger.warning(bstack1ll111_opy_ (u"ࠨࡩࡨࡰࡲࡶ࡮ࡴࡧࠡࡥࡤࡴࡱࡵࡧࠣᔰ"))
            return
        bstack11lll1l1lll_opy_ = {
            bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨᔱ"): (PytestBDDFramework.bstack11lllll11ll_opy_, PytestBDDFramework.bstack1l1111lll1l_opy_),
            bstack1ll111_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥᔲ"): (PytestBDDFramework.bstack1l11111l1l1_opy_, PytestBDDFramework.bstack1l1111l1l11_opy_),
        }
        for when in (bstack1ll111_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣᔳ"), bstack1ll111_opy_ (u"ࠥࡧࡦࡲ࡬ࠣᔴ"), bstack1ll111_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨᔵ")):
            bstack1l111111lll_opy_ = args[1].get_records(when)
            if not bstack1l111111lll_opy_:
                continue
            records = [
                bstack1ll1ll1llll_opy_(
                    kind=TestFramework.bstack1l1l1ll11ll_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1ll111_opy_ (u"ࠧࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠣᔶ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1ll111_opy_ (u"ࠨࡣࡳࡧࡤࡸࡪࡪࠢᔷ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111111lll_opy_
                if isinstance(getattr(r, bstack1ll111_opy_ (u"ࠢ࡮ࡧࡶࡷࡦ࡭ࡥࠣᔸ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11lllll111l_opy_, bstack1l1111l1lll_opy_ = bstack11lll1l1lll_opy_.get(when, (None, None))
            bstack11llll1l1l1_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack11lllll111l_opy_, None) if bstack11lllll111l_opy_ else None
            bstack11llllll111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1l1111l1lll_opy_, None) if bstack11llll1l1l1_opy_ else None
            if isinstance(bstack11llllll111_opy_, dict) and len(bstack11llllll111_opy_.get(bstack11llll1l1l1_opy_, [])) > 0:
                hook = bstack11llllll111_opy_[bstack11llll1l1l1_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack11lllll1lll_opy_ in hook:
                    hook[TestFramework.bstack11lllll1lll_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack11llll111ll_opy_, [])
            logs.extend(records)
    @staticmethod
    def __1l1111lll11_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l1lllll11_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__11llllll11l_opy_(request.node, scenario)
        bstack11llll1111l_opy_ = feature.filename
        if not bstack1l1lllll11_opy_ or not test_name or not bstack11llll1111l_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11l111ll_opy_: uuid4().__str__(),
            TestFramework.bstack11lllll1l11_opy_: bstack1l1lllll11_opy_,
            TestFramework.bstack1l1llll11l1_opy_: test_name,
            TestFramework.bstack1l1l111111l_opy_: bstack1l1lllll11_opy_,
            TestFramework.bstack11lllllll11_opy_: bstack11llll1111l_opy_,
            TestFramework.bstack1l11111ll11_opy_: PytestBDDFramework.__11lllll1111_opy_(feature, scenario),
            TestFramework.bstack1l11111lll1_opy_: code,
            TestFramework.bstack1l11l1lll11_opy_: TestFramework.bstack1l1111111ll_opy_,
            TestFramework.bstack1l111lllll1_opy_: test_name
        }
    @staticmethod
    def __11llllll11l_opy_(node, scenario):
        if hasattr(node, bstack1ll111_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᔹ")):
            parts = node.nodeid.rsplit(bstack1ll111_opy_ (u"ࠤ࡞ࠦᔺ"))
            params = parts[-1]
            return bstack1ll111_opy_ (u"ࠥࡿࢂ࡛ࠦࡼࡿࠥᔻ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __11lllll1111_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack1ll111_opy_ (u"ࠫࡹࡧࡧࡴࠩᔼ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack1ll111_opy_ (u"ࠬࡺࡡࡨࡵࠪᔽ")) else [])
    @staticmethod
    def __1l111l111ll_opy_(location):
        return bstack1ll111_opy_ (u"ࠨ࠺࠻ࠤᔾ").join(filter(lambda x: isinstance(x, str), location))