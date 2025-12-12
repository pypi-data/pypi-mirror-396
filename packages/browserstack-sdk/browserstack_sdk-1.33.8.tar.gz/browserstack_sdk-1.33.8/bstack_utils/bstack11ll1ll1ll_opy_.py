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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack111l1111l11_opy_ import bstack1111llll111_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from bstack_utils.helper import bstack1l1l1111l1_opy_
import json
class bstack1ll11ll11_opy_:
    _1ll1ll11ll1_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack1111lll1ll1_opy_ = bstack1111llll111_opy_(self.config, logger)
        self.bstack1llll1l11l_opy_ = bstack11ll1lll1l_opy_.bstack1l11l1l1l_opy_(config=self.config)
        self.bstack1111llllll1_opy_ = {}
        self.bstack11111111ll_opy_ = False
        self.bstack111l1111l1l_opy_ = (
            self.__111l11111l1_opy_()
            and self.bstack1llll1l11l_opy_ is not None
            and self.bstack1llll1l11l_opy_.bstack1l11ll1l_opy_()
            and config.get(bstack1ll111_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫẦ"), None) is not None
            and config.get(bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪầ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1l11l1l1l_opy_(cls, config, logger):
        if cls._1ll1ll11ll1_opy_ is None and config is not None:
            cls._1ll1ll11ll1_opy_ = bstack1ll11ll11_opy_(config, logger)
        return cls._1ll1ll11ll1_opy_
    def bstack1l11ll1l_opy_(self):
        bstack1ll111_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡊ࡯ࠡࡰࡲࡸࠥࡧࡰࡱ࡮ࡼࠤࡹ࡫ࡳࡵࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡼ࡮ࡥ࡯࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡑ࠴࠵ࡾࠦࡩࡴࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡪࡵࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠦࡩࡴࠢࡑࡳࡳ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦẨ")
        return self.bstack111l1111l1l_opy_ and self.bstack111l111111l_opy_()
    def bstack111l111111l_opy_(self):
        bstack1111lllll11_opy_ = os.getenv(bstack1ll111_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪẩ"), self.config.get(bstack1ll111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭Ẫ"), None))
        return bstack1111lllll11_opy_ in bstack11l1l1lll11_opy_
    def __111l11111l1_opy_(self):
        bstack11l1ll11lll_opy_ = False
        for fw in bstack11l1l1l11ll_opy_:
            if fw in self.config.get(bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧẫ"), bstack1ll111_opy_ (u"ࠬ࠭Ậ")):
                bstack11l1ll11lll_opy_ = True
        return bstack1l1l1111l1_opy_(self.config.get(bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪậ"), bstack11l1ll11lll_opy_))
    def bstack1111lllllll_opy_(self):
        return (not self.bstack1l11ll1l_opy_() and
                self.bstack1llll1l11l_opy_ is not None and self.bstack1llll1l11l_opy_.bstack1l11ll1l_opy_())
    def bstack111l11111ll_opy_(self):
        if not self.bstack1111lllllll_opy_():
            return
        if self.config.get(bstack1ll111_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬẮ"), None) is None or self.config.get(bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫắ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack1ll111_opy_ (u"ࠤࡗࡩࡸࡺࠠࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡨࡧ࡮ࠨࡶࠣࡻࡴࡸ࡫ࠡࡣࡶࠤࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠠࡰࡴࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡳࡻ࡬࡭࠰ࠣࡔࡱ࡫ࡡࡴࡧࠣࡷࡪࡺࠠࡢࠢࡱࡳࡳ࠳࡮ࡶ࡮࡯ࠤࡻࡧ࡬ࡶࡧ࠱ࠦẰ"))
        if not self.__111l11111l1_opy_():
            self.logger.info(bstack1ll111_opy_ (u"ࠥࡘࡪࡹࡴࠡࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡩࡡ࡯ࠩࡷࠤࡼࡵࡲ࡬ࠢࡤࡷࠥࡺࡥࡴࡶࡕࡩࡵࡵࡲࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦ࠱ࠤࡕࡲࡥࡢࡵࡨࠤࡪࡴࡡࡣ࡮ࡨࠤ࡮ࡺࠠࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴ࠢằ"))
    def bstack1111lll1lll_opy_(self):
        return self.bstack11111111ll_opy_
    def bstack11111l1l1l_opy_(self, bstack1111llll1l1_opy_):
        self.bstack11111111ll_opy_ = bstack1111llll1l1_opy_
        self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠦࡦࡶࡰ࡭࡫ࡨࡨࠧẲ"), bstack1111llll1l1_opy_)
    def bstack111111l1ll_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡧࡱࡵࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬࠴ࠢẳ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack1llll1l11l_opy_.bstack1111lllll1l_opy_()
            if self.bstack1llll1l11l_opy_ is not None:
                orchestration_strategy = self.bstack1llll1l11l_opy_.bstack1ll1lllll_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack1ll111_opy_ (u"ࠨࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹࠡ࡫ࡶࠤࡓࡵ࡮ࡦ࠰ࠣࡇࡦࡴ࡮ࡰࡶࠣࡴࡷࡵࡣࡦࡧࡧࠤࡼ࡯ࡴࡩࠢࡷࡩࡸࡺࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠯ࠤẴ"))
                return None
            self.logger.info(bstack1ll111_opy_ (u"ࠢࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡹ࡬ࡸ࡭ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹ࠻ࠢࡾࢁࠧẵ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack1ll111_opy_ (u"ࠣࡗࡶ࡭ࡳ࡭ࠠࡄࡎࡌࠤ࡫ࡲ࡯ࡸࠢࡩࡳࡷࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦẶ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡘࡷ࡮ࡴࡧࠡࡵࡧ࡯ࠥ࡬࡬ࡰࡹࠣࡪࡴࡸࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧặ"))
                self.bstack1111lll1ll1_opy_.bstack111l1111111_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack1111lll1ll1_opy_.bstack1111llll11l_opy_()
            if not ordered_test_files:
                return None
            self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠥࡹࡵࡲ࡯ࡢࡦࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹࡃࡰࡷࡱࡸࠧẸ"), len(test_files))
            self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦࡋࡱࡨࡪࡾࠢẹ"), int(os.environ.get(bstack1ll111_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣẺ")) or bstack1ll111_opy_ (u"ࠨ࠰ࠣẻ")))
            self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠢࡵࡱࡷࡥࡱࡔ࡯ࡥࡧࡶࠦẼ"), int(os.environ.get(bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦẽ")) or bstack1ll111_opy_ (u"ࠤ࠴ࠦẾ")))
            self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠥࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴࡅࡲࡹࡳࡺࠢế"), len(ordered_test_files))
            self.bstack11111l1lll_opy_(bstack1ll111_opy_ (u"ࠦࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳࡂࡒࡌࡇࡦࡲ࡬ࡄࡱࡸࡲࡹࠨỀ"), self.bstack1111lll1ll1_opy_.bstack1111llll1ll_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡤ࡮ࡤࡷࡸ࡫ࡳ࠻ࠢࡾࢁࠧề").format(e))
        return None
    def bstack11111l1lll_opy_(self, key, value):
        self.bstack1111llllll1_opy_[key] = value
    def bstack1lll11111_opy_(self):
        return self.bstack1111llllll1_opy_