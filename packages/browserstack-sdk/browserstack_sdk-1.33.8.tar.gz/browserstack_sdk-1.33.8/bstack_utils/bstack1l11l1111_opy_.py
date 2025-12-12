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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l111llll1_opy_, bstack1ll1111l11_opy_, bstack11111l1l1_opy_, bstack1l1lll111_opy_, \
    bstack111lll1ll1l_opy_
from bstack_utils.measure import measure
def bstack11l1111ll_opy_(bstack1llll1ll11l1_opy_):
    for driver in bstack1llll1ll11l1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l1ll1l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack11ll1ll11_opy_(driver, status, reason=bstack1ll111_opy_ (u"ࠬ࠭₈")):
    bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
    if bstack11ll11l11l_opy_.bstack1llllllll1l_opy_():
        return
    bstack1ll11l1l_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ₉"), bstack1ll111_opy_ (u"ࠧࠨ₊"), status, reason, bstack1ll111_opy_ (u"ࠨࠩ₋"), bstack1ll111_opy_ (u"ࠩࠪ₌"))
    driver.execute_script(bstack1ll11l1l_opy_)
@measure(event_name=EVENTS.bstack1l1ll1l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack1l1l1ll1l1_opy_(page, status, reason=bstack1ll111_opy_ (u"ࠪࠫ₍")):
    try:
        if page is None:
            return
        bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
        if bstack11ll11l11l_opy_.bstack1llllllll1l_opy_():
            return
        bstack1ll11l1l_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧ₎"), bstack1ll111_opy_ (u"ࠬ࠭₏"), status, reason, bstack1ll111_opy_ (u"࠭ࠧₐ"), bstack1ll111_opy_ (u"ࠧࠨₑ"))
        page.evaluate(bstack1ll111_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤₒ"), bstack1ll11l1l_opy_)
    except Exception as e:
        print(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡪࡴࡸࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࢀࢃࠢₓ"), e)
def bstack1l111l1l11_opy_(type, name, status, reason, bstack11lll1l1l_opy_, bstack11llll111_opy_):
    bstack1ll1ll1l11_opy_ = {
        bstack1ll111_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪₔ"): type,
        bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧₕ"): {}
    }
    if type == bstack1ll111_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧₖ"):
        bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩₗ")][bstack1ll111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ₘ")] = bstack11lll1l1l_opy_
        bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫₙ")][bstack1ll111_opy_ (u"ࠩࡧࡥࡹࡧࠧₚ")] = json.dumps(str(bstack11llll111_opy_))
    if type == bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫₛ"):
        bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧₜ")][bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ₝")] = name
    if type == bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ₞"):
        bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ₟")][bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ₠")] = status
        if status == bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ₡") and str(reason) != bstack1ll111_opy_ (u"ࠥࠦ₢"):
            bstack1ll1ll1l11_opy_[bstack1ll111_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ₣")][bstack1ll111_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬ₤")] = json.dumps(str(reason))
    bstack11ll11l1l_opy_ = bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫ₥").format(json.dumps(bstack1ll1ll1l11_opy_))
    return bstack11ll11l1l_opy_
def bstack1lll1l111_opy_(url, config, logger, bstack1ll11ll1l_opy_=False):
    hostname = bstack1ll1111l11_opy_(url)
    is_private = bstack1l1lll111_opy_(hostname)
    try:
        if is_private or bstack1ll11ll1l_opy_:
            file_path = bstack11l111llll1_opy_(bstack1ll111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ₦"), bstack1ll111_opy_ (u"ࠨ࠰ࡥࡷࡹࡧࡣ࡬࠯ࡦࡳࡳ࡬ࡩࡨ࠰࡭ࡷࡴࡴࠧ₧"), logger)
            if os.environ.get(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧ₨")) and eval(
                    os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡏࡓࡈࡇࡌࡠࡐࡒࡘࡤ࡙ࡅࡕࡡࡈࡖࡗࡕࡒࠨ₩"))):
                return
            if (bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ₪") in config and not config[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ₫")]):
                os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࡣࡓࡕࡔࡠࡕࡈࡘࡤࡋࡒࡓࡑࡕࠫ€")] = str(True)
                bstack1llll1ll111l_opy_ = {bstack1ll111_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩ₭"): hostname}
                bstack111lll1ll1l_opy_(bstack1ll111_opy_ (u"ࠨ࠰ࡥࡷࡹࡧࡣ࡬࠯ࡦࡳࡳ࡬ࡩࡨ࠰࡭ࡷࡴࡴࠧ₮"), bstack1ll111_opy_ (u"ࠩࡱࡹࡩ࡭ࡥࡠ࡮ࡲࡧࡦࡲࠧ₯"), bstack1llll1ll111l_opy_, logger)
    except Exception as e:
        pass
def bstack11ll1l1l1l_opy_(caps, bstack1llll1ll11ll_opy_):
    if bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ₰") in caps:
        caps[bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ₱")][bstack1ll111_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࠫ₲")] = True
        if bstack1llll1ll11ll_opy_:
            caps[bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ₳")][bstack1ll111_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ₴")] = bstack1llll1ll11ll_opy_
    else:
        caps[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱ࠭₵")] = True
        if bstack1llll1ll11ll_opy_:
            caps[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ₶")] = bstack1llll1ll11ll_opy_
def bstack1lllll1ll11l_opy_(bstack1111llllll_opy_):
    bstack1llll1ll1l11_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡔࡶࡤࡸࡺࡹࠧ₷"), bstack1ll111_opy_ (u"ࠫࠬ₸"))
    if bstack1llll1ll1l11_opy_ == bstack1ll111_opy_ (u"ࠬ࠭₹") or bstack1llll1ll1l11_opy_ == bstack1ll111_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ₺"):
        threading.current_thread().testStatus = bstack1111llllll_opy_
    else:
        if bstack1111llllll_opy_ == bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ₻"):
            threading.current_thread().testStatus = bstack1111llllll_opy_