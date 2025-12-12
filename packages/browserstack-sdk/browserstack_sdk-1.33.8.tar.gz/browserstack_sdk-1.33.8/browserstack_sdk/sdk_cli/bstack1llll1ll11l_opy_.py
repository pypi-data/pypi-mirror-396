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
from typing import Dict, Tuple, Callable, Type, List, Any
import abc
from datetime import datetime, timezone, timedelta
from browserstack_sdk.sdk_cli.bstack1llll1llll1_opy_ import bstack1llll1l11ll_opy_, bstack1lllll1l11l_opy_
import os
import threading
class bstack1lllll11l11_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1ll111_opy_ (u"ࠣࡊࡲࡳࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢრ").format(self.name)
class bstack1llll1l1111_opy_(Enum):
    NONE = 0
    bstack1llll11ll11_opy_ = 1
    bstack1lllll1l1ll_opy_ = 3
    bstack1lllll1111l_opy_ = 4
    bstack1llll1ll1l1_opy_ = 5
    QUIT = 6
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1ll111_opy_ (u"ࠤࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡸࡪ࠴ࡻࡾࠤს").format(self.name)
class bstack1lllll11111_opy_(bstack1llll1l11ll_opy_):
    framework_name: str
    framework_version: str
    state: bstack1llll1l1111_opy_
    previous_state: bstack1llll1l1111_opy_
    bstack1llll1ll1ll_opy_: datetime
    bstack1lllll111l1_opy_: datetime
    def __init__(
        self,
        context: bstack1lllll1l11l_opy_,
        framework_name: str,
        framework_version: str,
        state=bstack1llll1l1111_opy_.NONE,
    ):
        super().__init__(context)
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.state = state
        self.previous_state = bstack1llll1l1111_opy_.NONE
        self.bstack1llll1ll1ll_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1lllll111l1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llll11l11l_opy_(self, bstack1llll1lll11_opy_: bstack1llll1l1111_opy_):
        bstack1lllll111ll_opy_ = bstack1llll1l1111_opy_(bstack1llll1lll11_opy_).name
        if not bstack1lllll111ll_opy_:
            return False
        if bstack1llll1lll11_opy_ == self.state:
            return False
        if self.state == bstack1llll1l1111_opy_.bstack1lllll1l1ll_opy_: # bstack1lll1lllll1_opy_ bstack1lllll11lll_opy_ for bstack1llll11l111_opy_ in bstack1llll11l1l1_opy_, it bstack1llll1ll111_opy_ bstack1llll1111ll_opy_ bstack1llll1l11l1_opy_ times bstack1llll1l111l_opy_ a new state
            return True
        if (
            bstack1llll1lll11_opy_ == bstack1llll1l1111_opy_.NONE
            or (self.state != bstack1llll1l1111_opy_.NONE and bstack1llll1lll11_opy_ == bstack1llll1l1111_opy_.bstack1llll11ll11_opy_)
            or (self.state < bstack1llll1l1111_opy_.bstack1llll11ll11_opy_ and bstack1llll1lll11_opy_ == bstack1llll1l1111_opy_.bstack1lllll1111l_opy_)
            or (self.state < bstack1llll1l1111_opy_.bstack1llll11ll11_opy_ and bstack1llll1lll11_opy_ == bstack1llll1l1111_opy_.QUIT)
        ):
            raise ValueError(bstack1ll111_opy_ (u"ࠥ࡭ࡳࡼࡡ࡭࡫ࡧࠤࡸࡺࡡࡵࡧࠣࡸࡷࡧ࡮ࡴ࡫ࡷ࡭ࡴࡴ࠺ࠡࠤტ") + str(self.state) + bstack1ll111_opy_ (u"ࠦࠥࡃ࠾ࠡࠤუ") + str(bstack1llll1lll11_opy_))
        self.previous_state = self.state
        self.state = bstack1llll1lll11_opy_
        self.bstack1lllll111l1_opy_ = datetime.now(tz=timezone.utc)
        return True
class bstack1llll1lll1l_opy_(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1lll1llllll_opy_: Dict[str, bstack1lllll11111_opy_] = dict()
    framework_name: str
    framework_version: str
    classes: List[Type]
    def __init__(
        self,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
    ):
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.classes = classes
    @abc.abstractmethod
    def bstack1llll111l1l_opy_(self, instance: bstack1lllll11111_opy_, method_name: str, bstack1lllll1l1l1_opy_: timedelta, *args, **kwargs):
        return
    @abc.abstractmethod
    def bstack1llll111lll_opy_(
        self, method_name, previous_state: bstack1llll1l1111_opy_, *args, **kwargs
    ) -> bstack1llll1l1111_opy_:
        return
    @abc.abstractmethod
    def bstack1llll11llll_opy_(
        self,
        target: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable:
        return
    def bstack1llll1l1l11_opy_(self, bstack1llll111111_opy_: List[str]):
        for clazz in self.classes:
            for method_name in bstack1llll111111_opy_:
                bstack1lll1llll1l_opy_ = getattr(clazz, method_name, None)
                if not callable(bstack1lll1llll1l_opy_):
                    self.logger.warning(bstack1ll111_opy_ (u"ࠧࡻ࡮ࡱࡣࡷࡧ࡭࡫ࡤࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࠥფ") + str(method_name) + bstack1ll111_opy_ (u"ࠨࠢქ"))
                    continue
                bstack1llll1l1lll_opy_ = self.bstack1llll111lll_opy_(
                    method_name, previous_state=bstack1llll1l1111_opy_.NONE
                )
                bstack1lllll11ll1_opy_ = self.bstack1llll1lllll_opy_(
                    method_name,
                    (bstack1llll1l1lll_opy_ if bstack1llll1l1lll_opy_ else bstack1llll1l1111_opy_.NONE),
                    bstack1lll1llll1l_opy_,
                )
                if not callable(bstack1lllll11ll1_opy_):
                    self.logger.warning(bstack1ll111_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠠ࡯ࡱࡷࠤࡵࡧࡴࡤࡪࡨࡨ࠿ࠦࡻ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࢂࠦࠨࡼࡵࡨࡰ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽ࠻ࠢࠥღ") + str(self.framework_version) + bstack1ll111_opy_ (u"ࠣࠫࠥყ"))
                    continue
                setattr(clazz, method_name, bstack1lllll11ll1_opy_)
    def bstack1llll1lllll_opy_(
        self,
        method_name: str,
        bstack1llll1l1lll_opy_: bstack1llll1l1111_opy_,
        bstack1lll1llll1l_opy_: Callable,
    ):
        def wrapped(target, *args, **kwargs):
            bstack111ll1ll1_opy_ = datetime.now()
            (bstack1llll1l1lll_opy_,) = wrapped.__vars__
            bstack1llll1l1lll_opy_ = (
                bstack1llll1l1lll_opy_
                if bstack1llll1l1lll_opy_ and bstack1llll1l1lll_opy_ != bstack1llll1l1111_opy_.NONE
                else self.bstack1llll111lll_opy_(method_name, previous_state=bstack1llll1l1lll_opy_, *args, **kwargs)
            )
            if bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.bstack1llll11ll11_opy_:
                ctx = bstack1llll1l11ll_opy_.create_context(self.bstack1lllll1l111_opy_(target))
                if not self.bstack1llll1l1ll1_opy_() or ctx.id not in bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_:
                    bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_[ctx.id] = bstack1lllll11111_opy_(
                        ctx, self.framework_name, self.framework_version, bstack1llll1l1lll_opy_
                    )
                self.logger.debug(bstack1ll111_opy_ (u"ࠤࡺࡶࡦࡶࡰࡦࡦࠣࡱࡪࡺࡨࡰࡦࠣࡧࡷ࡫ࡡࡵࡧࡧ࠾ࠥࢁࡴࡢࡴࡪࡩࡹ࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡤࡶࡻࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥშ") + str(bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_.keys()) + bstack1ll111_opy_ (u"ࠥࠦჩ"))
            else:
                self.logger.debug(bstack1ll111_opy_ (u"ࠦࡼࡸࡡࡱࡲࡨࡨࠥࡳࡥࡵࡪࡲࡨࠥ࡯࡮ࡷࡱ࡮ࡩࡩࡀࠠࡼࡶࡤࡶ࡬࡫ࡴ࠯ࡡࡢࡧࡱࡧࡳࡴࡡࡢࢁࠥࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࡀࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨც") + str(bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_.keys()) + bstack1ll111_opy_ (u"ࠧࠨძ"))
            instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(self.bstack1lllll1l111_opy_(target))
            if bstack1llll1l1lll_opy_ == bstack1llll1l1111_opy_.NONE or not instance:
                ctx = bstack1llll1l11ll_opy_.create_context(self.bstack1lllll1l111_opy_(target))
                self.logger.warning(bstack1ll111_opy_ (u"ࠨࡷࡳࡣࡳࡴࡪࡪࠠ࡮ࡧࡷ࡬ࡴࡪࠠࡶࡰࡷࡶࡦࡩ࡫ࡦࡦ࠽ࠤࢀࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࢀࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡧࡹࡾ࠽ࡼࡥࡷࡼࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥწ") + str(bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_.keys()) + bstack1ll111_opy_ (u"ࠢࠣჭ"))
                return bstack1lll1llll1l_opy_(target, *args, **kwargs)
            bstack1lllll11l1l_opy_ = self.bstack1llll11llll_opy_(
                target,
                (instance, method_name),
                (bstack1llll1l1lll_opy_, bstack1lllll11l11_opy_.PRE),
                None,
                *args,
                **kwargs,
            )
            if instance.bstack1llll11l11l_opy_(bstack1llll1l1lll_opy_):
                self.logger.debug(bstack1ll111_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡥࡥࠢࡶࡸࡦࡺࡥ࠮ࡶࡵࡥࡳࡹࡩࡵ࡫ࡲࡲ࠿ࠦࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡳࡶࡪࡼࡩࡰࡷࡶࡣࡸࡺࡡࡵࡧࢀࠤࡂࡄࠠࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡷࡹࡧࡴࡦࡿࠣࠬࢀࡺࡹࡱࡧࠫࡸࡦࡸࡧࡦࡶࠬࢁ࠳ࢁ࡭ࡦࡶ࡫ࡳࡩࡥ࡮ࡢ࡯ࡨࢁࠥࢁࡡࡳࡩࡶࢁ࠮࡛ࠦࠣხ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠤࡠࠦჯ"))
            result = (
                bstack1lllll11l1l_opy_(target, bstack1lll1llll1l_opy_, *args, **kwargs)
                if callable(bstack1lllll11l1l_opy_)
                else bstack1lll1llll1l_opy_(target, *args, **kwargs)
            )
            bstack1llll1111l1_opy_ = self.bstack1llll11llll_opy_(
                target,
                (instance, method_name),
                (bstack1llll1l1lll_opy_, bstack1lllll11l11_opy_.POST),
                result,
                *args,
                **kwargs,
            )
            self.bstack1llll111l1l_opy_(instance, method_name, datetime.now() - bstack111ll1ll1_opy_, *args, **kwargs)
            return bstack1llll1111l1_opy_ if bstack1llll1111l1_opy_ else result
        wrapped.__name__ = method_name
        wrapped.__vars__ = (bstack1llll1l1lll_opy_,)
        return wrapped
    @staticmethod
    def bstack1llll111ll1_opy_(target: object, strict=True):
        ctx = bstack1llll1l11ll_opy_.create_context(target)
        instance = bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_.get(ctx.id, None)
        if instance and instance.bstack1llll111l11_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1llll11111l_opy_(
        ctx: bstack1lllll1l11l_opy_, state: bstack1llll1l1111_opy_, reverse=True
    ) -> List[bstack1lllll11111_opy_]:
        return sorted(
            filter(
                lambda t: t.state == state
                and t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                bstack1llll1lll1l_opy_.bstack1lll1llllll_opy_.values(),
            ),
            key=lambda t: t.bstack1llll1ll1ll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll11lll1_opy_(instance: bstack1lllll11111_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llll11l1ll_opy_(instance: bstack1lllll11111_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llll11l11l_opy_(instance: bstack1lllll11111_opy_, key: str, value: Any) -> bool:
        instance.data[key] = value
        bstack1llll1lll1l_opy_.logger.debug(bstack1ll111_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࡾ࡭ࡳࡹࡴࡢࡰࡦࡩ࠳ࡸࡥࡧࠪࠬࢁࠥࡱࡥࡺ࠿ࡾ࡯ࡪࡿࡽࠡࡸࡤࡰࡺ࡫࠽ࠣჰ") + str(value) + bstack1ll111_opy_ (u"ࠦࠧჱ"))
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(target, strict)
        return bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = bstack1llll1lll1l_opy_.bstack1llll111ll1_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    def bstack1llll1l1ll1_opy_(self):
        return self.framework_name == bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩჲ")
    def bstack1lllll1l111_opy_(self, target):
        return target if not self.bstack1llll1l1ll1_opy_() else self.bstack1llll1l1l1l_opy_()
    @staticmethod
    def bstack1llll1l1l1l_opy_():
        return str(os.getpid()) + str(threading.get_ident())