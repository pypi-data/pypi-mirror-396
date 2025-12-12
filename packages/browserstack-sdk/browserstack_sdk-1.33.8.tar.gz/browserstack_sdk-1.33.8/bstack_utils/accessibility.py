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
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll111111l_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll1l11l11_opy_ as bstack11ll111lll1_opy_, EVENTS
from bstack_utils.bstack111llll1ll_opy_ import bstack111llll1ll_opy_
from bstack_utils.helper import bstack11ll1l111_opy_, bstack1111l1lll1_opy_, bstack1ll1l1111_opy_, bstack11ll11ll1ll_opy_, \
  bstack11l1lllllll_opy_, bstack1l1lll11l1_opy_, get_host_info, bstack11ll111l111_opy_, bstack1l1l111111_opy_, error_handler, bstack11ll1111l1l_opy_, bstack11ll111l11l_opy_, bstack11111l1l1_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack1ll1lll11_opy_ = bstack1ll1ll111ll_opy_()
@error_handler(class_method=False)
def _11ll11lll1l_opy_(driver, bstack11111l11l1_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack1ll111_opy_ (u"ࠬࡵࡳࡠࡰࡤࡱࡪ࠭ᙸ"): caps.get(bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᙹ"), None),
        bstack1ll111_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫᙺ"): bstack11111l11l1_opy_.get(bstack1ll111_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫᙻ"), None),
        bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡲࡦࡳࡥࠨᙼ"): caps.get(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨᙽ"), None),
        bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᙾ"): caps.get(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᙿ"), None)
    }
  except Exception as error:
    logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࠢࡧࡩࡹࡧࡩ࡭ࡵࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠ࠻ࠢࠪ ") + str(error))
  return response
def on():
    if os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᚁ"), None) is None or os.environ[bstack1ll111_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᚂ")] == bstack1ll111_opy_ (u"ࠤࡱࡹࡱࡲࠢᚃ"):
        return False
    return True
def bstack1lllll11l_opy_(config):
  return config.get(bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᚄ"), False) or any([p.get(bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚅ"), False) == True for p in config.get(bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᚆ"), [])])
def bstack1llll111l_opy_(config, bstack1lll1l1l_opy_):
  try:
    bstack11ll11lllll_opy_ = config.get(bstack1ll111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᚇ"), False)
    if int(bstack1lll1l1l_opy_) < len(config.get(bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪᚈ"), [])) and config[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᚉ")][bstack1lll1l1l_opy_]:
      bstack11ll1l11lll_opy_ = config[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᚊ")][bstack1lll1l1l_opy_].get(bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᚋ"), None)
    else:
      bstack11ll1l11lll_opy_ = config.get(bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᚌ"), None)
    if bstack11ll1l11lll_opy_ != None:
      bstack11ll11lllll_opy_ = bstack11ll1l11lll_opy_
    bstack11ll11ll11l_opy_ = os.getenv(bstack1ll111_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᚍ")) is not None and len(os.getenv(bstack1ll111_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᚎ"))) > 0 and os.getenv(bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᚏ")) != bstack1ll111_opy_ (u"ࠨࡰࡸࡰࡱ࠭ᚐ")
    return bstack11ll11lllll_opy_ and bstack11ll11ll11l_opy_
  except Exception as error:
    logger.debug(bstack1ll111_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡸࡨࡶ࡮࡬ࡹࡪࡰࡪࠤࡹ࡮ࡥࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࠦ࠺ࠡࠩᚑ") + str(error))
  return False
def bstack11ll11lll1_opy_(test_tags):
  bstack1ll1111111l_opy_ = os.getenv(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᚒ"))
  if bstack1ll1111111l_opy_ is None:
    return True
  bstack1ll1111111l_opy_ = json.loads(bstack1ll1111111l_opy_)
  try:
    include_tags = bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᚓ")] if bstack1ll111_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᚔ") in bstack1ll1111111l_opy_ and isinstance(bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᚕ")], list) else []
    exclude_tags = bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᚖ")] if bstack1ll111_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᚗ") in bstack1ll1111111l_opy_ and isinstance(bstack1ll1111111l_opy_[bstack1ll111_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᚘ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack1ll111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡸࡤࡰ࡮ࡪࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡨࡲࡶࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡨࡥࡧࡱࡵࡩࠥࡹࡣࡢࡰࡱ࡭ࡳ࡭࠮ࠡࡇࡵࡶࡴࡸࠠ࠻ࠢࠥᚙ") + str(error))
  return False
def bstack11ll11l1l1l_opy_(config, bstack11ll11l1l11_opy_, bstack11ll1l11l1l_opy_, bstack11ll1l1l111_opy_):
  bstack11ll111ll1l_opy_ = bstack11ll11ll1ll_opy_(config)
  bstack11ll111ll11_opy_ = bstack11l1lllllll_opy_(config)
  if bstack11ll111ll1l_opy_ is None or bstack11ll111ll11_opy_ is None:
    logger.error(bstack1ll111_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡣࡳࡧࡤࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡲࡶࡰࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠽ࠤࡒ࡯ࡳࡴ࡫ࡱ࡫ࠥࡧࡵࡵࡪࡨࡲࡹ࡯ࡣࡢࡶ࡬ࡳࡳࠦࡴࡰ࡭ࡨࡲࠬᚚ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭᚛"), bstack1ll111_opy_ (u"࠭ࡻࡾࠩ᚜")))
    data = {
        bstack1ll111_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬ᚝"): config[bstack1ll111_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭᚞")],
        bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ᚟"): config.get(bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ᚠ"), os.path.basename(os.getcwd())),
        bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡗ࡭ࡲ࡫ࠧᚡ"): bstack11ll1l111_opy_(),
        bstack1ll111_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᚢ"): config.get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡉ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩᚣ"), bstack1ll111_opy_ (u"ࠧࠨᚤ")),
        bstack1ll111_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨᚥ"): {
            bstack1ll111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡓࡧ࡭ࡦࠩᚦ"): bstack11ll11l1l11_opy_,
            bstack1ll111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᚧ"): bstack11ll1l11l1l_opy_,
            bstack1ll111_opy_ (u"ࠫࡸࡪ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᚨ"): __version__,
            bstack1ll111_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠧᚩ"): bstack1ll111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ᚪ"),
            bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧᚫ"): bstack1ll111_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࠪᚬ"),
            bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᚭ"): bstack11ll1l1l111_opy_
        },
        bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡴࡪࡰࡪࡷࠬᚮ"): settings,
        bstack1ll111_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࡈࡵ࡮ࡵࡴࡲࡰࠬᚯ"): bstack11ll111l111_opy_(),
        bstack1ll111_opy_ (u"ࠬࡩࡩࡊࡰࡩࡳࠬᚰ"): bstack1l1lll11l1_opy_(),
        bstack1ll111_opy_ (u"࠭ࡨࡰࡵࡷࡍࡳ࡬࡯ࠨᚱ"): get_host_info(),
        bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᚲ"): bstack1ll1l1111_opy_(config)
    }
    headers = {
        bstack1ll111_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧᚳ"): bstack1ll111_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬᚴ"),
    }
    config = {
        bstack1ll111_opy_ (u"ࠪࡥࡺࡺࡨࠨᚵ"): (bstack11ll111ll1l_opy_, bstack11ll111ll11_opy_),
        bstack1ll111_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᚶ"): headers
    }
    response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠬࡖࡏࡔࡖࠪᚷ"), bstack11ll111lll1_opy_ + bstack1ll111_opy_ (u"࠭࠯ࡷ࠴࠲ࡸࡪࡹࡴࡠࡴࡸࡲࡸ࠭ᚸ"), data, config)
    bstack11ll1l111ll_opy_ = response.json()
    if bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨᚹ")]:
      parsed = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᚺ"), bstack1ll111_opy_ (u"ࠩࡾࢁࠬᚻ")))
      parsed[bstack1ll111_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᚼ")] = bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠫࡩࡧࡴࡢࠩᚽ")][bstack1ll111_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᚾ")]
      os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᚿ")] = json.dumps(parsed)
      bstack111llll1ll_opy_.bstack1l1111l1l_opy_(bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠧࡥࡣࡷࡥࠬᛀ")][bstack1ll111_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩᛁ")])
      bstack111llll1ll_opy_.bstack11ll1l1111l_opy_(bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠩࡧࡥࡹࡧࠧᛂ")][bstack1ll111_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡷࠬᛃ")])
      bstack111llll1ll_opy_.store()
      return bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠫࡩࡧࡴࡢࠩᛄ")][bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࡙ࡵ࡫ࡦࡰࠪᛅ")], bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"࠭ࡤࡢࡶࡤࠫᛆ")][bstack1ll111_opy_ (u"ࠧࡪࡦࠪᛇ")]
    else:
      logger.error(bstack1ll111_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡶࡺࡴ࡮ࡪࡰࡪࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠺ࠡࠩᛈ") + bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᛉ")])
      if bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᛊ")] == bstack1ll111_opy_ (u"ࠫࡎࡴࡶࡢ࡮࡬ࡨࠥࡩ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠥࡶࡡࡴࡵࡨࡨ࠳࠭ᛋ"):
        for bstack11ll111l1l1_opy_ in bstack11ll1l111ll_opy_[bstack1ll111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࡷࠬᛌ")]:
          logger.error(bstack11ll111l1l1_opy_[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᛍ")])
      return None, None
  except Exception as error:
    logger.error(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡵࡹࡳࠦࡦࡰࡴࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡀࠠࠣᛎ") +  str(error))
    return None, None
def bstack11ll11111ll_opy_():
  if os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᛏ")) is None:
    return {
        bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩᛐ"): bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᛑ"),
        bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᛒ"): bstack1ll111_opy_ (u"ࠬࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡨࡢࡦࠣࡪࡦ࡯࡬ࡦࡦ࠱ࠫᛓ")
    }
  data = {bstack1ll111_opy_ (u"࠭ࡥ࡯ࡦࡗ࡭ࡲ࡫ࠧᛔ"): bstack11ll1l111_opy_()}
  headers = {
      bstack1ll111_opy_ (u"ࠧࡂࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧᛕ"): bstack1ll111_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࠩᛖ") + os.getenv(bstack1ll111_opy_ (u"ࠤࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠢᛗ")),
      bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩᛘ"): bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧᛙ")
  }
  response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠬࡖࡕࡕࠩᛚ"), bstack11ll111lll1_opy_ + bstack1ll111_opy_ (u"࠭࠯ࡵࡧࡶࡸࡤࡸࡵ࡯ࡵ࠲ࡷࡹࡵࡰࠨᛛ"), data, { bstack1ll111_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨᛜ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack1ll111_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤ࡙࡫ࡳࡵࠢࡕࡹࡳࠦ࡭ࡢࡴ࡮ࡩࡩࠦࡡࡴࠢࡦࡳࡲࡶ࡬ࡦࡶࡨࡨࠥࡧࡴࠡࠤᛝ") + bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"ࠩ࡝ࠫᛞ"))
      return {bstack1ll111_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪᛟ"): bstack1ll111_opy_ (u"ࠫࡸࡻࡣࡤࡧࡶࡷࠬᛠ"), bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᛡ"): bstack1ll111_opy_ (u"࠭ࠧᛢ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡰࡥࡷࡱࡩ࡯ࡩࠣࡧࡴࡳࡰ࡭ࡧࡷ࡭ࡴࡴࠠࡰࡨࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡔࡦࡵࡷࠤࡗࡻ࡮࠻ࠢࠥᛣ") + str(error))
    return {
        bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨᛤ"): bstack1ll111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᛥ"),
        bstack1ll111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᛦ"): str(error)
    }
def bstack11ll1111111_opy_(bstack11ll11ll111_opy_):
    return re.match(bstack1ll111_opy_ (u"ࡶࠬࡤ࡜ࡥ࠭ࠫࡠ࠳ࡢࡤࠬࠫࡂࠨࠬᛧ"), bstack11ll11ll111_opy_.strip()) is not None
def bstack1ll1l11111_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll11111l1_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll11111l1_opy_ = desired_capabilities
        else:
          bstack11ll11111l1_opy_ = {}
        bstack1ll11l1ll11_opy_ = (bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠫᛨ"), bstack1ll111_opy_ (u"࠭ࠧᛩ")).lower() or caps.get(bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭ᛪ"), bstack1ll111_opy_ (u"ࠨࠩ᛫")).lower())
        if bstack1ll11l1ll11_opy_ == bstack1ll111_opy_ (u"ࠩ࡬ࡳࡸ࠭᛬"):
            return True
        if bstack1ll11l1ll11_opy_ == bstack1ll111_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࠫ᛭"):
            bstack1ll111l1lll_opy_ = str(float(caps.get(bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᛮ")) or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᛯ"), {}).get(bstack1ll111_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩᛰ"),bstack1ll111_opy_ (u"ࠧࠨᛱ"))))
            if bstack1ll11l1ll11_opy_ == bstack1ll111_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࠩᛲ") and int(bstack1ll111l1lll_opy_.split(bstack1ll111_opy_ (u"ࠩ࠱ࠫᛳ"))[0]) < float(bstack11ll1l111l1_opy_):
                logger.warning(str(bstack11ll1111l11_opy_))
                return False
            return True
        bstack1ll1111llll_opy_ = caps.get(bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᛴ"), {}).get(bstack1ll111_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨᛵ"), caps.get(bstack1ll111_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬᛶ"), bstack1ll111_opy_ (u"࠭ࠧᛷ")))
        if bstack1ll1111llll_opy_:
            logger.warning(bstack1ll111_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡅࡧࡶ࡯ࡹࡵࡰࠡࡤࡵࡳࡼࡹࡥࡳࡵ࠱ࠦᛸ"))
            return False
        browser = caps.get(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭᛹"), bstack1ll111_opy_ (u"ࠩࠪ᛺")).lower() or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨ᛻"), bstack1ll111_opy_ (u"ࠫࠬ᛼")).lower()
        if browser != bstack1ll111_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ᛽"):
            logger.warning(bstack1ll111_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࡳ࠯ࠤ᛾"))
            return False
        browser_version = caps.get(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᛿")) or caps.get(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪᜀ")) or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᜁ")) or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᜂ"), {}).get(bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᜃ")) or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᜄ"), {}).get(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᜅ"))
        bstack1ll11111l1l_opy_ = bstack11ll111111l_opy_.bstack1ll1111l1l1_opy_
        bstack11l1llllll1_opy_ = False
        if config is not None:
          bstack11l1llllll1_opy_ = bstack1ll111_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᜆ") in config and str(config[bstack1ll111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᜇ")]).lower() != bstack1ll111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨᜈ")
        if os.environ.get(bstack1ll111_opy_ (u"ࠪࡍࡘࡥࡎࡐࡐࡢࡆࡘ࡚ࡁࡄࡍࡢࡍࡓࡌࡒࡂࡡࡄ࠵࠶࡟࡟ࡔࡇࡖࡗࡎࡕࡎࠨᜉ"), bstack1ll111_opy_ (u"ࠫࠬᜊ")).lower() == bstack1ll111_opy_ (u"ࠬࡺࡲࡶࡧࠪᜋ") or bstack11l1llllll1_opy_:
          bstack1ll11111l1l_opy_ = bstack11ll111111l_opy_.bstack1ll111lll1l_opy_
        if browser_version and browser_version != bstack1ll111_opy_ (u"࠭࡬ࡢࡶࡨࡷࡹ࠭ᜌ") and int(browser_version.split(bstack1ll111_opy_ (u"ࠧ࠯ࠩᜍ"))[0]) <= bstack1ll11111l1l_opy_:
          logger.warning(bstack1lll11ll11l_opy_ (u"ࠨࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡅ࡫ࡶࡴࡳࡥࠡࡤࡵࡳࡼࡹࡥࡳࠢࡹࡩࡷࡹࡩࡰࡰࠣ࡫ࡷ࡫ࡡࡵࡧࡵࠤࡹ࡮ࡡ࡯ࠢࡾࡱ࡮ࡴ࡟ࡢ࠳࠴ࡽࡤࡹࡵࡱࡲࡲࡶࡹ࡫ࡤࡠࡥ࡫ࡶࡴࡳࡥࡠࡸࡨࡶࡸ࡯࡯࡯ࡿ࠱ࠫᜎ"))
          return False
        if not options:
          bstack1l1lllllll1_opy_ = caps.get(bstack1ll111_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᜏ")) or bstack11ll11111l1_opy_.get(bstack1ll111_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᜐ"), {})
          if bstack1ll111_opy_ (u"ࠫ࠲࠳ࡨࡦࡣࡧࡰࡪࡹࡳࠨᜑ") in bstack1l1lllllll1_opy_.get(bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪᜒ"), []):
              logger.warning(bstack1ll111_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡲࡲࠥࡲࡥࡨࡣࡦࡽࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠦࡓࡸ࡫ࡷࡧ࡭ࠦࡴࡰࠢࡱࡩࡼࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪࠦ࡯ࡳࠢࡤࡺࡴ࡯ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠣᜓ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡶࡢ࡮࡬ࡨࡦࡺࡥࠡࡣ࠴࠵ࡾࠦࡳࡶࡲࡳࡳࡷࡺࠠ࠻ࠤ᜔") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1ll1l1llll1_opy_ = config.get(bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᜕"), {})
    bstack1ll1l1llll1_opy_[bstack1ll111_opy_ (u"ࠩࡤࡹࡹ࡮ࡔࡰ࡭ࡨࡲࠬ᜖")] = os.getenv(bstack1ll111_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ᜗"))
    bstack11ll111llll_opy_ = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ᜘"), bstack1ll111_opy_ (u"ࠬࢁࡽࠨ᜙"))).get(bstack1ll111_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ᜚"))
    if not config[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩ᜛")].get(bstack1ll111_opy_ (u"ࠣࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠢ᜜")):
      if bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ᜝") in caps:
        caps[bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ᜞")][bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᜟ")] = bstack1ll1l1llll1_opy_
        caps[bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᜠ")][bstack1ll111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᜡ")][bstack1ll111_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᜢ")] = bstack11ll111llll_opy_
      else:
        caps[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᜣ")] = bstack1ll1l1llll1_opy_
        caps[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᜤ")][bstack1ll111_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᜥ")] = bstack11ll111llll_opy_
  except Exception as error:
    logger.debug(bstack1ll111_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵ࠱ࠤࡊࡸࡲࡰࡴ࠽ࠤࠧᜦ") +  str(error))
def bstack1111lll1l_opy_(driver, bstack11ll11ll1l1_opy_):
  try:
    setattr(driver, bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬᜧ"), True)
    session = driver.session_id
    if session:
      bstack11ll1111ll1_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11ll1111ll1_opy_ = False
      bstack11ll1111ll1_opy_ = url.scheme in [bstack1ll111_opy_ (u"ࠨࡨࡵࡶࡳࠦᜨ"), bstack1ll111_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᜩ")]
      if bstack11ll1111ll1_opy_:
        if bstack11ll11ll1l1_opy_:
          logger.info(bstack1ll111_opy_ (u"ࠣࡕࡨࡸࡺࡶࠠࡧࡱࡵࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡮ࡡࡴࠢࡶࡸࡦࡸࡴࡦࡦ࠱ࠤࡆࡻࡴࡰ࡯ࡤࡸࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡨࡼࡪࡩࡵࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡦࡪ࡭ࡩ࡯ࠢࡰࡳࡲ࡫࡮ࡵࡣࡵ࡭ࡱࡿ࠮ࠣᜪ"))
      return bstack11ll11ll1l1_opy_
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࡩ࡯ࡩࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡥࡤࡲࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧ࠽ࠤࠧᜫ") + str(e))
    return False
def bstack111lll1111_opy_(driver, name, path):
  try:
    bstack1ll11l1111l_opy_ = {
        bstack1ll111_opy_ (u"ࠪࡸ࡭࡚ࡥࡴࡶࡕࡹࡳ࡛ࡵࡪࡦࠪᜬ"): threading.current_thread().current_test_uuid,
        bstack1ll111_opy_ (u"ࠫࡹ࡮ࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᜭ"): os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᜮ"), bstack1ll111_opy_ (u"࠭ࠧᜯ")),
        bstack1ll111_opy_ (u"ࠧࡵࡪࡍࡻࡹ࡚࡯࡬ࡧࡱࠫᜰ"): os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬᜱ"), bstack1ll111_opy_ (u"ࠩࠪᜲ"))
    }
    bstack1ll111lllll_opy_ = bstack1ll1lll11_opy_.bstack1ll111ll11l_opy_(EVENTS.bstack1lllll11ll_opy_.value)
    logger.debug(bstack1ll111_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥࡨࡥࡧࡱࡵࡩࠥࡹࡡࡷ࡫ࡱ࡫ࠥࡸࡥࡴࡷ࡯ࡸࡸ࠭ᜳ"))
    try:
      if (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫ࡮ࡹࡁࡱࡲࡄ࠵࠶ࡿࡔࡦࡵࡷ᜴ࠫ"), None) and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ᜵"), None)):
        scripts = {bstack1ll111_opy_ (u"࠭ࡳࡤࡣࡱࠫ᜶"): bstack111llll1ll_opy_.perform_scan}
        bstack11ll11llll1_opy_ = json.loads(scripts[bstack1ll111_opy_ (u"ࠢࡴࡥࡤࡲࠧ᜷")].replace(bstack1ll111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࠦ᜸"), bstack1ll111_opy_ (u"ࠤࠥ᜹")))
        bstack11ll11llll1_opy_[bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭᜺")][bstack1ll111_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧࠫ᜻")] = None
        scripts[bstack1ll111_opy_ (u"ࠧࡹࡣࡢࡰࠥ᜼")] = bstack1ll111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࠤ᜽") + json.dumps(bstack11ll11llll1_opy_)
        bstack111llll1ll_opy_.bstack1l1111l1l_opy_(scripts)
        bstack111llll1ll_opy_.store()
        logger.debug(driver.execute_script(bstack111llll1ll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111llll1ll_opy_.perform_scan, {bstack1ll111_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠢ᜾"): name}))
      bstack1ll1lll11_opy_.end(EVENTS.bstack1lllll11ll_opy_.value, bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣ᜿"), bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᝀ"), True, None)
    except Exception as error:
      bstack1ll1lll11_opy_.end(EVENTS.bstack1lllll11ll_opy_.value, bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᝁ"), bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᝂ"), False, str(error))
    bstack1ll111lllll_opy_ = bstack1ll1lll11_opy_.bstack11ll1111lll_opy_(EVENTS.bstack1ll11l1ll1l_opy_.value)
    bstack1ll1lll11_opy_.mark(bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᝃ"))
    try:
      if (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ᝄ"), None) and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᝅ"), None)):
        scripts = {bstack1ll111_opy_ (u"ࠨࡵࡦࡥࡳ࠭ᝆ"): bstack111llll1ll_opy_.perform_scan}
        bstack11ll11llll1_opy_ = json.loads(scripts[bstack1ll111_opy_ (u"ࠤࡶࡧࡦࡴࠢᝇ")].replace(bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࠨᝈ"), bstack1ll111_opy_ (u"ࠦࠧᝉ")))
        bstack11ll11llll1_opy_[bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨᝊ")][bstack1ll111_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩ࠭ᝋ")] = None
        scripts[bstack1ll111_opy_ (u"ࠢࡴࡥࡤࡲࠧᝌ")] = bstack1ll111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࠦᝍ") + json.dumps(bstack11ll11llll1_opy_)
        bstack111llll1ll_opy_.bstack1l1111l1l_opy_(scripts)
        bstack111llll1ll_opy_.store()
        logger.debug(driver.execute_script(bstack111llll1ll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack111llll1ll_opy_.bstack11ll11lll11_opy_, bstack1ll11l1111l_opy_))
      bstack1ll1lll11_opy_.end(bstack1ll111lllll_opy_, bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᝎ"), bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᝏ"),True, None)
    except Exception as error:
      bstack1ll1lll11_opy_.end(bstack1ll111lllll_opy_, bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᝐ"), bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᝑ"),False, str(error))
    logger.info(bstack1ll111_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡴࡦࡵࡷ࡭ࡳ࡭ࠠࡧࡱࡵࠤࡹ࡮ࡩࡴࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡮ࡡࡴࠢࡨࡲࡩ࡫ࡤ࠯ࠤᝒ"))
  except Exception as bstack1ll11l11lll_opy_:
    logger.error(bstack1ll111_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡥࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡧ࡫ࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡪࡴࡸࠠࡵࡪࡨࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫࠺ࠡࠤᝓ") + str(path) + bstack1ll111_opy_ (u"ࠣࠢࡈࡶࡷࡵࡲࠡ࠼ࠥ᝔") + str(bstack1ll11l11lll_opy_))
def bstack11ll111l1ll_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack1ll111_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣ᝕")) and str(caps.get(bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ᝖"))).lower() == bstack1ll111_opy_ (u"ࠦࡦࡴࡤࡳࡱ࡬ࡨࠧ᝗"):
        bstack1ll111l1lll_opy_ = caps.get(bstack1ll111_opy_ (u"ࠧࡧࡰࡱ࡫ࡸࡱ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢ᝘")) or caps.get(bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ᝙"))
        if bstack1ll111l1lll_opy_ and int(str(bstack1ll111l1lll_opy_)) < bstack11ll1l111l1_opy_:
            return False
    return True
def bstack11llll11l_opy_(config):
  if bstack1ll111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ᝚") in config:
        return config[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ᝛")]
  for platform in config.get(bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ᝜"), []):
      if bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ᝝") in platform:
          return platform[bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ᝞")]
  return None
def bstack1ll11l11l1_opy_(bstack11ll111l1_opy_):
  try:
    browser_name = bstack11ll111l1_opy_[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥ࡮ࡢ࡯ࡨࠫ᝟")]
    browser_version = bstack11ll111l1_opy_[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᝠ")]
    chrome_options = bstack11ll111l1_opy_[bstack1ll111_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫࡟ࡰࡲࡷ࡭ࡴࡴࡳࠨᝡ")]
    try:
        bstack11ll11l11ll_opy_ = int(browser_version.split(bstack1ll111_opy_ (u"ࠨ࠰ࠪᝢ"))[0])
    except ValueError as e:
        logger.error(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡱࡱࡺࡪࡸࡴࡪࡰࡪࠤࡧࡸ࡯ࡸࡵࡨࡶࠥࡼࡥࡳࡵ࡬ࡳࡳࠨᝣ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack1ll111_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪᝤ")):
        logger.warning(bstack1ll111_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢᝥ"))
        return False
    if bstack11ll11l11ll_opy_ < bstack11ll111111l_opy_.bstack1ll111lll1l_opy_:
        logger.warning(bstack1lll11ll11l_opy_ (u"ࠬࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡵࡩࡶࡻࡩࡳࡧࡶࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࢁࡃࡐࡐࡖࡘࡆࡔࡔࡔ࠰ࡐࡍࡓࡏࡍࡖࡏࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘ࡛ࡐࡑࡑࡕࡘࡊࡊ࡟ࡄࡊࡕࡓࡒࡋ࡟ࡗࡇࡕࡗࡎࡕࡎࡾࠢࡲࡶࠥ࡮ࡩࡨࡪࡨࡶ࠳࠭ᝦ"))
        return False
    if chrome_options and any(bstack1ll111_opy_ (u"࠭࠭࠮ࡪࡨࡥࡩࡲࡥࡴࡵࠪᝧ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack1ll111_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡲࡶࡰࠣࡳࡳࠦ࡬ࡦࡩࡤࡧࡾࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠠࡔࡹ࡬ࡸࡨ࡮ࠠࡵࡱࠣࡲࡪࡽࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫ࠠࡰࡴࠣࡥࡻࡵࡩࡥࠢࡸࡷ࡮ࡴࡧࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠤᝨ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡧ࡭࡫ࡣ࡬࡫ࡱ࡫ࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠠࡴࡷࡳࡴࡴࡸࡴࠡࡨࡲࡶࠥࡲ࡯ࡤࡣ࡯ࠤࡈ࡮ࡲࡰ࡯ࡨ࠾ࠥࠨᝩ") + str(e))
    return False
def bstack111lll11l_opy_(bstack1l11111l11_opy_, config):
    try:
      bstack1ll111llll1_opy_ = bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᝪ") in config and config[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᝫ")] == True
      bstack11l1llllll1_opy_ = bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᝬ") in config and str(config[bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᝭")]).lower() != bstack1ll111_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬᝮ")
      if not (bstack1ll111llll1_opy_ and (not bstack1ll1l1111_opy_(config) or bstack11l1llllll1_opy_)):
        return bstack1l11111l11_opy_
      bstack11ll11l1ll1_opy_ = bstack111llll1ll_opy_.bstack11ll1l11111_opy_
      if bstack11ll11l1ll1_opy_ is None:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡈࡱࡲ࡫ࡱ࡫ࠠࡤࡪࡵࡳࡲ࡫ࠠࡰࡲࡷ࡭ࡴࡴࡳࠡࡣࡵࡩࠥࡔ࡯࡯ࡧࠥᝯ"))
        return bstack1l11111l11_opy_
      bstack11ll11l1111_opy_ = int(str(bstack11ll111l11l_opy_()).split(bstack1ll111_opy_ (u"ࠨ࠰ࠪᝰ"))[0])
      logger.debug(bstack1ll111_opy_ (u"ࠤࡖࡩࡱ࡫࡮ࡪࡷࡰࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡪࡥࡵࡧࡦࡸࡪࡪ࠺ࠡࠤ᝱") + str(bstack11ll11l1111_opy_) + bstack1ll111_opy_ (u"ࠥࠦᝲ"))
      if bstack11ll11l1111_opy_ == 3 and isinstance(bstack1l11111l11_opy_, dict) and bstack1ll111_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫᝳ") in bstack1l11111l11_opy_ and bstack11ll11l1ll1_opy_ is not None:
        if bstack1ll111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᝴") not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭᝵")]:
          bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᝶")][bstack1ll111_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᝷")] = {}
        if bstack1ll111_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ᝸") in bstack11ll11l1ll1_opy_:
          if bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ᝹") not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫ᝺")][bstack1ll111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᝻")]:
            bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭᝼")][bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ᝽")][bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭᝾")] = []
          for arg in bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ᝿")]:
            if arg not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪក")][bstack1ll111_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩខ")][bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪគ")]:
              bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ឃ")][bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬង")][bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ច")].append(arg)
        if bstack1ll111_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ឆ") in bstack11ll11l1ll1_opy_:
          if bstack1ll111_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧជ") not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫឈ")][bstack1ll111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪញ")]:
            bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ដ")][bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬឋ")][bstack1ll111_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬឌ")] = []
          for ext in bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ឍ")]:
            if ext not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪណ")][bstack1ll111_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩត")][bstack1ll111_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩថ")]:
              bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ទ")][bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬធ")][bstack1ll111_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬន")].append(ext)
        if bstack1ll111_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨប") in bstack11ll11l1ll1_opy_:
          if bstack1ll111_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩផ") not in bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫព")][bstack1ll111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪភ")]:
            bstack1l11111l11_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ម")][bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬយ")][bstack1ll111_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧរ")] = {}
          bstack11ll1111l1l_opy_(bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩល")][bstack1ll111_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨវ")][bstack1ll111_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪឝ")],
                    bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫឞ")])
        os.environ[bstack1ll111_opy_ (u"࠭ࡉࡔࡡࡑࡓࡓࡥࡂࡔࡖࡄࡇࡐࡥࡉࡏࡈࡕࡅࡤࡇ࠱࠲࡛ࡢࡗࡊ࡙ࡓࡊࡑࡑࠫស")] = bstack1ll111_opy_ (u"ࠧࡵࡴࡸࡩࠬហ")
        return bstack1l11111l11_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l11111l11_opy_, ChromeOptions):
          chrome_options = bstack1l11111l11_opy_
        elif isinstance(bstack1l11111l11_opy_, dict):
          for value in bstack1l11111l11_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l11111l11_opy_, dict):
            bstack1l11111l11_opy_[bstack1ll111_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩឡ")] = chrome_options
          else:
            bstack1l11111l11_opy_ = chrome_options
        if bstack11ll11l1ll1_opy_ is not None:
          if bstack1ll111_opy_ (u"ࠩࡤࡶ࡬ࡹࠧអ") in bstack11ll11l1ll1_opy_:
                bstack11ll11l1lll_opy_ = chrome_options.arguments or []
                new_args = bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨឣ")]
                for arg in new_args:
                    if arg not in bstack11ll11l1lll_opy_:
                        chrome_options.add_argument(arg)
          if bstack1ll111_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨឤ") in bstack11ll11l1ll1_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack1ll111_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩឥ"), [])
                bstack11ll11l111l_opy_ = bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪឦ")]
                for extension in bstack11ll11l111l_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack1ll111_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ឧ") in bstack11ll11l1ll1_opy_:
                bstack11ll11l11l1_opy_ = chrome_options.experimental_options.get(bstack1ll111_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧឨ"), {})
                bstack11ll1l11ll1_opy_ = bstack11ll11l1ll1_opy_[bstack1ll111_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨឩ")]
                bstack11ll1111l1l_opy_(bstack11ll11l11l1_opy_, bstack11ll1l11ll1_opy_)
                chrome_options.add_experimental_option(bstack1ll111_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩឪ"), bstack11ll11l11l1_opy_)
        os.environ[bstack1ll111_opy_ (u"ࠫࡎ࡙࡟ࡏࡑࡑࡣࡇ࡙ࡔࡂࡅࡎࡣࡎࡔࡆࡓࡃࡢࡅ࠶࠷࡙ࡠࡕࡈࡗࡘࡏࡏࡏࠩឫ")] = bstack1ll111_opy_ (u"ࠬࡺࡲࡶࡧࠪឬ")
        return bstack1l11111l11_opy_
    except Exception as e:
      logger.error(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡦࡪࡤࡪࡰࡪࠤࡳࡵ࡮࠮ࡄࡖࠤ࡮ࡴࡦࡳࡣࠣࡥ࠶࠷ࡹࠡࡥ࡫ࡶࡴࡳࡥࠡࡱࡳࡸ࡮ࡵ࡮ࡴ࠼ࠣࠦឭ") + str(e))
      return bstack1l11111l11_opy_