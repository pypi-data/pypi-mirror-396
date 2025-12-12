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
import tempfile
import math
from bstack_utils import bstack1llll1ll1l_opy_
from bstack_utils.constants import bstack11111111_opy_, bstack11l1l1lll11_opy_
from bstack_utils.helper import bstack111ll1111ll_opy_, get_host_info
from bstack_utils.bstack11l1lll111l_opy_ import bstack11l1lll11ll_opy_
import json
import re
import sys
bstack1111lll1l1l_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡦࡶࡵࡽ࡙࡫ࡳࡵࡵࡒࡲࡋࡧࡩ࡭ࡷࡵࡩࠧỂ")
bstack1111ll11lll_opy_ = bstack1ll111_opy_ (u"ࠢࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪࠨể")
bstack1111ll1l11l_opy_ = bstack1ll111_opy_ (u"ࠣࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࡆࡪࡴࡶࡸࠧỄ")
bstack1111ll11l11_opy_ = bstack1ll111_opy_ (u"ࠤࡵࡩࡷࡻ࡮ࡑࡴࡨࡺ࡮ࡵࡵࡴ࡮ࡼࡊࡦ࡯࡬ࡦࡦࠥễ")
bstack1111ll11ll1_opy_ = bstack1ll111_opy_ (u"ࠥࡷࡰ࡯ࡰࡇ࡮ࡤ࡯ࡾࡧ࡮ࡥࡈࡤ࡭ࡱ࡫ࡤࠣỆ")
bstack1111ll11l1l_opy_ = bstack1ll111_opy_ (u"ࠦࡷࡻ࡮ࡔ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠣệ")
bstack1111ll1ll1l_opy_ = {
    bstack1111lll1l1l_opy_,
    bstack1111ll11lll_opy_,
    bstack1111ll1l11l_opy_,
    bstack1111ll11l11_opy_,
    bstack1111ll11ll1_opy_,
    bstack1111ll11l1l_opy_
}
bstack1111l1111l1_opy_ = {bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬỈ")}
logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack11111111_opy_)
class bstack1111l1l11ll_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111ll111ll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack11ll1lll1l_opy_:
    _1ll1ll11ll1_opy_ = None
    def __init__(self, config):
        self.bstack1111ll1l1ll_opy_ = False
        self.bstack1111lll111l_opy_ = False
        self.bstack1111l11ll1l_opy_ = False
        self.bstack1111l1ll1ll_opy_ = False
        self.bstack1111ll11111_opy_ = None
        self.bstack1111l1l11l1_opy_ = bstack1111l1l11ll_opy_()
        self.bstack1111l1l1l1l_opy_ = None
        opts = config.get(bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪỉ"), {})
        self.bstack1111l1111ll_opy_ = config.get(bstack1ll111_opy_ (u"ࠧࡴ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࡇࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࡥࡴࡇࡑ࡚ࠬỊ"), bstack1ll111_opy_ (u"ࠣࠤị"))
        self.bstack1111l1ll11l_opy_ = config.get(bstack1ll111_opy_ (u"ࠩࡶࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࡉࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࡧࡶࡇࡑࡏࠧỌ"), bstack1ll111_opy_ (u"ࠥࠦọ"))
        bstack1111ll1lll1_opy_ = opts.get(bstack1111ll11l1l_opy_, {})
        bstack1111ll1ll11_opy_ = None
        if bstack1ll111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫỎ") in bstack1111ll1lll1_opy_:
            bstack1111l1l1ll1_opy_ = bstack1111ll1lll1_opy_[bstack1ll111_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬỏ")]
            if bstack1111l1l1ll1_opy_ is None or (isinstance(bstack1111l1l1ll1_opy_, str) and bstack1111l1l1ll1_opy_.strip() == bstack1ll111_opy_ (u"࠭ࠧỐ")) or (isinstance(bstack1111l1l1ll1_opy_, list) and len(bstack1111l1l1ll1_opy_) == 0):
                bstack1111ll1ll11_opy_ = []
            elif isinstance(bstack1111l1l1ll1_opy_, list):
                bstack1111ll1ll11_opy_ = bstack1111l1l1ll1_opy_
            elif isinstance(bstack1111l1l1ll1_opy_, str) and bstack1111l1l1ll1_opy_.strip():
                bstack1111ll1ll11_opy_ = bstack1111l1l1ll1_opy_
            else:
                logger.warning(bstack1ll111_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡲࡹࡷࡩࡥࠡࡸࡤࡰࡺ࡫ࠠࡪࡰࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࢀࢃ࠮ࠡࡆࡨࡪࡦࡻ࡬ࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡧࡰࡴࡹࡿࠠ࡭࡫ࡶࡸ࠳ࠨố").format(bstack1111l1l1ll1_opy_))
                bstack1111ll1ll11_opy_ = []
        self.__1111l1lll11_opy_(
            bstack1111ll1lll1_opy_.get(bstack1ll111_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩỒ"), False),
            bstack1111ll1lll1_opy_.get(bstack1ll111_opy_ (u"ࠩࡰࡳࡩ࡫ࠧồ"), bstack1ll111_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪỔ")),
            bstack1111ll1ll11_opy_
        )
        self.__11111llll1l_opy_(opts.get(bstack1111ll1l11l_opy_, False))
        self.__1111ll1l111_opy_(opts.get(bstack1111ll11l11_opy_, False))
        self.__1111lll1111_opy_(opts.get(bstack1111ll11ll1_opy_, False))
    @classmethod
    def bstack1l11l1l1l_opy_(cls, config=None):
        if cls._1ll1ll11ll1_opy_ is None and config is not None:
            cls._1ll1ll11ll1_opy_ = bstack11ll1lll1l_opy_(config)
        return cls._1ll1ll11ll1_opy_
    @staticmethod
    def bstack11ll1l11_opy_(config: dict) -> bool:
        bstack1111l11ll11_opy_ = config.get(bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨổ"), {}).get(bstack1111lll1l1l_opy_, {})
        return bstack1111l11ll11_opy_.get(bstack1ll111_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ỗ"), False)
    @staticmethod
    def bstack1l11l1l1ll_opy_(config: dict) -> int:
        bstack1111l11ll11_opy_ = config.get(bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪỗ"), {}).get(bstack1111lll1l1l_opy_, {})
        retries = 0
        if bstack11ll1lll1l_opy_.bstack11ll1l11_opy_(config):
            retries = bstack1111l11ll11_opy_.get(bstack1ll111_opy_ (u"ࠧ࡮ࡣࡻࡖࡪࡺࡲࡪࡧࡶࠫỘ"), 1)
        return retries
    @staticmethod
    def bstack11l1111l11_opy_(config: dict) -> dict:
        bstack1111ll1111l_opy_ = config.get(bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬộ"), {})
        return {
            key: value for key, value in bstack1111ll1111l_opy_.items() if key in bstack1111ll1ll1l_opy_
        }
    @staticmethod
    def bstack1111l1lll1l_opy_():
        bstack1ll111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡧࡢࡰࡴࡷࠤࡧࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨỚ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠥࡥࡧࡵࡲࡵࡡࡥࡹ࡮ࡲࡤࡠࡽࢀࠦớ").format(os.getenv(bstack1ll111_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤỜ")))))
    @staticmethod
    def bstack11111lllll1_opy_(test_name: str):
        bstack1ll111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡹ࡮ࡥࠡࡣࡥࡳࡷࡺࠠࡣࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡪࡾࡩࡴࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤờ")
        bstack1111ll111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࢁࡽ࠯ࡶࡻࡸࠧỞ").format(os.getenv(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠧở"))))
        with open(bstack1111ll111l1_opy_, bstack1ll111_opy_ (u"ࠨࡣࠪỠ")) as file:
            file.write(bstack1ll111_opy_ (u"ࠤࡾࢁࡡࡴࠢỡ").format(test_name))
    @staticmethod
    def bstack1111l1l1111_opy_(framework: str) -> bool:
       return framework.lower() in bstack1111l1111l1_opy_
    @staticmethod
    def bstack11l11ll111l_opy_(config: dict) -> bool:
        bstack1111l1llll1_opy_ = config.get(bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧỢ"), {}).get(bstack1111ll11lll_opy_, {})
        return bstack1111l1llll1_opy_.get(bstack1ll111_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬợ"), False)
    @staticmethod
    def bstack11l11lll1l1_opy_(config: dict, bstack11l11ll1111_opy_: int = 0) -> int:
        bstack1ll111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡊࡩࡹࠦࡴࡩࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡹ࡮ࡲࡦࡵ࡫ࡳࡱࡪࠬࠡࡹ࡫࡭ࡨ࡮ࠠࡤࡣࡱࠤࡧ࡫ࠠࡢࡰࠣࡥࡧࡹ࡯࡭ࡷࡷࡩࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡲࠡࡣࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡣࡰࡰࡩ࡭࡬ࠦࠨࡥ࡫ࡦࡸ࠮ࡀࠠࡕࡪࡨࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡵࡱࡷࡥࡱࡥࡴࡦࡵࡷࡷࠥ࠮ࡩ࡯ࡶࠬ࠾࡚ࠥࡨࡦࠢࡷࡳࡹࡧ࡬ࠡࡰࡸࡱࡧ࡫ࡲࠡࡱࡩࠤࡹ࡫ࡳࡵࡵࠣࠬࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡦࡰࡴࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠭ࡣࡣࡶࡩࡩࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥࡵࠬ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡩ࡯ࡶ࠽ࠤ࡙࡮ࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥỤ")
        bstack1111l1llll1_opy_ = config.get(bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪụ"), {}).get(bstack1ll111_opy_ (u"ࠧࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪ࠭Ủ"), {})
        bstack1111ll1l1l1_opy_ = 0
        bstack1111l11lll1_opy_ = 0
        if bstack11ll1lll1l_opy_.bstack11l11ll111l_opy_(config):
            bstack1111l11lll1_opy_ = bstack1111l1llll1_opy_.get(bstack1ll111_opy_ (u"ࠨ࡯ࡤࡼࡋࡧࡩ࡭ࡷࡵࡩࡸ࠭ủ"), 5)
            if isinstance(bstack1111l11lll1_opy_, str) and bstack1111l11lll1_opy_.endswith(bstack1ll111_opy_ (u"ࠩࠨࠫỨ")):
                try:
                    percentage = int(bstack1111l11lll1_opy_.strip(bstack1ll111_opy_ (u"ࠪࠩࠬứ")))
                    if bstack11l11ll1111_opy_ > 0:
                        bstack1111ll1l1l1_opy_ = math.ceil((percentage * bstack11l11ll1111_opy_) / 100)
                    else:
                        raise ValueError(bstack1ll111_opy_ (u"࡙ࠦࡵࡴࡢ࡮ࠣࡸࡪࡹࡴࡴࠢࡰࡹࡸࡺࠠࡣࡧࠣࡴࡷࡵࡶࡪࡦࡨࡨࠥ࡬࡯ࡳࠢࡳࡩࡷࡩࡥ࡯ࡶࡤ࡫ࡪ࠳ࡢࡢࡵࡨࡨࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࡴ࠰ࠥỪ"))
                except ValueError as e:
                    raise ValueError(bstack1ll111_opy_ (u"ࠧࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡰࡦࡴࡦࡩࡳࡺࡡࡨࡧࠣࡺࡦࡲࡵࡦࠢࡩࡳࡷࠦ࡭ࡢࡺࡉࡥ࡮ࡲࡵࡳࡧࡶ࠾ࠥࢁࡽࠣừ").format(bstack1111l11lll1_opy_)) from e
            else:
                bstack1111ll1l1l1_opy_ = int(bstack1111l11lll1_opy_)
        logger.info(bstack1ll111_opy_ (u"ࠨࡍࡢࡺࠣࡪࡦ࡯࡬ࡶࡴࡨࡷࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࠡࡵࡨࡸࠥࡺ࡯࠻ࠢࡾࢁࠥ࠮ࡦࡳࡱࡰࠤࡨࡵ࡮ࡧ࡫ࡪ࠾ࠥࢁࡽࠪࠤỬ").format(bstack1111ll1l1l1_opy_, bstack1111l11lll1_opy_))
        return bstack1111ll1l1l1_opy_
    def bstack1111l1l1lll_opy_(self):
        return self.bstack1111l1ll1ll_opy_
    def bstack11111llllll_opy_(self):
        return self.bstack1111ll11111_opy_
    def bstack1111l1lllll_opy_(self):
        return self.bstack1111l1l1l1l_opy_
    def __1111l1lll11_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111l1ll1ll_opy_ = bool(enabled)
            if mode not in [bstack1ll111_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧử"), bstack1ll111_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡒࡲࡱࡿࠧỮ")]:
                logger.warning(bstack1ll111_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡷࡲࡧࡲࡵࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥࡳ࡯ࡥࡧࠣࠫࢀࢃࠧࠡࡲࡵࡳࡻ࡯ࡤࡦࡦ࠱ࠤࡉ࡫ࡦࡢࡷ࡯ࡸ࡮ࡴࡧࠡࡶࡲࠤࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡆࡪࡴࡶࡸࠬ࠴ࠢữ").format(mode))
                mode = bstack1ll111_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪỰ")
            self.bstack1111ll11111_opy_ = mode
            self.bstack1111l1l1l1l_opy_ = []
            if source is None:
                self.bstack1111l1l1l1l_opy_ = None
            elif isinstance(source, list):
                self.bstack1111l1l1l1l_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack1ll111_opy_ (u"ࠫ࠳ࡰࡳࡰࡰࠪự")):
                self.bstack1111l1l1l1l_opy_ = self._1111l111l11_opy_(source)
            self.__1111l1l1l11_opy_()
        except Exception as e:
            logger.error(bstack1ll111_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹ࡭ࡢࡴࡷࠤࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠ࠮ࠢࡨࡲࡦࡨ࡬ࡦࡦ࠽ࠤࢀࢃࠬࠡ࡯ࡲࡨࡪࡀࠠࡼࡿ࠯ࠤࡸࡵࡵࡳࡥࡨ࠾ࠥࢁࡽ࠯ࠢࡈࡶࡷࡵࡲ࠻ࠢࡾࢁࠧỲ").format(enabled, mode, source, e))
    def bstack1111lll1l11_opy_(self):
        return self.bstack1111ll1l1ll_opy_
    def __11111llll1l_opy_(self, value):
        self.bstack1111ll1l1ll_opy_ = bool(value)
        self.__1111l1l1l11_opy_()
    def bstack1111l111l1l_opy_(self):
        return self.bstack1111lll111l_opy_
    def __1111ll1l111_opy_(self, value):
        self.bstack1111lll111l_opy_ = bool(value)
        self.__1111l1l1l11_opy_()
    def bstack1111lll11l1_opy_(self):
        return self.bstack1111l11ll1l_opy_
    def __1111lll1111_opy_(self, value):
        self.bstack1111l11ll1l_opy_ = bool(value)
        self.__1111l1l1l11_opy_()
    def __1111l1l1l11_opy_(self):
        if self.bstack1111l1ll1ll_opy_:
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111lll111l_opy_ = False
            self.bstack1111l11ll1l_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111ll11l1l_opy_)
        elif self.bstack1111ll1l1ll_opy_:
            self.bstack1111lll111l_opy_ = False
            self.bstack1111l11ll1l_opy_ = False
            self.bstack1111l1ll1ll_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111ll1l11l_opy_)
        elif self.bstack1111lll111l_opy_:
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111l11ll1l_opy_ = False
            self.bstack1111l1ll1ll_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111ll11l11_opy_)
        elif self.bstack1111l11ll1l_opy_:
            self.bstack1111ll1l1ll_opy_ = False
            self.bstack1111lll111l_opy_ = False
            self.bstack1111l1ll1ll_opy_ = False
            self.bstack1111l1l11l1_opy_.enable(bstack1111ll11ll1_opy_)
        else:
            self.bstack1111l1l11l1_opy_.disable()
    def bstack1l11ll1l_opy_(self):
        return self.bstack1111l1l11l1_opy_.bstack1111ll111ll_opy_()
    def bstack1ll1lllll_opy_(self):
        if self.bstack1111l1l11l1_opy_.bstack1111ll111ll_opy_():
            return self.bstack1111l1l11l1_opy_.get_name()
        return None
    def _1111l111l11_opy_(self, bstack1111lll11ll_opy_):
        bstack1ll111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡔࡦࡸࡳࡦࠢࡍࡗࡔࡔࠠࡴࡱࡸࡶࡨ࡫ࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡧ࡫࡯ࡩࠥࡧ࡮ࡥࠢࡩࡳࡷࡳࡡࡵࠢ࡬ࡸࠥ࡬࡯ࡳࠢࡶࡱࡦࡸࡴࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡷࡴࡻࡲࡤࡧࡢࡪ࡮ࡲࡥࡠࡲࡤࡸ࡭ࠦࠨࡴࡶࡵ࠭࠿ࠦࡐࡢࡶ࡫ࠤࡹࡵࠠࡵࡪࡨࠤࡏ࡙ࡏࡏࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡩ࡭ࡱ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࡮࡬ࡷࡹࡀࠠࡇࡱࡵࡱࡦࡺࡴࡦࡦࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡷ࡫ࡰࡰࡵ࡬ࡸࡴࡸࡹࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨỳ")
        if not os.path.isfile(bstack1111lll11ll_opy_):
            logger.error(bstack1ll111_opy_ (u"ࠢࡔࡱࡸࡶࡨ࡫ࠠࡧ࡫࡯ࡩࠥ࠭ࡻࡾࠩࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠲ࠧỴ").format(bstack1111lll11ll_opy_))
            return []
        data = None
        try:
            with open(bstack1111lll11ll_opy_, bstack1ll111_opy_ (u"ࠣࡴࠥỵ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡍࡗࡔࡔࠠࡧࡴࡲࡱࠥࡹ࡯ࡶࡴࡦࡩࠥ࡬ࡩ࡭ࡧࠣࠫࢀࢃࠧ࠻ࠢࡾࢁࠧỶ").format(bstack1111lll11ll_opy_, e))
            return []
        _1111l111lll_opy_ = None
        _1111l11l1ll_opy_ = None
        def _1111l11111l_opy_():
            bstack1111ll1llll_opy_ = {}
            bstack1111l1ll111_opy_ = {}
            try:
                if self.bstack1111l1111ll_opy_.startswith(bstack1ll111_opy_ (u"ࠪࡿࠬỷ")) and self.bstack1111l1111ll_opy_.endswith(bstack1ll111_opy_ (u"ࠫࢂ࠭Ỹ")):
                    bstack1111ll1llll_opy_ = json.loads(self.bstack1111l1111ll_opy_)
                else:
                    bstack1111ll1llll_opy_ = dict(item.split(bstack1ll111_opy_ (u"ࠬࡀࠧỹ")) for item in self.bstack1111l1111ll_opy_.split(bstack1ll111_opy_ (u"࠭ࠬࠨỺ")) if bstack1ll111_opy_ (u"ࠧ࠻ࠩỻ") in item) if self.bstack1111l1111ll_opy_ else {}
                if self.bstack1111l1ll11l_opy_.startswith(bstack1ll111_opy_ (u"ࠨࡽࠪỼ")) and self.bstack1111l1ll11l_opy_.endswith(bstack1ll111_opy_ (u"ࠩࢀࠫỽ")):
                    bstack1111l1ll111_opy_ = json.loads(self.bstack1111l1ll11l_opy_)
                else:
                    bstack1111l1ll111_opy_ = dict(item.split(bstack1ll111_opy_ (u"ࠪ࠾ࠬỾ")) for item in self.bstack1111l1ll11l_opy_.split(bstack1ll111_opy_ (u"ࠫ࠱࠭ỿ")) if bstack1ll111_opy_ (u"ࠬࡀࠧἀ") in item) if self.bstack1111l1ll11l_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠ࡮ࡣࡳࡴ࡮ࡴࡧࡴ࠼ࠣࡿࢂࠨἁ").format(e))
            logger.debug(bstack1ll111_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠣࡪࡷࡵ࡭ࠡࡧࡱࡺ࠿ࠦࡻࡾ࠮ࠣࡇࡑࡏ࠺ࠡࡽࢀࠦἂ").format(bstack1111ll1llll_opy_, bstack1111l1ll111_opy_))
            return bstack1111ll1llll_opy_, bstack1111l1ll111_opy_
        if _1111l111lll_opy_ is None or _1111l11l1ll_opy_ is None:
            _1111l111lll_opy_, _1111l11l1ll_opy_ = _1111l11111l_opy_()
        def bstack1111l11llll_opy_(name, bstack1111l11l11l_opy_):
            if name in _1111l11l1ll_opy_:
                return _1111l11l1ll_opy_[name]
            if name in _1111l111lll_opy_:
                return _1111l111lll_opy_[name]
            if bstack1111l11l11l_opy_.get(bstack1ll111_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨἃ")):
                return bstack1111l11l11l_opy_[bstack1ll111_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩἄ")]
            return None
        if isinstance(data, dict):
            bstack1111l111111_opy_ = []
            bstack1111l1ll1l1_opy_ = re.compile(bstack1ll111_opy_ (u"ࡵࠫࡣࡡࡁ࠮࡜࠳࠱࠾ࡥ࡝ࠬࠦࠪἅ"))
            for name, bstack1111l11l11l_opy_ in data.items():
                if not isinstance(bstack1111l11l11l_opy_, dict):
                    continue
                url = bstack1111l11l11l_opy_.get(bstack1ll111_opy_ (u"ࠫࡺࡸ࡬ࠨἆ"))
                if url is None or (isinstance(url, str) and url.strip() == bstack1ll111_opy_ (u"ࠬ࠭ἇ")):
                    logger.warning(bstack1ll111_opy_ (u"ࠨࡒࡦࡲࡲࡷ࡮ࡺ࡯ࡳࡻ࡙ࠣࡗࡒࠠࡪࡵࠣࡱ࡮ࡹࡳࡪࡰࡪࠤ࡫ࡵࡲࠡࡵࡲࡹࡷࡩࡥࠡࠩࡾࢁࠬࡀࠠࡼࡿࠥἈ").format(name, bstack1111l11l11l_opy_))
                    continue
                if not bstack1111l1ll1l1_opy_.match(name):
                    logger.warning(bstack1ll111_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡲࡹࡷࡩࡥࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠥ࡬࡯ࡳ࡯ࡤࡸࠥ࡬࡯ࡳࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦἉ").format(name, bstack1111l11l11l_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack1ll111_opy_ (u"ࠣࡕࡲࡹࡷࡩࡥࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠥ࠭ࡻࡾࠩࠣࡱࡺࡹࡴࠡࡪࡤࡺࡪࠦࡡࠡ࡮ࡨࡲ࡬ࡺࡨࠡࡤࡨࡸࡼ࡫ࡥ࡯ࠢ࠴ࠤࡦࡴࡤࠡ࠵࠳ࠤࡨ࡮ࡡࡳࡣࡦࡸࡪࡸࡳ࠯ࠤἊ").format(name))
                    continue
                bstack1111l11l11l_opy_ = bstack1111l11l11l_opy_.copy()
                bstack1111l11l11l_opy_[bstack1ll111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧἋ")] = name
                bstack1111l11l11l_opy_[bstack1ll111_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪἌ")] = bstack1111l11llll_opy_(name, bstack1111l11l11l_opy_)
                if not bstack1111l11l11l_opy_.get(bstack1ll111_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࡇࡸࡡ࡯ࡥ࡫ࠫἍ")) or bstack1111l11l11l_opy_.get(bstack1ll111_opy_ (u"ࠬ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠬἎ")) == bstack1ll111_opy_ (u"࠭ࠧἏ"):
                    logger.warning(bstack1ll111_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡࡰࡲࡸࠥࡹࡰࡦࡥ࡬ࡪ࡮࡫ࡤࠡࡨࡲࡶࠥࡹ࡯ࡶࡴࡦࡩࠥ࠭ࡻࡾࠩ࠽ࠤࢀࢃࠢἐ").format(name, bstack1111l11l11l_opy_))
                    continue
                if bstack1111l11l11l_opy_.get(bstack1ll111_opy_ (u"ࠨࡤࡤࡷࡪࡈࡲࡢࡰࡦ࡬ࠬἑ")) and bstack1111l11l11l_opy_[bstack1ll111_opy_ (u"ࠩࡥࡥࡸ࡫ࡂࡳࡣࡱࡧ࡭࠭ἒ")] == bstack1111l11l11l_opy_[bstack1ll111_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪἓ")]:
                    logger.warning(bstack1ll111_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡧ࡮ࡥࠢࡥࡥࡸ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠࡤࡣࡱࡲࡴࡺࠠࡣࡧࠣࡸ࡭࡫ࠠࡴࡣࡰࡩࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦἔ").format(name, bstack1111l11l11l_opy_))
                    continue
                bstack1111l111111_opy_.append(bstack1111l11l11l_opy_)
            return bstack1111l111111_opy_
        return data
    def bstack1111lllll1l_opy_(self):
        data = {
            bstack1ll111_opy_ (u"ࠬࡸࡵ࡯ࡡࡶࡱࡦࡸࡴࡠࡵࡨࡰࡪࡩࡴࡪࡱࡱࠫἕ"): {
                bstack1ll111_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧ἖"): self.bstack1111l1l1lll_opy_(),
                bstack1ll111_opy_ (u"ࠧ࡮ࡱࡧࡩࠬ἗"): self.bstack11111llllll_opy_(),
                bstack1ll111_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨἘ"): self.bstack1111l1lllll_opy_()
            }
        }
        return data
    def bstack1111l11l1l1_opy_(self, config):
        bstack1111l1l111l_opy_ = {}
        bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨἙ")] = {
            bstack1ll111_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἚ"): self.bstack1111l1l1lll_opy_(),
            bstack1ll111_opy_ (u"ࠫࡲࡵࡤࡦࠩἛ"): self.bstack11111llllll_opy_()
        }
        bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠬࡸࡥࡳࡷࡱࡣࡵࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡠࡨࡤ࡭ࡱ࡫ࡤࠨἜ")] = {
            bstack1ll111_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧἝ"): self.bstack1111l111l1l_opy_()
        }
        bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠧࡳࡷࡱࡣࡵࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡠࡨࡤ࡭ࡱ࡫ࡤࡠࡨ࡬ࡶࡸࡺࠧ἞")] = {
            bstack1ll111_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩ἟"): self.bstack1111lll1l11_opy_()
        }
        bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠩࡶ࡯࡮ࡶ࡟ࡧࡣ࡬ࡰ࡮ࡴࡧࡠࡣࡱࡨࡤ࡬࡬ࡢ࡭ࡼࠫἠ")] = {
            bstack1ll111_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫἡ"): self.bstack1111lll11l1_opy_()
        }
        if self.bstack11ll1l11_opy_(config):
            bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠫࡷ࡫ࡴࡳࡻࡢࡸࡪࡹࡴࡴࡡࡲࡲࡤ࡬ࡡࡪ࡮ࡸࡶࡪ࠭ἢ")] = {
                bstack1ll111_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ἣ"): True,
                bstack1ll111_opy_ (u"࠭࡭ࡢࡺࡢࡶࡪࡺࡲࡪࡧࡶࠫἤ"): self.bstack1l11l1l1ll_opy_(config)
            }
        if self.bstack11l11ll111l_opy_(config):
            bstack1111l1l111l_opy_[bstack1ll111_opy_ (u"ࠧࡢࡤࡲࡶࡹࡥࡢࡶ࡫࡯ࡨࡤࡵ࡮ࡠࡨࡤ࡭ࡱࡻࡲࡦࠩἥ")] = {
                bstack1ll111_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩἦ"): True,
                bstack1ll111_opy_ (u"ࠩࡰࡥࡽࡥࡦࡢ࡫࡯ࡹࡷ࡫ࡳࠨἧ"): self.bstack11l11lll1l1_opy_(config)
            }
        return bstack1111l1l111l_opy_
    def bstack11ll1lll_opy_(self, config):
        bstack1ll111_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡄࡱ࡯ࡰࡪࡩࡴࡴࠢࡥࡹ࡮ࡲࡤࠡࡦࡤࡸࡦࠦࡢࡺࠢࡰࡥࡰ࡯࡮ࡨࠢࡤࠤࡨࡧ࡬࡭ࠢࡷࡳࠥࡺࡨࡦࠢࡦࡳࡱࡲࡥࡤࡶ࠰ࡦࡺ࡯࡬ࡥ࠯ࡧࡥࡹࡧࠠࡦࡰࡧࡴࡴ࡯࡮ࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡸ࡭ࡱࡪ࡟ࡶࡷ࡬ࡨࠥ࠮ࡳࡵࡴࠬ࠾࡚ࠥࡨࡦࠢࡘ࡙ࡎࡊࠠࡰࡨࠣࡸ࡭࡫ࠠࡣࡷ࡬ࡰࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡨࡦࡺࡡࠡࡨࡲࡶ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥ࡫ࡦࡸ࠿ࠦࡒࡦࡵࡳࡳࡳࡹࡥࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡧࡻࡩ࡭ࡦ࠰ࡨࡦࡺࡡࠡࡧࡱࡨࡵࡵࡩ࡯ࡶ࠯ࠤࡴࡸࠠࡏࡱࡱࡩࠥ࡯ࡦࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨἨ")
        if not (config.get(bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧἩ"), None) in bstack11l1l1lll11_opy_ and self.bstack1111l1l1lll_opy_()):
            return None
        bstack1111l111ll1_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪἪ"), None)
        logger.debug(bstack1ll111_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡈࡵ࡬࡭ࡧࡦࡸ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡥࡹ࡮ࡲࡤࠡࡗࡘࡍࡉࡀࠠࡼࡿࠥἫ").format(bstack1111l111ll1_opy_))
        try:
            bstack11l1llll111_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃ࠯ࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠧἬ").format(bstack1111l111ll1_opy_)
            payload = {
                bstack1ll111_opy_ (u"ࠣࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪࠨἭ"): config.get(bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧἮ"), bstack1ll111_opy_ (u"ࠪࠫἯ")),
                bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠢἰ"): config.get(bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨἱ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡗࡻ࡮ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠦἲ"): os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࠨἳ"), bstack1ll111_opy_ (u"ࠣࠤἴ")),
                bstack1ll111_opy_ (u"ࠤࡱࡳࡩ࡫ࡉ࡯ࡦࡨࡼࠧἵ"): int(os.environ.get(bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨἶ")) or bstack1ll111_opy_ (u"ࠦ࠵ࠨἷ")),
                bstack1ll111_opy_ (u"ࠧࡺ࡯ࡵࡣ࡯ࡒࡴࡪࡥࡴࠤἸ"): int(os.environ.get(bstack1ll111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡏࡕࡃࡏࡣࡓࡕࡄࡆࡡࡆࡓ࡚ࡔࡔࠣἹ")) or bstack1ll111_opy_ (u"ࠢ࠲ࠤἺ")),
                bstack1ll111_opy_ (u"ࠣࡪࡲࡷࡹࡏ࡮ࡧࡱࠥἻ"): get_host_info(),
            }
            logger.debug(bstack1ll111_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡤࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥࡶࡡࡺ࡮ࡲࡥࡩࡀࠠࡼࡿࠥἼ").format(payload))
            response = bstack11l1lll11ll_opy_.bstack1111l11l111_opy_(bstack11l1llll111_opy_, payload)
            if response:
                logger.debug(bstack1ll111_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡄࡸ࡭ࡱࡪࠠࡥࡣࡷࡥࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣἽ").format(response))
                return response
            else:
                logger.error(bstack1ll111_opy_ (u"ࠦࡠࡩ࡯࡭࡮ࡨࡧࡹࡈࡵࡪ࡮ࡧࡈࡦࡺࡡ࡞ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩ࡯࡭࡮ࡨࡧࡹࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡕࡖࡋࡇ࠾ࠥࢁࡽࠣἾ").format(bstack1111l111ll1_opy_))
                return None
        except Exception as e:
            logger.error(bstack1ll111_opy_ (u"ࠧࡡࡣࡰ࡮࡯ࡩࡨࡺࡂࡶ࡫࡯ࡨࡉࡧࡴࡢ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡲ࡬ࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡣࡷ࡬ࡰࡩࠦࡕࡖࡋࡇࠤࢀࢃ࠺ࠡࡽࢀࠦἿ").format(bstack1111l111ll1_opy_, e))
            return None