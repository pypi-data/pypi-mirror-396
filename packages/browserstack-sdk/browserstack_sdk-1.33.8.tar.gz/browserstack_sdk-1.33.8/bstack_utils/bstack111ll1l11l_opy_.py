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
import threading
from bstack_utils.helper import bstack1l1l1111l1_opy_
from bstack_utils.constants import bstack11l1l1l11ll_opy_, EVENTS, STAGE
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack1llll1111_opy_:
    bstack1lllll1111ll_opy_ = None
    @classmethod
    def bstack1lllll1111_opy_(cls):
        if cls.on() and os.getenv(bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨ⊊")):
            logger.info(
                bstack1ll111_opy_ (u"࡙ࠩ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡥࡹ࡮ࡲࡤࡴ࠱ࡾࢁࠥࡺ࡯ࠡࡸ࡬ࡩࡼࠦࡢࡶ࡫࡯ࡨࠥࡸࡥࡱࡱࡵࡸ࠱ࠦࡩ࡯ࡵ࡬࡫࡭ࡺࡳ࠭ࠢࡤࡲࡩࠦ࡭ࡢࡰࡼࠤࡲࡵࡲࡦࠢࡧࡩࡧࡻࡧࡨ࡫ࡱ࡫ࠥ࡯࡮ࡧࡱࡵࡱࡦࡺࡩࡰࡰࠣࡥࡱࡲࠠࡢࡶࠣࡳࡳ࡫ࠠࡱ࡮ࡤࡧࡪࠧ࡜࡯ࠩ⊋").format(os.getenv(bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠣ⊌"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ⊍"), None) is None or os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ⊎")] == bstack1ll111_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦ⊏"):
            return False
        return True
    @classmethod
    def bstack1lll1ll1lll1_opy_(cls, bs_config, framework=bstack1ll111_opy_ (u"ࠢࠣ⊐")):
        bstack11l1ll11lll_opy_ = False
        for fw in bstack11l1l1l11ll_opy_:
            if fw in framework:
                bstack11l1ll11lll_opy_ = True
        return bstack1l1l1111l1_opy_(bs_config.get(bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ⊑"), bstack11l1ll11lll_opy_))
    @classmethod
    def bstack1lll1ll11ll1_opy_(cls, framework):
        return framework in bstack11l1l1l11ll_opy_
    @classmethod
    def bstack1lll1lllll11_opy_(cls, bs_config, framework):
        return cls.bstack1lll1ll1lll1_opy_(bs_config, framework) is True and cls.bstack1lll1ll11ll1_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⊒"), None)
    @staticmethod
    def bstack111ll11lll_opy_():
        if getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ⊓"), None):
            return {
                bstack1ll111_opy_ (u"ࠫࡹࡿࡰࡦࠩ⊔"): bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࠪ⊕"),
                bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⊖"): getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⊗"), None)
            }
        if getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⊘"), None):
            return {
                bstack1ll111_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⊙"): bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨ⊚"),
                bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⊛"): getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ⊜"), None)
            }
        return None
    @staticmethod
    def bstack1lll1ll11l11_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1llll1111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack111l111l11_opy_(test, hook_name=None):
        bstack1lll1ll111ll_opy_ = test.parent
        if hook_name in [bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ⊝"), bstack1ll111_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠨ⊞"), bstack1ll111_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠧ⊟"), bstack1ll111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲࡵࡤࡶ࡮ࡨࠫ⊠")]:
            bstack1lll1ll111ll_opy_ = test
        scope = []
        while bstack1lll1ll111ll_opy_ is not None:
            scope.append(bstack1lll1ll111ll_opy_.name)
            bstack1lll1ll111ll_opy_ = bstack1lll1ll111ll_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1lll1ll11l1l_opy_(hook_type):
        if hook_type == bstack1ll111_opy_ (u"ࠥࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠣ⊡"):
            return bstack1ll111_opy_ (u"ࠦࡘ࡫ࡴࡶࡲࠣ࡬ࡴࡵ࡫ࠣ⊢")
        elif hook_type == bstack1ll111_opy_ (u"ࠧࡇࡆࡕࡇࡕࡣࡊࡇࡃࡉࠤ⊣"):
            return bstack1ll111_opy_ (u"ࠨࡔࡦࡣࡵࡨࡴࡽ࡮ࠡࡪࡲࡳࡰࠨ⊤")
    @staticmethod
    def bstack1lll1ll111l1_opy_(bstack1l11l1l111_opy_):
        try:
            if not bstack1llll1111_opy_.on():
                return bstack1l11l1l111_opy_
            if os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࠧ⊥"), None) == bstack1ll111_opy_ (u"ࠣࡶࡵࡹࡪࠨ⊦"):
                tests = os.environ.get(bstack1ll111_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔ࡟ࡕࡇࡖࡘࡘࠨ⊧"), None)
                if tests is None or tests == bstack1ll111_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ⊨"):
                    return bstack1l11l1l111_opy_
                bstack1l11l1l111_opy_ = tests.split(bstack1ll111_opy_ (u"ࠫ࠱࠭⊩"))
                return bstack1l11l1l111_opy_
        except Exception as exc:
            logger.debug(bstack1ll111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡷ࡫ࡲࡶࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡵ࠾ࠥࠨ⊪") + str(str(exc)) + bstack1ll111_opy_ (u"ࠨࠢ⊫"))
        return bstack1l11l1l111_opy_