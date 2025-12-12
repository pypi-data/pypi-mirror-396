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
import json
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1lllll11_opy_(object):
  bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩឮ")), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨឯ"))
  bstack11l1llll11l_opy_ = os.path.join(bstack11lllll1l_opy_, bstack1ll111_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶ࠲࡯ࡹ࡯࡯ࠩឰ"))
  commands_to_wrap = None
  perform_scan = None
  bstack11lll111l_opy_ = None
  bstack1l11l11lll_opy_ = None
  bstack11ll11lll11_opy_ = None
  bstack11ll1l11111_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1ll111_opy_ (u"ࠪ࡭ࡳࡹࡴࡢࡰࡦࡩࠬឱ")):
      cls.instance = super(bstack11l1lllll11_opy_, cls).__new__(cls)
      cls.instance.bstack11l1lllll1l_opy_()
    return cls.instance
  def bstack11l1lllll1l_opy_(self):
    try:
      with open(self.bstack11l1llll11l_opy_, bstack1ll111_opy_ (u"ࠫࡷ࠭ឲ")) as bstack11111ll11_opy_:
        bstack11l1llll1ll_opy_ = bstack11111ll11_opy_.read()
        data = json.loads(bstack11l1llll1ll_opy_)
        if bstack1ll111_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧឳ") in data:
          self.bstack11ll1l1111l_opy_(data[bstack1ll111_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨ឴")])
        if bstack1ll111_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨ឵") in data:
          self.bstack1l1111l1l_opy_(data[bstack1ll111_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩា")])
        if bstack1ll111_opy_ (u"ࠩࡱࡳࡳࡈࡓࡵࡣࡦ࡯ࡎࡴࡦࡳࡣࡄ࠵࠶ࡿࡃࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ិ") in data:
          self.bstack11l1llll1l1_opy_(data[bstack1ll111_opy_ (u"ࠪࡲࡴࡴࡂࡔࡶࡤࡧࡰࡏ࡮ࡧࡴࡤࡅ࠶࠷ࡹࡄࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧី")])
    except:
      pass
  def bstack11l1llll1l1_opy_(self, bstack11ll1l11111_opy_):
    if bstack11ll1l11111_opy_ != None:
      self.bstack11ll1l11111_opy_ = bstack11ll1l11111_opy_
  def bstack1l1111l1l_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack1ll111_opy_ (u"ࠫࡸࡩࡡ࡯ࠩឹ"),bstack1ll111_opy_ (u"ࠬ࠭ឺ"))
      self.bstack11lll111l_opy_ = scripts.get(bstack1ll111_opy_ (u"࠭ࡧࡦࡶࡕࡩࡸࡻ࡬ࡵࡵࠪុ"),bstack1ll111_opy_ (u"ࠧࠨូ"))
      self.bstack1l11l11lll_opy_ = scripts.get(bstack1ll111_opy_ (u"ࠨࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࡘࡻ࡭࡮ࡣࡵࡽࠬួ"),bstack1ll111_opy_ (u"ࠩࠪើ"))
      self.bstack11ll11lll11_opy_ = scripts.get(bstack1ll111_opy_ (u"ࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨឿ"),bstack1ll111_opy_ (u"ࠫࠬៀ"))
  def bstack11ll1l1111l_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1llll11l_opy_, bstack1ll111_opy_ (u"ࠬࡽࠧេ")) as file:
        json.dump({
          bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࠣែ"): self.commands_to_wrap,
          bstack1ll111_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࡳࠣៃ"): {
            bstack1ll111_opy_ (u"ࠣࡵࡦࡥࡳࠨោ"): self.perform_scan,
            bstack1ll111_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸࠨៅ"): self.bstack11lll111l_opy_,
            bstack1ll111_opy_ (u"ࠥ࡫ࡪࡺࡒࡦࡵࡸࡰࡹࡹࡓࡶ࡯ࡰࡥࡷࡿࠢំ"): self.bstack1l11l11lll_opy_,
            bstack1ll111_opy_ (u"ࠦࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠤះ"): self.bstack11ll11lll11_opy_
          },
          bstack1ll111_opy_ (u"ࠧࡴ࡯࡯ࡄࡖࡸࡦࡩ࡫ࡊࡰࡩࡶࡦࡇ࠱࠲ࡻࡆ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠤៈ"): self.bstack11ll1l11111_opy_
        }, file)
    except Exception as e:
      logger.error(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡸࡺ࡯ࡳ࡫ࡱ࡫ࠥࡩ࡯࡮࡯ࡤࡲࡩࡹ࠺ࠡࡽࢀࠦ៉").format(e))
      pass
  def bstack11l1l1lll1_opy_(self, command_name):
    try:
      return any(command.get(bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ៊")) == command_name for command in self.commands_to_wrap)
    except:
      return False
bstack111llll1ll_opy_ = bstack11l1lllll11_opy_()