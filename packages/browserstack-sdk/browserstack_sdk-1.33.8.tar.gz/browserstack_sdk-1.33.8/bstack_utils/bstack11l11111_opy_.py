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
from browserstack_sdk.bstack1llll11lll_opy_ import bstack1lll1111ll_opy_
from browserstack_sdk.bstack1111l1l1l1_opy_ import RobotHandler
def bstack1ll111ll1_opy_(framework):
    if framework.lower() == bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭᭥"):
        return bstack1lll1111ll_opy_.version()
    elif framework.lower() == bstack1ll111_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭᭦"):
        return RobotHandler.version()
    elif framework.lower() == bstack1ll111_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ᭧"):
        import behave
        return behave.__version__
    else:
        return bstack1ll111_opy_ (u"ࠩࡸࡲࡰࡴ࡯ࡸࡰࠪ᭨")
def bstack1lll11ll_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack1ll111_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࠬ᭩"))
        framework_version.append(importlib.metadata.version(bstack1ll111_opy_ (u"ࠦࡸ࡫࡬ࡦࡰ࡬ࡹࡲࠨ᭪")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩ᭫"))
        framework_version.append(importlib.metadata.version(bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶ᭬ࠥ")))
    except:
        pass
    return {
        bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ᭭"): bstack1ll111_opy_ (u"ࠨࡡࠪ᭮").join(framework_name),
        bstack1ll111_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪ᭯"): bstack1ll111_opy_ (u"ࠪࡣࠬ᭰").join(framework_version)
    }