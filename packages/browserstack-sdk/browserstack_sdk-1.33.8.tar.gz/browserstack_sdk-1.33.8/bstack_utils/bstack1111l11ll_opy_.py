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
from bstack_utils.constants import bstack11l1lll1lll_opy_
def bstack1lll1ll1l1_opy_(bstack11l1llll111_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack1l111l1l1l_opy_
    host = bstack1l111l1l1l_opy_(cli.config, [bstack1ll111_opy_ (u"ࠣࡣࡳ࡭ࡸࠨ់"), bstack1ll111_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨࠦ៌"), bstack1ll111_opy_ (u"ࠥࡥࡵ࡯ࠢ៍")], bstack11l1lll1lll_opy_)
    return bstack1ll111_opy_ (u"ࠫࢀࢃ࠯ࡼࡿࠪ៎").format(host, bstack11l1llll111_opy_)