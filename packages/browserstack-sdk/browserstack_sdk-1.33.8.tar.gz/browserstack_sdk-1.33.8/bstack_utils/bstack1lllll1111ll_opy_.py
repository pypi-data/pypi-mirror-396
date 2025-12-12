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
import logging
logger = logging.getLogger(__name__)
bstack1lllll11l1ll_opy_ = 1000
bstack1lllll111lll_opy_ = 2
class bstack1lllll11l1l1_opy_:
    def __init__(self, handler, bstack1lllll111l1l_opy_=bstack1lllll11l1ll_opy_, bstack1lllll111ll1_opy_=bstack1lllll111lll_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lllll111l1l_opy_ = bstack1lllll111l1l_opy_
        self.bstack1lllll111ll1_opy_ = bstack1lllll111ll1_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1llllll1111_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1lllll11l11l_opy_()
    def bstack1lllll11l11l_opy_(self):
        self.bstack1llllll1111_opy_ = threading.Event()
        def bstack1lllll11l111_opy_():
            self.bstack1llllll1111_opy_.wait(self.bstack1lllll111ll1_opy_)
            if not self.bstack1llllll1111_opy_.is_set():
                self.bstack1lllll11ll11_opy_()
        self.timer = threading.Thread(target=bstack1lllll11l111_opy_, daemon=True)
        self.timer.start()
    def bstack1lllll11ll1l_opy_(self):
        try:
            if self.bstack1llllll1111_opy_ and not self.bstack1llllll1111_opy_.is_set():
                self.bstack1llllll1111_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠧ࡜ࡵࡷࡳࡵࡥࡴࡪ࡯ࡨࡶࡢࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯࠼ࠣࠫ‶") + (str(e) or bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡨࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡣࡧࠣࡧࡴࡴࡶࡦࡴࡷࡩࡩࠦࡴࡰࠢࡶࡸࡷ࡯࡮ࡨࠤ‷")))
        finally:
            self.timer = None
    def bstack1lllll111l11_opy_(self):
        if self.timer:
            self.bstack1lllll11ll1l_opy_()
        self.bstack1lllll11l11l_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lllll111l1l_opy_:
                threading.Thread(target=self.bstack1lllll11ll11_opy_).start()
    def bstack1lllll11ll11_opy_(self, source = bstack1ll111_opy_ (u"ࠩࠪ‸")):
        with self.lock:
            if not self.queue:
                self.bstack1lllll111l11_opy_()
                return
            data = self.queue[:self.bstack1lllll111l1l_opy_]
            del self.queue[:self.bstack1lllll111l1l_opy_]
        self.handler(data)
        if source != bstack1ll111_opy_ (u"ࠪࡷ࡭ࡻࡴࡥࡱࡺࡲࠬ‹"):
            self.bstack1lllll111l11_opy_()
    def shutdown(self):
        self.bstack1lllll11ll1l_opy_()
        while self.queue:
            self.bstack1lllll11ll11_opy_(source=bstack1ll111_opy_ (u"ࠫࡸ࡮ࡵࡵࡦࡲࡻࡳ࠭›"))