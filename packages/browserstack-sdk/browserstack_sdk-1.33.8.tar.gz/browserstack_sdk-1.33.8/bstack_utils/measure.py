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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
bstack1ll1lll11_opy_ = bstack1ll1ll111ll_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l1lll11_opy_: Optional[str] = None):
    bstack1ll111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡄࡦࡥࡲࡶࡦࡺ࡯ࡳࠢࡷࡳࠥࡲ࡯ࡨࠢࡷ࡬ࡪࠦࡳࡵࡣࡵࡸࠥࡺࡩ࡮ࡧࠣࡳ࡫ࠦࡡࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࡥࡱࡵ࡮ࡨࠢࡺ࡭ࡹ࡮ࠠࡦࡸࡨࡲࡹࠦ࡮ࡢ࡯ࡨࠤࡦࡴࡤࠡࡵࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠨࠢࠣṙ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll111lllll_opy_: str = bstack1ll1lll11_opy_.bstack11ll1111lll_opy_(label)
            start_mark: str = label + bstack1ll111_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢṚ")
            end_mark: str = label + bstack1ll111_opy_ (u"ࠣ࠼ࡨࡲࡩࠨṛ")
            result = None
            try:
                if stage.value == STAGE.bstack1lll11l111_opy_.value:
                    bstack1ll1lll11_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1ll1lll11_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l1lll11_opy_)
                elif stage.value == STAGE.bstack11ll1lll1_opy_.value:
                    start_mark: str = bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤṜ")
                    end_mark: str = bstack1ll111lllll_opy_ + bstack1ll111_opy_ (u"ࠥ࠾ࡪࡴࡤࠣṝ")
                    bstack1ll1lll11_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1ll1lll11_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l1lll11_opy_)
            except Exception as e:
                bstack1ll1lll11_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l1lll11_opy_)
            return result
        return wrapper
    return decorator