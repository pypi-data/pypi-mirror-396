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
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll11ll1ll_opy_, bstack11l1lllllll_opy_, bstack1l1l111111_opy_, error_handler, bstack11l1111llll_opy_, bstack111l1lll11l_opy_, bstack11l111ll11l_opy_, bstack11ll1l111_opy_, bstack11111l1l1_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1lllll1111ll_opy_ import bstack1lllll11l1l1_opy_
import bstack_utils.bstack1l111l11l1_opy_ as bstack1111ll11_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
import bstack_utils.accessibility as bstack1llll111_opy_
from bstack_utils.bstack111llll1ll_opy_ import bstack111llll1ll_opy_
from bstack_utils.bstack111ll11ll1_opy_ import bstack111l1l11l1_opy_
from bstack_utils.constants import bstack111ll11l_opy_
bstack1llll1111lll_opy_ = bstack1ll111_opy_ (u"ࠩ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡧࡴࡲ࡬ࡦࡥࡷࡳࡷ࠳࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ⅂")
logger = logging.getLogger(__name__)
class bstack111l1l111_opy_:
    bstack1lllll1111ll_opy_ = None
    bs_config = None
    bstack11l11111l1_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1ll1111l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def launch(cls, bs_config, bstack11l11111l1_opy_):
        cls.bs_config = bs_config
        cls.bstack11l11111l1_opy_ = bstack11l11111l1_opy_
        try:
            cls.bstack1llll111ll11_opy_()
            bstack11ll111ll1l_opy_ = bstack11ll11ll1ll_opy_(bs_config)
            bstack11ll111ll11_opy_ = bstack11l1lllllll_opy_(bs_config)
            data = bstack1111ll11_opy_.bstack1lll1lll1ll1_opy_(bs_config, bstack11l11111l1_opy_)
            config = {
                bstack1ll111_opy_ (u"ࠪࡥࡺࡺࡨࠨ⅃"): (bstack11ll111ll1l_opy_, bstack11ll111ll11_opy_),
                bstack1ll111_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬ⅄"): cls.default_headers()
            }
            response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠬࡖࡏࡔࡖࠪⅅ"), cls.request_url(bstack1ll111_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠷࠵ࡢࡶ࡫࡯ࡨࡸ࠭ⅆ")), data, config)
            if response.status_code != 200:
                bstack11111lll1_opy_ = response.json()
                if bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨⅇ")] == False:
                    cls.bstack1lll1lll1lll_opy_(bstack11111lll1_opy_)
                    return
                cls.bstack1lll1llll11l_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨⅈ")])
                cls.bstack1lll1lll1l1l_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩⅉ")])
                return None
            bstack1lll1llll1ll_opy_ = cls.bstack1llll11111ll_opy_(response)
            return bstack1lll1llll1ll_opy_, response.json()
        except Exception as error:
            logger.error(bstack1ll111_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡣࡷ࡬ࡰࡩࠦࡦࡰࡴࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࢁࡽࠣ⅊").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1llll111l11l_opy_=None):
        if not bstack1llll1111_opy_.on() and not bstack1llll111_opy_.on():
            return
        if os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ⅋")) == bstack1ll111_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ⅌") or os.environ.get(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ⅍")) == bstack1ll111_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧⅎ"):
            logger.error(bstack1ll111_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡶࡲࡴࠥࡨࡵࡪ࡮ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡺ࡯ࠡࡖࡨࡷࡹࡎࡵࡣ࠼ࠣࡑ࡮ࡹࡳࡪࡰࡪࠤࡦࡻࡴࡩࡧࡱࡸ࡮ࡩࡡࡵ࡫ࡲࡲࠥࡺ࡯࡬ࡧࡱࠫ⅏"))
            return {
                bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ⅐"): bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ⅑"),
                bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⅒"): bstack1ll111_opy_ (u"࡚ࠬ࡯࡬ࡧࡱ࠳ࡧࡻࡩ࡭ࡦࡌࡈࠥ࡯ࡳࠡࡷࡱࡨࡪ࡬ࡩ࡯ࡧࡧ࠰ࠥࡨࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦ࡭ࡪࡩ࡫ࡸࠥ࡮ࡡࡷࡧࠣࡪࡦ࡯࡬ࡦࡦࠪ⅓")
            }
        try:
            cls.bstack1lllll1111ll_opy_.shutdown()
            data = {
                bstack1ll111_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⅔"): bstack11ll1l111_opy_()
            }
            if not bstack1llll111l11l_opy_ is None:
                data[bstack1ll111_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡰࡩࡹࡧࡤࡢࡶࡤࠫ⅕")] = [{
                    bstack1ll111_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨ⅖"): bstack1ll111_opy_ (u"ࠩࡸࡷࡪࡸ࡟࡬࡫࡯ࡰࡪࡪࠧ⅗"),
                    bstack1ll111_opy_ (u"ࠪࡷ࡮࡭࡮ࡢ࡮ࠪ⅘"): bstack1llll111l11l_opy_
                }]
            config = {
                bstack1ll111_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬ⅙"): cls.default_headers()
            }
            bstack11l1llll111_opy_ = bstack1ll111_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽ࠰ࡵࡷࡳࡵ࠭⅚").format(os.environ[bstack1ll111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠦ⅛")])
            bstack1llll111l111_opy_ = cls.request_url(bstack11l1llll111_opy_)
            response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠧࡑࡗࡗࠫ⅜"), bstack1llll111l111_opy_, data, config)
            if not response.ok:
                raise Exception(bstack1ll111_opy_ (u"ࠣࡕࡷࡳࡵࠦࡲࡦࡳࡸࡩࡸࡺࠠ࡯ࡱࡷࠤࡴࡱࠢ⅝"))
        except Exception as error:
            logger.error(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡷࡳࡵࠦࡢࡶ࡫࡯ࡨࠥࡸࡥࡲࡷࡨࡷࡹࠦࡴࡰࠢࡗࡩࡸࡺࡈࡶࡤ࠽࠾ࠥࠨ⅞") + str(error))
            return {
                bstack1ll111_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⅟"): bstack1ll111_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪⅠ"),
                bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭Ⅱ"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll11111ll_opy_(cls, response):
        bstack11111lll1_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1lll1llll1ll_opy_ = {}
        if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"࠭ࡪࡸࡶࠪⅢ")) is None:
            os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫⅣ")] = bstack1ll111_opy_ (u"ࠨࡰࡸࡰࡱ࠭Ⅴ")
        else:
            os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭Ⅵ")] = bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠪ࡮ࡼࡺࠧⅦ"), bstack1ll111_opy_ (u"ࠫࡳࡻ࡬࡭ࠩⅧ"))
        os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪⅨ")] = bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨⅩ"), bstack1ll111_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬⅪ"))
        logger.info(bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹ࡮ࡵࡣࠢࡶࡸࡦࡸࡴࡦࡦࠣࡻ࡮ࡺࡨࠡ࡫ࡧ࠾ࠥ࠭Ⅻ") + os.getenv(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧⅬ")));
        if bstack1llll1111_opy_.bstack1lll1lllll11_opy_(cls.bs_config, cls.bstack11l11111l1_opy_.get(bstack1ll111_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡵࡴࡧࡧࠫⅭ"), bstack1ll111_opy_ (u"ࠫࠬⅮ"))) is True:
            bstack1lllll11111l_opy_, build_hashed_id, bstack1llll1111111_opy_ = cls.bstack1llll111ll1l_opy_(bstack11111lll1_opy_)
            if bstack1lllll11111l_opy_ != None and build_hashed_id != None:
                bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬⅯ")] = {
                    bstack1ll111_opy_ (u"࠭ࡪࡸࡶࡢࡸࡴࡱࡥ࡯ࠩⅰ"): bstack1lllll11111l_opy_,
                    bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩⅱ"): build_hashed_id,
                    bstack1ll111_opy_ (u"ࠨࡣ࡯ࡰࡴࡽ࡟ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬⅲ"): bstack1llll1111111_opy_
                }
            else:
                bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩⅳ")] = {}
        else:
            bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪⅴ")] = {}
        bstack1llll11111l1_opy_, build_hashed_id = cls.bstack1lll1lllll1l_opy_(bstack11111lll1_opy_)
        if bstack1llll11111l1_opy_ != None and build_hashed_id != None:
            bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫⅵ")] = {
                bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡪࡢࡸࡴࡱࡥ࡯ࠩⅶ"): bstack1llll11111l1_opy_,
                bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨⅷ"): build_hashed_id,
            }
        else:
            bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧⅸ")] = {}
        if bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨⅹ")].get(bstack1ll111_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫⅺ")) != None or bstack1lll1llll1ll_opy_[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪⅻ")].get(bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ⅼ")) != None:
            cls.bstack1llll111lll1_opy_(bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠬࡰࡷࡵࠩⅽ")), bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨⅾ")))
        return bstack1lll1llll1ll_opy_
    @classmethod
    def bstack1llll111ll1l_opy_(cls, bstack11111lll1_opy_):
        if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧⅿ")) == None:
            cls.bstack1lll1llll11l_opy_()
            return [None, None, None]
        if bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨↀ")][bstack1ll111_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪↁ")] != True:
            cls.bstack1lll1llll11l_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪↂ")])
            return [None, None, None]
        logger.debug(bstack1ll111_opy_ (u"ࠫࢀࢃࠠࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࠦ࠭Ↄ").format(bstack111ll11l_opy_))
        os.environ[bstack1ll111_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡅ࡙ࡎࡒࡄࡠࡅࡒࡑࡕࡒࡅࡕࡇࡇࠫↄ")] = bstack1ll111_opy_ (u"࠭ࡴࡳࡷࡨࠫↅ")
        if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠧ࡫ࡹࡷࠫↆ")):
            os.environ[bstack1ll111_opy_ (u"ࠨࡅࡕࡉࡉࡋࡎࡕࡋࡄࡐࡘࡥࡆࡐࡔࡢࡇࡗࡇࡓࡉࡡࡕࡉࡕࡕࡒࡕࡋࡑࡋࠬↇ")] = json.dumps({
                bstack1ll111_opy_ (u"ࠩࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫↈ"): bstack11ll11ll1ll_opy_(cls.bs_config),
                bstack1ll111_opy_ (u"ࠪࡴࡦࡹࡳࡸࡱࡵࡨࠬ↉"): bstack11l1lllllll_opy_(cls.bs_config)
            })
        if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭↊")):
            os.environ[bstack1ll111_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡅ࡙ࡎࡒࡄࡠࡊࡄࡗࡍࡋࡄࡠࡋࡇࠫ↋")] = bstack11111lll1_opy_[bstack1ll111_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ↌")]
        if bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ↍")].get(bstack1ll111_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩ↎"), {}).get(bstack1ll111_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭↏")):
            os.environ[bstack1ll111_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ←")] = str(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ↑")][bstack1ll111_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭→")][bstack1ll111_opy_ (u"࠭ࡡ࡭࡮ࡲࡻࡤࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ↓")])
        else:
            os.environ[bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡆࡒࡌࡐ࡙ࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࡓࠨ↔")] = bstack1ll111_opy_ (u"ࠣࡰࡸࡰࡱࠨ↕")
        return [bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠩ࡭ࡻࡹ࠭↖")], bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ↗")], os.environ[bstack1ll111_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡃࡏࡐࡔ࡝࡟ࡔࡅࡕࡉࡊࡔࡓࡉࡑࡗࡗࠬ↘")]]
    @classmethod
    def bstack1lll1lllll1l_opy_(cls, bstack11111lll1_opy_):
        if bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ↙")) == None:
            cls.bstack1lll1lll1l1l_opy_()
            return [None, None]
        if bstack11111lll1_opy_[bstack1ll111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭↚")][bstack1ll111_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨ↛")] != True:
            cls.bstack1lll1lll1l1l_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ↜")])
            return [None, None]
        if bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ↝")].get(bstack1ll111_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ↞")):
            logger.debug(bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡅࡹ࡮ࡲࡤࠡࡥࡵࡩࡦࡺࡩࡰࡰࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠡࠨ↟"))
            parsed = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭↠"), bstack1ll111_opy_ (u"࠭ࡻࡾࠩ↡")))
            capabilities = bstack1111ll11_opy_.bstack1llll111l1ll_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ↢")][bstack1ll111_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩ↣")][bstack1ll111_opy_ (u"ࠩࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ↤")], bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨ↥"), bstack1ll111_opy_ (u"ࠫࡻࡧ࡬ࡶࡧࠪ↦"))
            bstack1llll11111l1_opy_ = capabilities[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࡙ࡵ࡫ࡦࡰࠪ↧")]
            os.environ[bstack1ll111_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ↨")] = bstack1llll11111l1_opy_
            if bstack1ll111_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡦࠤ↩") in bstack11111lll1_opy_ and bstack11111lll1_opy_.get(bstack1ll111_opy_ (u"ࠣࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠢ↪")) is None:
                parsed[bstack1ll111_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ↫")] = capabilities[bstack1ll111_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ↬")]
            os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ↭")] = json.dumps(parsed)
            scripts = bstack1111ll11_opy_.bstack1llll111l1ll_opy_(bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ↮")][bstack1ll111_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧ↯")][bstack1ll111_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨ↰")], bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭↱"), bstack1ll111_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࠪ↲"))
            bstack111llll1ll_opy_.bstack1l1111l1l_opy_(scripts)
            commands = bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ↳")][bstack1ll111_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ↴")][bstack1ll111_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࡔࡰ࡙ࡵࡥࡵ࠭↵")].get(bstack1ll111_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨ↶"))
            bstack111llll1ll_opy_.bstack11ll1l1111l_opy_(commands)
            bstack11ll1l11111_opy_ = capabilities.get(bstack1ll111_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ↷"))
            bstack111llll1ll_opy_.bstack11l1llll1l1_opy_(bstack11ll1l11111_opy_)
            bstack111llll1ll_opy_.store()
        return [bstack1llll11111l1_opy_, bstack11111lll1_opy_[bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ↸")]]
    @classmethod
    def bstack1lll1llll11l_opy_(cls, response=None):
        os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ↹")] = bstack1ll111_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ↺")
        os.environ[bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ↻")] = bstack1ll111_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ↼")
        os.environ[bstack1ll111_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡆࡓࡒࡖࡌࡆࡖࡈࡈࠬ↽")] = bstack1ll111_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭↾")
        os.environ[bstack1ll111_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧ↿")] = bstack1ll111_opy_ (u"ࠤࡱࡹࡱࡲࠢ⇀")
        os.environ[bstack1ll111_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ⇁")] = bstack1ll111_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ⇂")
        cls.bstack1lll1lll1lll_opy_(response, bstack1ll111_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧ⇃"))
        return [None, None, None]
    @classmethod
    def bstack1lll1lll1l1l_opy_(cls, response=None):
        os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ⇄")] = bstack1ll111_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ⇅")
        os.environ[bstack1ll111_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭⇆")] = bstack1ll111_opy_ (u"ࠩࡱࡹࡱࡲࠧ⇇")
        os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ⇈")] = bstack1ll111_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ⇉")
        cls.bstack1lll1lll1lll_opy_(response, bstack1ll111_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠧ⇊"))
        return [None, None, None]
    @classmethod
    def bstack1llll111lll1_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⇋")] = jwt
        os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ⇌")] = build_hashed_id
    @classmethod
    def bstack1lll1lll1lll_opy_(cls, response=None, product=bstack1ll111_opy_ (u"ࠣࠤ⇍")):
        if response == None or response.get(bstack1ll111_opy_ (u"ࠩࡨࡶࡷࡵࡲࡴࠩ⇎")) == None:
            logger.error(product + bstack1ll111_opy_ (u"ࠥࠤࡇࡻࡩ࡭ࡦࠣࡧࡷ࡫ࡡࡵ࡫ࡲࡲࠥ࡬ࡡࡪ࡮ࡨࡨࠧ⇏"))
            return
        for error in response[bstack1ll111_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫ⇐")]:
            bstack11l111lll1l_opy_ = error[bstack1ll111_opy_ (u"ࠬࡱࡥࡺࠩ⇑")]
            error_message = error[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⇒")]
            if error_message:
                if bstack11l111lll1l_opy_ == bstack1ll111_opy_ (u"ࠢࡆࡔࡕࡓࡗࡥࡁࡄࡅࡈࡗࡘࡥࡄࡆࡐࡌࡉࡉࠨ⇓"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack1ll111_opy_ (u"ࠣࡆࡤࡸࡦࠦࡵࡱ࡮ࡲࡥࡩࠦࡴࡰࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࠤ⇔") + product + bstack1ll111_opy_ (u"ࠤࠣࡪࡦ࡯࡬ࡦࡦࠣࡨࡺ࡫ࠠࡵࡱࠣࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠢ⇕"))
    @classmethod
    def bstack1llll111ll11_opy_(cls):
        if cls.bstack1lllll1111ll_opy_ is not None:
            return
        cls.bstack1lllll1111ll_opy_ = bstack1lllll11l1l1_opy_(cls.bstack1llll1111l11_opy_)
        cls.bstack1lllll1111ll_opy_.start()
    @classmethod
    def bstack111l11l1ll_opy_(cls):
        if cls.bstack1lllll1111ll_opy_ is None:
            return
        cls.bstack1lllll1111ll_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll1111l11_opy_(cls, bstack111l1l1111_opy_, event_url=bstack1ll111_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡦࡺࡣࡩࠩ⇖")):
        config = {
            bstack1ll111_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬ⇗"): cls.default_headers()
        }
        logger.debug(bstack1ll111_opy_ (u"ࠧࡶ࡯ࡴࡶࡢࡨࡦࡺࡡ࠻ࠢࡖࡩࡳࡪࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡶࡲࠤࡹ࡫ࡳࡵࡪࡸࡦࠥ࡬࡯ࡳࠢࡨࡺࡪࡴࡴࡴࠢࡾࢁࠧ⇘").format(bstack1ll111_opy_ (u"࠭ࠬࠡࠩ⇙").join([event[bstack1ll111_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⇚")] for event in bstack111l1l1111_opy_])))
        response = bstack1l1l111111_opy_(bstack1ll111_opy_ (u"ࠨࡒࡒࡗ࡙࠭⇛"), cls.request_url(event_url), bstack111l1l1111_opy_, config)
        bstack11ll1l111ll_opy_ = response.json()
    @classmethod
    def bstack1lll111l11_opy_(cls, bstack111l1l1111_opy_, event_url=bstack1ll111_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨ⇜")):
        logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡪࡴࡤࡠࡦࡤࡸࡦࡀࠠࡂࡶࡷࡩࡲࡶࡴࡪࡰࡪࠤࡹࡵࠠࡢࡦࡧࠤࡩࡧࡴࡢࠢࡷࡳࠥࡨࡡࡵࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࡀࠠࡼࡿࠥ⇝").format(bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⇞")]))
        if not bstack1111ll11_opy_.bstack1llll111111l_opy_(bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⇟")]):
            logger.debug(bstack1ll111_opy_ (u"ࠨࡳࡦࡰࡧࡣࡩࡧࡴࡢ࠼ࠣࡒࡴࡺࠠࡢࡦࡧ࡭ࡳ࡭ࠠࡥࡣࡷࡥࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫࠺ࠡࡽࢀࠦ⇠").format(bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ⇡")]))
            return
        bstack1l11l111ll_opy_ = bstack1111ll11_opy_.bstack1llll1111ll1_opy_(bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⇢")], bstack111l1l1111_opy_.get(bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫ⇣")))
        if bstack1l11l111ll_opy_ != None:
            if bstack111l1l1111_opy_.get(bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬ⇤")) != None:
                bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭⇥")][bstack1ll111_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪ⇦")] = bstack1l11l111ll_opy_
            else:
                bstack111l1l1111_opy_[bstack1ll111_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺ࡟࡮ࡣࡳࠫ⇧")] = bstack1l11l111ll_opy_
        if event_url == bstack1ll111_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡣࡷࡧ࡭࠭⇨"):
            cls.bstack1llll111ll11_opy_()
            logger.debug(bstack1ll111_opy_ (u"ࠣࡵࡨࡲࡩࡥࡤࡢࡶࡤ࠾ࠥࡇࡤࡥ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡸࡴࠦࡢࡢࡶࡦ࡬ࠥࡽࡩࡵࡪࠣࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫࠺ࠡࡽࢀࠦ⇩").format(bstack111l1l1111_opy_[bstack1ll111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭⇪")]))
            cls.bstack1lllll1111ll_opy_.add(bstack111l1l1111_opy_)
        elif event_url == bstack1ll111_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ⇫"):
            cls.bstack1llll1111l11_opy_([bstack111l1l1111_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack11l1l1l111_opy_(cls, logs):
        for log in logs:
            bstack1lll1llll111_opy_ = {
                bstack1ll111_opy_ (u"ࠫࡰ࡯࡮ࡥࠩ⇬"): bstack1ll111_opy_ (u"࡚ࠬࡅࡔࡖࡢࡐࡔࡍࠧ⇭"),
                bstack1ll111_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⇮"): log[bstack1ll111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭⇯")],
                bstack1ll111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ⇰"): log[bstack1ll111_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ⇱")],
                bstack1ll111_opy_ (u"ࠪ࡬ࡹࡺࡰࡠࡴࡨࡷࡵࡵ࡮ࡴࡧࠪ⇲"): {},
                bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⇳"): log[bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⇴")],
            }
            if bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⇵") in log:
                bstack1lll1llll111_opy_[bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⇶")] = log[bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⇷")]
            elif bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⇸") in log:
                bstack1lll1llll111_opy_[bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⇹")] = log[bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⇺")]
            cls.bstack1lll111l11_opy_({
                bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⇻"): bstack1ll111_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪ⇼"),
                bstack1ll111_opy_ (u"ࠧ࡭ࡱࡪࡷࠬ⇽"): [bstack1lll1llll111_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1lll1llll1l1_opy_(cls, steps):
        bstack1lll1lllllll_opy_ = []
        for step in steps:
            bstack1llll1111l1l_opy_ = {
                bstack1ll111_opy_ (u"ࠨ࡭࡬ࡲࡩ࠭⇾"): bstack1ll111_opy_ (u"ࠩࡗࡉࡘ࡚࡟ࡔࡖࡈࡔࠬ⇿"),
                bstack1ll111_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ∀"): step[bstack1ll111_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ∁")],
                bstack1ll111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ∂"): step[bstack1ll111_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ∃")],
                bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ∄"): step[bstack1ll111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ∅")],
                bstack1ll111_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫ∆"): step[bstack1ll111_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࠬ∇")]
            }
            if bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ∈") in step:
                bstack1llll1111l1l_opy_[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ∉")] = step[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭∊")]
            elif bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ∋") in step:
                bstack1llll1111l1l_opy_[bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ∌")] = step[bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ∍")]
            bstack1lll1lllllll_opy_.append(bstack1llll1111l1l_opy_)
        cls.bstack1lll111l11_opy_({
            bstack1ll111_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ∎"): bstack1ll111_opy_ (u"ࠫࡑࡵࡧࡄࡴࡨࡥࡹ࡫ࡤࠨ∏"),
            bstack1ll111_opy_ (u"ࠬࡲ࡯ࡨࡵࠪ∐"): bstack1lll1lllllll_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11llll11ll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1lll1lllll_opy_(cls, screenshot):
        cls.bstack1lll111l11_opy_({
            bstack1ll111_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ∑"): bstack1ll111_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ−"),
            bstack1ll111_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭∓"): [{
                bstack1ll111_opy_ (u"ࠩ࡮࡭ࡳࡪࠧ∔"): bstack1ll111_opy_ (u"ࠪࡘࡊ࡙ࡔࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࠬ∕"),
                bstack1ll111_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ∖"): datetime.datetime.utcnow().isoformat() + bstack1ll111_opy_ (u"ࠬࡠࠧ∗"),
                bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ∘"): screenshot[bstack1ll111_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭∙")],
                bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ√"): screenshot[bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ∛")]
            }]
        }, event_url=bstack1ll111_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ∜"))
    @classmethod
    @error_handler(class_method=True)
    def bstack11l1llll11_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1lll111l11_opy_({
            bstack1ll111_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ∝"): bstack1ll111_opy_ (u"ࠬࡉࡂࡕࡕࡨࡷࡸ࡯࡯࡯ࡅࡵࡩࡦࡺࡥࡥࠩ∞"),
            bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ∟"): {
                bstack1ll111_opy_ (u"ࠢࡶࡷ࡬ࡨࠧ∠"): cls.current_test_uuid(),
                bstack1ll111_opy_ (u"ࠣ࡫ࡱࡸࡪ࡭ࡲࡢࡶ࡬ࡳࡳࡹࠢ∡"): cls.bstack111l1lll1l_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll1111l_opy_(cls, event: str, bstack111l1l1111_opy_: bstack111l1l11l1_opy_):
        bstack111l111l1l_opy_ = {
            bstack1ll111_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭∢"): event,
            bstack111l1l1111_opy_.bstack111l1l11ll_opy_(): bstack111l1l1111_opy_.bstack1111lll1l1_opy_(event)
        }
        cls.bstack1lll111l11_opy_(bstack111l111l1l_opy_)
        result = getattr(bstack111l1l1111_opy_, bstack1ll111_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ∣"), None)
        if event == bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬ∤"):
            threading.current_thread().bstackTestMeta = {bstack1ll111_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ∥"): bstack1ll111_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧ∦")}
        elif event == bstack1ll111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ∧"):
            threading.current_thread().bstackTestMeta = {bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ∨"): getattr(result, bstack1ll111_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ∩"), bstack1ll111_opy_ (u"ࠪࠫ∪"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ∫"), None) is None or os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ∬")] == bstack1ll111_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦ∭")) and (os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ∮"), None) is None or os.environ[bstack1ll111_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭∯")] == bstack1ll111_opy_ (u"ࠤࡱࡹࡱࡲࠢ∰")):
            return False
        return True
    @staticmethod
    def bstack1lll1llllll1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack111l1l111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack1ll111_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ∱"): bstack1ll111_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ∲"),
            bstack1ll111_opy_ (u"ࠬ࡞࠭ࡃࡕࡗࡅࡈࡑ࠭ࡕࡇࡖࡘࡔࡖࡓࠨ∳"): bstack1ll111_opy_ (u"࠭ࡴࡳࡷࡨࠫ∴")
        }
        if os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ∵"), None):
            headers[bstack1ll111_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨ∶")] = bstack1ll111_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬ∷").format(os.environ[bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠢ∸")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack1ll111_opy_ (u"ࠫࢀࢃ࠯ࡼࡿࠪ∹").format(bstack1llll1111lll_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ∺"), None)
    @staticmethod
    def bstack111l1lll1l_opy_(driver):
        return {
            bstack11l1111llll_opy_(): bstack111l1lll11l_opy_(driver)
        }
    @staticmethod
    def bstack1llll111l1l1_opy_(exception_info, report):
        return [{bstack1ll111_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩ∻"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1llllll1l11_opy_(typename):
        if bstack1ll111_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥ∼") in typename:
            return bstack1ll111_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤ∽")
        return bstack1ll111_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥ∾")