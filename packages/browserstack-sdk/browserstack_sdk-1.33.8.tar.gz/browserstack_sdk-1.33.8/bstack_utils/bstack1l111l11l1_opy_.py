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
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll111l111_opy_, bstack1l1lll11l1_opy_, get_host_info, bstack111l1ll11ll_opy_, \
 bstack1ll1l1111_opy_, bstack11111l1l1_opy_, error_handler, bstack11l111ll11l_opy_, bstack11ll1l111_opy_
import bstack_utils.accessibility as bstack1llll111_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
from bstack_utils.percy import bstack11lllll11_opy_
from bstack_utils.config import Config
bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
logger = logging.getLogger(__name__)
percy = bstack11lllll11_opy_()
@error_handler(class_method=False)
def bstack1lll1lll1ll1_opy_(bs_config, bstack11l11111l1_opy_):
  try:
    data = {
        bstack1ll111_opy_ (u"ࠪࡪࡴࡸ࡭ࡢࡶࠪ∿"): bstack1ll111_opy_ (u"ࠫ࡯ࡹ࡯࡯ࠩ≀"),
        bstack1ll111_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡥ࡮ࡢ࡯ࡨࠫ≁"): bs_config.get(bstack1ll111_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ≂"), bstack1ll111_opy_ (u"ࠧࠨ≃")),
        bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭≄"): bs_config.get(bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ≅"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭≆"): bs_config.get(bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭≇")),
        bstack1ll111_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪ≈"): bs_config.get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡉ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ≉"), bstack1ll111_opy_ (u"ࠧࠨ≊")),
        bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ≋"): bstack11ll1l111_opy_(),
        bstack1ll111_opy_ (u"ࠩࡷࡥ࡬ࡹࠧ≌"): bstack111l1ll11ll_opy_(bs_config),
        bstack1ll111_opy_ (u"ࠪ࡬ࡴࡹࡴࡠ࡫ࡱࡪࡴ࠭≍"): get_host_info(),
        bstack1ll111_opy_ (u"ࠫࡨ࡯࡟ࡪࡰࡩࡳࠬ≎"): bstack1l1lll11l1_opy_(),
        bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣࡷࡻ࡮ࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ≏"): os.environ.get(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬ≐")),
        bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡲࡦࡴࡸࡲࠬ≑"): os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓ࠭≒"), False),
        bstack1ll111_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࡢࡧࡴࡴࡴࡳࡱ࡯ࠫ≓"): bstack11ll111l111_opy_(),
        bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ≔"): bstack1lll1ll1l1ll_opy_(bs_config),
        bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡥࡧࡷࡥ࡮ࡲࡳࠨ≕"): bstack1lll1ll1llll_opy_(bstack11l11111l1_opy_),
        bstack1ll111_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪ≖"): bstack1lll1ll1ll1l_opy_(bs_config, bstack11l11111l1_opy_.get(bstack1ll111_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧ≗"), bstack1ll111_opy_ (u"ࠧࠨ≘"))),
        bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪ≙"): bstack1ll1l1111_opy_(bs_config),
        bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠧ≚"): bstack1lll1ll1ll11_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack1ll111_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡱࡣࡼࡰࡴࡧࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࠡࡽࢀࠦ≛").format(str(error)))
    return None
def bstack1lll1ll1llll_opy_(framework):
  return {
    bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡎࡢ࡯ࡨࠫ≜"): framework.get(bstack1ll111_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪ࠭≝"), bstack1ll111_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠭≞")),
    bstack1ll111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪ≟"): framework.get(bstack1ll111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ≠")),
    bstack1ll111_opy_ (u"ࠩࡶࡨࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭≡"): framework.get(bstack1ll111_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ≢")),
    bstack1ll111_opy_ (u"ࠫࡱࡧ࡮ࡨࡷࡤ࡫ࡪ࠭≣"): bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ≤"),
    bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭≥"): framework.get(bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ≦"))
  }
def bstack1lll1ll1ll11_opy_(bs_config):
  bstack1ll111_opy_ (u"ࠣࠤࠥࠎࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡵࡪࡨࠤࡹ࡫ࡳࡵࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦࠣࡷࡹࡧࡲࡵ࠰ࠍࠤࠥࠨࠢࠣ≧")
  if not bs_config:
    return {}
  bstack1111ll1111l_opy_ = bstack11ll1lll1l_opy_(bs_config).bstack1111l11l1l1_opy_(bs_config)
  return bstack1111ll1111l_opy_
def bstack1111llll_opy_(bs_config, framework):
  bstack11l1l11l11_opy_ = False
  bstack11l111ll_opy_ = False
  bstack1lll1lll111l_opy_ = False
  if bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭≨") in bs_config:
    bstack1lll1lll111l_opy_ = True
  elif bstack1ll111_opy_ (u"ࠪࡥࡵࡶࠧ≩") in bs_config:
    bstack11l1l11l11_opy_ = True
  else:
    bstack11l111ll_opy_ = True
  bstack1l11l111ll_opy_ = {
    bstack1ll111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ≪"): bstack1llll1111_opy_.bstack1lll1ll1lll1_opy_(bs_config, framework),
    bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ≫"): bstack1llll111_opy_.bstack1lllll11l_opy_(bs_config),
    bstack1ll111_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ≬"): bs_config.get(bstack1ll111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭≭"), False),
    bstack1ll111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪ≮"): bstack11l111ll_opy_,
    bstack1ll111_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨ≯"): bstack11l1l11l11_opy_,
    bstack1ll111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧ≰"): bstack1lll1lll111l_opy_
  }
  return bstack1l11l111ll_opy_
@error_handler(class_method=False)
def bstack1lll1ll1l1ll_opy_(bs_config):
  try:
    bstack1lll1lll1l11_opy_ = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ≱"), bstack1ll111_opy_ (u"ࠬࢁࡽࠨ≲")))
    bstack1lll1lll1l11_opy_ = bstack1lll1lll11ll_opy_(bs_config, bstack1lll1lll1l11_opy_)
    return {
        bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡷ࡭ࡳ࡭ࡳࠨ≳"): bstack1lll1lll1l11_opy_
    }
  except Exception as error:
    logger.error(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤ࡬࡫ࡴࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡵࡨࡸࡹ࡯࡮ࡨࡵࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨ≴").format(str(error)))
    return {}
def bstack1lll1lll11ll_opy_(bs_config, bstack1lll1lll1l11_opy_):
  if ((bstack1ll111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ≵") in bs_config or not bstack1ll1l1111_opy_(bs_config)) and bstack1llll111_opy_.bstack1lllll11l_opy_(bs_config)):
    bstack1lll1lll1l11_opy_[bstack1ll111_opy_ (u"ࠤ࡬ࡲࡨࡲࡵࡥࡧࡈࡲࡨࡵࡤࡦࡦࡈࡼࡹ࡫࡮ࡴ࡫ࡲࡲࠧ≶")] = True
  return bstack1lll1lll1l11_opy_
def bstack1llll111l1ll_opy_(array, bstack1lll1ll11lll_opy_, bstack1lll1ll1l111_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1ll11lll_opy_]
    result[key] = o[bstack1lll1ll1l111_opy_]
  return result
def bstack1llll111111l_opy_(bstack1lll1lll11_opy_=bstack1ll111_opy_ (u"ࠪࠫ≷")):
  bstack1lll1lll1111_opy_ = bstack1llll111_opy_.on()
  bstack1lll1lll11l1_opy_ = bstack1llll1111_opy_.on()
  bstack1lll1ll1l1l1_opy_ = percy.bstack1l11111l_opy_()
  if bstack1lll1ll1l1l1_opy_ and not bstack1lll1lll11l1_opy_ and not bstack1lll1lll1111_opy_:
    return bstack1lll1lll11_opy_ not in [bstack1ll111_opy_ (u"ࠫࡈࡈࡔࡔࡧࡶࡷ࡮ࡵ࡮ࡄࡴࡨࡥࡹ࡫ࡤࠨ≸"), bstack1ll111_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩ≹")]
  elif bstack1lll1lll1111_opy_ and not bstack1lll1lll11l1_opy_:
    return bstack1lll1lll11_opy_ not in [bstack1ll111_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ≺"), bstack1ll111_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ≻"), bstack1ll111_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬ≼")]
  return bstack1lll1lll1111_opy_ or bstack1lll1lll11l1_opy_ or bstack1lll1ll1l1l1_opy_
@error_handler(class_method=False)
def bstack1llll1111ll1_opy_(bstack1lll1lll11_opy_, test=None):
  bstack1lll1ll1l11l_opy_ = bstack1llll111_opy_.on()
  if not bstack1lll1ll1l11l_opy_ or bstack1lll1lll11_opy_ not in [bstack1ll111_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ≽")] or test == None:
    return None
  return {
    bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ≾"): bstack1lll1ll1l11l_opy_ and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ≿"), None) == True and bstack1llll111_opy_.bstack11ll11lll1_opy_(test[bstack1ll111_opy_ (u"ࠬࡺࡡࡨࡵࠪ⊀")])
  }
def bstack1lll1ll1ll1l_opy_(bs_config, framework):
  bstack11l1l11l11_opy_ = False
  bstack11l111ll_opy_ = False
  bstack1lll1lll111l_opy_ = False
  if bstack1ll111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ⊁") in bs_config:
    bstack1lll1lll111l_opy_ = True
  elif bstack1ll111_opy_ (u"ࠧࡢࡲࡳࠫ⊂") in bs_config:
    bstack11l1l11l11_opy_ = True
  else:
    bstack11l111ll_opy_ = True
  bstack1l11l111ll_opy_ = {
    bstack1ll111_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ⊃"): bstack1llll1111_opy_.bstack1lll1ll1lll1_opy_(bs_config, framework),
    bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ⊄"): bstack1llll111_opy_.bstack11llll11l_opy_(bs_config),
    bstack1ll111_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ⊅"): bs_config.get(bstack1ll111_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪ⊆"), False),
    bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ⊇"): bstack11l111ll_opy_,
    bstack1ll111_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ⊈"): bstack11l1l11l11_opy_,
    bstack1ll111_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫ⊉"): bstack1lll1lll111l_opy_
  }
  return bstack1l11l111ll_opy_