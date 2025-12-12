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
import atexit
import shlex
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from browserstack_sdk.bstack1llll11ll_opy_ import bstack11llllll1_opy_
from browserstack_sdk.bstack1l11ll11_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE, bstack1l1111lll_opy_
from bstack_utils.messages import bstack1ll1111ll_opy_, bstack1l1l11ll1_opy_, bstack1ll1ll1lll_opy_, bstack11l111ll1_opy_, bstack1lll11ll11_opy_, bstack11ll1llll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
from bstack_utils.helper import bstack1l1l1ll11l_opy_
from browserstack_sdk.bstack1ll11llll_opy_ import bstack1llll11l1_opy_
logger = get_logger(__name__)
def bstack1l1l11ll_opy_():
  global CONFIG
  headers = {
        bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1l1l1ll11l_opy_(CONFIG, bstack1l1111lll_opy_)
  try:
    response = requests.get(bstack1l1111lll_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1l1l1l1111_opy_ = response.json()[bstack1ll111_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1ll1111ll_opy_.format(response.json()))
      return bstack1l1l1l1111_opy_
    else:
      logger.debug(bstack1l1l11ll1_opy_.format(bstack1ll111_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack1l1l11ll1_opy_.format(e))
def bstack11l1ll111l_opy_(hub_url):
  global CONFIG
  url = bstack1ll111_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack1ll111_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack1ll111_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack1ll111_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1l1l1ll11l_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1ll1ll1lll_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack11l111ll1_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack111lllll1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack1l11l11l11_opy_():
  try:
    global bstack1ll1l111l_opy_
    global CONFIG
    if bstack1ll111_opy_ (u"ࠫ࡭ࡻࡢࡓࡧࡪ࡭ࡴࡴࠧࡾ") in CONFIG and CONFIG[bstack1ll111_opy_ (u"ࠬ࡮ࡵࡣࡔࡨ࡫࡮ࡵ࡮ࠨࡿ")]:
      from bstack_utils.constants import bstack1ll11l1lll_opy_
      bstack1l11lll1l_opy_ = CONFIG[bstack1ll111_opy_ (u"࠭ࡨࡶࡤࡕࡩ࡬࡯࡯࡯ࠩࢀ")]
      if bstack1l11lll1l_opy_ in bstack1ll11l1lll_opy_:
        bstack1ll1l111l_opy_ = bstack1ll11l1lll_opy_[bstack1l11lll1l_opy_]
        logger.debug(bstack1lll11ll11_opy_.format(bstack1ll1l111l_opy_))
        return
      else:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡉࡷࡥࠤࡰ࡫ࡹࠡࠩࡾࢁࠬࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠢ࡬ࡲࠥࡎࡕࡃࡡࡘࡖࡑࡥࡍࡂࡒ࠯ࠤ࡫ࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦ࡯ࡱࡶ࡬ࡱࡦࡲࠠࡩࡷࡥࠤࡩ࡫ࡴࡦࡥࡷ࡭ࡴࡴࠢࢁ").format(bstack1l11lll1l_opy_))
    bstack1l1l1l1111_opy_ = bstack1l1l11ll_opy_()
    bstack111lll11l1_opy_ = []
    results = []
    for bstack11lll1111_opy_ in bstack1l1l1l1111_opy_:
      bstack111lll11l1_opy_.append(bstack1llll11l1_opy_(target=bstack11l1ll111l_opy_,args=(bstack11lll1111_opy_,)))
    for t in bstack111lll11l1_opy_:
      t.start()
    for t in bstack111lll11l1_opy_:
      results.append(t.join())
    bstack111l11l1l_opy_ = {}
    for item in results:
      hub_url = item[bstack1ll111_opy_ (u"ࠨࡪࡸࡦࡤࡻࡲ࡭ࠩࢂ")]
      latency = item[bstack1ll111_opy_ (u"ࠩ࡯ࡥࡹ࡫࡮ࡤࡻࠪࢃ")]
      bstack111l11l1l_opy_[hub_url] = latency
    bstack111lll111_opy_ = min(bstack111l11l1l_opy_, key= lambda x: bstack111l11l1l_opy_[x])
    bstack1ll1l111l_opy_ = bstack111lll111_opy_
    logger.debug(bstack1lll11ll11_opy_.format(bstack111lll111_opy_))
  except Exception as e:
    logger.debug(bstack11ll1llll_opy_.format(e))
from browserstack_sdk.bstack1llll11lll_opy_ import *
from browserstack_sdk.bstack1ll11llll_opy_ import *
from browserstack_sdk.bstack11ll1lllll_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack11ll111111_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack1l111lllll_opy_():
    global bstack1ll1l111l_opy_
    try:
        bstack1l11llll_opy_ = bstack1lllllll11_opy_()
        bstack111l1l11l_opy_(bstack1l11llll_opy_)
        hub_url = bstack1l11llll_opy_.get(bstack1ll111_opy_ (u"ࠥࡹࡷࡲࠢࢄ"), bstack1ll111_opy_ (u"ࠦࠧࢅ"))
        if hub_url.endswith(bstack1ll111_opy_ (u"ࠬ࠵ࡷࡥ࠱࡫ࡹࡧ࠭ࢆ")):
            hub_url = hub_url.rsplit(bstack1ll111_opy_ (u"࠭࠯ࡸࡦ࠲࡬ࡺࡨࠧࢇ"), 1)[0]
        if hub_url.startswith(bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࠨ࢈")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack1ll111_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࠪࢉ")):
            hub_url = hub_url[8:]
        bstack1ll1l111l_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack1lllllll11_opy_():
    global CONFIG
    bstack1l111l11ll_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢊ"), {}).get(bstack1ll111_opy_ (u"ࠪ࡫ࡷ࡯ࡤࡏࡣࡰࡩࠬࢋ"), bstack1ll111_opy_ (u"ࠫࡓࡕ࡟ࡈࡔࡌࡈࡤࡔࡁࡎࡇࡢࡔࡆ࡙ࡓࡆࡆࠪࢌ"))
    if not isinstance(bstack1l111l11ll_opy_, str):
        raise ValueError(bstack1ll111_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡌࡸࡩࡥࠢࡱࡥࡲ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡣࠣࡺࡦࡲࡩࡥࠢࡶࡸࡷ࡯࡮ࡨࠤࢍ"))
    try:
        bstack1l11llll_opy_ = bstack1ll11l11_opy_(bstack1l111l11ll_opy_)
        return bstack1l11llll_opy_
    except Exception as e:
        logger.error(bstack1ll111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧࢎ").format(str(e)))
        return {}
def bstack1ll11l11_opy_(bstack1l111l11ll_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ࢏")] or not CONFIG[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ࢐")]:
            raise ValueError(bstack1ll111_opy_ (u"ࠤࡐ࡭ࡸࡹࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠤࡴࡸࠠࡢࡥࡦࡩࡸࡹࠠ࡬ࡧࡼࠦ࢑"))
        url = bstack111111ll_opy_ + bstack1l111l11ll_opy_
        auth = (CONFIG[bstack1ll111_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ࢒")], CONFIG[bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ࢓")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack11l111111_opy_ = json.loads(response.text)
            return bstack11l111111_opy_
    except ValueError as ve:
        logger.error(bstack1ll111_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡩࡵ࡭ࡩࠦࡤࡦࡶࡤ࡭ࡱࡹࠠ࠻ࠢࡾࢁࠧ࢔").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack1ll111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡪࡶ࡮ࡪࠠࡥࡧࡷࡥ࡮ࡲࡳࠡ࠼ࠣࡿࢂࠨ࢕").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack111l1l11l_opy_(bstack11111111l_opy_):
    global CONFIG
    if bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ࢖") not in CONFIG or str(CONFIG[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬࢗ")]).lower() == bstack1ll111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ࢘"):
        CONFIG[bstack1ll111_opy_ (u"ࠪࡰࡴࡩࡡ࡭࢙ࠩ")] = False
    elif bstack1ll111_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥ࢚ࠩ") in bstack11111111l_opy_:
        bstack1111ll1l1_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴ࢛ࠩ"), {})
        logger.debug(bstack1ll111_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡋࡸࡪࡵࡷ࡭ࡳ࡭ࠠ࡭ࡱࡦࡥࡱࠦ࡯ࡱࡶ࡬ࡳࡳࡹ࠺ࠡࠧࡶࠦ࢜"), bstack1111ll1l1_opy_)
        bstack111lll11ll_opy_ = bstack11111111l_opy_.get(bstack1ll111_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳࡒࡦࡲࡨࡥࡹ࡫ࡲࡴࠤ࢝"), [])
        bstack1llll1l111_opy_ = bstack1ll111_opy_ (u"ࠣ࠮ࠥ࢞").join(bstack111lll11ll_opy_)
        logger.debug(bstack1ll111_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡅࡸࡷࡹࡵ࡭ࠡࡴࡨࡴࡪࡧࡴࡦࡴࠣࡷࡹࡸࡩ࡯ࡩ࠽ࠤࠪࡹࠢ࢟"), bstack1llll1l111_opy_)
        bstack11l1l11111_opy_ = {
            bstack1ll111_opy_ (u"ࠥࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠧࢠ"): bstack1ll111_opy_ (u"ࠦࡦࡺࡳ࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠥࢡ"),
            bstack1ll111_opy_ (u"ࠧ࡬࡯ࡳࡥࡨࡐࡴࡩࡡ࡭ࠤࢢ"): bstack1ll111_opy_ (u"ࠨࡴࡳࡷࡨࠦࢣ"),
            bstack1ll111_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࠭ࡳࡧࡳࡩࡦࡺࡥࡳࠤࢤ"): bstack1llll1l111_opy_
        }
        bstack1111ll1l1_opy_.update(bstack11l1l11111_opy_)
        logger.debug(bstack1ll111_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡖࡲࡧࡥࡹ࡫ࡤࠡ࡮ࡲࡧࡦࡲࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠨࡷࠧࢥ"), bstack1111ll1l1_opy_)
        CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")] = bstack1111ll1l1_opy_
        logger.debug(bstack1ll111_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡉ࡭ࡳࡧ࡬ࠡࡅࡒࡒࡋࡏࡇ࠻ࠢࠨࡷࠧࢧ"), CONFIG)
def bstack1l1l11l1l1_opy_():
    bstack1l11llll_opy_ = bstack1lllllll11_opy_()
    if not bstack1l11llll_opy_[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡖࡴ࡯ࠫࢨ")]:
      raise ValueError(bstack1ll111_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡗࡵࡰࠥ࡯ࡳࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡩࡶࡴࡳࠠࡨࡴ࡬ࡨࠥࡪࡥࡵࡣ࡬ࡰࡸ࠴ࠢࢩ"))
    return bstack1l11llll_opy_[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡘࡶࡱ࠭ࢪ")] + bstack1ll111_opy_ (u"ࠧࡀࡥࡤࡴࡸࡃࠧࢫ")
@measure(event_name=EVENTS.bstack1ll1lll1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack11111llll_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack1ll111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪࢬ")], CONFIG[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࢭ")])
        url = bstack1ll11l111_opy_
        logger.debug(bstack1ll111_opy_ (u"ࠥࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡶࡴࡳࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡔࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠣࡅࡕࡏࠢࢮ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack1ll111_opy_ (u"ࠦࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠥࢯ"): bstack1ll111_opy_ (u"ࠧࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠣࢰ")})
            if response.status_code == 200:
                bstack1l1l111l1l_opy_ = json.loads(response.text)
                bstack1l1lll11ll_opy_ = bstack1l1l111l1l_opy_.get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠭ࢱ"), [])
                if bstack1l1lll11ll_opy_:
                    bstack11l1lll11_opy_ = bstack1l1lll11ll_opy_[0]
                    build_hashed_id = bstack11l1lll11_opy_.get(bstack1ll111_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪࢲ"))
                    bstack11l1l1lll_opy_ = bstack11l1ll1ll1_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack11l1l1lll_opy_])
                    logger.info(bstack111lll1lll_opy_.format(bstack11l1l1lll_opy_))
                    bstack1l11ll1ll_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫࢳ")]
                    if bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࢴ") in CONFIG:
                      bstack1l11ll1ll_opy_ += bstack1ll111_opy_ (u"ࠪࠤࠬࢵ") + CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࢶ")]
                    if bstack1l11ll1ll_opy_ != bstack11l1lll11_opy_.get(bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢷ")):
                      logger.debug(bstack1l1ll11ll1_opy_.format(bstack11l1lll11_opy_.get(bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫࢸ")), bstack1l11ll1ll_opy_))
                    return result
                else:
                    logger.debug(bstack1ll111_opy_ (u"ࠢࡂࡖࡖࠤ࠿ࠦࡎࡰࠢࡥࡹ࡮ࡲࡤࡴࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠱ࠦࢹ"))
            else:
                logger.debug(bstack1ll111_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢺ"))
        except Exception as e:
            logger.error(bstack1ll111_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡶࠤ࠿ࠦࡻࡾࠤࢻ").format(str(e)))
    else:
        logger.debug(bstack1ll111_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡆࡓࡓࡌࡉࡈࠢ࡬ࡷࠥࡴ࡯ࡵࠢࡶࡩࡹ࠴ࠠࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡥࡹ࡮ࡲࡤࡴ࠰ࠥࢼ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack111lll1l1_opy_ import bstack111lll1l1_opy_, bstack111llll1l_opy_, bstack1l1llll1_opy_, bstack1llllll1l1_opy_
from bstack_utils.measure import bstack1ll1lll11_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1l11ll1l1_opy_ import bstack1ll111l111_opy_
from bstack_utils.messages import *
from bstack_utils import bstack1llll1ll1l_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack111llll11_opy_, bstack1l1l111111_opy_, bstack1l111l1l1l_opy_, bstack11111l1l1_opy_, \
  bstack1ll1l1111_opy_, \
  Notset, bstack11l1lll11l_opy_, \
  bstack1111ll1l_opy_, bstack11lll1l1_opy_, bstack11ll111ll1_opy_, bstack1l1lll11l1_opy_, bstack11l11l11l_opy_, bstack1ll1l1l1ll_opy_, \
  bstack1ll1l11l1_opy_, \
  bstack1l111l1l1_opy_, bstack1ll1l11ll_opy_, bstack1lll11l1l_opy_, bstack11l11l1111_opy_, \
  bstack1ll1111lll_opy_, bstack1l1l111l11_opy_, bstack1l1l1111l1_opy_, bstack11lll11lll_opy_, bstack11ll1l11ll_opy_
from bstack_utils.bstack1111l11ll_opy_ import bstack1lll1ll1l1_opy_
from bstack_utils.bstack11l11111_opy_ import bstack1ll111ll1_opy_, bstack1lll11ll_opy_
from bstack_utils.bstack1lllll111l_opy_ import bstack111llllll1_opy_
from bstack_utils.bstack1l11l1111_opy_ import bstack11ll1ll11_opy_, bstack1l1l1ll1l1_opy_
from bstack_utils.bstack111llll1ll_opy_ import bstack111llll1ll_opy_
from bstack_utils.bstack1lllll11_opy_ import bstack1l1llllll_opy_
from bstack_utils.proxy import bstack1l11ll1ll1_opy_, bstack1l1l1ll11l_opy_, bstack1ll1ll111l_opy_, bstack1l1l11lll_opy_
from bstack_utils.bstack11ll11ll1_opy_ import bstack1ll11111l1_opy_
import bstack_utils.bstack1l111l11l1_opy_ as bstack1111ll11_opy_
import bstack_utils.bstack1l11lll1l1_opy_ as bstack11ll11ll11_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1l11l1l11l_opy_ import bstack1ll1llll_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from bstack_utils.bstack1l11ll11ll_opy_ import bstack11l11111ll_opy_
if os.getenv(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡉࡑࡒࡏࡘ࠭ࢽ")):
  cli.bstack1lll1llll_opy_()
else:
  os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡒࡉࡠࡊࡒࡓࡐ࡙ࠧࢾ")] = bstack1ll111_opy_ (u"࠭ࡴࡳࡷࡨࠫࢿ")
bstack11l1l1l1l_opy_ = bstack1ll111_opy_ (u"ࠧࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠠࠡ࡫ࡩࠬࡵࡧࡧࡦࠢࡀࡁࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠠࡼ࡞ࡱࠤࠥࠦࡴࡳࡻࡾࡠࡳࠦࡣࡰࡰࡶࡸࠥ࡬ࡳࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࡡ࠭ࡦࡴ࡞ࠪ࠭ࡀࡢ࡮ࠡࠢࠣࠤࠥ࡬ࡳ࠯ࡣࡳࡴࡪࡴࡤࡇ࡫࡯ࡩࡘࡿ࡮ࡤࠪࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠬࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡳࡣ࡮ࡴࡤࡦࡺࠬࠤ࠰ࠦࠢ࠻ࠤࠣ࠯ࠥࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࠬࡦࡽࡡࡪࡶࠣࡲࡪࡽࡐࡢࡩࡨ࠶࠳࡫ࡶࡢ࡮ࡸࡥࡹ࡫ࠨࠣࠪࠬࠤࡂࡄࠠࡼࡿࠥ࠰ࠥࡢࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡨࡧࡷࡗࡪࡹࡳࡪࡱࡱࡈࡪࡺࡡࡪ࡮ࡶࠦࢂࡢࠧࠪࠫࠬ࡟ࠧ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠣ࡟ࠬࠤ࠰ࠦࠢ࠭࡞࡟ࡲࠧ࠯࡜࡯ࠢࠣࠤࠥࢃࡣࡢࡶࡦ࡬࠭࡫ࡸࠪࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡽ࡝ࡰࠣࠤ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠧࣀ")
bstack111l1ll11_opy_ = bstack1ll111_opy_ (u"ࠨ࡞ࡱ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࡢ࡮ࡤࡱࡱࡷࡹࠦࡢࡴࡶࡤࡧࡰࡥࡰࡢࡶ࡫ࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳࡞࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡦࡥࡵࡹࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠴ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡶ࡟ࡪࡰࡧࡩࡽࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠴ࡠࡠࡳࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡹ࡬ࡪࡥࡨࠬ࠵࠲ࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࠬࡠࡳࡩ࡯࡯ࡵࡷࠤ࡮ࡳࡰࡰࡴࡷࡣࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴ࠵ࡡࡥࡷࡹࡧࡣ࡬ࠢࡀࠤࡷ࡫ࡱࡶ࡫ࡵࡩ࠭ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ࠭ࡀࡢ࡮ࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻ࡝ࡰ࡯ࡩࡹࠦࡣࡢࡲࡶ࠿ࡡࡴࡴࡳࡻࠣࡿࡡࡴࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࡞ࡱࠤࠥࢃࠠࡤࡣࡷࡧ࡭࠮ࡥࡹࠫࠣࡿࡡࡴࠠࠡࠢࠣࢁࡡࡴࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽ࡟ࡲࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࡠࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠦࡾࡩࡳࡩ࡯ࡥࡧࡘࡖࡎࡉ࡯࡮ࡲࡲࡲࡪࡴࡴࠩࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡦࡥࡵࡹࠩࠪࡿࡣ࠰ࡡࡴࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࡢ࡮ࠡࠢࢀ࠭ࡡࡴࡽ࡝ࡰ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࡡࡴࠧࣁ")
from ._version import __version__
bstack1l11111111_opy_ = None
CONFIG = {}
bstack1l11l11111_opy_ = {}
bstack11ll1ll111_opy_ = {}
bstack1ll1lll1ll_opy_ = None
bstack11l1ll1lll_opy_ = None
bstack11l1l1111l_opy_ = None
bstack1ll111111_opy_ = -1
bstack1ll1l1ll11_opy_ = 0
bstack111llll11l_opy_ = bstack11111111_opy_
bstack1lll11llll_opy_ = 1
bstack1l1lll1l11_opy_ = False
bstack1ll111ll_opy_ = False
bstack1ll11lllll_opy_ = bstack1ll111_opy_ (u"ࠩࠪࣂ")
bstack1l1lllll_opy_ = bstack1ll111_opy_ (u"ࠪࠫࣃ")
bstack1l11l1111l_opy_ = False
bstack1l11l1ll11_opy_ = True
bstack1l1111l1_opy_ = bstack1ll111_opy_ (u"ࠫࠬࣄ")
bstack1ll111ll1l_opy_ = []
bstack1111l1ll1_opy_ = threading.Lock()
bstack11l1l1l1l1_opy_ = threading.Lock()
bstack1ll1l111l_opy_ = bstack1ll111_opy_ (u"ࠬ࠭ࣅ")
bstack1l1111llll_opy_ = False
bstack11111l11l_opy_ = None
bstack1ll111l1l1_opy_ = None
bstack1lll1l11_opy_ = None
bstack1111111ll_opy_ = -1
bstack1ll1l1lll_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"࠭ࡾࠨࣆ")), bstack1ll111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧࣇ"), bstack1ll111_opy_ (u"ࠨ࠰ࡵࡳࡧࡵࡴ࠮ࡴࡨࡴࡴࡸࡴ࠮ࡪࡨࡰࡵ࡫ࡲ࠯࡬ࡶࡳࡳ࠭ࣈ"))
bstack11lllll1_opy_ = 0
bstack1lllll1ll_opy_ = 0
bstack1l11ll111_opy_ = []
bstack1lll1l11l_opy_ = []
bstack1ll1l1ll_opy_ = []
bstack11llll1l_opy_ = []
bstack11l1lll1l_opy_ = bstack1ll111_opy_ (u"ࠩࠪࣉ")
bstack11ll111l_opy_ = bstack1ll111_opy_ (u"ࠪࠫ࣊")
bstack11ll11lll_opy_ = False
bstack1llll111ll_opy_ = False
bstack1l1111l111_opy_ = {}
bstack11llll1l1_opy_ = {}
bstack1lll111111_opy_ = None
bstack111llll111_opy_ = None
bstack11l11l1ll1_opy_ = None
bstack11ll1111l1_opy_ = None
bstack1l11lllll1_opy_ = None
bstack11ll1l1111_opy_ = None
bstack1llll1l1l_opy_ = None
bstack11ll11ll1l_opy_ = None
bstack1111lllll_opy_ = None
bstack11l1l1l1ll_opy_ = None
bstack1l11ll111l_opy_ = None
bstack11ll1l1ll1_opy_ = None
bstack1111l1l1l_opy_ = None
bstack1l11llllll_opy_ = None
bstack1lllll1ll1_opy_ = None
bstack11l111ll11_opy_ = None
bstack1lllllllll_opy_ = None
bstack1l1l111lll_opy_ = None
bstack111ll11l1_opy_ = None
bstack1lll111l_opy_ = None
bstack1lllllll1l_opy_ = None
bstack1lll11l1l1_opy_ = None
bstack11lll1lll1_opy_ = None
thread_local = threading.local()
bstack1l1l1111_opy_ = False
bstack1l1ll11l1_opy_ = bstack1ll111_opy_ (u"ࠦࠧ࣋")
logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack111llll11l_opy_)
bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
percy = bstack11lllll11_opy_()
bstack11111ll1l_opy_ = bstack1ll111l111_opy_()
bstack1l1lll1l1l_opy_ = bstack11ll1lllll_opy_()
def bstack111l11111_opy_():
  global CONFIG
  global bstack11ll11lll_opy_
  global bstack11ll11l11l_opy_
  testContextOptions = bstack1l11111l1_opy_(CONFIG)
  if bstack1ll1l1111_opy_(CONFIG):
    if (bstack1ll111_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ࣌") in testContextOptions and str(testContextOptions[bstack1ll111_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ࣍")]).lower() == bstack1ll111_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎")):
      bstack11ll11lll_opy_ = True
    bstack11ll11l11l_opy_.bstack11l1l111ll_opy_(testContextOptions.get(bstack1ll111_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷ࣏ࠬ"), False))
  else:
    bstack11ll11lll_opy_ = True
    bstack11ll11l11l_opy_.bstack11l1l111ll_opy_(True)
def bstack1ll1l1l1l1_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack111l111l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack11l111lll_opy_():
  global bstack11llll1l1_opy_
  args = sys.argv
  for i in range(len(args)):
    if bstack1ll111_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡦࡳࡳ࡬ࡩࡨࡨ࡬ࡰࡪࠨ࣐") == args[i].lower() or bstack1ll111_opy_ (u"ࠥ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡮ࡧ࡫ࡪ࣑ࠦ") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      bstack11llll1l1_opy_[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒")] = path
      return path
  return None
bstack1l1l111ll1_opy_ = re.compile(bstack1ll111_opy_ (u"ࡷࠨ࠮ࠫࡁ࡟ࠨࢀ࠮࠮ࠫࡁࠬࢁ࠳࠰࠿࣓ࠣ"))
def bstack1ll11l1111_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1l1l111ll1_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack1ll111_opy_ (u"ࠨࠤࡼࠤࣔ") + group + bstack1ll111_opy_ (u"ࠢࡾࠤࣕ"), os.environ.get(group))
  return value
def bstack1l111l1ll_opy_():
  global bstack11lll1lll1_opy_
  if bstack11lll1lll1_opy_ is None:
        bstack11lll1lll1_opy_ = bstack11l111lll_opy_()
  bstack1lll11ll1_opy_ = bstack11lll1lll1_opy_
  if bstack1lll11ll1_opy_ and os.path.exists(os.path.abspath(bstack1lll11ll1_opy_)):
    fileName = bstack1lll11ll1_opy_
  if bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࣖ") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࡠࡈࡌࡐࡊ࠭ࣗ")])) and not bstack1ll111_opy_ (u"ࠪࡪ࡮ࡲࡥࡏࡣࡰࡩࠬࣘ") in locals():
    fileName = os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨࣙ")]
  if bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡑࡥࡲ࡫ࠧࣚ") in locals():
    bstack1111lll_opy_ = os.path.abspath(fileName)
  else:
    bstack1111lll_opy_ = bstack1ll111_opy_ (u"࠭ࠧࣛ")
  bstack111l111l1_opy_ = os.getcwd()
  bstack1ll1l11lll_opy_ = bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪࣜ")
  bstack1l1111l11_opy_ = bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺࡣࡰࡰࠬࣝ")
  while (not os.path.exists(bstack1111lll_opy_)) and bstack111l111l1_opy_ != bstack1ll111_opy_ (u"ࠤࠥࣞ"):
    bstack1111lll_opy_ = os.path.join(bstack111l111l1_opy_, bstack1ll1l11lll_opy_)
    if not os.path.exists(bstack1111lll_opy_):
      bstack1111lll_opy_ = os.path.join(bstack111l111l1_opy_, bstack1l1111l11_opy_)
    if bstack111l111l1_opy_ != os.path.dirname(bstack111l111l1_opy_):
      bstack111l111l1_opy_ = os.path.dirname(bstack111l111l1_opy_)
    else:
      bstack111l111l1_opy_ = bstack1ll111_opy_ (u"ࠥࠦࣟ")
  bstack11lll1lll1_opy_ = bstack1111lll_opy_ if os.path.exists(bstack1111lll_opy_) else None
  return bstack11lll1lll1_opy_
def bstack1l1l11lll1_opy_(config):
    if bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡔࡨࡴࡴࡸࡴࡪࡰࡪࠫ࣠") in config:
      config[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡒࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ࣡")] = config[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡖࡪࡶ࡯ࡳࡶ࡬ࡲ࡬࠭࣢")]
    if bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡗ࡫ࡰࡰࡴࡷ࡭ࡳ࡭ࡏࡱࡶ࡬ࡳࡳࡹࣣࠧ") in config:
      config[bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬࣤ")] = config[bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࡒࡦࡲࡲࡶࡹ࡯࡮ࡨࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣥ")]
def bstack11llll1ll_opy_():
  bstack1111lll_opy_ = bstack1l111l1ll_opy_()
  if not os.path.exists(bstack1111lll_opy_):
    bstack1ll1lll1l1_opy_(
      bstack1l11lllll_opy_.format(os.getcwd()))
  try:
    with open(bstack1111lll_opy_, bstack1ll111_opy_ (u"ࠪࡶࣦࠬ")) as stream:
      yaml.add_implicit_resolver(bstack1ll111_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࣧ"), bstack1l1l111ll1_opy_)
      yaml.add_constructor(bstack1ll111_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࣨ"), bstack1ll11l1111_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      bstack1l1l11lll1_opy_(config)
      return config
  except:
    with open(bstack1111lll_opy_, bstack1ll111_opy_ (u"࠭ࡲࠨࣩ")) as stream:
      try:
        config = yaml.safe_load(stream)
        bstack1l1l11lll1_opy_(config)
        return config
      except yaml.YAMLError as exc:
        bstack1ll1lll1l1_opy_(bstack11l1lll1ll_opy_.format(str(exc)))
def bstack11l11lllll_opy_(config):
  bstack1l1llll11l_opy_ = bstack11l1llll1l_opy_(config)
  for option in list(bstack1l1llll11l_opy_):
    if option.lower() in bstack1l111ll1ll_opy_ and option != bstack1l111ll1ll_opy_[option.lower()]:
      bstack1l1llll11l_opy_[bstack1l111ll1ll_opy_[option.lower()]] = bstack1l1llll11l_opy_[option]
      del bstack1l1llll11l_opy_[option]
  return config
def bstack11l1ll11_opy_():
  global bstack11ll1ll111_opy_
  for key, bstack1l1ll1l11l_opy_ in bstack1ll1l1ll1l_opy_.items():
    if isinstance(bstack1l1ll1l11l_opy_, list):
      for var in bstack1l1ll1l11l_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11ll1ll111_opy_[key] = os.environ[var]
          break
    elif bstack1l1ll1l11l_opy_ in os.environ and os.environ[bstack1l1ll1l11l_opy_] and str(os.environ[bstack1l1ll1l11l_opy_]).strip():
      bstack11ll1ll111_opy_[key] = os.environ[bstack1l1ll1l11l_opy_]
  if bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ࣪") in os.environ:
    bstack11ll1ll111_opy_[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ࣫")] = {}
    bstack11ll1ll111_opy_[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭࣬")][bstack1ll111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ࣭ࠬ")] = os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࣮࠭")]
def bstack11ll1llll1_opy_():
  global bstack1l11l11111_opy_
  global bstack1l1111l1_opy_
  global bstack11llll1l1_opy_
  bstack1llll1l1_opy_ = []
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) - 1 and bstack1ll111_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ࣯").lower() == val.lower():
      bstack1l11l11111_opy_[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࣰࠪ")] = {}
      bstack1l11l11111_opy_[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࣱࠫ")][bstack1ll111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = sys.argv[idx + 1]
      bstack1llll1l1_opy_.extend([idx, idx + 1])
      break
  for key, bstack11l1l11l1l_opy_ in bstack1lll1lll1l_opy_.items():
    if isinstance(bstack11l1l11l1l_opy_, list):
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        for var in bstack11l1l11l1l_opy_:
          if bstack1ll111_opy_ (u"ࠩ࠰࠱ࠬࣳ") + var.lower() == val.lower() and key not in bstack1l11l11111_opy_:
            bstack1l11l11111_opy_[key] = sys.argv[idx + 1]
            bstack1l1111l1_opy_ += bstack1ll111_opy_ (u"ࠪࠤ࠲࠳ࠧࣴ") + var + bstack1ll111_opy_ (u"ࠫࠥ࠭ࣵ") + shlex.quote(sys.argv[idx + 1])
            bstack11ll1l11ll_opy_(bstack11llll1l1_opy_, key, sys.argv[idx + 1])
            bstack1llll1l1_opy_.extend([idx, idx + 1])
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx >= len(sys.argv) - 1:
          continue
        if bstack1ll111_opy_ (u"ࠬ࠳࠭ࠨࣶ") + bstack11l1l11l1l_opy_.lower() == val.lower() and key not in bstack1l11l11111_opy_:
          bstack1l11l11111_opy_[key] = sys.argv[idx + 1]
          bstack1l1111l1_opy_ += bstack1ll111_opy_ (u"࠭ࠠ࠮࠯ࠪࣷ") + bstack11l1l11l1l_opy_ + bstack1ll111_opy_ (u"ࠧࠡࠩࣸ") + shlex.quote(sys.argv[idx + 1])
          bstack11ll1l11ll_opy_(bstack11llll1l1_opy_, key, sys.argv[idx + 1])
          bstack1llll1l1_opy_.extend([idx, idx + 1])
  for idx in sorted(set(bstack1llll1l1_opy_), reverse=True):
    if idx < len(sys.argv):
      del sys.argv[idx]
def bstack111lll1ll1_opy_(config):
  bstack1l1l11l1_opy_ = config.keys()
  for bstack1l1111lll1_opy_, bstack1l11111ll_opy_ in bstack11l111l11l_opy_.items():
    if bstack1l11111ll_opy_ in bstack1l1l11l1_opy_:
      config[bstack1l1111lll1_opy_] = config[bstack1l11111ll_opy_]
      del config[bstack1l11111ll_opy_]
  for bstack1l1111lll1_opy_, bstack1l11111ll_opy_ in bstack11l1ll1l1_opy_.items():
    if isinstance(bstack1l11111ll_opy_, list):
      for bstack1ll1111l1_opy_ in bstack1l11111ll_opy_:
        if bstack1ll1111l1_opy_ in bstack1l1l11l1_opy_:
          config[bstack1l1111lll1_opy_] = config[bstack1ll1111l1_opy_]
          del config[bstack1ll1111l1_opy_]
          break
    elif bstack1l11111ll_opy_ in bstack1l1l11l1_opy_:
      config[bstack1l1111lll1_opy_] = config[bstack1l11111ll_opy_]
      del config[bstack1l11111ll_opy_]
  for bstack1ll1111l1_opy_ in list(config):
    for bstack1ll1l11ll1_opy_ in bstack1lll1l1lll_opy_:
      if bstack1ll1111l1_opy_.lower() == bstack1ll1l11ll1_opy_.lower() and bstack1ll1111l1_opy_ != bstack1ll1l11ll1_opy_:
        config[bstack1ll1l11ll1_opy_] = config[bstack1ll1111l1_opy_]
        del config[bstack1ll1111l1_opy_]
  bstack1l1ll111ll_opy_ = [{}]
  if not config.get(bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࣹࠫ")):
    config[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࣺࠬ")] = [{}]
  bstack1l1ll111ll_opy_ = config[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ࣻ")]
  for platform in bstack1l1ll111ll_opy_:
    for bstack1ll1111l1_opy_ in list(platform):
      for bstack1ll1l11ll1_opy_ in bstack1lll1l1lll_opy_:
        if bstack1ll1111l1_opy_.lower() == bstack1ll1l11ll1_opy_.lower() and bstack1ll1111l1_opy_ != bstack1ll1l11ll1_opy_:
          platform[bstack1ll1l11ll1_opy_] = platform[bstack1ll1111l1_opy_]
          del platform[bstack1ll1111l1_opy_]
  for bstack1l1111lll1_opy_, bstack1l11111ll_opy_ in bstack11l1ll1l1_opy_.items():
    for platform in bstack1l1ll111ll_opy_:
      if isinstance(bstack1l11111ll_opy_, list):
        for bstack1ll1111l1_opy_ in bstack1l11111ll_opy_:
          if bstack1ll1111l1_opy_ in platform:
            platform[bstack1l1111lll1_opy_] = platform[bstack1ll1111l1_opy_]
            del platform[bstack1ll1111l1_opy_]
            break
      elif bstack1l11111ll_opy_ in platform:
        platform[bstack1l1111lll1_opy_] = platform[bstack1l11111ll_opy_]
        del platform[bstack1l11111ll_opy_]
  for bstack1llllll11l_opy_ in bstack1ll11lll1_opy_:
    if bstack1llllll11l_opy_ in config:
      if not bstack1ll11lll1_opy_[bstack1llllll11l_opy_] in config:
        config[bstack1ll11lll1_opy_[bstack1llllll11l_opy_]] = {}
      config[bstack1ll11lll1_opy_[bstack1llllll11l_opy_]].update(config[bstack1llllll11l_opy_])
      del config[bstack1llllll11l_opy_]
  for platform in bstack1l1ll111ll_opy_:
    for bstack1llllll11l_opy_ in bstack1ll11lll1_opy_:
      if bstack1llllll11l_opy_ in list(platform):
        if not bstack1ll11lll1_opy_[bstack1llllll11l_opy_] in platform:
          platform[bstack1ll11lll1_opy_[bstack1llllll11l_opy_]] = {}
        platform[bstack1ll11lll1_opy_[bstack1llllll11l_opy_]].update(platform[bstack1llllll11l_opy_])
        del platform[bstack1llllll11l_opy_]
  config = bstack11l11lllll_opy_(config)
  return config
def bstack111ll1111_opy_(config):
  global bstack1l1lllll_opy_
  bstack1ll1llll1_opy_ = False
  if bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨࣼ") in config and str(config[bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩࣽ")]).lower() != bstack1ll111_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣾ"):
    if bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫࣿ") not in config or str(config[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬऀ")]).lower() == bstack1ll111_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨँ"):
      config[bstack1ll111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࠩं")] = False
    else:
      bstack1l11llll_opy_ = bstack1lllllll11_opy_()
      if bstack1ll111_opy_ (u"ࠫ࡮ࡹࡔࡳ࡫ࡤࡰࡌࡸࡩࡥࠩः") in bstack1l11llll_opy_:
        if not bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
          config[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
        config[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")][bstack1ll111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪइ")] = bstack1ll111_opy_ (u"ࠩࡤࡸࡸ࠳ࡲࡦࡲࡨࡥࡹ࡫ࡲࠨई")
        bstack1ll1llll1_opy_ = True
        bstack1l1lllll_opy_ = config[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")].get(bstack1ll111_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ऊ"))
  if bstack1ll1l1111_opy_(config) and bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩऋ") in config and str(config[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪऌ")]).lower() != bstack1ll111_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ऍ") and not bstack1ll1llll1_opy_:
    if not bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬऎ") in config:
      config[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")] = {}
    if not config[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧऐ")].get(bstack1ll111_opy_ (u"ࠫࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠨऑ")) and not bstack1ll111_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ") in config[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪओ")]:
      bstack11ll1l111_opy_ = datetime.datetime.now()
      bstack1llllllll1_opy_ = bstack11ll1l111_opy_.strftime(bstack1ll111_opy_ (u"ࠧࠦࡦࡢࠩࡧࡥࠥࡉࠧࡐࠫऔ"))
      hostname = socket.gethostname()
      bstack1lll1l1l11_opy_ = bstack1ll111_opy_ (u"ࠨࠩक").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1ll111_opy_ (u"ࠩࡾࢁࡤࢁࡽࡠࡽࢀࠫख").format(bstack1llllllll1_opy_, hostname, bstack1lll1l1l11_opy_)
      config[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧग")][bstack1ll111_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")] = identifier
    bstack1l1lllll_opy_ = config[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩङ")].get(bstack1ll111_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच"))
  return config
def bstack1lll11lll_opy_():
  bstack1l11llll11_opy_ =  bstack1l1lll11l1_opy_()[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷ࠭छ")]
  return bstack1l11llll11_opy_ if bstack1l11llll11_opy_ else -1
def bstack1l1111l11l_opy_(bstack1l11llll11_opy_):
  global CONFIG
  if not bstack1ll111_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪज") in CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ")]:
    return
  CONFIG[bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")] = CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")].replace(
    bstack1ll111_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧठ"),
    str(bstack1l11llll11_opy_)
  )
def bstack111lllll11_opy_():
  global CONFIG
  if not bstack1ll111_opy_ (u"࠭ࠤࡼࡆࡄࡘࡊࡥࡔࡊࡏࡈࢁࠬड") in CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩढ")]:
    return
  bstack11ll1l111_opy_ = datetime.datetime.now()
  bstack1llllllll1_opy_ = bstack11ll1l111_opy_.strftime(bstack1ll111_opy_ (u"ࠨࠧࡧ࠱ࠪࡨ࠭ࠦࡊ࠽ࠩࡒ࠭ण"))
  CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")] = CONFIG[bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬथ")].replace(
    bstack1ll111_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪद"),
    bstack1llllllll1_opy_
  )
def bstack11ll1l1l1_opy_():
  global CONFIG
  if bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧध") in CONFIG and not bool(CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]):
    del CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऩ")]
    return
  if not bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪप") in CONFIG:
    CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫफ")] = bstack1ll111_opy_ (u"ࠪࠧࠩࢁࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࢂ࠭ब")
  if bstack1ll111_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪभ") in CONFIG[bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]:
    bstack111lllll11_opy_()
    os.environ[bstack1ll111_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪय")] = CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩर")]
  if not bstack1ll111_opy_ (u"ࠨࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪऱ") in CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫल")]:
    return
  bstack1l11llll11_opy_ = bstack1ll111_opy_ (u"ࠪࠫळ")
  bstack111l11l11_opy_ = bstack1lll11lll_opy_()
  if bstack111l11l11_opy_ != -1:
    bstack1l11llll11_opy_ = bstack1ll111_opy_ (u"ࠫࡈࡏࠠࠨऴ") + str(bstack111l11l11_opy_)
  if bstack1l11llll11_opy_ == bstack1ll111_opy_ (u"ࠬ࠭व"):
    bstack11l11ll11l_opy_ = bstack11lll11l11_opy_(CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩश")])
    if bstack11l11ll11l_opy_ != -1:
      bstack1l11llll11_opy_ = str(bstack11l11ll11l_opy_)
  if bstack1l11llll11_opy_:
    bstack1l1111l11l_opy_(bstack1l11llll11_opy_)
    os.environ[bstack1ll111_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫष")] = CONFIG[bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪस")]
def bstack1l11lll11l_opy_(bstack1l1l1l11l1_opy_, bstack11llllll11_opy_, path):
  bstack1l1l111l_opy_ = {
    bstack1ll111_opy_ (u"ࠩ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ह"): bstack11llllll11_opy_
  }
  if os.path.exists(path):
    bstack11lll11ll_opy_ = json.load(open(path, bstack1ll111_opy_ (u"ࠪࡶࡧ࠭ऺ")))
  else:
    bstack11lll11ll_opy_ = {}
  bstack11lll11ll_opy_[bstack1l1l1l11l1_opy_] = bstack1l1l111l_opy_
  with open(path, bstack1ll111_opy_ (u"ࠦࡼ࠱ࠢऻ")) as outfile:
    json.dump(bstack11lll11ll_opy_, outfile)
def bstack11lll11l11_opy_(bstack1l1l1l11l1_opy_):
  bstack1l1l1l11l1_opy_ = str(bstack1l1l1l11l1_opy_)
  bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠬࢄ़ࠧ")), bstack1ll111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ऽ"))
  try:
    if not os.path.exists(bstack11lllll1l_opy_):
      os.makedirs(bstack11lllll1l_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩा")), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨि"), bstack1ll111_opy_ (u"ࠩ࠱ࡦࡺ࡯࡬ࡥ࠯ࡱࡥࡲ࡫࠭ࡤࡣࡦ࡬ࡪ࠴ࡪࡴࡱࡱࠫी"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1ll111_opy_ (u"ࠪࡻࠬु")):
        pass
      with open(file_path, bstack1ll111_opy_ (u"ࠦࡼ࠱ࠢू")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1ll111_opy_ (u"ࠬࡸࠧृ")) as bstack11111ll11_opy_:
      bstack111111111_opy_ = json.load(bstack11111ll11_opy_)
    if bstack1l1l1l11l1_opy_ in bstack111111111_opy_:
      bstack11lll1l1ll_opy_ = bstack111111111_opy_[bstack1l1l1l11l1_opy_][bstack1ll111_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪॄ")]
      bstack1ll1ll11l1_opy_ = int(bstack11lll1l1ll_opy_) + 1
      bstack1l11lll11l_opy_(bstack1l1l1l11l1_opy_, bstack1ll1ll11l1_opy_, file_path)
      return bstack1ll1ll11l1_opy_
    else:
      bstack1l11lll11l_opy_(bstack1l1l1l11l1_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1lll11l1_opy_.format(str(e)))
    return -1
def bstack1l1l11l1ll_opy_(config):
  if not config[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩॅ")] or not config[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫॆ")]:
    return True
  else:
    return False
def bstack1l11llll1l_opy_(config, index=0):
  global bstack1l11l1111l_opy_
  bstack11lll1l11l_opy_ = {}
  caps = bstack11l1llll_opy_ + bstack11ll11l11_opy_
  if config.get(bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭े"), False):
    bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧै")] = True
    bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࡐࡲࡷ࡭ࡴࡴࡳࠨॉ")] = config.get(bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩॊ"), {})
  if bstack1l11l1111l_opy_:
    caps += bstack1lll1111l_opy_
  for key in config:
    if key in caps + [bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩो")]:
      continue
    bstack11lll1l11l_opy_[key] = config[key]
  if bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ") in config:
    for bstack1lllll1l1l_opy_ in config[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ्ࠫ")][index]:
      if bstack1lllll1l1l_opy_ in caps:
        continue
      bstack11lll1l11l_opy_[bstack1lllll1l1l_opy_] = config[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॎ")][index][bstack1lllll1l1l_opy_]
  bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠪ࡬ࡴࡹࡴࡏࡣࡰࡩࠬॏ")] = socket.gethostname()
  if bstack1ll111_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬॐ") in bstack11lll1l11l_opy_:
    del (bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭॑")])
  return bstack11lll1l11l_opy_
def bstack1ll1ll1111_opy_(config):
  global bstack1l11l1111l_opy_
  bstack11l1ll1l11_opy_ = {}
  caps = bstack11ll11l11_opy_
  if bstack1l11l1111l_opy_:
    caps += bstack1lll1111l_opy_
  for key in caps:
    if key in config:
      bstack11l1ll1l11_opy_[key] = config[key]
  return bstack11l1ll1l11_opy_
def bstack1l1l1ll1l_opy_(bstack11lll1l11l_opy_, bstack11l1ll1l11_opy_):
  bstack1l1l1l111_opy_ = {}
  for key in bstack11lll1l11l_opy_.keys():
    if key in bstack11l111l11l_opy_:
      bstack1l1l1l111_opy_[bstack11l111l11l_opy_[key]] = bstack11lll1l11l_opy_[key]
    else:
      bstack1l1l1l111_opy_[key] = bstack11lll1l11l_opy_[key]
  for key in bstack11l1ll1l11_opy_:
    if key in bstack11l111l11l_opy_:
      bstack1l1l1l111_opy_[bstack11l111l11l_opy_[key]] = bstack11l1ll1l11_opy_[key]
    else:
      bstack1l1l1l111_opy_[key] = bstack11l1ll1l11_opy_[key]
  return bstack1l1l1l111_opy_
def bstack1l1l111ll_opy_(config, index=0):
  global bstack1l11l1111l_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1lll111ll_opy_ = bstack111llll11_opy_(bstack111l1111l_opy_, config, logger)
  bstack11l1ll1l11_opy_ = bstack1ll1ll1111_opy_(config)
  bstack1lll1l1l1_opy_ = bstack11ll11l11_opy_
  bstack1lll1l1l1_opy_ += bstack1lllll11l1_opy_
  bstack11l1ll1l11_opy_ = update(bstack11l1ll1l11_opy_, bstack1lll111ll_opy_)
  if bstack1l11l1111l_opy_:
    bstack1lll1l1l1_opy_ += bstack1lll1111l_opy_
  if bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴ॒ࠩ") in config:
    if bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ॓") in config[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
      caps[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧॕ")] = config[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॗ")]
    if bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭क़") in config[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index]:
      caps[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨग़")] = str(config[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫज़")][index][bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪड़")])
    bstack1llll11l1l_opy_ = bstack111llll11_opy_(bstack111l1111l_opy_, config[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ढ़")][index], logger)
    bstack1lll1l1l1_opy_ += list(bstack1llll11l1l_opy_.keys())
    for bstack111l11ll1_opy_ in bstack1lll1l1l1_opy_:
      if bstack111l11ll1_opy_ in config[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧफ़")][index]:
        if bstack111l11ll1_opy_ == bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧय़"):
          try:
            bstack1llll11l1l_opy_[bstack111l11ll1_opy_] = str(config[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॠ")][index][bstack111l11ll1_opy_] * 1.0)
          except:
            bstack1llll11l1l_opy_[bstack111l11ll1_opy_] = str(config[bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪॡ")][index][bstack111l11ll1_opy_])
        else:
          bstack1llll11l1l_opy_[bstack111l11ll1_opy_] = config[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫॢ")][index][bstack111l11ll1_opy_]
        del (config[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬॣ")][index][bstack111l11ll1_opy_])
    bstack11l1ll1l11_opy_ = update(bstack11l1ll1l11_opy_, bstack1llll11l1l_opy_)
  bstack11lll1l11l_opy_ = bstack1l11llll1l_opy_(config, index)
  for bstack1ll1111l1_opy_ in bstack11ll11l11_opy_ + list(bstack1lll111ll_opy_.keys()):
    if bstack1ll1111l1_opy_ in bstack11lll1l11l_opy_:
      bstack11l1ll1l11_opy_[bstack1ll1111l1_opy_] = bstack11lll1l11l_opy_[bstack1ll1111l1_opy_]
      del (bstack11lll1l11l_opy_[bstack1ll1111l1_opy_])
  if bstack11l1lll11l_opy_(config):
    bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ।")] = True
    caps.update(bstack11l1ll1l11_opy_)
    caps[bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ॥")] = bstack11lll1l11l_opy_
  else:
    bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬ०")] = False
    caps.update(bstack1l1l1ll1l_opy_(bstack11lll1l11l_opy_, bstack11l1ll1l11_opy_))
    if bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ१") in caps:
      caps[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ२")] = caps[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭३")]
      del (caps[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ४")])
    if bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ५") in caps:
      caps[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭६")] = caps[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭७")]
      del (caps[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ८")])
  return caps
def bstack111111lll_opy_():
  global bstack1ll1l111l_opy_
  global CONFIG
  if bstack111l111l_opy_() <= version.parse(bstack1ll111_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ९")):
    if bstack1ll1l111l_opy_ != bstack1ll111_opy_ (u"ࠨࠩ॰"):
      return bstack1ll111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥॱ") + bstack1ll1l111l_opy_ + bstack1ll111_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢॲ")
    return bstack1lll1ll111_opy_
  if bstack1ll1l111l_opy_ != bstack1ll111_opy_ (u"ࠫࠬॳ"):
    return bstack1ll111_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢॴ") + bstack1ll1l111l_opy_ + bstack1ll111_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨࠢॵ")
  return bstack1ll1ll1ll_opy_
def bstack11lll11l_opy_(options):
  return hasattr(options, bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠨॶ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack11l1111lll_opy_(options, bstack11l11l1l1l_opy_):
  for bstack1l1l1l111l_opy_ in bstack11l11l1l1l_opy_:
    if bstack1l1l1l111l_opy_ in [bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॷ"), bstack1ll111_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॸ")]:
      continue
    if bstack1l1l1l111l_opy_ in options._experimental_options:
      options._experimental_options[bstack1l1l1l111l_opy_] = update(options._experimental_options[bstack1l1l1l111l_opy_],
                                                         bstack11l11l1l1l_opy_[bstack1l1l1l111l_opy_])
    else:
      options.add_experimental_option(bstack1l1l1l111l_opy_, bstack11l11l1l1l_opy_[bstack1l1l1l111l_opy_])
  if bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack11l11l1l1l_opy_:
    for arg in bstack11l11l1l1l_opy_[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
    del (bstack11l11l1l1l_opy_[bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪॻ")])
  if bstack1ll111_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪॼ") in bstack11l11l1l1l_opy_:
    for ext in bstack11l11l1l1l_opy_[bstack1ll111_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫॽ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack11l11l1l1l_opy_[bstack1ll111_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬॾ")])
def bstack1ll1l111ll_opy_(options, bstack1l1lllllll_opy_):
  if bstack1ll111_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॿ") in bstack1l1lllllll_opy_:
    for bstack1l111111_opy_ in bstack1l1lllllll_opy_[bstack1ll111_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩঀ")]:
      if bstack1l111111_opy_ in options._preferences:
        options._preferences[bstack1l111111_opy_] = update(options._preferences[bstack1l111111_opy_], bstack1l1lllllll_opy_[bstack1ll111_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪঁ")][bstack1l111111_opy_])
      else:
        options.set_preference(bstack1l111111_opy_, bstack1l1lllllll_opy_[bstack1ll111_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫং")][bstack1l111111_opy_])
  if bstack1ll111_opy_ (u"࠭ࡡࡳࡩࡶࠫঃ") in bstack1l1lllllll_opy_:
    for arg in bstack1l1lllllll_opy_[bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      options.add_argument(arg)
def bstack1l11l111l_opy_(options, bstack11111l1ll_opy_):
  if bstack1ll111_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࠩঅ") in bstack11111l1ll_opy_:
    options.use_webview(bool(bstack11111l1ll_opy_[bstack1ll111_opy_ (u"ࠩࡺࡩࡧࡼࡩࡦࡹࠪআ")]))
  bstack11l1111lll_opy_(options, bstack11111l1ll_opy_)
def bstack11l1l1ll11_opy_(options, bstack11ll11111_opy_):
  for bstack1ll11l1l11_opy_ in bstack11ll11111_opy_:
    if bstack1ll11l1l11_opy_ in [bstack1ll111_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧই"), bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ")]:
      continue
    options.set_capability(bstack1ll11l1l11_opy_, bstack11ll11111_opy_[bstack1ll11l1l11_opy_])
  if bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪউ") in bstack11ll11111_opy_:
    for arg in bstack11ll11111_opy_[bstack1ll111_opy_ (u"࠭ࡡࡳࡩࡶࠫঊ")]:
      options.add_argument(arg)
  if bstack1ll111_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫঋ") in bstack11ll11111_opy_:
    options.bstack1l1lll1ll1_opy_(bool(bstack11ll11111_opy_[bstack1ll111_opy_ (u"ࠨࡶࡨࡧ࡭ࡴ࡯࡭ࡱࡪࡽࡕࡸࡥࡷ࡫ࡨࡻࠬঌ")]))
def bstack111l1lll1_opy_(options, bstack111l1ll1_opy_):
  for bstack1l11l11ll1_opy_ in bstack111l1ll1_opy_:
    if bstack1l11l11ll1_opy_ in [bstack1ll111_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭঍"), bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ঎")]:
      continue
    options._options[bstack1l11l11ll1_opy_] = bstack111l1ll1_opy_[bstack1l11l11ll1_opy_]
  if bstack1ll111_opy_ (u"ࠫࡦࡪࡤࡪࡶ࡬ࡳࡳࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨএ") in bstack111l1ll1_opy_:
    for bstack1lllll1lll_opy_ in bstack111l1ll1_opy_[bstack1ll111_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঐ")]:
      options.bstack11l1l1llll_opy_(
        bstack1lllll1lll_opy_, bstack111l1ll1_opy_[bstack1ll111_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ঑")][bstack1lllll1lll_opy_])
  if bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡷࠬ঒") in bstack111l1ll1_opy_:
    for arg in bstack111l1ll1_opy_[bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ও")]:
      options.add_argument(arg)
def bstack11l11l1l_opy_(options, caps):
  if not hasattr(options, bstack1ll111_opy_ (u"ࠩࡎࡉ࡞࠭ঔ")):
    return
  if options.KEY == bstack1ll111_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨক"):
    options = bstack1llll111_opy_.bstack111lll11l_opy_(bstack1l11111l11_opy_=options, config=CONFIG)
  if options.KEY == bstack1ll111_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩখ") and options.KEY in caps:
    bstack11l1111lll_opy_(options, caps[bstack1ll111_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪগ")])
  elif options.KEY == bstack1ll111_opy_ (u"࠭࡭ࡰࡼ࠽ࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫঘ") and options.KEY in caps:
    bstack1ll1l111ll_opy_(options, caps[bstack1ll111_opy_ (u"ࠧ࡮ࡱࡽ࠾࡫࡯ࡲࡦࡨࡲࡼࡔࡶࡴࡪࡱࡱࡷࠬঙ")])
  elif options.KEY == bstack1ll111_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩচ") and options.KEY in caps:
    bstack11l1l1ll11_opy_(options, caps[bstack1ll111_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪছ")])
  elif options.KEY == bstack1ll111_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫজ") and options.KEY in caps:
    bstack1l11l111l_opy_(options, caps[bstack1ll111_opy_ (u"ࠫࡲࡹ࠺ࡦࡦࡪࡩࡔࡶࡴࡪࡱࡱࡷࠬঝ")])
  elif options.KEY == bstack1ll111_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫঞ") and options.KEY in caps:
    bstack111l1lll1_opy_(options, caps[bstack1ll111_opy_ (u"࠭ࡳࡦ࠼࡬ࡩࡔࡶࡴࡪࡱࡱࡷࠬট")])
def bstack1ll1l111l1_opy_(caps):
  global bstack1l11l1111l_opy_
  if isinstance(os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨঠ")), str):
    bstack1l11l1111l_opy_ = eval(os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩড")))
  if bstack1l11l1111l_opy_:
    if bstack1ll1l1l1l1_opy_() < version.parse(bstack1ll111_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨঢ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1ll111_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ")
    if bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩত") in caps:
      browser = caps[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪথ")]
    elif bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧদ") in caps:
      browser = caps[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨধ")]
    browser = str(browser).lower()
    if browser == bstack1ll111_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨন") or browser == bstack1ll111_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ঩"):
      browser = bstack1ll111_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪপ")
    if browser == bstack1ll111_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬফ"):
      browser = bstack1ll111_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬব")
    if browser not in [bstack1ll111_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ভ"), bstack1ll111_opy_ (u"ࠧࡦࡦࡪࡩࠬম"), bstack1ll111_opy_ (u"ࠨ࡫ࡨࠫয"), bstack1ll111_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩর"), bstack1ll111_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ঱")]:
      return None
    try:
      package = bstack1ll111_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ল").format(browser)
      name = bstack1ll111_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭঳")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack11lll11l_opy_(options):
        return None
      for bstack1ll1111l1_opy_ in caps.keys():
        options.set_capability(bstack1ll1111l1_opy_, caps[bstack1ll1111l1_opy_])
      bstack11l11l1l_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1llll1ll11_opy_(options, bstack1l1l1llll_opy_):
  if not bstack11lll11l_opy_(options):
    return
  for bstack1ll1111l1_opy_ in bstack1l1l1llll_opy_.keys():
    if bstack1ll1111l1_opy_ in bstack1lllll11l1_opy_:
      continue
    if bstack1ll1111l1_opy_ in options._caps and type(options._caps[bstack1ll1111l1_opy_]) in [dict, list]:
      options._caps[bstack1ll1111l1_opy_] = update(options._caps[bstack1ll1111l1_opy_], bstack1l1l1llll_opy_[bstack1ll1111l1_opy_])
    else:
      options.set_capability(bstack1ll1111l1_opy_, bstack1l1l1llll_opy_[bstack1ll1111l1_opy_])
  bstack11l11l1l_opy_(options, bstack1l1l1llll_opy_)
  if bstack1ll111_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬ঴") in options._caps:
    if options._caps[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ঵")] and options._caps[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭শ")].lower() != bstack1ll111_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪষ"):
      del options._caps[bstack1ll111_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩস")]
def bstack11l11lll11_opy_(proxy_config):
  if bstack1ll111_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨহ") in proxy_config:
    proxy_config[bstack1ll111_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧ঺")] = proxy_config[bstack1ll111_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঻")]
    del (proxy_config[bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼ়ࠫ")])
  if bstack1ll111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫঽ") in proxy_config and proxy_config[bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬা")].lower() != bstack1ll111_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪি"):
    proxy_config[bstack1ll111_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧী")] = bstack1ll111_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬু")
  if bstack1ll111_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫূ") in proxy_config:
    proxy_config[bstack1ll111_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪৃ")] = bstack1ll111_opy_ (u"ࠨࡲࡤࡧࠬৄ")
  return proxy_config
def bstack1l11111ll1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ৅") in config:
    return proxy
  config[bstack1ll111_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ৆")] = bstack11l11lll11_opy_(config[bstack1ll111_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪে")])
  if proxy == None:
    proxy = Proxy(config[bstack1ll111_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫৈ")])
  return proxy
def bstack1l111lll11_opy_(self):
  global CONFIG
  global bstack11ll1l1ll1_opy_
  try:
    proxy = bstack1ll1ll111l_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1ll111_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")):
        proxies = bstack1l11ll1ll1_opy_(proxy, bstack111111lll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l111l1ll_opy_ = proxies.popitem()
          if bstack1ll111_opy_ (u"ࠢ࠻࠱࠲ࠦ৊") in bstack11l111l1ll_opy_:
            return bstack11l111l1ll_opy_
          else:
            return bstack1ll111_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤো") + bstack11l111l1ll_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨৌ").format(str(e)))
  return bstack11ll1l1ll1_opy_(self)
def bstack11ll1ll11l_opy_():
  global CONFIG
  return bstack1l1l11lll_opy_(CONFIG) and bstack1ll1l1l1ll_opy_() and bstack111l111l_opy_() >= version.parse(bstack11l11l11ll_opy_)
def bstack1l1111l1ll_opy_():
  global CONFIG
  return (bstack1ll111_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ্࠭") in CONFIG or bstack1ll111_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨৎ") in CONFIG) and bstack1ll1l11l1_opy_()
def bstack11l1llll1l_opy_(config):
  bstack1l1llll11l_opy_ = {}
  if bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৏") in config:
    bstack1l1llll11l_opy_ = config[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৐")]
  if bstack1ll111_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৑") in config:
    bstack1l1llll11l_opy_ = config[bstack1ll111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৒")]
  proxy = bstack1ll1ll111l_opy_(config)
  if proxy:
    if proxy.endswith(bstack1ll111_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ৓")) and os.path.isfile(proxy):
      bstack1l1llll11l_opy_[bstack1ll111_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭৔")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1ll111_opy_ (u"ࠫ࠳ࡶࡡࡤࠩ৕")):
        proxies = bstack1l1l1ll11l_opy_(config, bstack111111lll_opy_())
        if len(proxies) > 0:
          protocol, bstack11l111l1ll_opy_ = proxies.popitem()
          if bstack1ll111_opy_ (u"ࠧࡀ࠯࠰ࠤ৖") in bstack11l111l1ll_opy_:
            parsed_url = urlparse(bstack11l111l1ll_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1ll111_opy_ (u"ࠨ࠺࠰࠱ࠥৗ") + bstack11l111l1ll_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l1llll11l_opy_[bstack1ll111_opy_ (u"ࠧࡱࡴࡲࡼࡾࡎ࡯ࡴࡶࠪ৘")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l1llll11l_opy_[bstack1ll111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡰࡴࡷࠫ৙")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l1llll11l_opy_[bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ৚")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l1llll11l_opy_[bstack1ll111_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡤࡷࡸ࠭৛")] = str(parsed_url.password)
  return bstack1l1llll11l_opy_
def bstack1l11111l1_opy_(config):
  if bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴࠩড়") in config:
    return config[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪঢ়")]
  return {}
def bstack11ll1l1l1l_opy_(caps):
  global bstack1l1lllll_opy_
  if bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ৞") in caps:
    caps[bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨয়")][bstack1ll111_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧৠ")] = True
    if bstack1l1lllll_opy_:
      caps[bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪৡ")][bstack1ll111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬৢ")] = bstack1l1lllll_opy_
  else:
    caps[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩৣ")] = True
    if bstack1l1lllll_opy_:
      caps[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৤")] = bstack1l1lllll_opy_
@measure(event_name=EVENTS.bstack1ll1l1l111_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1ll1l1l1_opy_():
  global CONFIG
  if not bstack1ll1l1111_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ৥") in CONFIG and bstack1l1l1111l1_opy_(CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ০")]):
    if (
      bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ১") in CONFIG
      and bstack1l1l1111l1_opy_(CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭২")].get(bstack1ll111_opy_ (u"ࠪࡷࡰ࡯ࡰࡃ࡫ࡱࡥࡷࡿࡉ࡯࡫ࡷ࡭ࡦࡲࡩࡴࡣࡷ࡭ࡴࡴࠧ৩")))
    ):
      logger.debug(bstack1ll111_opy_ (u"ࠦࡑࡵࡣࡢ࡮ࠣࡦ࡮ࡴࡡࡳࡻࠣࡲࡴࡺࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡣࡶࠤࡸࡱࡩࡱࡄ࡬ࡲࡦࡸࡹࡊࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࡪࡴࡡࡣ࡮ࡨࡨࠧ৪"))
      return
    bstack1l1llll11l_opy_ = bstack11l1llll1l_opy_(CONFIG)
    bstack1111ll111_opy_(CONFIG[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ৫")], bstack1l1llll11l_opy_)
def bstack1111ll111_opy_(key, bstack1l1llll11l_opy_):
  global bstack1l11111111_opy_
  logger.info(bstack1l111111l1_opy_)
  try:
    bstack1l11111111_opy_ = Local()
    bstack1l1l11ll1l_opy_ = {bstack1ll111_opy_ (u"࠭࡫ࡦࡻࠪ৬"): key}
    bstack1l1l11ll1l_opy_.update(bstack1l1llll11l_opy_)
    logger.debug(bstack1111lll11_opy_.format(str(bstack1l1l11ll1l_opy_)).replace(key, bstack1ll111_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ৭")))
    bstack1l11111111_opy_.start(**bstack1l1l11ll1l_opy_)
    if bstack1l11111111_opy_.isRunning():
      logger.info(bstack11llll11_opy_)
  except Exception as e:
    bstack1ll1lll1l1_opy_(bstack11l1l1ll_opy_.format(str(e)))
def bstack11l1111l1l_opy_():
  global bstack1l11111111_opy_
  if bstack1l11111111_opy_.isRunning():
    logger.info(bstack11lll111ll_opy_)
    bstack1l11111111_opy_.stop()
  bstack1l11111111_opy_ = None
def bstack11l1llllll_opy_(bstack11lll1ll11_opy_=[]):
  global CONFIG
  bstack111lll1ll_opy_ = []
  bstack1l11l1ll1_opy_ = [bstack1ll111_opy_ (u"ࠨࡱࡶࠫ৮"), bstack1ll111_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ৯"), bstack1ll111_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧৰ"), bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ৱ"), bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ৲"), bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ৳")]
  try:
    for err in bstack11lll1ll11_opy_:
      bstack11111l11_opy_ = {}
      for k in bstack1l11l1ll1_opy_:
        val = CONFIG[bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ৴")][int(err[bstack1ll111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ৵")])].get(k)
        if val:
          bstack11111l11_opy_[k] = val
      if(err[bstack1ll111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ৶")] != bstack1ll111_opy_ (u"ࠪࠫ৷")):
        bstack11111l11_opy_[bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡵࠪ৸")] = {
          err[bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ৹")]: err[bstack1ll111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৺")]
        }
        bstack111lll1ll_opy_.append(bstack11111l11_opy_)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡳࡷࡳࡡࡵࡶ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࠺ࠡࠩ৻") + str(e))
  finally:
    return bstack111lll1ll_opy_
def bstack1l111l11l_opy_(file_name):
  bstack1111ll11l_opy_ = []
  try:
    bstack1ll11l1l1_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack1ll11l1l1_opy_):
      with open(bstack1ll11l1l1_opy_) as f:
        bstack1l1ll1ll1l_opy_ = json.load(f)
        bstack1111ll11l_opy_ = bstack1l1ll1ll1l_opy_
      os.remove(bstack1ll11l1l1_opy_)
    return bstack1111ll11l_opy_
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪ࡮ࡴࡤࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣࡰ࡮ࡹࡴ࠻ࠢࠪৼ") + str(e))
    return bstack1111ll11l_opy_
def bstack1111l1111_opy_():
  try:
      from bstack_utils.constants import bstack1l1l1ll11_opy_, EVENTS
      from bstack_utils.helper import bstack1l1l111111_opy_, get_host_info, bstack11ll11l11l_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack11ll111l11_opy_ = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠩ࡯ࡳ࡬࠭৽"), bstack1ll111_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭৾"))
      lock = FileLock(bstack11ll111l11_opy_+bstack1ll111_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ৿"))
      def bstack1lll111l11_opy_():
          try:
              with lock:
                  with open(bstack11ll111l11_opy_, bstack1ll111_opy_ (u"ࠧࡸࠢ਀"), encoding=bstack1ll111_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧਁ")) as file:
                      data = json.load(file)
                      config = {
                          bstack1ll111_opy_ (u"ࠢࡩࡧࡤࡨࡪࡸࡳࠣਂ"): {
                              bstack1ll111_opy_ (u"ࠣࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠢਃ"): bstack1ll111_opy_ (u"ࠤࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠧ਄"),
                          }
                      }
                      bstack11l111111l_opy_ = datetime.utcnow()
                      bstack11ll1l111_opy_ = bstack11l111111l_opy_.strftime(bstack1ll111_opy_ (u"ࠥࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙ࠪ࠮ࠦࡨ࡙࡙ࠣࡉࠢਅ"))
                      bstack1l1lllll11_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩਆ")) if os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪਇ")) else bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"))
                      payload = {
                          bstack1ll111_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠦਉ"): bstack1ll111_opy_ (u"ࠣࡵࡧ࡯ࡤ࡫ࡶࡦࡰࡷࡷࠧਊ"),
                          bstack1ll111_opy_ (u"ࠤࡧࡥࡹࡧࠢ਋"): {
                              bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡺࡻࡩࡥࠤ਌"): bstack1l1lllll11_opy_,
                              bstack1ll111_opy_ (u"ࠦࡨࡸࡥࡢࡶࡨࡨࡤࡪࡡࡺࠤ਍"): bstack11ll1l111_opy_,
                              bstack1ll111_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࠤ਎"): bstack1ll111_opy_ (u"ࠨࡓࡅࡍࡉࡩࡦࡺࡵࡳࡧࡓࡩࡷ࡬࡯ࡳ࡯ࡤࡲࡨ࡫ࠢਏ"),
                              bstack1ll111_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡪࡴࡱࡱࠦਐ"): {
                                  bstack1ll111_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࡵࠥ਑"): data,
                                  bstack1ll111_opy_ (u"ࠤࡶࡨࡰࡘࡵ࡯ࡋࡧࠦ਒"): bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧਓ"))
                              },
                              bstack1ll111_opy_ (u"ࠦࡺࡹࡥࡳࡡࡧࡥࡹࡧࠢਔ"): bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਕ")),
                              bstack1ll111_opy_ (u"ࠨࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠤਖ"): get_host_info()
                          }
                      }
                      bstack1l1lll1111_opy_ = bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠢࡢࡲ࡬ࡷࠧਗ"), bstack1ll111_opy_ (u"ࠣࡧࡧࡷࡎࡴࡳࡵࡴࡸࡱࡪࡴࡴࡢࡶ࡬ࡳࡳࠨਘ"), bstack1ll111_opy_ (u"ࠤࡤࡴ࡮ࠨਙ")], bstack1l1l1ll11_opy_)
                      response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠥࡔࡔ࡙ࡔࠣਚ"), bstack1l1lll1111_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack1ll111_opy_ (u"ࠦࡉࡧࡴࡢࠢࡶࡩࡳࡺࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡴࡰࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦਛ").format(bstack1l1l1ll11_opy_, payload))
                      else:
                          logger.debug(bstack1ll111_opy_ (u"ࠧࡘࡥࡲࡷࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡦࡰࡴࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧਜ").format(bstack1l1l1ll11_opy_, payload))
          except Exception as e:
              logger.debug(bstack1ll111_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡳࡪࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷࠥࡪࡡࡵࡣࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠࡼࡿࠥਝ").format(e))
      bstack1lll111l11_opy_()
      bstack11lll1l1_opy_(bstack11ll111l11_opy_, logger)
  except:
    pass
def bstack11l1111ll_opy_():
  global bstack1l1ll11l1_opy_
  global bstack1ll111ll1l_opy_
  global bstack1l11ll111_opy_
  global bstack1lll1l11l_opy_
  global bstack1ll1l1ll_opy_
  global bstack11ll111l_opy_
  global CONFIG
  bstack11l11ll1_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਞ"))
  if bstack11l11ll1_opy_ in [bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਟ"), bstack1ll111_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨਠ")]:
    bstack1ll1l1llll_opy_()
  percy.shutdown()
  if bstack1l1ll11l1_opy_:
    logger.warning(bstack11ll1l1l11_opy_.format(str(bstack1l1ll11l1_opy_)))
  else:
    try:
      bstack11lll11ll_opy_ = bstack1111ll1l_opy_(bstack1ll111_opy_ (u"ࠪ࠲ࡧࡹࡴࡢࡥ࡮࠱ࡨࡵ࡮ࡧ࡫ࡪ࠲࡯ࡹ࡯࡯ࠩਡ"), logger)
      if bstack11lll11ll_opy_.get(bstack1ll111_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਢ")) and bstack11lll11ll_opy_.get(bstack1ll111_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਣ")).get(bstack1ll111_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨਤ")):
        logger.warning(bstack11ll1l1l11_opy_.format(str(bstack11lll11ll_opy_[bstack1ll111_opy_ (u"ࠧ࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࠬਥ")][bstack1ll111_opy_ (u"ࠨࡪࡲࡷࡹࡴࡡ࡮ࡧࠪਦ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.bstack11ll11ll_opy_)
  logger.info(bstack1l11l1ll_opy_)
  global bstack1l11111111_opy_
  if bstack1l11111111_opy_:
    bstack11l1111l1l_opy_()
  try:
    with bstack1111l1ll1_opy_:
      bstack11l11llll_opy_ = bstack1ll111ll1l_opy_.copy()
    for driver in bstack11l11llll_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack11l1lll1l1_opy_)
  if bstack11ll111l_opy_ == bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨਧ"):
    bstack1ll1l1ll_opy_ = bstack1l111l11l_opy_(bstack1ll111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਨ"))
  if bstack11ll111l_opy_ == bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ਩") and len(bstack1lll1l11l_opy_) == 0:
    bstack1lll1l11l_opy_ = bstack1l111l11l_opy_(bstack1ll111_opy_ (u"ࠬࡶࡷࡠࡲࡼࡸࡪࡹࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਪ"))
    if len(bstack1lll1l11l_opy_) == 0:
      bstack1lll1l11l_opy_ = bstack1l111l11l_opy_(bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਫ"))
  bstack1111l1l1_opy_ = bstack1ll111_opy_ (u"ࠧࠨਬ")
  if len(bstack1l11ll111_opy_) > 0:
    bstack1111l1l1_opy_ = bstack11l1llllll_opy_(bstack1l11ll111_opy_)
  elif len(bstack1lll1l11l_opy_) > 0:
    bstack1111l1l1_opy_ = bstack11l1llllll_opy_(bstack1lll1l11l_opy_)
  elif len(bstack1ll1l1ll_opy_) > 0:
    bstack1111l1l1_opy_ = bstack11l1llllll_opy_(bstack1ll1l1ll_opy_)
  elif len(bstack11llll1l_opy_) > 0:
    bstack1111l1l1_opy_ = bstack11l1llllll_opy_(bstack11llll1l_opy_)
  if bool(bstack1111l1l1_opy_):
    bstack1ll1ll11ll_opy_(bstack1111l1l1_opy_)
  else:
    bstack1ll1ll11ll_opy_()
  bstack11lll1l1_opy_(bstack1l1ll1111l_opy_, logger)
  if bstack11l11ll1_opy_ not in [bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩਭ")]:
    bstack1111l1111_opy_()
  bstack1llll1ll1l_opy_.bstack11l1l1l111_opy_(CONFIG)
  if len(bstack1ll1l1ll_opy_) > 0:
    sys.exit(len(bstack1ll1l1ll_opy_))
def bstack11lll11ll1_opy_(bstack1ll1ll1ll1_opy_, frame):
  global bstack11ll11l11l_opy_
  logger.error(bstack1ll1111l1l_opy_)
  bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬਮ"), bstack1ll1ll1ll1_opy_)
  if hasattr(signal, bstack1ll111_opy_ (u"ࠪࡗ࡮࡭࡮ࡢ࡮ࡶࠫਯ")):
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਰ"), signal.Signals(bstack1ll1ll1ll1_opy_).name)
  else:
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ਱"), bstack1ll111_opy_ (u"࠭ࡓࡊࡉࡘࡒࡐࡔࡏࡘࡐࠪਲ"))
  if cli.is_running():
    bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.bstack11ll11ll_opy_)
  bstack11l11ll1_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠧࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࡢ࡙ࡘࡋࡄࠨਲ਼"))
  if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ਴") and not cli.is_enabled(CONFIG):
    bstack111l1l111_opy_.stop(bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩਵ")))
  bstack11l1111ll_opy_()
  sys.exit(1)
def bstack1ll1lll1l1_opy_(err):
  logger.critical(bstack1l1111ll1_opy_.format(str(err)))
  bstack1ll1ll11ll_opy_(bstack1l1111ll1_opy_.format(str(err)), True)
  atexit.unregister(bstack11l1111ll_opy_)
  bstack1ll1l1llll_opy_()
  sys.exit(1)
def bstack111111ll1_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1ll1ll11ll_opy_(message, True)
  atexit.unregister(bstack11l1111ll_opy_)
  bstack1ll1l1llll_opy_()
  sys.exit(1)
def bstack11ll11llll_opy_():
  global CONFIG
  global bstack1l11l11111_opy_
  global bstack11ll1ll111_opy_
  global bstack1l11l1ll11_opy_
  CONFIG = bstack11llll1ll_opy_()
  load_dotenv(CONFIG.get(bstack1ll111_opy_ (u"ࠪࡩࡳࡼࡆࡪ࡮ࡨࠫਸ਼")))
  bstack11l1ll11_opy_()
  bstack11ll1llll1_opy_()
  CONFIG = bstack111lll1ll1_opy_(CONFIG)
  update(CONFIG, bstack11ll1ll111_opy_)
  update(CONFIG, bstack1l11l11111_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack111ll1111_opy_(CONFIG)
  bstack1l11l1ll11_opy_ = bstack1ll1l1111_opy_(CONFIG)
  os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧ਷")] = bstack1l11l1ll11_opy_.__str__().lower()
  bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ਸ"), bstack1l11l1ll11_opy_)
  if (bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਹ") in CONFIG and bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ਺") in bstack1l11l11111_opy_) or (
          bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ਻") in CONFIG and bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ਼ࠬ") not in bstack11ll1ll111_opy_):
    if os.getenv(bstack1ll111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ਽")):
      CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ਾ")] = os.getenv(bstack1ll111_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩਿ"))
    else:
      if not CONFIG.get(bstack1ll111_opy_ (u"ࠨࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠤੀ"), bstack1ll111_opy_ (u"ࠢࠣੁ")) in bstack1lll1l11ll_opy_:
        bstack11ll1l1l1_opy_()
  elif (bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫੂ") not in CONFIG and bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ੃") in CONFIG) or (
          bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭੄") in bstack11ll1ll111_opy_ and bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ੅") not in bstack1l11l11111_opy_):
    del (CONFIG[bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ੆")])
  if bstack1l1l11l1ll_opy_(CONFIG):
    bstack1ll1lll1l1_opy_(bstack11l111l1l_opy_)
  Config.bstack1l11l1l1l_opy_().bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠨࡵࡴࡧࡵࡒࡦࡳࡥࠣੇ"), CONFIG[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩੈ")])
  bstack1ll1llllll_opy_()
  bstack11l1111111_opy_()
  if bstack1l11l1111l_opy_ and not CONFIG.get(bstack1ll111_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦ੉"), bstack1ll111_opy_ (u"ࠤࠥ੊")) in bstack1lll1l11ll_opy_:
    CONFIG[bstack1ll111_opy_ (u"ࠪࡥࡵࡶࠧੋ")] = bstack1l1lll11l_opy_(CONFIG)
    logger.info(bstack1ll1l11l1l_opy_.format(CONFIG[bstack1ll111_opy_ (u"ࠫࡦࡶࡰࠨੌ")]))
  if not bstack1l11l1ll11_opy_:
    CONFIG[bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ੍")] = [{}]
def bstack1l1l1111l_opy_(config, bstack11l111l1_opy_):
  global CONFIG
  global bstack1l11l1111l_opy_
  CONFIG = config
  bstack1l11l1111l_opy_ = bstack11l111l1_opy_
def bstack11l1111111_opy_():
  global CONFIG
  global bstack1l11l1111l_opy_
  if bstack1ll111_opy_ (u"࠭ࡡࡱࡲࠪ੎") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack111111ll1_opy_(e, bstack1l111111ll_opy_)
    bstack1l11l1111l_opy_ = True
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭੏"), True)
def bstack1l1lll11l_opy_(config):
  bstack11lll1l111_opy_ = bstack1ll111_opy_ (u"ࠨࠩ੐")
  app = config[bstack1ll111_opy_ (u"ࠩࡤࡴࡵ࠭ੑ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack11ll111l1l_opy_:
      if os.path.exists(app):
        bstack11lll1l111_opy_ = bstack11l111l1l1_opy_(config, app)
      elif bstack1ll1l1111l_opy_(app):
        bstack11lll1l111_opy_ = app
      else:
        bstack1ll1lll1l1_opy_(bstack1111111l1_opy_.format(app))
    else:
      if bstack1ll1l1111l_opy_(app):
        bstack11lll1l111_opy_ = app
      elif os.path.exists(app):
        bstack11lll1l111_opy_ = bstack11l111l1l1_opy_(app)
      else:
        bstack1ll1lll1l1_opy_(bstack1llll1llll_opy_)
  else:
    if len(app) > 2:
      bstack1ll1lll1l1_opy_(bstack1l11llll1_opy_)
    elif len(app) == 2:
      if bstack1ll111_opy_ (u"ࠪࡴࡦࡺࡨࠨ੒") in app and bstack1ll111_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡣ࡮ࡪࠧ੓") in app:
        if os.path.exists(app[bstack1ll111_opy_ (u"ࠬࡶࡡࡵࡪࠪ੔")]):
          bstack11lll1l111_opy_ = bstack11l111l1l1_opy_(config, app[bstack1ll111_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ੕")], app[bstack1ll111_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ੖")])
        else:
          bstack1ll1lll1l1_opy_(bstack1111111l1_opy_.format(app))
      else:
        bstack1ll1lll1l1_opy_(bstack1l11llll1_opy_)
    else:
      for key in app:
        if key in bstack1l11lll111_opy_:
          if key == bstack1ll111_opy_ (u"ࠨࡲࡤࡸ࡭࠭੗"):
            if os.path.exists(app[key]):
              bstack11lll1l111_opy_ = bstack11l111l1l1_opy_(config, app[key])
            else:
              bstack1ll1lll1l1_opy_(bstack1111111l1_opy_.format(app))
          else:
            bstack11lll1l111_opy_ = app[key]
        else:
          bstack1ll1lll1l1_opy_(bstack1l111ll1l_opy_)
  return bstack11lll1l111_opy_
def bstack1ll1l1111l_opy_(bstack11lll1l111_opy_):
  import re
  bstack1l1111ll11_opy_ = re.compile(bstack1ll111_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪࠥࠤ੘"))
  bstack11ll1l1l_opy_ = re.compile(bstack1ll111_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫ࠱࡞ࡥ࠲ࢀࡁ࠮࡜࠳࠱࠾ࡢ࡟࠯࡞࠰ࡡ࠯ࠪࠢਖ਼"))
  if bstack1ll111_opy_ (u"ࠫࡧࡹ࠺࠰࠱ࠪਗ਼") in bstack11lll1l111_opy_ or re.fullmatch(bstack1l1111ll11_opy_, bstack11lll1l111_opy_) or re.fullmatch(bstack11ll1l1l_opy_, bstack11lll1l111_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1l1l1111ll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11l111l1l1_opy_(config, path, bstack1l111l1ll1_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1ll111_opy_ (u"ࠬࡸࡢࠨਜ਼")).read()).hexdigest()
  bstack11l1llll1_opy_ = bstack1lllll1l11_opy_(md5_hash)
  bstack11lll1l111_opy_ = None
  if bstack11l1llll1_opy_:
    logger.info(bstack1lll1ll1ll_opy_.format(bstack11l1llll1_opy_, md5_hash))
    return bstack11l1llll1_opy_
  bstack111ll1ll1_opy_ = datetime.datetime.now()
  bstack11l111llll_opy_ = MultipartEncoder(
    fields={
      bstack1ll111_opy_ (u"࠭ࡦࡪ࡮ࡨࠫੜ"): (os.path.basename(path), open(os.path.abspath(path), bstack1ll111_opy_ (u"ࠧࡳࡤࠪ੝")), bstack1ll111_opy_ (u"ࠨࡶࡨࡼࡹ࠵ࡰ࡭ࡣ࡬ࡲࠬਫ਼")),
      bstack1ll111_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡡ࡬ࡨࠬ੟"): bstack1l111l1ll1_opy_
    }
  )
  response = requests.post(bstack1ll1ll1l1l_opy_, data=bstack11l111llll_opy_,
                           headers={bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ੠"): bstack11l111llll_opy_.content_type},
                           auth=(config[bstack1ll111_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭੡")], config[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ੢")]))
  try:
    res = json.loads(response.text)
    bstack11lll1l111_opy_ = res[bstack1ll111_opy_ (u"࠭ࡡࡱࡲࡢࡹࡷࡲࠧ੣")]
    logger.info(bstack11l1ll11ll_opy_.format(bstack11lll1l111_opy_))
    bstack1l1ll1llll_opy_(md5_hash, bstack11lll1l111_opy_)
    cli.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠢࡩࡶࡷࡴ࠿ࡻࡰ࡭ࡱࡤࡨࡤࡧࡰࡱࠤ੤"), datetime.datetime.now() - bstack111ll1ll1_opy_)
  except ValueError as err:
    bstack1ll1lll1l1_opy_(bstack1lll11lll1_opy_.format(str(err)))
  return bstack11lll1l111_opy_
def bstack1ll1llllll_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack1lll11llll_opy_
  bstack11lll111_opy_ = 1
  bstack1llllll1l_opy_ = 1
  if bstack1ll111_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੥") in CONFIG:
    bstack1llllll1l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੦")]
  else:
    bstack1llllll1l_opy_ = bstack1l1ll111l1_opy_(framework_name, args) or 1
  if bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭੧") in CONFIG:
    bstack11lll111_opy_ = len(CONFIG[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੨")])
  bstack1lll11llll_opy_ = int(bstack1llllll1l_opy_) * int(bstack11lll111_opy_)
def bstack1l1ll111l1_opy_(framework_name, args):
  if framework_name == bstack1llll11111_opy_ and args and bstack1ll111_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ੩") in args:
      bstack11llllll1l_opy_ = args.index(bstack1ll111_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫ੪"))
      return int(args[bstack11llllll1l_opy_ + 1]) or 1
  return 1
def bstack1lllll1l11_opy_(md5_hash):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠢࡱࡳࡹࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡥࡥࡸ࡯ࡣࠡࡨ࡬ࡰࡪࠦ࡯ࡱࡧࡵࡥࡹ࡯࡯࡯ࡵࠪ੫"))
    bstack1ll111llll_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠨࢀࠪ੬")), bstack1ll111_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੭"), bstack1ll111_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੮"))
    if os.path.exists(bstack1ll111llll_opy_):
      try:
        bstack111llllll_opy_ = json.load(open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠫࡷࡨࠧ੯")))
        if md5_hash in bstack111llllll_opy_:
          bstack1ll1ll1l1_opy_ = bstack111llllll_opy_[md5_hash]
          bstack11ll1l1lll_opy_ = datetime.datetime.now()
          bstack1l11l111_opy_ = datetime.datetime.strptime(bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨੰ")], bstack1ll111_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪੱ"))
          if (bstack11ll1l1lll_opy_ - bstack1l11l111_opy_).days > 30:
            return None
          elif version.parse(str(__version__)) > version.parse(bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬੲ")]):
            return None
          return bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠨ࡫ࡧࠫੳ")]
      except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡴࡨࡥࡩ࡯࡮ࡨࠢࡐࡈ࠺ࠦࡨࡢࡵ࡫ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂ࠭ੴ").format(str(e)))
    return None
  bstack1ll111llll_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠪࢂࠬੵ")), bstack1ll111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ੶"), bstack1ll111_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭੷"))
  lock_file = bstack1ll111llll_opy_ + bstack1ll111_opy_ (u"࠭࠮࡭ࡱࡦ࡯ࠬ੸")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack1ll111llll_opy_):
        with open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠧࡳࠩ੹")) as f:
          content = f.read().strip()
          if content:
            bstack111llllll_opy_ = json.loads(content)
            if md5_hash in bstack111llllll_opy_:
              bstack1ll1ll1l1_opy_ = bstack111llllll_opy_[md5_hash]
              bstack11ll1l1lll_opy_ = datetime.datetime.now()
              bstack1l11l111_opy_ = datetime.datetime.strptime(bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੺")], bstack1ll111_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੻"))
              if (bstack11ll1l1lll_opy_ - bstack1l11l111_opy_).days > 30:
                return None
              elif version.parse(str(__version__)) > version.parse(bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੼")]):
                return None
              return bstack1ll1ll1l1_opy_[bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧ੽")]
      return None
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧࠡࡨࡲࡶࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮࠺ࠡࡽࢀࠫ੾").format(str(e)))
    return None
def bstack1l1ll1llll_opy_(md5_hash, bstack11lll1l111_opy_):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1ll111_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩ੿"))
    bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩ઀")), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨઁ"))
    if not os.path.exists(bstack11lllll1l_opy_):
      os.makedirs(bstack11lllll1l_opy_)
    bstack1ll111llll_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠩࢁࠫં")), bstack1ll111_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪઃ"), bstack1ll111_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ઄"))
    bstack11l1111l_opy_ = {
      bstack1ll111_opy_ (u"ࠬ࡯ࡤࠨઅ"): bstack11lll1l111_opy_,
      bstack1ll111_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩઆ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1ll111_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫઇ")),
      bstack1ll111_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ઈ"): str(__version__)
    }
    try:
      bstack111llllll_opy_ = {}
      if os.path.exists(bstack1ll111llll_opy_):
        bstack111llllll_opy_ = json.load(open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠩࡵࡦࠬઉ")))
      bstack111llllll_opy_[md5_hash] = bstack11l1111l_opy_
      with open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠥࡻ࠰ࠨઊ")) as outfile:
        json.dump(bstack111llllll_opy_, outfile)
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡪࡡࡵ࡫ࡱ࡫ࠥࡓࡄ࠶ࠢ࡫ࡥࡸ࡮ࠠࡧ࡫࡯ࡩ࠿ࠦࡻࡾࠩઋ").format(str(e)))
    return
  bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠬࢄࠧઌ")), bstack1ll111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ઍ"))
  if not os.path.exists(bstack11lllll1l_opy_):
    os.makedirs(bstack11lllll1l_opy_)
  bstack1ll111llll_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩ઎")), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨએ"), bstack1ll111_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪઐ"))
  lock_file = bstack1ll111llll_opy_ + bstack1ll111_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩઑ")
  bstack11l1111l_opy_ = {
    bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧ઒"): bstack11lll1l111_opy_,
    bstack1ll111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨઓ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1ll111_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪઔ")),
    bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬક"): str(__version__)
  }
  try:
    with FileLock(lock_file, timeout=10):
      bstack111llllll_opy_ = {}
      if os.path.exists(bstack1ll111llll_opy_):
        with open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠨࡴࠪખ")) as f:
          content = f.read().strip()
          if content:
            bstack111llllll_opy_ = json.loads(content)
      bstack111llllll_opy_[md5_hash] = bstack11l1111l_opy_
      with open(bstack1ll111llll_opy_, bstack1ll111_opy_ (u"ࠤࡺࠦગ")) as outfile:
        json.dump(bstack111llllll_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡭ࡹ࡮ࠠࡧ࡫࡯ࡩࠥࡲ࡯ࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡑࡉ࠻ࠠࡩࡣࡶ࡬ࠥࡻࡰࡥࡣࡷࡩ࠿ࠦࡻࡾࠩઘ").format(str(e)))
def bstack11l1111ll1_opy_(self):
  return
def bstack1lll1lll1_opy_(self):
  return
def bstack11l11l111_opy_():
  global bstack1lll1l11_opy_
  bstack1lll1l11_opy_ = True
@measure(event_name=EVENTS.bstack1l1l11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11lllll11l_opy_(self):
  global bstack1ll11lllll_opy_
  global bstack1ll1lll1ll_opy_
  global bstack111llll111_opy_
  try:
    if bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫઙ") in bstack1ll11lllll_opy_ and self.session_id != None and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩચ"), bstack1ll111_opy_ (u"࠭ࠧછ")) != bstack1ll111_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨજ"):
      bstack1lll1ll1l_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨઝ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩઞ")
      if bstack1lll1ll1l_opy_ == bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪટ"):
        bstack1ll1111lll_opy_(logger)
      if self != None:
        bstack11ll1ll11_opy_(self, bstack1lll1ll1l_opy_, bstack1ll111_opy_ (u"ࠫ࠱ࠦࠧઠ").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack1ll111_opy_ (u"ࠬ࠭ડ")
    if bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઢ") in bstack1ll11lllll_opy_ and getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None):
      bstack1lll1111ll_opy_.bstack11lllllll_opy_(self, bstack1l1111l111_opy_, logger, wait=True)
    if bstack1ll111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨત") in bstack1ll11lllll_opy_:
      if not threading.currentThread().behave_test_status:
        bstack11ll1ll11_opy_(self, bstack1ll111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤથ"))
      bstack11ll11ll11_opy_.bstack1l1lllll1l_opy_(self)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦદ") + str(e))
  bstack111llll111_opy_(self)
  self.session_id = None
def bstack11ll1ll1l1_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1l1l1ll1ll_opy_
    global bstack1ll11lllll_opy_
    command_executor = kwargs.get(bstack1ll111_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧધ"), bstack1ll111_opy_ (u"ࠬ࠭ન"))
    bstack111l1l11_opy_ = False
    if type(command_executor) == str and bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ઩") in command_executor:
      bstack111l1l11_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪપ") in str(getattr(command_executor, bstack1ll111_opy_ (u"ࠨࡡࡸࡶࡱ࠭ફ"), bstack1ll111_opy_ (u"ࠩࠪબ"))):
      bstack111l1l11_opy_ = True
    else:
      kwargs = bstack1llll111_opy_.bstack111lll11l_opy_(bstack1l11111l11_opy_=kwargs, config=CONFIG)
      return bstack1lll111111_opy_(self, *args, **kwargs)
    if bstack111l1l11_opy_:
      bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(CONFIG, bstack1ll11lllll_opy_)
      if kwargs.get(bstack1ll111_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫભ")):
        kwargs[bstack1ll111_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬમ")] = bstack1l1l1ll1ll_opy_(kwargs[bstack1ll111_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭ય")], bstack1ll11lllll_opy_, CONFIG, bstack1l11l111ll_opy_)
      elif kwargs.get(bstack1ll111_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ર")):
        kwargs[bstack1ll111_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ઱")] = bstack1l1l1ll1ll_opy_(kwargs[bstack1ll111_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨલ")], bstack1ll11lllll_opy_, CONFIG, bstack1l11l111ll_opy_)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤળ").format(str(e)))
  return bstack1lll111111_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack1l111lll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll11l1ll1_opy_(self, command_executor=bstack1ll111_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦ઴"), *args, **kwargs):
  global bstack1ll1lll1ll_opy_
  global bstack1ll111ll1l_opy_
  bstack1ll1l1l1_opy_ = bstack11ll1ll1l1_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack1llll1111_opy_.on():
    return bstack1ll1l1l1_opy_
  try:
    logger.debug(bstack1ll111_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨવ").format(str(command_executor)))
    logger.debug(bstack1ll111_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧશ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩષ") in command_executor._url:
      bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨસ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫહ") in command_executor):
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ઺"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack11llllll_opy_ = getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫ઻"), None)
  bstack11ll111l1_opy_ = {}
  if self.capabilities is not None:
    bstack11ll111l1_opy_[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧ઼ࠪ")] = self.capabilities.get(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪઽ"))
    bstack11ll111l1_opy_[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨા")] = self.capabilities.get(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨિ"))
    bstack11ll111l1_opy_[bstack1ll111_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩી")] = self.capabilities.get(bstack1ll111_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧુ"))
  if CONFIG.get(bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૂ"), False) and bstack1llll111_opy_.bstack1ll11l11l1_opy_(bstack11ll111l1_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack1ll111_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack1ll11lllll_opy_ or bstack1ll111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack1ll11lllll_opy_:
    bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
  if bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ૅ") in bstack1ll11lllll_opy_ and bstack11llllll_opy_ and bstack11llllll_opy_.get(bstack1ll111_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ૆"), bstack1ll111_opy_ (u"ࠨࠩે")) == bstack1ll111_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪૈ"):
    bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
  bstack1ll1lll1ll_opy_ = self.session_id
  with bstack1111l1ll1_opy_:
    bstack1ll111ll1l_opy_.append(self)
  return bstack1ll1l1l1_opy_
def bstack1l1llll11_opy_(args):
  return bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫૉ") in str(args)
def bstack1ll111lll1_opy_(self, driver_command, *args, **kwargs):
  global bstack1lll111l_opy_
  global bstack1l1l1111_opy_
  bstack1l1111l1l1_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨ૊"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫો"), None)
  bstack11l1l111_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡩࡴࡃࡳࡴࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭ૌ"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡢࡲࡳࡅ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮્ࠩ"), None)
  bstack1l11111l1l_opy_ = getattr(self, bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ૎"), None) != None and getattr(self, bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ૏"), None) == True
  if not bstack1l1l1111_opy_ and bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪૐ") in CONFIG and CONFIG[bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ૑")] == True and bstack111llll1ll_opy_.bstack11l1l1lll1_opy_(driver_command) and (bstack1l11111l1l_opy_ or bstack1l1111l1l1_opy_ or bstack11l1l111_opy_) and not bstack1l1llll11_opy_(args):
    try:
      bstack1l1l1111_opy_ = True
      logger.debug(bstack1ll111_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡧࡱࡵࠤࢀࢃࠧ૒").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack1ll111_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡩࡷ࡬࡯ࡳ࡯ࠣࡷࡨࡧ࡮ࠡࡽࢀࠫ૓").format(str(err)))
    bstack1l1l1111_opy_ = False
  response = bstack1lll111l_opy_(self, driver_command, *args, **kwargs)
  if (bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭૔") in str(bstack1ll11lllll_opy_).lower() or bstack1ll111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ૕") in str(bstack1ll11lllll_opy_).lower()) and bstack1llll1111_opy_.on():
    try:
      if driver_command == bstack1ll111_opy_ (u"ࠩࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭૖"):
        bstack111l1l111_opy_.bstack1lll1lllll_opy_({
            bstack1ll111_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩ૗"): response[bstack1ll111_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪ૘")],
            bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ૙"): bstack111l1l111_opy_.current_test_uuid() if bstack111l1l111_opy_.current_test_uuid() else bstack1llll1111_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack11lll1l1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1l1l1l1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1ll1lll1ll_opy_
  global bstack1ll111111_opy_
  global bstack11l1l1111l_opy_
  global bstack1l1lll1l11_opy_
  global bstack1ll111ll_opy_
  global bstack1ll11lllll_opy_
  global bstack1lll111111_opy_
  global bstack1ll111ll1l_opy_
  global bstack1111111ll_opy_
  global bstack1l1111l111_opy_
  if os.getenv(bstack1ll111_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ૚")) is not None and bstack1llll111_opy_.bstack11llll11l_opy_(CONFIG) is None:
    CONFIG[bstack1ll111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ૛")] = True
  CONFIG[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ૜")] = str(bstack1ll11lllll_opy_) + str(__version__)
  bstack1llll1l1l1_opy_ = os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ૝")]
  bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(CONFIG, bstack1ll11lllll_opy_)
  CONFIG[bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭૞")] = bstack1llll1l1l1_opy_
  CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭૟")] = bstack1l11l111ll_opy_
  if CONFIG.get(bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬૠ"),bstack1ll111_opy_ (u"࠭ࠧૡ")) and bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ૢ") in bstack1ll11lllll_opy_:
    CONFIG[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨૣ")].pop(bstack1ll111_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ૤"), None)
    CONFIG[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ૥")].pop(bstack1ll111_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ૦"), None)
  command_executor = bstack111111lll_opy_()
  logger.debug(bstack1lll11l11l_opy_.format(command_executor))
  proxy = bstack1l11111ll1_opy_(CONFIG, proxy)
  bstack1lll1l1l_opy_ = 0 if bstack1ll111111_opy_ < 0 else bstack1ll111111_opy_
  try:
    if bstack1l1lll1l11_opy_ is True:
      bstack1lll1l1l_opy_ = int(multiprocessing.current_process().name)
    elif bstack1ll111ll_opy_ is True:
      bstack1lll1l1l_opy_ = int(threading.current_thread().name)
  except:
    bstack1lll1l1l_opy_ = 0
  bstack1l1l1llll_opy_ = bstack1l1l111ll_opy_(CONFIG, bstack1lll1l1l_opy_)
  logger.debug(bstack1l11l11l_opy_.format(str(bstack1l1l1llll_opy_)))
  if bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ૧") in CONFIG and bstack1l1l1111l1_opy_(CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ૨")]):
    bstack11ll1l1l1l_opy_(bstack1l1l1llll_opy_)
  if bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1lll1l1l_opy_) and bstack1llll111_opy_.bstack1ll1l11111_opy_(bstack1l1l1llll_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack1llll111_opy_.set_capabilities(bstack1l1l1llll_opy_, CONFIG)
  if desired_capabilities:
    bstack1111llll1_opy_ = bstack111lll1ll1_opy_(desired_capabilities)
    bstack1111llll1_opy_[bstack1ll111_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ૩")] = bstack11l1lll11l_opy_(CONFIG)
    bstack1ll111lll_opy_ = bstack1l1l111ll_opy_(bstack1111llll1_opy_)
    if bstack1ll111lll_opy_:
      bstack1l1l1llll_opy_ = update(bstack1ll111lll_opy_, bstack1l1l1llll_opy_)
    desired_capabilities = None
  if options:
    bstack1llll1ll11_opy_(options, bstack1l1l1llll_opy_)
  if not options:
    options = bstack1ll1l111l1_opy_(bstack1l1l1llll_opy_)
  bstack1l1111l111_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૪"))[bstack1lll1l1l_opy_]
  if proxy and bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૫")):
    options.proxy(proxy)
  if options and bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૬")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack111l111l_opy_() < version.parse(bstack1ll111_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪ૭")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack1l1l1llll_opy_)
  logger.info(bstack11111l1l_opy_)
  bstack1ll1lll11_opy_.end(EVENTS.bstack11l11ll1l_opy_.value, EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ૮"), EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ૯"), status=True, failure=None, test_name=bstack11l1l1111l_opy_)
  if bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡲࡵࡳ࡫࡯࡬ࡦࠩ૰") in kwargs:
    del kwargs[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡳࡶࡴ࡬ࡩ࡭ࡧࠪ૱")]
  try:
    if bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ૲")):
      bstack1lll111111_opy_(self, command_executor=command_executor,
                options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
    elif bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ૳")):
      bstack1lll111111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities, options=options,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    elif bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠫ࠷࠴࠵࠴࠰࠳ࠫ૴")):
      bstack1lll111111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive, file_detector=file_detector)
    else:
      bstack1lll111111_opy_(self, command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile, proxy=proxy,
                keep_alive=keep_alive)
  except Exception as bstack11lll1111l_opy_:
    logger.error(bstack1l1l1lll_opy_.format(bstack1ll111_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠫ૵"), str(bstack11lll1111l_opy_)))
    raise bstack11lll1111l_opy_
  if bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1lll1l1l_opy_) and bstack1llll111_opy_.bstack1ll1l11111_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨ૶")][bstack1ll111_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭૷")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack1llll111_opy_.set_capabilities(bstack1l1l1llll_opy_, CONFIG)
  try:
    bstack1lll11l11_opy_ = bstack1ll111_opy_ (u"ࠨࠩ૸")
    if bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠩ࠷࠲࠵࠴࠰ࡣ࠳ࠪૹ")):
      if self.caps is not None:
        bstack1lll11l11_opy_ = self.caps.get(bstack1ll111_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥૺ"))
    else:
      if self.capabilities is not None:
        bstack1lll11l11_opy_ = self.capabilities.get(bstack1ll111_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦૻ"))
    if bstack1lll11l11_opy_:
      bstack1lll11l1l_opy_(bstack1lll11l11_opy_)
      if bstack111l111l_opy_() <= version.parse(bstack1ll111_opy_ (u"ࠬ࠹࠮࠲࠵࠱࠴ࠬૼ")):
        self.command_executor._url = bstack1ll111_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ૽") + bstack1ll1l111l_opy_ + bstack1ll111_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦ૾")
      else:
        self.command_executor._url = bstack1ll111_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ૿") + bstack1lll11l11_opy_ + bstack1ll111_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ଀")
      logger.debug(bstack11l111l11_opy_.format(bstack1lll11l11_opy_))
    else:
      logger.debug(bstack11llll1l11_opy_.format(bstack1ll111_opy_ (u"ࠥࡓࡵࡺࡩ࡮ࡣ࡯ࠤࡍࡻࡢࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦଁ")))
  except Exception as e:
    logger.debug(bstack11llll1l11_opy_.format(e))
  if bstack1ll111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪଂ") in bstack1ll11lllll_opy_:
    bstack11l1ll11l_opy_(bstack1ll111111_opy_, bstack1111111ll_opy_)
  bstack1ll1lll1ll_opy_ = self.session_id
  if bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬଃ") in bstack1ll11lllll_opy_ or bstack1ll111_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭଄") in bstack1ll11lllll_opy_ or bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ଅ") in bstack1ll11lllll_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack11llllll_opy_ = getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩଆ"), None)
  if bstack1ll111_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩଇ") in bstack1ll11lllll_opy_ or bstack1ll111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩଈ") in bstack1ll11lllll_opy_:
    bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
  if bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫଉ") in bstack1ll11lllll_opy_ and bstack11llllll_opy_ and bstack11llllll_opy_.get(bstack1ll111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬଊ"), bstack1ll111_opy_ (u"࠭ࠧଋ")) == bstack1ll111_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨଌ"):
    bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
  with bstack1111l1ll1_opy_:
    bstack1ll111ll1l_opy_.append(self)
  if bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଍") in CONFIG and bstack1ll111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ଎") in CONFIG[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଏ")][bstack1lll1l1l_opy_]:
    bstack11l1l1111l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଐ")][bstack1lll1l1l_opy_][bstack1ll111_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଑")]
  logger.debug(bstack1llll11l_opy_.format(bstack1ll1lll1ll_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack1l1l11l1l1_opy_
    def bstack1l11ll1111_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l1111llll_opy_
      if(bstack1ll111_opy_ (u"ࠨࡩ࡯ࡦࡨࡼ࠳ࡰࡳࠣ଒") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩଓ")), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨଔ"), bstack1ll111_opy_ (u"ࠩ࠱ࡷࡪࡹࡳࡪࡱࡱ࡭ࡩࡹ࠮ࡵࡺࡷࠫକ")), bstack1ll111_opy_ (u"ࠪࡻࠬଖ")) as fp:
          fp.write(bstack1ll111_opy_ (u"ࠦࠧଗ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1ll111_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଘ")))):
          with open(args[1], bstack1ll111_opy_ (u"࠭ࡲࠨଙ")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1ll111_opy_ (u"ࠧࡢࡵࡼࡲࡨࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡡࡱࡩࡼࡖࡡࡨࡧࠫࡧࡴࡴࡴࡦࡺࡷ࠰ࠥࡶࡡࡨࡧࠣࡁࠥࡼ࡯ࡪࡦࠣ࠴࠮࠭ଚ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack11l1l1l1l_opy_)
            if bstack1ll111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬଛ") in CONFIG and str(CONFIG[bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ଜ")]).lower() != bstack1ll111_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩଝ"):
                bstack11l1ll11l1_opy_ = bstack1l1l11l1l1_opy_()
                bstack111l1ll11_opy_ = bstack1ll111_opy_ (u"ࠫࠬ࠭ࠊ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠍࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶ࡡࡀࠐࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠷࡝࠼ࠌࡦࡳࡳࡹࡴࠡࡲࡢ࡭ࡳࡪࡥࡹࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠷ࡣ࠻ࠋࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯ࡵ࡯࡭ࡨ࡫ࠨ࠱࠮ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸࠯࠻ࠋࡥࡲࡲࡸࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯ࠥࡃࠠࡳࡧࡴࡹ࡮ࡸࡥࠩࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨࠩ࠼ࠌ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰࡯ࡥࡺࡴࡣࡩࠢࡀࠤࡦࡹࡹ࡯ࡥࠣࠬࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶ࠭ࠥࡃ࠾ࠡࡽࡾࠎࠥࠦ࡬ࡦࡶࠣࡧࡦࡶࡳ࠼ࠌࠣࠤࡹࡸࡹࠡࡽࡾࠎࠥࠦࠠࠡࡥࡤࡴࡸࠦ࠽ࠡࡌࡖࡓࡓ࠴ࡰࡢࡴࡶࡩ࠭ࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠬ࠿ࠏࠦࠠࡾࡿࠣࡧࡦࡺࡣࡩࠢࠫࡩࡽ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࡤࡱࡱࡷࡴࡲࡥ࠯ࡧࡵࡶࡴࡸࠨࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠼ࠥ࠰ࠥ࡫ࡸࠪ࠽ࠍࠤࠥࢃࡽࠋࠢࠣࡶࡪࡺࡵࡳࡰࠣࡥࡼࡧࡩࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱ࠮ࡤࡪࡵࡳࡲ࡯ࡵ࡮࠰ࡦࡳࡳࡴࡥࡤࡶࠫࡿࢀࠐࠠࠡࠢࠣࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺ࠺ࠡࠩࡾࡧࡩࡶࡕࡳ࡮ࢀࠫࠥ࠱ࠠࡦࡰࡦࡳࡩ࡫ࡕࡓࡋࡆࡳࡲࡶ࡯࡯ࡧࡱࡸ࠭ࡐࡓࡐࡐ࠱ࡷࡹࡸࡩ࡯ࡩ࡬ࡪࡾ࠮ࡣࡢࡲࡶ࠭࠮࠲ࠊࠡࠢࠣࠤ࠳࠴࠮࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠊࠡࠢࢀࢁ࠮ࡁࠊࡾࡿ࠾ࠎ࠴࠰ࠠ࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࠤ࠯࠵ࠊࠨࠩࠪଞ").format(bstack11l1ll11l1_opy_=bstack11l1ll11l1_opy_)
            lines.insert(1, bstack111l1ll11_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1ll111_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢଟ")), bstack1ll111_opy_ (u"࠭ࡷࠨଠ")) as bstack111l1l1ll_opy_:
              bstack111l1l1ll_opy_.writelines(lines)
        CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩଡ")] = str(bstack1ll11lllll_opy_) + str(__version__)
        bstack1llll1l1l1_opy_ = os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ଢ")]
        bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(CONFIG, bstack1ll11lllll_opy_)
        CONFIG[bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬଣ")] = bstack1llll1l1l1_opy_
        CONFIG[bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬତ")] = bstack1l11l111ll_opy_
        bstack1lll1l1l_opy_ = 0 if bstack1ll111111_opy_ < 0 else bstack1ll111111_opy_
        try:
          if bstack1l1lll1l11_opy_ is True:
            bstack1lll1l1l_opy_ = int(multiprocessing.current_process().name)
          elif bstack1ll111ll_opy_ is True:
            bstack1lll1l1l_opy_ = int(threading.current_thread().name)
        except:
          bstack1lll1l1l_opy_ = 0
        CONFIG[bstack1ll111_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦଥ")] = False
        CONFIG[bstack1ll111_opy_ (u"ࠧ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦଦ")] = True
        bstack1l1l1llll_opy_ = bstack1l1l111ll_opy_(CONFIG, bstack1lll1l1l_opy_)
        logger.debug(bstack1l11l11l_opy_.format(str(bstack1l1l1llll_opy_)))
        if CONFIG.get(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪଧ")):
          bstack11ll1l1l1l_opy_(bstack1l1l1llll_opy_)
        if bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪନ") in CONFIG and bstack1ll111_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭଩") in CONFIG[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬପ")][bstack1lll1l1l_opy_]:
          bstack11l1l1111l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][bstack1lll1l1l_opy_][bstack1ll111_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩବ")]
        args.append(os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠬࢄࠧଭ")), bstack1ll111_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ମ"), bstack1ll111_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩଯ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack1l1l1llll_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1ll111_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥର"))
      bstack1l1111llll_opy_ = True
      return bstack1lllll1ll1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack11l1l11lll_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1ll111111_opy_
    global bstack11l1l1111l_opy_
    global bstack1l1lll1l11_opy_
    global bstack1ll111ll_opy_
    global bstack1ll11lllll_opy_
    CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ଱")] = str(bstack1ll11lllll_opy_) + str(__version__)
    bstack1llll1l1l1_opy_ = os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨଲ")]
    bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(CONFIG, bstack1ll11lllll_opy_)
    CONFIG[bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧଳ")] = bstack1llll1l1l1_opy_
    CONFIG[bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧ଴")] = bstack1l11l111ll_opy_
    bstack1lll1l1l_opy_ = 0 if bstack1ll111111_opy_ < 0 else bstack1ll111111_opy_
    try:
      if bstack1l1lll1l11_opy_ is True:
        bstack1lll1l1l_opy_ = int(multiprocessing.current_process().name)
      elif bstack1ll111ll_opy_ is True:
        bstack1lll1l1l_opy_ = int(threading.current_thread().name)
    except:
      bstack1lll1l1l_opy_ = 0
    CONFIG[bstack1ll111_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧଵ")] = True
    bstack1l1l1llll_opy_ = bstack1l1l111ll_opy_(CONFIG, bstack1lll1l1l_opy_)
    logger.debug(bstack1l11l11l_opy_.format(str(bstack1l1l1llll_opy_)))
    if CONFIG.get(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫଶ")):
      bstack11ll1l1l1l_opy_(bstack1l1l1llll_opy_)
    if bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଷ") in CONFIG and bstack1ll111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧସ") in CONFIG[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ହ")][bstack1lll1l1l_opy_]:
      bstack11l1l1111l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ଺")][bstack1lll1l1l_opy_][bstack1ll111_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ଻")]
    import urllib
    import json
    if bstack1ll111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧ଼ࠪ") in CONFIG and str(CONFIG[bstack1ll111_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫଽ")]).lower() != bstack1ll111_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧା"):
        bstack1l111ll1l1_opy_ = bstack1l1l11l1l1_opy_()
        bstack11l1ll11l1_opy_ = bstack1l111ll1l1_opy_ + urllib.parse.quote(json.dumps(bstack1l1l1llll_opy_))
    else:
        bstack11l1ll11l1_opy_ = bstack1ll111_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫି") + urllib.parse.quote(json.dumps(bstack1l1l1llll_opy_))
    browser = self.connect(bstack11l1ll11l1_opy_)
    return browser
except Exception as e:
    pass
def bstack11l1l1ll1l_opy_():
    global bstack1l1111llll_opy_
    global bstack1ll11lllll_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1ll111l1l_opy_
        global bstack11ll11l11l_opy_
        if not bstack1l11l1ll11_opy_:
          global bstack1lll11l1l1_opy_
          if not bstack1lll11l1l1_opy_:
            from bstack_utils.helper import bstack1ll1l11l_opy_, bstack11l11llll1_opy_, bstack1llll1lll1_opy_
            bstack1lll11l1l1_opy_ = bstack1ll1l11l_opy_()
            bstack11l11llll1_opy_(bstack1ll11lllll_opy_)
            bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(CONFIG, bstack1ll11lllll_opy_)
            bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠥࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡑࡔࡒࡈ࡚ࡉࡔࡠࡏࡄࡔࠧୀ"), bstack1l11l111ll_opy_)
          BrowserType.connect = bstack1ll111l1l_opy_
          return
        BrowserType.launch = bstack11l1l11lll_opy_
        bstack1l1111llll_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1l11ll1111_opy_
      bstack1l1111llll_opy_ = True
    except Exception as e:
      pass
def bstack1l1lllll1_opy_(context, bstack1l11l1l1_opy_):
  try:
    context.page.evaluate(bstack1ll111_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧୁ"), bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩୂ")+ json.dumps(bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠨࡽࡾࠤୃ"))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁ࠿ࠦࡻࡾࠤୄ").format(str(e), traceback.format_exc()))
def bstack11llll1l1l_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1ll111_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ୅"), bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ୆") + json.dumps(message) + bstack1ll111_opy_ (u"ࠪ࠰ࠧࡲࡥࡷࡧ࡯ࠦ࠿࠭େ") + json.dumps(level) + bstack1ll111_opy_ (u"ࠫࢂࢃࠧୈ"))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠥࢁࡽ࠻ࠢࡾࢁࠧ୉").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack11lll11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1111111_opy_(self, url):
  global bstack1l11llllll_opy_
  try:
    bstack1lll1l111_opy_(url)
  except Exception as err:
    logger.debug(bstack1l11ll11l_opy_.format(str(err)))
  try:
    bstack1l11llllll_opy_(self, url)
  except Exception as e:
    try:
      bstack1l111l1l_opy_ = str(e)
      if any(err_msg in bstack1l111l1l_opy_ for err_msg in bstack1111l1ll_opy_):
        bstack1lll1l111_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l11ll11l_opy_.format(str(err)))
    raise e
def bstack1ll111l1ll_opy_(self):
  global bstack1ll111l1l1_opy_
  bstack1ll111l1l1_opy_ = self
  return
def bstack11l11lll1l_opy_(self):
  global bstack11111l11l_opy_
  bstack11111l11l_opy_ = self
  return
def bstack11llll11l1_opy_(test_name, bstack11ll11111l_opy_):
  global CONFIG
  if percy.bstack1l11111l_opy_() == bstack1ll111_opy_ (u"ࠨࡴࡳࡷࡨࠦ୊"):
    bstack1lll1l1l1l_opy_ = os.path.relpath(bstack11ll11111l_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1lll1l1l1l_opy_)
    bstack1l1lll11_opy_ = suite_name + bstack1ll111_opy_ (u"ࠢ࠮ࠤୋ") + test_name
    threading.current_thread().percySessionName = bstack1l1lll11_opy_
def bstack11l1ll1l1l_opy_(self, test, *args, **kwargs):
  global bstack11l11l1ll1_opy_
  test_name = None
  bstack11ll11111l_opy_ = None
  if test:
    test_name = str(test.name)
    bstack11ll11111l_opy_ = str(test.source)
  bstack11llll11l1_opy_(test_name, bstack11ll11111l_opy_)
  bstack11l11l1ll1_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack111l1llll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1lll111l1l_opy_(driver, bstack1l1lll11_opy_):
  if not bstack11ll11lll_opy_ and bstack1l1lll11_opy_:
      bstack1ll1ll1l11_opy_ = {
          bstack1ll111_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨୌ"): bstack1ll111_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧ୍ࠪ"),
          bstack1ll111_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭୎"): {
              bstack1ll111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ୏"): bstack1l1lll11_opy_
          }
      }
      bstack11ll11l1l_opy_ = bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ୐").format(json.dumps(bstack1ll1ll1l11_opy_))
      driver.execute_script(bstack11ll11l1l_opy_)
  if bstack11l1ll1lll_opy_:
      bstack11ll1lll11_opy_ = {
          bstack1ll111_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭୑"): bstack1ll111_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ୒"),
          bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ୓"): {
              bstack1ll111_opy_ (u"ࠩࡧࡥࡹࡧࠧ୔"): bstack1l1lll11_opy_ + bstack1ll111_opy_ (u"ࠪࠤࡵࡧࡳࡴࡧࡧࠥࠬ୕"),
              bstack1ll111_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪୖ"): bstack1ll111_opy_ (u"ࠬ࡯࡮ࡧࡱࠪୗ")
          }
      }
      if bstack11l1ll1lll_opy_.status == bstack1ll111_opy_ (u"࠭ࡐࡂࡕࡖࠫ୘"):
          bstack1lll1l1ll1_opy_ = bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬ୙").format(json.dumps(bstack11ll1lll11_opy_))
          driver.execute_script(bstack1lll1l1ll1_opy_)
          bstack11ll1ll11_opy_(driver, bstack1ll111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ୚"))
      elif bstack11l1ll1lll_opy_.status == bstack1ll111_opy_ (u"ࠩࡉࡅࡎࡒࠧ୛"):
          reason = bstack1ll111_opy_ (u"ࠥࠦଡ଼")
          bstack11lllll1ll_opy_ = bstack1l1lll11_opy_ + bstack1ll111_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠬଢ଼")
          if bstack11l1ll1lll_opy_.message:
              reason = str(bstack11l1ll1lll_opy_.message)
              bstack11lllll1ll_opy_ = bstack11lllll1ll_opy_ + bstack1ll111_opy_ (u"ࠬࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࠬ୞") + reason
          bstack11ll1lll11_opy_[bstack1ll111_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩୟ")] = {
              bstack1ll111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ୠ"): bstack1ll111_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧୡ"),
              bstack1ll111_opy_ (u"ࠩࡧࡥࡹࡧࠧୢ"): bstack11lllll1ll_opy_
          }
          bstack1lll1l1ll1_opy_ = bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨୣ").format(json.dumps(bstack11ll1lll11_opy_))
          driver.execute_script(bstack1lll1l1ll1_opy_)
          bstack11ll1ll11_opy_(driver, bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ୤"), reason)
          bstack1l1l111l11_opy_(reason, str(bstack11l1ll1lll_opy_), str(bstack1ll111111_opy_), logger)
@measure(event_name=EVENTS.bstack11llll11ll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1ll1l1ll_opy_(driver, test):
  if percy.bstack1l11111l_opy_() == bstack1ll111_opy_ (u"ࠧࡺࡲࡶࡧࠥ୥") and percy.bstack1ll1l1lll1_opy_() == bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣ୦"):
      bstack1l11l1l1l1_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ୧"), None)
      bstack1l1l1lll1l_opy_(driver, bstack1l11l1l1l1_opy_, test)
  if (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ୨"), None) and
      bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ୩"), None)) or (
      bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ୪"), None) and
      bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭୫"), None)):
      logger.info(bstack1ll111_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠣࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡷࡱࡨࡪࡸࡷࡢࡻ࠱ࠤࠧ୬"))
      bstack1llll111_opy_.bstack111lll1111_opy_(driver, name=test.name, path=test.source)
def bstack1l1ll1l1_opy_(test, bstack1l1lll11_opy_):
    try:
      bstack111ll1ll1_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ୭")] = bstack1l1lll11_opy_
      if bstack11l1ll1lll_opy_:
        if bstack11l1ll1lll_opy_.status == bstack1ll111_opy_ (u"ࠧࡑࡃࡖࡗࠬ୮"):
          data[bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ୯")] = bstack1ll111_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ୰")
        elif bstack11l1ll1lll_opy_.status == bstack1ll111_opy_ (u"ࠪࡊࡆࡏࡌࠨୱ"):
          data[bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ୲")] = bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ୳")
          if bstack11l1ll1lll_opy_.message:
            data[bstack1ll111_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭୴")] = str(bstack11l1ll1lll_opy_.message)
      user = CONFIG[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ୵")]
      key = CONFIG[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ୶")]
      host = bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠤࡤࡴ࡮ࡹࠢ୷"), bstack1ll111_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧ୸"), bstack1ll111_opy_ (u"ࠦࡦࡶࡩࠣ୹")], bstack1ll111_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡱ࡫࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨ୺"))
      url = bstack1ll111_opy_ (u"࠭ࡻࡾ࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠳ࡸ࡫ࡳࡴ࡫ࡲࡲࡸ࠵ࡻࡾ࠰࡭ࡷࡴࡴࠧ୻").format(host, bstack1ll1lll1ll_opy_)
      headers = {
        bstack1ll111_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡶࡼࡴࡪ࠭୼"): bstack1ll111_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ୽"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers, auth=(user, key))
        cli.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡶࡲࡧࡥࡹ࡫࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡳࡵࡣࡷࡹࡸࠨ୾"), datetime.datetime.now() - bstack111ll1ll1_opy_)
    except Exception as e:
      logger.error(bstack1ll1ll1l_opy_.format(str(e)))
def bstack111111l11_opy_(test, bstack1l1lll11_opy_):
  global CONFIG
  global bstack11111l11l_opy_
  global bstack1ll111l1l1_opy_
  global bstack1ll1lll1ll_opy_
  global bstack11l1ll1lll_opy_
  global bstack11l1l1111l_opy_
  global bstack11ll1111l1_opy_
  global bstack1l11lllll1_opy_
  global bstack11ll1l1111_opy_
  global bstack1lllllll1l_opy_
  global bstack1ll111ll1l_opy_
  global bstack1l1111l111_opy_
  global bstack11l1l1l1l1_opy_
  try:
    if not bstack1ll1lll1ll_opy_:
      with bstack11l1l1l1l1_opy_:
        bstack1l1ll111l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠪࢂࠬ୿")), bstack1ll111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ஀"), bstack1ll111_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧ஁"))
        if os.path.exists(bstack1l1ll111l_opy_):
          with open(bstack1l1ll111l_opy_, bstack1ll111_opy_ (u"࠭ࡲࠨஂ")) as f:
            content = f.read().strip()
            if content:
              bstack1llll1ll_opy_ = json.loads(bstack1ll111_opy_ (u"ࠢࡼࠤஃ") + content + bstack1ll111_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪ஄") + bstack1ll111_opy_ (u"ࠤࢀࠦஅ"))
              bstack1ll1lll1ll_opy_ = bstack1llll1ll_opy_.get(str(threading.get_ident()))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡵࡩࡦࡪࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࠤࡎࡊࡳࠡࡨ࡬ࡰࡪࡀࠠࠨஆ") + str(e))
  if bstack1ll111ll1l_opy_:
    with bstack1111l1ll1_opy_:
      bstack1l111ll111_opy_ = bstack1ll111ll1l_opy_.copy()
    for driver in bstack1l111ll111_opy_:
      if bstack1ll1lll1ll_opy_ == driver.session_id:
        if test:
          bstack1l1ll1l1ll_opy_(driver, test)
        bstack1lll111l1l_opy_(driver, bstack1l1lll11_opy_)
  elif bstack1ll1lll1ll_opy_:
    bstack1l1ll1l1_opy_(test, bstack1l1lll11_opy_)
  if bstack11111l11l_opy_:
    bstack1l11lllll1_opy_(bstack11111l11l_opy_)
  if bstack1ll111l1l1_opy_:
    bstack11ll1l1111_opy_(bstack1ll111l1l1_opy_)
  if bstack1lll1l11_opy_:
    bstack1lllllll1l_opy_()
def bstack11l11l1l11_opy_(self, test, *args, **kwargs):
  bstack1l1lll11_opy_ = None
  if test:
    bstack1l1lll11_opy_ = str(test.name)
  bstack111111l11_opy_(test, bstack1l1lll11_opy_)
  bstack11ll1111l1_opy_(self, test, *args, **kwargs)
def bstack1lll111l1_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1llll1l1l_opy_
  global CONFIG
  global bstack1ll111ll1l_opy_
  global bstack1ll1lll1ll_opy_
  global bstack11l1l1l1l1_opy_
  bstack11ll111lll_opy_ = None
  try:
    if bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪஇ"), None) or bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧஈ"), None):
      try:
        if not bstack1ll1lll1ll_opy_:
          bstack1l1ll111l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"࠭ࡾࠨஉ")), bstack1ll111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧஊ"), bstack1ll111_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ஋"))
          with bstack11l1l1l1l1_opy_:
            if os.path.exists(bstack1l1ll111l_opy_):
              with open(bstack1l1ll111l_opy_, bstack1ll111_opy_ (u"ࠩࡵࠫ஌")) as f:
                content = f.read().strip()
                if content:
                  bstack1llll1ll_opy_ = json.loads(bstack1ll111_opy_ (u"ࠥࡿࠧ஍") + content + bstack1ll111_opy_ (u"ࠫࠧࡾࠢ࠻ࠢࠥࡽࠧ࠭எ") + bstack1ll111_opy_ (u"ࠧࢃࠢஏ"))
                  bstack1ll1lll1ll_opy_ = bstack1llll1ll_opy_.get(str(threading.get_ident()))
      except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࡶࠤ࡫࡯࡬ࡦࠢ࡬ࡲࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࠬஐ") + str(e))
      if bstack1ll111ll1l_opy_:
        with bstack1111l1ll1_opy_:
          bstack1l111ll111_opy_ = bstack1ll111ll1l_opy_.copy()
        for driver in bstack1l111ll111_opy_:
          if bstack1ll1lll1ll_opy_ == driver.session_id:
            bstack11ll111lll_opy_ = driver
    bstack1l11ll11l1_opy_ = bstack1llll111_opy_.bstack11ll11lll1_opy_(test.tags)
    if bstack11ll111lll_opy_:
      threading.current_thread().isA11yTest = bstack1llll111_opy_.bstack1111lll1l_opy_(bstack11ll111lll_opy_, bstack1l11ll11l1_opy_)
      threading.current_thread().isAppA11yTest = bstack1llll111_opy_.bstack1111lll1l_opy_(bstack11ll111lll_opy_, bstack1l11ll11l1_opy_)
    else:
      threading.current_thread().isA11yTest = bstack1l11ll11l1_opy_
      threading.current_thread().isAppA11yTest = bstack1l11ll11l1_opy_
  except:
    pass
  bstack1llll1l1l_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack11l1ll1lll_opy_
  try:
    bstack11l1ll1lll_opy_ = self._test
  except:
    bstack11l1ll1lll_opy_ = self.test
def bstack11l1lllll1_opy_():
  global bstack1ll1l1lll_opy_
  try:
    if os.path.exists(bstack1ll1l1lll_opy_):
      os.remove(bstack1ll1l1lll_opy_)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡧࡩࡱ࡫ࡴࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪ஑") + str(e))
def bstack111lllll_opy_():
  global bstack1ll1l1lll_opy_
  bstack11lll11ll_opy_ = {}
  lock_file = bstack1ll1l1lll_opy_ + bstack1ll111_opy_ (u"ࠨ࠰࡯ࡳࡨࡱࠧஒ")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1ll111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡬ࡰࡥ࡮ࠤࡳࡵࡴࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨ࠰ࠥࡻࡳࡪࡰࡪࠤࡧࡧࡳࡪࡥࠣࡪ࡮ࡲࡥࠡࡱࡳࡩࡷࡧࡴࡪࡱࡱࡷࠬஓ"))
    try:
      if not os.path.isfile(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠪࡻࠬஔ")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠫࡷ࠭க")) as f:
          content = f.read().strip()
          if content:
            bstack11lll11ll_opy_ = json.loads(content)
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஖") + str(e))
    return bstack11lll11ll_opy_
  try:
    os.makedirs(os.path.dirname(bstack1ll1l1lll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      if not os.path.isfile(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"࠭ࡷࠨ஗")) as f:
          json.dump({}, f)
      if os.path.exists(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠧࡳࠩ஘")) as f:
          content = f.read().strip()
          if content:
            bstack11lll11ll_opy_ = json.loads(content)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡶࡪࡧࡤࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪங") + str(e))
  finally:
    return bstack11lll11ll_opy_
def bstack11l1ll11l_opy_(platform_index, item_index):
  global bstack1ll1l1lll_opy_
  lock_file = bstack1ll1l1lll_opy_ + bstack1ll111_opy_ (u"ࠩ࠱ࡰࡴࡩ࡫ࠨச")
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1ll111_opy_ (u"ࠪࡪ࡮ࡲࡥ࡭ࡱࡦ࡯ࠥࡴ࡯ࡵࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩ࠱ࠦࡵࡴ࡫ࡱ࡫ࠥࡨࡡࡴ࡫ࡦࠤ࡫࡯࡬ࡦࠢࡲࡴࡪࡸࡡࡵ࡫ࡲࡲࡸ࠭஛"))
    try:
      bstack11lll11ll_opy_ = {}
      if os.path.exists(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠫࡷ࠭ஜ")) as f:
          content = f.read().strip()
          if content:
            bstack11lll11ll_opy_ = json.loads(content)
      bstack11lll11ll_opy_[item_index] = platform_index
      with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠧࡽࠢ஝")) as outfile:
        json.dump(bstack11lll11ll_opy_, outfile)
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡹࡵ࡭ࡹ࡯࡮ࡨࠢࡷࡳࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫஞ") + str(e))
    return
  try:
    os.makedirs(os.path.dirname(bstack1ll1l1lll_opy_), exist_ok=True)
    with FileLock(lock_file, timeout=10):
      bstack11lll11ll_opy_ = {}
      if os.path.exists(bstack1ll1l1lll_opy_):
        with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠧࡳࠩட")) as f:
          content = f.read().strip()
          if content:
            bstack11lll11ll_opy_ = json.loads(content)
      bstack11lll11ll_opy_[item_index] = platform_index
      with open(bstack1ll1l1lll_opy_, bstack1ll111_opy_ (u"ࠣࡹࠥ஠")) as outfile:
        json.dump(bstack11lll11ll_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡼࡸࡩࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ஡") + str(e))
def bstack1llllll11_opy_(bstack111lll1l1l_opy_):
  global CONFIG
  bstack1ll11l11ll_opy_ = bstack1ll111_opy_ (u"ࠪࠫ஢")
  if not bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧண") in CONFIG:
    logger.info(bstack1ll111_opy_ (u"ࠬࡔ࡯ࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠤࡵࡧࡳࡴࡧࡧࠤࡺࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢࡵࡩࡵࡵࡲࡵࠢࡩࡳࡷࠦࡒࡰࡤࡲࡸࠥࡸࡵ࡯ࠩத"))
  try:
    platform = CONFIG[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ஥")][bstack111lll1l1l_opy_]
    if bstack1ll111_opy_ (u"ࠧࡰࡵࠪ஦") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"ࠨࡱࡶࠫ஧")]) + bstack1ll111_opy_ (u"ࠩ࠯ࠤࠬந")
    if bstack1ll111_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ன") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧப")]) + bstack1ll111_opy_ (u"ࠬ࠲ࠠࠨ஫")
    if bstack1ll111_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪ஬") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ஭")]) + bstack1ll111_opy_ (u"ࠨ࠮ࠣࠫம")
    if bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫய") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬர")]) + bstack1ll111_opy_ (u"ࠫ࠱ࠦࠧற")
    if bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪல") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫள")]) + bstack1ll111_opy_ (u"ࠧ࠭ࠢࠪழ")
    if bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩவ") in platform:
      bstack1ll11l11ll_opy_ += str(platform[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪஶ")]) + bstack1ll111_opy_ (u"ࠪ࠰ࠥ࠭ஷ")
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠫࡘࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡷࡹࡸࡩ࡯ࡩࠣࡪࡴࡸࠠࡳࡧࡳࡳࡷࡺࠠࡨࡧࡱࡩࡷࡧࡴࡪࡱࡱࠫஸ") + str(e))
  finally:
    if bstack1ll11l11ll_opy_[len(bstack1ll11l11ll_opy_) - 2:] == bstack1ll111_opy_ (u"ࠬ࠲ࠠࠨஹ"):
      bstack1ll11l11ll_opy_ = bstack1ll11l11ll_opy_[:-2]
    return bstack1ll11l11ll_opy_
def bstack1ll11l1ll_opy_(path, bstack1ll11l11ll_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack111l1111_opy_ = ET.parse(path)
    bstack1ll11111ll_opy_ = bstack111l1111_opy_.getroot()
    bstack1l1l1lll1_opy_ = None
    for suite in bstack1ll11111ll_opy_.iter(bstack1ll111_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬ஺")):
      if bstack1ll111_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ஻") in suite.attrib:
        suite.attrib[bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭஼")] += bstack1ll111_opy_ (u"ࠩࠣࠫ஽") + bstack1ll11l11ll_opy_
        bstack1l1l1lll1_opy_ = suite
    bstack1l111lll1_opy_ = None
    for robot in bstack1ll11111ll_opy_.iter(bstack1ll111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩா")):
      bstack1l111lll1_opy_ = robot
    bstack111lll1l11_opy_ = len(bstack1l111lll1_opy_.findall(bstack1ll111_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪி")))
    if bstack111lll1l11_opy_ == 1:
      bstack1l111lll1_opy_.remove(bstack1l111lll1_opy_.findall(bstack1ll111_opy_ (u"ࠬࡹࡵࡪࡶࡨࠫீ"))[0])
      bstack11lll111l1_opy_ = ET.Element(bstack1ll111_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬு"), attrib={bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬூ"): bstack1ll111_opy_ (u"ࠨࡕࡸ࡭ࡹ࡫ࡳࠨ௃"), bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬ௄"): bstack1ll111_opy_ (u"ࠪࡷ࠵࠭௅")})
      bstack1l111lll1_opy_.insert(1, bstack11lll111l1_opy_)
      bstack1l11ll1lll_opy_ = None
      for suite in bstack1l111lll1_opy_.iter(bstack1ll111_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪெ")):
        bstack1l11ll1lll_opy_ = suite
      bstack1l11ll1lll_opy_.append(bstack1l1l1lll1_opy_)
      bstack11l1l111l_opy_ = None
      for status in bstack1l1l1lll1_opy_.iter(bstack1ll111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬே")):
        bstack11l1l111l_opy_ = status
      bstack1l11ll1lll_opy_.append(bstack11l1l111l_opy_)
    bstack111l1111_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠫை") + str(e))
def bstack111llll1l1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1l1l111lll_opy_
  global CONFIG
  if bstack1ll111_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࡰࡢࡶ࡫ࠦ௉") in options:
    del options[bstack1ll111_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࡱࡣࡷ࡬ࠧொ")]
  bstack1l1l111l_opy_ = bstack111lllll_opy_()
  for item_id in bstack1l1l111l_opy_.keys():
    path = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠩࡳࡥࡧࡵࡴࡠࡴࡨࡷࡺࡲࡴࡴࠩோ"), str(item_id), bstack1ll111_opy_ (u"ࠪࡳࡺࡺࡰࡶࡶ࠱ࡼࡲࡲࠧௌ"))
    bstack1ll11l1ll_opy_(path, bstack1llllll11_opy_(bstack1l1l111l_opy_[item_id]))
  bstack11l1lllll1_opy_()
  return bstack1l1l111lll_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1ll11ll11l_opy_(self, ff_profile_dir):
  global bstack11ll11ll1l_opy_
  if not ff_profile_dir:
    return None
  return bstack11ll11ll1l_opy_(self, ff_profile_dir)
def bstack1l111llll1_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1l1lllll_opy_
  bstack11l11l11l1_opy_ = []
  if bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹ்ࠧ") in CONFIG:
    bstack11l11l11l1_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ௎")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࠢ௏")],
      pabot_args[bstack1ll111_opy_ (u"ࠢࡷࡧࡵࡦࡴࡹࡥࠣௐ")],
      argfile,
      pabot_args.get(bstack1ll111_opy_ (u"ࠣࡪ࡬ࡺࡪࠨ௑")),
      pabot_args[bstack1ll111_opy_ (u"ࠤࡳࡶࡴࡩࡥࡴࡵࡨࡷࠧ௒")],
      platform[0],
      bstack1l1lllll_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1ll111_opy_ (u"ࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸ࡫࡯࡬ࡦࡵࠥ௓")] or [(bstack1ll111_opy_ (u"ࠦࠧ௔"), None)]
    for platform in enumerate(bstack11l11l11l1_opy_)
  ]
def bstack1l1ll11lll_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1ll11lll11_opy_=bstack1ll111_opy_ (u"ࠬ࠭௕")):
  global bstack11l1l1l1ll_opy_
  self.platform_index = platform_index
  self.bstack111l1lll_opy_ = bstack1ll11lll11_opy_
  bstack11l1l1l1ll_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack11l11ll111_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1l11ll111l_opy_
  global bstack1l1111l1_opy_
  bstack11l1l1l1_opy_ = copy.deepcopy(item)
  if not bstack1ll111_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ௖") in item.options:
    bstack11l1l1l1_opy_.options[bstack1ll111_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩௗ")] = []
  bstack1l111l1lll_opy_ = bstack11l1l1l1_opy_.options[bstack1ll111_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௘")].copy()
  for v in bstack11l1l1l1_opy_.options[bstack1ll111_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௙")]:
    if bstack1ll111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡓࡐࡆ࡚ࡆࡐࡔࡐࡍࡓࡊࡅ࡙ࠩ௚") in v:
      bstack1l111l1lll_opy_.remove(v)
    if bstack1ll111_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡇࡑࡏࡁࡓࡉࡖࠫ௛") in v:
      bstack1l111l1lll_opy_.remove(v)
    if bstack1ll111_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡉࡋࡆࡍࡑࡆࡅࡑࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ௜") in v:
      bstack1l111l1lll_opy_.remove(v)
  bstack1l111l1lll_opy_.insert(0, bstack1ll111_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜࠿ࢁࡽࠨ௝").format(bstack11l1l1l1_opy_.platform_index))
  bstack1l111l1lll_opy_.insert(0, bstack1ll111_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࠾ࢀࢃࠧ௞").format(bstack11l1l1l1_opy_.bstack111l1lll_opy_))
  bstack11l1l1l1_opy_.options[bstack1ll111_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ௟")] = bstack1l111l1lll_opy_
  if bstack1l1111l1_opy_:
    bstack11l1l1l1_opy_.options[bstack1ll111_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ௠")].insert(0, bstack1ll111_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡆࡐࡎࡇࡒࡈࡕ࠽ࡿࢂ࠭௡").format(bstack1l1111l1_opy_))
  return bstack1l11ll111l_opy_(caller_id, datasources, is_last, bstack11l1l1l1_opy_, outs_dir)
def bstack1ll11ll1_opy_(command, item_index):
  try:
    if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ௢")):
      os.environ[bstack1ll111_opy_ (u"ࠬࡉࡕࡓࡔࡈࡒ࡙ࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡆࡄࡘࡆ࠭௣")] = json.dumps(CONFIG[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ௤")][item_index % bstack1ll1l1ll11_opy_])
    global bstack1l1111l1_opy_
    if bstack1l1111l1_opy_:
      command[0] = command[0].replace(bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭௥"), bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡴࡦ࡮ࠤࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠥ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩ௦") + str(item_index % bstack1ll1l1ll11_opy_) + bstack1ll111_opy_ (u"ࠩࠣ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠢࠪ௧") + str(
        item_index) + bstack1ll111_opy_ (u"ࠪࠤࠬ௨") + bstack1l1111l1_opy_, 1)
    else:
      command[0] = command[0].replace(bstack1ll111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪ௩"),
                                      bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡸࡪ࡫ࠡࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠥ࠭௪") +  str(item_index % bstack1ll1l1ll11_opy_) + bstack1ll111_opy_ (u"࠭ࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽࠦࠧ௫") + str(item_index), 1)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦ࡭ࡰࡦ࡬ࡪࡾ࡯࡮ࡨࠢࡦࡳࡲࡳࡡ࡯ࡦࠣࡪࡴࡸࠠࡱࡣࡥࡳࡹࠦࡲࡶࡰ࠽ࠤࢀࢃࠧ௬").format(str(e)))
def bstack111ll1ll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1111lllll_opy_
  try:
    bstack1ll11ll1_opy_(command, item_index)
    return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡦࡨ࡯ࡵࠢࡵࡹࡳࡀࠠࡼࡿࠪ௭").format(str(e)))
    raise e
def bstack1l1l11l11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1111lllll_opy_
  try:
    bstack1ll11ll1_opy_(command, item_index)
    return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡢࡰࡶࠣࡶࡺࡴࠠ࠳࠰࠴࠷࠿ࠦࡻࡾࠩ௮").format(str(e)))
    try:
      return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
    except Exception as e2:
      logger.error(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤ࠷࠴࠱࠴ࠢࡩࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࢁࡽࠨ௯").format(str(e2)))
      raise e
def bstack11l111l111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1111lllll_opy_
  try:
    bstack1ll11ll1_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥࡸࡵ࡯ࠢ࠵࠲࠶࠻࠺ࠡࡽࢀࠫ௰").format(str(e)))
    try:
      return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
    except Exception as e2:
      logger.error(bstack1ll111_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡱࡣࡥࡳࡹࠦ࠲࠯࠳࠸ࠤ࡫ࡧ࡬࡭ࡤࡤࡧࡰࡀࠠࡼࡿࠪ௱").format(str(e2)))
      raise e
def _1l1lll1ll_opy_(bstack1111l11l1_opy_, item_index, process_timeout, sleep_before_start, bstack11l1l1111_opy_):
  bstack1ll11ll1_opy_(bstack1111l11l1_opy_, item_index)
  if process_timeout is None:
    process_timeout = 3600
  if sleep_before_start and sleep_before_start > 0:
    time.sleep(min(sleep_before_start, 5))
  return process_timeout
def bstack11lll1lll_opy_(command, bstack1l1l1lllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1111lllll_opy_
  global bstack11llll1l1_opy_
  global bstack1l1111l1_opy_
  try:
    for env_name, bstack11111ll1_opy_ in bstack11llll1l1_opy_.items():
      os.environ[env_name] = bstack11111ll1_opy_
    bstack1l1111l1_opy_ = bstack1ll111_opy_ (u"ࠨࠢ௲")
    bstack1ll11ll1_opy_(command, item_index)
    if process_timeout is None:
      process_timeout = 3600
    if sleep_before_start and sleep_before_start > 0:
      time.sleep(min(sleep_before_start, 5))
    return bstack1111lllll_opy_(command, bstack1l1l1lllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡳࡥࡧࡵࡴࠡࡴࡸࡲࠥ࠻࠮࠱࠼ࠣࡿࢂ࠭௳").format(str(e)))
    try:
      return bstack1111lllll_opy_(command, bstack1l1l1lllll_opy_, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡦࡨ࡯ࡵࠢࡩࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࢁࡽࠨ௴").format(str(e2)))
      raise e
def bstack1lll111ll1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack1111lllll_opy_
  try:
    process_timeout = _1l1lll1ll_opy_(command, item_index, process_timeout, sleep_before_start, bstack1ll111_opy_ (u"ࠩ࠷࠲࠷࠭௵"))
    return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡣࡱࡷࠤࡷࡻ࡮ࠡ࠶࠱࠶࠿ࠦࡻࡾࠩ௶").format(str(e)))
    try:
      return bstack1111lllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
    except Exception as e2:
      logger.error(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡤࡲࡸࠥ࡬ࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࡽࢀࠫ௷").format(str(e2)))
      raise e
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack1llll1lll_opy_(self, runner, quiet=False, capture=True):
  global bstack1ll1llll11_opy_
  bstack1111111l_opy_ = bstack1ll1llll11_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack1ll111_opy_ (u"ࠬ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࡠࡣࡵࡶࠬ௸")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1ll111_opy_ (u"࠭ࡥࡹࡥࡢࡸࡷࡧࡣࡦࡤࡤࡧࡰࡥࡡࡳࡴࠪ௹")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1111111l_opy_
def bstack1l11lll1_opy_(runner, hook_name, context, element, bstack1l111ll11l_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack1l1lll1l1l_opy_.bstack111llll1_opy_(hook_name, element)
    bstack1l111ll11l_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack1l1lll1l1l_opy_.bstack1ll1lll111_opy_(element)
      if hook_name not in [bstack1ll111_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠫ௺"), bstack1ll111_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠫ௻")] and args and hasattr(args[0], bstack1ll111_opy_ (u"ࠩࡨࡶࡷࡵࡲࡠ࡯ࡨࡷࡸࡧࡧࡦࠩ௼")):
        args[0].error_message = bstack1ll111_opy_ (u"ࠪࠫ௽")
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡩࡣࡱࡨࡱ࡫ࠠࡩࡱࡲ࡯ࡸࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦ࠼ࠣࡿࢂ࠭௾").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lll111l_opy_, stage=STAGE.bstack11ll1lll1_opy_, hook_type=bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡆࡲ࡬ࠣ௿"), bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack111l11ll_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    if runner.hooks.get(bstack1ll111_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥఀ")).__name__ != bstack1ll111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࡣࡩ࡫ࡦࡢࡷ࡯ࡸࡤ࡮࡯ࡰ࡭ࠥఁ"):
      bstack1l11lll1_opy_(runner, name, context, runner, bstack1l111ll11l_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack1l1111ll_opy_(bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧం")) else context.browser
      runner.driver_initialised = bstack1ll111_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨః")
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡨࡷ࡯ࡶࡦࡴࠣ࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡸ࡫ࠠࡢࡶࡷࡶ࡮ࡨࡵࡵࡧ࠽ࠤࢀࢃࠧఄ").format(str(e)))
def bstack1lll1l1ll_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    bstack1l11lll1_opy_(runner, name, context, context.feature, bstack1l111ll11l_opy_, *args)
    try:
      if not bstack11ll11lll_opy_:
        bstack11ll111lll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1111ll_opy_(bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఅ")) else context.browser
        if is_driver_active(bstack11ll111lll_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪࠨఆ")
          bstack1l11l1l1_opy_ = str(runner.feature.name)
          bstack1l1lllll1_opy_(context, bstack1l11l1l1_opy_)
          bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠣࠫఇ") + json.dumps(bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠧࡾࡿࠪఈ"))
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠠࡪࡰࠣࡦࡪ࡬࡯ࡳࡧࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨఉ").format(str(e)))
def bstack1ll1llll1l_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    if hasattr(context, bstack1ll111_opy_ (u"ࠩࡶࡧࡪࡴࡡࡳ࡫ࡲࠫఊ")):
        bstack1l1lll1l1l_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack1ll111_opy_ (u"ࠪࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬఋ")) else context.feature
    bstack1l11lll1_opy_(runner, name, context, target, bstack1l111ll11l_opy_, *args)
@measure(event_name=EVENTS.bstack11l1ll1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1ll1lll_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    if len(context.scenario.tags) == 0: bstack1l1lll1l1l_opy_.start_test(context)
    bstack1l11lll1_opy_(runner, name, context, context.scenario, bstack1l111ll11l_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack11ll11ll11_opy_.bstack11111lll_opy_(context, *args)
    try:
      bstack11ll111lll_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఌ"), context.browser)
      if is_driver_active(bstack11ll111lll_opy_):
        bstack111l1l111_opy_.bstack11l1llll11_opy_(bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫ఍"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack1ll111_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣఎ")
        if (not bstack11ll11lll_opy_):
          scenario_name = args[0].name
          feature_name = bstack1l11l1l1_opy_ = str(runner.feature.name)
          bstack1l11l1l1_opy_ = feature_name + bstack1ll111_opy_ (u"ࠧࠡ࠯ࠣࠫఏ") + scenario_name
          if runner.driver_initialised == bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠥఐ"):
            bstack1l1lllll1_opy_(context, bstack1l11l1l1_opy_)
            bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿ࠦࠧ఑") + json.dumps(bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠪࢁࢂ࠭ఒ"))
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣ࡭ࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡤࡧࡱࡥࡷ࡯࡯࠻ࠢࡾࢁࠬఓ").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lll111l_opy_, stage=STAGE.bstack11ll1lll1_opy_, hook_type=bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡘࡺࡥࡱࠤఔ"), bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1lllll1_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    bstack1l11lll1_opy_(runner, name, context, args[0], bstack1l111ll11l_opy_, *args)
    try:
      bstack11ll111lll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1111ll_opy_(bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬక")) else context.browser
      if is_driver_active(bstack11ll111lll_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack1ll111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧఖ")
        bstack1l1lll1l1l_opy_.bstack1l11l111l1_opy_(args[0])
        if runner.driver_initialised == bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨగ"):
          feature_name = bstack1l11l1l1_opy_ = str(runner.feature.name)
          bstack1l11l1l1_opy_ = feature_name + bstack1ll111_opy_ (u"ࠩࠣ࠱ࠥ࠭ఘ") + context.scenario.name
          bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨఙ") + json.dumps(bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠫࢂࢃࠧచ"))
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠤ࡮ࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡶࡨࡴ࠿ࠦࡻࡾࠩఛ").format(str(e)))
@measure(event_name=EVENTS.bstack1l1lll111l_opy_, stage=STAGE.bstack11ll1lll1_opy_, hook_type=bstack1ll111_opy_ (u"ࠨࡡࡧࡶࡨࡶࡘࡺࡥࡱࠤజ"), bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1l1ll1_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
  bstack1l1lll1l1l_opy_.bstack1llll1ll1_opy_(args[0])
  try:
    step_status = args[0].status.name
    bstack11ll111lll_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ఝ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack11ll111lll_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack1ll111_opy_ (u"ࠨ࡫ࡱࡷࡹ࡫ࡰࠨఞ")
        feature_name = bstack1l11l1l1_opy_ = str(runner.feature.name)
        bstack1l11l1l1_opy_ = feature_name + bstack1ll111_opy_ (u"ࠩࠣ࠱ࠥ࠭ట") + context.scenario.name
        bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨఠ") + json.dumps(bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠫࢂࢃࠧడ"))
    if str(step_status).lower() == bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬఢ"):
      bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"࠭ࠧణ")
      bstack11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠧࠨత")
      bstack1111l1lll_opy_ = bstack1ll111_opy_ (u"ࠨࠩథ")
      try:
        import traceback
        bstack1l111l1111_opy_ = runner.exception.__class__.__name__
        bstack11ll1l11l1_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠩࠣࠫద").join(bstack11ll1l11l1_opy_)
        bstack1111l1lll_opy_ = bstack11ll1l11l1_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1ll1ll1_opy_.format(str(e)))
      bstack1l111l1111_opy_ += bstack1111l1lll_opy_
      bstack11llll1l1l_opy_(context, json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤధ") + str(bstack11ll111ll_opy_)),
                          bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥన"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠥ఩"):
        bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"࠭ࡰࡢࡩࡨࠫప"), None), bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢఫ"), bstack1l111l1111_opy_)
        bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭బ") + json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠤࠣ࠱ࠥࡌࡡࡪ࡮ࡨࡨࠦࡢ࡮ࠣభ") + str(bstack11ll111ll_opy_)) + bstack1ll111_opy_ (u"ࠪ࠰ࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣࡧࡵࡶࡴࡸࠢࡾࡿࠪమ"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠤయ"):
        bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬర"), bstack1ll111_opy_ (u"ࠨࡓࡤࡧࡱࡥࡷ࡯࡯ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥఱ") + str(bstack1l111l1111_opy_))
    else:
      bstack11llll1l1l_opy_(context, bstack1ll111_opy_ (u"ࠢࡑࡣࡶࡷࡪࡪࠡࠣల"), bstack1ll111_opy_ (u"ࠣ࡫ࡱࡪࡴࠨళ"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢఴ"):
        bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"ࠪࡴࡦ࡭ࡥࠨవ"), None), bstack1ll111_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦశ"))
      bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪష") + json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠨࠠ࠮ࠢࡓࡥࡸࡹࡥࡥࠣࠥస")) + bstack1ll111_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡯࡮ࡧࡱࠥࢁࢂ࠭హ"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨ఺"):
        bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ఻"))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡴࡶࡨࡴ࠿ࠦࡻࡾ఼ࠩ").format(str(e)))
  bstack1l11lll1_opy_(runner, name, context, args[0], bstack1l111ll11l_opy_, *args)
@measure(event_name=EVENTS.bstack1l1111111l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1l1l1l_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
  bstack1l1lll1l1l_opy_.end_test(args[0])
  try:
    bstack11l11ll11_opy_ = args[0].status.name
    bstack11ll111lll_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఽ"), context.browser)
    bstack11ll11ll11_opy_.bstack1l1lllll1l_opy_(bstack11ll111lll_opy_)
    if str(bstack11l11ll11_opy_).lower() == bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬా"):
      bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"࠭ࠧి")
      bstack11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠧࠨీ")
      bstack1111l1lll_opy_ = bstack1ll111_opy_ (u"ࠨࠩు")
      try:
        import traceback
        bstack1l111l1111_opy_ = runner.exception.__class__.__name__
        bstack11ll1l11l1_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11ll111ll_opy_ = bstack1ll111_opy_ (u"ࠩࠣࠫూ").join(bstack11ll1l11l1_opy_)
        bstack1111l1lll_opy_ = bstack11ll1l11l1_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l1ll1ll1_opy_.format(str(e)))
      bstack1l111l1111_opy_ += bstack1111l1lll_opy_
      bstack11llll1l1l_opy_(context, json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤృ") + str(bstack11ll111ll_opy_)),
                          bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥౄ"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢ౅") or runner.driver_initialised == bstack1ll111_opy_ (u"࠭ࡩ࡯ࡵࡷࡩࡵ࠭ె"):
        bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"ࠧࡱࡣࡪࡩࠬే"), None), bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣై"), bstack1l111l1111_opy_)
        bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ౉") + json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤొ") + str(bstack11ll111ll_opy_)) + bstack1ll111_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤࡨࡶࡷࡵࡲࠣࡿࢀࠫో"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢౌ") or runner.driver_initialised == bstack1ll111_opy_ (u"࠭ࡩ࡯ࡵࡷࡩࡵ్࠭"):
        bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ౎"), bstack1ll111_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧ౏") + str(bstack1l111l1111_opy_))
    else:
      bstack11llll1l1l_opy_(context, bstack1ll111_opy_ (u"ࠤࡓࡥࡸࡹࡥࡥࠣࠥ౐"), bstack1ll111_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣ౑"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨ౒") or runner.driver_initialised == bstack1ll111_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬ౓"):
        bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"࠭ࡰࡢࡩࡨࠫ౔"), None), bstack1ll111_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪౕࠢ"))
      bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿ౖ࠭") + json.dumps(str(args[0].name) + bstack1ll111_opy_ (u"ࠤࠣ࠱ࠥࡖࡡࡴࡵࡨࡨࠦࠨ౗")) + bstack1ll111_opy_ (u"ࠪ࠰ࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣ࡫ࡱࡪࡴࠨࡽࡾࠩౘ"))
      if runner.driver_initialised == bstack1ll111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨౙ") or runner.driver_initialised == bstack1ll111_opy_ (u"ࠬ࡯࡮ࡴࡶࡨࡴࠬౚ"):
        bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ౛"))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡱࡦࡸ࡫ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢ࡬ࡲࠥࡧࡦࡵࡧࡵࠤ࡫࡫ࡡࡵࡷࡵࡩ࠿ࠦࡻࡾࠩ౜").format(str(e)))
  bstack1l11lll1_opy_(runner, name, context, context.scenario, bstack1l111ll11l_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1lll11111l_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    target = context.scenario if hasattr(context, bstack1ll111_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪౝ")) else context.feature
    bstack1l11lll1_opy_(runner, name, context, target, bstack1l111ll11l_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack11l1ll111_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    try:
      bstack11ll111lll_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ౞"), context.browser)
      bstack1ll1lll1_opy_ = bstack1ll111_opy_ (u"ࠪࠫ౟")
      if context.failed is True:
        bstack11lll11111_opy_ = []
        bstack11l1l11l_opy_ = []
        bstack111ll1l1_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack11lll11111_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack11ll1l11l1_opy_ = traceback.format_tb(exc_tb)
            bstack1lll1lll_opy_ = bstack1ll111_opy_ (u"ࠫࠥ࠭ౠ").join(bstack11ll1l11l1_opy_)
            bstack11l1l11l_opy_.append(bstack1lll1lll_opy_)
            bstack111ll1l1_opy_.append(bstack11ll1l11l1_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1ll1ll1_opy_.format(str(e)))
        bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"ࠬ࠭ౡ")
        for i in range(len(bstack11lll11111_opy_)):
          bstack1l111l1111_opy_ += bstack11lll11111_opy_[i] + bstack111ll1l1_opy_[i] + bstack1ll111_opy_ (u"࠭࡜࡯ࠩౢ")
        bstack1ll1lll1_opy_ = bstack1ll111_opy_ (u"ࠧࠡࠩౣ").join(bstack11l1l11l_opy_)
        if runner.driver_initialised in [bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡨࡨࡥࡹࡻࡲࡦࠤ౤"), bstack1ll111_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨ౥")]:
          bstack11llll1l1l_opy_(context, bstack1ll1lll1_opy_, bstack1ll111_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤ౦"))
          bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"ࠫࡵࡧࡧࡦࠩ౧"), None), bstack1ll111_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧ౨"), bstack1l111l1111_opy_)
          bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫ౩") + json.dumps(bstack1ll1lll1_opy_) + bstack1ll111_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡫ࡲࡳࡱࡵࠦࢂࢃࠧ౪"))
          bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ౫"), bstack1ll111_opy_ (u"ࠤࡖࡳࡲ࡫ࠠࡴࡥࡨࡲࡦࡸࡩࡰࡵࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࡡࡴࠢ౬") + str(bstack1l111l1111_opy_))
          bstack1l1ll11l11_opy_ = bstack11l11l1111_opy_(bstack1ll1lll1_opy_, runner.feature.name, logger)
          if (bstack1l1ll11l11_opy_ != None):
            bstack11llll1l_opy_.append(bstack1l1ll11l11_opy_)
      else:
        if runner.driver_initialised in [bstack1ll111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠦ౭"), bstack1ll111_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣ౮")]:
          bstack11llll1l1l_opy_(context, bstack1ll111_opy_ (u"ࠧࡌࡥࡢࡶࡸࡶࡪࡀࠠࠣ౯") + str(runner.feature.name) + bstack1ll111_opy_ (u"ࠨࠠࡱࡣࡶࡷࡪࡪࠡࠣ౰"), bstack1ll111_opy_ (u"ࠢࡪࡰࡩࡳࠧ౱"))
          bstack1l1l1ll1l1_opy_(getattr(context, bstack1ll111_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭౲"), None), bstack1ll111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ౳"))
          bstack11ll111lll_opy_.execute_script(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ౴") + json.dumps(bstack1ll111_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢ౵") + str(runner.feature.name) + bstack1ll111_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢ౶")) + bstack1ll111_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤࢀࢁࠬ౷"))
          bstack11ll1ll11_opy_(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ౸"))
          bstack1l1ll11l11_opy_ = bstack11l11l1111_opy_(bstack1ll1lll1_opy_, runner.feature.name, logger)
          if (bstack1l1ll11l11_opy_ != None):
            bstack11llll1l_opy_.append(bstack1l1ll11l11_opy_)
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪ౹").format(str(e)))
    bstack1l11lll1_opy_(runner, name, context, context.feature, bstack1l111ll11l_opy_, *args)
@measure(event_name=EVENTS.bstack1l1lll111l_opy_, stage=STAGE.bstack11ll1lll1_opy_, hook_type=bstack1ll111_opy_ (u"ࠤࡤࡪࡹ࡫ࡲࡂ࡮࡯ࠦ౺"), bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11111l111_opy_(runner, name, context, bstack1l111ll11l_opy_, *args):
    bstack1l11lll1_opy_(runner, name, context, runner, bstack1l111ll11l_opy_, *args)
def bstack11llll1ll1_opy_(self, name, context, *args):
  try:
    if bstack1l11l1ll11_opy_:
      platform_index = int(threading.current_thread()._name) % bstack1ll1l1ll11_opy_
      bstack1l11ll1l1l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭౻")][platform_index]
      os.environ[bstack1ll111_opy_ (u"ࠫࡈ࡛ࡒࡓࡇࡑࡘࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡅࡃࡗࡅࠬ౼")] = json.dumps(bstack1l11ll1l1l_opy_)
    global bstack1l111ll11l_opy_
    if not hasattr(self, bstack1ll111_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡳࡦࡦࠪ౽")):
      self.driver_initialised = None
    bstack1111l111l_opy_ = {
        bstack1ll111_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠪ౾"): bstack111l11ll_opy_,
        bstack1ll111_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠨ౿"): bstack1lll1l1ll_opy_,
        bstack1ll111_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡶࡤ࡫ࠬಀ"): bstack1ll1llll1l_opy_,
        bstack1ll111_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫಁ"): bstack1l1ll1lll_opy_,
        bstack1ll111_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠨಂ"): bstack1ll1lllll1_opy_,
        bstack1ll111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡹ࡫ࡰࠨಃ"): bstack1ll1l1ll1_opy_,
        bstack1ll111_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭಄"): bstack1l1l1l1l_opy_,
        bstack1ll111_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡺࡡࡨࠩಅ"): bstack1lll11111l_opy_,
        bstack1ll111_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫ࠧಆ"): bstack11l1ll111_opy_,
        bstack1ll111_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠫಇ"): bstack11111l111_opy_
    }
    handler = bstack1111l111l_opy_.get(name, bstack1l111ll11l_opy_)
    try:
      handler(self, name, context, bstack1l111ll11l_opy_, *args)
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡧ࡫ࡨࡢࡸࡨࠤ࡭ࡵ࡯࡬ࠢ࡫ࡥࡳࡪ࡬ࡦࡴࠣࡿࢂࡀࠠࡼࡿࠪಈ").format(name, str(e)))
    if name in [bstack1ll111_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪಉ"), bstack1ll111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬಊ"), bstack1ll111_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡦࡲ࡬ࠨಋ")]:
      try:
        bstack11ll111lll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1111ll_opy_(bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬಌ")) else context.browser
        bstack1l11l1llll_opy_ = (
          (name == bstack1ll111_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠪ಍") and self.driver_initialised == bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧಎ")) or
          (name == bstack1ll111_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩಏ") and self.driver_initialised == bstack1ll111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠦಐ")) or
          (name == bstack1ll111_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬ಑") and self.driver_initialised in [bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠢಒ"), bstack1ll111_opy_ (u"ࠨࡩ࡯ࡵࡷࡩࡵࠨಓ")]) or
          (name == bstack1ll111_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡵࡧࡳࠫಔ") and self.driver_initialised == bstack1ll111_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵࠨಕ"))
        )
        if bstack1l11l1llll_opy_:
          self.driver_initialised = None
          if bstack11ll111lll_opy_ and hasattr(bstack11ll111lll_opy_, bstack1ll111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩ࠭ಖ")):
            try:
              bstack11ll111lll_opy_.quit()
            except Exception as e:
              logger.debug(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡴࡹ࡮ࡺࡴࡪࡰࡪࠤࡩࡸࡩࡷࡧࡵࠤ࡮ࡴࠠࡣࡧ࡫ࡥࡻ࡫ࠠࡩࡱࡲ࡯࠿ࠦࡻࡾࠩಗ").format(str(e)))
      except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥ࡮࡯ࡰ࡭ࠣࡧࡱ࡫ࡡ࡯ࡷࡳࠤ࡫ࡵࡲࠡࡽࢀ࠾ࠥࢁࡽࠨಘ").format(name, str(e)))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠬࡉࡲࡪࡶ࡬ࡧࡦࡲࠠࡦࡴࡵࡳࡷࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦࠢࡵࡹࡳࠦࡨࡰࡱ࡮ࠤࢀࢃ࠺ࠡࡽࢀࠫಙ").format(name, str(e)))
    try:
      bstack1l111ll11l_opy_(self, name, context, *args)
    except Exception as e2:
      logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡳࡷ࡯ࡧࡪࡰࡤࡰࠥࡨࡥࡩࡣࡹࡩࠥ࡮࡯ࡰ࡭ࠣࡿࢂࡀࠠࡼࡿࠪಚ").format(name, str(e2)))
def bstack1l1l1l11l_opy_(config, startdir):
  return bstack1ll111_opy_ (u"ࠢࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡽ࠳ࢁࠧಛ").format(bstack1ll111_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢಜ"))
notset = Notset()
def bstack1l1l1ll111_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack11l111ll11_opy_
  if str(name).lower() == bstack1ll111_opy_ (u"ࠩࡧࡶ࡮ࡼࡥࡳࠩಝ"):
    return bstack1ll111_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤಞ")
  else:
    return bstack11l111ll11_opy_(self, name, default, skip)
def bstack1l1l1ll1_opy_(item, when):
  global bstack1lllllllll_opy_
  try:
    bstack1lllllllll_opy_(item, when)
  except Exception as e:
    pass
def bstack1l1ll11111_opy_():
  return
def bstack1l111l1l11_opy_(type, name, status, reason, bstack11lll1l1l_opy_, bstack11llll111_opy_):
  bstack1ll1ll1l11_opy_ = {
    bstack1ll111_opy_ (u"ࠫࡦࡩࡴࡪࡱࡱࠫಟ"): type,
    bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨಠ"): {}
  }
  if type == bstack1ll111_opy_ (u"࠭ࡡ࡯ࡰࡲࡸࡦࡺࡥࠨಡ"):
    bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪಢ")][bstack1ll111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧಣ")] = bstack11lll1l1l_opy_
    bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬತ")][bstack1ll111_opy_ (u"ࠪࡨࡦࡺࡡࠨಥ")] = json.dumps(str(bstack11llll111_opy_))
  if type == bstack1ll111_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬದ"):
    bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨಧ")][bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫನ")] = name
  if type == bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪ಩"):
    bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫಪ")][bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩಫ")] = status
    if status == bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪಬ"):
      bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧಭ")][bstack1ll111_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬಮ")] = json.dumps(str(reason))
  bstack11ll11l1l_opy_ = bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫಯ").format(json.dumps(bstack1ll1ll1l11_opy_))
  return bstack11ll11l1l_opy_
def bstack1lll1l1111_opy_(driver_command, response):
    if driver_command == bstack1ll111_opy_ (u"ࠧࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠫರ"):
        bstack111l1l111_opy_.bstack1lll1lllll_opy_({
            bstack1ll111_opy_ (u"ࠨ࡫ࡰࡥ࡬࡫ࠧಱ"): response[bstack1ll111_opy_ (u"ࠩࡹࡥࡱࡻࡥࠨಲ")],
            bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪಳ"): bstack111l1l111_opy_.current_test_uuid()
        })
def bstack11l1111l1_opy_(item, call, rep):
  global bstack111ll11l1_opy_
  global bstack1ll111ll1l_opy_
  global bstack11ll11lll_opy_
  name = bstack1ll111_opy_ (u"ࠫࠬ಴")
  try:
    if rep.when == bstack1ll111_opy_ (u"ࠬࡩࡡ࡭࡮ࠪವ"):
      bstack1ll1lll1ll_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack11ll11lll_opy_:
          name = str(rep.nodeid)
          bstack1ll11l1l_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧಶ"), name, bstack1ll111_opy_ (u"ࠧࠨಷ"), bstack1ll111_opy_ (u"ࠨࠩಸ"), bstack1ll111_opy_ (u"ࠩࠪಹ"), bstack1ll111_opy_ (u"ࠪࠫ಺"))
          threading.current_thread().bstack1l11ll1l11_opy_ = name
          for driver in bstack1ll111ll1l_opy_:
            if bstack1ll1lll1ll_opy_ == driver.session_id:
              driver.execute_script(bstack1ll11l1l_opy_)
      except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠥ࡬࡯ࡳࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡳࡦࡵࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠫ಻").format(str(e)))
      try:
        bstack1ll11111l1_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack1ll111_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ಼࠭"):
          status = bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ಽ") if rep.outcome.lower() == bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧಾ") else bstack1ll111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨಿ")
          reason = bstack1ll111_opy_ (u"ࠩࠪೀ")
          if status == bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪು"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack1ll111_opy_ (u"ࠫ࡮ࡴࡦࡰࠩೂ") if status == bstack1ll111_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬೃ") else bstack1ll111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬೄ")
          data = name + bstack1ll111_opy_ (u"ࠧࠡࡲࡤࡷࡸ࡫ࡤࠢࠩ೅") if status == bstack1ll111_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨೆ") else name + bstack1ll111_opy_ (u"ࠩࠣࡪࡦ࡯࡬ࡦࡦࠤࠤࠬೇ") + reason
          bstack1l11l1l11_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬೈ"), bstack1ll111_opy_ (u"ࠫࠬ೉"), bstack1ll111_opy_ (u"ࠬ࠭ೊ"), bstack1ll111_opy_ (u"࠭ࠧೋ"), level, data)
          for driver in bstack1ll111ll1l_opy_:
            if bstack1ll1lll1ll_opy_ == driver.session_id:
              driver.execute_script(bstack1l11l1l11_opy_)
      except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࠤࡨࡵ࡮ࡵࡧࡻࡸࠥ࡬࡯ࡳࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡳࡦࡵࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠫೌ").format(str(e)))
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡸࡺࡡࡵࡧࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࠡࡵࡷࡥࡹࡻࡳ࠻ࠢࡾࢁ್ࠬ").format(str(e)))
  bstack111ll11l1_opy_(item, call, rep)
def bstack1l1l1lll1l_opy_(driver, bstack1l1l11ll11_opy_, test=None):
  global bstack1ll111111_opy_
  if test != None:
    bstack11lllll1l1_opy_ = getattr(test, bstack1ll111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ೎"), None)
    bstack1ll11l11l_opy_ = getattr(test, bstack1ll111_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ೏"), None)
    PercySDK.screenshot(driver, bstack1l1l11ll11_opy_, bstack11lllll1l1_opy_=bstack11lllll1l1_opy_, bstack1ll11l11l_opy_=bstack1ll11l11l_opy_, bstack1lllll111_opy_=bstack1ll111111_opy_)
  else:
    PercySDK.screenshot(driver, bstack1l1l11ll11_opy_)
@measure(event_name=EVENTS.bstack111l11lll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11lll11l1_opy_(driver):
  if bstack11111ll1l_opy_.bstack1l1llllll1_opy_() is True or bstack11111ll1l_opy_.capturing() is True:
    return
  bstack11111ll1l_opy_.bstack1lll1l111l_opy_()
  while not bstack11111ll1l_opy_.bstack1l1llllll1_opy_():
    bstack11l111lll1_opy_ = bstack11111ll1l_opy_.bstack1l1ll1lll1_opy_()
    bstack1l1l1lll1l_opy_(driver, bstack11l111lll1_opy_)
  bstack11111ll1l_opy_.bstack1l111l111_opy_()
def bstack11ll11l1ll_opy_(sequence, driver_command, response = None, bstack1l111l11_opy_ = None, args = None):
    try:
      if sequence != bstack1ll111_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫ೐"):
        return
      if percy.bstack1l11111l_opy_() == bstack1ll111_opy_ (u"ࠧ࡬ࡡ࡭ࡵࡨࠦ೑"):
        return
      bstack11l111lll1_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡰࡦࡴࡦࡽࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ೒"), None)
      for command in bstack1ll1l11l11_opy_:
        if command == driver_command:
          with bstack1111l1ll1_opy_:
            bstack1l111ll111_opy_ = bstack1ll111ll1l_opy_.copy()
          for driver in bstack1l111ll111_opy_:
            bstack11lll11l1_opy_(driver)
      bstack11ll1111_opy_ = percy.bstack1ll1l1lll1_opy_()
      if driver_command in bstack1llll11ll1_opy_[bstack11ll1111_opy_]:
        bstack11111ll1l_opy_.bstack1l1ll1ll_opy_(bstack11l111lll1_opy_, driver_command)
    except Exception as e:
      pass
def bstack11ll11l1l1_opy_(framework_name):
  if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ೓")):
      return
  bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠ࡯ࡲࡨࡤࡩࡡ࡭࡮ࡨࡨࠬ೔"), True)
  global bstack1ll11lllll_opy_
  global bstack1l1111llll_opy_
  global bstack1llll111ll_opy_
  bstack1ll11lllll_opy_ = framework_name
  logger.info(bstack1l11l11ll_opy_.format(bstack1ll11lllll_opy_.split(bstack1ll111_opy_ (u"ࠩ࠰ࠫೕ"))[0]))
  bstack111l11111_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1l11l1ll11_opy_:
      Service.start = bstack11l1111ll1_opy_
      Service.stop = bstack1lll1lll1_opy_
      webdriver.Remote.get = bstack1ll1111111_opy_
      WebDriver.quit = bstack11lllll11l_opy_
      webdriver.Remote.__init__ = bstack1l1l1l1l1_opy_
    if not bstack1l11l1ll11_opy_:
        webdriver.Remote.__init__ = bstack1ll11l1ll1_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack1ll111lll1_opy_
    bstack1l1111llll_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1l11l1ll11_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack11l11l111_opy_
  except Exception as e:
    pass
  bstack11l1l1ll1l_opy_()
  if not bstack1l1111llll_opy_:
    bstack111111ll1_opy_(bstack1ll111_opy_ (u"ࠥࡔࡦࡩ࡫ࡢࡩࡨࡷࠥࡴ࡯ࡵࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠧೖ"), bstack11l1lllll_opy_)
  if bstack11ll1ll11l_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack1ll111_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬ೗")) and callable(getattr(RemoteConnection, bstack1ll111_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭೘"))):
        RemoteConnection._get_proxy_url = bstack1l111lll11_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack1l111lll11_opy_
    except Exception as e:
      logger.error(bstack1l111ll1_opy_.format(str(e)))
  if bstack1l1111l1ll_opy_():
    bstack1l111l1l1_opy_(CONFIG, logger)
  if (bstack1ll111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ೙") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1l11111l_opy_() == bstack1ll111_opy_ (u"ࠢࡵࡴࡸࡩࠧ೚"):
          bstack111llllll1_opy_(bstack11ll11l1ll_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1ll11ll11l_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11l11lll1l_opy_
      except Exception as e:
        logger.warn(bstack111lll111l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1ll111l1ll_opy_
      except Exception as e:
        logger.debug(bstack1llll1l11_opy_ + str(e))
    except Exception as e:
      bstack111111ll1_opy_(e, bstack111lll111l_opy_)
    Output.start_test = bstack11l1ll1l1l_opy_
    Output.end_test = bstack11l11l1l11_opy_
    TestStatus.__init__ = bstack1lll111l1_opy_
    QueueItem.__init__ = bstack1l1ll11lll_opy_
    pabot._create_items = bstack1l111llll1_opy_
    try:
      from pabot import __version__ as bstack1llll11l11_opy_
      if version.parse(bstack1llll11l11_opy_) >= version.parse(bstack1ll111_opy_ (u"ࠨ࠷࠱࠴࠳࠶ࠧ೛")):
        pabot._run = bstack11lll1lll_opy_
      elif version.parse(bstack1llll11l11_opy_) >= version.parse(bstack1ll111_opy_ (u"ࠩ࠷࠲࠷࠴࠰ࠨ೜")):
        pabot._run = bstack1lll111ll1_opy_
      elif version.parse(bstack1llll11l11_opy_) >= version.parse(bstack1ll111_opy_ (u"ࠪ࠶࠳࠷࠵࠯࠲ࠪೝ")):
        pabot._run = bstack11l111l111_opy_
      elif version.parse(bstack1llll11l11_opy_) >= version.parse(bstack1ll111_opy_ (u"ࠫ࠷࠴࠱࠴࠰࠳ࠫೞ")):
        pabot._run = bstack1l1l11l11l_opy_
      else:
        pabot._run = bstack111ll1ll_opy_
    except Exception as e:
      pabot._run = bstack111ll1ll_opy_
    pabot._create_command_for_execution = bstack11l11ll111_opy_
    pabot._report_results = bstack111llll1l1_opy_
  if bstack1ll111_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ೟") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack111111ll1_opy_(e, bstack11l1l1ll1_opy_)
    Runner.run_hook = bstack11llll1ll1_opy_
    Step.run = bstack1llll1lll_opy_
  if bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ೠ") in str(framework_name).lower():
    if not bstack1l11l1ll11_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1l1l1l11l_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1l1ll11111_opy_
      Config.getoption = bstack1l1l1ll111_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack11l1111l1_opy_
    except Exception as e:
      pass
def bstack11lll1ll_opy_():
  global CONFIG
  if bstack1ll111_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧೡ") in CONFIG and int(CONFIG[bstack1ll111_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨೢ")]) > 1:
    logger.warn(bstack1ll1111ll1_opy_)
def bstack1111l1l11_opy_(arg, bstack1l111lll1l_opy_, bstack1111ll11l_opy_=None):
  global CONFIG
  global bstack1ll1l111l_opy_
  global bstack1l11l1111l_opy_
  global bstack1l11l1ll11_opy_
  global bstack11ll11l11l_opy_
  bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩೣ")
  if bstack1l111lll1l_opy_ and isinstance(bstack1l111lll1l_opy_, str):
    bstack1l111lll1l_opy_ = eval(bstack1l111lll1l_opy_)
  CONFIG = bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠪࡇࡔࡔࡆࡊࡉࠪ೤")]
  bstack1ll1l111l_opy_ = bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠫࡍ࡛ࡂࡠࡗࡕࡐࠬ೥")]
  bstack1l11l1111l_opy_ = bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧ೦")]
  bstack1l11l1ll11_opy_ = bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩ೧")]
  bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨ೨"), bstack1l11l1ll11_opy_)
  os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ೩")] = bstack11l11ll1_opy_
  os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡒࡒࡋࡏࡇࠨ೪")] = json.dumps(CONFIG)
  os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡋ࡙ࡇࡥࡕࡓࡎࠪ೫")] = bstack1ll1l111l_opy_
  os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ೬")] = str(bstack1l11l1111l_opy_)
  os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕ࡟ࡔࡆࡕࡗࡣࡕࡒࡕࡈࡋࡑࠫ೭")] = str(True)
  if bstack11ll111ll1_opy_(arg, [bstack1ll111_opy_ (u"࠭࠭࡯ࠩ೮"), bstack1ll111_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨ೯")]) != -1:
    os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑ࡛ࡗࡉࡘ࡚࡟ࡑࡃࡕࡅࡑࡒࡅࡍࠩ೰")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1l1llll1l_opy_)
    return
  bstack1ll11111l_opy_()
  global bstack1lll11llll_opy_
  global bstack1ll111111_opy_
  global bstack1l1lllll_opy_
  global bstack1l1111l1_opy_
  global bstack1lll1l11l_opy_
  global bstack1llll111ll_opy_
  global bstack1l1lll1l11_opy_
  arg.append(bstack1ll111_opy_ (u"ࠤ࠰࡛ࠧೱ"))
  arg.append(bstack1ll111_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳࡧ࠽ࡑࡴࡪࡵ࡭ࡧࠣࡥࡱࡸࡥࡢࡦࡼࠤ࡮ࡳࡰࡰࡴࡷࡩࡩࡀࡰࡺࡶࡨࡷࡹ࠴ࡐࡺࡶࡨࡷࡹ࡝ࡡࡳࡰ࡬ࡲ࡬ࠨೲ"))
  arg.append(bstack1ll111_opy_ (u"ࠦ࠲࡝ࠢೳ"))
  arg.append(bstack1ll111_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩ࠿࡚ࡨࡦࠢ࡫ࡳࡴࡱࡩ࡮ࡲ࡯ࠦ೴"))
  global bstack1lll111111_opy_
  global bstack111llll111_opy_
  global bstack1lll111l_opy_
  global bstack1llll1l1l_opy_
  global bstack11ll11ll1l_opy_
  global bstack11l1l1l1ll_opy_
  global bstack1l11ll111l_opy_
  global bstack1111l1l1l_opy_
  global bstack1l11llllll_opy_
  global bstack11ll1l1ll1_opy_
  global bstack11l111ll11_opy_
  global bstack1lllllllll_opy_
  global bstack111ll11l1_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1lll111111_opy_ = webdriver.Remote.__init__
    bstack111llll111_opy_ = WebDriver.quit
    bstack1111l1l1l_opy_ = WebDriver.close
    bstack1l11llllll_opy_ = WebDriver.get
    bstack1lll111l_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack1l1l11lll_opy_(CONFIG) and bstack1ll1l1l1ll_opy_():
    if bstack111l111l_opy_() < version.parse(bstack11l11l11ll_opy_):
      logger.error(bstack1l1l1l11ll_opy_.format(bstack111l111l_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1ll111_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ೵")) and callable(getattr(RemoteConnection, bstack1ll111_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨ೶"))):
          bstack11ll1l1ll1_opy_ = RemoteConnection._get_proxy_url
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          bstack11ll1l1ll1_opy_ = ClientConfig.get_proxy_url
      except Exception as e:
        logger.error(bstack1l111ll1_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack11l111ll11_opy_ = Config.getoption
    from _pytest import runner
    bstack1lllllllll_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warn(e, bstack11l1l1l11l_opy_)
  try:
    from pytest_bdd import reporting
    bstack111ll11l1_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack1ll111_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩ೷"))
  bstack1l1lllll_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭೸"), {}).get(bstack1ll111_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ೹"))
  bstack1l1lll1l11_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack11llll1111_opy_():
      bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.CONNECT, bstack1llllll1l1_opy_())
    platform_index = int(os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ೺"), bstack1ll111_opy_ (u"ࠬ࠶ࠧ೻")))
  else:
    bstack11ll11l1l1_opy_(bstack1l11l11l1_opy_)
  os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧ೼")] = CONFIG[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ೽")]
  os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ೾")] = CONFIG[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ೿")]
  os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ഀ")] = bstack1l11l1ll11_opy_.__str__()
  from _pytest.config import main as bstack1ll111ll11_opy_
  bstack1ll11lll1l_opy_ = []
  try:
    exit_code = bstack1ll111ll11_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack11llll1lll_opy_()
    if bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨഁ") in multiprocessing.current_process().__dict__.keys():
      for bstack11l1ll1111_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1ll11lll1l_opy_.append(bstack11l1ll1111_opy_)
    try:
      bstack1l1l1l1l11_opy_ = (bstack1ll11lll1l_opy_, int(exit_code))
      bstack1111ll11l_opy_.append(bstack1l1l1l1l11_opy_)
    except:
      bstack1111ll11l_opy_.append((bstack1ll11lll1l_opy_, exit_code))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack1ll11lll1l_opy_.append({bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪം"): bstack1ll111_opy_ (u"࠭ࡐࡳࡱࡦࡩࡸࡹࠠࠨഃ") + os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧഄ")), bstack1ll111_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧഅ"): traceback.format_exc(), bstack1ll111_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨആ"): int(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪഇ")))})
    bstack1111ll11l_opy_.append((bstack1ll11lll1l_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack1ll111_opy_ (u"ࠦࡷ࡫ࡴࡳ࡫ࡨࡷࠧഈ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack11lll1l11_opy_ = e.__class__.__name__
    print(bstack1ll111_opy_ (u"ࠧࠫࡳ࠻ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡴࡸࡲࡳ࡯࡮ࡨࠢࡥࡩ࡭ࡧࡶࡦࠢࡷࡩࡸࡺࠠࠦࡵࠥഉ") % (bstack11lll1l11_opy_, e))
    return 1
def bstack1l111l111l_opy_(arg):
  global bstack1lllll1ll_opy_
  bstack11ll11l1l1_opy_(bstack11l11l111l_opy_)
  os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧഊ")] = str(bstack1l11l1111l_opy_)
  retries = bstack11ll1lll1l_opy_.bstack1l11l1l1ll_opy_(CONFIG)
  status_code = 0
  if bstack11ll1lll1l_opy_.bstack11ll1l11_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack11ll1ll1_opy_
    status_code = bstack11ll1ll1_opy_(arg)
  if status_code != 0:
    bstack1lllll1ll_opy_ = status_code
def bstack1ll11lll_opy_():
  logger.info(bstack1l1ll1l111_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ഋ"), help=bstack1ll111_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡦࡳࡳ࡬ࡩࡨࠩഌ"))
  parser.add_argument(bstack1ll111_opy_ (u"ࠩ࠰ࡹࠬ഍"), bstack1ll111_opy_ (u"ࠪ࠱࠲ࡻࡳࡦࡴࡱࡥࡲ࡫ࠧഎ"), help=bstack1ll111_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡷࡶࡩࡷࡴࡡ࡮ࡧࠪഏ"))
  parser.add_argument(bstack1ll111_opy_ (u"ࠬ࠳࡫ࠨഐ"), bstack1ll111_opy_ (u"࠭࠭࠮࡭ࡨࡽࠬ഑"), help=bstack1ll111_opy_ (u"࡚ࠧࡱࡸࡶࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡦࡩࡣࡦࡵࡶࠤࡰ࡫ࡹࠨഒ"))
  parser.add_argument(bstack1ll111_opy_ (u"ࠨ࠯ࡩࠫഓ"), bstack1ll111_opy_ (u"ࠩ࠰࠱࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧഔ"), help=bstack1ll111_opy_ (u"ࠪ࡝ࡴࡻࡲࠡࡶࡨࡷࡹࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩക"))
  bstack11l1l11l1_opy_ = parser.parse_args()
  try:
    bstack111l11l1_opy_ = bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱࡫ࡪࡴࡥࡳ࡫ࡦ࠲ࡾࡳ࡬࠯ࡵࡤࡱࡵࡲࡥࠨഖ")
    if bstack11l1l11l1_opy_.framework and bstack11l1l11l1_opy_.framework not in (bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬഗ"), bstack1ll111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠹ࠧഘ")):
      bstack111l11l1_opy_ = bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠰ࡼࡱࡱ࠴ࡳࡢ࡯ࡳࡰࡪ࠭ങ")
    bstack1l1l1llll1_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack111l11l1_opy_)
    bstack1ll11ll111_opy_ = open(bstack1l1l1llll1_opy_, bstack1ll111_opy_ (u"ࠨࡴࠪച"))
    bstack11l11lll1_opy_ = bstack1ll11ll111_opy_.read()
    bstack1ll11ll111_opy_.close()
    if bstack11l1l11l1_opy_.username:
      bstack11l11lll1_opy_ = bstack11l11lll1_opy_.replace(bstack1ll111_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩഛ"), bstack11l1l11l1_opy_.username)
    if bstack11l1l11l1_opy_.key:
      bstack11l11lll1_opy_ = bstack11l11lll1_opy_.replace(bstack1ll111_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬജ"), bstack11l1l11l1_opy_.key)
    if bstack11l1l11l1_opy_.framework:
      bstack11l11lll1_opy_ = bstack11l11lll1_opy_.replace(bstack1ll111_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬഝ"), bstack11l1l11l1_opy_.framework)
    file_name = bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨഞ")
    file_path = os.path.abspath(file_name)
    bstack1l11111lll_opy_ = open(file_path, bstack1ll111_opy_ (u"࠭ࡷࠨട"))
    bstack1l11111lll_opy_.write(bstack11l11lll1_opy_)
    bstack1l11111lll_opy_.close()
    logger.info(bstack111ll1l1l_opy_)
    try:
      os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩഠ")] = bstack11l1l11l1_opy_.framework if bstack11l1l11l1_opy_.framework != None else bstack1ll111_opy_ (u"ࠣࠤഡ")
      config = yaml.safe_load(bstack11l11lll1_opy_)
      config[bstack1ll111_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩഢ")] = bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠰ࡷࡪࡺࡵࡱࠩണ")
      bstack111ll111l_opy_(bstack11ll1l111l_opy_, config)
    except Exception as e:
      logger.debug(bstack1ll1l1l1l_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l1111111_opy_.format(str(e)))
def bstack111ll111l_opy_(bstack1lll1lll11_opy_, config, bstack111l1ll1l_opy_={}):
  global bstack1l11l1ll11_opy_
  global bstack11ll111l_opy_
  global bstack11ll11l11l_opy_
  if not config:
    return
  bstack1ll1111l_opy_ = bstack1lllll1l1_opy_ if not bstack1l11l1ll11_opy_ else (
    bstack11l11lll_opy_ if bstack1ll111_opy_ (u"ࠫࡦࡶࡰࠨത") in config else (
        bstack1ll1ll111_opy_ if config.get(bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩഥ")) else bstack11l11ll1ll_opy_
    )
)
  bstack11l1l11l11_opy_ = False
  bstack11l111ll_opy_ = False
  if bstack1l11l1ll11_opy_ is True:
      if bstack1ll111_opy_ (u"࠭ࡡࡱࡲࠪദ") in config:
          bstack11l1l11l11_opy_ = True
      else:
          bstack11l111ll_opy_ = True
  bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1111llll_opy_(config, bstack11ll111l_opy_)
  bstack1l1ll1111_opy_ = bstack1lll11ll_opy_()
  data = {
    bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩധ"): config[bstack1ll111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪന")],
    bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬഩ"): config[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭പ")],
    bstack1ll111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨഫ"): bstack1lll1lll11_opy_,
    bstack1ll111_opy_ (u"ࠬࡪࡥࡵࡧࡦࡸࡪࡪࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩബ"): os.environ.get(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨഭ"), bstack11ll111l_opy_),
    bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩമ"): bstack11l1lll1l_opy_,
    bstack1ll111_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮ࠪയ"): bstack1ll1l11ll_opy_(),
    bstack1ll111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬര"): {
      bstack1ll111_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨറ"): str(config[bstack1ll111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫല")]) if bstack1ll111_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬള") in config else bstack1ll111_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢഴ"),
      bstack1ll111_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࡘࡨࡶࡸ࡯࡯࡯ࠩവ"): sys.version,
      bstack1ll111_opy_ (u"ࠨࡴࡨࡪࡪࡸࡲࡦࡴࠪശ"): bstack111lll11_opy_(os.environ.get(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫഷ"), bstack11ll111l_opy_)),
      bstack1ll111_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩࠬസ"): bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫഹ"),
      bstack1ll111_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ࠭ഺ"): bstack1ll1111l_opy_,
      bstack1ll111_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺ࡟࡮ࡣࡳ഻ࠫ"): bstack1l11l111ll_opy_,
      bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡠࡷࡸ࡭ࡩ഼࠭"): os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ഽ")],
      bstack1ll111_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬാ"): os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬി"), bstack11ll111l_opy_),
      bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧീ"): bstack1ll111ll1_opy_(os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧു"), bstack11ll111l_opy_)),
      bstack1ll111_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬൂ"): bstack1l1ll1111_opy_.get(bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬൃ")),
      bstack1ll111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧൄ"): bstack1l1ll1111_opy_.get(bstack1ll111_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪ൅")),
      bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭െ"): config[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧേ")] if config[bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨൈ")] else bstack1ll111_opy_ (u"ࠨࡵ࡯࡭ࡱࡳࡼࡴࠢ൉"),
      bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩൊ"): str(config[bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪോ")]) if bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫൌ") in config else bstack1ll111_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱ്ࠦ"),
      bstack1ll111_opy_ (u"ࠫࡴࡹࠧൎ"): sys.platform,
      bstack1ll111_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧ൏"): socket.gethostname(),
      bstack1ll111_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨ൐"): bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩ൑"))
    }
  }
  if not bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡕ࡬࡫ࡳࡧ࡬ࠨ൒")) is None:
    data[bstack1ll111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ൓")][bstack1ll111_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡒ࡫ࡴࡢࡦࡤࡸࡦ࠭ൔ")] = {
      bstack1ll111_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫൕ"): bstack1ll111_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪൖ"),
      bstack1ll111_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭ൗ"): bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡏ࡮ࡲ࡬ࡔ࡫ࡪࡲࡦࡲࠧ൘")),
      bstack1ll111_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࡏࡷࡰࡦࡪࡸࠧ൙"): bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡑࡳࠬ൚"))
    }
  if bstack1lll1lll11_opy_ == bstack1lll1111_opy_:
    data[bstack1ll111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭൛")][bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡆࡳࡳ࡬ࡩࡨࠩ൜")] = bstack11lll11lll_opy_(config)
    data[bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൝")][bstack1ll111_opy_ (u"࠭ࡩࡴࡒࡨࡶࡨࡿࡁࡶࡶࡲࡉࡳࡧࡢ࡭ࡧࡧࠫ൞")] = percy.bstack1llll1111l_opy_
    data[bstack1ll111_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪൟ")][bstack1ll111_opy_ (u"ࠨࡲࡨࡶࡨࡿࡂࡶ࡫࡯ࡨࡎࡪࠧൠ")] = percy.percy_build_id
  if not bstack11ll1lll1l_opy_.bstack11l1111l11_opy_(CONFIG):
    data[bstack1ll111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬൡ")][bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠧൢ")] = bstack11ll1lll1l_opy_.bstack11l1111l11_opy_(CONFIG)
  bstack11ll1ll1ll_opy_ = bstack1ll11ll11_opy_.bstack1l11l1l1l_opy_(CONFIG, logger)
  bstack1llll1l11l_opy_ = bstack11ll1lll1l_opy_.bstack1l11l1l1l_opy_(config=CONFIG)
  if bstack11ll1ll1ll_opy_ is not None and bstack1llll1l11l_opy_ is not None and bstack1llll1l11l_opy_.bstack1l11ll1l_opy_():
    data[bstack1ll111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧൣ")][bstack1llll1l11l_opy_.bstack1ll1lllll_opy_()] = bstack11ll1ll1ll_opy_.bstack1lll11111_opy_()
  update(data[bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ൤")], bstack111l1ll1l_opy_)
  try:
    response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"࠭ࡐࡐࡕࡗࠫ൥"), bstack1lll1ll1l1_opy_(bstack111lll1l_opy_), data, {
      bstack1ll111_opy_ (u"ࠧࡢࡷࡷ࡬ࠬ൦"): (config[bstack1ll111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ൧")], config[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬ൨")])
    })
    if response:
      logger.debug(bstack1llll111l1_opy_.format(bstack1lll1lll11_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack11lll1ll1_opy_.format(str(e)))
def bstack111lll11_opy_(framework):
  return bstack1ll111_opy_ (u"ࠥࡿࢂ࠳ࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢ൩").format(str(framework), __version__) if framework else bstack1ll111_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࡾࢁࠧ൪").format(
    __version__)
def bstack1ll11111l_opy_():
  global CONFIG
  global bstack111llll11l_opy_
  if bool(CONFIG):
    return
  try:
    bstack11ll11llll_opy_()
    logger.debug(bstack1l1l1lll11_opy_.format(str(CONFIG)))
    bstack111llll11l_opy_ = bstack1llll1ll1l_opy_.configure_logger(CONFIG, bstack111llll11l_opy_)
    bstack111l11111_opy_()
  except Exception as e:
    logger.error(bstack1ll111_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࡺࡶࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࠤ൫") + str(e))
    sys.exit(1)
  sys.excepthook = bstack11lllllll1_opy_
  atexit.register(bstack11l1111ll_opy_)
  signal.signal(signal.SIGINT, bstack11lll11ll1_opy_)
  signal.signal(signal.SIGTERM, bstack11lll11ll1_opy_)
def bstack11lllllll1_opy_(exctype, value, traceback):
  global bstack1ll111ll1l_opy_
  try:
    for driver in bstack1ll111ll1l_opy_:
      bstack11ll1ll11_opy_(driver, bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭൬"), bstack1ll111_opy_ (u"ࠢࡔࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥ൭") + str(value))
  except Exception:
    pass
  logger.info(bstack11l11111l_opy_)
  bstack1ll1ll11ll_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1ll1ll11ll_opy_(message=bstack1ll111_opy_ (u"ࠨࠩ൮"), bstack1l1lll1lll_opy_ = False):
  global CONFIG
  bstack111ll1l11_opy_ = bstack1ll111_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡇࡻࡧࡪࡶࡴࡪࡱࡱࠫ൯") if bstack1l1lll1lll_opy_ else bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ൰")
  try:
    if message:
      bstack111l1ll1l_opy_ = {
        bstack111ll1l11_opy_ : str(message)
      }
      bstack111ll111l_opy_(bstack1lll1111_opy_, CONFIG, bstack111l1ll1l_opy_)
    else:
      bstack111ll111l_opy_(bstack1lll1111_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack11lllll111_opy_.format(str(e)))
def bstack11ll1ll1l_opy_(bstack1ll111l11l_opy_, size):
  bstack11ll1l1ll_opy_ = []
  while len(bstack1ll111l11l_opy_) > size:
    bstack111ll111_opy_ = bstack1ll111l11l_opy_[:size]
    bstack11ll1l1ll_opy_.append(bstack111ll111_opy_)
    bstack1ll111l11l_opy_ = bstack1ll111l11l_opy_[size:]
  bstack11ll1l1ll_opy_.append(bstack1ll111l11l_opy_)
  return bstack11ll1l1ll_opy_
def bstack1ll1l111_opy_(args):
  if bstack1ll111_opy_ (u"ࠫ࠲ࡳࠧ൱") in args and bstack1ll111_opy_ (u"ࠬࡶࡤࡣࠩ൲") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack11l11ll1l_opy_, stage=STAGE.bstack1lll11l111_opy_)
def run_on_browserstack(bstack1l1l1l11_opy_=None, bstack1111ll11l_opy_=None, bstack1lll1111l1_opy_=False):
  global CONFIG
  global bstack1ll1l111l_opy_
  global bstack1l11l1111l_opy_
  global bstack11ll111l_opy_
  global bstack11ll11l11l_opy_
  bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"࠭ࠧ൳")
  bstack11lll1l1_opy_(bstack1l1ll1111l_opy_, logger)
  if bstack1l1l1l11_opy_ and isinstance(bstack1l1l1l11_opy_, str):
    bstack1l1l1l11_opy_ = eval(bstack1l1l1l11_opy_)
  if bstack1l1l1l11_opy_:
    CONFIG = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡄࡑࡑࡊࡎࡍࠧ൴")]
    bstack1ll1l111l_opy_ = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠨࡊࡘࡆࡤ࡛ࡒࡍࠩ൵")]
    bstack1l11l1111l_opy_ = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫ൶")]
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ൷"), bstack1l11l1111l_opy_)
    bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ൸")
  bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ൹"), uuid4().__str__())
  logger.info(bstack1ll111_opy_ (u"࠭ࡓࡅࡍࠣࡶࡺࡴࠠࡴࡶࡤࡶࡹ࡫ࡤࠡࡹ࡬ࡸ࡭ࠦࡩࡥ࠼ࠣࠫൺ") + bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩൻ")));
  logger.debug(bstack1ll111_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࡀࠫർ") + bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫൽ")))
  if not bstack1lll1111l1_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1l1llll1l_opy_)
      return
    if sys.argv[1] == bstack1ll111_opy_ (u"ࠪ࠱࠲ࡼࡥࡳࡵ࡬ࡳࡳ࠭ൾ") or sys.argv[1] == bstack1ll111_opy_ (u"ࠫ࠲ࡼࠧൿ"):
      logger.info(bstack1ll111_opy_ (u"ࠬࡈࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡕࡿࡴࡩࡱࡱࠤࡘࡊࡋࠡࡸࡾࢁࠬ඀").format(__version__))
      return
    if sys.argv[1] == bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬඁ"):
      bstack1ll11lll_opy_()
      return
  args = sys.argv
  bstack1ll11111l_opy_()
  global bstack1lll11llll_opy_
  global bstack1ll1l1ll11_opy_
  global bstack1l1lll1l11_opy_
  global bstack1ll111ll_opy_
  global bstack1ll111111_opy_
  global bstack1l1lllll_opy_
  global bstack1l1111l1_opy_
  global bstack1l11ll111_opy_
  global bstack1lll1l11l_opy_
  global bstack1llll111ll_opy_
  global bstack11lllll1_opy_
  bstack1ll1l1ll11_opy_ = len(CONFIG.get(bstack1ll111_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪං"), []))
  if not bstack11l11ll1_opy_:
    if args[1] == bstack1ll111_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨඃ") or args[1] == bstack1ll111_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯࠵ࠪ඄"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪඅ")
      args = args[2:]
    elif args[1] == bstack1ll111_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪආ"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫඇ")
      args = args[2:]
    elif args[1] == bstack1ll111_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬඈ"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ඉ")
      args = args[2:]
    elif args[1] == bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩඊ"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪඋ")
      args = args[2:]
    elif args[1] == bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪඌ"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫඍ")
      args = args[2:]
    elif args[1] == bstack1ll111_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬඎ"):
      bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ඏ")
      args = args[2:]
    else:
      if not bstack1ll111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඐ") in CONFIG or str(CONFIG[bstack1ll111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫඑ")]).lower() in [bstack1ll111_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩඒ"), bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫඓ")]:
        bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫඔ")
        args = args[1:]
      elif str(CONFIG[bstack1ll111_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨඕ")]).lower() == bstack1ll111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬඖ"):
        bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭඗")
        args = args[1:]
      elif str(CONFIG[bstack1ll111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ඘")]).lower() == bstack1ll111_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඙"):
        bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩක")
        args = args[1:]
      elif str(CONFIG[bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧඛ")]).lower() == bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬග"):
        bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඝ")
        args = args[1:]
      elif str(CONFIG[bstack1ll111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඞ")]).lower() == bstack1ll111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨඟ"):
        bstack11l11ll1_opy_ = bstack1ll111_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩච")
        args = args[1:]
      else:
        os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬඡ")] = bstack11l11ll1_opy_
        bstack1ll1lll1l1_opy_(bstack1l1l1l1l1l_opy_)
  os.environ[bstack1ll111_opy_ (u"ࠫࡋࡘࡁࡎࡇ࡚ࡓࡗࡑ࡟ࡖࡕࡈࡈࠬජ")] = bstack11l11ll1_opy_
  bstack11ll111l_opy_ = bstack11l11ll1_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack1l1ll11l_opy_ = bstack1l11l1lll_opy_[bstack1ll111_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘ࠲ࡈࡄࡅࠩඣ")] if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ඤ") and bstack11l11l11l_opy_() else bstack11l11ll1_opy_
      bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.bstack11l11l1lll_opy_, bstack1l1llll1_opy_(
        sdk_version=__version__,
        path_config=bstack1l111l1ll_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack1l1ll11l_opy_,
        frameworks=[bstack1l1ll11l_opy_],
        framework_versions={
          bstack1l1ll11l_opy_: bstack1ll111ll1_opy_(bstack1ll111_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭ඥ") if bstack11l11ll1_opy_ in [bstack1ll111_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧඦ"), bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨට"), bstack1ll111_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫඨ")] else bstack11l11ll1_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࠨඩ"), None):
        CONFIG[bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢඪ")] = cli.config.get(bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣණ"), None)
    except Exception as e:
      bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.bstack11llllllll_opy_, e.__traceback__, 1)
    if bstack1l11l1111l_opy_:
      CONFIG[bstack1ll111_opy_ (u"ࠢࡢࡲࡳࠦඬ")] = cli.config[bstack1ll111_opy_ (u"ࠣࡣࡳࡴࠧත")]
      logger.info(bstack1ll1l11l1l_opy_.format(CONFIG[bstack1ll111_opy_ (u"ࠩࡤࡴࡵ࠭ථ")]))
  else:
    bstack111lll1l1_opy_.clear()
  global bstack1lllll1ll1_opy_
  global bstack1lll11l1l1_opy_
  if bstack1l1l1l11_opy_:
    try:
      bstack111ll1ll1_opy_ = datetime.datetime.now()
      os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬද")] = bstack11l11ll1_opy_
      bstack111ll111l_opy_(bstack1ll11ll1l1_opy_, CONFIG)
      cli.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼ࡶࡨࡰࡥࡴࡦࡵࡷࡣࡦࡺࡴࡦ࡯ࡳࡸࡪࡪࠢධ"), datetime.datetime.now() - bstack111ll1ll1_opy_)
    except Exception as e:
      logger.debug(bstack1l1ll111_opy_.format(str(e)))
  global bstack1lll111111_opy_
  global bstack111llll111_opy_
  global bstack11l11l1ll1_opy_
  global bstack11ll1111l1_opy_
  global bstack11ll1l1111_opy_
  global bstack1l11lllll1_opy_
  global bstack1llll1l1l_opy_
  global bstack11ll11ll1l_opy_
  global bstack1111lllll_opy_
  global bstack11l1l1l1ll_opy_
  global bstack1l11ll111l_opy_
  global bstack1111l1l1l_opy_
  global bstack1l111ll11l_opy_
  global bstack1ll1llll11_opy_
  global bstack1l11llllll_opy_
  global bstack11ll1l1ll1_opy_
  global bstack11l111ll11_opy_
  global bstack1lllllllll_opy_
  global bstack1l1l111lll_opy_
  global bstack111ll11l1_opy_
  global bstack1lll111l_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1lll111111_opy_ = webdriver.Remote.__init__
    bstack111llll111_opy_ = WebDriver.quit
    bstack1111l1l1l_opy_ = WebDriver.close
    bstack1l11llllll_opy_ = WebDriver.get
    bstack1lll111l_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1lllll1ll1_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack1ll1l11l_opy_
    bstack1lll11l1l1_opy_ = bstack1ll1l11l_opy_()
  except Exception as e:
    pass
  try:
    global bstack1lllllll1l_opy_
    from QWeb.keywords import browser
    bstack1lllllll1l_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack1l1l11lll_opy_(CONFIG) and bstack1ll1l1l1ll_opy_():
    if bstack111l111l_opy_() < version.parse(bstack11l11l11ll_opy_):
      logger.error(bstack1l1l1l11ll_opy_.format(bstack111l111l_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1ll111_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭න")) and callable(getattr(RemoteConnection, bstack1ll111_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ඲"))):
          RemoteConnection._get_proxy_url = bstack1l111lll11_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack1l111lll11_opy_
      except Exception as e:
        logger.error(bstack1l111ll1_opy_.format(str(e)))
  if not CONFIG.get(bstack1ll111_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩඳ"), False) and not bstack1l1l1l11_opy_:
    logger.info(bstack1l1llll1ll_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack1ll111_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬප") in CONFIG and str(CONFIG[bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ඵ")]).lower() != bstack1ll111_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩබ"):
      bstack1l111lllll_opy_()
    elif bstack11l11ll1_opy_ != bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫභ") or (bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬම") and not bstack1l1l1l11_opy_):
      bstack1l11l11l11_opy_()
  if (bstack11l11ll1_opy_ in [bstack1ll111_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬඹ"), bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ය"), bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩර")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1ll11ll11l_opy_
        bstack1l11lllll1_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack111lll111l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack11ll1l1111_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1llll1l11_opy_ + str(e))
    except Exception as e:
      bstack111111ll1_opy_(e, bstack111lll111l_opy_)
    if bstack11l11ll1_opy_ != bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ඼"):
      bstack11l1lllll1_opy_()
    bstack11l11l1ll1_opy_ = Output.start_test
    bstack11ll1111l1_opy_ = Output.end_test
    bstack1llll1l1l_opy_ = TestStatus.__init__
    bstack1111lllll_opy_ = pabot._run
    bstack11l1l1l1ll_opy_ = QueueItem.__init__
    bstack1l11ll111l_opy_ = pabot._create_command_for_execution
    bstack1l1l111lll_opy_ = pabot._report_results
  if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪල"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack111111ll1_opy_(e, bstack11l1l1ll1_opy_)
    bstack1l111ll11l_opy_ = Runner.run_hook
    bstack1ll1llll11_opy_ = Step.run
  if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ඾"):
    try:
      from _pytest.config import Config
      bstack11l111ll11_opy_ = Config.getoption
      from _pytest import runner
      bstack1lllllllll_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack11l1l1l11l_opy_)
    try:
      from pytest_bdd import reporting
      bstack111ll11l1_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡴࠦࡲࡶࡰࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡧࡶࡸࡸ࠭඿"))
  try:
    framework_name = bstack1ll111_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬව") if bstack11l11ll1_opy_ in [bstack1ll111_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ශ"), bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧෂ"), bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪස")] else bstack11ll1111ll_opy_(bstack11l11ll1_opy_)
    bstack11l11111l1_opy_ = {
      bstack1ll111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࠫහ"): bstack1ll111_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷ࠱ࡨࡻࡣࡶ࡯ࡥࡩࡷ࠭ළ") if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬෆ") and bstack11l11l11l_opy_() else framework_name,
      bstack1ll111_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ෇"): bstack1ll111ll1_opy_(framework_name),
      bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ෈"): __version__,
      bstack1ll111_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ෉"): bstack11l11ll1_opy_
    }
    if bstack11l11ll1_opy_ in bstack11l11ll1l1_opy_ + bstack111ll11ll_opy_:
      if bstack1llll111_opy_.bstack1lllll11l_opy_(CONFIG):
        if bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴ්ࠩ") in CONFIG:
          os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ෋")] = os.getenv(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ෌"), json.dumps(CONFIG[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬ෍")]))
          CONFIG[bstack1ll111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭෎")].pop(bstack1ll111_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬා"), None)
          CONFIG[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨැ")].pop(bstack1ll111_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧෑ"), None)
        bstack11l11111l1_opy_[bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪි")] = {
          bstack1ll111_opy_ (u"ࠫࡳࡧ࡭ࡦࠩී"): bstack1ll111_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠧු"),
          bstack1ll111_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧ෕"): str(bstack111l111l_opy_())
        }
    if bstack11l11ll1_opy_ not in [bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨූ")] and not cli.is_running():
      bstack1ll11l1l1l_opy_, bstack11111lll1_opy_ = bstack111l1l111_opy_.launch(CONFIG, bstack11l11111l1_opy_)
      if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ෗")) is not None and bstack1llll111_opy_.bstack11llll11l_opy_(CONFIG) is None:
        value = bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩෘ")].get(bstack1ll111_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫෙ"))
        if value is not None:
            CONFIG[bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫේ")] = value
        else:
          logger.debug(bstack1ll111_opy_ (u"ࠧࡔ࡯ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡦࡤࡸࡦࠦࡦࡰࡷࡱࡨࠥ࡯࡮ࠡࡴࡨࡷࡵࡵ࡮ࡴࡧࠥෛ"))
  except Exception as e:
    logger.debug(bstack1l1l1lll_opy_.format(bstack1ll111_opy_ (u"࠭ࡔࡦࡵࡷࡌࡺࡨࠧො"), str(e)))
  if bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧෝ"):
    bstack1l1lll1l11_opy_ = True
    if bstack1l1l1l11_opy_ and bstack1lll1111l1_opy_:
      bstack1l1lllll_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬෞ"), {}).get(bstack1ll111_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫෟ"))
      bstack11ll11l1l1_opy_(bstack1l11lll11_opy_)
    elif bstack1l1l1l11_opy_:
      bstack1l1lllll_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ෠"), {}).get(bstack1ll111_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭෡"))
      global bstack1ll111ll1l_opy_
      try:
        if bstack1ll1l111_opy_(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෢")]) and multiprocessing.current_process().name == bstack1ll111_opy_ (u"࠭࠰ࠨ෣"):
          bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෤")].remove(bstack1ll111_opy_ (u"ࠨ࠯ࡰࠫ෥"))
          bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෦")].remove(bstack1ll111_opy_ (u"ࠪࡴࡩࡨࠧ෧"))
          bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෨")] = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෩")][0]
          with open(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෪")], bstack1ll111_opy_ (u"ࠧࡳࠩ෫")) as f:
            bstack1l1ll1l11_opy_ = f.read()
          bstack11l1lll111_opy_ = bstack1ll111_opy_ (u"ࠣࠤࠥࡪࡷࡵ࡭ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡴࡦ࡮ࠤ࡮ࡳࡰࡰࡴࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢ࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡿ࡫࠻ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨࠬࢀࢃࠩ࠼ࠢࡩࡶࡴࡳࠠࡱࡦࡥࠤ࡮ࡳࡰࡰࡴࡷࠤࡕࡪࡢ࠼ࠢࡲ࡫ࡤࡪࡢࠡ࠿ࠣࡔࡩࡨ࠮ࡥࡱࡢࡦࡷ࡫ࡡ࡬࠽ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡤࡦࡨࠣࡱࡴࡪ࡟ࡣࡴࡨࡥࡰ࠮ࡳࡦ࡮ࡩ࠰ࠥࡧࡲࡨ࠮ࠣࡸࡪࡳࡰࡰࡴࡤࡶࡾࠦ࠽ࠡ࠲ࠬ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡸࡷࡿ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡣࡵ࡫ࠥࡃࠠࡴࡶࡵࠬ࡮ࡴࡴࠩࡣࡵ࡫࠮࠱࠱࠱ࠫࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡧࡻࡧࡪࡶࡴࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡦࡹࠠࡦ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡴࡦࡹࡳࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࡯ࡨࡡࡧࡦ࠭ࡹࡥ࡭ࡨ࠯ࡥࡷ࡭ࠬࡵࡧࡰࡴࡴࡸࡡࡳࡻࠬࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࠢࡀࠤࡲࡵࡤࡠࡤࡵࡩࡦࡱࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡔࡩࡨ࠮ࡥࡱࡢࡦࡷ࡫ࡡ࡬ࠢࡀࠤࡲࡵࡤࡠࡤࡵࡩࡦࡱࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡔࡩࡨࠨࠪ࠰ࡶࡩࡹࡥࡴࡳࡣࡦࡩ࠭࠯࡜࡯ࠤࠥࠦ෬").format(str(bstack1l1l1l11_opy_))
          bstack1ll111l11_opy_ = bstack11l1lll111_opy_ + bstack1l1ll1l11_opy_
          bstack1111ll1ll_opy_ = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෭")] + bstack1ll111_opy_ (u"ࠪࡣࡧࡹࡴࡢࡥ࡮ࡣࡹ࡫࡭ࡱ࠰ࡳࡽࠬ෮")
          with open(bstack1111ll1ll_opy_, bstack1ll111_opy_ (u"ࠫࡼ࠭෯")):
            pass
          with open(bstack1111ll1ll_opy_, bstack1ll111_opy_ (u"ࠧࡽࠫࠣ෰")) as f:
            f.write(bstack1ll111l11_opy_)
          import subprocess
          bstack1111lll1_opy_ = subprocess.run([bstack1ll111_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࠨ෱"), bstack1111ll1ll_opy_])
          if os.path.exists(bstack1111ll1ll_opy_):
            os.unlink(bstack1111ll1ll_opy_)
          os._exit(bstack1111lll1_opy_.returncode)
        else:
          if bstack1ll1l111_opy_(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪෲ")]):
            bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫෳ")].remove(bstack1ll111_opy_ (u"ࠩ࠰ࡱࠬ෴"))
            bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭෵")].remove(bstack1ll111_opy_ (u"ࠫࡵࡪࡢࠨ෶"))
            bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෷")] = bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෸")][0]
          bstack11ll11l1l1_opy_(bstack1l11lll11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ෹")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1ll111_opy_ (u"ࠨࡡࡢࡲࡦࡳࡥࡠࡡࠪ෺")] = bstack1ll111_opy_ (u"ࠩࡢࡣࡲࡧࡩ࡯ࡡࡢࠫ෻")
          mod_globals[bstack1ll111_opy_ (u"ࠪࡣࡤ࡬ࡩ࡭ࡧࡢࡣࠬ෼")] = os.path.abspath(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෽")])
          exec(open(bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ෾")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1ll111_opy_ (u"࠭ࡃࡢࡷࡪ࡬ࡹࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯࠼ࠣࡿࢂ࠭෿").format(str(e)))
          for driver in bstack1ll111ll1l_opy_:
            bstack1111ll11l_opy_.append({
              bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ฀"): bstack1l1l1l11_opy_[bstack1ll111_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫก")],
              bstack1ll111_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨข"): str(e),
              bstack1ll111_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩฃ"): multiprocessing.current_process().name
            })
            bstack11ll1ll11_opy_(driver, bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫค"), bstack1ll111_opy_ (u"࡙ࠧࡥࡴࡵ࡬ࡳࡳࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࡢ࡮ࠣฅ") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1ll111ll1l_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1l11l1111l_opy_, CONFIG, logger)
      bstack1l1ll1l1l1_opy_()
      bstack11lll1ll_opy_()
      percy.bstack1lll1llll1_opy_()
      bstack1l111lll1l_opy_ = {
        bstack1ll111_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩฆ"): args[0],
        bstack1ll111_opy_ (u"ࠧࡄࡑࡑࡊࡎࡍࠧง"): CONFIG,
        bstack1ll111_opy_ (u"ࠨࡊࡘࡆࡤ࡛ࡒࡍࠩจ"): bstack1ll1l111l_opy_,
        bstack1ll111_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫฉ"): bstack1l11l1111l_opy_
      }
      if bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ช") in CONFIG:
        bstack11ll1l11l_opy_ = bstack11llllll1_opy_(args, logger, CONFIG, bstack1l11l1ll11_opy_, bstack1ll1l1ll11_opy_)
        bstack1l11ll111_opy_ = bstack11ll1l11l_opy_.bstack11l1l11ll1_opy_(run_on_browserstack, bstack1l111lll1l_opy_, bstack1ll1l111_opy_(args))
      else:
        if bstack1ll1l111_opy_(args):
          bstack1l111lll1l_opy_[bstack1ll111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧซ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1l111lll1l_opy_,))
          test.start()
          test.join()
        else:
          bstack11ll11l1l1_opy_(bstack1l11lll11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1ll111_opy_ (u"ࠬࡥ࡟࡯ࡣࡰࡩࡤࡥࠧฌ")] = bstack1ll111_opy_ (u"࠭࡟ࡠ࡯ࡤ࡭ࡳࡥ࡟ࠨญ")
          mod_globals[bstack1ll111_opy_ (u"ࠧࡠࡡࡩ࡭ࡱ࡫࡟ࡠࠩฎ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧฏ") or bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨฐ"):
    percy.init(bstack1l11l1111l_opy_, CONFIG, logger)
    percy.bstack1lll1llll1_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack111111ll1_opy_(e, bstack111lll111l_opy_)
    bstack1l1ll1l1l1_opy_()
    bstack11ll11l1l1_opy_(bstack1llll11111_opy_)
    if bstack1l11l1ll11_opy_:
      bstack1ll1llllll_opy_(bstack1llll11111_opy_, args)
      if bstack1ll111_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨฑ") in args:
        i = args.index(bstack1ll111_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩฒ"))
        args.pop(i)
        args.pop(i)
      if bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨณ") not in CONFIG:
        CONFIG[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩด")] = [{}]
        bstack1ll1l1ll11_opy_ = 1
      if bstack1lll11llll_opy_ == 0:
        bstack1lll11llll_opy_ = 1
      args.insert(0, str(bstack1lll11llll_opy_))
      args.insert(0, str(bstack1ll111_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬต")))
    if bstack111l1l111_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack1l1l11l111_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack1l1ll11l1l_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack1ll111_opy_ (u"ࠣࡔࡒࡆࡔ࡚࡟ࡐࡒࡗࡍࡔࡔࡓࠣถ"),
        ).parse_args(bstack1l1l11l111_opy_)
        bstack111ll1lll_opy_ = args.index(bstack1l1l11l111_opy_[0]) if len(bstack1l1l11l111_opy_) > 0 else len(args)
        args.insert(bstack111ll1lll_opy_, str(bstack1ll111_opy_ (u"ࠩ࠰࠱ࡱ࡯ࡳࡵࡧࡱࡩࡷ࠭ท")))
        args.insert(bstack111ll1lll_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡶࡴࡨ࡯ࡵࡡ࡯࡭ࡸࡺࡥ࡯ࡧࡵ࠲ࡵࡿࠧธ"))))
        if bstack11ll1lll1l_opy_.bstack11ll1l11_opy_(CONFIG):
          args.insert(bstack111ll1lll_opy_, str(bstack1ll111_opy_ (u"ࠫ࠲࠳࡬ࡪࡵࡷࡩࡳ࡫ࡲࠨน")))
          args.insert(bstack111ll1lll_opy_ + 1, str(bstack1ll111_opy_ (u"ࠬࡘࡥࡵࡴࡼࡊࡦ࡯࡬ࡦࡦ࠽ࡿࢂ࠭บ").format(bstack11ll1lll1l_opy_.bstack1l11l1l1ll_opy_(CONFIG))))
        if bstack1l1l1111l1_opy_(os.environ.get(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡘࡅࡓࡗࡑࠫป"))) and str(os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࡤ࡚ࡅࡔࡖࡖࠫผ"), bstack1ll111_opy_ (u"ࠨࡰࡸࡰࡱ࠭ฝ"))) != bstack1ll111_opy_ (u"ࠩࡱࡹࡱࡲࠧพ"):
          for bstack1ll1lll11l_opy_ in bstack1l1ll11l1l_opy_:
            args.remove(bstack1ll1lll11l_opy_)
          test_files = os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࡠࡖࡈࡗ࡙࡙ࠧฟ")).split(bstack1ll111_opy_ (u"ࠫ࠱࠭ภ"))
          for bstack1l1l1l1lll_opy_ in test_files:
            args.append(bstack1l1l1l1lll_opy_)
      except Exception as e:
        logger.error(bstack1ll111_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡥࡹࡺࡡࡤࡪ࡬ࡲ࡬ࠦ࡬ࡪࡵࡷࡩࡳ࡫ࡲࠡࡨࡲࡶࠥࢁࡽ࠯ࠢࡈࡶࡷࡵࡲࠡ࠯ࠣࡿࢂࠨม").format(bstack111ll11l_opy_, e))
    pabot.main(args)
  elif bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧย"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack111111ll1_opy_(e, bstack111lll111l_opy_)
    for a in args:
      if bstack1ll111_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡐࡍࡃࡗࡊࡔࡘࡍࡊࡐࡇࡉ࡝࠭ร") in a:
        bstack1ll111111_opy_ = int(a.split(bstack1ll111_opy_ (u"ࠨ࠼ࠪฤ"))[1])
      if bstack1ll111_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡆࡈࡊࡑࡕࡃࡂࡎࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ล") in a:
        bstack1l1lllll_opy_ = str(a.split(bstack1ll111_opy_ (u"ࠪ࠾ࠬฦ"))[1])
      if bstack1ll111_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡇࡑࡏࡁࡓࡉࡖࠫว") in a:
        bstack1l1111l1_opy_ = str(a.split(bstack1ll111_opy_ (u"ࠬࡀࠧศ"))[1])
    bstack11l1l1l11_opy_ = None
    bstack111l111ll_opy_ = None
    if bstack1ll111_opy_ (u"࠭࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠬษ") in args:
      i = args.index(bstack1ll111_opy_ (u"ࠧ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽ࠭ส"))
      args.pop(i)
      bstack11l1l1l11_opy_ = args.pop(i)
    if bstack1ll111_opy_ (u"ࠨ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࠫห") in args:
      i = args.index(bstack1ll111_opy_ (u"ࠩ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠬฬ"))
      args.pop(i)
      bstack111l111ll_opy_ = args.pop(i)
    if bstack11l1l1l11_opy_ is not None:
      global bstack1111111ll_opy_
      bstack1111111ll_opy_ = bstack11l1l1l11_opy_
    if bstack111l111ll_opy_ is not None and int(bstack1ll111111_opy_) < 0:
      bstack1ll111111_opy_ = int(bstack111l111ll_opy_)
    bstack11ll11l1l1_opy_(bstack1llll11111_opy_)
    run_cli(args)
    if bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺࠧอ") in multiprocessing.current_process().__dict__.keys():
      for bstack11l1ll1111_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1111ll11l_opy_.append(bstack11l1ll1111_opy_)
  elif bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫฮ"):
    bstack1ll11111_opy_ = bstack1lll1111ll_opy_(args, logger, CONFIG, bstack1l11l1ll11_opy_)
    bstack1ll11111_opy_.bstack11l11l1ll_opy_()
    bstack1l1ll1l1l1_opy_()
    bstack1ll111ll_opy_ = True
    bstack1llll111ll_opy_ = bstack1ll11111_opy_.bstack11ll11l111_opy_()
    bstack1ll11111_opy_.bstack1l111lll1l_opy_(bstack11ll11lll_opy_)
    bstack1ll11111_opy_.bstack1ll11ll1ll_opy_()
    bstack11l11111ll_opy_(bstack11l11ll1_opy_, CONFIG, bstack1ll11111_opy_.bstack1l1llll111_opy_())
    bstack1ll111l1_opy_ = bstack1ll11111_opy_.bstack11l1l11ll1_opy_(bstack1111l1l11_opy_, {
      bstack1ll111_opy_ (u"ࠬࡎࡕࡃࡡࡘࡖࡑ࠭ฯ"): bstack1ll1l111l_opy_,
      bstack1ll111_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨะ"): bstack1l11l1111l_opy_,
      bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪั"): bstack1l11l1ll11_opy_
    })
    try:
      bstack1ll11lll1l_opy_, bstack111111l1l_opy_ = map(list, zip(*bstack1ll111l1_opy_))
      bstack1lll1l11l_opy_ = bstack1ll11lll1l_opy_[0]
      for status_code in bstack111111l1l_opy_:
        if status_code != 0:
          bstack11lllll1_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack1ll111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡧࡶࡦࠢࡨࡶࡷࡵࡲࡴࠢࡤࡲࡩࠦࡳࡵࡣࡷࡹࡸࠦࡣࡰࡦࡨ࠲ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࠼ࠣࡿࢂࠨา").format(str(e)))
  elif bstack11l11ll1_opy_ == bstack1ll111_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩำ"):
    try:
      from behave.__main__ import main as bstack11ll1ll1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack111111ll1_opy_(e, bstack11l1l1ll1_opy_)
    bstack1l1ll1l1l1_opy_()
    bstack1ll111ll_opy_ = True
    bstack111111l1_opy_ = 1
    if bstack1ll111_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪิ") in CONFIG:
      bstack111111l1_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫี")]
    if bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨึ") in CONFIG:
      bstack111l1l1l_opy_ = int(bstack111111l1_opy_) * int(len(CONFIG[bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩื")]))
    else:
      bstack111l1l1l_opy_ = int(bstack111111l1_opy_)
    config = Configuration(args)
    bstack1111l11l_opy_ = config.paths
    if len(bstack1111l11l_opy_) == 0:
      import glob
      pattern = bstack1ll111_opy_ (u"ࠧࠫࠬ࠲࠮࠳࡬ࡥࡢࡶࡸࡶࡪุ࠭")
      bstack1l1l11111l_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1l1l11111l_opy_)
      config = Configuration(args)
      bstack1111l11l_opy_ = config.paths
    bstack1l11l1l111_opy_ = [os.path.normpath(item) for item in bstack1111l11l_opy_]
    bstack1l111ll11_opy_ = [os.path.normpath(item) for item in args]
    bstack1l1l1l1ll1_opy_ = [item for item in bstack1l111ll11_opy_ if item not in bstack1l11l1l111_opy_]
    import platform as pf
    if pf.system().lower() == bstack1ll111_opy_ (u"ࠨࡹ࡬ࡲࡩࡵࡷࡴูࠩ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l11l1l111_opy_ = [str(PurePosixPath(PureWindowsPath(bstack1llll1l1ll_opy_)))
                    for bstack1llll1l1ll_opy_ in bstack1l11l1l111_opy_]
    bstack11lll1llll_opy_ = []
    for spec in bstack1l11l1l111_opy_:
      bstack1l1llll1l1_opy_ = []
      bstack1l1llll1l1_opy_ += bstack1l1l1l1ll1_opy_
      bstack1l1llll1l1_opy_.append(spec)
      bstack11lll1llll_opy_.append(bstack1l1llll1l1_opy_)
    execution_items = []
    for bstack1l1llll1l1_opy_ in bstack11lll1llll_opy_:
      if bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷฺࠬ") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭฻")]):
          item = {}
          item[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࠨ฼")] = bstack1ll111_opy_ (u"ࠬࠦࠧ฽").join(bstack1l1llll1l1_opy_)
          item[bstack1ll111_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬ฾")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack1ll111_opy_ (u"ࠧࡢࡴࡪࠫ฿")] = bstack1ll111_opy_ (u"ࠨࠢࠪเ").join(bstack1l1llll1l1_opy_)
        item[bstack1ll111_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨแ")] = 0
        execution_items.append(item)
    bstack111lllll1_opy_ = bstack11ll1ll1l_opy_(execution_items, bstack111l1l1l_opy_)
    for execution_item in bstack111lllll1_opy_:
      bstack1l11lll1ll_opy_ = []
      for item in execution_item:
        bstack1l11lll1ll_opy_.append(bstack1llll11l1_opy_(name=str(item[bstack1ll111_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩโ")]),
                                             target=bstack1l111l111l_opy_,
                                             args=(item[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࠨใ")],)))
      for t in bstack1l11lll1ll_opy_:
        t.start()
      for t in bstack1l11lll1ll_opy_:
        t.join()
  else:
    bstack1ll1lll1l1_opy_(bstack1l1l1l1l1l_opy_)
  if not bstack1l1l1l11_opy_:
    bstack1ll1l1llll_opy_()
    if(bstack11l11ll1_opy_ in [bstack1ll111_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬไ"), bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ๅ")]):
      bstack1111l1111_opy_()
  bstack1llll1ll1l_opy_.bstack1l1ll11ll_opy_()
def browserstack_initialize(bstack1l1ll1ll11_opy_=None):
  logger.info(bstack1ll111_opy_ (u"ࠧࡓࡷࡱࡲ࡮ࡴࡧࠡࡕࡇࡏࠥࡽࡩࡵࡪࠣࡥࡷ࡭ࡳ࠻ࠢࠪๆ") + str(bstack1l1ll1ll11_opy_))
  run_on_browserstack(bstack1l1ll1ll11_opy_, None, True)
@measure(event_name=EVENTS.bstack1ll1ll11_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1l1llll_opy_():
  global CONFIG
  global bstack11ll111l_opy_
  global bstack11lllll1_opy_
  global bstack1lllll1ll_opy_
  global bstack11ll11l11l_opy_
  bstack1ll1llll_opy_.bstack1l1l11l11_opy_()
  if cli.is_running():
    bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.bstack11ll11ll_opy_)
  else:
    bstack1llll1l11l_opy_ = bstack11ll1lll1l_opy_.bstack1l11l1l1l_opy_(config=CONFIG)
    bstack1llll1l11l_opy_.bstack11ll1lll_opy_(CONFIG)
  if bstack11ll111l_opy_ == bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ็"):
    if not cli.is_enabled(CONFIG):
      bstack111l1l111_opy_.stop()
  else:
    bstack111l1l111_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack1llll1111_opy_.bstack1lllll1111_opy_()
  if bstack1ll111_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ่࠭") in CONFIG and str(CONFIG[bstack1ll111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫้ࠧ")]).lower() != bstack1ll111_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧ๊ࠪ"):
    hashed_id, bstack11l1l1lll_opy_ = bstack11111llll_opy_()
  else:
    hashed_id, bstack11l1l1lll_opy_ = get_build_link()
  bstack1llllllll_opy_(hashed_id)
  logger.info(bstack1ll111_opy_ (u"࡙ࠬࡄࡌࠢࡵࡹࡳࠦࡥ࡯ࡦࡨࡨࠥ࡬࡯ࡳࠢ࡬ࡨ࠿๋࠭") + bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨ์"), bstack1ll111_opy_ (u"ࠧࠨํ")) + bstack1ll111_opy_ (u"ࠨ࠮ࠣࡸࡪࡹࡴࡩࡷࡥࠤ࡮ࡪ࠺ࠡࠩ๎") + os.getenv(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ๏"), bstack1ll111_opy_ (u"ࠪࠫ๐")))
  if hashed_id is not None and bstack1lll11lll_opy_() != -1:
    sessions = bstack11l11l11_opy_(hashed_id)
    bstack1l11l1ll1l_opy_(sessions, bstack11l1l1lll_opy_)
  if bstack11ll111l_opy_ == bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ๑") and bstack11lllll1_opy_ != 0:
    sys.exit(bstack11lllll1_opy_)
  if bstack11ll111l_opy_ == bstack1ll111_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ๒") and bstack1lllll1ll_opy_ != 0:
    sys.exit(bstack1lllll1ll_opy_)
def bstack1llllllll_opy_(new_id):
    global bstack11l1lll1l_opy_
    bstack11l1lll1l_opy_ = new_id
def bstack11ll1111ll_opy_(bstack11ll1111l_opy_):
  if bstack11ll1111l_opy_:
    return bstack11ll1111l_opy_.capitalize()
  else:
    return bstack1ll111_opy_ (u"࠭ࠧ๓")
@measure(event_name=EVENTS.bstack1l1lll1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1l11llll_opy_(bstack1l1l11111_opy_):
  if bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ๔") in bstack1l1l11111_opy_ and bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭๕")] != bstack1ll111_opy_ (u"ࠩࠪ๖"):
    return bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨ๗")]
  else:
    bstack1l1lll11_opy_ = bstack1ll111_opy_ (u"ࠦࠧ๘")
    if bstack1ll111_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ๙") in bstack1l1l11111_opy_ and bstack1l1l11111_opy_[bstack1ll111_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭๚")] != None:
      bstack1l1lll11_opy_ += bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ๛")] + bstack1ll111_opy_ (u"ࠣ࠮ࠣࠦ๜")
      if bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠩࡲࡷࠬ๝")] == bstack1ll111_opy_ (u"ࠥ࡭ࡴࡹࠢ๞"):
        bstack1l1lll11_opy_ += bstack1ll111_opy_ (u"ࠦ࡮ࡕࡓࠡࠤ๟")
      bstack1l1lll11_opy_ += (bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ๠")] or bstack1ll111_opy_ (u"࠭ࠧ๡"))
      return bstack1l1lll11_opy_
    else:
      bstack1l1lll11_opy_ += bstack11ll1111ll_opy_(bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ๢")]) + bstack1ll111_opy_ (u"ࠣࠢࠥ๣") + (
              bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫ๤")] or bstack1ll111_opy_ (u"ࠪࠫ๥")) + bstack1ll111_opy_ (u"ࠦ࠱ࠦࠢ๦")
      if bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠬࡵࡳࠨ๧")] == bstack1ll111_opy_ (u"ࠨࡗࡪࡰࡧࡳࡼࡹࠢ๨"):
        bstack1l1lll11_opy_ += bstack1ll111_opy_ (u"ࠢࡘ࡫ࡱࠤࠧ๩")
      bstack1l1lll11_opy_ += bstack1l1l11111_opy_[bstack1ll111_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ๪")] or bstack1ll111_opy_ (u"ࠩࠪ๫")
      return bstack1l1lll11_opy_
@measure(event_name=EVENTS.bstack1l1ll1l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1l1l11l_opy_(bstack11l1l11ll_opy_):
  if bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠥࡨࡴࡴࡥࠣ๬"):
    return bstack1ll111_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡧࡳࡧࡨࡲࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡧࡳࡧࡨࡲࠧࡄࡃࡰ࡯ࡳࡰࡪࡺࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ๭")
  elif bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧ๮"):
    return bstack1ll111_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡴࡨࡨࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡲࡦࡦࠥࡂࡋࡧࡩ࡭ࡧࡧࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩ๯")
  elif bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢ๰"):
    return bstack1ll111_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽࡫ࡷ࡫ࡥ࡯࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥ࡫ࡷ࡫ࡥ࡯ࠤࡁࡔࡦࡹࡳࡦࡦ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ๱")
  elif bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ๲"):
    return bstack1ll111_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࡸࡥࡥ࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡶࡪࡪࠢ࠿ࡇࡵࡶࡴࡸ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ๳")
  elif bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࠧ๴"):
    return bstack1ll111_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࠤࡧࡨࡥ࠸࠸࠶࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࠦࡩࡪࡧ࠳࠳࠸ࠥࡂ࡙࡯࡭ࡦࡱࡸࡸࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪ๵")
  elif bstack11l1l11ll_opy_ == bstack1ll111_opy_ (u"ࠨࡲࡶࡰࡱ࡭ࡳ࡭ࠢ๶"):
    return bstack1ll111_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡥࡰࡦࡩ࡫࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡥࡰࡦࡩ࡫ࠣࡀࡕࡹࡳࡴࡩ࡯ࡩ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ๷")
  else:
    return bstack1ll111_opy_ (u"ࠨ࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࡧࡲࡡࡤ࡭࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡧࡲࡡࡤ࡭ࠥࡂࠬ๸") + bstack11ll1111ll_opy_(
      bstack11l1l11ll_opy_) + bstack1ll111_opy_ (u"ࠩ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ๹")
def bstack1lll1ll1_opy_(session):
  return bstack1ll111_opy_ (u"ࠪࡀࡹࡸࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡳࡱࡺࠦࡃࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠠࡴࡧࡶࡷ࡮ࡵ࡮࠮ࡰࡤࡱࡪࠨ࠾࠽ࡣࠣ࡬ࡷ࡫ࡦ࠾ࠤࡾࢁࠧࠦࡴࡢࡴࡪࡩࡹࡃࠢࡠࡤ࡯ࡥࡳࡱࠢ࠿ࡽࢀࡀ࠴ࡧ࠾࠽࠱ࡷࡨࡃࢁࡽࡼࡿ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࡄࡻࡾ࠾࠲ࡸࡩࡄ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨ࠾ࡼࡿ࠿࠳ࡹࡪ࠾࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁ࠵ࡴࡳࡀࠪ๺").format(
    session[bstack1ll111_opy_ (u"ࠫࡵࡻࡢ࡭࡫ࡦࡣࡺࡸ࡬ࠨ๻")], bstack1l1l11llll_opy_(session), bstack1ll1l1l11l_opy_(session[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡸࡺࡡࡵࡷࡶࠫ๼")]),
    bstack1ll1l1l11l_opy_(session[bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭๽")]),
    bstack11ll1111ll_opy_(session[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ๾")] or session[bstack1ll111_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ๿")] or bstack1ll111_opy_ (u"ࠩࠪ຀")) + bstack1ll111_opy_ (u"ࠥࠤࠧກ") + (session[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ຂ")] or bstack1ll111_opy_ (u"ࠬ࠭຃")),
    session[bstack1ll111_opy_ (u"࠭࡯ࡴࠩຄ")] + bstack1ll111_opy_ (u"ࠢࠡࠤ຅") + session[bstack1ll111_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬຆ")], session[bstack1ll111_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫງ")] or bstack1ll111_opy_ (u"ࠪࠫຈ"),
    session[bstack1ll111_opy_ (u"ࠫࡨࡸࡥࡢࡶࡨࡨࡤࡧࡴࠨຉ")] if session[bstack1ll111_opy_ (u"ࠬࡩࡲࡦࡣࡷࡩࡩࡥࡡࡵࠩຊ")] else bstack1ll111_opy_ (u"࠭ࠧ຋"))
@measure(event_name=EVENTS.bstack1llllll1ll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l11l1ll1l_opy_(sessions, bstack11l1l1lll_opy_):
  try:
    bstack1lll11l1ll_opy_ = bstack1ll111_opy_ (u"ࠢࠣຌ")
    if not os.path.exists(bstack1l111111l_opy_):
      os.mkdir(bstack1l111111l_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1ll111_opy_ (u"ࠨࡣࡶࡷࡪࡺࡳ࠰ࡴࡨࡴࡴࡸࡴ࠯ࡪࡷࡱࡱ࠭ຍ")), bstack1ll111_opy_ (u"ࠩࡵࠫຎ")) as f:
      bstack1lll11l1ll_opy_ = f.read()
    bstack1lll11l1ll_opy_ = bstack1lll11l1ll_opy_.replace(bstack1ll111_opy_ (u"ࠪࡿࠪࡘࡅࡔࡗࡏࡘࡘࡥࡃࡐࡗࡑࡘࠪࢃࠧຏ"), str(len(sessions)))
    bstack1lll11l1ll_opy_ = bstack1lll11l1ll_opy_.replace(bstack1ll111_opy_ (u"ࠫࢀࠫࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠧࢀࠫຐ"), bstack11l1l1lll_opy_)
    bstack1lll11l1ll_opy_ = bstack1lll11l1ll_opy_.replace(bstack1ll111_opy_ (u"ࠬࢁࠥࡃࡗࡌࡐࡉࡥࡎࡂࡏࡈࠩࢂ࠭ຑ"),
                                              sessions[0].get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤࡴࡡ࡮ࡧࠪຒ")) if sessions[0] else bstack1ll111_opy_ (u"ࠧࠨຓ"))
    with open(os.path.join(bstack1l111111l_opy_, bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡳࡧࡳࡳࡷࡺ࠮ࡩࡶࡰࡰࠬດ")), bstack1ll111_opy_ (u"ࠩࡺࠫຕ")) as stream:
      stream.write(bstack1lll11l1ll_opy_.split(bstack1ll111_opy_ (u"ࠪࡿ࡙ࠪࡅࡔࡕࡌࡓࡓ࡙࡟ࡅࡃࡗࡅࠪࢃࠧຖ"))[0])
      for session in sessions:
        stream.write(bstack1lll1ll1_opy_(session))
      stream.write(bstack1lll11l1ll_opy_.split(bstack1ll111_opy_ (u"ࠫࢀࠫࡓࡆࡕࡖࡍࡔࡔࡓࡠࡆࡄࡘࡆࠫࡽࠨທ"))[1])
    logger.info(bstack1ll111_opy_ (u"ࠬࡍࡥ࡯ࡧࡵࡥࡹ࡫ࡤࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡣࡷ࡬ࡰࡩࠦࡡࡳࡶ࡬ࡪࡦࡩࡴࡴࠢࡤࡸࠥࢁࡽࠨຘ").format(bstack1l111111l_opy_));
  except Exception as e:
    logger.debug(bstack1ll11llll1_opy_.format(str(e)))
def bstack11l11l11_opy_(hashed_id):
  global CONFIG
  try:
    bstack111ll1ll1_opy_ = datetime.datetime.now()
    host = bstack1ll111_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡢࡲ࡬࠱ࡨࡲ࡯ࡶࡦ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭ນ") if bstack1ll111_opy_ (u"ࠧࡢࡲࡳࠫບ") in CONFIG else bstack1ll111_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩປ")
    user = CONFIG[bstack1ll111_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫຜ")]
    key = CONFIG[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ຝ")]
    bstack1l11l11l1l_opy_ = bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧࠪພ") if bstack1ll111_opy_ (u"ࠬࡧࡰࡱࠩຟ") in CONFIG else (bstack1ll111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪຠ") if CONFIG.get(bstack1ll111_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫມ")) else bstack1ll111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪຢ"))
    host = bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠤࡤࡴ࡮ࡹࠢຣ"), bstack1ll111_opy_ (u"ࠥࡥࡵࡶࡁࡶࡶࡲࡱࡦࡺࡥࠣ຤"), bstack1ll111_opy_ (u"ࠦࡦࡶࡩࠣລ")], host) if bstack1ll111_opy_ (u"ࠬࡧࡰࡱࠩ຦") in CONFIG else bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠨࡡࡱ࡫ࡶࠦວ"), bstack1ll111_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡦࠤຨ"), bstack1ll111_opy_ (u"ࠣࡣࡳ࡭ࠧຩ")], host)
    url = bstack1ll111_opy_ (u"ࠩࡾࢁ࠴ࢁࡽ࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡸ࡫ࡳࡴ࡫ࡲࡲࡸ࠴ࡪࡴࡱࡱࠫສ").format(host, bstack1l11l11l1l_opy_, hashed_id)
    headers = {
      bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩຫ"): bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧຬ"),
    }
    proxies = bstack1l1l1ll11l_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies, auth=(user, key))
    if response.json():
      cli.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࡫ࡪࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࡡ࡯࡭ࡸࡺࠢອ"), datetime.datetime.now() - bstack111ll1ll1_opy_)
      return list(map(lambda session: session[bstack1ll111_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࠫຮ")], response.json()))
  except Exception as e:
    logger.debug(bstack11l1ll1ll_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack1lll1ll11l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def get_build_link():
  global CONFIG
  global bstack11l1lll1l_opy_
  try:
    if bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪຯ") in CONFIG:
      bstack111ll1ll1_opy_ = datetime.datetime.now()
      host = bstack1ll111_opy_ (u"ࠨࡣࡳ࡭࠲ࡩ࡬ࡰࡷࡧࠫະ") if bstack1ll111_opy_ (u"ࠩࡤࡴࡵ࠭ັ") in CONFIG else bstack1ll111_opy_ (u"ࠪࡥࡵ࡯ࠧາ")
      user = CONFIG[bstack1ll111_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ຳ")]
      key = CONFIG[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨິ")]
      bstack1l11l11l1l_opy_ = bstack1ll111_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩࠬີ") if bstack1ll111_opy_ (u"ࠧࡢࡲࡳࠫຶ") in CONFIG else bstack1ll111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧࠪື")
      url = bstack1ll111_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡿࢂࡀࡻࡾࡂࡾࢁ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡽࢀ࠳ࡧࡻࡩ࡭ࡦࡶ࠲࡯ࡹ࡯࡯ຸࠩ").format(user, key, host, bstack1l11l11l1l_opy_)
      if cli.is_enabled(CONFIG):
        bstack11l1l1lll_opy_, hashed_id = cli.bstack1ll1l1l11_opy_()
        logger.info(bstack111lll1lll_opy_.format(bstack11l1l1lll_opy_))
        return [hashed_id, bstack11l1l1lll_opy_]
      else:
        headers = {
          bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦູࠩ"): bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴ຺ࠧ"),
        }
        if bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧົ") in CONFIG:
          params = {bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫຼ"): CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪຽ")], bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ຾"): CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ຿")]}
        else:
          params = {bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨເ"): CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧແ")]}
        proxies = bstack1l1l1ll11l_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack1llllll111_opy_ = response.json()[0][bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡥࡹ࡮ࡲࡤࠨໂ")]
          if bstack1llllll111_opy_:
            bstack11l1l1lll_opy_ = bstack1llllll111_opy_[bstack1ll111_opy_ (u"࠭ࡰࡶࡤ࡯࡭ࡨࡥࡵࡳ࡮ࠪໃ")].split(bstack1ll111_opy_ (u"ࠧࡱࡷࡥࡰ࡮ࡩ࠭ࡣࡷ࡬ࡰࡩ࠭ໄ"))[0] + bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡳ࠰ࠩ໅") + bstack1llllll111_opy_[
              bstack1ll111_opy_ (u"ࠩ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬໆ")]
            logger.info(bstack111lll1lll_opy_.format(bstack11l1l1lll_opy_))
            bstack11l1lll1l_opy_ = bstack1llllll111_opy_[bstack1ll111_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭໇")]
            bstack1l11ll1ll_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫່ࠧ")]
            if bstack1ll111_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸ້ࠧ") in CONFIG:
              bstack1l11ll1ll_opy_ += bstack1ll111_opy_ (u"࠭ࠠࠨ໊") + CONFIG[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ໋ࠩ")]
            if bstack1l11ll1ll_opy_ != bstack1llllll111_opy_[bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭໌")]:
              logger.debug(bstack1l1ll11ll1_opy_.format(bstack1llllll111_opy_[bstack1ll111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧໍ")], bstack1l11ll1ll_opy_))
            cli.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻ࡩࡨࡸࡤࡨࡵࡪ࡮ࡧࡣࡱ࡯࡮࡬ࠤ໎"), datetime.datetime.now() - bstack111ll1ll1_opy_)
            return [bstack1llllll111_opy_[bstack1ll111_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ໏")], bstack11l1l1lll_opy_]
    else:
      logger.warn(bstack1l11l1lll1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l111l1_opy_.format(str(e)))
  return [None, None]
def bstack1lll1l111_opy_(url, bstack1ll11ll1l_opy_=False):
  global CONFIG
  global bstack1l1ll11l1_opy_
  if not bstack1l1ll11l1_opy_:
    hostname = bstack1ll1111l11_opy_(url)
    is_private = bstack1l1lll111_opy_(hostname)
    if (bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ໐") in CONFIG and not bstack1l1l1111l1_opy_(CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ໑")])) and (is_private or bstack1ll11ll1l_opy_):
      bstack1l1ll11l1_opy_ = hostname
def bstack1ll1111l11_opy_(url):
  return urlparse(url).hostname
def bstack1l1lll111_opy_(hostname):
  for bstack1ll11l111l_opy_ in bstack1l1l1l1ll_opy_:
    regex = re.compile(bstack1ll11l111l_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack1l1111ll_opy_(bstack11l1lll1_opy_):
  return True if bstack11l1lll1_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack11ll11l1_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack1ll111111_opy_
  bstack111l1l1l1_opy_ = not (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໒"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໓"), None))
  bstack1111l111_opy_ = getattr(driver, bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ໔"), None) != True
  bstack11l1l111_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ໕"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭໖"), None)
  if bstack11l1l111_opy_:
    if not bstack11l1l111l1_opy_():
      logger.warning(bstack1ll111_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡰࡱࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳ࠯ࠤ໗"))
      return {}
    logger.debug(bstack1ll111_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪ໘"))
    logger.debug(perform_scan(driver, driver_command=bstack1ll111_opy_ (u"ࠧࡦࡺࡨࡧࡺࡺࡥࡔࡥࡵ࡭ࡵࡺࠧ໙")))
    results = bstack1l111llll_opy_(bstack1ll111_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡴࠤ໚"))
    if results is not None and results.get(bstack1ll111_opy_ (u"ࠤ࡬ࡷࡸࡻࡥࡴࠤ໛")) is not None:
        return results[bstack1ll111_opy_ (u"ࠥ࡭ࡸࡹࡵࡦࡵࠥໜ")]
    logger.error(bstack1ll111_opy_ (u"ࠦࡓࡵࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡓࡧࡶࡹࡱࡺࡳࠡࡹࡨࡶࡪࠦࡦࡰࡷࡱࡨ࠳ࠨໝ"))
    return []
  if not bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1ll111111_opy_) or (bstack1111l111_opy_ and bstack111l1l1l1_opy_):
    logger.warning(bstack1ll111_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹ࠮ࠣໞ"))
    return {}
  try:
    logger.debug(bstack1ll111_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪໟ"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack111llll1ll_opy_.bstack11lll111l_opy_)
    return results
  except Exception:
    logger.error(bstack1ll111_opy_ (u"ࠢࡏࡱࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡼ࡫ࡲࡦࠢࡩࡳࡺࡴࡤ࠯ࠤ໠"))
    return {}
@measure(event_name=EVENTS.bstack111lllllll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack1ll111111_opy_
  bstack111l1l1l1_opy_ = not (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ໡"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ໢"), None))
  bstack1111l111_opy_ = getattr(driver, bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ໣"), None) != True
  bstack11l1l111_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫ࡮ࡹࡁࡱࡲࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໤"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໥"), None)
  if bstack11l1l111_opy_:
    if not bstack11l1l111l1_opy_():
      logger.warning(bstack1ll111_opy_ (u"ࠨࡎࡰࡶࠣࡥࡳࠦࡁࡱࡲࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠭ࠢࡦࡥࡳࡴ࡯ࡵࠢࡵࡩࡹࡸࡩࡦࡸࡨࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡶࡹࡲࡳࡡࡳࡻ࠱ࠦ໦"))
      return {}
    logger.debug(bstack1ll111_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡸࡻ࡭࡮ࡣࡵࡽࠬ໧"))
    logger.debug(perform_scan(driver, driver_command=bstack1ll111_opy_ (u"ࠨࡧࡻࡩࡨࡻࡴࡦࡕࡦࡶ࡮ࡶࡴࠨ໨")))
    results = bstack1l111llll_opy_(bstack1ll111_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡕࡸࡱࡲࡧࡲࡺࠤ໩"))
    if results is not None and results.get(bstack1ll111_opy_ (u"ࠥࡷࡺࡳ࡭ࡢࡴࡼࠦ໪")) is not None:
        return results[bstack1ll111_opy_ (u"ࠦࡸࡻ࡭࡮ࡣࡵࡽࠧ໫")]
    logger.error(bstack1ll111_opy_ (u"ࠧࡔ࡯ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡔࡨࡷࡺࡲࡴࡴࠢࡖࡹࡲࡳࡡࡳࡻࠣࡻࡦࡹࠠࡧࡱࡸࡲࡩ࠴ࠢ໬"))
    return {}
  if not bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1ll111111_opy_) or (bstack1111l111_opy_ and bstack111l1l1l1_opy_):
    logger.warning(bstack1ll111_opy_ (u"ࠨࡎࡰࡶࠣࡥࡳࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥࡩࡡ࡯ࡰࡲࡸࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺ࠰ࠥ໭"))
    return {}
  try:
    logger.debug(bstack1ll111_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡶࡪࡹࡵ࡭ࡶࡶࠤࡸࡻ࡭࡮ࡣࡵࡽࠬ໮"))
    logger.debug(perform_scan(driver))
    bstack11l111ll1l_opy_ = driver.execute_async_script(bstack111llll1ll_opy_.bstack1l11l11lll_opy_)
    return bstack11l111ll1l_opy_
  except Exception:
    logger.error(bstack1ll111_opy_ (u"ࠣࡐࡲࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡸࡻ࡭࡮ࡣࡵࡽࠥࡽࡡࡴࠢࡩࡳࡺࡴࡤ࠯ࠤ໯"))
    return {}
def bstack11l1l111l1_opy_():
  global CONFIG
  global bstack1ll111111_opy_
  bstack1lllllll1_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໰"), None) and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໱"), None)
  if not bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1ll111111_opy_) or not bstack1lllllll1_opy_:
        logger.warning(bstack1ll111_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡤࡣࡱࡲࡴࡺࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡵࡩࡸࡻ࡬ࡵࡵ࠱ࠦ໲"))
        return False
  return True
def bstack1l111llll_opy_(bstack11l11l1l1_opy_):
    bstack1l1lll1l_opy_ = bstack111l1l111_opy_.current_test_uuid() if bstack111l1l111_opy_.current_test_uuid() else bstack1llll1111_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack1l1llllll_opy_(bstack1l1lll1l_opy_, bstack11l11l1l1_opy_))
        try:
            return future.result(timeout=bstack1lll1ll11_opy_)
        except TimeoutError:
            logger.error(bstack1ll111_opy_ (u"࡚ࠧࡩ࡮ࡧࡲࡹࡹࠦࡡࡧࡶࡨࡶࠥࢁࡽࡴࠢࡺ࡬࡮ࡲࡥࠡࡨࡨࡸࡨ࡮ࡩ࡯ࡩࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡖࡪࡹࡵ࡭ࡶࡶࠦ໳").format(bstack1lll1ll11_opy_))
        except Exception as ex:
            logger.debug(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡸࡥࡵࡴ࡬ࡩࡻ࡯࡮ࡨࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡿࢂ࠴ࠠࡆࡴࡵࡳࡷࠦ࠭ࠡࡽࢀࠦ໴").format(bstack11l11l1l1_opy_, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack1lllll11ll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack1ll111111_opy_
  bstack111l1l1l1_opy_ = not (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ໵"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ໶"), None))
  bstack11lll1ll1l_opy_ = not (bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ໷"), None) and bstack11111l1l1_opy_(
          threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ໸"), None))
  bstack1111l111_opy_ = getattr(driver, bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫ໹"), None) != True
  if not bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1ll111111_opy_) or (bstack1111l111_opy_ and bstack111l1l1l1_opy_ and bstack11lll1ll1l_opy_):
    logger.warning(bstack1ll111_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷࡻ࡮ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳ࠴ࠢ໺"))
    return {}
  try:
    bstack1lll1l11l1_opy_ = bstack1ll111_opy_ (u"࠭ࡡࡱࡲࠪ໻") in CONFIG and CONFIG.get(bstack1ll111_opy_ (u"ࠧࡢࡲࡳࠫ໼"), bstack1ll111_opy_ (u"ࠨࠩ໽"))
    session_id = getattr(driver, bstack1ll111_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩ࠭໾"), None)
    if not session_id:
      logger.warning(bstack1ll111_opy_ (u"ࠥࡒࡴࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡊࡆࠣࡪࡴࡻ࡮ࡥࠢࡩࡳࡷࠦࡤࡳ࡫ࡹࡩࡷࠨ໿"))
      return {bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥༀ"): bstack1ll111_opy_ (u"ࠧࡔ࡯ࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡌࡈࠥ࡬࡯ࡶࡰࡧࠦ༁")}
    if bstack1lll1l11l1_opy_:
      try:
        bstack1ll1ll11l_opy_ = {
              bstack1ll111_opy_ (u"࠭ࡴࡩࡌࡺࡸ࡙ࡵ࡫ࡦࡰࠪ༂"): os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ༃"), os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ༄"), bstack1ll111_opy_ (u"ࠩࠪ༅"))),
              bstack1ll111_opy_ (u"ࠪࡸ࡭࡚ࡥࡴࡶࡕࡹࡳ࡛ࡵࡪࡦࠪ༆"): bstack111l1l111_opy_.current_test_uuid() if bstack111l1l111_opy_.current_test_uuid() else bstack1llll1111_opy_.current_hook_uuid(),
              bstack1ll111_opy_ (u"ࠫࡦࡻࡴࡩࡊࡨࡥࡩ࡫ࡲࠨ༇"): os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ༈")),
              bstack1ll111_opy_ (u"࠭ࡳࡤࡣࡱࡘ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭༉"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack1ll111_opy_ (u"ࠧࡵࡪࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬ༊"): os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭་"), bstack1ll111_opy_ (u"ࠩࠪ༌")),
              bstack1ll111_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࠪ།"): kwargs.get(bstack1ll111_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࡣࡨࡵ࡭࡮ࡣࡱࡨࠬ༎"), None) or bstack1ll111_opy_ (u"ࠬ࠭༏")
          }
        if not hasattr(thread_local, bstack1ll111_opy_ (u"࠭ࡢࡢࡵࡨࡣࡦࡶࡰࡠࡣ࠴࠵ࡾࡥࡳࡤࡴ࡬ࡴࡹ࠭༐")):
            scripts = {bstack1ll111_opy_ (u"ࠧࡴࡥࡤࡲࠬ༑"): bstack111llll1ll_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack1ll111111l_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack1ll111111l_opy_[bstack1ll111_opy_ (u"ࠨࡵࡦࡥࡳ࠭༒")] = bstack1ll111111l_opy_[bstack1ll111_opy_ (u"ࠩࡶࡧࡦࡴࠧ༓")] % json.dumps(bstack1ll1ll11l_opy_)
        bstack111llll1ll_opy_.bstack1l1111l1l_opy_(bstack1ll111111l_opy_)
        bstack111llll1ll_opy_.store()
        bstack1lll11ll1l_opy_ = driver.execute_script(bstack111llll1ll_opy_.perform_scan)
      except Exception as bstack11llll111l_opy_:
        logger.info(bstack1ll111_opy_ (u"ࠥࡅࡵࡶࡩࡶ࡯ࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡨࡧ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢࠥ༔") + str(bstack11llll111l_opy_))
        bstack1lll11ll1l_opy_ = {bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥ༕"): str(bstack11llll111l_opy_)}
    else:
      bstack1lll11ll1l_opy_ = driver.execute_async_script(bstack111llll1ll_opy_.perform_scan, {bstack1ll111_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬ༖"): kwargs.get(bstack1ll111_opy_ (u"࠭ࡤࡳ࡫ࡹࡩࡷࡥࡣࡰ࡯ࡰࡥࡳࡪࠧ༗"), None) or bstack1ll111_opy_ (u"ࠧࠨ༘")})
    return bstack1lll11ll1l_opy_
  except Exception as err:
    logger.error(bstack1ll111_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡷࡻ࡮ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳ࠴ࠠࡼࡿ༙ࠥ").format(str(err)))
    return {}