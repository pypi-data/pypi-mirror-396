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
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111ll11ll1_opy_ import bstack111l1ll1ll_opy_, bstack111ll1l1l1_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
from bstack_utils.helper import bstack11111l1l1_opy_, bstack11ll1l111_opy_, Result
from bstack_utils.bstack111l1llll1_opy_ import bstack111l1l111_opy_
from bstack_utils.capture import bstack111l1lllll_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack11ll1lllll_opy_:
    def __init__(self):
        self.bstack111l1ll111_opy_ = bstack111l1lllll_opy_(self.bstack111l1ll1l1_opy_)
        self.tests = {}
    @staticmethod
    def bstack111l1ll1l1_opy_(log):
        if not (log[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧཁ")] and log[bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨག")].strip()):
            return
        active = bstack1llll1111_opy_.bstack111ll11lll_opy_()
        log = {
            bstack1ll111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧགྷ"): log[bstack1ll111_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨང")],
            bstack1ll111_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ཅ"): bstack11ll1l111_opy_(),
            bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬཆ"): log[bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ཇ")],
        }
        if active:
            if active[bstack1ll111_opy_ (u"࠭ࡴࡺࡲࡨࠫ཈")] == bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࠬཉ"):
                log[bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨཊ")] = active[bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩཋ")]
            elif active[bstack1ll111_opy_ (u"ࠪࡸࡾࡶࡥࠨཌ")] == bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࠩཌྷ"):
                log[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬཎ")] = active[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ཏ")]
        bstack111l1l111_opy_.bstack11l1l1l111_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111l1ll111_opy_.start()
        driver = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ཐ"), None)
        bstack111ll11ll1_opy_ = bstack111ll1l1l1_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack11ll1l111_opy_(),
            file_path=attrs.feature.filename,
            result=bstack1ll111_opy_ (u"ࠣࡲࡨࡲࡩ࡯࡮ࡨࠤད"),
            framework=bstack1ll111_opy_ (u"ࠩࡅࡩ࡭ࡧࡶࡦࠩདྷ"),
            scope=[attrs.feature.name],
            bstack111ll1ll11_opy_=bstack111l1l111_opy_.bstack111l1lll1l_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ན")] = bstack111ll11ll1_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡘࡺࡡࡳࡶࡨࡨࠬཔ"), bstack111ll11ll1_opy_)
    def end_test(self, attrs):
        bstack111ll1l1ll_opy_ = {
            bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥཕ"): attrs.feature.name,
            bstack1ll111_opy_ (u"ࠨࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠦབ"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111ll11ll1_opy_ = self.tests[current_test_uuid][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪབྷ")]
        meta = {
            bstack1ll111_opy_ (u"ࠣࡨࡨࡥࡹࡻࡲࡦࠤམ"): bstack111ll1l1ll_opy_,
            bstack1ll111_opy_ (u"ࠤࡶࡸࡪࡶࡳࠣཙ"): bstack111ll11ll1_opy_.meta.get(bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩཚ"), []),
            bstack1ll111_opy_ (u"ࠦࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨཛ"): {
                bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥཛྷ"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111ll11ll1_opy_.bstack111ll11l11_opy_(meta)
        bstack111ll11ll1_opy_.bstack111ll1l111_opy_(bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࠫཝ"), []))
        bstack111ll111l1_opy_, exception = self._111l1l1ll1_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll11l1l_opy_=[bstack111ll111l1_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪཞ")].stop(time=bstack11ll1l111_opy_(), duration=int(attrs.duration)*1000, result=bstack111l1lll11_opy_)
        bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪཟ"), self.tests[threading.current_thread().current_test_uuid][bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬའ")])
    def bstack1l11l111l1_opy_(self, attrs):
        bstack111l1l1l1l_opy_ = {
            bstack1ll111_opy_ (u"ࠪ࡭ࡩ࠭ཡ"): uuid4().__str__(),
            bstack1ll111_opy_ (u"ࠫࡰ࡫ࡹࡸࡱࡵࡨࠬར"): attrs.keyword,
            bstack1ll111_opy_ (u"ࠬࡹࡴࡦࡲࡢࡥࡷ࡭ࡵ࡮ࡧࡱࡸࠬལ"): [],
            bstack1ll111_opy_ (u"࠭ࡴࡦࡺࡷࠫཤ"): attrs.name,
            bstack1ll111_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫཥ"): bstack11ll1l111_opy_(),
            bstack1ll111_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨས"): bstack1ll111_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪཧ"),
            bstack1ll111_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨཨ"): bstack1ll111_opy_ (u"ࠫࠬཀྵ")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཪ")].add_step(bstack111l1l1l1l_opy_)
        threading.current_thread().current_step_uuid = bstack111l1l1l1l_opy_[bstack1ll111_opy_ (u"࠭ࡩࡥࠩཫ")]
    def bstack1llll1ll1_opy_(self, attrs):
        current_test_id = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫཬ"), None)
        current_step_uuid = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡶࡸࡪࡶ࡟ࡶࡷ࡬ࡨࠬ཭"), None)
        bstack111ll111l1_opy_, exception = self._111l1l1ll1_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll11l1l_opy_=[bstack111ll111l1_opy_])
        self.tests[current_test_id][bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ཮")].bstack111l1l1lll_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111l1lll11_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack111llll1_opy_(self, name, attrs):
        try:
            bstack111l1ll11l_opy_ = uuid4().__str__()
            self.tests[bstack111l1ll11l_opy_] = {}
            self.bstack111l1ll111_opy_.start()
            scopes = []
            driver = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩ཯"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡴࠩ཰")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111l1ll11l_opy_)
            if name in [bstack1ll111_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤཱ"), bstack1ll111_opy_ (u"ࠨࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠤི")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack1ll111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥཱིࠣ"), bstack1ll111_opy_ (u"ࠣࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥུࠣ")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack1ll111_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧཱུࠪ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111l1ll1ll_opy_(
                name=name,
                uuid=bstack111l1ll11l_opy_,
                started_at=bstack11ll1l111_opy_(),
                file_path=file_path,
                framework=bstack1ll111_opy_ (u"ࠥࡆࡪ࡮ࡡࡷࡧࠥྲྀ"),
                bstack111ll1ll11_opy_=bstack111l1l111_opy_.bstack111l1lll1l_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack1ll111_opy_ (u"ࠦࡵ࡫࡮ࡥ࡫ࡱ࡫ࠧཷ"),
                hook_type=name
            )
            self.tests[bstack111l1ll11l_opy_][bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡦࡺࡡࠣླྀ")] = hook_data
            current_test_id = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠥཹ"), None)
            if current_test_id:
                hook_data.bstack111ll1ll1l_opy_(current_test_id)
            if name == bstack1ll111_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ེࠦ"):
                threading.current_thread().before_all_hook_uuid = bstack111l1ll11l_opy_
            threading.current_thread().current_hook_uuid = bstack111l1ll11l_opy_
            bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠣࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠤཻ"), hook_data)
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡱࡦࡧࡺࡸࡲࡦࡦࠣ࡭ࡳࠦࡳࡵࡣࡵࡸࠥ࡮࡯ࡰ࡭ࠣࡩࡻ࡫࡮ࡵࡵ࠯ࠤ࡭ࡵ࡯࡬ࠢࡱࡥࡲ࡫࠺ࠡࠧࡶ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࠫࡳོࠣ"), name, e)
    def bstack1ll1lll111_opy_(self, attrs):
        bstack111ll111ll_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪཽࠧ"), None)
        hook_data = self.tests[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧཾ")]
        status = bstack1ll111_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧཿ")
        exception = None
        bstack111ll111l1_opy_ = None
        if hook_data.name == bstack1ll111_opy_ (u"ࠨࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠤྀ"):
            self.bstack111l1ll111_opy_.reset()
            bstack111ll11111_opy_ = self.tests[bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪཱྀࠧ"), None)][bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫྂ")].result.result
            if bstack111ll11111_opy_ == bstack1ll111_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤྃ"):
                if attrs.hook_failures == 1:
                    status = bstack1ll111_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦ྄ࠥ")
                elif attrs.hook_failures == 2:
                    status = bstack1ll111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ྅")
            elif attrs.aborted:
                status = bstack1ll111_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧ྆")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack1ll111_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠪ྇") and attrs.hook_failures == 1:
                status = bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢྈ")
            elif hasattr(attrs, bstack1ll111_opy_ (u"ࠨࡧࡵࡶࡴࡸ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠨྉ")) and attrs.error_message:
                status = bstack1ll111_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤྊ")
            bstack111ll111l1_opy_, exception = self._111l1l1ll1_opy_(attrs)
        bstack111l1lll11_opy_ = Result(result=status, exception=exception, bstack111ll11l1l_opy_=[bstack111ll111l1_opy_])
        hook_data.stop(time=bstack11ll1l111_opy_(), duration=0, result=bstack111l1lll11_opy_)
        bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠪࡌࡴࡵ࡫ࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬྋ"), self.tests[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧྌ")])
        threading.current_thread().current_hook_uuid = None
    def _111l1l1ll1_opy_(self, attrs):
        try:
            import traceback
            bstack11ll1l11l1_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111ll111l1_opy_ = bstack11ll1l11l1_opy_[-1] if bstack11ll1l11l1_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack1ll111_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡴࡩࡣࡶࡴࡵࡩࡩࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡣࡶࡵࡷࡳࡲࠦࡴࡳࡣࡦࡩࡧࡧࡣ࡬ࠤྍ"))
            bstack111ll111l1_opy_ = None
            exception = None
        return bstack111ll111l1_opy_, exception