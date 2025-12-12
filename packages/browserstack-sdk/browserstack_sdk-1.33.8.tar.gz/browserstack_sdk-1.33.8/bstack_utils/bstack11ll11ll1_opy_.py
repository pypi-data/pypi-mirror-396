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
import re
from bstack_utils.bstack1l11l1111_opy_ import bstack1lllll1ll11l_opy_
def bstack1lllll11lll1_opy_(fixture_name):
    if fixture_name.startswith(bstack1ll111_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ ")):
        return bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ ")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡴࡧࡷࡹࡵࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ ")):
        return bstack1ll111_opy_ (u"ࠨࡵࡨࡸࡺࡶ࠭࡮ࡱࡧࡹࡱ࡫ࠧ ")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ ")):
        return bstack1ll111_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧ ")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ ")):
        return bstack1ll111_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭࡮ࡱࡧࡹࡱ࡫ࠧ ")
def bstack1lllll1ll111_opy_(fixture_name):
    return bool(re.match(bstack1ll111_opy_ (u"࠭࡞ࡠࡺࡸࡲ࡮ࡺ࡟ࠩࡵࡨࡸࡺࡶࡼࡵࡧࡤࡶࡩࡵࡷ࡯ࠫࡢࠬ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࢂ࡭ࡰࡦࡸࡰࡪ࠯࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠ࠰࠭ࠫ​"), fixture_name))
def bstack1lllll1l1111_opy_(fixture_name):
    return bool(re.match(bstack1ll111_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨ‌"), fixture_name))
def bstack1lllll1ll1l1_opy_(fixture_name):
    return bool(re.match(bstack1ll111_opy_ (u"ࠨࡠࡢࡼࡺࡴࡩࡵࡡࠫࡷࡪࡺࡵࡱࡾࡷࡩࡦࡸࡤࡰࡹࡱ࠭ࡤࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨ‍"), fixture_name))
def bstack1lllll1l1ll1_opy_(fixture_name):
    if fixture_name.startswith(bstack1ll111_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ‎")):
        return bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫ‏"), bstack1ll111_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ‐")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡹࡥࡵࡷࡳࡣࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ‑")):
        return bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴ࠲ࡳ࡯ࡥࡷ࡯ࡩࠬ‒"), bstack1ll111_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫ–")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭—")):
        return bstack1ll111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭―"), bstack1ll111_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ‖")
    elif fixture_name.startswith(bstack1ll111_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪࡥࡦࡪࡺࡷࡹࡷ࡫ࠧ‗")):
        return bstack1ll111_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࠭࡮ࡱࡧࡹࡱ࡫ࠧ‘"), bstack1ll111_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ’")
    return None, None
def bstack1lllll1l11ll_opy_(hook_name):
    if hook_name in [bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭‚"), bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ‛")]:
        return hook_name.capitalize()
    return hook_name
def bstack1lllll11llll_opy_(hook_name):
    if hook_name in [bstack1ll111_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࠪ“"), bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡩࡹ࡮࡯ࡥࠩ”")]:
        return bstack1ll111_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ„")
    elif hook_name in [bstack1ll111_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡲࡵࡤࡶ࡮ࡨࠫ‟"), bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ†")]:
        return bstack1ll111_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫ‡")
    elif hook_name in [bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ•"), bstack1ll111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲ࡫ࡴࡩࡱࡧࠫ‣")]:
        return bstack1ll111_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡈࡅࡈࡎࠧ․")
    elif hook_name in [bstack1ll111_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭‥"), bstack1ll111_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸ࠭…")]:
        return bstack1ll111_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡇࡌࡍࠩ‧")
    return hook_name
def bstack1lllll1ll1ll_opy_(node, scenario):
    if hasattr(node, bstack1ll111_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩ ")):
        parts = node.nodeid.rsplit(bstack1ll111_opy_ (u"ࠣ࡝ࠥ "))
        params = parts[-1]
        return bstack1ll111_opy_ (u"ࠤࡾࢁࠥࡡࡻࡾࠤ‪").format(scenario.name, params)
    return scenario.name
def bstack1lllll1l1lll_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack1ll111_opy_ (u"ࠪࡧࡦࡲ࡬ࡴࡲࡨࡧࠬ‫")):
            examples = list(node.callspec.params[bstack1ll111_opy_ (u"ࠫࡤࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡨࡼࡦࡳࡰ࡭ࡧࠪ‬")].values())
        return examples
    except:
        return []
def bstack1lllll1l1l11_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1lllll1l111l_opy_(report):
    try:
        status = bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ‭")
        if report.passed or (report.failed and hasattr(report, bstack1ll111_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣ‮"))):
            status = bstack1ll111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ ")
        elif report.skipped:
            status = bstack1ll111_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ‰")
        bstack1lllll1ll11l_opy_(status)
    except:
        pass
def bstack1ll11111l1_opy_(status):
    try:
        bstack1lllll1l1l1l_opy_ = bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ‱")
        if status == bstack1ll111_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ′"):
            bstack1lllll1l1l1l_opy_ = bstack1ll111_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ″")
        elif status == bstack1ll111_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭‴"):
            bstack1lllll1l1l1l_opy_ = bstack1ll111_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧ‵")
        bstack1lllll1ll11l_opy_(bstack1lllll1l1l1l_opy_)
    except:
        pass
def bstack1lllll1l11l1_opy_(item=None, report=None, summary=None, extra=None):
    return