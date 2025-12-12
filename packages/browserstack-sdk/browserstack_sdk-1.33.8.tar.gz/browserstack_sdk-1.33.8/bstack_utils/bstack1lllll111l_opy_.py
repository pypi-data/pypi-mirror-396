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
class bstack111llllll1_opy_:
    def __init__(self, handler):
        self._1llll1lll111_opy_ = None
        self.handler = handler
        self._1llll1ll1ll1_opy_ = self.bstack1llll1ll1l1l_opy_()
        self.patch()
    def patch(self):
        self._1llll1lll111_opy_ = self._1llll1ll1ll1_opy_.execute
        self._1llll1ll1ll1_opy_.execute = self.bstack1llll1ll1lll_opy_()
    def bstack1llll1ll1lll_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1ll111_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࠥ₆"), driver_command, None, this, args)
            response = self._1llll1lll111_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1ll111_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࠥ₇"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1llll1ll1ll1_opy_.execute = self._1llll1lll111_opy_
    @staticmethod
    def bstack1llll1ll1l1l_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver