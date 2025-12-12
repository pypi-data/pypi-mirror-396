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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l111l11_opy_, bstack11l1ll111ll_opy_, bstack11l1l111l1l_opy_
import tempfile
import json
bstack111l111ll11_opy_ = os.getenv(bstack1ll111_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡋࡤࡌࡉࡍࡇࠥḖ"), None) or os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠧḗ"))
bstack111l11ll111_opy_ = os.path.join(bstack1ll111_opy_ (u"ࠦࡱࡵࡧࠣḘ"), bstack1ll111_opy_ (u"ࠬࡹࡤ࡬࠯ࡦࡰ࡮࠳ࡤࡦࡤࡸ࡫࠳ࡲ࡯ࡨࠩḙ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1ll111_opy_ (u"࠭ࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩḚ"),
      datefmt=bstack1ll111_opy_ (u"࡛ࠧࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࡞ࠬḛ"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1l111lll_opy_():
  bstack111l11l1111_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡅࡇࡅ࡙ࡌࠨḜ"), bstack1ll111_opy_ (u"ࠤࡩࡥࡱࡹࡥࠣḝ"))
  return logging.DEBUG if bstack111l11l1111_opy_.lower() == bstack1ll111_opy_ (u"ࠥࡸࡷࡻࡥࠣḞ") else logging.INFO
def bstack1l1l1llllll_opy_():
  global bstack111l111ll11_opy_
  if os.path.exists(bstack111l111ll11_opy_):
    os.remove(bstack111l111ll11_opy_)
  if os.path.exists(bstack111l11ll111_opy_):
    os.remove(bstack111l11ll111_opy_)
def bstack1l1ll11ll_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l11lll1l_opy_ = log_level
  if bstack1ll111_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ḟ") in config and config[bstack1ll111_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧḠ")] in bstack11l1ll111ll_opy_:
    bstack111l11lll1l_opy_ = bstack11l1ll111ll_opy_[config[bstack1ll111_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨḡ")]]
  if config.get(bstack1ll111_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩḢ"), False):
    logging.getLogger().setLevel(bstack111l11lll1l_opy_)
    return bstack111l11lll1l_opy_
  global bstack111l111ll11_opy_
  bstack1l1ll11ll_opy_()
  bstack111l1l11111_opy_ = logging.Formatter(
    fmt=bstack1ll111_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫḣ"),
    datefmt=bstack1ll111_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧḤ"),
  )
  bstack111l11l1lll_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l111ll11_opy_)
  file_handler.setFormatter(bstack111l1l11111_opy_)
  bstack111l11l1lll_opy_.setFormatter(bstack111l1l11111_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l11l1lll_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1ll111_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࠳ࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡴࡨࡱࡴࡺࡥ࠯ࡴࡨࡱࡴࡺࡥࡠࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲࠬḥ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l11l1lll_opy_.setLevel(bstack111l11lll1l_opy_)
  logging.getLogger().addHandler(bstack111l11l1lll_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l11lll1l_opy_
def bstack111l11l1l1l_opy_(config):
  try:
    bstack111l11lllll_opy_ = set(bstack11l1l111l1l_opy_)
    bstack111l111l1ll_opy_ = bstack1ll111_opy_ (u"ࠫࠬḦ")
    with open(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨḧ")) as bstack111l11ll11l_opy_:
      bstack111l11ll1ll_opy_ = bstack111l11ll11l_opy_.read()
      bstack111l111l1ll_opy_ = re.sub(bstack1ll111_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠤ࠰࠭ࠨࡡࡴࠧḨ"), bstack1ll111_opy_ (u"ࠧࠨḩ"), bstack111l11ll1ll_opy_, flags=re.M)
      bstack111l111l1ll_opy_ = re.sub(
        bstack1ll111_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠫࠫḪ") + bstack1ll111_opy_ (u"ࠩࡿࠫḫ").join(bstack111l11lllll_opy_) + bstack1ll111_opy_ (u"ࠪ࠭࠳࠰ࠤࠨḬ"),
        bstack1ll111_opy_ (u"ࡶࠬࡢ࠲࠻ࠢ࡞ࡖࡊࡊࡁࡄࡖࡈࡈࡢ࠭ḭ"),
        bstack111l111l1ll_opy_, flags=re.M | re.I
      )
    def bstack111l11l11ll_opy_(dic):
      bstack111l11l1ll1_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l11lllll_opy_:
          bstack111l11l1ll1_opy_[key] = bstack1ll111_opy_ (u"ࠬࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩḮ")
        else:
          if isinstance(value, dict):
            bstack111l11l1ll1_opy_[key] = bstack111l11l11ll_opy_(value)
          else:
            bstack111l11l1ll1_opy_[key] = value
      return bstack111l11l1ll1_opy_
    bstack111l11l1ll1_opy_ = bstack111l11l11ll_opy_(config)
    return {
      bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩḯ"): bstack111l111l1ll_opy_,
      bstack1ll111_opy_ (u"ࠧࡧ࡫ࡱࡥࡱࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪḰ"): json.dumps(bstack111l11l1ll1_opy_)
    }
  except Exception as e:
    return {}
def bstack111l11l1l11_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠨ࡮ࡲ࡫ࠬḱ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l1l111l1_opy_ = os.path.join(log_dir, bstack1ll111_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵࠪḲ"))
  if not os.path.exists(bstack111l1l111l1_opy_):
    bstack111l11lll11_opy_ = {
      bstack1ll111_opy_ (u"ࠥ࡭ࡳ࡯ࡰࡢࡶ࡫ࠦḳ"): str(inipath),
      bstack1ll111_opy_ (u"ࠦࡷࡵ࡯ࡵࡲࡤࡸ࡭ࠨḴ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠴ࡪࡴࡱࡱࠫḵ")), bstack1ll111_opy_ (u"࠭ࡷࠨḶ")) as bstack111l111lll1_opy_:
      bstack111l111lll1_opy_.write(json.dumps(bstack111l11lll11_opy_))
def bstack111l11llll1_opy_():
  try:
    bstack111l1l111l1_opy_ = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠧ࡭ࡱࡪࠫḷ"), bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḸ"))
    if os.path.exists(bstack111l1l111l1_opy_):
      with open(bstack111l1l111l1_opy_, bstack1ll111_opy_ (u"ࠩࡵࠫḹ")) as bstack111l111lll1_opy_:
        bstack111l111llll_opy_ = json.load(bstack111l111lll1_opy_)
      return bstack111l111llll_opy_.get(bstack1ll111_opy_ (u"ࠪ࡭ࡳ࡯ࡰࡢࡶ࡫ࠫḺ"), bstack1ll111_opy_ (u"ࠫࠬḻ")), bstack111l111llll_opy_.get(bstack1ll111_opy_ (u"ࠬࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠧḼ"), bstack1ll111_opy_ (u"࠭ࠧḽ"))
  except:
    pass
  return None, None
def bstack111l111ll1l_opy_():
  try:
    bstack111l1l111l1_opy_ = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠧ࡭ࡱࡪࠫḾ"), bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḿ"))
    if os.path.exists(bstack111l1l111l1_opy_):
      os.remove(bstack111l1l111l1_opy_)
  except:
    pass
def bstack11l1l1l111_opy_(config):
  try:
    from bstack_utils.helper import bstack11ll11l11l_opy_, bstack1l111l1l1l_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l111ll11_opy_
    if config.get(bstack1ll111_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫṀ"), False):
      return
    uuid = os.getenv(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨṁ")) if os.getenv(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩṂ")) else bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢṃ"))
    if not uuid or uuid == bstack1ll111_opy_ (u"࠭࡮ࡶ࡮࡯ࠫṄ"):
      return
    bstack111l11ll1l1_opy_ = [bstack1ll111_opy_ (u"ࠧࡳࡧࡴࡹ࡮ࡸࡥ࡮ࡧࡱࡸࡸ࠴ࡴࡹࡶࠪṅ"), bstack1ll111_opy_ (u"ࠨࡒ࡬ࡴ࡫࡯࡬ࡦࠩṆ"), bstack1ll111_opy_ (u"ࠩࡳࡽࡵࡸ࡯࡫ࡧࡦࡸ࠳ࡺ࡯࡮࡮ࠪṇ"), bstack111l111ll11_opy_, bstack111l11ll111_opy_]
    bstack111l11l111l_opy_, root_path = bstack111l11llll1_opy_()
    if bstack111l11l111l_opy_ != None:
      bstack111l11ll1l1_opy_.append(bstack111l11l111l_opy_)
    if root_path != None:
      bstack111l11ll1l1_opy_.append(os.path.join(root_path, bstack1ll111_opy_ (u"ࠪࡧࡴࡴࡦࡵࡧࡶࡸ࠳ࡶࡹࠨṈ")))
    bstack1l1ll11ll_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡱࡵࡧࡴ࠯ࠪṉ") + uuid + bstack1ll111_opy_ (u"ࠬ࠴ࡴࡢࡴ࠱࡫ࡿ࠭Ṋ"))
    with tarfile.open(output_file, bstack1ll111_opy_ (u"ࠨࡷ࠻ࡩࡽࠦṋ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l11ll1l1_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l11l1l1l_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1l1111l_opy_ = data.encode()
        tarinfo.size = len(bstack111l1l1111l_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1l1111l_opy_))
    bstack11l111llll_opy_ = MultipartEncoder(
      fields= {
        bstack1ll111_opy_ (u"ࠧࡥࡣࡷࡥࠬṌ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1ll111_opy_ (u"ࠨࡴࡥࠫṍ")), bstack1ll111_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯ࡹ࠯ࡪࡾ࡮ࡶࠧṎ")),
        bstack1ll111_opy_ (u"ࠪࡧࡱ࡯ࡥ࡯ࡶࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬṏ"): uuid
      }
    )
    bstack111l11l11l1_opy_ = bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠦࡦࡶࡩࡴࠤṐ"), bstack1ll111_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧṑ"), bstack1ll111_opy_ (u"ࠨࡵࡱ࡮ࡲࡥࡩࠨṒ")], bstack11l1l111l11_opy_)
    response = requests.post(
      bstack1ll111_opy_ (u"ࠢࡼࡿ࠲ࡧࡱ࡯ࡥ࡯ࡶ࠰ࡰࡴ࡭ࡳ࠰ࡷࡳࡰࡴࡧࡤࠣṓ").format(bstack111l11l11l1_opy_),
      data=bstack11l111llll_opy_,
      headers={bstack1ll111_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧṔ"): bstack11l111llll_opy_.content_type},
      auth=(config[bstack1ll111_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫṕ")], config[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭Ṗ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1ll111_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡲ࡯ࡢࡦࠣࡰࡴ࡭ࡳ࠻ࠢࠪṗ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1ll111_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫࡮ࡥ࡫ࡱ࡫ࠥࡲ࡯ࡨࡵ࠽ࠫṘ") + str(e))
  finally:
    try:
      bstack1l1l1llllll_opy_()
      bstack111l111ll1l_opy_()
    except:
      pass