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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111ll11l111_opy_
from browserstack_sdk.bstack1llll11lll_opy_ import bstack1lll1111ll_opy_
def _111l1l1llll_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l1l11l1l_opy_:
    def __init__(self, handler):
        self._111l1l1l1l1_opy_ = {}
        self._111l1l11lll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1lll1111ll_opy_.version()
        if bstack111ll11l111_opy_(pytest_version, bstack1ll111_opy_ (u"ࠣ࠺࠱࠵࠳࠷ࠢᷫ")) >= 0:
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᷬ")] = Module._register_setup_function_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᷭ")] = Module._register_setup_module_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᷮ")] = Class._register_setup_class_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᷯ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᷰ"))
            Module._register_setup_module_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᷱ"))
            Class._register_setup_class_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᷲ"))
            Class._register_setup_method_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᷳ"))
        else:
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᷴ")] = Module._inject_setup_function_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ᷵")] = Module._inject_setup_module_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ᷶")] = Class._inject_setup_class_fixture
            self._111l1l1l1l1_opy_[bstack1ll111_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫᷷ࠧ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧ᷸ࠪ"))
            Module._inject_setup_module_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦ᷹ࠩ"))
            Class._inject_setup_class_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦ᷺ࠩ"))
            Class._inject_setup_method_fixture = self.bstack111l1l1l111_opy_(bstack1ll111_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᷻"))
    def bstack111l1l1l1ll_opy_(self, bstack111l1ll11l1_opy_, hook_type):
        bstack111l1l11ll1_opy_ = id(bstack111l1ll11l1_opy_.__class__)
        if (bstack111l1l11ll1_opy_, hook_type) in self._111l1l11lll_opy_:
            return
        meth = getattr(bstack111l1ll11l1_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111l1l11lll_opy_[(bstack111l1l11ll1_opy_, hook_type)] = meth
            setattr(bstack111l1ll11l1_opy_, hook_type, self.bstack111l1ll1111_opy_(hook_type, bstack111l1l11ll1_opy_))
    def bstack111l1l1ll1l_opy_(self, instance, bstack111l1l111ll_opy_):
        if bstack111l1l111ll_opy_ == bstack1ll111_opy_ (u"ࠦ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠢ᷼"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨ᷽"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠥ᷾"))
        if bstack111l1l111ll_opy_ == bstack1ll111_opy_ (u"ࠢ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥ᷿ࠣ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠢḀ"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲࡵࡤࡶ࡮ࡨࠦḁ"))
        if bstack111l1l111ll_opy_ == bstack1ll111_opy_ (u"ࠥࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠥḂ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠤḃ"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸࠨḄ"))
        if bstack111l1l111ll_opy_ == bstack1ll111_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠢḅ"):
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩࠨḆ"))
            self.bstack111l1l1l1ll_opy_(instance.obj, bstack1ll111_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠥḇ"))
    @staticmethod
    def bstack111l1l1l11l_opy_(hook_type, func, args):
        if hook_type in [bstack1ll111_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨḈ"), bstack1ll111_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬḉ")]:
            _111l1l1llll_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l1ll1111_opy_(self, hook_type, bstack111l1l11ll1_opy_):
        def bstack111l1l1ll11_opy_(arg=None):
            self.handler(hook_type, bstack1ll111_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫḊ"))
            result = None
            try:
                bstack1lll1llll1l_opy_ = self._111l1l11lll_opy_[(bstack111l1l11ll1_opy_, hook_type)]
                self.bstack111l1l1l11l_opy_(hook_type, bstack1lll1llll1l_opy_, (arg,))
                result = Result(result=bstack1ll111_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬḋ"))
            except Exception as e:
                result = Result(result=bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭Ḍ"), exception=e)
                self.handler(hook_type, bstack1ll111_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ḍ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1ll111_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧḎ"), result)
        def bstack111l1l11l11_opy_(this, arg=None):
            self.handler(hook_type, bstack1ll111_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩḏ"))
            result = None
            exception = None
            try:
                self.bstack111l1l1l11l_opy_(hook_type, self._111l1l11lll_opy_[hook_type], (this, arg))
                result = Result(result=bstack1ll111_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪḐ"))
            except Exception as e:
                result = Result(result=bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫḑ"), exception=e)
                self.handler(hook_type, bstack1ll111_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫḒ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1ll111_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬḓ"), result)
        if hook_type in [bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭Ḕ"), bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪḕ")]:
            return bstack111l1l11l11_opy_
        return bstack111l1l1ll11_opy_
    def bstack111l1l1l111_opy_(self, bstack111l1l111ll_opy_):
        def bstack111l1ll111l_opy_(this, *args, **kwargs):
            self.bstack111l1l1ll1l_opy_(this, bstack111l1l111ll_opy_)
            self._111l1l1l1l1_opy_[bstack111l1l111ll_opy_](this, *args, **kwargs)
        return bstack111l1ll111l_opy_