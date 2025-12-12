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
from collections import deque
from bstack_utils.constants import *
class bstack1ll111l111_opy_:
    def __init__(self):
        self._1lllllll11l1_opy_ = deque()
        self._1lllllll1111_opy_ = {}
        self._1llllll1lll1_opy_ = False
        self._lock = threading.RLock()
    def bstack1lllllll111l_opy_(self, test_name, bstack1lllllll1l1l_opy_):
        with self._lock:
            bstack1lllllll11ll_opy_ = self._1lllllll1111_opy_.get(test_name, {})
            return bstack1lllllll11ll_opy_.get(bstack1lllllll1l1l_opy_, 0)
    def bstack1lllllll1lll_opy_(self, test_name, bstack1lllllll1l1l_opy_):
        with self._lock:
            bstack1lllllll1ll1_opy_ = self.bstack1lllllll111l_opy_(test_name, bstack1lllllll1l1l_opy_)
            self.bstack1llllll1ll1l_opy_(test_name, bstack1lllllll1l1l_opy_)
            return bstack1lllllll1ll1_opy_
    def bstack1llllll1ll1l_opy_(self, test_name, bstack1lllllll1l1l_opy_):
        with self._lock:
            if test_name not in self._1lllllll1111_opy_:
                self._1lllllll1111_opy_[test_name] = {}
            bstack1lllllll11ll_opy_ = self._1lllllll1111_opy_[test_name]
            bstack1lllllll1ll1_opy_ = bstack1lllllll11ll_opy_.get(bstack1lllllll1l1l_opy_, 0)
            bstack1lllllll11ll_opy_[bstack1lllllll1l1l_opy_] = bstack1lllllll1ll1_opy_ + 1
    def bstack1l1ll1ll_opy_(self, bstack1lllllll1l11_opy_, bstack1llllll1llll_opy_):
        bstack1llllllll11l_opy_ = self.bstack1lllllll1lll_opy_(bstack1lllllll1l11_opy_, bstack1llllll1llll_opy_)
        event_name = bstack11l1l1l1111_opy_[bstack1llllll1llll_opy_]
        bstack1l1l1111ll1_opy_ = bstack1ll111_opy_ (u"ࠦࢀࢃ࠭ࡼࡿ࠰ࡿࢂࠨῃ").format(bstack1lllllll1l11_opy_, event_name, bstack1llllllll11l_opy_)
        with self._lock:
            self._1lllllll11l1_opy_.append(bstack1l1l1111ll1_opy_)
    def bstack1l1llllll1_opy_(self):
        with self._lock:
            return len(self._1lllllll11l1_opy_) == 0
    def bstack1l1ll1lll1_opy_(self):
        with self._lock:
            if self._1lllllll11l1_opy_:
                bstack1llllllll111_opy_ = self._1lllllll11l1_opy_.popleft()
                return bstack1llllllll111_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._1llllll1lll1_opy_
    def bstack1lll1l111l_opy_(self):
        with self._lock:
            self._1llllll1lll1_opy_ = True
    def bstack1l111l111_opy_(self):
        with self._lock:
            self._1llllll1lll1_opy_ = False