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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1lll1l1lll1_opy_,
    bstack1ll1l1ll1ll_opy_,
    bstack1lll1l1llll_opy_,
    bstack1l1111l1111_opy_,
    bstack1ll1ll1llll_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1l1ll11l1ll_opy_
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lllll1llll_opy_ import bstack1llllll111l_opy_
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1111l_opy_ import bstack1lll11l1l11_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
bstack1l1l1lllll1_opy_ = bstack1l1ll11l1ll_opy_()
bstack11llll11lll_opy_ = 1.0
bstack1l1l1llll1l_opy_ = bstack1ll111_opy_ (u"ࠢࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠳ࠢᔿ")
bstack11lll1l11ll_opy_ = bstack1ll111_opy_ (u"ࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦᕀ")
bstack11lll1l1ll1_opy_ = bstack1ll111_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠨᕁ")
bstack11lll1l11l1_opy_ = bstack1ll111_opy_ (u"ࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠨᕂ")
bstack11lll1l1l1l_opy_ = bstack1ll111_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠥᕃ")
_1l1ll1l11l1_opy_ = set()
class bstack1ll1ll1ll11_opy_(TestFramework):
    bstack1l11111111l_opy_ = bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡷࠧᕄ")
    bstack1l1111lll1l_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࡢࡷࡹࡧࡲࡵࡧࡧࠦᕅ")
    bstack1l1111l1l11_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᕆ")
    bstack11lllll11ll_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡱࡧࡳࡵࡡࡶࡸࡦࡸࡴࡦࡦࠥᕇ")
    bstack1l11111l1l1_opy_ = bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࠧᕈ")
    bstack1l11111llll_opy_: bool
    bstack1lllll1llll_opy_: bstack1llllll111l_opy_  = None
    bstack1lll1l11lll_opy_ = None
    bstack1l111111l1l_opy_ = [
        bstack1lll1l1lll1_opy_.BEFORE_ALL,
        bstack1lll1l1lll1_opy_.AFTER_ALL,
        bstack1lll1l1lll1_opy_.BEFORE_EACH,
        bstack1lll1l1lll1_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lll1llll1_opy_: Dict[str, str],
        bstack1l1llllll11_opy_: List[str]=[bstack1ll111_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥᕉ")],
        bstack1lllll1llll_opy_: bstack1llllll111l_opy_=None,
        bstack1lll1l11lll_opy_=None
    ):
        super().__init__(bstack1l1llllll11_opy_, bstack11lll1llll1_opy_, bstack1lllll1llll_opy_)
        self.bstack1l11111llll_opy_ = any(bstack1ll111_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᕊ") in item.lower() for item in bstack1l1llllll11_opy_)
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
        if test_framework_state == bstack1lll1l1lll1_opy_.TEST or test_framework_state in bstack1ll1ll1ll11_opy_.bstack1l111111l1l_opy_:
            bstack11llll111l1_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1lll1l1lll1_opy_.NONE:
            self.logger.warning(bstack1ll111_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩࡩࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࡂࠨᕋ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠨࠢᕌ"))
            return
        if not self.bstack1l11111llll_opy_:
            self.logger.warning(bstack1ll111_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࠽ࠣᕍ") + str(str(self.bstack1l1llllll11_opy_)) + bstack1ll111_opy_ (u"ࠣࠤᕎ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1ll111_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᕏ") + str(kwargs) + bstack1ll111_opy_ (u"ࠥࠦᕐ"))
            return
        instance = self.__1l111111ll1_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡦࡸࡧࡴ࠿ࠥᕑ") + str(args) + bstack1ll111_opy_ (u"ࠧࠨᕒ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1ll1ll1ll11_opy_.bstack1l111111l1l_opy_ and test_hook_state == bstack1lll1l1llll_opy_.PRE:
                bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1l1lll111l_opy_.value)
                name = str(EVENTS.bstack1l1lll111l_opy_.name)+bstack1ll111_opy_ (u"ࠨ࠺ࠣᕓ")+str(test_framework_state.name)
                TestFramework.bstack11llllll1ll_opy_(instance, name, bstack1ll111lllll_opy_)
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴࠣࡴࡷ࡫࠺ࠡࡽࢀࠦᕔ").format(e))
        try:
            if not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack11lllll1l11_opy_) and test_hook_state == bstack1lll1l1llll_opy_.PRE:
                test = bstack1ll1ll1ll11_opy_.__1l1111lll11_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack1ll111_opy_ (u"ࠣ࡮ࡲࡥࡩ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᕕ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠤࠥᕖ"))
            if test_framework_state == bstack1lll1l1lll1_opy_.TEST:
                if test_hook_state == bstack1lll1l1llll_opy_.PRE and not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack1l1l111lll1_opy_):
                    TestFramework.bstack1llll11l11l_opy_(instance, TestFramework.bstack1l1l111lll1_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡪࡺࠠࡵࡧࡶࡸ࠲ࡹࡴࡢࡴࡷࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᕗ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠦࠧᕘ"))
                elif test_hook_state == bstack1lll1l1llll_opy_.POST and not TestFramework.bstack1llll11lll1_opy_(instance, TestFramework.bstack1l1ll1l1l11_opy_):
                    TestFramework.bstack1llll11l11l_opy_(instance, TestFramework.bstack1l1ll1l1l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1ll111_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡦࡰࡧࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᕙ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠨࠢᕚ"))
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG and test_hook_state == bstack1lll1l1llll_opy_.POST:
                bstack1ll1ll1ll11_opy_.__11lllll1ll1_opy_(instance, *args)
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG_REPORT and test_hook_state == bstack1lll1l1llll_opy_.POST:
                self.__11llll11l11_opy_(instance, *args)
                self.__1l1111l1ll1_opy_(instance)
            elif test_framework_state in bstack1ll1ll1ll11_opy_.bstack1l111111l1l_opy_:
                self.__1l1111l111l_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᕛ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠣࠤᕜ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llll1l1ll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1ll1ll1ll11_opy_.bstack1l111111l1l_opy_ and test_hook_state == bstack1lll1l1llll_opy_.POST:
                name = str(EVENTS.bstack1l1lll111l_opy_.name)+bstack1ll111_opy_ (u"ࠤ࠽ࠦᕝ")+str(test_framework_state.name)
                bstack1ll111lllll_opy_ = TestFramework.bstack1l1111ll1ll_opy_(instance, name)
                bstack1ll1ll111ll_opy_.end(EVENTS.bstack1l1lll111l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᕞ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᕟ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᕠ").format(e))
    def bstack1l1l1ll1ll1_opy_(self):
        return self.bstack1l11111llll_opy_
    def __1l1111l11l1_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1ll111_opy_ (u"ࠨࡧࡦࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᕡ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l11l11l1_opy_(rep, [bstack1ll111_opy_ (u"ࠢࡸࡪࡨࡲࠧᕢ"), bstack1ll111_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᕣ"), bstack1ll111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤᕤ"), bstack1ll111_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥᕥ"), bstack1ll111_opy_ (u"ࠦࡸࡱࡩࡱࡲࡨࡨࠧᕦ"), bstack1ll111_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᕧ")])
        return None
    def __11llll11l11_opy_(self, instance: bstack1ll1l1ll1ll_opy_, *args):
        result = self.__1l1111l11l1_opy_(*args)
        if not result:
            return
        failure = None
        bstack1llllll1l11_opy_ = None
        if result.get(bstack1ll111_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᕨ"), None) == bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢᕩ") and len(args) > 1 and getattr(args[1], bstack1ll111_opy_ (u"ࠣࡧࡻࡧ࡮ࡴࡦࡰࠤᕪ"), None) is not None:
            failure = [{bstack1ll111_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᕫ"): [args[1].excinfo.exconly(), result.get(bstack1ll111_opy_ (u"ࠥࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠤᕬ"), None)]}]
            bstack1llllll1l11_opy_ = bstack1ll111_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᕭ") if bstack1ll111_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣᕮ") in getattr(args[1].excinfo, bstack1ll111_opy_ (u"ࠨࡴࡺࡲࡨࡲࡦࡳࡥࠣᕯ"), bstack1ll111_opy_ (u"ࠢࠣᕰ")) else bstack1ll111_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤᕱ")
        bstack1l1111ll11l_opy_ = result.get(bstack1ll111_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᕲ"), TestFramework.bstack1l1111111ll_opy_)
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
            target = None # bstack1l111111l11_opy_ bstack1l11111l111_opy_ this to be bstack1ll111_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᕳ")
            if test_framework_state == bstack1lll1l1lll1_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__11llll1ll1l_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1lll1l1lll1_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦࠤᕴ"), None), bstack1ll111_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᕵ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1ll111_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᕶ"), None):
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
        bstack1l1111ll111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1ll1ll1ll11_opy_.bstack1l1111lll1l_opy_, {})
        if not key in bstack1l1111ll111_opy_:
            bstack1l1111ll111_opy_[key] = []
        bstack1l111l1l111_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1ll1ll1ll11_opy_.bstack1l1111l1l11_opy_, {})
        if not key in bstack1l111l1l111_opy_:
            bstack1l111l1l111_opy_[key] = []
        bstack11llll11111_opy_ = {
            bstack1ll1ll1ll11_opy_.bstack1l1111lll1l_opy_: bstack1l1111ll111_opy_,
            bstack1ll1ll1ll11_opy_.bstack1l1111l1l11_opy_: bstack1l111l1l111_opy_,
        }
        if test_hook_state == bstack1lll1l1llll_opy_.PRE:
            hook = {
                bstack1ll111_opy_ (u"ࠢ࡬ࡧࡼࠦᕷ"): key,
                TestFramework.bstack1l1111l1l1l_opy_: uuid4().__str__(),
                TestFramework.bstack11lll1lllll_opy_: TestFramework.bstack11llllll1l1_opy_,
                TestFramework.bstack1l111l11ll1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack11lllll1lll_opy_: [],
                TestFramework.bstack11llll1llll_opy_: args[1] if len(args) > 1 else bstack1ll111_opy_ (u"ࠨࠩᕸ"),
                TestFramework.bstack1l111l11lll_opy_: bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()
            }
            bstack1l1111ll111_opy_[key].append(hook)
            bstack11llll11111_opy_[bstack1ll1ll1ll11_opy_.bstack11lllll11ll_opy_] = key
        elif test_hook_state == bstack1lll1l1llll_opy_.POST:
            bstack11llll1l11l_opy_ = bstack1l1111ll111_opy_.get(key, [])
            hook = bstack11llll1l11l_opy_.pop() if bstack11llll1l11l_opy_ else None
            if hook:
                result = self.__1l1111l11l1_opy_(*args)
                if result:
                    bstack11lll1lll1l_opy_ = result.get(bstack1ll111_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᕹ"), TestFramework.bstack11llllll1l1_opy_)
                    if bstack11lll1lll1l_opy_ != TestFramework.bstack11llllll1l1_opy_:
                        hook[TestFramework.bstack11lll1lllll_opy_] = bstack11lll1lll1l_opy_
                hook[TestFramework.bstack11llllllll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l111l11lll_opy_]= bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()
                self.bstack1l111l1111l_opy_(hook)
                logs = hook.get(TestFramework.bstack11lll1ll1l1_opy_, [])
                if logs: self.bstack1l1l1ll111l_opy_(instance, logs)
                bstack1l111l1l111_opy_[key].append(hook)
                bstack11llll11111_opy_[bstack1ll1ll1ll11_opy_.bstack1l11111l1l1_opy_] = key
        TestFramework.bstack1l11111l11l_opy_(instance, bstack11llll11111_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡ࡫ࡳࡴࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾ࡯ࡪࡿࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࡂࢁࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࢃࠠࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤ࠾ࠤᕺ") + str(bstack1l111l1l111_opy_) + bstack1ll111_opy_ (u"ࠦࠧᕻ"))
    def __1l1111ll1l1_opy_(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l11l11l1_opy_(args[0], [bstack1ll111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᕼ"), bstack1ll111_opy_ (u"ࠨࡡࡳࡩࡱࡥࡲ࡫ࠢᕽ"), bstack1ll111_opy_ (u"ࠢࡱࡣࡵࡥࡲࡹࠢᕾ"), bstack1ll111_opy_ (u"ࠣ࡫ࡧࡷࠧᕿ"), bstack1ll111_opy_ (u"ࠤࡸࡲ࡮ࡺࡴࡦࡵࡷࠦᖀ"), bstack1ll111_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᖁ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack1ll111_opy_ (u"ࠦࡸࡩ࡯ࡱࡧࠥᖂ")) else fixturedef.get(bstack1ll111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᖃ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1ll111_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦᖄ")) else None
        node = request.node if hasattr(request, bstack1ll111_opy_ (u"ࠢ࡯ࡱࡧࡩࠧᖅ")) else None
        target = request.node.nodeid if hasattr(node, bstack1ll111_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᖆ")) else None
        baseid = fixturedef.get(bstack1ll111_opy_ (u"ࠤࡥࡥࡸ࡫ࡩࡥࠤᖇ"), None) or bstack1ll111_opy_ (u"ࠥࠦᖈ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1ll111_opy_ (u"ࠦࡤࡶࡹࡧࡷࡱࡧ࡮ࡺࡥ࡮ࠤᖉ")):
            target = bstack1ll1ll1ll11_opy_.__1l111l111ll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1ll111_opy_ (u"ࠧࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠢᖊ")) else None
            if target and not TestFramework.bstack1llll111ll1_opy_(target):
                self.__11llll1ll1l_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1ll111_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡥࡷࡧࡱࡸ࠿ࠦࡦࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡤࡶ࡬࡫ࡴ࠾ࡽࡷࡥࡷ࡭ࡥࡵࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࡽࠡࡰࡲࡨࡪࡃࡻ࡯ࡱࡧࡩࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᖋ") + str(test_hook_state) + bstack1ll111_opy_ (u"ࠢࠣᖌ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1ll111_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࡃࡻࡧ࡫ࡻࡸࡺࡸࡥࡥࡧࡩࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᖍ") + str(target) + bstack1ll111_opy_ (u"ࠤࠥᖎ"))
            return None
        instance = TestFramework.bstack1llll111ll1_opy_(target)
        if not instance:
            self.logger.warning(bstack1ll111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡥࡥࡸ࡫ࡩࡥ࠿ࡾࡦࡦࡹࡥࡪࡦࢀࠤࡹࡧࡲࡨࡧࡷࡁࠧᖏ") + str(target) + bstack1ll111_opy_ (u"ࠦࠧᖐ"))
            return None
        bstack1l11111l1ll_opy_ = TestFramework.bstack1llll11l1ll_opy_(instance, bstack1ll1ll1ll11_opy_.bstack1l11111111l_opy_, {})
        if os.getenv(bstack1ll111_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡆࡍࡃࡊࡣࡋࡏࡘࡕࡗࡕࡉࡘࠨᖑ"), bstack1ll111_opy_ (u"ࠨ࠱ࠣᖒ")) == bstack1ll111_opy_ (u"ࠢ࠲ࠤᖓ"):
            bstack11llll1l111_opy_ = bstack1ll111_opy_ (u"ࠣ࠼ࠥᖔ").join((scope, fixturename))
            bstack11lll1lll11_opy_ = datetime.now(tz=timezone.utc)
            bstack11llll1ll11_opy_ = {
                bstack1ll111_opy_ (u"ࠤ࡮ࡩࡾࠨᖕ"): bstack11llll1l111_opy_,
                bstack1ll111_opy_ (u"ࠥࡸࡦ࡭ࡳࠣᖖ"): bstack1ll1ll1ll11_opy_.__11lllll1111_opy_(request.node),
                bstack1ll111_opy_ (u"ࠦ࡫࡯ࡸࡵࡷࡵࡩࠧᖗ"): fixturedef,
                bstack1ll111_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᖘ"): scope,
                bstack1ll111_opy_ (u"ࠨࡴࡺࡲࡨࠦᖙ"): None,
            }
            try:
                if test_hook_state == bstack1lll1l1llll_opy_.POST and callable(getattr(args[-1], bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᖚ"), None)):
                    bstack11llll1ll11_opy_[bstack1ll111_opy_ (u"ࠣࡶࡼࡴࡪࠨᖛ")] = TestFramework.bstack1l1l1l1l11l_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll1l1llll_opy_.PRE:
                bstack11llll1ll11_opy_[bstack1ll111_opy_ (u"ࠤࡸࡹ࡮ࡪࠢᖜ")] = uuid4().__str__()
                bstack11llll1ll11_opy_[bstack1ll1ll1ll11_opy_.bstack1l111l11ll1_opy_] = bstack11lll1lll11_opy_
            elif test_hook_state == bstack1lll1l1llll_opy_.POST:
                bstack11llll1ll11_opy_[bstack1ll1ll1ll11_opy_.bstack11llllllll1_opy_] = bstack11lll1lll11_opy_
            if bstack11llll1l111_opy_ in bstack1l11111l1ll_opy_:
                bstack1l11111l1ll_opy_[bstack11llll1l111_opy_].update(bstack11llll1ll11_opy_)
                self.logger.debug(bstack1ll111_opy_ (u"ࠥࡹࡵࡪࡡࡵࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࠦᖝ") + str(bstack1l11111l1ll_opy_[bstack11llll1l111_opy_]) + bstack1ll111_opy_ (u"ࠦࠧᖞ"))
            else:
                bstack1l11111l1ll_opy_[bstack11llll1l111_opy_] = bstack11llll1ll11_opy_
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡹࡡࡷࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࡿࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࢀࠤࡹࡸࡡࡤ࡭ࡨࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡹ࠽ࠣᖟ") + str(len(bstack1l11111l1ll_opy_)) + bstack1ll111_opy_ (u"ࠨࠢᖠ"))
        TestFramework.bstack1llll11l11l_opy_(instance, bstack1ll1ll1ll11_opy_.bstack1l11111111l_opy_, bstack1l11111l1ll_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࡽ࡯ࡩࡳ࠮ࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠫࢀࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢᖡ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠣࠤᖢ"))
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
            bstack1ll1ll1ll11_opy_.bstack1l11111111l_opy_: {},
            bstack1ll1ll1ll11_opy_.bstack1l1111l1l11_opy_: {},
            bstack1ll1ll1ll11_opy_.bstack1l1111lll1l_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1llll11l11l_opy_(ob, TestFramework.bstack11lll1ll111_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1llll11l11l_opy_(ob, TestFramework.bstack1ll11ll1111_opy_, context.platform_index)
        TestFramework.bstack1lll1llllll_opy_[ctx.id] = ob
        self.logger.debug(bstack1ll111_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠣࡧࡹࡾ࠮ࡪࡦࡀࡿࡨࡺࡸ࠯࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳ࠾ࠤᖣ") + str(TestFramework.bstack1lll1llllll_opy_.keys()) + bstack1ll111_opy_ (u"ࠥࠦᖤ"))
        return ob
    def bstack1l1l1ll1l11_opy_(self, instance: bstack1ll1l1ll1ll_opy_, bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]):
        bstack1l111l11l11_opy_ = (
            bstack1ll1ll1ll11_opy_.bstack11lllll11ll_opy_
            if bstack1llll11ll1l_opy_[1] == bstack1lll1l1llll_opy_.PRE
            else bstack1ll1ll1ll11_opy_.bstack1l11111l1l1_opy_
        )
        hook = bstack1ll1ll1ll11_opy_.bstack11lllll1l1l_opy_(instance, bstack1l111l11l11_opy_)
        entries = hook.get(TestFramework.bstack11lllll1lll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack11llll111ll_opy_, []))
        return entries
    def bstack1l1l1llllll_opy_(self, instance: bstack1ll1l1ll1ll_opy_, bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]):
        bstack1l111l11l11_opy_ = (
            bstack1ll1ll1ll11_opy_.bstack11lllll11ll_opy_
            if bstack1llll11ll1l_opy_[1] == bstack1lll1l1llll_opy_.PRE
            else bstack1ll1ll1ll11_opy_.bstack1l11111l1l1_opy_
        )
        bstack1ll1ll1ll11_opy_.bstack1l1111111l1_opy_(instance, bstack1l111l11l11_opy_)
        TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack11llll111ll_opy_, []).clear()
    def bstack1l111l1111l_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1ll111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡹ࡮ࡥࠡࡊࡲࡳࡰࡒࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡶ࡭ࡲ࡯࡬ࡢࡴࠣࡸࡴࠦࡴࡩࡧࠣࡎࡦࡼࡡࠡ࡫ࡰࡴࡱ࡫࡭ࡦࡰࡷࡥࡹ࡯࡯࡯࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤ࡙࡮ࡩࡴࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡅ࡫ࡩࡨࡱࡳࠡࡶ࡫ࡩࠥࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤ࡮ࡴࡳࡪࡦࡨࠤࢃ࠵࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠵ࡕࡱ࡮ࡲࡥࡩ࡫ࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡋࡵࡲࠡࡧࡤࡧ࡭ࠦࡦࡪ࡮ࡨࠤ࡮ࡴࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠯ࠤࡷ࡫ࡰ࡭ࡣࡦࡩࡸࠦࠢࡕࡧࡶࡸࡑ࡫ࡶࡦ࡮ࠥࠤࡼ࡯ࡴࡩࠢࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠨࠠࡪࡰࠣ࡭ࡹࡹࠠࡱࡣࡷ࡬࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡎ࡬ࠠࡢࠢࡩ࡭ࡱ࡫ࠠࡪࡰࠣࡸ࡭࡫ࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡱࡦࡺࡣࡩࡧࡶࠤࡦࠦ࡭ࡰࡦ࡬ࡪ࡮࡫ࡤࠡࡪࡲࡳࡰ࠳࡬ࡦࡸࡨࡰࠥ࡬ࡩ࡭ࡧ࠯ࠤ࡮ࡺࠠࡤࡴࡨࡥࡹ࡫ࡳࠡࡣࠣࡐࡴ࡭ࡅ࡯ࡶࡵࡽࠥࡵࡢ࡫ࡧࡦࡸࠥࡽࡩࡵࡪࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡥࡧࡷࡥ࡮ࡲࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡔ࡫ࡰ࡭ࡱࡧࡲ࡭ࡻ࠯ࠤ࡮ࡺࠠࡱࡴࡲࡧࡪࡹࡳࡦࡵࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷࠥࡲ࡯ࡤࡣࡷࡩࡩࠦࡩ࡯ࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡧࡿࠠࡳࡧࡳࡰࡦࡩࡩ࡯ࡩࠣࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠣࠢࡺ࡭ࡹ࡮ࠠࠣࡊࡲࡳࡰࡒࡥࡷࡧ࡯࠳ࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠥ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡘ࡭࡫ࠠࡤࡴࡨࡥࡹ࡫ࡤࠡࡎࡲ࡫ࡊࡴࡴࡳࡻࠣࡳࡧࡰࡥࡤࡶࡶࠤࡦࡸࡥࠡࡣࡧࡨࡪࡪࠠࡵࡱࠣࡸ࡭࡫ࠠࡩࡱࡲ࡯ࠬࡹࠠࠣ࡮ࡲ࡫ࡸࠨࠠ࡭࡫ࡶࡸ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡭ࡵ࡯࡬࠼ࠣࡘ࡭࡫ࠠࡦࡸࡨࡲࡹࠦࡤࡪࡥࡷ࡭ࡴࡴࡡࡳࡻࠣࡧࡴࡴࡴࡢ࡫ࡱ࡭ࡳ࡭ࠠࡦࡺ࡬ࡷࡹ࡯࡮ࡨࠢ࡯ࡳ࡬ࡹࠠࡢࡰࡧࠤ࡭ࡵ࡯࡬ࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡨࡰࡱ࡮ࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩ࡚ࠥࡥࡴࡶࡏࡩࡻ࡫࡬ࠡ࡯ࡲࡲ࡮ࡺ࡯ࡳ࡫ࡱ࡫࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡧࡻࡩ࡭ࡦࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡔࡦࡺࡨࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡ࡯ࡲࡲ࡮ࡺ࡯ࡳ࡫ࡱ࡫࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥᖥ")
        global _1l1ll1l11l1_opy_
        platform_index = os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᖦ")]
        bstack1l1l1l11lll_opy_ = os.path.join(bstack1l1l1lllll1_opy_, (bstack1l1l1llll1l_opy_ + str(platform_index)), bstack11lll1l11l1_opy_)
        if not os.path.exists(bstack1l1l1l11lll_opy_) or not os.path.isdir(bstack1l1l1l11lll_opy_):
            self.logger.debug(bstack1ll111_opy_ (u"ࠨࡄࡪࡴࡨࡧࡹࡵࡲࡺࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶࡶࠤࡹࡵࠠࡱࡴࡲࡧࡪࡹࡳࠡࡽࢀࠦᖧ").format(bstack1l1l1l11lll_opy_))
            return
        logs = hook.get(bstack1ll111_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᖨ"), [])
        with os.scandir(bstack1l1l1l11lll_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll1l11l1_opy_:
                    self.logger.info(bstack1ll111_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᖩ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1ll111_opy_ (u"ࠤࠥᖪ")
                    log_entry = bstack1ll1ll1llll_opy_(
                        kind=bstack1ll111_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᖫ"),
                        message=bstack1ll111_opy_ (u"ࠦࠧᖬ"),
                        level=bstack1ll111_opy_ (u"ࠧࠨᖭ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1l1111l_opy_=entry.stat().st_size,
                        bstack1l1l1ll1111_opy_=bstack1ll111_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᖮ"),
                        bstack1111lll_opy_=os.path.abspath(entry.path),
                        bstack1l11111ll1l_opy_=hook.get(TestFramework.bstack1l1111l1l1l_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll1l11l1_opy_.add(abs_path)
        platform_index = os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᖯ")]
        bstack11lll1ll11l_opy_ = os.path.join(bstack1l1l1lllll1_opy_, (bstack1l1l1llll1l_opy_ + str(platform_index)), bstack11lll1l11l1_opy_, bstack11lll1l1l1l_opy_)
        if not os.path.exists(bstack11lll1ll11l_opy_) or not os.path.isdir(bstack11lll1ll11l_opy_):
            self.logger.info(bstack1ll111_opy_ (u"ࠣࡐࡲࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤ࡫ࡵࡵ࡯ࡦࠣࡥࡹࡀࠠࡼࡿࠥᖰ").format(bstack11lll1ll11l_opy_))
        else:
            self.logger.info(bstack1ll111_opy_ (u"ࠤࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡪࡷࡵ࡭ࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠾ࠥࢁࡽࠣᖱ").format(bstack11lll1ll11l_opy_))
            with os.scandir(bstack11lll1ll11l_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll1l11l1_opy_:
                        self.logger.info(bstack1ll111_opy_ (u"ࠥࡔࡦࡺࡨࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥࢁࡽࠣᖲ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1ll111_opy_ (u"ࠦࠧᖳ")
                        log_entry = bstack1ll1ll1llll_opy_(
                            kind=bstack1ll111_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢᖴ"),
                            message=bstack1ll111_opy_ (u"ࠨࠢᖵ"),
                            level=bstack1ll111_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠦᖶ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1l1111l_opy_=entry.stat().st_size,
                            bstack1l1l1ll1111_opy_=bstack1ll111_opy_ (u"ࠣࡏࡄࡒ࡚ࡇࡌࡠࡗࡓࡐࡔࡇࡄࠣᖷ"),
                            bstack1111lll_opy_=os.path.abspath(entry.path),
                            bstack1l1l11lllll_opy_=hook.get(TestFramework.bstack1l1111l1l1l_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll1l11l1_opy_.add(abs_path)
        hook[bstack1ll111_opy_ (u"ࠤ࡯ࡳ࡬ࡹࠢᖸ")] = logs
    def bstack1l1l1ll111l_opy_(
        self,
        bstack1l1ll111l11_opy_: bstack1ll1l1ll1ll_opy_,
        entries: List[bstack1ll1ll1llll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡗࡊ࡙ࡓࡊࡑࡑࡣࡎࡊࠢᖹ"))
        req.platform_index = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1ll11ll1111_opy_)
        req.execution_context.hash = str(bstack1l1ll111l11_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll111l11_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll111l11_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1l1lllll1ll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llll11l1ll_opy_(bstack1l1ll111l11_opy_, TestFramework.bstack1l1ll1111ll_opy_)
            log_entry.uuid = entry.bstack1l11111ll1l_opy_
            log_entry.test_framework_state = bstack1l1ll111l11_opy_.state.name
            log_entry.message = entry.message.encode(bstack1ll111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᖺ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack1ll111_opy_ (u"ࠧࠨᖻ")
            if entry.kind == bstack1ll111_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᖼ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1l1111l_opy_
                log_entry.file_path = entry.bstack1111lll_opy_
        def bstack1l1ll111ll1_opy_():
            bstack111ll1ll1_opy_ = datetime.now()
            try:
                self.bstack1lll1l11lll_opy_.LogCreatedEvent(req)
                bstack1l1ll111l11_opy_.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡹࡥ࡯ࡦࡢࡰࡴ࡭࡟ࡤࡴࡨࡥࡹ࡫ࡤࡠࡧࡹࡩࡳࡺ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠦᖽ"), datetime.now() - bstack111ll1ll1_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1ll111_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࡹࡥ࡯ࡦࡢࡰࡴ࡭࡟ࡤࡴࡨࡥࡹ࡫ࡤࡠࡧࡹࡩࡳࡺ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࢀࢃࠢᖾ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllll1llll_opy_.enqueue(bstack1l1ll111ll1_opy_)
    def __1l1111l1ll1_opy_(self, instance) -> None:
        bstack1ll111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡌࡰࡣࡧࡷࠥࡩࡵࡴࡶࡲࡱࠥࡺࡡࡨࡵࠣࡪࡴࡸࠠࡵࡪࡨࠤ࡬࡯ࡶࡦࡰࠣࡸࡪࡹࡴࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡵࡩࡦࡺࡥࡴࠢࡤࠤࡩ࡯ࡣࡵࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡱ࡫ࡶࡦ࡮ࠣࡧࡺࡹࡴࡰ࡯ࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࡤࠡࡨࡵࡳࡲࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡷࡶࡸࡴࡳࡔࡢࡩࡐࡥࡳࡧࡧࡦࡴࠣࡥࡳࡪࠠࡶࡲࡧࡥࡹ࡫ࡳࠡࡶ࡫ࡩࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡴࡶࡤࡸࡪࠦࡵࡴ࡫ࡱ࡫ࠥࡹࡥࡵࡡࡶࡸࡦࡺࡥࡠࡧࡱࡸࡷ࡯ࡥࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᖿ")
        bstack11llll11111_opy_ = {bstack1ll111_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯ࡢࡱࡪࡺࡡࡥࡣࡷࡥࠧᗀ"): bstack1lll11l1l11_opy_.bstack1l111l11l1l_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack1l11111l11l_opy_(instance, bstack11llll11111_opy_)
    @staticmethod
    def bstack11lllll1l1l_opy_(instance: bstack1ll1l1ll1ll_opy_, bstack1l111l11l11_opy_: str):
        bstack1l1111l1lll_opy_ = (
            bstack1ll1ll1ll11_opy_.bstack1l1111l1l11_opy_
            if bstack1l111l11l11_opy_ == bstack1ll1ll1ll11_opy_.bstack1l11111l1l1_opy_
            else bstack1ll1ll1ll11_opy_.bstack1l1111lll1l_opy_
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
        hook = bstack1ll1ll1ll11_opy_.bstack11lllll1l1l_opy_(instance, bstack1l111l11l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack11lllll1lll_opy_, []).clear()
    @staticmethod
    def __11lllll1ll1_opy_(instance: bstack1ll1l1ll1ll_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1ll111_opy_ (u"ࠦ࡬࡫ࡴࡠࡴࡨࡧࡴࡸࡤࡴࠤᗁ"), None)):
            return
        if os.getenv(bstack1ll111_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡆࡍࡃࡊࡣࡑࡕࡇࡔࠤᗂ"), bstack1ll111_opy_ (u"ࠨ࠱ࠣᗃ")) != bstack1ll111_opy_ (u"ࠢ࠲ࠤᗄ"):
            bstack1ll1ll1ll11_opy_.logger.warning(bstack1ll111_opy_ (u"ࠣ࡫ࡪࡲࡴࡸࡩ࡯ࡩࠣࡧࡦࡶ࡬ࡰࡩࠥᗅ"))
            return
        bstack11lll1l1lll_opy_ = {
            bstack1ll111_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣᗆ"): (bstack1ll1ll1ll11_opy_.bstack11lllll11ll_opy_, bstack1ll1ll1ll11_opy_.bstack1l1111lll1l_opy_),
            bstack1ll111_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧᗇ"): (bstack1ll1ll1ll11_opy_.bstack1l11111l1l1_opy_, bstack1ll1ll1ll11_opy_.bstack1l1111l1l11_opy_),
        }
        for when in (bstack1ll111_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࠥᗈ"), bstack1ll111_opy_ (u"ࠧࡩࡡ࡭࡮ࠥᗉ"), bstack1ll111_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࠣᗊ")):
            bstack1l111111lll_opy_ = args[1].get_records(when)
            if not bstack1l111111lll_opy_:
                continue
            records = [
                bstack1ll1ll1llll_opy_(
                    kind=TestFramework.bstack1l1l1ll11ll_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1ll111_opy_ (u"ࠢ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠥᗋ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1ll111_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡥࠤᗌ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111111lll_opy_
                if isinstance(getattr(r, bstack1ll111_opy_ (u"ࠤࡰࡩࡸࡹࡡࡨࡧࠥᗍ"), None), str) and r.message.strip()
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
    def __1l1111lll11_opy_(test) -> Dict[str, Any]:
        bstack1l1lllll11_opy_ = bstack1ll1ll1ll11_opy_.__1l111l111ll_opy_(test.location) if hasattr(test, bstack1ll111_opy_ (u"ࠥࡰࡴࡩࡡࡵ࡫ࡲࡲࠧᗎ")) else getattr(test, bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᗏ"), None)
        test_name = test.name if hasattr(test, bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᗐ")) else None
        bstack11llll1111l_opy_ = test.fspath.strpath if hasattr(test, bstack1ll111_opy_ (u"ࠨࡦࡴࡲࡤࡸ࡭ࠨᗑ")) and test.fspath else None
        if not bstack1l1lllll11_opy_ or not test_name or not bstack11llll1111l_opy_:
            return None
        code = None
        if hasattr(test, bstack1ll111_opy_ (u"ࠢࡰࡤ࡭ࠦᗒ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack11lll1l111l_opy_ = []
        try:
            bstack11lll1l111l_opy_ = bstack1llll1111_opy_.bstack111l111l11_opy_(test)
        except:
            bstack1ll1ll1ll11_opy_.logger.warning(bstack1ll111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡷࡩࡸࡺࠠࡴࡥࡲࡴࡪࡹࠬࠡࡶࡨࡷࡹࠦࡳࡤࡱࡳࡩࡸࠦࡷࡪ࡮࡯ࠤࡧ࡫ࠠࡳࡧࡶࡳࡱࡼࡥࡥࠢ࡬ࡲࠥࡉࡌࡊࠤᗓ"))
        return {
            TestFramework.bstack1ll11l111ll_opy_: uuid4().__str__(),
            TestFramework.bstack11lllll1l11_opy_: bstack1l1lllll11_opy_,
            TestFramework.bstack1l1llll11l1_opy_: test_name,
            TestFramework.bstack1l1l111111l_opy_: getattr(test, bstack1ll111_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᗔ"), None),
            TestFramework.bstack11lllllll11_opy_: bstack11llll1111l_opy_,
            TestFramework.bstack1l11111ll11_opy_: bstack1ll1ll1ll11_opy_.__11lllll1111_opy_(test),
            TestFramework.bstack1l11111lll1_opy_: code,
            TestFramework.bstack1l11l1lll11_opy_: TestFramework.bstack1l1111111ll_opy_,
            TestFramework.bstack1l111lllll1_opy_: bstack1l1lllll11_opy_,
            TestFramework.bstack11lll1l1l11_opy_: bstack11lll1l111l_opy_
        }
    @staticmethod
    def __11lllll1111_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack1ll111_opy_ (u"ࠥࡳࡼࡴ࡟࡮ࡣࡵ࡯ࡪࡸࡳࠣᗕ"), [])
            markers.extend([getattr(m, bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᗖ"), None) for m in own_markers if getattr(m, bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᗗ"), None)])
            current = getattr(current, bstack1ll111_opy_ (u"ࠨࡰࡢࡴࡨࡲࡹࠨᗘ"), None)
        return markers
    @staticmethod
    def __1l111l111ll_opy_(location):
        return bstack1ll111_opy_ (u"ࠢ࠻࠼ࠥᗙ").join(filter(lambda x: isinstance(x, str), location))