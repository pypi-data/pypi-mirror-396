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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack1l1l111111_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1111l11ll_opy_ import bstack1lll1ll1l1_opy_
class bstack11lllll11_opy_:
  working_dir = os.getcwd()
  bstack11l111l1_opy_ = False
  config = {}
  bstack111l1ll1l11_opy_ = bstack1ll111_opy_ (u"࠭ࠧὀ")
  binary_path = bstack1ll111_opy_ (u"ࠧࠨὁ")
  bstack11111l111l1_opy_ = bstack1ll111_opy_ (u"ࠨࠩὂ")
  bstack11111ll1l_opy_ = False
  bstack111111l1l11_opy_ = None
  bstack11111l1lll1_opy_ = {}
  bstack111111l1l1l_opy_ = 300
  bstack1lllllllll1l_opy_ = False
  logger = None
  bstack11111l111ll_opy_ = False
  bstack1llll1111l_opy_ = False
  percy_build_id = None
  bstack1lllllllll11_opy_ = bstack1ll111_opy_ (u"ࠩࠪὃ")
  bstack111111111l1_opy_ = {
    bstack1ll111_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪὄ") : 1,
    bstack1ll111_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬὅ") : 2,
    bstack1ll111_opy_ (u"ࠬ࡫ࡤࡨࡧࠪ὆") : 3,
    bstack1ll111_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠭὇") : 4
  }
  def __init__(self) -> None: pass
  def bstack11111ll1ll1_opy_(self):
    bstack11111ll1l1l_opy_ = bstack1ll111_opy_ (u"ࠧࠨὈ")
    bstack1111111ll1l_opy_ = sys.platform
    bstack1111111llll_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧὉ")
    if re.match(bstack1ll111_opy_ (u"ࠤࡧࡥࡷࡽࡩ࡯ࡾࡰࡥࡨࠦ࡯ࡴࠤὊ"), bstack1111111ll1l_opy_) != None:
      bstack11111ll1l1l_opy_ = bstack11l1l111111_opy_ + bstack1ll111_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠰ࡳࡸࡾ࠮ࡻ࡫ࡳࠦὋ")
      self.bstack1lllllllll11_opy_ = bstack1ll111_opy_ (u"ࠫࡲࡧࡣࠨὌ")
    elif re.match(bstack1ll111_opy_ (u"ࠧࡳࡳࡸ࡫ࡱࢀࡲࡹࡹࡴࡾࡰ࡭ࡳ࡭ࡷࡽࡥࡼ࡫ࡼ࡯࡮ࡽࡤࡦࡧࡼ࡯࡮ࡽࡹ࡬ࡲࡨ࡫ࡼࡦ࡯ࡦࢀࡼ࡯࡮࠴࠴ࠥὍ"), bstack1111111ll1l_opy_) != None:
      bstack11111ll1l1l_opy_ = bstack11l1l111111_opy_ + bstack1ll111_opy_ (u"ࠨ࠯ࡱࡧࡵࡧࡾ࠳ࡷࡪࡰ࠱ࡾ࡮ࡶࠢ὎")
      bstack1111111llll_opy_ = bstack1ll111_opy_ (u"ࠢࡱࡧࡵࡧࡾ࠴ࡥࡹࡧࠥ὏")
      self.bstack1lllllllll11_opy_ = bstack1ll111_opy_ (u"ࠨࡹ࡬ࡲࠬὐ")
    else:
      bstack11111ll1l1l_opy_ = bstack11l1l111111_opy_ + bstack1ll111_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠯࡯࡭ࡳࡻࡸ࠯ࡼ࡬ࡴࠧὑ")
      self.bstack1lllllllll11_opy_ = bstack1ll111_opy_ (u"ࠪࡰ࡮ࡴࡵࡹࠩὒ")
    return bstack11111ll1l1l_opy_, bstack1111111llll_opy_
  def bstack1111111lll1_opy_(self):
    try:
      bstack111111ll1l1_opy_ = [os.path.join(expanduser(bstack1ll111_opy_ (u"ࠦࢃࠨὓ")), bstack1ll111_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬὔ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack111111ll1l1_opy_:
        if(self.bstack11111l11l11_opy_(path)):
          return path
      raise bstack1ll111_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥὕ")
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪ࡮ࡴࡤࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨࠤࡵࡧࡴࡩࠢࡩࡳࡷࠦࡰࡦࡴࡦࡽࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࠲ࠦࡻࡾࠤὖ").format(e))
  def bstack11111l11l11_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack11111111ll1_opy_(self, bstack11111l1ll1l_opy_):
    return os.path.join(bstack11111l1ll1l_opy_, self.bstack111l1ll1l11_opy_ + bstack1ll111_opy_ (u"ࠣ࠰ࡨࡸࡦ࡭ࠢὗ"))
  def bstack111111ll111_opy_(self, bstack11111l1ll1l_opy_, bstack111111l1111_opy_):
    if not bstack111111l1111_opy_: return
    try:
      bstack111111lll1l_opy_ = self.bstack11111111ll1_opy_(bstack11111l1ll1l_opy_)
      with open(bstack111111lll1l_opy_, bstack1ll111_opy_ (u"ࠤࡺࠦ὘")) as f:
        f.write(bstack111111l1111_opy_)
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡗࡦࡼࡥࡥࠢࡱࡩࡼࠦࡅࡕࡣࡪࠤ࡫ࡵࡲࠡࡲࡨࡶࡨࡿࠢὙ"))
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡣࡹࡩࠥࡺࡨࡦࠢࡨࡸࡦ࡭ࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠦ὚").format(e))
  def bstack1llllllllll1_opy_(self, bstack11111l1ll1l_opy_):
    try:
      bstack111111lll1l_opy_ = self.bstack11111111ll1_opy_(bstack11111l1ll1l_opy_)
      if os.path.exists(bstack111111lll1l_opy_):
        with open(bstack111111lll1l_opy_, bstack1ll111_opy_ (u"ࠧࡸࠢὛ")) as f:
          bstack111111l1111_opy_ = f.read().strip()
          return bstack111111l1111_opy_ if bstack111111l1111_opy_ else None
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡆࡖࡤ࡫࠱ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤ὜").format(e))
  def bstack11111lll111_opy_(self, bstack11111l1ll1l_opy_, bstack11111ll1l1l_opy_):
    bstack111111l11ll_opy_ = self.bstack1llllllllll1_opy_(bstack11111l1ll1l_opy_)
    if bstack111111l11ll_opy_:
      try:
        bstack11111l11lll_opy_ = self.bstack11111llll11_opy_(bstack111111l11ll_opy_, bstack11111ll1l1l_opy_)
        if not bstack11111l11lll_opy_:
          self.logger.debug(bstack1ll111_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡩࡴࠢࡸࡴࠥࡺ࡯ࠡࡦࡤࡸࡪࠦࠨࡆࡖࡤ࡫ࠥࡻ࡮ࡤࡪࡤࡲ࡬࡫ࡤࠪࠤὝ"))
          return True
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡐࡨࡻࠥࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡶࡲࡧࡥࡹ࡫ࠢ὞"))
        return False
      except Exception as e:
        self.logger.warn(bstack1ll111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡩࡨࡦࡥ࡮ࠤ࡫ࡵࡲࠡࡤ࡬ࡲࡦࡸࡹࠡࡷࡳࡨࡦࡺࡥࡴ࠮ࠣࡹࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡧ࡯࡮ࡢࡴࡼ࠾ࠥࢁࡽࠣὟ").format(e))
    return False
  def bstack11111llll11_opy_(self, bstack111111l11ll_opy_, bstack11111ll1l1l_opy_):
    try:
      headers = {
        bstack1ll111_opy_ (u"ࠥࡍ࡫࠳ࡎࡰࡰࡨ࠱ࡒࡧࡴࡤࡪࠥὠ"): bstack111111l11ll_opy_
      }
      response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠫࡌࡋࡔࠨὡ"), bstack11111ll1l1l_opy_, {}, {bstack1ll111_opy_ (u"ࠧ࡮ࡥࡢࡦࡨࡶࡸࠨὢ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡩࡨࡦࡥ࡮࡭ࡳ࡭ࠠࡧࡱࡵࠤࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡹࡵࡪࡡࡵࡧࡶ࠾ࠥࢁࡽࠣὣ").format(e))
  @measure(event_name=EVENTS.bstack11l1l1llll1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
  def bstack111111111ll_opy_(self, bstack11111ll1l1l_opy_, bstack1111111llll_opy_):
    try:
      bstack11111l1l1l1_opy_ = self.bstack1111111lll1_opy_()
      bstack111111ll1ll_opy_ = os.path.join(bstack11111l1l1l1_opy_, bstack1ll111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠴ࡺࡪࡲࠪὤ"))
      bstack1111111l1l1_opy_ = os.path.join(bstack11111l1l1l1_opy_, bstack1111111llll_opy_)
      if self.bstack11111lll111_opy_(bstack11111l1l1l1_opy_, bstack11111ll1l1l_opy_): # if bstack1llllllll1ll_opy_, bstack1l11lll111l_opy_ bstack111111l1111_opy_ is bstack1111111l11l_opy_ to bstack111llll1l1l_opy_ version available (response 304)
        if os.path.exists(bstack1111111l1l1_opy_):
          self.logger.info(bstack1ll111_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡱࡸࡲࡩࠦࡩ࡯ࠢࡾࢁ࠱ࠦࡳ࡬࡫ࡳࡴ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥὥ").format(bstack1111111l1l1_opy_))
          return bstack1111111l1l1_opy_
        if os.path.exists(bstack111111ll1ll_opy_):
          self.logger.info(bstack1ll111_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡼ࡬ࡴࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡼࡿ࠯ࠤࡺࡴࡺࡪࡲࡳ࡭ࡳ࡭ࠢὦ").format(bstack111111ll1ll_opy_))
          return self.bstack11111lll1l1_opy_(bstack111111ll1ll_opy_, bstack1111111llll_opy_)
      self.logger.info(bstack1ll111_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡧࡴࡲࡱࠥࢁࡽࠣὧ").format(bstack11111ll1l1l_opy_))
      response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠫࡌࡋࡔࠨὨ"), bstack11111ll1l1l_opy_, {}, {})
      if response.status_code == 200:
        bstack11111ll11ll_opy_ = response.headers.get(bstack1ll111_opy_ (u"ࠧࡋࡔࡢࡩࠥὩ"), bstack1ll111_opy_ (u"ࠨࠢὪ"))
        if bstack11111ll11ll_opy_:
          self.bstack111111ll111_opy_(bstack11111l1l1l1_opy_, bstack11111ll11ll_opy_)
        with open(bstack111111ll1ll_opy_, bstack1ll111_opy_ (u"ࠧࡸࡤࠪὫ")) as file:
          file.write(response.content)
        self.logger.info(bstack1ll111_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤࡦࡴࡤࠡࡵࡤࡺࡪࡪࠠࡢࡶࠣࡿࢂࠨὬ").format(bstack111111ll1ll_opy_))
        return self.bstack11111lll1l1_opy_(bstack111111ll1ll_opy_, bstack1111111llll_opy_)
      else:
        raise(bstack1ll111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡵࡪࡨࠤ࡫࡯࡬ࡦ࠰ࠣࡗࡹࡧࡴࡶࡵࠣࡧࡴࡪࡥ࠻ࠢࡾࢁࠧὭ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿ࠺ࠡࡽࢀࠦὮ").format(e))
  def bstack11111111l11_opy_(self, bstack11111ll1l1l_opy_, bstack1111111llll_opy_):
    try:
      retry = 2
      bstack1111111l1l1_opy_ = None
      bstack11111lll1ll_opy_ = False
      while retry > 0:
        bstack1111111l1l1_opy_ = self.bstack111111111ll_opy_(bstack11111ll1l1l_opy_, bstack1111111llll_opy_)
        bstack11111lll1ll_opy_ = self.bstack1llllllll1l1_opy_(bstack11111ll1l1l_opy_, bstack1111111llll_opy_, bstack1111111l1l1_opy_)
        if bstack11111lll1ll_opy_:
          break
        retry -= 1
      return bstack1111111l1l1_opy_, bstack11111lll1ll_opy_
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡨࡧࡷࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡴࡦࡺࡨࠣὯ").format(e))
    return bstack1111111l1l1_opy_, False
  def bstack1llllllll1l1_opy_(self, bstack11111ll1l1l_opy_, bstack1111111llll_opy_, bstack1111111l1l1_opy_, bstack11111l1llll_opy_ = 0):
    if bstack11111l1llll_opy_ > 1:
      return False
    if bstack1111111l1l1_opy_ == None or os.path.exists(bstack1111111l1l1_opy_) == False:
      self.logger.warn(bstack1ll111_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡵࡧࡴࡩࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨ࠱ࠦࡲࡦࡶࡵࡽ࡮ࡴࡧࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠥὰ"))
      return False
    bstack11111111l1l_opy_ = bstack1ll111_opy_ (u"ࡸࠢ࡟࠰࠭ࡄࡵ࡫ࡲࡤࡻ࠲ࡧࡱ࡯ࠠ࡝ࡦ࠮ࡠ࠳ࡢࡤࠬ࡞࠱ࡠࡩ࠱ࠢά")
    command = bstack1ll111_opy_ (u"ࠧࡼࡿࠣ࠱࠲ࡼࡥࡳࡵ࡬ࡳࡳ࠭ὲ").format(bstack1111111l1l1_opy_)
    bstack1111111111l_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack11111111l1l_opy_, bstack1111111111l_opy_) != None:
      return True
    else:
      self.logger.error(bstack1ll111_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡥ࡫ࡩࡨࡱࠠࡧࡣ࡬ࡰࡪࡪࠢέ"))
      return False
  def bstack11111lll1l1_opy_(self, bstack111111ll1ll_opy_, bstack1111111llll_opy_):
    try:
      working_dir = os.path.dirname(bstack111111ll1ll_opy_)
      shutil.unpack_archive(bstack111111ll1ll_opy_, working_dir)
      bstack1111111l1l1_opy_ = os.path.join(working_dir, bstack1111111llll_opy_)
      os.chmod(bstack1111111l1l1_opy_, 0o755)
      return bstack1111111l1l1_opy_
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡻ࡮ࡻ࡫ࡳࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠥὴ"))
  def bstack11111111lll_opy_(self):
    try:
      bstack11111lll11l_opy_ = self.config.get(bstack1ll111_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩή"))
      bstack11111111lll_opy_ = bstack11111lll11l_opy_ or (bstack11111lll11l_opy_ is None and self.bstack11l111l1_opy_)
      if not bstack11111111lll_opy_ or self.config.get(bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧὶ"), None) not in bstack11l11llll1l_opy_:
        return False
      self.bstack11111ll1l_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡩࡴࠡࡲࡨࡶࡨࡿࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢί").format(e))
  def bstack1111111l111_opy_(self):
    try:
      bstack1111111l111_opy_ = self.percy_capture_mode
      return bstack1111111l111_opy_
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡩࡹ࡫ࡣࡵࠢࡳࡩࡷࡩࡹࠡࡥࡤࡴࡹࡻࡲࡦࠢࡰࡳࡩ࡫ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢὸ").format(e))
  def init(self, bstack11l111l1_opy_, config, logger):
    self.bstack11l111l1_opy_ = bstack11l111l1_opy_
    self.config = config
    self.logger = logger
    if not self.bstack11111111lll_opy_():
      return
    self.bstack11111l1lll1_opy_ = config.get(bstack1ll111_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ό"), {})
    self.percy_capture_mode = config.get(bstack1ll111_opy_ (u"ࠨࡲࡨࡶࡨࡿࡃࡢࡲࡷࡹࡷ࡫ࡍࡰࡦࡨࠫὺ"))
    try:
      bstack11111ll1l1l_opy_, bstack1111111llll_opy_ = self.bstack11111ll1ll1_opy_()
      self.bstack111l1ll1l11_opy_ = bstack1111111llll_opy_
      bstack1111111l1l1_opy_, bstack11111lll1ll_opy_ = self.bstack11111111l11_opy_(bstack11111ll1l1l_opy_, bstack1111111llll_opy_)
      if bstack11111lll1ll_opy_:
        self.binary_path = bstack1111111l1l1_opy_
        thread = Thread(target=self.bstack111111ll11l_opy_)
        thread.start()
      else:
        self.bstack11111l111ll_opy_ = True
        self.logger.error(bstack1ll111_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡴࡪࡸࡣࡺࠢࡳࡥࡹ࡮ࠠࡧࡱࡸࡲࡩࠦ࠭ࠡࡽࢀ࠰࡛ࠥ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡑࡧࡵࡧࡾࠨύ").format(bstack1111111l1l1_opy_))
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦὼ").format(e))
  def bstack11111ll11l1_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack1ll111_opy_ (u"ࠫࡱࡵࡧࠨώ"), bstack1ll111_opy_ (u"ࠬࡶࡥࡳࡥࡼ࠲ࡱࡵࡧࠨ὾"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack1ll111_opy_ (u"ࠨࡐࡶࡵ࡫࡭ࡳ࡭ࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࡶࠤࡦࡺࠠࡼࡿࠥ὿").format(logfile))
      self.bstack11111l111l1_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡪࡺࠠࡱࡧࡵࡧࡾࠦ࡬ࡰࡩࠣࡴࡦࡺࡨ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᾀ").format(e))
  @measure(event_name=EVENTS.bstack11l1ll11111_opy_, stage=STAGE.bstack11ll1lll1_opy_)
  def bstack111111ll11l_opy_(self):
    bstack11111l11111_opy_ = self.bstack11111l1l11l_opy_()
    if bstack11111l11111_opy_ == None:
      self.bstack11111l111ll_opy_ = True
      self.logger.error(bstack1ll111_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡵࡱ࡮ࡩࡳࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡶࡥࡳࡥࡼࠦᾁ"))
      return False
    bstack111111llll1_opy_ = [bstack1ll111_opy_ (u"ࠤࡤࡴࡵࡀࡥࡹࡧࡦ࠾ࡸࡺࡡࡳࡶࠥᾂ") if self.bstack11l111l1_opy_ else bstack1ll111_opy_ (u"ࠪࡩࡽ࡫ࡣ࠻ࡵࡷࡥࡷࡺࠧᾃ")]
    bstack111l1l111l1_opy_ = self.bstack11111l1l1ll_opy_()
    if bstack111l1l111l1_opy_ != None:
      bstack111111llll1_opy_.append(bstack1ll111_opy_ (u"ࠦ࠲ࡩࠠࡼࡿࠥᾄ").format(bstack111l1l111l1_opy_))
    env = os.environ.copy()
    env[bstack1ll111_opy_ (u"ࠧࡖࡅࡓࡅ࡜ࡣ࡙ࡕࡋࡆࡐࠥᾅ")] = bstack11111l11111_opy_
    env[bstack1ll111_opy_ (u"ࠨࡔࡉࡡࡅ࡙ࡎࡒࡄࡠࡗࡘࡍࡉࠨᾆ")] = os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᾇ"), bstack1ll111_opy_ (u"ࠨࠩᾈ"))
    bstack111111lllll_opy_ = [self.binary_path]
    self.bstack11111ll11l1_opy_()
    self.bstack111111l1l11_opy_ = self.bstack1111111ll11_opy_(bstack111111lllll_opy_ + bstack111111llll1_opy_, env)
    self.logger.debug(bstack1ll111_opy_ (u"ࠤࡖࡸࡦࡸࡴࡪࡰࡪࠤࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠥᾉ"))
    bstack11111l1llll_opy_ = 0
    while self.bstack111111l1l11_opy_.poll() == None:
      bstack111111l1lll_opy_ = self.bstack11111l1111l_opy_()
      if bstack111111l1lll_opy_:
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠢࡶࡹࡨࡩࡥࡴࡵࡩࡹࡱࠨᾊ"))
        self.bstack1lllllllll1l_opy_ = True
        return True
      bstack11111l1llll_opy_ += 1
      self.logger.debug(bstack1ll111_opy_ (u"ࠦࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡖࡪࡺࡲࡺࠢ࠰ࠤࢀࢃࠢᾋ").format(bstack11111l1llll_opy_))
      time.sleep(2)
    self.logger.error(bstack1ll111_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡱࡧࡵࡧࡾ࠲ࠠࡉࡧࡤࡰࡹ࡮ࠠࡄࡪࡨࡧࡰࠦࡆࡢ࡫࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࢁࡽࠡࡣࡷࡸࡪࡳࡰࡵࡵࠥᾌ").format(bstack11111l1llll_opy_))
    self.bstack11111l111ll_opy_ = True
    return False
  def bstack11111l1111l_opy_(self, bstack11111l1llll_opy_ = 0):
    if bstack11111l1llll_opy_ > 10:
      return False
    try:
      bstack11111ll1l11_opy_ = os.environ.get(bstack1ll111_opy_ (u"࠭ࡐࡆࡔࡆ࡝ࡤ࡙ࡅࡓࡘࡈࡖࡤࡇࡄࡅࡔࡈࡗࡘ࠭ᾍ"), bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶ࠽࠹࠸࠹࠸ࠨᾎ"))
      bstack1lllllllllll_opy_ = bstack11111ll1l11_opy_ + bstack11l1l111lll_opy_
      response = requests.get(bstack1lllllllllll_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧᾏ"), {}).get(bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬᾐ"), None)
      return True
    except:
      self.logger.debug(bstack1ll111_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡲࡧࡨࡻࡲࡳࡧࡧࠤࡼ࡮ࡩ࡭ࡧࠣࡴࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡰࡹ࡮ࠠࡤࡪࡨࡧࡰࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣᾑ"))
      return False
  def bstack11111l1l11l_opy_(self):
    bstack11111l1l111_opy_ = bstack1ll111_opy_ (u"ࠫࡦࡶࡰࠨᾒ") if self.bstack11l111l1_opy_ else bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᾓ")
    bstack111111l11l1_opy_ = bstack1ll111_opy_ (u"ࠨࡵ࡯ࡦࡨࡪ࡮ࡴࡥࡥࠤᾔ") if self.config.get(bstack1ll111_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᾕ")) is None else True
    bstack11l1llll111_opy_ = bstack1ll111_opy_ (u"ࠣࡣࡳ࡭࠴ࡧࡰࡱࡡࡳࡩࡷࡩࡹ࠰ࡩࡨࡸࡤࡶࡲࡰ࡬ࡨࡧࡹࡥࡴࡰ࡭ࡨࡲࡄࡴࡡ࡮ࡧࡀࡿࢂࠬࡴࡺࡲࡨࡁࢀࢃࠦࡱࡧࡵࡧࡾࡃࡻࡾࠤᾖ").format(self.config[bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᾗ")], bstack11111l1l111_opy_, bstack111111l11l1_opy_)
    if self.percy_capture_mode:
      bstack11l1llll111_opy_ += bstack1ll111_opy_ (u"ࠥࠪࡵ࡫ࡲࡤࡻࡢࡧࡦࡶࡴࡶࡴࡨࡣࡲࡵࡤࡦ࠿ࡾࢁࠧᾘ").format(self.percy_capture_mode)
    uri = bstack1lll1ll1l1_opy_(bstack11l1llll111_opy_)
    try:
      response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠫࡌࡋࡔࠨᾙ"), uri, {}, {bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡪࠪᾚ"): (self.config[bstack1ll111_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᾛ")], self.config[bstack1ll111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᾜ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack11111ll1l_opy_ = data.get(bstack1ll111_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᾝ"))
        self.percy_capture_mode = data.get(bstack1ll111_opy_ (u"ࠩࡳࡩࡷࡩࡹࡠࡥࡤࡴࡹࡻࡲࡦࡡࡰࡳࡩ࡫ࠧᾞ"))
        os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨᾟ")] = str(self.bstack11111ll1l_opy_)
        os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨᾠ")] = str(self.percy_capture_mode)
        if bstack111111l11l1_opy_ == bstack1ll111_opy_ (u"ࠧࡻ࡮ࡥࡧࡩ࡭ࡳ࡫ࡤࠣᾡ") and str(self.bstack11111ll1l_opy_).lower() == bstack1ll111_opy_ (u"ࠨࡴࡳࡷࡨࠦᾢ"):
          self.bstack1llll1111l_opy_ = True
        if bstack1ll111_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨᾣ") in data:
          return data[bstack1ll111_opy_ (u"ࠣࡶࡲ࡯ࡪࡴࠢᾤ")]
        else:
          raise bstack1ll111_opy_ (u"ࠩࡗࡳࡰ࡫࡮ࠡࡐࡲࡸࠥࡌ࡯ࡶࡰࡧࠤ࠲ࠦࡻࡾࠩᾥ").format(data)
      else:
        raise bstack1ll111_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡶࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡳࡵࡣࡷࡹࡸࠦ࠭ࠡࡽࢀ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡃࡱࡧࡽࠥ࠳ࠠࡼࡿࠥᾦ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡵࡸ࡯࡫ࡧࡦࡸࠧᾧ").format(e))
  def bstack11111l1l1ll_opy_(self):
    bstack11111l11ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠧࡶࡥࡳࡥࡼࡇࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠣᾨ"))
    try:
      if bstack1ll111_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᾩ") not in self.bstack11111l1lll1_opy_:
        self.bstack11111l1lll1_opy_[bstack1ll111_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᾪ")] = 2
      with open(bstack11111l11ll1_opy_, bstack1ll111_opy_ (u"ࠨࡹࠪᾫ")) as fp:
        json.dump(self.bstack11111l1lll1_opy_, fp)
      return bstack11111l11ll1_opy_
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡩࡲࡦࡣࡷࡩࠥࡶࡥࡳࡥࡼࠤࡨࡵ࡮ࡧ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᾬ").format(e))
  def bstack1111111ll11_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack1lllllllll11_opy_ == bstack1ll111_opy_ (u"ࠪࡻ࡮ࡴࠧᾭ"):
        bstack11111ll1111_opy_ = [bstack1ll111_opy_ (u"ࠫࡨࡳࡤ࠯ࡧࡻࡩࠬᾮ"), bstack1ll111_opy_ (u"ࠬ࠵ࡣࠨᾯ")]
        cmd = bstack11111ll1111_opy_ + cmd
      cmd = bstack1ll111_opy_ (u"࠭ࠠࠨᾰ").join(cmd)
      self.logger.debug(bstack1ll111_opy_ (u"ࠢࡓࡷࡱࡲ࡮ࡴࡧࠡࡽࢀࠦᾱ").format(cmd))
      with open(self.bstack11111l111l1_opy_, bstack1ll111_opy_ (u"ࠣࡣࠥᾲ")) as bstack11111ll111l_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11111ll111l_opy_, text=True, stderr=bstack11111ll111l_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack11111l111ll_opy_ = True
      self.logger.error(bstack1ll111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠣࡻ࡮ࡺࡨࠡࡥࡰࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦᾳ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack1lllllllll1l_opy_:
        self.logger.info(bstack1ll111_opy_ (u"ࠥࡗࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡖࡥࡳࡥࡼࠦᾴ"))
        cmd = [self.binary_path, bstack1ll111_opy_ (u"ࠦࡪࡾࡥࡤ࠼ࡶࡸࡴࡶࠢ᾵")]
        self.bstack1111111ll11_opy_(cmd)
        self.bstack1lllllllll1l_opy_ = False
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡳࡵࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡸ࡫ࡷ࡬ࠥࡩ࡯࡮࡯ࡤࡲࡩࠦ࠭ࠡࡽࢀ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧᾶ").format(cmd, e))
  def bstack1lll1llll1_opy_(self):
    if not self.bstack11111ll1l_opy_:
      return
    try:
      bstack111111l111l_opy_ = 0
      while not self.bstack1lllllllll1l_opy_ and bstack111111l111l_opy_ < self.bstack111111l1l1l_opy_:
        if self.bstack11111l111ll_opy_:
          self.logger.info(bstack1ll111_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡹࡥࡵࡷࡳࠤ࡫ࡧࡩ࡭ࡧࡧࠦᾷ"))
          return
        time.sleep(1)
        bstack111111l111l_opy_ += 1
      os.environ[bstack1ll111_opy_ (u"ࠧࡑࡇࡕࡇ࡞ࡥࡂࡆࡕࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒ࠭Ᾰ")] = str(self.bstack11111ll1lll_opy_())
      self.logger.info(bstack1ll111_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡴࡧࡷࡹࡵࠦࡣࡰ࡯ࡳࡰࡪࡺࡥࡥࠤᾹ"))
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡥࡵࡷࡳࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥᾺ").format(e))
  def bstack11111ll1lll_opy_(self):
    if self.bstack11l111l1_opy_:
      return
    try:
      bstack11111111111_opy_ = [platform[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨΆ")].lower() for platform in self.config.get(bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᾼ"), [])]
      bstack1111111l1ll_opy_ = sys.maxsize
      bstack11111l1ll11_opy_ = bstack1ll111_opy_ (u"ࠬ࠭᾽")
      for browser in bstack11111111111_opy_:
        if browser in self.bstack111111111l1_opy_:
          bstack111111lll11_opy_ = self.bstack111111111l1_opy_[browser]
        if bstack111111lll11_opy_ < bstack1111111l1ll_opy_:
          bstack1111111l1ll_opy_ = bstack111111lll11_opy_
          bstack11111l1ll11_opy_ = browser
      return bstack11111l1ll11_opy_
    except Exception as e:
      self.logger.error(bstack1ll111_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡣࡧࡶࡸࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢι").format(e))
  @classmethod
  def bstack1l11111l_opy_(self):
    return os.getenv(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬ᾿"), bstack1ll111_opy_ (u"ࠨࡈࡤࡰࡸ࡫ࠧ῀")).lower()
  @classmethod
  def bstack1ll1l1lll1_opy_(self):
    return os.getenv(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟࡟ࡄࡃࡓࡘ࡚ࡘࡅࡠࡏࡒࡈࡊ࠭῁"), bstack1ll111_opy_ (u"ࠪࠫῂ"))
  @classmethod
  def bstack1l1l1111l1l_opy_(cls, value):
    cls.bstack1llll1111l_opy_ = value
  @classmethod
  def bstack11111l11l1l_opy_(cls):
    return cls.bstack1llll1111l_opy_
  @classmethod
  def bstack1l1l111l111_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack111111l1ll1_opy_(cls):
    return cls.percy_build_id