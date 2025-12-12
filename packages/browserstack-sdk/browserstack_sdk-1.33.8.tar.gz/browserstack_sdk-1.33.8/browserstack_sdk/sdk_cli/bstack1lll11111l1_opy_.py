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
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1llll1lll1l_opy_,
    bstack1lllll11111_opy_,
    bstack1lllll1l11l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_, bstack1ll1l1ll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1l1lll111l1_opy_ import bstack1l1ll1lll1l_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l11l1l1l_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1lll11lll1l_opy_(bstack1l1ll1lll1l_opy_):
    bstack1l11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩࡸࡩࡷࡧࡵࡷࠧᐟ")
    bstack1l1l1l1l1l1_opy_ = bstack1ll111_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡸࠨᐠ")
    bstack1l11ll11111_opy_ = bstack1ll111_opy_ (u"ࠣࡰࡲࡲࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡵࠥᐡ")
    bstack1l11l1lll1l_opy_ = bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤᐢ")
    bstack1l11ll1ll1l_opy_ = bstack1ll111_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡡࡵࡩ࡫ࡹࠢᐣ")
    bstack1l1ll11lll1_opy_ = bstack1ll111_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡦࡶࡪࡧࡴࡦࡦࠥᐤ")
    bstack1l11ll11l1l_opy_ = bstack1ll111_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡲࡦࡳࡥࠣᐥ")
    bstack1l11ll11ll1_opy_ = bstack1ll111_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡸࡺࡡࡵࡷࡶࠦᐦ")
    def __init__(self):
        super().__init__(bstack1l1ll1lll11_opy_=self.bstack1l11ll111ll_opy_, frameworks=[bstack1lll11l11ll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.BEFORE_EACH, bstack1lll1l1llll_opy_.POST), self.bstack1l111llll11_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.PRE), self.bstack1ll11l1l1l1_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST), self.bstack1ll11l111l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l111llll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l11ll111_opy_ = self.bstack1l111llllll_opy_(instance.context)
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡣࡦࡩࡴࡪࡸࡨࡣࡩࡸࡩࡷࡧࡵࡷ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࠥᐧ") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠣࠤᐨ"))
        f.bstack1llll11l11l_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, bstack1l1l11ll111_opy_)
        bstack1l111ll1lll_opy_ = self.bstack1l111llllll_opy_(instance.context, bstack1l111lll1ll_opy_=False)
        f.bstack1llll11l11l_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11111_opy_, bstack1l111ll1lll_opy_)
    def bstack1ll11l1l1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111llll11_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if not f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11l1l_opy_, False):
            self.__1l111llll1l_opy_(f,instance,bstack1llll11ll1l_opy_)
    def bstack1ll11l111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111llll11_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if not f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11l1l_opy_, False):
            self.__1l111llll1l_opy_(f, instance, bstack1llll11ll1l_opy_)
        if not f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11ll1_opy_, False):
            self.__1l111lll11l_opy_(f, instance, bstack1llll11ll1l_opy_)
    def bstack1l111lll111_opy_(
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
        if not f.bstack1l1lll1111l_opy_(instance):
            return
        if f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11ll1_opy_, False):
            return
        driver.execute_script(
            bstack1ll111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢᐩ").format(
                json.dumps(
                    {
                        bstack1ll111_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥᐪ"): bstack1ll111_opy_ (u"ࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢᐫ"),
                        bstack1ll111_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᐬ"): {bstack1ll111_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨᐭ"): result},
                    }
                )
            )
        )
        f.bstack1llll11l11l_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11ll1_opy_, True)
    def bstack1l111llllll_opy_(self, context: bstack1lllll1l11l_opy_, bstack1l111lll1ll_opy_= True):
        if bstack1l111lll1ll_opy_:
            bstack1l1l11ll111_opy_ = self.bstack1l1ll1ll111_opy_(context, reverse=True)
        else:
            bstack1l1l11ll111_opy_ = self.bstack1l1ll1l1lll_opy_(context, reverse=True)
        return [f for f in bstack1l1l11ll111_opy_ if f[1].state != bstack1llll1l1111_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1l1ll1l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1l111lll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠧᐮ")).get(bstack1ll111_opy_ (u"ࠣࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧᐯ")):
            bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
            if not bstack1l1l11ll111_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᐰ") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠥࠦᐱ"))
                return
            driver = bstack1l1l11ll111_opy_[0][0]()
            status = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l11l1lll11_opy_, None)
            if not status:
                self.logger.debug(bstack1ll111_opy_ (u"ࠦࡸ࡫ࡴࡠࡣࡦࡸ࡮ࡼࡥࡠࡦࡵ࡭ࡻ࡫ࡲࡴ࠼ࠣࡲࡴࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡸࡪࡹࡴ࠭ࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࠨᐲ") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠧࠨᐳ"))
                return
            bstack1l11ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨᐴ"): status.lower()}
            bstack1l11ll11lll_opy_ = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l11ll1l11l_opy_, None)
            if status.lower() == bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᐵ") and bstack1l11ll11lll_opy_ is not None:
                bstack1l11ll11l11_opy_[bstack1ll111_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨᐶ")] = bstack1l11ll11lll_opy_[0][bstack1ll111_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᐷ")][0] if isinstance(bstack1l11ll11lll_opy_, list) else str(bstack1l11ll11lll_opy_)
            driver.execute_script(
                bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠣᐸ").format(
                    json.dumps(
                        {
                            bstack1ll111_opy_ (u"ࠦࡦࡩࡴࡪࡱࡱࠦᐹ"): bstack1ll111_opy_ (u"ࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣᐺ"),
                            bstack1ll111_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤᐻ"): bstack1l11ll11l11_opy_,
                        }
                    )
                )
            )
            f.bstack1llll11l11l_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11ll1_opy_, True)
    @measure(event_name=EVENTS.bstack1l1lll1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1l111llll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠧᐼ")).get(bstack1ll111_opy_ (u"ࠣࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥᐽ")):
            test_name = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l111lllll1_opy_, None)
            if not test_name:
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣᐾ"))
                return
            bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
            if not bstack1l1l11ll111_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᐿ") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠦࠧᑀ"))
                return
            for bstack1l1l1111lll_opy_, bstack1l111lll1l1_opy_ in bstack1l1l11ll111_opy_:
                if not bstack1lll11l11ll_opy_.bstack1l1lll1111l_opy_(bstack1l111lll1l1_opy_):
                    continue
                driver = bstack1l1l1111lll_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1ll111_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥᑁ").format(
                        json.dumps(
                            {
                                bstack1ll111_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨᑂ"): bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠣᑃ"),
                                bstack1ll111_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦᑄ"): {bstack1ll111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᑅ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1llll11l11l_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11l1l_opy_, True)
    def bstack1l1l11l1l11_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        f: TestFramework,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111llll11_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        bstack1l1l11ll111_opy_ = [d for d, _ in f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])]
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠢࡷࡳࠥࡲࡩ࡯࡭ࠥᑆ"))
            return
        if not bstack1l1l11l1l1l_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࡵࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠤᑇ"))
            return
        for bstack1l111ll1l11_opy_ in bstack1l1l11ll111_opy_:
            driver = bstack1l111ll1l11_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1ll111_opy_ (u"ࠧࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡘࡿ࡮ࡤ࠼ࠥᑈ") + str(timestamp)
            driver.execute_script(
                bstack1ll111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠦᑉ").format(
                    json.dumps(
                        {
                            bstack1ll111_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢᑊ"): bstack1ll111_opy_ (u"ࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥᑋ"),
                            bstack1ll111_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧᑌ"): {
                                bstack1ll111_opy_ (u"ࠥࡸࡾࡶࡥࠣᑍ"): bstack1ll111_opy_ (u"ࠦࡆࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠣᑎ"),
                                bstack1ll111_opy_ (u"ࠧࡪࡡࡵࡣࠥᑏ"): data,
                                bstack1ll111_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࠧᑐ"): bstack1ll111_opy_ (u"ࠢࡥࡧࡥࡹ࡬ࠨᑑ")
                            }
                        }
                    )
                )
            )
    def bstack1l1l11lll1l_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        f: TestFramework,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l111llll11_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        keys = [
            bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_,
            bstack1lll11lll1l_opy_.bstack1l11ll11111_opy_,
        ]
        bstack1l1l11ll111_opy_ = []
        for key in keys:
            bstack1l1l11ll111_opy_.extend(f.bstack1llll11l1ll_opy_(instance, key, []))
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡥࡳࡿࠠࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠢࡷࡳࠥࡲࡩ࡯࡭ࠥᑒ"))
            return
        if f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1ll11lll1_opy_, False):
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡇࡇ࡚ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡥࡵࡩࡦࡺࡥࡥࠤᑓ"))
            return
        self.bstack1ll1111l1ll_opy_()
        bstack111ll1ll1_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11ll1111_opy_)
        req.test_framework_name = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1lllll1ll_opy_)
        req.test_framework_version = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1ll1111ll_opy_)
        req.test_framework_state = bstack1llll11ll1l_opy_[0].name
        req.test_hook_state = bstack1llll11ll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11l111ll_opy_)
        for bstack1l1l1111lll_opy_, driver in bstack1l1l11ll111_opy_:
            try:
                webdriver = bstack1l1l1111lll_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1ll111_opy_ (u"࡛ࠥࡪࡨࡄࡳ࡫ࡹࡩࡷࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡ࡫ࡶࠤࡓࡵ࡮ࡦࠢࠫࡶࡪ࡬ࡥࡳࡧࡱࡧࡪࠦࡥࡹࡲ࡬ࡶࡪࡪࠩࠣᑔ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1ll111_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠥᑕ")
                    if bstack1lll11l11ll_opy_.bstack1llll11l1ll_opy_(driver, bstack1lll11l11ll_opy_.bstack1l111ll11ll_opy_, False)
                    else bstack1ll111_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠦᑖ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1lll11l11ll_opy_.bstack1llll11l1ll_opy_(driver, bstack1lll11l11ll_opy_.bstack1l11lll1111_opy_, bstack1ll111_opy_ (u"ࠨࠢᑗ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1lll11l11ll_opy_.bstack1llll11l1ll_opy_(driver, bstack1lll11l11ll_opy_.bstack1l11ll1lll1_opy_, bstack1ll111_opy_ (u"ࠢࠣᑘ"))
                caps = None
                if hasattr(webdriver, bstack1ll111_opy_ (u"ࠣࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠢᑙ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1ll111_opy_ (u"ࠤࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࡧࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡨ࡮ࡸࡥࡤࡶ࡯ࡽࠥ࡬ࡲࡰ࡯ࠣࡨࡷ࡯ࡶࡦࡴ࠱ࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤᑚ"))
                    except Exception as e:
                        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡶࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡩࡶࡴࡳࠠࡥࡴ࡬ࡺࡪࡸ࠮ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࡀࠠࠣᑛ") + str(e) + bstack1ll111_opy_ (u"ࠦࠧᑜ"))
                try:
                    bstack1l111ll1l1l_opy_ = json.dumps(caps).encode(bstack1ll111_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᑝ")) if caps else bstack1l111ll1ll1_opy_ (u"ࠨࡻࡾࠤᑞ")
                    req.capabilities = bstack1l111ll1l1l_opy_
                except Exception as e:
                    self.logger.debug(bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡣࡨࡨࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫࡮ࡥࠢࡶࡩࡷ࡯ࡡ࡭࡫ࡽࡩࠥࡩࡡࡱࡵࠣࡪࡴࡸࠠࡳࡧࡴࡹࡪࡹࡴ࠻ࠢࠥᑟ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤᑠ"))
            except Exception as e:
                self.logger.error(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥࡪࡲࡪࡸࡨࡶࠥ࡯ࡴࡦ࡯࠽ࠤࠧᑡ") + str(str(e)) + bstack1ll111_opy_ (u"ࠥࠦᑢ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll111l11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l1l11l1l1l_opy_() and len(bstack1l1l11ll111_opy_) == 0:
            bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11111_opy_, [])
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᑣ") + str(kwargs) + bstack1ll111_opy_ (u"ࠧࠨᑤ"))
            return {}
        if len(bstack1l1l11ll111_opy_) > 1:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᑥ") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣᑦ"))
            return {}
        bstack1l1l1111lll_opy_, bstack1l1l1111l11_opy_ = bstack1l1l11ll111_opy_[0]
        driver = bstack1l1l1111lll_opy_()
        if not driver:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑧ") + str(kwargs) + bstack1ll111_opy_ (u"ࠤࠥᑨ"))
            return {}
        capabilities = f.bstack1llll11l1ll_opy_(bstack1l1l1111l11_opy_, bstack1lll11l11ll_opy_.bstack1l11lll1l1l_opy_)
        if not capabilities:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠠࡧࡱࡸࡲࡩࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᑩ") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧᑪ"))
            return {}
        return capabilities.get(bstack1ll111_opy_ (u"ࠧࡧ࡬ࡸࡣࡼࡷࡒࡧࡴࡤࡪࠥᑫ"), {})
    def bstack1ll1111ll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l1l11l1l1l_opy_() and len(bstack1l1l11ll111_opy_) == 0:
            bstack1l1l11ll111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll11lll1l_opy_.bstack1l11ll11111_opy_, [])
        if not bstack1l1l11ll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᑬ") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣᑭ"))
            return
        if len(bstack1l1l11ll111_opy_) > 1:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࡱ࡫࡮ࠩࡦࡵ࡭ࡻ࡫ࡲࡠ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡶ࠭ࢂࠦࡤࡳ࡫ࡹࡩࡷࡹࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᑮ") + str(kwargs) + bstack1ll111_opy_ (u"ࠤࠥᑯ"))
        bstack1l1l1111lll_opy_, bstack1l1l1111l11_opy_ = bstack1l1l11ll111_opy_[0]
        driver = bstack1l1l1111lll_opy_()
        if not driver:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᑰ") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧᑱ"))
            return
        return driver