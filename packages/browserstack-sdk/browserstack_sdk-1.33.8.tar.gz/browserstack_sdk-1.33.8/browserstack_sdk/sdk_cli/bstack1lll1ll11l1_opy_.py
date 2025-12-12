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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1llll1lll1l_opy_,
    bstack1lllll11111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_, bstack1ll1l1ll1ll_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll11111l1_opy_ import bstack1lll11lll1l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1l1l_opy_ import bstack1lll1l1ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllllll_opy_ import bstack1ll11lll1ll_opy_
from bstack_utils.helper import bstack1l1llllllll_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
import grpc
import traceback
import json
class bstack1lll1lll111_opy_(bstack1ll1ll1l1l1_opy_):
    bstack1ll111ll1ll_opy_ = False
    bstack1ll11l1l11l_opy_ = bstack1ll111_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥᇒ")
    bstack1l1llll1lll_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࠤᇓ")
    bstack1ll11l11111_opy_ = bstack1ll111_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡪࡰ࡬ࡸࠧᇔ")
    bstack1ll11111lll_opy_ = bstack1ll111_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡶࡣࡸࡩࡡ࡯ࡰ࡬ࡲ࡬ࠨᇕ")
    bstack1ll11111ll1_opy_ = bstack1ll111_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳࡡ࡫ࡥࡸࡥࡵࡳ࡮ࠥᇖ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1ll1ll1l1ll_opy_, bstack1ll1l11111l_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1l1lllll111_opy_ = False
        self.bstack1l1llllll1l_opy_ = dict()
        self.bstack1ll11l1llll_opy_ = False
        self.bstack1l1lllll1l1_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1ll111l1l11_opy_ = bstack1ll1l11111l_opy_
        bstack1ll1ll1l1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1ll1111l111_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.PRE), self.bstack1ll11l1l1l1_opy_)
        TestFramework.bstack1l1llll111l_opy_((bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST), self.bstack1ll11l111l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11l1l1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll111l111l_opy_(instance, args)
        test_framework = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1lllll1ll_opy_)
        if self.bstack1l1lllll111_opy_:
            self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᇗ")] = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11l111ll_opy_)
        if bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨᇘ") in instance.bstack1l1llllll11_opy_:
            platform_index = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11ll1111_opy_)
            self.accessibility = self.bstack1ll111llll1_opy_(tags, self.config[bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᇙ")][platform_index])
        else:
            capabilities = self.bstack1ll111l1l11_opy_.bstack1ll111l11ll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠣࡪࡴࡻ࡮ࡥࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᇚ") + str(kwargs) + bstack1ll111_opy_ (u"ࠢࠣᇛ"))
                return
            self.accessibility = self.bstack1ll111llll1_opy_(tags, capabilities)
        if self.bstack1ll111l1l11_opy_.pages and self.bstack1ll111l1l11_opy_.pages.values():
            bstack1ll111lll11_opy_ = list(self.bstack1ll111l1l11_opy_.pages.values())
            if bstack1ll111lll11_opy_ and isinstance(bstack1ll111lll11_opy_[0], (list, tuple)) and bstack1ll111lll11_opy_[0]:
                bstack1ll11ll111l_opy_ = bstack1ll111lll11_opy_[0][0]
                if callable(bstack1ll11ll111l_opy_):
                    page = bstack1ll11ll111l_opy_()
                    def bstack11lll111l_opy_():
                        self.get_accessibility_results(page, bstack1ll111_opy_ (u"ࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧᇜ"))
                    def bstack1l1lll1llll_opy_():
                        self.get_accessibility_results_summary(page, bstack1ll111_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᇝ"))
                    setattr(page, bstack1ll111_opy_ (u"ࠥ࡫ࡪࡺࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡘࡥࡴࡷ࡯ࡸࡸࠨᇞ"), bstack11lll111l_opy_)
                    setattr(page, bstack1ll111_opy_ (u"ࠦ࡬࡫ࡴࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡒࡦࡵࡸࡰࡹ࡙ࡵ࡮࡯ࡤࡶࡾࠨᇟ"), bstack1l1lll1llll_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠧࡹࡨࡰࡷ࡯ࡨࠥࡸࡵ࡯ࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡹࡥࡱࡻࡥ࠾ࠤᇠ") + str(self.accessibility) + bstack1ll111_opy_ (u"ࠨࠢᇡ"))
    def bstack1ll1111l111_opy_(
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
            bstack111ll1ll1_opy_ = datetime.now()
            self.bstack1ll11111111_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠢࡢ࠳࠴ࡽ࠿࡯࡮ࡪࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡧࡴࡴࡦࡪࡩࠥᇢ"), datetime.now() - bstack111ll1ll1_opy_)
            if (
                not f.bstack1ll111ll111_opy_(method_name)
                or f.bstack1ll111111ll_opy_(method_name, *args)
                or f.bstack1ll1111l11l_opy_(method_name, *args)
            ):
                return
            if not f.bstack1llll11l1ll_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11l11111_opy_, False):
                if not bstack1lll1lll111_opy_.bstack1ll111ll1ll_opy_:
                    self.logger.warning(bstack1ll111_opy_ (u"ࠣ࡝ࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦᇣ") + str(f.platform_index) + bstack1ll111_opy_ (u"ࠤࡠࠤࡦ࠷࠱ࡺࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡪࡤࡺࡪࠦ࡮ࡰࡶࠣࡦࡪ࡫࡮ࠡࡵࡨࡸࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᇤ"))
                    bstack1lll1lll111_opy_.bstack1ll111ll1ll_opy_ = True
                return
            bstack1ll11l11ll1_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1ll11l11ll1_opy_:
                platform_index = f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0)
                self.logger.debug(bstack1ll111_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࡿࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࢂࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᇥ") + str(f.framework_name) + bstack1ll111_opy_ (u"ࠦࠧᇦ"))
                return
            command_name = f.bstack1ll111l1111_opy_(*args)
            if not command_name:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡣࡰ࡯ࡰࡥࡳࡪ࡟࡯ࡣࡰࡩࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࠢᇧ") + str(method_name) + bstack1ll111_opy_ (u"ࠨࠢᇨ"))
                return
            bstack1l1lll1lll1_opy_ = f.bstack1llll11l1ll_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11111ll1_opy_, False)
            if command_name == bstack1ll111_opy_ (u"ࠢࡨࡧࡷࠦᇩ") and not bstack1l1lll1lll1_opy_:
                f.bstack1llll11l11l_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11111ll1_opy_, True)
                bstack1l1lll1lll1_opy_ = True
            if not bstack1l1lll1lll1_opy_ and not self.bstack1l1lllll111_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠣࡰࡲࠤ࡚ࡘࡌࠡ࡮ࡲࡥࡩ࡫ࡤࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᇪ") + str(command_name) + bstack1ll111_opy_ (u"ࠤࠥᇫ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack1ll111_opy_ (u"ࠥࡲࡴࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷࡷࠥ࡬࡯ࡳࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᇬ") + str(command_name) + bstack1ll111_opy_ (u"ࠦࠧᇭ"))
                return
            self.logger.info(bstack1ll111_opy_ (u"ࠧࡸࡵ࡯ࡰ࡬ࡲ࡬ࠦࡻ࡭ࡧࡱࠬࡸࡩࡲࡪࡲࡷࡷࡤࡺ࡯ࡠࡴࡸࡲ࠮ࢃࠠࡴࡥࡵ࡭ࡵࡺࡳࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪ࠳࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࡃࠢᇮ") + str(command_name) + bstack1ll111_opy_ (u"ࠨࠢᇯ"))
            scripts = [(s, bstack1ll11l11ll1_opy_[s]) for s in scripts_to_run if s in bstack1ll11l11ll1_opy_]
            for script_name, bstack1ll11111l11_opy_ in scripts:
                try:
                    bstack111ll1ll1_opy_ = datetime.now()
                    if script_name == bstack1ll111_opy_ (u"ࠢࡴࡥࡤࡲࠧᇰ"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                    instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࠢᇱ") + script_name, datetime.now() - bstack111ll1ll1_opy_)
                    if isinstance(result, dict) and not result.get(bstack1ll111_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥᇲ"), True):
                        self.logger.warning(bstack1ll111_opy_ (u"ࠥࡷࡰ࡯ࡰࠡࡧࡻࡩࡨࡻࡴࡪࡰࡪࠤࡷ࡫࡭ࡢ࡫ࡱ࡭ࡳ࡭ࠠࡴࡥࡵ࡭ࡵࡺࡳ࠻ࠢࠥᇳ") + str(result) + bstack1ll111_opy_ (u"ࠦࠧᇴ"))
                        break
                except Exception as e:
                    self.logger.error(bstack1ll111_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠤࡪࡾࡥࡤࡷࡷ࡭ࡳ࡭ࠠࡴࡥࡵ࡭ࡵࡺ࠽ࡼࡵࡦࡶ࡮ࡶࡴࡠࡰࡤࡱࡪࢃࠠࡦࡴࡵࡳࡷࡃࠢᇵ") + str(e) + bstack1ll111_opy_ (u"ࠨࠢᇶ"))
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡩࡽ࡫ࡣࡶࡶࡨࠤࡪࡸࡲࡰࡴࡀࠦᇷ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤᇸ"))
    def bstack1ll11l111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll111l111l_opy_(instance, args)
        capabilities = self.bstack1ll111l1l11_opy_.bstack1ll111l11ll_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        self.accessibility = self.bstack1ll111llll1_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠨᇹ"))
            return
        driver = self.bstack1ll111l1l11_opy_.bstack1ll1111ll11_opy_(f, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
        test_name = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1l1llll11l1_opy_)
        if not test_name:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡲࡦࡳࡥࠣᇺ"))
            return
        test_uuid = f.bstack1llll11l1ll_opy_(instance, TestFramework.bstack1ll11l111ll_opy_)
        if not test_uuid:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡺࡻࡩࡥࠤᇻ"))
            return
        if isinstance(self.bstack1ll111l1l11_opy_, bstack1lll1l1ll1l_opy_):
            framework_name = bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩᇼ")
        else:
            framework_name = bstack1ll111_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨᇽ")
        self.bstack111lll1111_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1lllll11ll_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠࡢ࠳࠴ࡽࠥࡴ࡯ࡵࠢࡨࡲࡦࡨ࡬ࡦࡦࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࢃࠠࠣᇾ"))
            return
        bstack111ll1ll1_opy_ = datetime.now()
        bstack1ll11111l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1ll111_opy_ (u"ࠣࡵࡦࡥࡳࠨᇿ"), None)
        if not bstack1ll11111l11_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫࡸࡩࡡ࡯ࠩࠣࡷࡨࡸࡩࡱࡶࠣࡪࡴࡸࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤሀ") + str(framework_name) + bstack1ll111_opy_ (u"ࠥࠤࠧሁ"))
            return
        if self.bstack1l1lllll111_opy_:
            arg = dict()
            arg[bstack1ll111_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࠦሂ")] = method if method else bstack1ll111_opy_ (u"ࠧࠨሃ")
            arg[bstack1ll111_opy_ (u"ࠨࡴࡩࡖࡨࡷࡹࡘࡵ࡯ࡗࡸ࡭ࡩࠨሄ")] = self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠢህ")]
            arg[bstack1ll111_opy_ (u"ࠣࡶ࡫ࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩࠨሆ")] = self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺࡨࡶࡤࡢࡦࡺ࡯࡬ࡥࡡࡸࡹ࡮ࡪࠢሇ")]
            arg[bstack1ll111_opy_ (u"ࠥࡥࡺࡺࡨࡉࡧࡤࡨࡪࡸࠢለ")] = self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠦࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡘࡴࡱࡥ࡯ࠤሉ")]
            arg[bstack1ll111_opy_ (u"ࠧࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠤሊ")] = self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠨࡴࡩࡡ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠧላ")]
            arg[bstack1ll111_opy_ (u"ࠢࡴࡥࡤࡲ࡙࡯࡭ࡦࡵࡷࡥࡲࡶࠢሌ")] = str(int(datetime.now().timestamp() * 1000))
            bstack1l1llll1l11_opy_ = self.bstack1ll11l11l11_opy_(bstack1ll111_opy_ (u"ࠣࡵࡦࡥࡳࠨል"), self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠤሎ")])
            if bstack1ll111_opy_ (u"ࠥࡧࡪࡴࡴࡳࡣ࡯ࡅࡺࡺࡨࡕࡱ࡮ࡩࡳࠨሏ") in bstack1l1llll1l11_opy_:
                bstack1l1llll1l11_opy_ = bstack1l1llll1l11_opy_.copy()
                bstack1l1llll1l11_opy_[bstack1ll111_opy_ (u"ࠦࡨ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡊࡨࡥࡩ࡫ࡲࠣሐ")] = bstack1l1llll1l11_opy_.pop(bstack1ll111_opy_ (u"ࠧࡩࡥ࡯ࡶࡵࡥࡱࡇࡵࡵࡪࡗࡳࡰ࡫࡮ࠣሑ"))
            arg = bstack1l1llllllll_opy_(arg, bstack1l1llll1l11_opy_)
            bstack1l1llll11ll_opy_ = bstack1ll11111l11_opy_ % json.dumps(arg)
            driver.execute_script(bstack1l1llll11ll_opy_)
            return
        instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(driver)
        if instance:
            if not bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11111lll_opy_, False):
                bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11111lll_opy_, True)
            else:
                self.logger.info(bstack1ll111_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳ࡟ࡴࡥࡤࡲ࠿ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡪࡰࠣࡴࡷࡵࡧࡳࡧࡶࡷࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࡻࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࡾࠢࡰࡩࡹ࡮࡯ࡥ࠿ࠥሒ") + str(method) + bstack1ll111_opy_ (u"ࠢࠣሓ"))
                return
        self.logger.info(bstack1ll111_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࡾࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࢁࠥࡳࡥࡵࡪࡲࡨࡂࠨሔ") + str(method) + bstack1ll111_opy_ (u"ࠤࠥሕ"))
        if framework_name == bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧሖ"):
            result = self.bstack1ll111l1l11_opy_.bstack1ll111111l1_opy_(driver, bstack1ll11111l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11111l11_opy_, {bstack1ll111_opy_ (u"ࠦࡲ࡫ࡴࡩࡱࡧࠦሗ"): method if method else bstack1ll111_opy_ (u"ࠧࠨመ")})
        bstack1ll1ll111ll_opy_.end(EVENTS.bstack1lllll11ll_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨሙ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠢ࠻ࡧࡱࡨࠧሚ"), True, None, command=method)
        if instance:
            bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11111lll_opy_, False)
            instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࡰࡦࡴࡩࡳࡷࡳ࡟ࡴࡥࡤࡲࠧማ"), datetime.now() - bstack111ll1ll1_opy_)
        return result
        def bstack1ll111l1ll1_opy_(self, driver: object, framework_name, bstack11l11l1l1_opy_: str):
            self.bstack1ll1111l1ll_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1l1llll1ll1_opy_ = self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠤሜ")]
            req.bstack11l11l1l1_opy_ = bstack11l11l1l1_opy_
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1lll1l11lll_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack1ll111_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧም") + str(r) + bstack1ll111_opy_ (u"ࠦࠧሞ"))
                else:
                    bstack1l1lllll11l_opy_ = json.loads(r.bstack1ll11l1lll1_opy_.decode(bstack1ll111_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫሟ")))
                    if bstack11l11l1l1_opy_ == bstack1ll111_opy_ (u"࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠪሠ"):
                        return bstack1l1lllll11l_opy_.get(bstack1ll111_opy_ (u"ࠢࡥࡣࡷࡥࠧሡ"), [])
                    else:
                        return bstack1l1lllll11l_opy_.get(bstack1ll111_opy_ (u"ࠣࡦࡤࡸࡦࠨሢ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack1ll111_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤ࡫࡫ࡴࡤࡪ࡬ࡲ࡬ࠦࡧࡦࡶࡢࡥࡵࡶ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࠠࡧࡴࡲࡱࠥࡩ࡬ࡪ࠼ࠣࠦሣ") + str(e) + bstack1ll111_opy_ (u"ࠥࠦሤ"))
    @measure(event_name=EVENTS.bstack11ll11l1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦ࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࡴ࠼ࠣࡥ࠶࠷ࡹࠡࡰࡲࡸࠥ࡫࡮ࡢࡤ࡯ࡩࡩࠨሥ"))
            return
        if self.bstack1l1lllll111_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࡦࡶࡰࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨሦ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll111l1ll1_opy_(driver, framework_name, bstack1ll111_opy_ (u"ࠨࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠥሧ"))
        bstack1ll11111l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠦረ"), None)
        if not bstack1ll11111l11_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠪ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࠧࠡࡵࡦࡶ࡮ࡶࡴࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࠢሩ") + str(framework_name) + bstack1ll111_opy_ (u"ࠤࠥሪ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack111ll1ll1_opy_ = datetime.now()
        if framework_name == bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧራ"):
            result = self.bstack1ll111l1l11_opy_.bstack1ll111111l1_opy_(driver, bstack1ll11111l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11111l11_opy_)
        instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(driver)
        if instance:
            instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠦࡦ࠷࠱ࡺ࠼ࡪࡩࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡲࡦࡵࡸࡰࡹࡹࠢሬ"), datetime.now() - bstack111ll1ll1_opy_)
        return result
    @measure(event_name=EVENTS.bstack111lllllll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1ll111_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࡵࡢࡷࡺࡳ࡭ࡢࡴࡼ࠾ࠥࡧ࠱࠲ࡻࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠣር"))
            return
        if self.bstack1l1lllll111_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll111l1ll1_opy_(driver, framework_name, bstack1ll111_opy_ (u"࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࡖࡹࡲࡳࡡࡳࡻࠪሮ"))
        bstack1ll11111l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1ll111_opy_ (u"ࠢࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠦሯ"), None)
        if not bstack1ll11111l11_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠪ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࡓࡶ࡯ࡰࡥࡷࡿࠧࠡࡵࡦࡶ࡮ࡶࡴࠡࡨࡲࡶࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࡃࠢሰ") + str(framework_name) + bstack1ll111_opy_ (u"ࠤࠥሱ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack111ll1ll1_opy_ = datetime.now()
        if framework_name == bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧሲ"):
            result = self.bstack1ll111l1l11_opy_.bstack1ll111111l1_opy_(driver, bstack1ll11111l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11111l11_opy_)
        instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(driver)
        if instance:
            instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠦࡦ࠷࠱ࡺ࠼ࡪࡩࡹࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡲࡦࡵࡸࡰࡹࡹ࡟ࡴࡷࡰࡱࡦࡸࡹࠣሳ"), datetime.now() - bstack111ll1ll1_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll11l1l1ll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1ll1111111l_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll1111l1ll_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1lll1l11lll_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࠢሴ") + str(r) + bstack1ll111_opy_ (u"ࠨࠢስ"))
            else:
                self.bstack1ll11l1l111_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧሶ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤሷ"))
            traceback.print_exc()
            raise e
    def bstack1ll11l1l111_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡯ࡳࡦࡪ࡟ࡤࡱࡱࡪ࡮࡭࠺ࠡࡣ࠴࠵ࡾࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠤሸ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1l1lllll111_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡧࡻࡩ࡭ࡦࡢࡹࡺ࡯ࡤࠣሹ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1l1llllll1l_opy_[bstack1ll111_opy_ (u"ࠦࡹ࡮࡟࡫ࡹࡷࡣࡹࡵ࡫ࡦࡰࠥሺ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1l1llllll1l_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1l1llll1111_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1ll11l1l11l_opy_ and command.module == self.bstack1l1llll1lll_opy_:
                        if command.method and not command.method in bstack1l1llll1111_opy_:
                            bstack1l1llll1111_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1l1llll1111_opy_[command.method]:
                            bstack1l1llll1111_opy_[command.method][command.name] = list()
                        bstack1l1llll1111_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1l1llll1111_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1ll11111111_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        exec: Tuple[bstack1lllll11111_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1ll111l1l11_opy_, bstack1lll1l1ll1l_opy_) and method_name != bstack1ll111_opy_ (u"ࠬࡩ࡯࡯ࡰࡨࡧࡹ࠭ሻ"):
            return
        if bstack1llll1lll1l_opy_.bstack1llll11lll1_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11l11111_opy_):
            return
        if f.bstack1ll1111lll1_opy_(method_name, *args):
            bstack1ll11ll11l1_opy_ = False
            desired_capabilities = f.bstack1l1llll1l1l_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1ll111l11l1_opy_(instance)
                platform_index = f.bstack1llll11l1ll_opy_(instance, bstack1lll11l11ll_opy_.bstack1ll11ll1111_opy_, 0)
                bstack1ll111ll1l1_opy_ = datetime.now()
                r = self.bstack1ll1111111l_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡨࡵ࡮ࡧ࡫ࡪࠦሼ"), datetime.now() - bstack1ll111ll1l1_opy_)
                bstack1ll11ll11l1_opy_ = r.success
            else:
                self.logger.error(bstack1ll111_opy_ (u"ࠢ࡮࡫ࡶࡷ࡮ࡴࡧࠡࡦࡨࡷ࡮ࡸࡥࡥࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳ࠾ࠤሽ") + str(desired_capabilities) + bstack1ll111_opy_ (u"ࠣࠤሾ"))
            f.bstack1llll11l11l_opy_(instance, bstack1lll1lll111_opy_.bstack1ll11l11111_opy_, bstack1ll11ll11l1_opy_)
    def bstack11ll11lll1_opy_(self, test_tags):
        bstack1ll1111111l_opy_ = self.config.get(bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩሿ"))
        if not bstack1ll1111111l_opy_:
            return True
        try:
            include_tags = bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨቀ")] if bstack1ll111_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩቁ") in bstack1ll1111111l_opy_ and isinstance(bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪቂ")], list) else []
            exclude_tags = bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫቃ")] if bstack1ll111_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬቄ") in bstack1ll1111111l_opy_ and isinstance(bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ቅ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡷࡣ࡯࡭ࡩࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡧ࡫ࡦࡰࡴࡨࠤࡸࡩࡡ࡯ࡰ࡬ࡲ࡬࠴ࠠࡆࡴࡵࡳࡷࠦ࠺ࠡࠤቆ") + str(error))
        return False
    def bstack1ll1l11111_opy_(self, caps):
        try:
            if self.bstack1l1lllll111_opy_:
                bstack1ll11l1ll11_opy_ = caps.get(bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤቇ"))
                if bstack1ll11l1ll11_opy_ is not None and str(bstack1ll11l1ll11_opy_).lower() == bstack1ll111_opy_ (u"ࠦࡦࡴࡤࡳࡱ࡬ࡨࠧቈ"):
                    bstack1ll111l1lll_opy_ = caps.get(bstack1ll111_opy_ (u"ࠧࡧࡰࡱ࡫ࡸࡱ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢ቉")) or caps.get(bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣቊ"))
                    if bstack1ll111l1lll_opy_ is not None and int(bstack1ll111l1lll_opy_) < 11:
                        self.logger.warning(bstack1ll111_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡂࡰࡧࡶࡴ࡯ࡤࠡ࠳࠴ࠤࡦࡴࡤࠡࡣࡥࡳࡻ࡫࠮ࠡࡅࡸࡶࡷ࡫࡮ࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡃࠢቋ") + str(bstack1ll111l1lll_opy_) + bstack1ll111_opy_ (u"ࠣࠤቌ"))
                        return False
                return True
            bstack1ll1111llll_opy_ = caps.get(bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪቍ"), {}).get(bstack1ll111_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧ቎"), caps.get(bstack1ll111_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ቏"), bstack1ll111_opy_ (u"ࠬ࠭ቐ")))
            if bstack1ll1111llll_opy_:
                self.logger.warning(bstack1ll111_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡄࡦࡵ࡮ࡸࡴࡶࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥቑ"))
                return False
            browser = caps.get(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬቒ"), bstack1ll111_opy_ (u"ࠨࠩቓ")).lower()
            if browser != bstack1ll111_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩቔ"):
                self.logger.warning(bstack1ll111_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡇ࡭ࡸ࡯࡮ࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷ࠳ࠨቕ"))
                return False
            bstack1ll11111l1l_opy_ = bstack1ll1111l1l1_opy_
            if not self.config.get(bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ቖ")) or self.config.get(bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ቗")):
                bstack1ll11111l1l_opy_ = bstack1ll111lll1l_opy_
            browser_version = caps.get(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧቘ"))
            if not browser_version:
                browser_version = caps.get(bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ቙"), {}).get(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩቚ"), bstack1ll111_opy_ (u"ࠩࠪቛ"))
            if browser_version and browser_version != bstack1ll111_opy_ (u"ࠪࡰࡦࡺࡥࡴࡶࠪቜ") and int(browser_version.split(bstack1ll111_opy_ (u"ࠫ࠳࠭ቝ"))[0]) <= bstack1ll11111l1l_opy_:
                self.logger.warning(bstack1ll111_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡨࡴࡨࡥࡹ࡫ࡲࠡࡶ࡫ࡥࡳࠦࠢ቞") + str(bstack1ll11111l1l_opy_) + bstack1ll111_opy_ (u"ࠨ࠮ࠣ቟"))
                return False
            bstack1l1lllllll1_opy_ = caps.get(bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨበ"), {}).get(bstack1ll111_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨቡ"))
            if not bstack1l1lllllll1_opy_:
                bstack1l1lllllll1_opy_ = caps.get(bstack1ll111_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧቢ"), {})
            if bstack1l1lllllll1_opy_ and bstack1ll111_opy_ (u"ࠪ࠱࠲࡮ࡥࡢࡦ࡯ࡩࡸࡹࠧባ") in bstack1l1lllllll1_opy_.get(bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡴࠩቤ"), []):
                self.logger.warning(bstack1ll111_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠ࡯ࡱࡷࠤࡷࡻ࡮ࠡࡱࡱࠤࡱ࡫ࡧࡢࡥࡼࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲࡙ࠥࡷࡪࡶࡦ࡬ࠥࡺ࡯ࠡࡰࡨࡻࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩࠥࡵࡲࠡࡣࡹࡳ࡮ࡪࠠࡶࡵ࡬ࡲ࡬ࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠢብ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡼࡡ࡭࡫ࡧࡥࡹ࡫ࠠࡢ࠳࠴ࡽࠥࡹࡵࡱࡲࡲࡶࡹࠦ࠺ࠣቦ") + str(error))
            return False
    def bstack1ll11l11l1l_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1ll11l1111l_opy_ = {
            bstack1ll111_opy_ (u"ࠧࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪࠧቧ"): test_uuid,
        }
        bstack1ll1111ll1l_opy_ = {}
        if result.success:
            bstack1ll1111ll1l_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1l1llllllll_opy_(bstack1ll11l1111l_opy_, bstack1ll1111ll1l_opy_)
    def bstack1ll11l11l11_opy_(self, script_name: str, test_uuid: str) -> dict:
        bstack1ll111_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡌࡥࡵࡥ࡫ࠤࡨ࡫࡮ࡵࡴࡤࡰࠥࡧࡵࡵࡪࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡧࡴࡴࡦࡪࡩࡸࡶࡦࡺࡩࡰࡰࠣࡪࡴࡸࠠࡵࡪࡨࠤ࡬࡯ࡶࡦࡰࠣࡷࡨࡸࡩࡱࡶࠣࡲࡦࡳࡥ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶࠤࡨࡧࡣࡩࡧࡧࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡮࡬ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡨࡨࡸࡨ࡮ࡥࡥ࠮ࠣࡳࡹ࡮ࡥࡳࡹ࡬ࡷࡪࠦ࡬ࡰࡣࡧࡷࠥࡧ࡮ࡥࠢࡦࡥࡨ࡮ࡥࡴࠢ࡬ࡸ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡂࡴࡪࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡸࡩࡲࡪࡲࡷࡣࡳࡧ࡭ࡦ࠼ࠣࡒࡦࡳࡥࠡࡱࡩࠤࡹ࡮ࡥࠡࡵࡦࡶ࡮ࡶࡴࠡࡶࡲࠤ࡫࡫ࡴࡤࡪࠣࡧࡴࡴࡦࡪࡩࠣࡪࡴࡸࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡺࡥࡴࡶࡢࡹࡺ࡯ࡤ࠻ࠢࡘ࡙ࡎࡊࠠࡰࡨࠣࡸ࡭࡫ࠠࡵࡧࡶࡸࠥࡸࡵ࡯ࠢࡩࡳࡷࠦࡷࡩ࡫ࡦ࡬ࠥࡺ࡯ࠡࡨࡨࡸࡨ࡮ࠠࡤࡱࡱࡪ࡮࡭ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡦ࡬ࡧࡹࡀࠠࡄࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼ࠰ࠥ࡫࡭ࡱࡶࡼࠤࡩ࡯ࡣࡵࠢ࡬ࡪࠥ࡫ࡲࡳࡱࡵࠤࡴࡩࡣࡶࡴࡶࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣቨ")
        try:
            if self.bstack1ll11l1llll_opy_:
                return self.bstack1l1lllll1l1_opy_
            self.bstack1ll1111l1ll_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1ll111_opy_ (u"ࠤࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠤቩ")
            req.script_name = script_name
            r = self.bstack1lll1l11lll_opy_.FetchDriverExecuteParamsEvent(req)
            if r.success:
                self.bstack1l1lllll1l1_opy_ = self.bstack1ll11l11l1l_opy_(test_uuid, r)
                self.bstack1ll11l1llll_opy_ = True
            else:
                self.logger.error(bstack1ll111_opy_ (u"ࠥࡪࡪࡺࡣࡩࡅࡨࡲࡹࡸࡡ࡭ࡃࡸࡸ࡭ࡇ࠱࠲ࡻࡆࡳࡳ࡬ࡩࡨ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡪࡲࡪࡸࡨࡶࠥ࡫ࡸࡦࡥࡸࡸࡪࠦࡰࡢࡴࡤࡱࡸࠦࡦࡰࡴࠣࡿࡸࡩࡲࡪࡲࡷࡣࡳࡧ࡭ࡦࡿ࠽ࠤࠧቪ") + str(r.error) + bstack1ll111_opy_ (u"ࠦࠧቫ"))
                self.bstack1l1lllll1l1_opy_ = dict()
            return self.bstack1l1lllll1l1_opy_
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠧ࡬ࡥࡵࡥ࡫ࡇࡪࡴࡴࡳࡣ࡯ࡅࡺࡺࡨࡂ࠳࠴ࡽࡈࡵ࡮ࡧ࡫ࡪ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡨࡨࡸࡨ࡮ࠠࡥࡴ࡬ࡺࡪࡸࠠࡦࡺࡨࡧࡺࡺࡥࠡࡲࡤࡶࡦࡳࡳࠡࡨࡲࡶࠥࢁࡳࡤࡴ࡬ࡴࡹࡥ࡮ࡢ࡯ࡨࢁ࠿ࠦࠢቬ") + str(traceback.format_exc()) + bstack1ll111_opy_ (u"ࠨࠢቭ"))
            return dict()
    def bstack111lll1111_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1ll111lllll_opy_ = None
        try:
            self.bstack1ll1111l1ll_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1ll111_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢቮ")
            req.script_name = bstack1ll111_opy_ (u"ࠣࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸࠨቯ")
            r = self.bstack1lll1l11lll_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤࡩࡸࡩࡷࡧࡵࠤࡪࡾࡥࡤࡷࡷࡩࠥࡶࡡࡳࡣࡰࡷࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧተ") + str(r.error) + bstack1ll111_opy_ (u"ࠥࠦቱ"))
            else:
                bstack1ll11l1111l_opy_ = self.bstack1ll11l11l1l_opy_(test_uuid, r)
                bstack1ll11111l11_opy_ = r.script
            self.logger.debug(bstack1ll111_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡢࡸ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹࠧቲ") + str(bstack1ll11l1111l_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1ll11111l11_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡥࡳࡤࡣࡱ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࠧࡴࡣࡹࡩࡗ࡫ࡳࡶ࡮ࡷࡷࠬࠦࡳࡤࡴ࡬ࡴࡹࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࠧታ") + str(framework_name) + bstack1ll111_opy_ (u"ࠨࠠࠣቴ"))
                return
            bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1ll11l1ll1l_opy_.value)
            self.bstack1ll111l1l1l_opy_(driver, bstack1ll11111l11_opy_, bstack1ll11l1111l_opy_, framework_name)
            self.logger.info(bstack1ll111_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠥት"))
            bstack1ll1ll111ll_opy_.end(EVENTS.bstack1ll11l1ll1l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣቶ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠤ࠽ࡩࡳࡪࠢቷ"), True, None, command=bstack1ll111_opy_ (u"ࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨቸ"),test_name=name)
        except Exception as bstack1ll11l11lll_opy_:
            self.logger.error(bstack1ll111_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡩ࡯ࡶ࡮ࡧࠤࡳࡵࡴࠡࡤࡨࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡪࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨ࠾ࠥࠨቹ") + bstack1ll111_opy_ (u"ࠧࡹࡴࡳࠪࡳࡥࡹ࡮ࠩࠣቺ") + bstack1ll111_opy_ (u"ࠨࠠࡆࡴࡵࡳࡷࠦ࠺ࠣቻ") + str(bstack1ll11l11lll_opy_))
            bstack1ll1ll111ll_opy_.end(EVENTS.bstack1ll11l1ll1l_opy_.value, bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢቼ"), bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠣ࠼ࡨࡲࡩࠨች"), False, bstack1ll11l11lll_opy_, command=bstack1ll111_opy_ (u"ࠩࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠧቾ"),test_name=name)
    def bstack1ll111l1l1l_opy_(self, driver, bstack1ll11111l11_opy_, bstack1ll11l1111l_opy_, framework_name):
        if framework_name == bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧቿ"):
            self.bstack1ll111l1l11_opy_.bstack1ll111111l1_opy_(driver, bstack1ll11111l11_opy_, bstack1ll11l1111l_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1ll11111l11_opy_, bstack1ll11l1111l_opy_))
    def _1ll111l111l_opy_(self, instance: bstack1ll1l1ll1ll_opy_, args: Tuple) -> list:
        bstack1ll111_opy_ (u"ࠦࠧࠨࡅࡹࡶࡵࡥࡨࡺࠠࡵࡣࡪࡷࠥࡨࡡࡴࡧࡧࠤࡴࡴࠠࡵࡪࡨࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯࠳ࠨࠢࠣኀ")
        if bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠩኁ") in instance.bstack1l1llllll11_opy_:
            return args[2].tags if hasattr(args[2], bstack1ll111_opy_ (u"࠭ࡴࡢࡩࡶࠫኂ")) else []
        if hasattr(args[0], bstack1ll111_opy_ (u"ࠧࡰࡹࡱࡣࡲࡧࡲ࡬ࡧࡵࡷࠬኃ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1ll111llll1_opy_(self, tags, capabilities):
        return self.bstack11ll11lll1_opy_(tags) and self.bstack1ll1l11111_opy_(capabilities)