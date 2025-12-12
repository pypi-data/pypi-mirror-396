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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1lll111l_opy_ import bstack11l1lll11ll_opy_
from bstack_utils.constants import *
import json
class bstack1l1llllll_opy_:
    def __init__(self, bstack1l1lll1l_opy_, bstack11l1lll1l11_opy_):
        self.bstack1l1lll1l_opy_ = bstack1l1lll1l_opy_
        self.bstack11l1lll1l11_opy_ = bstack11l1lll1l11_opy_
        self.bstack11l1lll1l1l_opy_ = None
    def __call__(self):
        bstack11l1lll1111_opy_ = {}
        while True:
            self.bstack11l1lll1l1l_opy_ = bstack11l1lll1111_opy_.get(
                bstack1ll111_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭៏"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1ll1lll1_opy_ = self.bstack11l1lll1l1l_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1ll1lll1_opy_ > 0:
                sleep(bstack11l1ll1lll1_opy_ / 1000)
            params = {
                bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭័"): self.bstack1l1lll1l_opy_,
                bstack1ll111_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ៑"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1ll1llll_opy_ = bstack1ll111_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱្ࠥ") + bstack11l1lll1ll1_opy_ + bstack1ll111_opy_ (u"ࠤ࠲ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡧࡰࡪ࠱ࡹ࠵࠴ࠨ៓")
            if self.bstack11l1lll1l11_opy_.lower() == bstack1ll111_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡶࠦ។"):
                bstack11l1lll1111_opy_ = bstack11l1lll11ll_opy_.results(bstack11l1ll1llll_opy_, params)
            else:
                bstack11l1lll1111_opy_ = bstack11l1lll11ll_opy_.bstack11l1lll11l1_opy_(bstack11l1ll1llll_opy_, params)
            if str(bstack11l1lll1111_opy_.get(bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ៕"), bstack1ll111_opy_ (u"ࠬ࠸࠰࠱ࠩ៖"))) != bstack1ll111_opy_ (u"࠭࠴࠱࠶ࠪៗ"):
                break
        return bstack11l1lll1111_opy_.get(bstack1ll111_opy_ (u"ࠧࡥࡣࡷࡥࠬ៘"), bstack11l1lll1111_opy_)