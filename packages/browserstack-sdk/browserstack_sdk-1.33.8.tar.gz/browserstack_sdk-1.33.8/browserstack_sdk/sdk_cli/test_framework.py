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
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1lllll1llll_opy_ import bstack1llllll111l_opy_
from browserstack_sdk.sdk_cli.bstack1llll1llll1_opy_ import bstack1llll1l11ll_opy_, bstack1lllll1l11l_opy_
class bstack1lll1l1llll_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1ll111_opy_ (u"ࠤࡗࡩࡸࡺࡈࡰࡱ࡮ࡗࡹࡧࡴࡦ࠰ࡾࢁࠧᘓ").format(self.name)
class bstack1lll1l1lll1_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1ll111_opy_ (u"ࠥࡘࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡖࡸࡦࡺࡥ࠯ࡽࢀࠦᘔ").format(self.name)
class bstack1ll1l1ll1ll_opy_(bstack1llll1l11ll_opy_):
    bstack1l1llllll11_opy_: List[str]
    bstack11lll1llll1_opy_: Dict[str, str]
    state: bstack1lll1l1lll1_opy_
    bstack1llll1ll1ll_opy_: datetime
    bstack1lllll111l1_opy_: datetime
    def __init__(
        self,
        context: bstack1lllll1l11l_opy_,
        bstack1l1llllll11_opy_: List[str],
        bstack11lll1llll1_opy_: Dict[str, str],
        state=bstack1lll1l1lll1_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1l1llllll11_opy_ = bstack1l1llllll11_opy_
        self.bstack11lll1llll1_opy_ = bstack11lll1llll1_opy_
        self.state = state
        self.bstack1llll1ll1ll_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1lllll111l1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llll11l11l_opy_(self, bstack1llll1lll11_opy_: bstack1lll1l1lll1_opy_):
        bstack1lllll111ll_opy_ = bstack1lll1l1lll1_opy_(bstack1llll1lll11_opy_).name
        if not bstack1lllll111ll_opy_:
            return False
        if bstack1llll1lll11_opy_ == self.state:
            return False
        self.state = bstack1llll1lll11_opy_
        self.bstack1lllll111l1_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1l1111l1111_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1ll1ll1llll_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1l1l1111l_opy_: int = None
    bstack1l1l1ll1111_opy_: str = None
    bstack1111lll_opy_: str = None
    bstack1l1lll1l_opy_: str = None
    bstack1l1l11lllll_opy_: str = None
    bstack1l11111ll1l_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11l111ll_opy_ = bstack1ll111_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠢᘕ")
    bstack11lllll1l11_opy_ = bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡭ࡩࠨᘖ")
    bstack1l1llll11l1_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣࡳࡧ࡭ࡦࠤᘗ")
    bstack11lllllll11_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡢࡴࡦࡺࡨࠣᘘ")
    bstack1l11111ll11_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡴࡢࡩࡶࠦᘙ")
    bstack1l11l1lll11_opy_ = bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡳࡧࡶࡹࡱࡺࠢᘚ")
    bstack1l1l1l1llll_opy_ = bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡷࡺࡲࡴࡠࡣࡷࠦᘛ")
    bstack1l1l111lll1_opy_ = bstack1ll111_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨᘜ")
    bstack1l1ll1l1l11_opy_ = bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡩࡳࡪࡥࡥࡡࡤࡸࠧᘝ")
    bstack11lll1ll111_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣࡱࡵࡣࡢࡶ࡬ࡳࡳࠨᘞ")
    bstack1l1lllll1ll_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࠨᘟ")
    bstack1l1ll1111ll_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠥᘠ")
    bstack1l11111lll1_opy_ = bstack1ll111_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡤࡱࡧࡩࠧᘡ")
    bstack1l1l111111l_opy_ = bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡶࡺࡴ࡟࡯ࡣࡰࡩࠧᘢ")
    bstack1ll11ll1111_opy_ = bstack1ll111_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠧᘣ")
    bstack1l11ll1l11l_opy_ = bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪࡦ࡯࡬ࡶࡴࡨࠦᘤ")
    bstack1l1111llll1_opy_ = bstack1ll111_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠥᘥ")
    bstack11llll111ll_opy_ = bstack1ll111_opy_ (u"ࠢࡵࡧࡶࡸࡤࡲ࡯ࡨࡵࠥᘦ")
    bstack1l111111111_opy_ = bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥ࡭ࡦࡶࡤࠦᘧ")
    bstack11lll1l1l11_opy_ = bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡴࡥࡲࡴࡪࡹࠧᘨ")
    bstack1l111lllll1_opy_ = bstack1ll111_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࡤࡹࡥࡴࡵ࡬ࡳࡳࡥ࡮ࡢ࡯ࡨࠦᘩ")
    bstack1l111l11ll1_opy_ = bstack1ll111_opy_ (u"ࠦࡪࡼࡥ࡯ࡶࡢࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠢᘪ")
    bstack11llllllll1_opy_ = bstack1ll111_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡪࡴࡤࡦࡦࡢࡥࡹࠨᘫ")
    bstack1l1111l1l1l_opy_ = bstack1ll111_opy_ (u"ࠨࡨࡰࡱ࡮ࡣ࡮ࡪࠢᘬ")
    bstack11lll1lllll_opy_ = bstack1ll111_opy_ (u"ࠢࡩࡱࡲ࡯ࡤࡸࡥࡴࡷ࡯ࡸࠧᘭ")
    bstack11lllll1lll_opy_ = bstack1ll111_opy_ (u"ࠣࡪࡲࡳࡰࡥ࡬ࡰࡩࡶࠦᘮ")
    bstack11llll1llll_opy_ = bstack1ll111_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟࡯ࡣࡰࡩࠧᘯ")
    bstack11lll1ll1l1_opy_ = bstack1ll111_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᘰ")
    bstack1l111l11lll_opy_ = bstack1ll111_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨᘱ")
    bstack1l1111111ll_opy_ = bstack1ll111_opy_ (u"ࠧࡶࡥ࡯ࡦ࡬ࡲ࡬ࠨᘲ")
    bstack11llllll1l1_opy_ = bstack1ll111_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢᘳ")
    bstack1l1l1l11l11_opy_ = bstack1ll111_opy_ (u"ࠢࡕࡇࡖࡘࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࠤᘴ")
    bstack1l1l1ll11ll_opy_ = bstack1ll111_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡌࡐࡉࠥᘵ")
    bstack1l1l1lll1l1_opy_ = bstack1ll111_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦᘶ")
    bstack1lll1llllll_opy_: Dict[str, bstack1ll1l1ll1ll_opy_] = dict()
    bstack11lll11ll11_opy_: Dict[str, List[Callable]] = dict()
    bstack1l1llllll11_opy_: List[str]
    bstack11lll1llll1_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1l1llllll11_opy_: List[str],
        bstack11lll1llll1_opy_: Dict[str, str],
        bstack1lllll1llll_opy_: bstack1llllll111l_opy_
    ):
        self.bstack1l1llllll11_opy_ = bstack1l1llllll11_opy_
        self.bstack11lll1llll1_opy_ = bstack11lll1llll1_opy_
        self.bstack1lllll1llll_opy_ = bstack1lllll1llll_opy_
    def track_event(
        self,
        context: bstack1l1111l1111_opy_,
        test_framework_state: bstack1lll1l1lll1_opy_,
        test_hook_state: bstack1lll1l1llll_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼࡿࠣࡥࡷ࡭ࡳ࠾ࡽࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࢃࠢᘷ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack11llll1l1ll_opy_(
        self,
        instance: bstack1ll1l1ll1ll_opy_,
        bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l111l1lll1_opy_ = TestFramework.bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_)
        if not bstack1l111l1lll1_opy_ in TestFramework.bstack11lll11ll11_opy_:
            return
        self.logger.debug(bstack1ll111_opy_ (u"ࠦ࡮ࡴࡶࡰ࡭࡬ࡲ࡬ࠦࡻࡾࠢࡦࡥࡱࡲࡢࡢࡥ࡮ࡷࠧᘸ").format(len(TestFramework.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_])))
        for callback in TestFramework.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_]:
            try:
                callback(self, instance, bstack1llll11ll1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack1ll111_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠤ࡮ࡴࡶࡰ࡭࡬ࡲ࡬ࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢࡾࢁࠧᘹ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1l1ll1ll1_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1l1ll1l11_opy_(self, instance, bstack1llll11ll1l_opy_):
        return
    @abc.abstractmethod
    def bstack1l1l1llllll_opy_(self, instance, bstack1llll11ll1l_opy_):
        return
    @staticmethod
    def bstack1llll111ll1_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1llll1l11ll_opy_.create_context(target)
        instance = TestFramework.bstack1lll1llllll_opy_.get(ctx.id, None)
        if instance and instance.bstack1llll111l11_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1l11l1lll_opy_(reverse=True) -> List[bstack1ll1l1ll1ll_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1llll1ll1ll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll11111l_opy_(ctx: bstack1lllll1l11l_opy_, reverse=True) -> List[bstack1ll1l1ll1ll_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1llll1ll1ll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll11lll1_opy_(instance: bstack1ll1l1ll1ll_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll11l1ll_opy_(instance: bstack1ll1l1ll1ll_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llll11l11l_opy_(instance: bstack1ll1l1ll1ll_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1ll111_opy_ (u"ࠨࡳࡦࡶࡢࡷࡹࡧࡴࡦ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡ࡭ࡨࡽࡂࢁࡽࠡࡸࡤࡰࡺ࡫࠽ࡼࡿࠥᘺ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l11111l11l_opy_(instance: bstack1ll1l1ll1ll_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡣࡸࡺࡡࡵࡧࡢࡩࡳࡺࡲࡪࡧࡶ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼࡿࠣࡩࡳࡺࡲࡪࡧࡶࡁࢀࢃࠢᘻ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11lll111ll1_opy_(instance: bstack1lll1l1lll1_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1ll111_opy_ (u"ࠣࡷࡳࡨࡦࡺࡥࡠࡵࡷࡥࡹ࡫࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿࢂࠦ࡫ࡦࡻࡀࡿࢂࠦࡶࡢ࡮ࡸࡩࡂࢁࡽࠣᘼ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1llll111ll1_opy_(target, strict)
        return TestFramework.bstack1llll11l1ll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1llll111ll1_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11llllll1ll_opy_(instance: bstack1ll1l1ll1ll_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l1111ll1ll_opy_(instance: bstack1ll1l1ll1ll_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_]):
        return bstack1ll111_opy_ (u"ࠤ࠽ࠦᘽ").join((bstack1lll1l1lll1_opy_(bstack1llll11ll1l_opy_[0]).name, bstack1lll1l1llll_opy_(bstack1llll11ll1l_opy_[1]).name))
    @staticmethod
    def bstack1l1llll111l_opy_(bstack1llll11ll1l_opy_: Tuple[bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_], callback: Callable):
        bstack1l111l1lll1_opy_ = TestFramework.bstack1l111ll11l1_opy_(bstack1llll11ll1l_opy_)
        TestFramework.logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡪࡺ࡟ࡩࡱࡲ࡯ࡤࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࡪࡲࡳࡰࡥࡲࡦࡩ࡬ࡷࡹࡸࡹࡠ࡭ࡨࡽࡂࢁࡽࠣᘾ").format(bstack1l111l1lll1_opy_))
        if not bstack1l111l1lll1_opy_ in TestFramework.bstack11lll11ll11_opy_:
            TestFramework.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_] = []
        TestFramework.bstack11lll11ll11_opy_[bstack1l111l1lll1_opy_].append(callback)
    @staticmethod
    def bstack1l1l1l1l11l_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡶ࡬ࡲࡸࠨᘿ"):
            return klass.__qualname__
        return module + bstack1ll111_opy_ (u"ࠧ࠴ࠢᙀ") + klass.__qualname__
    @staticmethod
    def bstack1l1l11l11l1_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}