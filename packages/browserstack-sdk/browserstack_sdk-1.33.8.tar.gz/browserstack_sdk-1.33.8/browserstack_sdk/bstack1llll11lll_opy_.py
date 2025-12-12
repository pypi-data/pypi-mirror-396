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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1llll111_opy_
from browserstack_sdk.bstack1ll11llll_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack11l1l1l11l_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from bstack_utils.constants import bstack1111111111_opy_
from bstack_utils.bstack11ll1ll1ll_opy_ import bstack1ll11ll11_opy_
class bstack1lll1111ll_opy_:
    def __init__(self, args, logger, bstack11111111l1_opy_, bstack1111111lll_opy_):
        self.args = args
        self.logger = logger
        self.bstack11111111l1_opy_ = bstack11111111l1_opy_
        self.bstack1111111lll_opy_ = bstack1111111lll_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1l11l1l111_opy_ = []
        self.bstack111111ll11_opy_ = []
        self.bstack11lll1llll_opy_ = []
        self.bstack11111l1l11_opy_ = self.bstack11ll11l111_opy_()
        self.bstack111111l1_opy_ = -1
    def bstack1l111lll1l_opy_(self, bstack11111l111l_opy_):
        self.parse_args()
        self.bstack111111lll1_opy_()
        self.bstack111111111l_opy_(bstack11111l111l_opy_)
        self.bstack1111111l11_opy_()
    def bstack1ll11ll1ll_opy_(self):
        bstack11ll1ll1ll_opy_ = bstack1ll11ll11_opy_.bstack1l11l1l1l_opy_(self.bstack11111111l1_opy_, self.logger)
        if bstack11ll1ll1ll_opy_ is None:
            self.logger.warn(bstack1ll111_opy_ (u"ࠣࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡪࡤࡲࡩࡲࡥࡳࠢ࡬ࡷࠥࡴ࡯ࡵࠢ࡬ࡲ࡮ࡺࡩࡢ࡮࡬ࡾࡪࡪ࠮ࠡࡕ࡮࡭ࡵࡶࡩ࡯ࡩࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦ႓"))
            return
        bstack11111111ll_opy_ = False
        bstack11ll1ll1ll_opy_.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠤࡨࡲࡦࡨ࡬ࡦࡦࠥ႔"), bstack11ll1ll1ll_opy_.bstack1l11ll1l_opy_())
        start_time = time.time()
        if bstack11ll1ll1ll_opy_.bstack1l11ll1l_opy_():
            test_files = self.bstack111111l111_opy_()
            bstack11111111ll_opy_ = True
            bstack1lllllll1l1_opy_ = bstack11ll1ll1ll_opy_.bstack111111l1ll_opy_(test_files)
            if bstack1lllllll1l1_opy_:
                self.bstack1l11l1l111_opy_ = [os.path.normpath(item) for item in bstack1lllllll1l1_opy_]
                self.__1lllllll11l_opy_()
                bstack11ll1ll1ll_opy_.bstack11111l1l1l_opy_(bstack11111111ll_opy_)
                self.logger.info(bstack1ll111_opy_ (u"ࠥࡘࡪࡹࡴࡴࠢࡵࡩࡴࡸࡤࡦࡴࡨࡨࠥࡻࡳࡪࡰࡪࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠾ࠥࢁࡽࠣ႕").format(self.bstack1l11l1l111_opy_))
            else:
                self.logger.info(bstack1ll111_opy_ (u"ࠦࡓࡵࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡼ࡫ࡲࡦࠢࡵࡩࡴࡸࡤࡦࡴࡨࡨࠥࡨࡹࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠯ࠤ႖"))
        bstack11ll1ll1ll_opy_.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠧࡺࡩ࡮ࡧࡗࡥࡰ࡫࡮ࡕࡱࡄࡴࡵࡲࡹࠣ႗"), int((time.time() - start_time) * 1000)) # bstack1111111l1l_opy_ to bstack1llllllllll_opy_
    def __1lllllll11l_opy_(self):
        bstack1ll111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡖࡪࡶ࡬ࡢࡥࡨࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࠠࡱࡣࡷ࡬ࡸࠦࡩ࡯ࠢࡆࡐࡎࠦࡦ࡭ࡣࡪࡷࠥࡽࡩࡵࡪࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡥࡥࠢࡩ࡭ࡱ࡫ࠠࡱࡣࡷ࡬ࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡶࡻ࡫ࡲࠡࡴࡨࡸࡺࡸ࡮ࡴࠢࡵࡩࡴࡸࡤࡦࡴࡨࡨࠥ࡬ࡩ࡭ࡧࠣࡲࡦࡳࡥࡴ࠮ࠣࡥࡳࡪࠠࡸࡧࠣࡷ࡮ࡳࡰ࡭ࡻࠣࡹࡵࡪࡡࡵࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࡹ࡮ࡥࠡࡅࡏࡍࠥࡧࡲࡨࡵࠣࡸࡴࠦࡵࡴࡧࠣࡸ࡭ࡵࡳࡦࠢࡩ࡭ࡱ࡫ࡳ࠯ࠢࡘࡷࡪࡸࠧࡴࠢࡩ࡭ࡱࡺࡥࡳ࡫ࡱ࡫ࠥ࡬࡬ࡢࡩࡶࠤ࠭࠳࡭࠭ࠢ࠰࡯࠮ࠦࡲࡦ࡯ࡤ࡭ࡳࠐࠠࠡࠢࠣࠤࠥࠦࠠࡪࡰࡷࡥࡨࡺࠠࡢࡰࡧࠤࡼ࡯࡬࡭ࠢࡥࡩࠥࡧࡰࡱ࡮࡬ࡩࡩࠦ࡮ࡢࡶࡸࡶࡦࡲ࡬ࡺࠢࡧࡹࡷ࡯࡮ࡨࠢࡳࡽࡹ࡫ࡳࡵࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ႘")
        try:
            if not self.bstack1l11l1l111_opy_:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡏࡱࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡥࡥࠢࡩ࡭ࡱ࡫ࡳࠡࡲࡤࡸ࡭ࠦࡴࡰࠢࡶࡩࡹࠨ႙"))
                return
            bstack111111l1l1_opy_ = []
            for flag in self.bstack111111ll11_opy_:
                if flag.startswith(bstack1ll111_opy_ (u"ࠨ࠯ࠪႚ")):
                    bstack111111l1l1_opy_.append(flag)
                    continue
                bstack11111ll11l_opy_ = False
                if bstack1ll111_opy_ (u"ࠩ࠽࠾ࠬႛ") in flag:
                    bstack1lllllllll1_opy_ = flag.split(bstack1ll111_opy_ (u"ࠪ࠾࠿࠭ႜ"), 1)[0]
                    if os.path.exists(bstack1lllllllll1_opy_):
                        bstack11111ll11l_opy_ = True
                elif os.path.exists(flag):
                    if os.path.isdir(flag) or (os.path.isfile(flag) and flag.endswith(bstack1ll111_opy_ (u"ࠫ࠳ࡶࡹࠨႝ"))):
                        bstack11111ll11l_opy_ = True
                if not bstack11111ll11l_opy_:
                    bstack111111l1l1_opy_.append(flag)
            bstack111111l1l1_opy_.extend(self.bstack1l11l1l111_opy_)
            self.bstack111111ll11_opy_ = bstack111111l1l1_opy_
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸࡪࡪࠠࡴࡧ࡯ࡩࡨࡺ࡯ࡳࡵ࠽ࠤࢀࢃࠢ႞").format(str(e)))
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack11111l1ll1_opy_():
        import importlib
        if getattr(importlib, bstack1ll111_opy_ (u"࠭ࡦࡪࡰࡧࡣࡱࡵࡡࡥࡧࡵࠫ႟"), False):
            bstack1111111ll1_opy_ = importlib.find_loader(bstack1ll111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩႠ"))
        else:
            bstack1111111ll1_opy_ = importlib.util.find_spec(bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࠪႡ"))
    def bstack111111l11l_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack111111l1_opy_ = -1
        if self.bstack1111111lll_opy_ and bstack1ll111_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩႢ") in self.bstack11111111l1_opy_:
            self.bstack111111l1_opy_ = int(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪႣ")])
        try:
            bstack1lllllll1ll_opy_ = [bstack1ll111_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭Ⴄ"), bstack1ll111_opy_ (u"ࠬ࠳࠭ࡱ࡮ࡸ࡫࡮ࡴࡳࠨႥ"), bstack1ll111_opy_ (u"࠭࠭ࡱࠩႦ")]
            if self.bstack111111l1_opy_ >= 0:
                bstack1lllllll1ll_opy_.extend([bstack1ll111_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨႧ"), bstack1ll111_opy_ (u"ࠨ࠯ࡱࠫႨ")])
            for arg in bstack1lllllll1ll_opy_:
                self.bstack111111l11l_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack111111lll1_opy_(self):
        bstack111111ll11_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack111111ll11_opy_ = bstack111111ll11_opy_
        return self.bstack111111ll11_opy_
    def bstack11l11l1ll_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            self.bstack11111l1ll1_opy_()
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warn(e, bstack11l1l1l11l_opy_)
    def bstack111111111l_opy_(self, bstack11111l111l_opy_):
        bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
        if bstack11111l111l_opy_:
            self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠩ࠰࠱ࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭Ⴉ"))
            self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠪࡘࡷࡻࡥࠨႪ"))
        if bstack11ll11l11l_opy_.bstack1llllllll1l_opy_():
            self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠫ࠲࠳ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪႫ"))
            self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"࡚ࠬࡲࡶࡧࠪႬ"))
        self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"࠭࠭ࡱࠩႭ"))
        self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡶ࡬ࡶࡩ࡬ࡲࠬႮ"))
        self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠨ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠪႯ"))
        self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩႰ"))
        if self.bstack111111l1_opy_ > 1:
            self.bstack111111ll11_opy_.append(bstack1ll111_opy_ (u"ࠪ࠱ࡳ࠭Ⴑ"))
            self.bstack111111ll11_opy_.append(str(self.bstack111111l1_opy_))
    def bstack1111111l11_opy_(self):
        if bstack11ll1lll1l_opy_.bstack11ll1l11_opy_(self.bstack11111111l1_opy_):
             self.bstack111111ll11_opy_ += [
                bstack1111111111_opy_.get(bstack1ll111_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࠪႲ")), str(bstack11ll1lll1l_opy_.bstack1l11l1l1ll_opy_(self.bstack11111111l1_opy_)),
                bstack1111111111_opy_.get(bstack1ll111_opy_ (u"ࠬࡪࡥ࡭ࡣࡼࠫႳ")), str(bstack1111111111_opy_.get(bstack1ll111_opy_ (u"࠭ࡲࡦࡴࡸࡲ࠲ࡪࡥ࡭ࡣࡼࠫႴ")))
            ]
    def bstack111111llll_opy_(self):
        bstack11lll1llll_opy_ = []
        for spec in self.bstack1l11l1l111_opy_:
            bstack1l1llll1l1_opy_ = [spec]
            bstack1l1llll1l1_opy_ += self.bstack111111ll11_opy_
            bstack11lll1llll_opy_.append(bstack1l1llll1l1_opy_)
        self.bstack11lll1llll_opy_ = bstack11lll1llll_opy_
        return bstack11lll1llll_opy_
    def bstack11ll11l111_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack11111l1l11_opy_ = True
            return True
        except Exception as e:
            self.bstack11111l1l11_opy_ = False
        return self.bstack11111l1l11_opy_
    def bstack1l1llll111_opy_(self):
        bstack1ll111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡌ࡫ࡴࠡࡶ࡫ࡩࠥࡩ࡯ࡶࡰࡷࠤࡴ࡬ࠠࡵࡧࡶࡸࡸࠦࡷࡪࡶ࡫ࡳࡺࡺࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡶ࡫ࡩࡲࠦࡵࡴ࡫ࡱ࡫ࠥࡶࡹࡵࡧࡶࡸࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡮ࡴࡴ࠻ࠢࡗ࡬ࡪࠦࡴࡰࡶࡤࡰࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࡤࡱ࡯ࡰࡪࡩࡴࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣႵ")
        try:
            from browserstack_sdk.bstack1111l11111_opy_ import bstack1111l111ll_opy_
            bstack11111ll111_opy_ = bstack1111l111ll_opy_(bstack1111l111l1_opy_=self.bstack111111ll11_opy_)
            if not bstack11111ll111_opy_.get(bstack1ll111_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩႶ"), False):
                self.logger.error(bstack1ll111_opy_ (u"ࠤࡗࡩࡸࡺࠠࡤࡱࡸࡲࡹࠦࡣࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࢀࢃࠢႷ").format(bstack11111ll111_opy_.get(bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩႸ"), bstack1ll111_opy_ (u"࡚ࠫࡴ࡫࡯ࡱࡺࡲࠥ࡫ࡲࡳࡱࡵࠫႹ"))))
                return 0
            count = bstack11111ll111_opy_.get(bstack1ll111_opy_ (u"ࠬࡩ࡯ࡶࡰࡷࠫႺ"), 0)
            self.logger.info(bstack1ll111_opy_ (u"ࠨࡔࡰࡶࡤࡰࠥࡺࡥࡴࡶࡶࠤࡨࡵ࡬࡭ࡧࡦࡸࡪࡪ࠺ࠡࡽࢀࠦႻ").format(count))
            return count
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡥࡲࡹࡳࡺ࠺ࠡࡽࢀࠦႼ").format(e))
            return 0
    def bstack11l1l11ll1_opy_(self, bstack1lllllll111_opy_, bstack1l111lll1l_opy_):
        bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨႽ")] = self.bstack11111111l1_opy_
        multiprocessing.set_start_method(bstack1ll111_opy_ (u"ࠩࡶࡴࡦࡽ࡮ࠨႾ"))
        bstack1l11lll1ll_opy_ = []
        manager = multiprocessing.Manager()
        bstack1llllllll11_opy_ = manager.list()
        if bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭Ⴟ") in self.bstack11111111l1_opy_:
            for index, platform in enumerate(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧჀ")]):
                bstack1l11lll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack1lllllll111_opy_,
                                                            args=(self.bstack111111ll11_opy_, bstack1l111lll1l_opy_, bstack1llllllll11_opy_)))
            bstack11111l1111_opy_ = len(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨჁ")])
        else:
            bstack1l11lll1ll_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack1lllllll111_opy_,
                                                        args=(self.bstack111111ll11_opy_, bstack1l111lll1l_opy_, bstack1llllllll11_opy_)))
            bstack11111l1111_opy_ = 1
        i = 0
        for t in bstack1l11lll1ll_opy_:
            os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭Ⴢ")] = str(i)
            if bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪჃ") in self.bstack11111111l1_opy_:
                os.environ[bstack1ll111_opy_ (u"ࠨࡅࡘࡖࡗࡋࡎࡕࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡉࡇࡔࡂࠩჄ")] = json.dumps(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬჅ")][i % bstack11111l1111_opy_])
            i += 1
            t.start()
        for t in bstack1l11lll1ll_opy_:
            t.join()
        return list(bstack1llllllll11_opy_)
    @staticmethod
    def bstack11lllllll_opy_(driver, bstack11111l11l1_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ჆"), None)
        if item and getattr(item, bstack1ll111_opy_ (u"ࠫࡤࡧ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡥࡤࡷࡪ࠭Ⴧ"), None) and not getattr(item, bstack1ll111_opy_ (u"ࠬࡥࡡ࠲࠳ࡼࡣࡸࡺ࡯ࡱࡡࡧࡳࡳ࡫ࠧ჈"), False):
            logger.info(
                bstack1ll111_opy_ (u"ࠨࡁࡶࡶࡲࡱࡦࡺࡥࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤࡪࡾࡥࡤࡷࡷ࡭ࡴࡴࠠࡩࡣࡶࠤࡪࡴࡤࡦࡦ࠱ࠤࡕࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡨࡲࡶࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡩࡴࠢࡸࡲࡩ࡫ࡲࡸࡣࡼ࠲ࠧ჉"))
            bstack111111ll1l_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1llll111_opy_.bstack111lll1111_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack111111l111_opy_(self):
        bstack1ll111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡺࡨࡦࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡵࡱࠣࡦࡪࠦࡥࡹࡧࡦࡹࡹ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ჊")
        try:
            from browserstack_sdk.bstack1111l11111_opy_ import bstack1111l111ll_opy_
            bstack11111l11ll_opy_ = bstack1111l111ll_opy_(bstack1111l111l1_opy_=self.bstack111111ll11_opy_)
            if not bstack11111l11ll_opy_.get(bstack1ll111_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩ჋"), False):
                self.logger.error(bstack1ll111_opy_ (u"ࠤࡗࡩࡸࡺࠠࡧ࡫࡯ࡩࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥ࠼ࠣࡿࢂࠨ჌").format(bstack11111l11ll_opy_.get(bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩჍ"), bstack1ll111_opy_ (u"࡚ࠫࡴ࡫࡯ࡱࡺࡲࠥ࡫ࡲࡳࡱࡵࠫ჎"))))
                return []
            test_files = bstack11111l11ll_opy_.get(bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴࠩ჏"), [])
            count = bstack11111l11ll_opy_.get(bstack1ll111_opy_ (u"࠭ࡣࡰࡷࡱࡸࠬა"), 0)
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡄࡱ࡯ࡰࡪࡩࡴࡦࡦࠣࡿࢂࠦࡴࡦࡵࡷࡷࠥ࡯࡮ࠡࡽࢀࠤ࡫࡯࡬ࡦࡵࠥბ").format(count, len(test_files)))
            return test_files
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡩࡻࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲ࠿ࠦࡻࡾࠤგ").format(e))
            return []