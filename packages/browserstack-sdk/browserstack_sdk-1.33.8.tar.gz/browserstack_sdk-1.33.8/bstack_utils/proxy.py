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
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111l111l1l1_opy_
bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
def bstack1llllll1111l_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1lllll1lllll_opy_(bstack1lllll1lll11_opy_, bstack1lllll1lll1l_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1lllll1lll11_opy_):
        with open(bstack1lllll1lll11_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1llllll1111l_opy_(bstack1lllll1lll11_opy_):
        pac = get_pac(url=bstack1lllll1lll11_opy_)
    else:
        raise Exception(bstack1ll111_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩ῝").format(bstack1lllll1lll11_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack1ll111_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦ῞"), 80))
        bstack1lllll1llll1_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1lllll1llll1_opy_ = bstack1ll111_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬ῟")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1lllll1lll1l_opy_, bstack1lllll1llll1_opy_)
    return proxy_url
def bstack1l1l11lll_opy_(config):
    return bstack1ll111_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨῠ") in config or bstack1ll111_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪῡ") in config
def bstack1ll1ll111l_opy_(config):
    if not bstack1l1l11lll_opy_(config):
        return
    if config.get(bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪῢ")):
        return config.get(bstack1ll111_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫΰ"))
    if config.get(bstack1ll111_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ῤ")):
        return config.get(bstack1ll111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧῥ"))
def bstack1l1l1ll11l_opy_(config, bstack1lllll1lll1l_opy_):
    proxy = bstack1ll1ll111l_opy_(config)
    proxies = {}
    if config.get(bstack1ll111_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧῦ")) or config.get(bstack1ll111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩῧ")):
        if proxy.endswith(bstack1ll111_opy_ (u"࠭࠮ࡱࡣࡦࠫῨ")):
            proxies = bstack1l11ll1ll1_opy_(proxy, bstack1lllll1lll1l_opy_)
        else:
            proxies = {
                bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭Ῡ"): proxy
            }
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡓࡦࡶࡷ࡭ࡳ࡭ࡳࠨῪ"), proxies)
    return proxies
def bstack1l11ll1ll1_opy_(bstack1lllll1lll11_opy_, bstack1lllll1lll1l_opy_):
    proxies = {}
    global bstack1llllll11111_opy_
    if bstack1ll111_opy_ (u"ࠩࡓࡅࡈࡥࡐࡓࡑ࡛࡝ࠬΎ") in globals():
        return bstack1llllll11111_opy_
    try:
        proxy = bstack1lllll1lllll_opy_(bstack1lllll1lll11_opy_, bstack1lllll1lll1l_opy_)
        if bstack1ll111_opy_ (u"ࠥࡈࡎࡘࡅࡄࡖࠥῬ") in proxy:
            proxies = {}
        elif bstack1ll111_opy_ (u"ࠦࡍ࡚ࡔࡑࠤ῭") in proxy or bstack1ll111_opy_ (u"ࠧࡎࡔࡕࡒࡖࠦ΅") in proxy or bstack1ll111_opy_ (u"ࠨࡓࡐࡅࡎࡗࠧ`") in proxy:
            bstack1llllll111l1_opy_ = proxy.split(bstack1ll111_opy_ (u"ࠢࠡࠤ῰"))
            if bstack1ll111_opy_ (u"ࠣ࠼࠲࠳ࠧ῱") in bstack1ll111_opy_ (u"ࠤࠥῲ").join(bstack1llllll111l1_opy_[1:]):
                proxies = {
                    bstack1ll111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩῳ"): bstack1ll111_opy_ (u"ࠦࠧῴ").join(bstack1llllll111l1_opy_[1:])
                }
            else:
                proxies = {
                    bstack1ll111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫ῵"): str(bstack1llllll111l1_opy_[0]).lower() + bstack1ll111_opy_ (u"ࠨ࠺࠰࠱ࠥῶ") + bstack1ll111_opy_ (u"ࠢࠣῷ").join(bstack1llllll111l1_opy_[1:])
                }
        elif bstack1ll111_opy_ (u"ࠣࡒࡕࡓ࡝࡟ࠢῸ") in proxy:
            bstack1llllll111l1_opy_ = proxy.split(bstack1ll111_opy_ (u"ࠤࠣࠦΌ"))
            if bstack1ll111_opy_ (u"ࠥ࠾࠴࠵ࠢῺ") in bstack1ll111_opy_ (u"ࠦࠧΏ").join(bstack1llllll111l1_opy_[1:]):
                proxies = {
                    bstack1ll111_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࠫῼ"): bstack1ll111_opy_ (u"ࠨࠢ´").join(bstack1llllll111l1_opy_[1:])
                }
            else:
                proxies = {
                    bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴࡸ࠭῾"): bstack1ll111_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ῿") + bstack1ll111_opy_ (u"ࠤࠥ ").join(bstack1llllll111l1_opy_[1:])
                }
        else:
            proxies = {
                bstack1ll111_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩ "): proxy
            }
    except Exception as e:
        print(bstack1ll111_opy_ (u"ࠦࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠣ "), bstack111l111l1l1_opy_.format(bstack1lllll1lll11_opy_, str(e)))
    bstack1llllll11111_opy_ = proxies
    return proxies