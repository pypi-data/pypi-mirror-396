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
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1lllll11111_opy_,
    bstack1lllll1l11l_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1l11l1l1l_opy_, bstack11l11l11l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_, bstack1ll1l1ll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllllll_opy_ import bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1l1lll111l1_opy_ import bstack1l1ll1lll1l_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1l11l1111_opy_ import bstack1l111l1l11_opy_, bstack11ll1ll11_opy_, bstack1l1l1ll1l1_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1lll1l1ll1l_opy_(bstack1l1ll1lll1l_opy_):
    bstack1l11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡷ࡯ࡶࡦࡴࡶࠦ፯")
    bstack1l1l1l1l1l1_opy_ = bstack1ll111_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧ፰")
    bstack1l11ll11111_opy_ = bstack1ll111_opy_ (u"ࠢ࡯ࡱࡱࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤ፱")
    bstack1l11l1lll1l_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣ፲")
    bstack1l11ll1ll1l_opy_ = bstack1ll111_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡠࡴࡨࡪࡸࠨ፳")
    bstack1l1ll11lll1_opy_ = bstack1ll111_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡥࡵࡩࡦࡺࡥࡥࠤ፴")
    bstack1l11ll11l1l_opy_ = bstack1ll111_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢ፵")
    bstack1l11ll11ll1_opy_ = bstack1ll111_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠥ፶")
    def __init__(self):
        super().__init__(bstack1l1ll1lll11_opy_=self.bstack1l11ll111ll_opy_, frameworks=[bstack1lll11l11ll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.BEFORE_EACH, bstack1lll1l1llll_opy_.POST), self.bstack1l11l1lllll_opy_)
        if bstack11l11l11l_opy_():
            TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST), self.bstack1ll11l1l1l1_opy_)
        else:
            TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.PRE), self.bstack1ll11l1l1l1_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST), self.bstack1ll11l111l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1lllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11ll1l111_opy_ = self.bstack1l11ll1ll11_opy_(instance.context)
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡴࡦ࡭ࡥ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦ፷") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠢࠣ፸"))
            return
        f.bstack1llll11l11l_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1l1l1l1l1_opy_, bstack1l11ll1l111_opy_)
    def bstack1l11ll1ll11_opy_(self, context: bstack1lllll1l11l_opy_, bstack1l11ll1l1ll_opy_= True):
        if bstack1l11ll1l1ll_opy_:
            bstack1l11ll1l111_opy_ = self.bstack1l1ll1ll111_opy_(context, reverse=True)
        else:
            bstack1l11ll1l111_opy_ = self.bstack1l1ll1l1lll_opy_(context, reverse=True)
        return [f for f in bstack1l11ll1l111_opy_ if f[1].state != bstack1llll1l1111_opy_.QUIT]
    def bstack1ll11l1l1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if not bstack1l1l11l1l1l_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦ፹") + str(kwargs) + bstack1ll111_opy_ (u"ࠤࠥ፺"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨ፻") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧ፼"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll11ll11l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡶࡡࡨࡧࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁ࡫ࡸࡣࡵ࡫ࡸࢃࠢ፽"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l11_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨ፾") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣ፿"))
            return
        bstack1l1lll11_opy_ = getattr(args[0], bstack1ll111_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᎀ"), None)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺࡃࡰࡰࡷࡩࡽࡺࡏࡱࡶ࡬ࡳࡳࡹࠢᎁ")).get(bstack1ll111_opy_ (u"ࠥࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧᎂ")):
            try:
                page.evaluate(bstack1ll111_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧᎃ"),
                            bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩᎄ") + json.dumps(
                                bstack1l1lll11_opy_) + bstack1ll111_opy_ (u"ࠨࡽࡾࠤᎅ"))
            except Exception as e:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁࠧᎆ"), e)
    def bstack1ll11l111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if not bstack1l1l11l1l1l_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎇ") + str(kwargs) + bstack1ll111_opy_ (u"ࠤࠥᎈ"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᎉ") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧᎊ"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll11ll11l_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡶࡡࡨࡧࡢ࡭ࡳࡹࡴࡢࡰࡦࡩࡸ࠯ࡽࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁ࡫ࡸࡣࡵ࡫ࡸࢃࠢᎋ"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l11_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᎌ") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣᎍ"))
            return
        status = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l11l1lll11_opy_, None)
        if not status:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡰࡲࠤࡸࡺࡡࡵࡷࡶࠤ࡫ࡵࡲࠡࡶࡨࡷࡹ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᎎ") + str(bstack1llll11ll1l_opy_) + bstack1ll111_opy_ (u"ࠤࠥᎏ"))
            return
        bstack1l11ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥ᎐"): status.lower()}
        bstack1l11ll11lll_opy_ = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l11ll1l11l_opy_, None)
        if status.lower() == bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ᎑") and bstack1l11ll11lll_opy_ is not None:
            bstack1l11ll11l11_opy_[bstack1ll111_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬ᎒")] = bstack1l11ll11lll_opy_[0][bstack1ll111_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩ᎓")][0] if isinstance(bstack1l11ll11lll_opy_, list) else str(bstack1l11ll11lll_opy_)
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠧ᎔")).get(bstack1ll111_opy_ (u"ࠣࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ᎕")):
            try:
                page.evaluate(
                        bstack1ll111_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ᎖"),
                        bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࠨ᎗")
                        + json.dumps(bstack1l11ll11l11_opy_)
                        + bstack1ll111_opy_ (u"ࠦࢂࠨ᎘")
                    )
            except Exception as e:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢࡾࢁࠧ᎙"), e)
    def bstack1l1l11l1l11_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        f: TestFramework,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if not bstack1l1l11l1l1l_opy_:
            self.logger.debug(
                bstack1lll11ll11l_opy_ (u"ࠨ࡭ࡢࡴ࡮ࡣࡴ࠷࠱ࡺࡡࡶࡽࡳࡩ࠺ࠡࡰࡲࡸࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁ࡫ࡸࡣࡵ࡫ࡸࢃࠢ᎚"))
            return
        bstack1l11ll1l111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ᎛") + str(kwargs) + bstack1ll111_opy_ (u"ࠣࠤ᎜"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(
                bstack1lll11ll11l_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࢀࡲࡥ࡯ࠪࡳࡥ࡬࡫࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࡾ࡯ࡼࡧࡲࡨࡵࢀࠦ᎝"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l11_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡱࡦࡸ࡫ࡠࡱ࠴࠵ࡾࡥࡳࡺࡰࡦ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ᎞") + str(kwargs) + bstack1ll111_opy_ (u"ࠦࠧ᎟"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack1ll111_opy_ (u"ࠧࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡘࡿ࡮ࡤ࠼ࠥᎠ") + str(timestamp)
        try:
            page.evaluate(
                bstack1ll111_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢᎡ"),
                bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬᎢ").format(
                    json.dumps(
                        {
                            bstack1ll111_opy_ (u"ࠣࡣࡦࡸ࡮ࡵ࡮ࠣᎣ"): bstack1ll111_opy_ (u"ࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦᎤ"),
                            bstack1ll111_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨᎥ"): {
                                bstack1ll111_opy_ (u"ࠦࡹࡿࡰࡦࠤᎦ"): bstack1ll111_opy_ (u"ࠧࡇ࡮࡯ࡱࡷࡥࡹ࡯࡯࡯ࠤᎧ"),
                                bstack1ll111_opy_ (u"ࠨࡤࡢࡶࡤࠦᎨ"): data,
                                bstack1ll111_opy_ (u"ࠢ࡭ࡧࡹࡩࡱࠨᎩ"): bstack1ll111_opy_ (u"ࠣࡦࡨࡦࡺ࡭ࠢᎪ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡵ࠱࠲ࡻࠣࡥࡳࡴ࡯ࡵࡣࡷ࡭ࡴࡴࠠ࡮ࡣࡵ࡯࡮ࡴࡧࠡࡽࢀࠦᎫ"), e)
    def bstack1l1l11lll1l_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        f: TestFramework,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        if f.bstack1llll11l1ll_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1ll11lll1_opy_, False):
            return
        self.bstack1ll1111l1ll_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11ll1111_opy_)
        req.test_framework_name = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1lllll1ll_opy_)
        req.test_framework_version = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1ll1111ll_opy_)
        req.test_framework_state = bstack1llll11ll1l_opy_[0].name
        req.test_hook_state = bstack1llll11ll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11l111ll_opy_)
        for bstack1l11ll1l1l1_opy_ in bstack1ll11lll1ll_opy_.bstack1lll1llllll_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠤᎬ")
                if bstack1l1l11l1l1l_opy_
                else bstack1ll111_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࡤ࡭ࡲࡪࡦࠥᎭ")
            )
            session.ref = bstack1l11ll1l1l1_opy_.ref()
            session.hub_url = bstack1ll11lll1ll_opy_.bstack1llll11l1ll_opy_(bstack1l11ll1l1l1_opy_, bstack1ll11lll1ll_opy_.bstack1l11lll1111_opy_, bstack1ll111_opy_ (u"ࠧࠨᎮ"))
            session.framework_name = bstack1l11ll1l1l1_opy_.framework_name
            session.framework_version = bstack1l11ll1l1l1_opy_.framework_version
            session.framework_session_id = bstack1ll11lll1ll_opy_.bstack1llll11l1ll_opy_(bstack1l11ll1l1l1_opy_, bstack1ll11lll1ll_opy_.bstack1l11ll1lll1_opy_, bstack1ll111_opy_ (u"ࠨࠢᎯ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll1111ll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs
    ):
        bstack1l11ll1l111_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll1l1ll1l_opy_.bstack1l1l1l1l1l1_opy_, [])
        if not bstack1l11ll1l111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᎰ") + str(kwargs) + bstack1ll111_opy_ (u"ࠣࠤᎱ"))
            return
        if len(bstack1l11ll1l111_opy_) > 1:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀࡲࡥ࡯ࠪࡳࡥ࡬࡫࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᎲ") + str(kwargs) + bstack1ll111_opy_ (u"ࠥࠦᎳ"))
        bstack1l11ll111l1_opy_, bstack1l1l1111l11_opy_ = bstack1l11ll1l111_opy_[0]
        page = bstack1l11ll111l1_opy_()
        if not page:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡪࡲࡪࡸࡨࡶ࠿ࠦ࡮ࡰࠢࡳࡥ࡬࡫ࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎴ") + str(kwargs) + bstack1ll111_opy_ (u"ࠧࠨᎵ"))
            return
        return page
    def bstack1ll111l11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l11l1llll1_opy_ = {}
        for bstack1l11ll1l1l1_opy_ in bstack1ll11lll1ll_opy_.bstack1lll1llllll_opy_.values():
            caps = bstack1ll11lll1ll_opy_.bstack1llll11l1ll_opy_(bstack1l11ll1l1l1_opy_, bstack1ll11lll1ll_opy_.bstack1l11lll1l1l_opy_, bstack1ll111_opy_ (u"ࠨࠢᎶ"))
        bstack1l11l1llll1_opy_[bstack1ll111_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧᎷ")] = caps.get(bstack1ll111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࠤᎸ"), bstack1ll111_opy_ (u"ࠤࠥᎹ"))
        bstack1l11l1llll1_opy_[bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤᎺ")] = caps.get(bstack1ll111_opy_ (u"ࠦࡴࡹࠢᎻ"), bstack1ll111_opy_ (u"ࠧࠨᎼ"))
        bstack1l11l1llll1_opy_[bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣᎽ")] = caps.get(bstack1ll111_opy_ (u"ࠢࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠦᎾ"), bstack1ll111_opy_ (u"ࠣࠤᎿ"))
        bstack1l11l1llll1_opy_[bstack1ll111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥᏀ")] = caps.get(bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧᏁ"), bstack1ll111_opy_ (u"ࠦࠧᏂ"))
        return bstack1l11l1llll1_opy_
    def bstack1ll111111l1_opy_(self, page: object, bstack1ll11111l11_opy_, args={}):
        try:
            bstack1l11ll1111l_opy_ = bstack1ll111_opy_ (u"ࠧࠨࠢࠩࡨࡸࡲࡨࡺࡩࡰࡰࠣࠬ࠳࠴࠮ࡣࡵࡷࡥࡨࡱࡓࡥ࡭ࡄࡶ࡬ࡹࠩࠡࡽࡾࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡲࡦࡶࡸࡶࡳࠦ࡮ࡦࡹࠣࡔࡷࡵ࡭ࡪࡵࡨࠬ࠭ࡸࡥࡴࡱ࡯ࡺࡪ࠲ࠠࡳࡧ࡭ࡩࡨࡺࠩࠡ࠿ࡁࠤࢀࢁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸ࠴ࡰࡶࡵ࡫ࠬࡷ࡫ࡳࡰ࡮ࡹࡩ࠮ࡁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡻࡧࡰࡢࡦࡴࡪࡹࡾࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࢃࠩ࠼ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࡿࠬࠬࢀࡧࡲࡨࡡ࡭ࡷࡴࡴࡽࠪࠤࠥࠦᏃ")
            bstack1ll11111l11_opy_ = bstack1ll11111l11_opy_.replace(bstack1ll111_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤᏄ"), bstack1ll111_opy_ (u"ࠢࡣࡵࡷࡥࡨࡱࡓࡥ࡭ࡄࡶ࡬ࡹࠢᏅ"))
            script = bstack1l11ll1111l_opy_.format(fn_body=bstack1ll11111l11_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠣࡣ࠴࠵ࡾࡥࡳࡤࡴ࡬ࡴࡹࡥࡥࡹࡧࡦࡹࡹ࡫࠺ࠡࡇࡵࡶࡴࡸࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣࡸ࡭࡫ࠠࡢ࠳࠴ࡽࠥࡹࡣࡳ࡫ࡳࡸ࠱ࠦࠢᏆ") + str(e) + bstack1ll111_opy_ (u"ࠤࠥᏇ"))