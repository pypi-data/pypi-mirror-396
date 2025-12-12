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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack1llll1ll1l_opy_ import get_logger
logger = get_logger(__name__)
bstack1llllll111ll_opy_: Dict[str, float] = {}
bstack1llllll1l11l_opy_: List = []
bstack1llllll1l1ll_opy_ = 5
bstack11ll111l11_opy_ = os.path.join(os.getcwd(), bstack1ll111_opy_ (u"ࠬࡲ࡯ࡨࠩῄ"), bstack1ll111_opy_ (u"࠭࡫ࡦࡻ࠰ࡱࡪࡺࡲࡪࡥࡶ࠲࡯ࡹ࡯࡯ࠩ῅"))
logging.getLogger(bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡱࡵࡣ࡬ࠩῆ")).setLevel(logging.WARNING)
lock = FileLock(bstack11ll111l11_opy_+bstack1ll111_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢῇ"))
class bstack1llllll11l1l_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack1llllll1l1l1_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1llllll1l1l1_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack1ll111_opy_ (u"ࠤࡰࡩࡦࡹࡵࡳࡧࠥῈ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1ll1ll111ll_opy_:
    global bstack1llllll111ll_opy_
    @staticmethod
    def bstack1ll111ll11l_opy_(key: str):
        bstack1ll111lllll_opy_ = bstack1ll1ll111ll_opy_.bstack11ll1111lll_opy_(key)
        bstack1ll1ll111ll_opy_.mark(bstack1ll111lllll_opy_+bstack1ll111_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥΈ"))
        return bstack1ll111lllll_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1llllll111ll_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠦࡊࡸࡲࡰࡴ࠽ࠤࢀࢃࠢῊ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1ll1ll111ll_opy_.mark(end)
            bstack1ll1ll111ll_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠ࡬ࡧࡼࠤࡲ࡫ࡴࡳ࡫ࡦࡷ࠿ࠦࡻࡾࠤΉ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1llllll111ll_opy_ or end not in bstack1llllll111ll_opy_:
                logger.debug(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡷࡥࡷࡺࠠ࡬ࡧࡼࠤࡼ࡯ࡴࡩࠢࡹࡥࡱࡻࡥࠡࡽࢀࠤࡴࡸࠠࡦࡰࡧࠤࡰ࡫ࡹࠡࡹ࡬ࡸ࡭ࠦࡶࡢ࡮ࡸࡩࠥࢁࡽࠣῌ").format(start,end))
                return
            duration: float = bstack1llllll111ll_opy_[end] - bstack1llllll111ll_opy_[start]
            bstack1llllll11l11_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡉࡔࡡࡕ࡙ࡓࡔࡉࡏࡉࠥ῍"), bstack1ll111_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢ῎")).lower() == bstack1ll111_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ῏")
            bstack1llllll11lll_opy_: bstack1llllll11l1l_opy_ = bstack1llllll11l1l_opy_(duration, label, bstack1llllll111ll_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠥῐ"), 0), command, test_name, hook_type, bstack1llllll11l11_opy_)
            del bstack1llllll111ll_opy_[start]
            del bstack1llllll111ll_opy_[end]
            bstack1ll1ll111ll_opy_.bstack1llllll11ll1_opy_(bstack1llllll11lll_opy_)
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡰࡩࡦࡹࡵࡳ࡫ࡱ࡫ࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵ࠽ࠤࢀࢃࠢῑ").format(e))
    @staticmethod
    def bstack1llllll11ll1_opy_(bstack1llllll11lll_opy_):
        os.makedirs(os.path.dirname(bstack11ll111l11_opy_)) if not os.path.exists(os.path.dirname(bstack11ll111l11_opy_)) else None
        bstack1ll1ll111ll_opy_.bstack1llllll1ll11_opy_()
        try:
            with lock:
                with open(bstack11ll111l11_opy_, bstack1ll111_opy_ (u"ࠧࡸࠫࠣῒ"), encoding=bstack1ll111_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧΐ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1llllll11lll_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack1llllll1l111_opy_:
            logger.debug(bstack1ll111_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤࠡࡽࢀࠦ῔").format(bstack1llllll1l111_opy_))
            with lock:
                with open(bstack11ll111l11_opy_, bstack1ll111_opy_ (u"ࠣࡹࠥ῕"), encoding=bstack1ll111_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣῖ")) as file:
                    data = [bstack1llllll11lll_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵࠣࡥࡵࡶࡥ࡯ࡦࠣࡿࢂࠨῗ").format(str(e)))
        finally:
            if os.path.exists(bstack11ll111l11_opy_+bstack1ll111_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥῘ")):
                os.remove(bstack11ll111l11_opy_+bstack1ll111_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦῙ"))
    @staticmethod
    def bstack1llllll1ll11_opy_():
        attempt = 0
        while (attempt < bstack1llllll1l1ll_opy_):
            attempt += 1
            if os.path.exists(bstack11ll111l11_opy_+bstack1ll111_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧῚ")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll1111lll_opy_(label: str) -> str:
        try:
            return bstack1ll111_opy_ (u"ࠢࡼࡿ࠽ࡿࢂࠨΊ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡵࡶࡴࡸ࠺ࠡࡽࢀࠦ῜").format(e))