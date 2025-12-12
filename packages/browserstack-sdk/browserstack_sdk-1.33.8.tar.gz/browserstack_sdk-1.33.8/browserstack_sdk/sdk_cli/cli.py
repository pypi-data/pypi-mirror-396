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
import json
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lllll1llll_opy_ import bstack1llllll111l_opy_
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll11l1_opy_ import bstack1lll1lll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll11llll1l_opy_ import bstack1ll1ll1lll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llll11_opy_ import bstack1ll1l111111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1ll1l1l11ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11111l1_opy_ import bstack1lll11lll1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1111l1_opy_ import bstack1ll1ll1l111_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1l1l_opy_ import bstack1lll1l1ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll1l1l_opy_ import bstack1lll111ll1l_opy_
from browserstack_sdk.sdk_cli.bstack111lll1l1_opy_ import bstack111lll1l1_opy_, bstack111llll1l_opy_, bstack1llllll1l1_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1lll11ll111_opy_ import bstack1ll1ll1ll11_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1111ll_opy_ import bstack1lll11l11ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import bstack1llll1lll1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lllllll_opy_ import bstack1ll11lll1ll_opy_
from bstack_utils.helper import Notset, bstack1lll11l1ll1_opy_, get_cli_dir, bstack1lll111111l_opy_, bstack11l11l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1lll1l1111l_opy_ import bstack1lll11l1l11_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11l1l11l_opy_ import bstack1ll1llll_opy_
from bstack_utils.helper import Notset, bstack1lll11l1ll1_opy_, get_cli_dir, bstack1lll111111l_opy_, bstack11l11l11l_opy_, bstack1l1l111111_opy_, bstack1ll1l11l1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l1lll1_opy_, bstack1ll1l1ll1ll_opy_, bstack1lll1l1llll_opy_, bstack1ll1ll1llll_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import bstack1lllll11111_opy_, bstack1llll1l1111_opy_, bstack1lllll11l11_opy_
from bstack_utils.constants import *
from bstack_utils.bstack1111l11ll_opy_ import bstack1lll1ll1l1_opy_
from bstack_utils import bstack1llll1ll1l_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1llll111l1_opy_, bstack11lll1ll1_opy_
logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack1llll1ll1l_opy_.bstack1ll1l111lll_opy_())
def bstack1ll1l1l1lll_opy_(bs_config):
    bstack1lll1ll1lll_opy_ = None
    bstack1ll1l1l111l_opy_ = None
    try:
        bstack1ll1l1l111l_opy_ = get_cli_dir()
        bstack1lll1ll1lll_opy_ = bstack1lll111111l_opy_(bstack1ll1l1l111l_opy_)
        bstack1ll1ll11lll_opy_ = bstack1lll11l1ll1_opy_(bstack1lll1ll1lll_opy_, bstack1ll1l1l111l_opy_, bs_config)
        bstack1lll1ll1lll_opy_ = bstack1ll1ll11lll_opy_ if bstack1ll1ll11lll_opy_ else bstack1lll1ll1lll_opy_
        if not bstack1lll1ll1lll_opy_:
            raise ValueError(bstack1ll111_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡔࡆࡎࡣࡈࡒࡉࡠࡄࡌࡒࡤࡖࡁࡕࡊࠥჳ"))
    except Exception as ex:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡸ࡭࡫ࠠ࡭ࡣࡷࡩࡸࡺࠠࡣ࡫ࡱࡥࡷࡿࠠࡼࡿࠥჴ").format(ex))
        bstack1lll1ll1lll_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠦჵ"))
        if bstack1lll1ll1lll_opy_:
            logger.debug(bstack1ll111_opy_ (u"ࠤࡉࡥࡱࡲࡩ࡯ࡩࠣࡦࡦࡩ࡫ࠡࡶࡲࠤࡘࡊࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡓࡅ࡙ࡎࠠࡧࡴࡲࡱࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶ࠽ࠤࠧჶ") + str(bstack1lll1ll1lll_opy_) + bstack1ll111_opy_ (u"ࠥࠦჷ"))
        else:
            logger.debug(bstack1ll111_opy_ (u"ࠦࡓࡵࠠࡷࡣ࡯࡭ࡩࠦࡓࡅࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡕࡇࡔࡉࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࡪࡴࡶࡪࡴࡲࡲࡲ࡫࡮ࡵ࠽ࠣࡷࡪࡺࡵࡱࠢࡰࡥࡾࠦࡢࡦࠢ࡬ࡲࡨࡵ࡭ࡱ࡮ࡨࡸࡪ࠴ࠢჸ"))
    return bstack1lll1ll1lll_opy_, bstack1ll1l1l111l_opy_
bstack1ll11llll11_opy_ = bstack1ll111_opy_ (u"ࠧ࠿࠹࠺࠻ࠥჹ")
bstack1ll1lll1l11_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡦࡣࡧࡽࠧჺ")
bstack1lll1l1ll11_opy_ = bstack1ll111_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡔࡇࡖࡗࡎࡕࡎࡠࡋࡇࠦ჻")
bstack1ll1lllll11_opy_ = bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡎࡌࡗ࡙ࡋࡎࡠࡃࡇࡈࡗࠨჼ")
bstack1l11l1ll11_opy_ = bstack1ll111_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠧჽ")
bstack1ll1l1l1ll1_opy_ = re.compile(bstack1ll111_opy_ (u"ࡵࠦ࠭ࡅࡩࠪ࠰࠭ࠬࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡿࡆࡘ࠯࠮ࠫࠤჾ"))
bstack1ll1l1l1l1l_opy_ = bstack1ll111_opy_ (u"ࠦࡩ࡫ࡶࡦ࡮ࡲࡴࡲ࡫࡮ࡵࠤჿ")
bstack1lll111l1l1_opy_ = bstack1ll111_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡕࡒࡄࡇࡢࡊࡆࡒࡌࡃࡃࡆࡏࠧᄀ")
bstack1ll1l111l1l_opy_ = [
    bstack111llll1l_opy_.bstack11l11l1lll_opy_,
    bstack111llll1l_opy_.CONNECT,
    bstack111llll1l_opy_.bstack11ll11ll_opy_,
]
class SDKCLI:
    _1ll1ll11ll1_opy_ = None
    process: Union[None, Any]
    bstack1ll1llllll1_opy_: bool
    bstack1ll1l1lllll_opy_: bool
    bstack1ll1l11llll_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1ll1l11ll1l_opy_: Union[None, grpc.Channel]
    bstack1lll1l11l1l_opy_: str
    test_framework: TestFramework
    bstack1llll1ll11l_opy_: bstack1llll1lll1l_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1lll111llll_opy_: bstack1lll111ll1l_opy_
    accessibility: bstack1lll1lll111_opy_
    bstack1l11l1l11l_opy_: bstack1ll1llll_opy_
    ai: bstack1ll1ll1lll1_opy_
    bstack1lll11l1l1l_opy_: bstack1ll1l111111_opy_
    bstack1lll1111lll_opy_: List[bstack1ll1ll1l1l1_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1lll1ll1111_opy_: Any
    bstack1ll1l11ll11_opy_: Dict[str, timedelta]
    bstack1lll1ll111l_opy_: str
    bstack1lllll1llll_opy_: bstack1llllll111l_opy_
    def __new__(cls):
        if not cls._1ll1ll11ll1_opy_:
            cls._1ll1ll11ll1_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1ll1ll11ll1_opy_
    def __init__(self):
        self.process = None
        self.bstack1ll1llllll1_opy_ = False
        self.bstack1ll1l11ll1l_opy_ = None
        self.bstack1lll1l11lll_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1ll1lllll11_opy_, None)
        self.bstack1ll1ll11111_opy_ = os.environ.get(bstack1lll1l1ll11_opy_, bstack1ll111_opy_ (u"ࠨࠢᄁ")) == bstack1ll111_opy_ (u"ࠢࠣᄂ")
        self.bstack1ll1l1lllll_opy_ = False
        self.bstack1ll1l11llll_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1lll1ll1111_opy_ = None
        self.test_framework = None
        self.bstack1llll1ll11l_opy_ = None
        self.bstack1lll1l11l1l_opy_=bstack1ll111_opy_ (u"ࠣࠤᄃ")
        self.session_framework = None
        self.logger = bstack1llll1ll1l_opy_.get_logger(self.__class__.__name__, bstack1llll1ll1l_opy_.bstack1ll1l111lll_opy_())
        self.bstack1ll1l11ll11_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack1lllll1llll_opy_ = bstack1llllll111l_opy_()
        self.bstack1ll1ll1l1ll_opy_ = None
        self.bstack1ll1l11111l_opy_ = None
        self.bstack1lll111llll_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1lll1111lll_opy_ = []
    def bstack1ll1l1111_opy_(self):
        return os.environ.get(bstack1l11l1ll11_opy_).lower().__eq__(bstack1ll111_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᄄ"))
    def is_enabled(self, config):
        if os.environ.get(bstack1lll111l1l1_opy_, bstack1ll111_opy_ (u"ࠪࠫᄅ")).lower() in [bstack1ll111_opy_ (u"ࠫࡹࡸࡵࡦࠩᄆ"), bstack1ll111_opy_ (u"ࠬ࠷ࠧᄇ"), bstack1ll111_opy_ (u"࠭ࡹࡦࡵࠪᄈ")]:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡇࡱࡵࡧ࡮ࡴࡧࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡱࡴࡪࡥࠡࡦࡸࡩࠥࡺ࡯ࠡࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡑࡕࡇࡊࡥࡆࡂࡎࡏࡆࡆࡉࡋࠡࡧࡱࡺ࡮ࡸ࡯࡯࡯ࡨࡲࡹࠦࡶࡢࡴ࡬ࡥࡧࡲࡥࠣᄉ"))
            os.environ[bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡊࡕࡢࡖ࡚ࡔࡎࡊࡐࡊࠦᄊ")] = bstack1ll111_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣᄋ")
            return False
        if bstack1ll111_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᄌ") in config and str(config[bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᄍ")]).lower() != bstack1ll111_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫᄎ"):
            return False
        bstack1ll1llll111_opy_ = [bstack1ll111_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᄏ"), bstack1ll111_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᄐ")]
        bstack1lll1lll1ll_opy_ = config.get(bstack1ll111_opy_ (u"ࠣࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠦᄑ")) in bstack1ll1llll111_opy_ or os.environ.get(bstack1ll111_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪᄒ")) in bstack1ll1llll111_opy_
        os.environ[bstack1ll111_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡌࡗࡤࡘࡕࡏࡐࡌࡒࡌࠨᄓ")] = str(bstack1lll1lll1ll_opy_) # bstack1ll1lll11ll_opy_ bstack1ll1l11lll1_opy_ VAR to bstack1ll1l11l11l_opy_ is binary running
        return bstack1lll1lll1ll_opy_
    def bstack1lll1llll_opy_(self):
        for event in bstack1ll1l111l1l_opy_:
            bstack111lll1l1_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack111lll1l1_opy_.logger.debug(bstack1ll111_opy_ (u"ࠦࢀ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࡿࠣࡁࡃࠦࡻࡢࡴࡪࡷࢂࠦࠢᄔ") + str(kwargs) + bstack1ll111_opy_ (u"ࠧࠨᄕ"))
            )
        bstack111lll1l1_opy_.register(bstack111llll1l_opy_.bstack11l11l1lll_opy_, self.__1lll1l1l111_opy_)
        bstack111lll1l1_opy_.register(bstack111llll1l_opy_.CONNECT, self.__1lll11ll1ll_opy_)
        bstack111lll1l1_opy_.register(bstack111llll1l_opy_.bstack11ll11ll_opy_, self.__1ll1l1l11l1_opy_)
        bstack111lll1l1_opy_.register(bstack111llll1l_opy_.bstack11llllllll_opy_, self.__1lll1l11l11_opy_)
    def bstack11llll1111_opy_(self):
        return not self.bstack1ll1ll11111_opy_ and os.environ.get(bstack1lll1l1ll11_opy_, bstack1ll111_opy_ (u"ࠨࠢᄖ")) != bstack1ll111_opy_ (u"ࠢࠣᄗ")
    def is_running(self):
        if self.bstack1ll1ll11111_opy_:
            return self.bstack1ll1llllll1_opy_
        else:
            return bool(self.bstack1ll1l11ll1l_opy_)
    def bstack1ll1l1ll111_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1lll1111lll_opy_) and cli.is_running()
    def __1ll1lllll1l_opy_(self, bstack1lll1ll1l11_opy_=10):
        if self.bstack1lll1l11lll_opy_:
            return
        bstack111ll1ll1_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1ll1lllll11_opy_, self.cli_listen_addr)
        self.logger.debug(bstack1ll111_opy_ (u"ࠣ࡝ࠥᄘ") + str(id(self)) + bstack1ll111_opy_ (u"ࠤࡠࠤࡨࡵ࡮࡯ࡧࡦࡸ࡮ࡴࡧࠣᄙ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack1ll111_opy_ (u"ࠥ࡫ࡷࡶࡣ࠯ࡧࡱࡥࡧࡲࡥࡠࡪࡷࡸࡵࡥࡰࡳࡱࡻࡽࠧᄚ"), 0), (bstack1ll111_opy_ (u"ࠦ࡬ࡸࡰࡤ࠰ࡨࡲࡦࡨ࡬ࡦࡡ࡫ࡸࡹࡶࡳࡠࡲࡵࡳࡽࡿࠢᄛ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1lll1ll1l11_opy_)
        self.bstack1ll1l11ll1l_opy_ = channel
        self.bstack1lll1l11lll_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1ll1l11ll1l_opy_)
        self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡧࡴࡴ࡮ࡦࡥࡷࠦᄜ"), datetime.now() - bstack111ll1ll1_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1ll1lllll11_opy_] = self.cli_listen_addr
        self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡩ࡯࡯ࡰࡨࡧࡹ࡫ࡤ࠻ࠢ࡬ࡷࡤࡩࡨࡪ࡮ࡧࡣࡵࡸ࡯ࡤࡧࡶࡷࡂࠨᄝ") + str(self.bstack11llll1111_opy_()) + bstack1ll111_opy_ (u"ࠢࠣᄞ"))
    def __1ll1l1l11l1_opy_(self, event_name):
        if self.bstack11llll1111_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡥ࡫࡭ࡱࡪ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡶࡸࡴࡶࡰࡪࡰࡪࠤࡈࡒࡉࠣᄟ"))
        self.__1ll1l1ll1l1_opy_()
    def __1lll1l11l11_opy_(self, event_name, bstack1ll1ll1111l_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack1ll111_opy_ (u"ࠤࡖࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨࠤᄠ"))
        bstack1lll111lll1_opy_ = Path(bstack1lll11ll11l_opy_ (u"ࠥࡿࡸ࡫࡬ࡧ࠰ࡦࡰ࡮ࡥࡤࡪࡴࢀ࠳ࡺࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࡸ࠴ࡪࡴࡱࡱࠦᄡ"))
        if self.bstack1ll1l1l111l_opy_ and bstack1lll111lll1_opy_.exists():
            with open(bstack1lll111lll1_opy_, bstack1ll111_opy_ (u"ࠫࡷ࠭ᄢ"), encoding=bstack1ll111_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᄣ")) as fp:
                data = json.load(fp)
                try:
                    bstack1l1l111111_opy_(bstack1ll111_opy_ (u"࠭ࡐࡐࡕࡗࠫᄤ"), bstack1lll1ll1l1_opy_(bstack111lll1l_opy_), data, {
                        bstack1ll111_opy_ (u"ࠧࡢࡷࡷ࡬ࠬᄥ"): (self.config[bstack1ll111_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪᄦ")], self.config[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬᄧ")])
                    })
                except Exception as e:
                    logger.debug(bstack11lll1ll1_opy_.format(str(e)))
            bstack1lll111lll1_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1ll1lll1ll1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1lll1l1l111_opy_(self, event_name: str, data):
        from bstack_utils.bstack1ll1lll11_opy_ import bstack1ll1ll111ll_opy_
        self.bstack1lll1l11l1l_opy_, self.bstack1ll1l1l111l_opy_ = bstack1ll1l1l1lll_opy_(data.bs_config)
        os.environ[bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡ࡚ࡖࡎ࡚ࡁࡃࡎࡈࡣࡉࡏࡒࠨᄨ")] = self.bstack1ll1l1l111l_opy_
        if not self.bstack1lll1l11l1l_opy_ or not self.bstack1ll1l1l111l_opy_:
            raise ValueError(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡺࡨࡦࠢࡖࡈࡐࠦࡃࡍࡋࠣࡦ࡮ࡴࡡࡳࡻࠥᄩ"))
        if self.bstack11llll1111_opy_():
            self.__1lll11ll1ll_opy_(event_name, bstack1llllll1l1_opy_())
            return
        try:
            bstack1ll1ll111ll_opy_.end(EVENTS.bstack11l11ll1l_opy_.value, EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᄪ"), EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᄫ"), status=True, failure=None, test_name=None)
            logger.debug(bstack1ll111_opy_ (u"ࠢࡄࡱࡰࡴࡱ࡫ࡴࡦࠢࡖࡈࡐࠦࡓࡦࡶࡸࡴ࠳ࠨᄬ"))
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴࠢࡾࢁࠧᄭ").format(e))
        start = datetime.now()
        is_started = self.__1ll1l1l1l11_opy_()
        self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠤࡶࡴࡦࡽ࡮ࡠࡶ࡬ࡱࡪࠨᄮ"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1ll1lllll1l_opy_()
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠥࡧࡴࡴ࡮ࡦࡥࡷࡣࡹ࡯࡭ࡦࠤᄯ"), datetime.now() - start)
            start = datetime.now()
            self.__1lll1111l1l_opy_(data)
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡹ࡯࡭ࡦࠤᄰ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1ll1l111l11_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1lll11ll1ll_opy_(self, event_name: str, data: bstack1llllll1l1_opy_):
        if not self.bstack11llll1111_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡥࡲࡲࡳ࡫ࡣࡵ࠼ࠣࡲࡴࡺࠠࡢࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᄱ"))
            return
        bin_session_id = os.environ.get(bstack1lll1l1ll11_opy_)
        start = datetime.now()
        self.__1ll1lllll1l_opy_()
        self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠨࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧᄲ"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack1ll111_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡤࡱࡱࡲࡪࡩࡴࡦࡦࠣࡸࡴࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡࡅࡏࡍࠥࠨᄳ") + str(bin_session_id) + bstack1ll111_opy_ (u"ࠣࠤᄴ"))
        start = datetime.now()
        self.__1ll1ll111l1_opy_()
        self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠤࡶࡸࡦࡸࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢᄵ"), datetime.now() - start)
    def __1lll11111ll_opy_(self):
        if not self.bstack1lll1l11lll_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡧࡦࡴ࡮ࡰࡶࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦ࡭ࡰࡦࡸࡰࡪࡹࠢᄶ"))
            return
        bstack1lll111ll11_opy_ = {
            bstack1ll111_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᄷ"): (bstack1ll1ll1l111_opy_, bstack1lll1l1ll1l_opy_, bstack1ll11lll1ll_opy_),
            bstack1ll111_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᄸ"): (bstack1ll1l1l11ll_opy_, bstack1lll11lll1l_opy_, bstack1lll11l11ll_opy_),
        }
        if not self.bstack1ll1ll1l1ll_opy_ and self.session_framework in bstack1lll111ll11_opy_:
            bstack1lll11l11l1_opy_, bstack1lll1l1l11l_opy_, bstack1ll11llllll_opy_ = bstack1lll111ll11_opy_[self.session_framework]
            bstack1lll1l1l1l1_opy_ = bstack1lll1l1l11l_opy_()
            self.bstack1ll1l11111l_opy_ = bstack1lll1l1l1l1_opy_
            self.bstack1ll1ll1l1ll_opy_ = bstack1ll11llllll_opy_
            self.bstack1lll1111lll_opy_.append(bstack1lll1l1l1l1_opy_)
            self.bstack1lll1111lll_opy_.append(bstack1lll11l11l1_opy_(self.bstack1ll1l11111l_opy_))
        if not self.bstack1lll111llll_opy_ and self.config_observability and self.config_observability.success: # bstack1ll1llll11l_opy_
            self.bstack1lll111llll_opy_ = bstack1lll111ll1l_opy_(self.bstack1ll1ll1l1ll_opy_, self.bstack1ll1l11111l_opy_) # bstack1lll1l11ll1_opy_
            self.bstack1lll1111lll_opy_.append(self.bstack1lll111llll_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1lll1lll111_opy_(self.bstack1ll1ll1l1ll_opy_, self.bstack1ll1l11111l_opy_)
            self.bstack1lll1111lll_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack1ll111_opy_ (u"ࠨࡳࡦ࡮ࡩࡌࡪࡧ࡬ࠣᄹ"), False) == True:
            self.ai = bstack1ll1ll1lll1_opy_()
            self.bstack1lll1111lll_opy_.append(self.ai)
        if not self.percy and self.bstack1lll1ll1111_opy_ and self.bstack1lll1ll1111_opy_.success:
            self.percy = bstack1ll1l111111_opy_(self.bstack1lll1ll1111_opy_)
            self.bstack1lll1111lll_opy_.append(self.percy)
        for mod in self.bstack1lll1111lll_opy_:
            if not mod.bstack1ll1llll1ll_opy_():
                mod.configure(self.bstack1lll1l11lll_opy_, self.config, self.cli_bin_session_id, self.bstack1lllll1llll_opy_)
    def __1ll1lll1lll_opy_(self):
        for mod in self.bstack1lll1111lll_opy_:
            if mod.bstack1ll1llll1ll_opy_():
                mod.configure(self.bstack1lll1l11lll_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1lll1l111ll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1lll1111l1l_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1ll1l1lllll_opy_:
            return
        self.__1ll1lll11l1_opy_(data)
        bstack111ll1ll1_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack1ll111_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢᄺ")
        req.sdk_language = bstack1ll111_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣᄻ")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1ll1l1l1ll1_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡞ࠦᄼ") + str(id(self)) + bstack1ll111_opy_ (u"ࠥࡡࠥࡳࡡࡪࡰ࠰ࡴࡷࡵࡣࡦࡵࡶ࠾ࠥࡹࡴࡢࡴࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᄽ"))
            r = self.bstack1lll1l11lll_opy_.StartBinSession(req)
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡸࡦࡸࡴࡠࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᄾ"), datetime.now() - bstack111ll1ll1_opy_)
            os.environ[bstack1lll1l1ll11_opy_] = r.bin_session_id
            self.__1lll111l11l_opy_(r)
            self.__1lll11111ll_opy_()
            self.bstack1lllll1llll_opy_.start()
            self.bstack1ll1l1lllll_opy_ = True
            self.logger.debug(bstack1ll111_opy_ (u"ࠧࡡࠢᄿ") + str(id(self)) + bstack1ll111_opy_ (u"ࠨ࡝ࠡ࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠦᅀ"))
        except grpc.bstack1lll11lllll_opy_ as bstack1ll1llll1l1_opy_:
            self.logger.error(bstack1ll111_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡴࡪ࡯ࡨࡳࡪࡻࡴ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᅁ") + str(bstack1ll1llll1l1_opy_) + bstack1ll111_opy_ (u"ࠣࠤᅂ"))
            traceback.print_exc()
            raise bstack1ll1llll1l1_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᅃ") + str(e) + bstack1ll111_opy_ (u"ࠥࠦᅄ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1ll1lll111l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1ll1ll111l1_opy_(self):
        if not self.bstack11llll1111_opy_() or not self.cli_bin_session_id or self.bstack1ll1l11llll_opy_:
            return
        bstack111ll1ll1_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᅅ"), bstack1ll111_opy_ (u"ࠬ࠶ࠧᅆ")))
        try:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡛ࠣᅇ") + str(id(self)) + bstack1ll111_opy_ (u"ࠢ࡞ࠢࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡧࡴࡴ࡮ࡦࡥࡷࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᅈ"))
            r = self.bstack1lll1l11lll_opy_.ConnectBinSession(req)
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡩࡵࡴࡨࡀࡣࡰࡰࡱࡩࡨࡺ࡟ࡣ࡫ࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᅉ"), datetime.now() - bstack111ll1ll1_opy_)
            self.__1lll111l11l_opy_(r)
            self.__1lll11111ll_opy_()
            self.bstack1lllll1llll_opy_.start()
            self.bstack1ll1l11llll_opy_ = True
            self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡞ࠦᅊ") + str(id(self)) + bstack1ll111_opy_ (u"ࠥࡡࠥࡩࡨࡪ࡮ࡧ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡣࡰࡰࡱࡩࡨࡺࡥࡥࠤᅋ"))
        except grpc.bstack1lll11lllll_opy_ as bstack1ll1llll1l1_opy_:
            self.logger.error(bstack1ll111_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡸ࡮ࡳࡥࡰࡧࡸࡸ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᅌ") + str(bstack1ll1llll1l1_opy_) + bstack1ll111_opy_ (u"ࠧࠨᅍ"))
            traceback.print_exc()
            raise bstack1ll1llll1l1_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᅎ") + str(e) + bstack1ll111_opy_ (u"ࠢࠣᅏ"))
            traceback.print_exc()
            raise e
    def __1lll111l11l_opy_(self, r):
        self.bstack1ll1l1lll1l_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack1ll111_opy_ (u"ࠣࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡹࡥࡳࡸࡨࡶࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢᅐ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack1ll111_opy_ (u"ࠤࡨࡱࡵࡺࡹࠡࡥࡲࡲ࡫࡯ࡧࠡࡨࡲࡹࡳࡪࠢᅑ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack1ll111_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡧࡵࡧࡾࠦࡩࡴࠢࡶࡩࡳࡺࠠࡰࡰ࡯ࡽࠥࡧࡳࠡࡲࡤࡶࡹࠦ࡯ࡧࠢࡷ࡬ࡪࠦࠢࡄࡱࡱࡲࡪࡩࡴࡃ࡫ࡱࡗࡪࡹࡳࡪࡱࡱ࠰ࠧࠦࡡ࡯ࡦࠣࡸ࡭࡯ࡳࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣ࡭ࡸࠦࡡ࡭ࡵࡲࠤࡺࡹࡥࡥࠢࡥࡽ࡙ࠥࡴࡢࡴࡷࡆ࡮ࡴࡓࡦࡵࡶ࡭ࡴࡴ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡗ࡬ࡪࡸࡥࡧࡱࡵࡩ࠱ࠦࡎࡰࡰࡨࠤ࡭ࡧ࡮ࡥ࡮࡬ࡲ࡬ࠦࡩࡴࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡪࡪ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧᅒ")
        self.bstack1lll1ll1111_opy_ = getattr(r, bstack1ll111_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᅓ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩᅔ")] = self.config_testhub.jwt
        os.environ[bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᅕ")] = self.config_testhub.build_hashed_id
    def bstack1ll1lll1111_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1ll1llllll1_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1lll1111111_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1lll1111111_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1ll1lll1111_opy_(event_name=EVENTS.bstack1lll1lll1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1ll1l1l1l11_opy_(self, bstack1lll1ll1l11_opy_=10):
        if self.bstack1ll1llllll1_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠢࡴࡶࡤࡶࡹࡀࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡴࡸࡲࡳ࡯࡮ࡨࠤᅖ"))
            return True
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡵࡷࡥࡷࡺࠢᅗ"))
        if os.getenv(bstack1ll111_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡏࡍࡤࡋࡎࡗࠤᅘ")) == bstack1ll1l1l1l1l_opy_:
            self.cli_bin_session_id = bstack1ll1l1l1l1l_opy_
            self.cli_listen_addr = bstack1ll111_opy_ (u"ࠥࡹࡳ࡯ࡸ࠻࠱ࡷࡱࡵ࠵ࡳࡥ࡭࠰ࡴࡱࡧࡴࡧࡱࡵࡱ࠲ࠫࡳ࠯ࡵࡲࡧࡰࠨᅙ") % (self.cli_bin_session_id)
            self.bstack1ll1llllll1_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1lll1l11l1l_opy_, bstack1ll111_opy_ (u"ࠦࡸࡪ࡫ࠣᅚ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1lll11ll1l1_opy_ compat for text=True in bstack1lll1l1l1ll_opy_ python
            encoding=bstack1ll111_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᅛ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1ll1l1l1111_opy_ = threading.Thread(target=self.__1ll1l11l1ll_opy_, args=(bstack1lll1ll1l11_opy_,))
        bstack1ll1l1l1111_opy_.start()
        bstack1ll1l1l1111_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡛ࡼ࡫ࡧࠬࡸ࡫࡬ࡧࠫࢀࡡࠥࡹࡰࡢࡹࡱ࠾ࠥࡸࡥࡵࡷࡵࡲࡨࡵࡤࡦ࠿ࡾࡷࡪࡲࡦ࠯ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡵࡩࡹࡻࡲ࡯ࡥࡲࡨࡪࢃࠠࡰࡷࡷࡁࢀࡹࡥ࡭ࡨ࠱ࡴࡷࡵࡣࡦࡵࡶ࠲ࡸࡺࡤࡰࡷࡷ࠲ࡷ࡫ࡡࡥࠪࠬࢁࠥ࡫ࡲࡳ࠿ࠥᅜ") + str(self.process.stderr.read()) + bstack1ll111_opy_ (u"ࠢࠣᅝ"))
        if not self.bstack1ll1llllll1_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠣ࡝ࠥᅞ") + str(id(self)) + bstack1ll111_opy_ (u"ࠤࡠࠤࡨࡲࡥࡢࡰࡸࡴࠧᅟ"))
            self.__1ll1l1ll1l1_opy_()
        self.logger.debug(bstack1ll111_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡳࡶࡴࡩࡥࡴࡵࡢࡶࡪࡧࡤࡺ࠼ࠣࠦᅠ") + str(self.bstack1ll1llllll1_opy_) + bstack1ll111_opy_ (u"ࠦࠧᅡ"))
        return self.bstack1ll1llllll1_opy_
    def __1ll1l11l1ll_opy_(self, bstack1ll1l11l111_opy_=10):
        bstack1lll1111ll1_opy_ = time.time()
        while self.process and time.time() - bstack1lll1111ll1_opy_ < bstack1ll1l11l111_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack1ll111_opy_ (u"ࠧ࡯ࡤ࠾ࠤᅢ") in line:
                    self.cli_bin_session_id = line.split(bstack1ll111_opy_ (u"ࠨࡩࡥ࠿ࠥᅣ"))[-1:][0].strip()
                    self.logger.debug(bstack1ll111_opy_ (u"ࠢࡤ࡮࡬ࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨ࠿ࠨᅤ") + str(self.cli_bin_session_id) + bstack1ll111_opy_ (u"ࠣࠤᅥ"))
                    continue
                if bstack1ll111_opy_ (u"ࠤ࡯࡭ࡸࡺࡥ࡯࠿ࠥᅦ") in line:
                    self.cli_listen_addr = line.split(bstack1ll111_opy_ (u"ࠥࡰ࡮ࡹࡴࡦࡰࡀࠦᅧ"))[-1:][0].strip()
                    self.logger.debug(bstack1ll111_opy_ (u"ࠦࡨࡲࡩࡠ࡮࡬ࡷࡹ࡫࡮ࡠࡣࡧࡨࡷࡀࠢᅨ") + str(self.cli_listen_addr) + bstack1ll111_opy_ (u"ࠧࠨᅩ"))
                    continue
                if bstack1ll111_opy_ (u"ࠨࡰࡰࡴࡷࡁࠧᅪ") in line:
                    port = line.split(bstack1ll111_opy_ (u"ࠢࡱࡱࡵࡸࡂࠨᅫ"))[-1:][0].strip()
                    self.logger.debug(bstack1ll111_opy_ (u"ࠣࡲࡲࡶࡹࡀࠢᅬ") + str(port) + bstack1ll111_opy_ (u"ࠤࠥᅭ"))
                    continue
                if line.strip() == bstack1ll1lll1l11_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack1ll111_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡋࡒࡁࡈࡡࡌࡓࡤ࡙ࡔࡓࡇࡄࡑࠧᅮ"), bstack1ll111_opy_ (u"ࠦ࠶ࠨᅯ")) == bstack1ll111_opy_ (u"ࠧ࠷ࠢᅰ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1ll1llllll1_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack1ll111_opy_ (u"ࠨࡥࡳࡴࡲࡶ࠿ࠦࠢᅱ") + str(e) + bstack1ll111_opy_ (u"ࠢࠣᅲ"))
        return False
    @measure(event_name=EVENTS.bstack1ll1l1ll11l_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def __1ll1l1ll1l1_opy_(self):
        if self.bstack1ll1l11ll1l_opy_:
            self.bstack1lllll1llll_opy_.stop()
            start = datetime.now()
            if self.bstack1lll11lll11_opy_():
                self.cli_bin_session_id = None
                if self.bstack1ll1l11llll_opy_:
                    self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡵࡷࡳࡵࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡵ࡫ࡰࡩࠧᅳ"), datetime.now() - start)
                else:
                    self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠤࡶࡸࡴࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨᅴ"), datetime.now() - start)
            self.__1ll1lll1lll_opy_()
            start = datetime.now()
            self.bstack1ll1l11ll1l_opy_.close()
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠥࡨ࡮ࡹࡣࡰࡰࡱࡩࡨࡺ࡟ࡵ࡫ࡰࡩࠧᅵ"), datetime.now() - start)
            self.bstack1ll1l11ll1l_opy_ = None
        if self.process:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡸࡺ࡯ࡱࠤᅶ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠧࡱࡩ࡭࡮ࡢࡸ࡮ࡳࡥࠣᅷ"), datetime.now() - start)
            self.process = None
            if self.bstack1ll1ll11111_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack11llll1lll_opy_()
                self.logger.info(
                    bstack1ll111_opy_ (u"ࠨࡖࡪࡵ࡬ࡸࠥ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳࠨᅸ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack1ll111_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭ᅹ")] = self.config_testhub.build_hashed_id
        self.bstack1ll1llllll1_opy_ = False
    def __1ll1lll11l1_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack1ll111_opy_ (u"ࠣࡵࡨࡰࡪࡴࡩࡶ࡯ࠥᅺ")] = selenium.__version__
            data.frameworks.append(bstack1ll111_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᅻ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack1ll111_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᅼ")] = __version__
            data.frameworks.append(bstack1ll111_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᅽ"))
        except:
            pass
    def bstack1lll1l111l1_opy_(self, hub_url: str, platform_index: int, bstack1ll1l111l1_opy_: Any):
        if self.bstack1llll1ll11l_opy_:
            self.logger.debug(bstack1ll111_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠦࡳࡦࡶࡸࡴࠥࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡶࡩࡹࠦࡵࡱࠤᅾ"))
            return
        try:
            bstack111ll1ll1_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack1ll111_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣᅿ")
            self.bstack1llll1ll11l_opy_ = bstack1lll11l11ll_opy_(
                cli.config.get(bstack1ll111_opy_ (u"ࠢࡩࡷࡥ࡙ࡷࡲࠢᆀ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1ll1ll1l11l_opy_={bstack1ll111_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࡡࡩࡶࡴࡳ࡟ࡤࡣࡳࡷࠧᆁ"): bstack1ll1l111l1_opy_}
            )
            def bstack1lll1lll11l_opy_(self):
                return
            if self.config.get(bstack1ll111_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠦᆂ"), True):
                Service.start = bstack1lll1lll11l_opy_
                Service.stop = bstack1lll1lll11l_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.upload_attachment = staticmethod(bstack1ll1llll_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1lll11l1l11_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠥࡷࡪࡺࡵࡱࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᆃ"), datetime.now() - bstack111ll1ll1_opy_)
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡷࡹࡵࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠻ࠢࠥᆄ") + str(e) + bstack1ll111_opy_ (u"ࠧࠨᆅ"))
    def bstack1lll11l111l_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack1ll111l1l_opy_
            self.bstack1llll1ll11l_opy_ = bstack1ll11lll1ll_opy_(
                platform_index,
                framework_name=bstack1ll111_opy_ (u"ࠨࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥᆆ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡀࠠࠣᆇ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤᆈ"))
            pass
    def bstack1lll111l1ll_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡶ࡯࡮ࡶࡰࡦࡦࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࡥࡱࡸࡥࡢࡦࡼࠤࡸ࡫ࡴࠡࡷࡳࠦᆉ"))
            return
        if bstack11l11l11l_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack1ll111_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶࠥᆊ"): pytest.__version__ }, [bstack1ll111_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᆋ")], self.bstack1lllll1llll_opy_, self.bstack1lll1l11lll_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1ll1ll11_opy_({ bstack1ll111_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᆌ"): pytest.__version__ }, [bstack1ll111_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᆍ")], self.bstack1lllll1llll_opy_, self.bstack1lll1l11lll_opy_)
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱࠢࡳࡽࡹ࡫ࡳࡵ࠼ࠣࠦᆎ") + str(e) + bstack1ll111_opy_ (u"ࠣࠤᆏ"))
        self.bstack1ll1ll11l1l_opy_()
    def bstack1ll1ll11l1l_opy_(self):
        if not self.bstack1ll1l1111_opy_():
            return
        bstack11l111ll11_opy_ = None
        def bstack1l1l1l11l_opy_(config, startdir):
            return bstack1ll111_opy_ (u"ࠤࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿ࠵ࢃࠢᆐ").format(bstack1ll111_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠤᆑ"))
        def bstack1l1ll11111_opy_():
            return
        def bstack1l1l1ll111_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack1ll111_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫᆒ"):
                return bstack1ll111_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦᆓ")
            else:
                return bstack11l111ll11_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack11l111ll11_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack1l1l1l11l_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l1ll11111_opy_
            Config.getoption = bstack1l1l1ll111_opy_
        except Exception as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡹࡩࡨࠡࡲࡼࡸࡪࡹࡴࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࠣࡪࡴࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡀࠠࠣᆔ") + str(e) + bstack1ll111_opy_ (u"ࠢࠣᆕ"))
    def bstack1lll111l111_opy_(self):
        bstack11111lll1_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack11111lll1_opy_, dict):
            if cli.config_observability:
                bstack11111lll1_opy_.update(
                    {bstack1ll111_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣᆖ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack1ll111_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡶࡣࡹࡵ࡟ࡸࡴࡤࡴࠧᆗ") in accessibility.get(bstack1ll111_opy_ (u"ࠥࡳࡵࡺࡩࡰࡰࡶࠦᆘ"), {}):
                    bstack1ll1l1llll1_opy_ = accessibility.get(bstack1ll111_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᆙ"))
                    bstack1ll1l1llll1_opy_.update({ bstack1ll111_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࡔࡰ࡙ࡵࡥࡵࠨᆚ"): bstack1ll1l1llll1_opy_.pop(bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࡠࡶࡲࡣࡼࡸࡡࡱࠤᆛ")) })
                bstack11111lll1_opy_.update({bstack1ll111_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢᆜ"): accessibility })
        return bstack11111lll1_opy_
    @measure(event_name=EVENTS.bstack1ll11lllll1_opy_, stage=STAGE.bstack11ll1lll1_opy_)
    def bstack1lll11lll11_opy_(self, bstack1ll1l11l1l1_opy_: str = None, bstack1lll1111l11_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1lll1l11lll_opy_:
            return
        bstack111ll1ll1_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1ll1l11l1l1_opy_:
            req.bstack1ll1l11l1l1_opy_ = bstack1ll1l11l1l1_opy_
        if bstack1lll1111l11_opy_:
            req.bstack1lll1111l11_opy_ = bstack1lll1111l11_opy_
        try:
            r = self.bstack1lll1l11lll_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack1l1111ll1l_opy_(bstack1ll111_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡵࡱࡳࡣࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠤᆝ"), datetime.now() - bstack111ll1ll1_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack1l1111ll1l_opy_(self, key: str, value: timedelta):
        tag = bstack1ll111_opy_ (u"ࠤࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᆞ") if self.bstack11llll1111_opy_() else bstack1ll111_opy_ (u"ࠥࡱࡦ࡯࡮࠮ࡲࡵࡳࡨ࡫ࡳࡴࠤᆟ")
        self.bstack1ll1l11ll11_opy_[bstack1ll111_opy_ (u"ࠦ࠿ࠨᆠ").join([tag + bstack1ll111_opy_ (u"ࠧ࠳ࠢᆡ") + str(id(self)), key])] += value
    def bstack11llll1lll_opy_(self):
        if not os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡆࡄࡘࡋࡤࡖࡅࡓࡈࠥᆢ"), bstack1ll111_opy_ (u"ࠢ࠱ࠤᆣ")) == bstack1ll111_opy_ (u"ࠣ࠳ࠥᆤ"):
            return
        bstack1lll11l1111_opy_ = dict()
        bstack1lll1llllll_opy_ = []
        if self.test_framework:
            bstack1lll1llllll_opy_.extend(list(self.test_framework.bstack1lll1llllll_opy_.values()))
        if self.bstack1llll1ll11l_opy_:
            bstack1lll1llllll_opy_.extend(list(self.bstack1llll1ll11l_opy_.bstack1lll1llllll_opy_.values()))
        for instance in bstack1lll1llllll_opy_:
            if not instance.platform_index in bstack1lll11l1111_opy_:
                bstack1lll11l1111_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1lll11l1111_opy_[instance.platform_index]
            for k, v in instance.bstack1ll1ll11l11_opy_().items():
                report[k] += v
                report[k.split(bstack1ll111_opy_ (u"ࠤ࠽ࠦᆥ"))[0]] += v
        bstack1ll1l1lll11_opy_ = sorted([(k, v) for k, v in self.bstack1ll1l11ll11_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1ll1ll1ll1l_opy_ = 0
        for r in bstack1ll1l1lll11_opy_:
            bstack1lll1ll11ll_opy_ = r[1].total_seconds()
            bstack1ll1ll1ll1l_opy_ += bstack1lll1ll11ll_opy_
            self.logger.debug(bstack1ll111_opy_ (u"ࠥ࡟ࡵ࡫ࡲࡧ࡟ࠣࡧࡱ࡯࠺ࡼࡴ࡞࠴ࡢࢃ࠽ࠣᆦ") + str(bstack1lll1ll11ll_opy_) + bstack1ll111_opy_ (u"ࠦࠧᆧ"))
        self.logger.debug(bstack1ll111_opy_ (u"ࠧ࠳࠭ࠣᆨ"))
        bstack1lll1l11111_opy_ = []
        for platform_index, report in bstack1lll11l1111_opy_.items():
            bstack1lll1l11111_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1lll1l11111_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack11lll111_opy_ = set()
        bstack1ll1l111ll1_opy_ = 0
        for r in bstack1lll1l11111_opy_:
            bstack1lll1ll11ll_opy_ = r[2].total_seconds()
            bstack1ll1l111ll1_opy_ += bstack1lll1ll11ll_opy_
            bstack11lll111_opy_.add(r[0])
            self.logger.debug(bstack1ll111_opy_ (u"ࠨ࡛ࡱࡧࡵࡪࡢࠦࡴࡦࡵࡷ࠾ࡵࡲࡡࡵࡨࡲࡶࡲ࠳ࡻࡳ࡝࠳ࡡࢂࡀࡻࡳ࡝࠴ࡡࢂࡃࠢᆩ") + str(bstack1lll1ll11ll_opy_) + bstack1ll111_opy_ (u"ࠢࠣᆪ"))
        if self.bstack11llll1111_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠣ࠯࠰ࠦᆫ"))
            self.logger.debug(bstack1ll111_opy_ (u"ࠤ࡞ࡴࡪࡸࡦ࡞ࠢࡦࡰ࡮ࡀࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡃࡻࡵࡱࡷࡥࡱࡥࡣ࡭࡫ࢀࠤࡹ࡫ࡳࡵ࠼ࡳࡰࡦࡺࡦࡰࡴࡰࡷ࠲ࢁࡳࡵࡴࠫࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠯ࡽ࠾ࠤᆬ") + str(bstack1ll1l111ll1_opy_) + bstack1ll111_opy_ (u"ࠥࠦᆭ"))
        else:
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡠࡶࡥࡳࡨࡠࠤࡨࡲࡩ࠻࡯ࡤ࡭ࡳ࠳ࡰࡳࡱࡦࡩࡸࡹ࠽ࠣᆮ") + str(bstack1ll1ll1ll1l_opy_) + bstack1ll111_opy_ (u"ࠧࠨᆯ"))
        self.logger.debug(bstack1ll111_opy_ (u"ࠨ࠭࠮ࠤᆰ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str, orchestration_metadata: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files,
            orchestration_metadata=orchestration_metadata
        )
        if not self.bstack1lll1l11lll_opy_:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡤ࡮࡬ࡣࡸ࡫ࡲࡷ࡫ࡦࡩࠥ࡯ࡳࠡࡰࡲࡸࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡦࡦ࠱ࠤࡈࡧ࡮࡯ࡱࡷࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡺࡥࡴࡶࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦᆱ"))
            return None
        response = self.bstack1lll1l11lll_opy_.TestOrchestration(request)
        self.logger.debug(bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹ࠳࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠳ࡳࡦࡵࡶ࡭ࡴࡴ࠽ࡼࡿࠥᆲ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1ll1l1lll1l_opy_(self, r):
        if r is not None and getattr(r, bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࠪᆳ"), None) and getattr(r.testhub, bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵࠪᆴ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack1ll111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᆵ")))
            for bstack1lll11l1lll_opy_, err in errors.items():
                if err[bstack1ll111_opy_ (u"ࠬࡺࡹࡱࡧࠪᆶ")] == bstack1ll111_opy_ (u"࠭ࡩ࡯ࡨࡲࠫᆷ"):
                    self.logger.info(err[bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᆸ")])
                else:
                    self.logger.error(err[bstack1ll111_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᆹ")])
    def bstack1ll1l1l11_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()