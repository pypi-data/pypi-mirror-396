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
import multiprocessing
import os
from bstack_utils.config import Config
class bstack11llllll1_opy_():
  def __init__(self, args, logger, bstack11111111l1_opy_, bstack1111111lll_opy_, bstack1llllll1ll1_opy_):
    self.args = args
    self.logger = logger
    self.bstack11111111l1_opy_ = bstack11111111l1_opy_
    self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    self.bstack1llllll1ll1_opy_ = bstack1llllll1ll1_opy_
  def bstack11l1l11ll1_opy_(self, bstack1lllllll111_opy_, bstack1l111lll1l_opy_, bstack1llllll1lll_opy_=False):
    bstack1l11lll1ll_opy_ = []
    manager = multiprocessing.Manager()
    bstack1llllllll11_opy_ = manager.list()
    bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
    if bstack1llllll1lll_opy_:
      for index, platform in enumerate(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬდ")]):
        if index == 0:
          bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ე")] = self.args
        bstack1l11lll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1lllllll111_opy_,
                                                    args=(bstack1l111lll1l_opy_, bstack1llllllll11_opy_)))
    else:
      for index, platform in enumerate(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧვ")]):
        bstack1l11lll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1lllllll111_opy_,
                                                    args=(bstack1l111lll1l_opy_, bstack1llllllll11_opy_)))
    i = 0
    for t in bstack1l11lll1ll_opy_:
      try:
        if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ზ")):
          os.environ[bstack1ll111_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧთ")] = json.dumps(self.bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪი")][i % self.bstack1llllll1ll1_opy_])
      except Exception as e:
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡵࡱࡵ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶ࠾ࠥࢁࡽࠣკ").format(str(e)))
      i += 1
      t.start()
    for t in bstack1l11lll1ll_opy_:
      t.join()
    return list(bstack1llllllll11_opy_)