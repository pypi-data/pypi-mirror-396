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
from typing import List, Dict, Any
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
logger = get_logger(__name__)
class bstack1lll11l1l11_opy_:
    bstack1ll111_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡆࡹࡸࡺ࡯࡮ࡖࡤ࡫ࡒࡧ࡮ࡢࡩࡨࡶࠥࡶࡲࡰࡸ࡬ࡨࡪࡹࠠࡶࡶ࡬ࡰ࡮ࡺࡹࠡ࡯ࡨࡸ࡭ࡵࡤࡴࠢࡷࡳࠥࡹࡥࡵࠢࡤࡲࡩࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡥࡸࡷࡹࡵ࡭ࠡࡶࡤ࡫ࠥࡳࡥࡵࡣࡧࡥࡹࡧ࠮ࠋࠢࠣࠤࠥࡏࡴࠡ࡯ࡤ࡭ࡳࡺࡡࡪࡰࡶࠤࡹࡽ࡯ࠡࡵࡨࡴࡦࡸࡡࡵࡧࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡪࡧࡶࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࠦ࡬ࡦࡸࡨࡰࠥࡧ࡮ࡥࠢࡥࡹ࡮ࡲࡤࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠࡵࡣࡪࡷ࠳ࠐࠠࠡࠢࠣࡉࡦࡩࡨࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡩࡳࡺࡲࡺࠢ࡬ࡷࠥ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡵࡱࠣࡦࡪࠦࡳࡵࡴࡸࡧࡹࡻࡲࡦࡦࠣࡥࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠ࡬ࡧࡼ࠾ࠥࢁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧ࡬ࡩࡦ࡮ࡧࡣࡹࡿࡰࡦࠤ࠽ࠤࠧࡳࡵ࡭ࡶ࡬ࡣࡩࡸ࡯ࡱࡦࡲࡻࡳࠨࠬࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡶࡢ࡮ࡸࡩࡸࠨ࠺ࠡ࡝࡯࡭ࡸࡺࠠࡰࡨࠣࡸࡦ࡭ࠠࡷࡣ࡯ࡹࡪࡹ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࡿࠍࠤࠥࠦࠠࠣࠤࠥᙄ")
    _11ll1lllll1_opy_: Dict[str, Dict[str, Any]] = {}
    _11ll1llll1l_opy_: Dict[str, Dict[str, Any]] = {}
    @staticmethod
    def set_custom_tag(bstack11l1lll1_opy_: str, key_value: str, bstack11lll1111ll_opy_: bool = False) -> None:
        if not bstack11l1lll1_opy_ or not key_value or bstack11l1lll1_opy_.strip() == bstack1ll111_opy_ (u"ࠥࠦᙅ") or key_value.strip() == bstack1ll111_opy_ (u"ࠦࠧᙆ"):
            logger.error(bstack1ll111_opy_ (u"ࠧࡱࡥࡺࡡࡱࡥࡲ࡫ࠠࡢࡰࡧࠤࡰ࡫ࡹࡠࡸࡤࡰࡺ࡫ࠠ࡮ࡷࡶࡸࠥࡨࡥࠡࡰࡲࡲ࠲ࡴࡵ࡭࡮ࠣࡥࡳࡪࠠ࡯ࡱࡱ࠱ࡪࡳࡰࡵࡻࠥᙇ"))
        values: List[str] = bstack1lll11l1l11_opy_.bstack11lll1111l1_opy_(key_value)
        bstack11ll1llll11_opy_ = {bstack1ll111_opy_ (u"ࠨࡦࡪࡧ࡯ࡨࡤࡺࡹࡱࡧࠥᙈ"): bstack1ll111_opy_ (u"ࠢ࡮ࡷ࡯ࡸ࡮ࡥࡤࡳࡱࡳࡨࡴࡽ࡮ࠣᙉ"), bstack1ll111_opy_ (u"ࠣࡸࡤࡰࡺ࡫ࡳࠣᙊ"): values}
        bstack11lll111111_opy_ = bstack1lll11l1l11_opy_._11ll1llll1l_opy_ if bstack11lll1111ll_opy_ else bstack1lll11l1l11_opy_._11ll1lllll1_opy_
        if bstack11l1lll1_opy_ in bstack11lll111111_opy_:
            bstack11lll11111l_opy_ = bstack11lll111111_opy_[bstack11l1lll1_opy_]
            bstack11ll1llllll_opy_ = bstack11lll11111l_opy_.get(bstack1ll111_opy_ (u"ࠤࡹࡥࡱࡻࡥࡴࠤᙋ"), [])
            for val in values:
                if val not in bstack11ll1llllll_opy_:
                    bstack11ll1llllll_opy_.append(val)
            bstack11lll11111l_opy_[bstack1ll111_opy_ (u"ࠥࡺࡦࡲࡵࡦࡵࠥᙌ")] = bstack11ll1llllll_opy_
        else:
            bstack11lll111111_opy_[bstack11l1lll1_opy_] = bstack11ll1llll11_opy_
    @staticmethod
    def bstack1l111l11l1l_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1lll11l1l11_opy_._11ll1lllll1_opy_
    @staticmethod
    def bstack11lll111l11_opy_() -> Dict[str, Dict[str, Any]]:
        return bstack1lll11l1l11_opy_._11ll1llll1l_opy_
    @staticmethod
    def bstack11lll1111l1_opy_(bstack11ll1lll1ll_opy_: str) -> List[str]:
        bstack1ll111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡕࡳࡰ࡮ࡺࡳࠡࡶ࡫ࡩࠥ࡯࡮ࡱࡷࡷࠤࡸࡺࡲࡪࡰࡪࠤࡧࡿࠠࡤࡱࡰࡱࡦࡹࠠࡸࡪ࡬ࡰࡪࠦࡲࡦࡵࡳࡩࡨࡺࡩ࡯ࡩࠣࡨࡴࡻࡢ࡭ࡧ࠰ࡵࡺࡵࡴࡦࡦࠣࡷࡺࡨࡳࡵࡴ࡬ࡲ࡬ࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡉࡳࡷࠦࡥࡹࡣࡰࡴࡱ࡫࠺ࠡࠩࡤ࠰ࠥࠨࡢ࠭ࡥࠥ࠰ࠥࡪࠧࠡ࠯ࡁࠤࡠ࠭ࡡࠨ࠮ࠣࠫࡧ࠲ࡣࠨ࠮ࠣࠫࡩ࠭࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧᙍ")
        pattern = re.compile(bstack1ll111_opy_ (u"ࡷ࠭ࠢࠩ࡝ࡡࠦࡢ࠰ࠩࠣࡾࠫ࡟ࡣ࠲࡝ࠬࠫࠪᙎ"))
        result = []
        for match in pattern.finditer(bstack11ll1lll1ll_opy_):
            if match.group(1) is not None:
                result.append(match.group(1).strip())
            elif match.group(2) is not None:
                result.append(match.group(2).strip())
        return result
    def __new__(cls, *args, **kwargs):
        raise Exception(bstack1ll111_opy_ (u"ࠨࡕࡵ࡫࡯࡭ࡹࡿࠠࡤ࡮ࡤࡷࡸࠦࡳࡩࡱࡸࡰࡩࠦ࡮ࡰࡶࠣࡦࡪࠦࡩ࡯ࡵࡷࡥࡳࡺࡩࡢࡶࡨࡨࠧᙏ"))