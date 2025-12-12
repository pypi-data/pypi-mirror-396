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
from uuid import uuid4
from itertools import zip_longest
from collections import OrderedDict
from robot.libraries.BuiltIn import BuiltIn
from browserstack_sdk.bstack1111l1l1l1_opy_ import RobotHandler
from bstack_utils.capture import bstack111l1lllll_opy_
from bstack_utils.bstack111ll11ll1_opy_ import bstack111l1l11l1_opy_, bstack111l1ll1ll_opy_, bstack111ll1l1l1_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
from bstack_utils.bstack111l1llll1_opy_ import bstack111l1l111_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack11111l1l1_opy_, bstack11ll1l111_opy_, Result, \
    error_handler, bstack1111l1lll1_opy_
class bstack_robot_listener:
    ROBOT_LISTENER_API_VERSION = 2
    _lock = threading.Lock()
    store = {
        bstack1ll111_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪྎ"): [],
        bstack1ll111_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࡟ࡩࡱࡲ࡯ࡸ࠭ྏ"): [],
        bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬྐ"): []
    }
    bstack1111ll1l11_opy_ = []
    bstack1111lllll1_opy_ = []
    @staticmethod
    def bstack111l1ll1l1_opy_(log):
        if not ((isinstance(log[bstack1ll111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪྑ")], list) or (isinstance(log[bstack1ll111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫྒ")], dict)) and len(log[bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྒྷ")])>0) or (isinstance(log[bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ྔ")], str) and log[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧྕ")].strip())):
            return
        active = bstack1llll1111_opy_.bstack111ll11lll_opy_()
        log = {
            bstack1ll111_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ྖ"): log[bstack1ll111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧྗ")],
            bstack1ll111_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ྘"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"ࠪ࡞ࠬྙ"),
            bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬྚ"): log[bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ྛ")],
        }
        if active:
            if active[bstack1ll111_opy_ (u"࠭ࡴࡺࡲࡨࠫྜ")] == bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࠬྜྷ"):
                log[bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨྞ")] = active[bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩྟ")]
            elif active[bstack1ll111_opy_ (u"ࠪࡸࡾࡶࡥࠨྠ")] == bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࠩྡ"):
                log[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬྡྷ")] = active[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ྣ")]
        bstack111l1l111_opy_.bstack11l1l1l111_opy_([log])
    def __init__(self):
        self.messages = bstack1111ll1lll_opy_()
        self._1111l1ll1l_opy_ = None
        self._1111lll1ll_opy_ = None
        self._1111ll11ll_opy_ = OrderedDict()
        self.bstack111l1ll111_opy_ = bstack111l1lllll_opy_(self.bstack111l1ll1l1_opy_)
    @error_handler(class_method=True)
    def start_suite(self, name, attrs):
        self.messages.bstack1111l1l11l_opy_()
        if not self._1111ll11ll_opy_.get(attrs.get(bstack1ll111_opy_ (u"ࠧࡪࡦࠪྤ")), None):
            self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"ࠨ࡫ࡧࠫྥ"))] = {}
        bstack1111llll1l_opy_ = bstack111ll1l1l1_opy_(
                bstack111l1l111l_opy_=attrs.get(bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬྦ")),
                name=name,
                started_at=bstack11ll1l111_opy_(),
                file_path=os.path.relpath(attrs[bstack1ll111_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪྦྷ")], start=os.getcwd()) if attrs.get(bstack1ll111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫྨ")) != bstack1ll111_opy_ (u"ࠬ࠭ྩ") else bstack1ll111_opy_ (u"࠭ࠧྪ"),
                framework=bstack1ll111_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭ྫ")
            )
        threading.current_thread().current_suite_id = attrs.get(bstack1ll111_opy_ (u"ࠨ࡫ࡧࠫྫྷ"), None)
        self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬྭ"))][bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ྮ")] = bstack1111llll1l_opy_
    @error_handler(class_method=True)
    def end_suite(self, name, attrs):
        messages = self.messages.bstack111l1111ll_opy_()
        self._111l11lll1_opy_(messages)
        with self._lock:
            for bstack1111l1l1ll_opy_ in self.bstack1111ll1l11_opy_:
                bstack1111l1l1ll_opy_[bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭ྯ")][bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫྰ")].extend(self.store[bstack1ll111_opy_ (u"࠭ࡧ࡭ࡱࡥࡥࡱࡥࡨࡰࡱ࡮ࡷࠬྱ")])
                bstack111l1l111_opy_.bstack1lll111l11_opy_(bstack1111l1l1ll_opy_)
            self.bstack1111ll1l11_opy_ = []
            self.store[bstack1ll111_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࡟ࡩࡱࡲ࡯ࡸ࠭ྲ")] = []
    @error_handler(class_method=True)
    def start_test(self, name, attrs):
        self.bstack111l1ll111_opy_.start()
        if not self._1111ll11ll_opy_.get(attrs.get(bstack1ll111_opy_ (u"ࠨ࡫ࡧࠫླ")), None):
            self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬྴ"))] = {}
        driver = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩྵ"), None)
        bstack111ll11ll1_opy_ = bstack111ll1l1l1_opy_(
            bstack111l1l111l_opy_=attrs.get(bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧྶ")),
            name=name,
            started_at=bstack11ll1l111_opy_(),
            file_path=os.path.relpath(attrs[bstack1ll111_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬྷ")], start=os.getcwd()),
            scope=RobotHandler.bstack111l111l11_opy_(attrs.get(bstack1ll111_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ྸ"), None)),
            framework=bstack1ll111_opy_ (u"ࠧࡓࡱࡥࡳࡹ࠭ྐྵ"),
            tags=attrs[bstack1ll111_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ྺ")],
            hooks=self.store[bstack1ll111_opy_ (u"ࠩࡪࡰࡴࡨࡡ࡭ࡡ࡫ࡳࡴࡱࡳࠨྻ")],
            bstack111ll1ll11_opy_=bstack111l1l111_opy_.bstack111l1lll1l_opy_(driver) if driver and driver.session_id else {},
            meta={},
            code=bstack1ll111_opy_ (u"ࠥࡿࢂࠦ࡜࡯ࠢࡾࢁࠧྼ").format(bstack1ll111_opy_ (u"ࠦࠥࠨ྽").join(attrs[bstack1ll111_opy_ (u"ࠬࡺࡡࡨࡵࠪ྾")]), name) if attrs[bstack1ll111_opy_ (u"࠭ࡴࡢࡩࡶࠫ྿")] else name
        )
        self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"ࠧࡪࡦࠪ࿀"))][bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ࿁")] = bstack111ll11ll1_opy_
        threading.current_thread().current_test_uuid = bstack111ll11ll1_opy_.bstack111l11llll_opy_()
        threading.current_thread().current_test_id = attrs.get(bstack1ll111_opy_ (u"ࠩ࡬ࡨࠬ࿂"), None)
        self.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ࿃"), bstack111ll11ll1_opy_)
    @error_handler(class_method=True)
    def end_test(self, name, attrs):
        self.bstack111l1ll111_opy_.reset()
        bstack1111llllll_opy_ = bstack1111lll11l_opy_.get(attrs.get(bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ࿄")), bstack1ll111_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭࿅"))
        self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"࠭ࡩࡥ࿆ࠩ"))][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ࿇")].stop(time=bstack11ll1l111_opy_(), duration=int(attrs.get(bstack1ll111_opy_ (u"ࠨࡧ࡯ࡥࡵࡹࡥࡥࡶ࡬ࡱࡪ࠭࿈"), bstack1ll111_opy_ (u"ࠩ࠳ࠫ࿉"))), result=Result(result=bstack1111llllll_opy_, exception=attrs.get(bstack1ll111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ࿊")), bstack111ll11l1l_opy_=[attrs.get(bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ࿋"))]))
        self.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ࿌"), self._1111ll11ll_opy_[attrs.get(bstack1ll111_opy_ (u"࠭ࡩࡥࠩ࿍"))][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ࿎")], True)
        with self._lock:
            self.store[bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬ࿏")] = []
        threading.current_thread().current_test_uuid = None
        threading.current_thread().current_test_id = None
    @error_handler(class_method=True)
    def start_keyword(self, name, attrs):
        self.messages.bstack1111l1l11l_opy_()
        current_test_id = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡧࠫ࿐"), None)
        bstack111l11l11l_opy_ = current_test_id if bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡨࠬ࿑"), None) else bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡹࡵࡪࡶࡨࡣ࡮ࡪࠧ࿒"), None)
        if attrs.get(bstack1ll111_opy_ (u"ࠬࡺࡹࡱࡧࠪ࿓"), bstack1ll111_opy_ (u"࠭ࠧ࿔")).lower() in [bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭࿕"), bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ࿖")]:
            hook_type = bstack1111ll1ll1_opy_(attrs.get(bstack1ll111_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ࿗")), bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧ࿘"), None))
            hook_name = bstack1ll111_opy_ (u"ࠫࢀࢃࠧ࿙").format(attrs.get(bstack1ll111_opy_ (u"ࠬࡱࡷ࡯ࡣࡰࡩࠬ࿚"), bstack1ll111_opy_ (u"࠭ࠧ࿛")))
            if hook_type in [bstack1ll111_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡂࡎࡏࠫ࿜"), bstack1ll111_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡂࡎࡏࠫ࿝")]:
                hook_name = bstack1ll111_opy_ (u"ࠩ࡞ࡿࢂࡣࠠࡼࡿࠪ࿞").format(bstack111l11l1l1_opy_.get(hook_type), attrs.get(bstack1ll111_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪ࿟"), bstack1ll111_opy_ (u"ࠫࠬ࿠")))
            bstack111l1111l1_opy_ = bstack111l1ll1ll_opy_(
                bstack111l1l111l_opy_=bstack111l11l11l_opy_ + bstack1ll111_opy_ (u"ࠬ࠳ࠧ࿡") + attrs.get(bstack1ll111_opy_ (u"࠭ࡴࡺࡲࡨࠫ࿢"), bstack1ll111_opy_ (u"ࠧࠨ࿣")).lower(),
                name=hook_name,
                started_at=bstack11ll1l111_opy_(),
                file_path=os.path.relpath(attrs.get(bstack1ll111_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ࿤")), start=os.getcwd()),
                framework=bstack1ll111_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨ࿥"),
                tags=attrs[bstack1ll111_opy_ (u"ࠪࡸࡦ࡭ࡳࠨ࿦")],
                scope=RobotHandler.bstack111l111l11_opy_(attrs.get(bstack1ll111_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫ࿧"), None)),
                hook_type=hook_type,
                meta={}
            )
            threading.current_thread().current_hook_uuid = bstack111l1111l1_opy_.bstack111l11llll_opy_()
            threading.current_thread().current_hook_id = bstack111l11l11l_opy_ + bstack1ll111_opy_ (u"ࠬ࠳ࠧ࿨") + attrs.get(bstack1ll111_opy_ (u"࠭ࡴࡺࡲࡨࠫ࿩"), bstack1ll111_opy_ (u"ࠧࠨ࿪")).lower()
            with self._lock:
                self.store[bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ࿫")] = [bstack111l1111l1_opy_.bstack111l11llll_opy_()]
                if bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭࿬"), None):
                    self.store[bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡪࡲࡳࡰࡹࠧ࿭")].append(bstack111l1111l1_opy_.bstack111l11llll_opy_())
                else:
                    self.store[bstack1ll111_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡣ࡭ࡵ࡯࡬ࡵࠪ࿮")].append(bstack111l1111l1_opy_.bstack111l11llll_opy_())
            if bstack111l11l11l_opy_:
                self._1111ll11ll_opy_[bstack111l11l11l_opy_ + bstack1ll111_opy_ (u"ࠬ࠳ࠧ࿯") + attrs.get(bstack1ll111_opy_ (u"࠭ࡴࡺࡲࡨࠫ࿰"), bstack1ll111_opy_ (u"ࠧࠨ࿱")).lower()] = { bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ࿲"): bstack111l1111l1_opy_ }
            bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠪ࿳"), bstack111l1111l1_opy_)
        else:
            bstack111l1l1l1l_opy_ = {
                bstack1ll111_opy_ (u"ࠪ࡭ࡩ࠭࿴"): uuid4().__str__(),
                bstack1ll111_opy_ (u"ࠫࡹ࡫ࡸࡵࠩ࿵"): bstack1ll111_opy_ (u"ࠬࢁࡽࠡࡽࢀࠫ࿶").format(attrs.get(bstack1ll111_opy_ (u"࠭࡫ࡸࡰࡤࡱࡪ࠭࿷")), attrs.get(bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡷࠬ࿸"), bstack1ll111_opy_ (u"ࠨࠩ࿹"))) if attrs.get(bstack1ll111_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ࿺"), []) else attrs.get(bstack1ll111_opy_ (u"ࠪ࡯ࡼࡴࡡ࡮ࡧࠪ࿻")),
                bstack1ll111_opy_ (u"ࠫࡸࡺࡥࡱࡡࡤࡶ࡬ࡻ࡭ࡦࡰࡷࠫ࿼"): attrs.get(bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪ࿽"), []),
                bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ࿾"): bstack11ll1l111_opy_(),
                bstack1ll111_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ࿿"): bstack1ll111_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩက"),
                bstack1ll111_opy_ (u"ࠩࡧࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧခ"): attrs.get(bstack1ll111_opy_ (u"ࠪࡨࡴࡩࠧဂ"), bstack1ll111_opy_ (u"ࠫࠬဃ"))
            }
            if attrs.get(bstack1ll111_opy_ (u"ࠬࡲࡩࡣࡰࡤࡱࡪ࠭င"), bstack1ll111_opy_ (u"࠭ࠧစ")) != bstack1ll111_opy_ (u"ࠧࠨဆ"):
                bstack111l1l1l1l_opy_[bstack1ll111_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩဇ")] = attrs.get(bstack1ll111_opy_ (u"ࠩ࡯࡭ࡧࡴࡡ࡮ࡧࠪဈ"))
            if not self.bstack1111lllll1_opy_:
                self._1111ll11ll_opy_[self._1111ll11l1_opy_()][bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ဉ")].add_step(bstack111l1l1l1l_opy_)
                threading.current_thread().current_step_uuid = bstack111l1l1l1l_opy_[bstack1ll111_opy_ (u"ࠫ࡮ࡪࠧည")]
            self.bstack1111lllll1_opy_.append(bstack111l1l1l1l_opy_)
    @error_handler(class_method=True)
    def end_keyword(self, name, attrs):
        messages = self.messages.bstack111l1111ll_opy_()
        self._111l11lll1_opy_(messages)
        current_test_id = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡪࠧဋ"), None)
        bstack111l11l11l_opy_ = current_test_id if current_test_id else bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡴࡷ࡬ࡸࡪࡥࡩࡥࠩဌ"), None)
        bstack1111l1ll11_opy_ = bstack1111lll11l_opy_.get(attrs.get(bstack1ll111_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧဍ")), bstack1ll111_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩဎ"))
        bstack1111lll111_opy_ = attrs.get(bstack1ll111_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪဏ"))
        if bstack1111l1ll11_opy_ != bstack1ll111_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫတ") and not attrs.get(bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬထ")) and self._1111l1ll1l_opy_:
            bstack1111lll111_opy_ = self._1111l1ll1l_opy_
        bstack111l1lll11_opy_ = Result(result=bstack1111l1ll11_opy_, exception=bstack1111lll111_opy_, bstack111ll11l1l_opy_=[bstack1111lll111_opy_])
        if attrs.get(bstack1ll111_opy_ (u"ࠬࡺࡹࡱࡧࠪဒ"), bstack1ll111_opy_ (u"࠭ࠧဓ")).lower() in [bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭န"), bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪပ")]:
            bstack111l11l11l_opy_ = current_test_id if current_test_id else bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡷࡺ࡯ࡴࡦࡡ࡬ࡨࠬဖ"), None)
            if bstack111l11l11l_opy_:
                bstack111ll111ll_opy_ = bstack111l11l11l_opy_ + bstack1ll111_opy_ (u"ࠥ࠱ࠧဗ") + attrs.get(bstack1ll111_opy_ (u"ࠫࡹࡿࡰࡦࠩဘ"), bstack1ll111_opy_ (u"ࠬ࠭မ")).lower()
                self._1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩယ")].stop(time=bstack11ll1l111_opy_(), duration=int(attrs.get(bstack1ll111_opy_ (u"ࠧࡦ࡮ࡤࡴࡸ࡫ࡤࡵ࡫ࡰࡩࠬရ"), bstack1ll111_opy_ (u"ࠨ࠲ࠪလ"))), result=bstack111l1lll11_opy_)
                bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫဝ"), self._1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭သ")])
        else:
            bstack111l11l11l_opy_ = current_test_id if current_test_id else bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢ࡭ࡩ࠭ဟ"), None)
            if bstack111l11l11l_opy_ and len(self.bstack1111lllll1_opy_) == 1:
                current_step_uuid = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡳࡵࡧࡳࡣࡺࡻࡩࡥࠩဠ"), None)
                self._1111ll11ll_opy_[bstack111l11l11l_opy_][bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩအ")].bstack111l1l1lll_opy_(current_step_uuid, duration=int(attrs.get(bstack1ll111_opy_ (u"ࠧࡦ࡮ࡤࡴࡸ࡫ࡤࡵ࡫ࡰࡩࠬဢ"), bstack1ll111_opy_ (u"ࠨ࠲ࠪဣ"))), result=bstack111l1lll11_opy_)
            else:
                self.bstack1111l11ll1_opy_(attrs)
            self.bstack1111lllll1_opy_.pop()
    def log_message(self, message):
        try:
            if message.get(bstack1ll111_opy_ (u"ࠩ࡫ࡸࡲࡲࠧဤ"), bstack1ll111_opy_ (u"ࠪࡲࡴ࠭ဥ")) == bstack1ll111_opy_ (u"ࠫࡾ࡫ࡳࠨဦ"):
                return
            self.messages.push(message)
            logs = []
            if bstack1llll1111_opy_.bstack111ll11lll_opy_():
                logs.append({
                    bstack1ll111_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨဧ"): bstack11ll1l111_opy_(),
                    bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧဨ"): message.get(bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨဩ")),
                    bstack1ll111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧဪ"): message.get(bstack1ll111_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨါ")),
                    **bstack1llll1111_opy_.bstack111ll11lll_opy_()
                })
                if len(logs) > 0:
                    bstack111l1l111_opy_.bstack11l1l1l111_opy_(logs)
        except Exception as err:
            pass
    def close(self):
        bstack111l1l111_opy_.bstack111l11l1ll_opy_()
    def bstack1111l11ll1_opy_(self, bstack111l11l111_opy_):
        if not bstack1llll1111_opy_.bstack111ll11lll_opy_():
            return
        kwname = bstack1ll111_opy_ (u"ࠪࡿࢂࠦࡻࡾࠩာ").format(bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠫࡰࡽ࡮ࡢ࡯ࡨࠫိ")), bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠬࡧࡲࡨࡵࠪီ"), bstack1ll111_opy_ (u"࠭ࠧု"))) if bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠧࡢࡴࡪࡷࠬူ"), []) else bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠨ࡭ࡺࡲࡦࡳࡥࠨေ"))
        error_message = bstack1ll111_opy_ (u"ࠤ࡮ࡻࡳࡧ࡭ࡦ࠼ࠣࡠࠧࢁ࠰ࡾ࡞ࠥࠤࢁࠦࡳࡵࡣࡷࡹࡸࡀࠠ࡝ࠤࡾ࠵ࢂࡢࠢࠡࡾࠣࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠ࡝ࠤࡾ࠶ࢂࡢࠢࠣဲ").format(kwname, bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪဳ")), str(bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬဴ"))))
        bstack111l11ll1l_opy_ = bstack1ll111_opy_ (u"ࠧࡱࡷ࡯ࡣࡰࡩ࠿ࠦ࡜ࠣࡽ࠳ࢁࡡࠨࠠࡽࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࡠࠧࢁ࠱ࡾ࡞ࠥࠦဵ").format(kwname, bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ံ")))
        bstack111l111ll1_opy_ = error_message if bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ့")) else bstack111l11ll1l_opy_
        bstack1111ll1l1l_opy_ = {
            bstack1ll111_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫး"): self.bstack1111lllll1_opy_[-1].get(bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ္࠭"), bstack11ll1l111_opy_()),
            bstack1ll111_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨ်ࠫ"): bstack111l111ll1_opy_,
            bstack1ll111_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪျ"): bstack1ll111_opy_ (u"ࠬࡋࡒࡓࡑࡕࠫြ") if bstack111l11l111_opy_.get(bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ွ")) == bstack1ll111_opy_ (u"ࠧࡇࡃࡌࡐࠬှ") else bstack1ll111_opy_ (u"ࠨࡋࡑࡊࡔ࠭ဿ"),
            **bstack1llll1111_opy_.bstack111ll11lll_opy_()
        }
        bstack111l1l111_opy_.bstack11l1l1l111_opy_([bstack1111ll1l1l_opy_])
    def _1111ll11l1_opy_(self):
        for bstack111l1l111l_opy_ in reversed(self._1111ll11ll_opy_):
            bstack111l111lll_opy_ = bstack111l1l111l_opy_
            data = self._1111ll11ll_opy_[bstack111l1l111l_opy_][bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ၀")]
            if isinstance(data, bstack111l1ll1ll_opy_):
                if not bstack1ll111_opy_ (u"ࠪࡉࡆࡉࡈࠨ၁") in data.bstack1111ll111l_opy_():
                    return bstack111l111lll_opy_
            else:
                return bstack111l111lll_opy_
    def _111l11lll1_opy_(self, messages):
        try:
            bstack1111l11lll_opy_ = BuiltIn().get_variable_value(bstack1ll111_opy_ (u"ࠦࠩࢁࡌࡐࡉࠣࡐࡊ࡜ࡅࡍࡿࠥ၂")) in (bstack1111ll1111_opy_.DEBUG, bstack1111ll1111_opy_.TRACE)
            for message, bstack111l111111_opy_ in zip_longest(messages, messages[1:]):
                name = message.get(bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭၃"))
                level = message.get(bstack1ll111_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ၄"))
                if level == bstack1111ll1111_opy_.FAIL:
                    self._1111l1ll1l_opy_ = name or self._1111l1ll1l_opy_
                    self._1111lll1ll_opy_ = bstack111l111111_opy_.get(bstack1ll111_opy_ (u"ࠢ࡮ࡧࡶࡷࡦ࡭ࡥࠣ၅")) if bstack1111l11lll_opy_ and bstack111l111111_opy_ else self._1111lll1ll_opy_
        except:
            pass
    @classmethod
    def bstack111ll1111l_opy_(self, event: str, bstack111l1l1111_opy_: bstack111l1l11l1_opy_, bstack111l11ll11_opy_=False):
        if event == bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪ၆"):
            bstack111l1l1111_opy_.set(hooks=self.store[bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸ࠭၇")])
        if event == bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ၈"):
            event = bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭၉")
        if bstack111l11ll11_opy_:
            bstack111l111l1l_opy_ = {
                bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ၊"): event,
                bstack111l1l1111_opy_.bstack111l1l11ll_opy_(): bstack111l1l1111_opy_.bstack1111lll1l1_opy_(event)
            }
            with self._lock:
                self.bstack1111ll1l11_opy_.append(bstack111l111l1l_opy_)
        else:
            bstack111l1l111_opy_.bstack111ll1111l_opy_(event, bstack111l1l1111_opy_)
class bstack1111ll1lll_opy_:
    def __init__(self):
        self._1111llll11_opy_ = []
    def bstack1111l1l11l_opy_(self):
        self._1111llll11_opy_.append([])
    def bstack111l1111ll_opy_(self):
        return self._1111llll11_opy_.pop() if self._1111llll11_opy_ else list()
    def push(self, message):
        self._1111llll11_opy_[-1].append(message) if self._1111llll11_opy_ else self._1111llll11_opy_.append([message])
class bstack1111ll1111_opy_:
    FAIL = bstack1ll111_opy_ (u"࠭ࡆࡂࡋࡏࠫ။")
    ERROR = bstack1ll111_opy_ (u"ࠧࡆࡔࡕࡓࡗ࠭၌")
    WARNING = bstack1ll111_opy_ (u"ࠨ࡙ࡄࡖࡓ࠭၍")
    bstack1111l1l111_opy_ = bstack1ll111_opy_ (u"ࠩࡌࡒࡋࡕࠧ၎")
    DEBUG = bstack1ll111_opy_ (u"ࠪࡈࡊࡈࡕࡈࠩ၏")
    TRACE = bstack1ll111_opy_ (u"࡙ࠫࡘࡁࡄࡇࠪၐ")
    bstack111l11111l_opy_ = [FAIL, ERROR]
def bstack1111l1llll_opy_(bstack111l1l1l11_opy_):
    if not bstack111l1l1l11_opy_:
        return None
    if bstack111l1l1l11_opy_.get(bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨၑ"), None):
        return getattr(bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩၒ")], bstack1ll111_opy_ (u"ࠧࡶࡷ࡬ࡨࠬၓ"), None)
    return bstack111l1l1l11_opy_.get(bstack1ll111_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ၔ"), None)
def bstack1111ll1ll1_opy_(hook_type, current_test_uuid):
    if hook_type.lower() not in [bstack1ll111_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨၕ"), bstack1ll111_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬၖ")]:
        return
    if hook_type.lower() == bstack1ll111_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪၗ"):
        if current_test_uuid is None:
            return bstack1ll111_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡇࡌࡍࠩၘ")
        else:
            return bstack1ll111_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡅࡂࡅࡋࠫၙ")
    elif hook_type.lower() == bstack1ll111_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩၚ"):
        if current_test_uuid is None:
            return bstack1ll111_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡂࡎࡏࠫၛ")
        else:
            return bstack1ll111_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭ၜ")