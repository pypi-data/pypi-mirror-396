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
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1llll1lll1l_opy_,
    bstack1lllll11111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllllll_opy_ import bstack1ll11lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll1llll1_opy_ import bstack1lllll1l11l_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
import weakref
class bstack1l1ll1lll1l_opy_(bstack1ll1ll1l1l1_opy_):
    bstack1l1ll1lll11_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1lllll11111_opy_]]
    pages: Dict[str, Tuple[Callable, bstack1lllll11111_opy_]]
    def __init__(self, bstack1l1ll1lll11_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1l1ll1ll1l1_opy_ = dict()
        self.bstack1l1ll1lll11_opy_ = bstack1l1ll1lll11_opy_
        self.frameworks = frameworks
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1llll11ll11_opy_, bstack1lllll11l11_opy_.POST), self.__1l1ll1lllll_opy_)
        if any(bstack1lll11l11ll_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_(
                (bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.__1l1ll1ll11l_opy_
            )
            bstack1lll11l11ll_opy_.bstack1l1llll111l_opy_(
                (bstack1llll1l1111_opy_.QUIT, bstack1lllll11l11_opy_.POST), self.__1l1ll1l1ll1_opy_
            )
    def __1l1ll1lllll_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        bstack1l1ll1l1l1l_opy_: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack1ll111_opy_ (u"ࠥࡲࡪࡽ࡟ࡱࡣࡪࡩࠧኩ"):
                return
            contexts = bstack1l1ll1l1l1l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1ll111_opy_ (u"ࠦࡦࡨ࡯ࡶࡶ࠽ࡦࡱࡧ࡮࡬ࠤኪ") in page.url:
                                self.logger.debug(bstack1ll111_opy_ (u"࡙ࠧࡴࡰࡴ࡬ࡲ࡬ࠦࡴࡩࡧࠣࡲࡪࡽࠠࡱࡣࡪࡩࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠢካ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, self.bstack1l1ll1lll11_opy_, True)
                                self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡟ࡠࡱࡱࡣࡵࡧࡧࡦࡡ࡬ࡲ࡮ࡺ࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦኬ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠢࠣክ"))
        except Exception as e:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡰࡨࡻࠥࡶࡡࡨࡧࠣ࠾ࠧኮ"),e)
    def __1l1ll1ll11l_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1llll1lll1l_opy_.bstack1llll11l1ll_opy_(instance, self.bstack1l1ll1lll11_opy_, False):
            return
        if not f.bstack1l1lll1ll11_opy_(f.hub_url(driver)):
            self.bstack1l1ll1ll1l1_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, self.bstack1l1ll1lll11_opy_, True)
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡢࡣࡴࡴ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡡ࡬ࡲ࡮ࡺ࠺ࠡࡰࡲࡲࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡩࡸࡩࡷࡧࡵࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢኯ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠥࠦኰ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, self.bstack1l1ll1lll11_opy_, True)
        self.logger.debug(bstack1ll111_opy_ (u"ࠦࡤࡥ࡯࡯ࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࡣ࡮ࡴࡩࡵ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࠨ኱") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠧࠨኲ"))
    def __1l1ll1l1ll1_opy_(
        self,
        f: bstack1lll11l11ll_opy_,
        driver: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1l1ll1ll1ll_opy_(instance)
        self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡟ࡠࡱࡱࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡱࡶ࡫ࡷ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣኳ") + str(instance.ref()) + bstack1ll111_opy_ (u"ࠢࠣኴ"))
    def bstack1l1ll1ll111_opy_(self, context: bstack1lllll1l11l_opy_, reverse=True) -> List[Tuple[Callable, bstack1lllll11111_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1l1lll11111_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1lll11l11ll_opy_.bstack1l1lll1111l_opy_(data[1])
                    and data[1].bstack1l1lll11111_opy_(context)
                    and getattr(data[0](), bstack1ll111_opy_ (u"ࠣࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧኵ"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1llll1ll1ll_opy_, reverse=reverse)
    def bstack1l1ll1l1lll_opy_(self, context: bstack1lllll1l11l_opy_, reverse=True) -> List[Tuple[Callable, bstack1lllll11111_opy_]]:
        matches = []
        for data in self.bstack1l1ll1ll1l1_opy_.values():
            if (
                data[1].bstack1l1lll11111_opy_(context)
                and getattr(data[0](), bstack1ll111_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࠨ኶"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1llll1ll1ll_opy_, reverse=reverse)
    def bstack1l1ll1llll1_opy_(self, instance: bstack1lllll11111_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1l1ll1ll1ll_opy_(self, instance: bstack1lllll11111_opy_) -> bool:
        if self.bstack1l1ll1llll1_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1llll1lll1l_opy_.bstack1llll11l11l_opy_(instance, self.bstack1l1ll1lll11_opy_, False)
            return True
        return False