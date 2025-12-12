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
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack11lll111_opy_ = {}
        bstack111ll1lll1_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠩࡆ࡙ࡗࡘࡅࡏࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡊࡁࡕࡃࠪ༚"), bstack1ll111_opy_ (u"ࠪࠫ༛"))
        if not bstack111ll1lll1_opy_:
            return bstack11lll111_opy_
        try:
            bstack111ll1llll_opy_ = json.loads(bstack111ll1lll1_opy_)
            if bstack1ll111_opy_ (u"ࠦࡴࡹࠢ༜") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠧࡵࡳࠣ༝")] = bstack111ll1llll_opy_[bstack1ll111_opy_ (u"ࠨ࡯ࡴࠤ༞")]
            if bstack1ll111_opy_ (u"ࠢࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠦ༟") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠣࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠦ༠") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠤࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༡")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠥࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ༢"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠦࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠢ༣")))
            if bstack1ll111_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࠨ༤") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠦ༥") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠧ༦")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࠤ༧"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠢ༨")))
            if bstack1ll111_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ༩") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༪") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༫")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣ༬"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠣ༭")))
            if bstack1ll111_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࠣ༮") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪࠨ༯") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠢ༰")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠦࡩ࡫ࡶࡪࡥࡨࠦ༱"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠧࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠤ༲")))
            if bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠣ༳") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪࠨ༴") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫༵ࠢ")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࠦ༶"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ༷")))
            if bstack1ll111_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ༸") in bstack111ll1llll_opy_ or bstack1ll111_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴ༹ࠢ") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣ༺")] = bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡࡹࡩࡷࡹࡩࡰࡰࠥ༻"), bstack111ll1llll_opy_.get(bstack1ll111_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥ༼")))
            if bstack1ll111_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦ༽") in bstack111ll1llll_opy_:
                bstack11lll111_opy_[bstack1ll111_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠧ༾")] = bstack111ll1llll_opy_[bstack1ll111_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰ࡚ࡦࡸࡩࡢࡤ࡯ࡩࡸࠨ༿")]
        except Exception as error:
            logger.error(bstack1ll111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩࡧࡴࡢ࠼ࠣࠦཀ") +  str(error))
        return bstack11lll111_opy_