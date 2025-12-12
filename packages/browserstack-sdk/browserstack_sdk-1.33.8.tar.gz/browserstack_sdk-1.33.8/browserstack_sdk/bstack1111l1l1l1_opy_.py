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
class RobotHandler():
    def __init__(self, args, logger, bstack11111111l1_opy_, bstack1111111lll_opy_):
        self.args = args
        self.logger = logger
        self.bstack11111111l1_opy_ = bstack11111111l1_opy_
        self.bstack1111111lll_opy_ = bstack1111111lll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111l111l11_opy_(bstack1llllll1l1l_opy_):
        bstack1llllll11l1_opy_ = []
        if bstack1llllll1l1l_opy_:
            tokens = str(os.path.basename(bstack1llllll1l1l_opy_)).split(bstack1ll111_opy_ (u"ࠤࡢࠦლ"))
            camelcase_name = bstack1ll111_opy_ (u"ࠥࠤࠧმ").join(t.title() for t in tokens)
            suite_name, bstack1llllll11ll_opy_ = os.path.splitext(camelcase_name)
            bstack1llllll11l1_opy_.append(suite_name)
        return bstack1llllll11l1_opy_
    @staticmethod
    def bstack1llllll1l11_opy_(typename):
        if bstack1ll111_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢნ") in typename:
            return bstack1ll111_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨო")
        return bstack1ll111_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢპ")