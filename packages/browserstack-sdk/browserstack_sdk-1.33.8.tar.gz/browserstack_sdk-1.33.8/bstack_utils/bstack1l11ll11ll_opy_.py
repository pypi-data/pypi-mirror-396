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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11l1lll111l_opy_ import bstack11l1lll11ll_opy_
from bstack_utils.constants import bstack11l1l11l1ll_opy_, bstack11111111_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from bstack_utils import bstack1llll1ll1l_opy_
bstack11l11ll1ll1_opy_ = 10
class bstack11l11111ll_opy_:
    def __init__(self, bstack11l11ll1_opy_, config, bstack11l11ll1111_opy_=0):
        self.bstack11l11l1l1l1_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l11l1ll1l_opy_ = bstack1ll111_opy_ (u"ࠣࡽࢀ࠳ࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡨࡤ࡭ࡱ࡫ࡤ࠮ࡶࡨࡷࡹࡹࠢᬽ").format(bstack11l1l11l1ll_opy_)
        self.bstack11l11lll111_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠤࡤࡦࡴࡸࡴࡠࡤࡸ࡭ࡱࡪ࡟ࡼࡿࠥᬾ").format(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᬿ"))))
        self.bstack11l11ll1l11_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡣࡹ࡫ࡳࡵࡵࡢࡿࢂ࠴ࡴࡹࡶࠥᭀ").format(os.environ.get(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᭁ"))))
        self.bstack11l11l1l11l_opy_ = 2
        self.bstack11l11ll1_opy_ = bstack11l11ll1_opy_
        self.config = config
        self.logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack11111111_opy_)
        self.bstack11l11ll1111_opy_ = bstack11l11ll1111_opy_
        self.bstack11l11l1l111_opy_ = False
        self.bstack11l11l1ll11_opy_ = not (
                            os.environ.get(bstack1ll111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠧᭂ")) and
                            os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥᭃ")) and
                            os.environ.get(bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡑࡗࡅࡑࡥࡎࡐࡆࡈࡣࡈࡕࡕࡏࡖ᭄ࠥ"))
                        )
        if bstack11ll1lll1l_opy_.bstack11l11ll111l_opy_(config):
            self.bstack11l11l1l11l_opy_ = bstack11ll1lll1l_opy_.bstack11l11lll1l1_opy_(config, self.bstack11l11ll1111_opy_)
            self.bstack11l11l1llll_opy_()
    def bstack11l11lll1ll_opy_(self):
        return bstack1ll111_opy_ (u"ࠤࡾࢁࡤࢁࡽࠣᭅ").format(self.config.get(bstack1ll111_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ᭆ")), os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪᭇ")))
    def bstack11l11ll1l1l_opy_(self):
        try:
            if self.bstack11l11l1ll11_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l11ll1l11_opy_, bstack1ll111_opy_ (u"ࠧࡸࠢᭈ")) as f:
                        bstack11l11l1l1ll_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l11l1l1ll_opy_ = set()
                bstack11l11ll11ll_opy_ = bstack11l11l1l1ll_opy_ - self.bstack11l11l1l1l1_opy_
                if not bstack11l11ll11ll_opy_:
                    return
                self.bstack11l11l1l1l1_opy_.update(bstack11l11ll11ll_opy_)
                data = {bstack1ll111_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩ࡚ࡥࡴࡶࡶࠦᭉ"): list(self.bstack11l11l1l1l1_opy_), bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠥᭊ"): self.config.get(bstack1ll111_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᭋ")), bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢᭌ"): os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩ᭍")), bstack1ll111_opy_ (u"ࠦࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠤ᭎"): self.config.get(bstack1ll111_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᭏"))}
            response = bstack11l1lll11ll_opy_.bstack11l11l11lll_opy_(self.bstack11l11l1ll1l_opy_, data)
            if response.get(bstack1ll111_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨ᭐")) == 200:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡳࡦࡰࡷࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢ᭑").format(data))
            else:
                self.logger.debug(bstack1ll111_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫࡮ࡥࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧ᭒").format(response))
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡪࡵࡳ࡫ࡱ࡫ࠥࡹࡥ࡯ࡦ࡬ࡲ࡬ࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷ࠿ࠦࡻࡾࠤ᭓").format(e))
    def bstack11l11l1lll1_opy_(self):
        if self.bstack11l11l1ll11_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l11ll1l11_opy_, bstack1ll111_opy_ (u"ࠥࡶࠧ᭔")) as f:
                        bstack11l11ll1lll_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l11ll1lll_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack1ll111_opy_ (u"ࠦࡕࡵ࡬࡭ࡧࡧࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡧࡴࡻ࡮ࡵࠢࠫࡰࡴࡩࡡ࡭ࠫ࠽ࠤࢀࢃࠢ᭕").format(failed_count))
                if failed_count >= self.bstack11l11l1l11l_opy_:
                    self.logger.info(bstack1ll111_opy_ (u"࡚ࠧࡨࡳࡧࡶ࡬ࡴࡲࡤࠡࡥࡵࡳࡸࡹࡥࡥࠢࠫࡰࡴࡩࡡ࡭ࠫ࠽ࠤࢀࢃࠠ࠿࠿ࠣࡿࢂࠨ᭖").format(failed_count, self.bstack11l11l1l11l_opy_))
                    self.bstack11l11ll11l1_opy_(failed_count)
                    self.bstack11l11l1l111_opy_ = True
            return
        try:
            response = bstack11l1lll11ll_opy_.bstack11l11l1lll1_opy_(bstack1ll111_opy_ (u"ࠨࡻࡾࡁࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࡂࢁࡽࠧࡤࡸ࡭ࡱࡪࡒࡶࡰࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࡃࡻࡾࠨࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫࠽ࡼࡿࠥ᭗").format(self.bstack11l11l1ll1l_opy_, self.config.get(bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ᭘")), os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧ᭙")), self.config.get(bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧ᭚"))))
            if response.get(bstack1ll111_opy_ (u"ࠥࡷࡹࡧࡴࡶࡵࠥ᭛")) == 200:
                failed_count = response.get(bstack1ll111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࡘࡪࡹࡴࡴࡅࡲࡹࡳࡺࠢ᭜"), 0)
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡖ࡯࡭࡮ࡨࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠤࡨࡵࡵ࡯ࡶ࠽ࠤࢀࢃࠢ᭝").format(failed_count))
                if failed_count >= self.bstack11l11l1l11l_opy_:
                    self.logger.info(bstack1ll111_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦ࠽ࠤࢀࢃࠠ࠿࠿ࠣࡿࢂࠨ᭞").format(failed_count, self.bstack11l11l1l11l_opy_))
                    self.bstack11l11ll11l1_opy_(failed_count)
                    self.bstack11l11l1l111_opy_ = True
            else:
                self.logger.error(bstack1ll111_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡴࡲ࡬ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹ࠺ࠡࡽࢀࠦ᭟").format(response))
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡩࡻࡲࡪࡰࡪࠤࡵࡵ࡬࡭࡫ࡱ࡫࠿ࠦࡻࡾࠤ᭠").format(e))
    def bstack11l11ll11l1_opy_(self, failed_count):
        with open(self.bstack11l11lll111_opy_, bstack1ll111_opy_ (u"ࠤࡺࠦ᭡")) as f:
            f.write(bstack1ll111_opy_ (u"ࠥࡘ࡭ࡸࡥࡴࡪࡲࡰࡩࠦࡣࡳࡱࡶࡷࡪࡪࠠࡢࡶࠣࡿࢂࡢ࡮ࠣ᭢").format(datetime.now()))
            f.write(bstack1ll111_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵࠣࡧࡴࡻ࡮ࡵ࠼ࠣࡿࢂࡢ࡮ࠣ᭣").format(failed_count))
        self.logger.debug(bstack1ll111_opy_ (u"ࠧࡇࡢࡰࡴࡷࠤࡇࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡥࡥ࠼ࠣࡿࢂࠨ᭤").format(self.bstack11l11lll111_opy_))
    def bstack11l11l1llll_opy_(self):
        def bstack11l11lll11l_opy_():
            while not self.bstack11l11l1l111_opy_:
                time.sleep(bstack11l11ll1ll1_opy_)
                self.bstack11l11ll1l1l_opy_()
                self.bstack11l11l1lll1_opy_()
        bstack11l11llll11_opy_ = threading.Thread(target=bstack11l11lll11l_opy_, daemon=True)
        bstack11l11llll11_opy_.start()