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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lllll1llll_opy_ import bstack1llllll111l_opy_
class bstack1ll1ll1l1l1_opy_(abc.ABC):
    bin_session_id: str
    bstack1lllll1llll_opy_: bstack1llllll111l_opy_
    def __init__(self):
        self.bstack1lll1l11lll_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lllll1llll_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1ll1llll1ll_opy_(self):
        return (self.bstack1lll1l11lll_opy_ != None and self.bin_session_id != None and self.bstack1lllll1llll_opy_ != None)
    def configure(self, bstack1lll1l11lll_opy_, config, bin_session_id: str, bstack1lllll1llll_opy_: bstack1llllll111l_opy_):
        self.bstack1lll1l11lll_opy_ = bstack1lll1l11lll_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lllll1llll_opy_ = bstack1lllll1llll_opy_
        if self.bin_session_id:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡦࡦࠣࡱࡴࡪࡵ࡭ࡧࠣࡿࡸ࡫࡬ࡧ࠰ࡢࡣࡨࡲࡡࡴࡵࡢࡣ࠳ࡥ࡟࡯ࡣࡰࡩࡤࡥࡽ࠻ࠢࡥ࡭ࡳࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࡀࠦኦ") + str(self.bin_session_id) + bstack1ll111_opy_ (u"ࠣࠤኧ"))
    def bstack1ll1111l1ll_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack1ll111_opy_ (u"ࠤࡥ࡭ࡳࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠣࡧࡦࡴ࡮ࡰࡶࠣࡦࡪࠦࡎࡰࡰࡨࠦከ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False