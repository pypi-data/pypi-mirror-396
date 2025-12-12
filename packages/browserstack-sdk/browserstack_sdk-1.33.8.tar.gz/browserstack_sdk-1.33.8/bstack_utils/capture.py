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
import builtins
import logging
class bstack111l1lllll_opy_:
    def __init__(self, handler):
        self._11l1ll1l11l_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1ll1l1l1_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack1ll111_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨ២"), bstack1ll111_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪ៣"), bstack1ll111_opy_ (u"ࠬࡽࡡࡳࡰ࡬ࡲ࡬࠭៤"), bstack1ll111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ៥")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1ll1l1ll_opy_
        self._11l1ll1ll11_opy_()
    def _11l1ll1l1ll_opy_(self, *args, **kwargs):
        self._11l1ll1l11l_opy_(*args, **kwargs)
        message = bstack1ll111_opy_ (u"ࠧࠡࠩ៦").join(map(str, args)) + bstack1ll111_opy_ (u"ࠨ࡞ࡱࠫ៧")
        self._log_message(bstack1ll111_opy_ (u"ࠩࡌࡒࡋࡕࠧ៨"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack1ll111_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ៩"): level, bstack1ll111_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ៪"): msg})
    def _11l1ll1ll11_opy_(self):
        for level, bstack11l1ll1l111_opy_ in self._11l1ll1l1l1_opy_.items():
            setattr(logging, level, self._11l1ll1ll1l_opy_(level, bstack11l1ll1l111_opy_))
    def _11l1ll1ll1l_opy_(self, level, bstack11l1ll1l111_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1ll1l111_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1ll1l11l_opy_
        for level, bstack11l1ll1l111_opy_ in self._11l1ll1l1l1_opy_.items():
            setattr(logging, level, bstack11l1ll1l111_opy_)