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
import threading
import logging
import bstack_utils.accessibility as bstack1llll111_opy_
from bstack_utils.helper import bstack11111l1l1_opy_
logger = logging.getLogger(__name__)
def bstack1l1111ll_opy_(bstack11l1lll1_opy_):
  return True if bstack11l1lll1_opy_ in threading.current_thread().__dict__.keys() else False
def bstack11111lll_opy_(context, *args):
    tags = getattr(args[0], bstack1ll111_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭៙"), [])
    bstack1l11ll11l1_opy_ = bstack1llll111_opy_.bstack11ll11lll1_opy_(tags)
    threading.current_thread().isA11yTest = bstack1l11ll11l1_opy_
    try:
      bstack11ll111lll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1111ll_opy_(bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ៚")) else context.browser
      if bstack11ll111lll_opy_ and bstack11ll111lll_opy_.session_id and bstack1l11ll11l1_opy_ and bstack11111l1l1_opy_(
              threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ៛"), None):
          threading.current_thread().isA11yTest = bstack1llll111_opy_.bstack1111lll1l_opy_(bstack11ll111lll_opy_, bstack1l11ll11l1_opy_)
    except Exception as e:
       logger.debug(bstack1ll111_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡡ࠲࠳ࡼࠤ࡮ࡴࠠࡣࡧ࡫ࡥࡻ࡫࠺ࠡࡽࢀࠫៜ").format(str(e)))
def bstack1l1lllll1l_opy_(bstack11ll111lll_opy_):
    if bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬ࡯ࡳࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ៝"), None) and bstack11111l1l1_opy_(
      threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ៞"), None) and not bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡢ࠳࠴ࡽࡤࡹࡴࡰࡲࠪ៟"), False):
      threading.current_thread().a11y_stop = True
      bstack1llll111_opy_.bstack111lll1111_opy_(bstack11ll111lll_opy_, name=bstack1ll111_opy_ (u"ࠣࠤ០"), path=bstack1ll111_opy_ (u"ࠤࠥ១"))