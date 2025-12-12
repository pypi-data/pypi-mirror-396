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
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack1ll1lll11_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack1l1l111ll_opy_, bstack111lll1ll1_opy_, update, bstack1ll1l111l1_opy_,
                                       bstack1l1l1l11l_opy_, bstack1l1ll11111_opy_, bstack11l1111ll1_opy_, bstack1lll1lll1_opy_,
                                       bstack1llll1ll11_opy_, bstack111111ll1_opy_, bstack1l1l1111l_opy_,
                                       bstack1l11111ll1_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack1l1llll11_opy_)
from browserstack_sdk.bstack1llll11lll_opy_ import bstack1lll1111ll_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1llll1ll1l_opy_
from bstack_utils.capture import bstack111l1lllll_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack11111111_opy_, bstack11l11l11ll_opy_, bstack1111l1ll_opy_, \
    bstack1l11l11l1_opy_
from bstack_utils.helper import bstack11111l1l1_opy_, bstack11l1111ll11_opy_, bstack1111l1lll1_opy_, bstack1ll1l1l1ll_opy_, bstack1l1l11l1l1l_opy_, bstack11ll1l111_opy_, \
    bstack111lll1111l_opy_, \
    bstack111lllll1l1_opy_, bstack111l111l_opy_, bstack111111lll_opy_, bstack111l1lll111_opy_, bstack11l11l11l_opy_, Notset, \
    bstack11l1lll11l_opy_, bstack111ll1lll1l_opy_, bstack111ll11l11l_opy_, Result, bstack11l11l111l1_opy_, bstack111llllll11_opy_, error_handler, \
    bstack1lll11l1l_opy_, bstack1ll1111lll_opy_, bstack1l1l1111l1_opy_, bstack111ll1l1lll_opy_
from bstack_utils.bstack111l1l1lll1_opy_ import bstack111l1l11l1l_opy_
from bstack_utils.messages import bstack11llll1l11_opy_, bstack11l111l11_opy_, bstack11111l1l_opy_, bstack1lll11l11l_opy_, bstack11l1l1l11l_opy_, \
    bstack1l111ll1_opy_, bstack1l1l1l11ll_opy_, bstack1l11l11l_opy_, bstack1l11ll11l_opy_, bstack1llll11l_opy_, \
    bstack11l1lllll_opy_, bstack1l11l11ll_opy_, bstack1l1l1lll_opy_
from bstack_utils.proxy import bstack1ll1ll111l_opy_, bstack1l11ll1ll1_opy_
from bstack_utils.bstack11ll11ll1_opy_ import bstack1lllll1l11l1_opy_, bstack1lllll1l11ll_opy_, bstack1lllll11llll_opy_, bstack1lllll1l1111_opy_, \
    bstack1lllll1ll1l1_opy_, bstack1lllll1ll1ll_opy_, bstack1lllll1l1l11_opy_, bstack1ll11111l1_opy_, bstack1lllll1l111l_opy_
from bstack_utils.bstack1lllll111l_opy_ import bstack111llllll1_opy_
from bstack_utils.bstack1l11l1111_opy_ import bstack1l111l1l11_opy_, bstack1lll1l111_opy_, bstack11ll1l1l1l_opy_, \
    bstack11ll1ll11_opy_, bstack1l1l1ll1l1_opy_
from bstack_utils.bstack111ll11ll1_opy_ import bstack111ll1l1l1_opy_
from bstack_utils.bstack111ll1l11l_opy_ import bstack1llll1111_opy_
import bstack_utils.accessibility as bstack1llll111_opy_
from bstack_utils.bstack111l1llll1_opy_ import bstack111l1l111_opy_
from bstack_utils.bstack111llll1ll_opy_ import bstack111llll1ll_opy_
from bstack_utils.bstack1llll1l11l_opy_ import bstack11ll1lll1l_opy_
from browserstack_sdk.__init__ import bstack1l1l11l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1lll1l1l_opy_ import bstack1lll111ll1l_opy_
from browserstack_sdk.sdk_cli.bstack111lll1l1_opy_ import bstack111lll1l1_opy_, bstack111llll1l_opy_, bstack1llllll1l1_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1l1111l1111_opy_, bstack1lll1l1lll1_opy_, bstack1lll1l1llll_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack111lll1l1_opy_ import bstack111lll1l1_opy_, bstack111llll1l_opy_, bstack1llllll1l1_opy_
bstack1lll111111_opy_ = None
bstack111llll111_opy_ = None
bstack1llll1l1l_opy_ = None
bstack11ll11ll1l_opy_ = None
bstack11l1l1l1ll_opy_ = None
bstack1l11ll111l_opy_ = None
bstack11ll1l1ll1_opy_ = None
bstack1111l1l1l_opy_ = None
bstack1l11llllll_opy_ = None
bstack1lllll1ll1_opy_ = None
bstack11l111ll11_opy_ = None
bstack1lllllllll_opy_ = None
bstack111ll11l1_opy_ = None
bstack1ll11lllll_opy_ = bstack1ll111_opy_ (u"ࠧࠨ⊬")
CONFIG = {}
bstack1l11l1111l_opy_ = False
bstack1ll1l111l_opy_ = bstack1ll111_opy_ (u"ࠨࠩ⊭")
bstack1l1lllll_opy_ = bstack1ll111_opy_ (u"ࠩࠪ⊮")
bstack1l1lll1l11_opy_ = False
bstack1ll111ll1l_opy_ = []
bstack111llll11l_opy_ = bstack11111111_opy_
bstack1lll1l111l1l_opy_ = bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ⊯")
bstack1l1111l111_opy_ = {}
bstack11l1l1111l_opy_ = None
bstack1l1l1111_opy_ = False
logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack111llll11l_opy_)
store = {
    bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⊰"): []
}
bstack1lll1l11l1l1_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_1111ll11ll_opy_ = {}
current_test_uuid = None
cli_context = bstack1l1111l1111_opy_(
    test_framework_name=bstack1l11l1lll_opy_[bstack1ll111_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘ࠲ࡈࡄࡅࠩ⊱")] if bstack11l11l11l_opy_() else bstack1l11l1lll_opy_[bstack1ll111_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠭⊲")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack1l1lllll1_opy_(page, bstack1l11l1l1_opy_):
    try:
        page.evaluate(bstack1ll111_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ⊳"),
                      bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠬ⊴") + json.dumps(
                          bstack1l11l1l1_opy_) + bstack1ll111_opy_ (u"ࠤࢀࢁࠧ⊵"))
    except Exception as e:
        print(bstack1ll111_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥࢁࡽࠣ⊶"), e)
def bstack11llll1l1l_opy_(page, message, level):
    try:
        page.evaluate(bstack1ll111_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧ⊷"), bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ⊸") + json.dumps(
            message) + bstack1ll111_opy_ (u"࠭ࠬࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠩ⊹") + json.dumps(level) + bstack1ll111_opy_ (u"ࠧࡾࡿࠪ⊺"))
    except Exception as e:
        print(bstack1ll111_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡦࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠡࡽࢀࠦ⊻"), e)
def pytest_configure(config):
    global bstack1ll1l111l_opy_
    global CONFIG
    bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
    config.args = bstack1llll1111_opy_.bstack1lll1ll111l1_opy_(config.args)
    bstack11ll11l11l_opy_.bstack11l1l111ll_opy_(bstack1l1l1111l1_opy_(config.getoption(bstack1ll111_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ࠭⊼"))))
    try:
        bstack1llll1ll1l_opy_.bstack111l11l1l11_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.CONNECT, bstack1llllll1l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⊽"), bstack1ll111_opy_ (u"ࠫ࠵࠭⊾")))
        config = json.loads(os.environ.get(bstack1ll111_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡕࡎࡇࡋࡊࠦ⊿"), bstack1ll111_opy_ (u"ࠨࡻࡾࠤ⋀")))
        cli.bstack1lll1l111l1_opy_(bstack111111lll_opy_(bstack1ll1l111l_opy_, CONFIG), cli_context.platform_index, bstack1ll1l111l1_opy_)
    if cli.bstack1ll1l1ll111_opy_(bstack1lll111ll1l_opy_):
        cli.bstack1lll111l1ll_opy_()
        logger.debug(bstack1ll111_opy_ (u"ࠢࡄࡎࡌࠤ࡮ࡹࠠࡢࡥࡷ࡭ࡻ࡫ࠠࡧࡱࡵࠤࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࡂࠨ⋁") + str(cli_context.platform_index) + bstack1ll111_opy_ (u"ࠣࠤ⋂"))
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.BEFORE_ALL, bstack1lll1l1llll_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack1ll111_opy_ (u"ࠤࡺ࡬ࡪࡴࠢ⋃"), None)
    if cli.is_running() and when == bstack1ll111_opy_ (u"ࠥࡧࡦࡲ࡬ࠣ⋄"):
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.LOG_REPORT, bstack1lll1l1llll_opy_.PRE, item, call)
    outcome = yield
    if when == bstack1ll111_opy_ (u"ࠦࡨࡧ࡬࡭ࠤ⋅"):
        report = outcome.get_result()
        passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1ll111_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⋆")))
        if not passed:
            config = json.loads(os.environ.get(bstack1ll111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡏࡏࡈࡌࡋࠧ⋇"), bstack1ll111_opy_ (u"ࠢࡼࡿࠥ⋈")))
            if bstack11ll1lll1l_opy_.bstack11ll1l11_opy_(config):
                bstack11111l1llll_opy_ = bstack11ll1lll1l_opy_.bstack1l11l1l1ll_opy_(config)
                if item.execution_count > bstack11111l1llll_opy_:
                    print(bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࠦࡦࡢ࡫࡯ࡩࡩࠦࡡࡧࡶࡨࡶࠥࡸࡥࡵࡴ࡬ࡩࡸࡀࠠࠨ⋉"), report.nodeid, os.environ.get(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ⋊")))
                    bstack11ll1lll1l_opy_.bstack11111lllll1_opy_(report.nodeid)
            else:
                print(bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢࠪ⋋"), report.nodeid, os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ⋌")))
                bstack11ll1lll1l_opy_.bstack11111lllll1_opy_(report.nodeid)
        else:
            print(bstack1ll111_opy_ (u"࡚ࠬࡥࡴࡶࠣࡴࡦࡹࡳࡦࡦ࠽ࠤࠬ⋍"), report.nodeid, os.environ.get(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ⋎")))
    if cli.is_running():
        if when == bstack1ll111_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨ⋏"):
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.BEFORE_EACH, bstack1lll1l1llll_opy_.POST, item, call, outcome)
        elif when == bstack1ll111_opy_ (u"ࠣࡥࡤࡰࡱࠨ⋐"):
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.LOG_REPORT, bstack1lll1l1llll_opy_.POST, item, call, outcome)
        elif when == bstack1ll111_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦ⋑"):
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.AFTER_EACH, bstack1lll1l1llll_opy_.POST, item, call, outcome)
        return # skip all existing operations
    skipSessionName = item.config.getoption(bstack1ll111_opy_ (u"ࠪࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ⋒"))
    plugins = item.config.getoption(bstack1ll111_opy_ (u"ࠦࡵࡲࡵࡨ࡫ࡱࡷࠧ⋓"))
    report = outcome.get_result()
    os.environ[bstack1ll111_opy_ (u"ࠬࡖ࡙ࡕࡇࡖࡘࡤ࡚ࡅࡔࡖࡢࡒࡆࡓࡅࠨ⋔")] = report.nodeid
    bstack1lll1l111ll1_opy_(item, call, report)
    if bstack1ll111_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡵࡲࡵࡨ࡫ࡱࠦ⋕") not in plugins or bstack11l11l11l_opy_():
        return
    summary = []
    driver = getattr(item, bstack1ll111_opy_ (u"ࠢࡠࡦࡵ࡭ࡻ࡫ࡲࠣ⋖"), None)
    page = getattr(item, bstack1ll111_opy_ (u"ࠣࡡࡳࡥ࡬࡫ࠢ⋗"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack1lll1l1lll11_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack1lll1l1llll1_opy_(item, report, summary, skipSessionName)
def bstack1lll1l1lll11_opy_(item, report, summary, skipSessionName):
    if report.when == bstack1ll111_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⋘") and report.skipped:
        bstack1lllll1l111l_opy_(report)
    if report.when in [bstack1ll111_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤ⋙"), bstack1ll111_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨ⋚")]:
        return
    if not bstack1l1l11l1l1l_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack1ll111_opy_ (u"ࠬࡺࡲࡶࡧࠪ⋛")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠣࠫ⋜") + json.dumps(
                    report.nodeid) + bstack1ll111_opy_ (u"ࠧࡾࡿࠪ⋝"))
        os.environ[bstack1ll111_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ⋞")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack1ll111_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠ࡮ࡣࡵ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨ࠾ࠥࢁ࠰ࡾࠤ⋟").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1ll111_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧ⋠")))
    bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"ࠦࠧ⋡")
    bstack1lllll1l111l_opy_(report)
    if not passed:
        try:
            bstack1l111l1111_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1ll111_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡨࡪࡺࡥࡳ࡯࡬ࡲࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫ࠠࡳࡧࡤࡷࡴࡴ࠺ࠡࡽ࠳ࢁࠧ⋢").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1l111l1111_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack1ll111_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣ⋣")))
        bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"ࠢࠣ⋤")
        if not passed:
            try:
                bstack1l111l1111_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1ll111_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡩࡥ࡮ࡲࡵࡳࡧࠣࡶࡪࡧࡳࡰࡰ࠽ࠤࢀ࠶ࡽࠣ⋥").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack1l111l1111_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡯࡮ࡧࡱࠥ࠰ࠥࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡪࡡࡵࡣࠥ࠾ࠥ࠭⋦")
                    + json.dumps(bstack1ll111_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠤࠦ⋧"))
                    + bstack1ll111_opy_ (u"ࠦࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࠢ⋨")
                )
            else:
                item._driver.execute_script(
                    bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨ࡬ࡦࡸࡨࡰࠧࡀࠠࠣࡧࡵࡶࡴࡸࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡧࡥࡹࡧࠢ࠻ࠢࠪ⋩")
                    + json.dumps(str(bstack1l111l1111_opy_))
                    + bstack1ll111_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡾࠤ⋪")
                )
        except Exception as e:
            summary.append(bstack1ll111_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡧ࡮࡯ࡱࡷࡥࡹ࡫࠺ࠡࡽ࠳ࢁࠧ⋫").format(e))
def bstack1lll1l11ll11_opy_(test_name, error_message):
    try:
        bstack1lll1l11lll1_opy_ = []
        bstack1lll1l1l_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨ⋬"), bstack1ll111_opy_ (u"ࠩ࠳ࠫ⋭"))
        bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨ⋮"): test_name, bstack1ll111_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ⋯"): error_message, bstack1ll111_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ⋰"): bstack1lll1l1l_opy_}
        bstack1lll1l1l1ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"࠭ࡰࡸࡡࡳࡽࡹ࡫ࡳࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫ⋱"))
        if os.path.exists(bstack1lll1l1l1ll1_opy_):
            with open(bstack1lll1l1l1ll1_opy_) as f:
                bstack1lll1l11lll1_opy_ = json.load(f)
        bstack1lll1l11lll1_opy_.append(bstack1l1ll11l11_opy_)
        with open(bstack1lll1l1l1ll1_opy_, bstack1ll111_opy_ (u"ࠧࡸࠩ⋲")) as f:
            json.dump(bstack1lll1l11lll1_opy_, f)
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡪࡸࡳࡪࡵࡷ࡭ࡳ࡭ࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡵࡿࡴࡦࡵࡷࠤࡪࡸࡲࡰࡴࡶ࠾ࠥ࠭⋳") + str(e))
def bstack1lll1l1llll1_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack1ll111_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣ⋴"), bstack1ll111_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧ⋵")]:
        return
    if (str(skipSessionName).lower() != bstack1ll111_opy_ (u"ࠫࡹࡸࡵࡦࠩ⋶")):
        bstack1l1lllll1_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1ll111_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢ⋷")))
    bstack1l111l1111_opy_ = bstack1ll111_opy_ (u"ࠨࠢ⋸")
    bstack1lllll1l111l_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack1l111l1111_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1ll111_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡵࡩࡦࡹ࡯࡯࠼ࠣࡿ࠵ࢃࠢ⋹").format(e)
                )
        try:
            if passed:
                bstack1l1l1ll1l1_opy_(getattr(item, bstack1ll111_opy_ (u"ࠨࡡࡳࡥ࡬࡫ࠧ⋺"), None), bstack1ll111_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ⋻"))
            else:
                error_message = bstack1ll111_opy_ (u"ࠪࠫ⋼")
                if bstack1l111l1111_opy_:
                    bstack11llll1l1l_opy_(item._page, str(bstack1l111l1111_opy_), bstack1ll111_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥ⋽"))
                    bstack1l1l1ll1l1_opy_(getattr(item, bstack1ll111_opy_ (u"ࠬࡥࡰࡢࡩࡨࠫ⋾"), None), bstack1ll111_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ⋿"), str(bstack1l111l1111_opy_))
                    error_message = str(bstack1l111l1111_opy_)
                else:
                    bstack1l1l1ll1l1_opy_(getattr(item, bstack1ll111_opy_ (u"ࠧࡠࡲࡤ࡫ࡪ࠭⌀"), None), bstack1ll111_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ⌁"))
                bstack1lll1l11ll11_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack1ll111_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡶࡲࡧࡥࡹ࡫ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳ࠻ࠢࡾ࠴ࢂࠨ⌂").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack1ll111_opy_ (u"ࠥ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ⌃"), default=bstack1ll111_opy_ (u"ࠦࡋࡧ࡬ࡴࡧࠥ⌄"), help=bstack1ll111_opy_ (u"ࠧࡇࡵࡵࡱࡰࡥࡹ࡯ࡣࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠦ⌅"))
    parser.addoption(bstack1ll111_opy_ (u"ࠨ࠭࠮ࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ⌆"), default=bstack1ll111_opy_ (u"ࠢࡇࡣ࡯ࡷࡪࠨ⌇"), help=bstack1ll111_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵ࡫ࡦࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠢ⌈"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1ll111_opy_ (u"ࠤ࠰࠱ࡩࡸࡩࡷࡧࡵࠦ⌉"), action=bstack1ll111_opy_ (u"ࠥࡷࡹࡵࡲࡦࠤ⌊"), default=bstack1ll111_opy_ (u"ࠦࡨ࡮ࡲࡰ࡯ࡨࠦ⌋"),
                         help=bstack1ll111_opy_ (u"ࠧࡊࡲࡪࡸࡨࡶࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶࠦ⌌"))
def bstack111l1ll1l1_opy_(log):
    if not (log[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⌍")] and log[bstack1ll111_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ⌎")].strip()):
        return
    active = bstack111ll11lll_opy_()
    log = {
        bstack1ll111_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ⌏"): log[bstack1ll111_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ⌐")],
        bstack1ll111_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭⌑"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"ࠫ࡟࠭⌒"),
        bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⌓"): log[bstack1ll111_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ⌔")],
    }
    if active:
        if active[bstack1ll111_opy_ (u"ࠧࡵࡻࡳࡩࠬ⌕")] == bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰ࠭⌖"):
            log[bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⌗")] = active[bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⌘")]
        elif active[bstack1ll111_opy_ (u"ࠫࡹࡿࡰࡦࠩ⌙")] == bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࠪ⌚"):
            log[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⌛")] = active[bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⌜")]
    bstack111l1l111_opy_.bstack11l1l1l111_opy_([log])
def bstack111ll11lll_opy_():
    if len(store[bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ⌝")]) > 0 and store[bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⌞")][-1]:
        return {
            bstack1ll111_opy_ (u"ࠪࡸࡾࡶࡥࠨ⌟"): bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⌠"),
            bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⌡"): store[bstack1ll111_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ⌢")][-1]
        }
    if store.get(bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⌣"), None):
        return {
            bstack1ll111_opy_ (u"ࠨࡶࡼࡴࡪ࠭⌤"): bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࠧ⌥"),
            bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⌦"): store[bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⌧")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.INIT_TEST, bstack1lll1l1llll_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.INIT_TEST, bstack1lll1l1llll_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._1lll1l1ll111_opy_ = True
        bstack1l11ll11l1_opy_ = bstack1llll111_opy_.bstack11ll11lll1_opy_(bstack111lllll1l1_opy_(item.own_markers))
        if not cli.bstack1ll1l1ll111_opy_(bstack1lll111ll1l_opy_):
            item._a11y_test_case = bstack1l11ll11l1_opy_
            if bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ⌨"), None):
                driver = getattr(item, bstack1ll111_opy_ (u"࠭࡟ࡥࡴ࡬ࡺࡪࡸࠧ〈"), None)
                item._a11y_started = bstack1llll111_opy_.bstack1111lll1l_opy_(driver, bstack1l11ll11l1_opy_)
        if not bstack111l1l111_opy_.on() or bstack1lll1l111l1l_opy_ != bstack1ll111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ〉"):
            return
        global current_test_uuid #, bstack111l1ll111_opy_
        bstack111l1l1l11_opy_ = {
            bstack1ll111_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭⌫"): uuid4().__str__(),
            bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⌬"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"ࠪ࡞ࠬ⌭")
        }
        current_test_uuid = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫࡺࡻࡩࡥࠩ⌮")]
        store[bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⌯")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⌰")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _1111ll11ll_opy_[item.nodeid] = {**_1111ll11ll_opy_[item.nodeid], **bstack111l1l1l11_opy_}
        bstack1lll1l1l11ll_opy_(item, _1111ll11ll_opy_[item.nodeid], bstack1ll111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ⌱"))
    except Exception as err:
        print(bstack1ll111_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡳࡷࡱࡸࡪࡹࡴࡠࡥࡤࡰࡱࡀࠠࡼࡿࠪ⌲"), str(err))
def pytest_runtest_setup(item):
    store[bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⌳")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.BEFORE_EACH, bstack1lll1l1llll_opy_.PRE, item, bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⌴"))
    if bstack11ll1lll1l_opy_.bstack1111l1lll1l_opy_():
            bstack1lll1l11ll1l_opy_ = bstack1ll111_opy_ (u"ࠦࡘࡱࡩࡱࡲ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡦࡹࠠࡵࡪࡨࠤࡦࡨ࡯ࡳࡶࠣࡦࡺ࡯࡬ࡥࠢࡩ࡭ࡱ࡫ࠠࡦࡺ࡬ࡷࡹࡹ࠮ࠣ⌵")
            logger.error(bstack1lll1l11ll1l_opy_)
            bstack111l1l1l11_opy_ = {
                bstack1ll111_opy_ (u"ࠬࡻࡵࡪࡦࠪ⌶"): uuid4().__str__(),
                bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⌷"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"࡛ࠧࠩ⌸"),
                bstack1ll111_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⌹"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"ࠩ࡝ࠫ⌺"),
                bstack1ll111_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⌻"): bstack1ll111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⌼"),
                bstack1ll111_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬ⌽"): bstack1lll1l11ll1l_opy_,
                bstack1ll111_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⌾"): [],
                bstack1ll111_opy_ (u"ࠧࡧ࡫ࡻࡸࡺࡸࡥࡴࠩ⌿"): []
            }
            bstack1lll1l1l11ll_opy_(item, bstack111l1l1l11_opy_, bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕ࡮࡭ࡵࡶࡥࡥࠩ⍀"))
            pytest.skip(bstack1lll1l11ll1l_opy_)
            return # skip all existing operations
    global bstack1lll1l11l1l1_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack111l1lll111_opy_():
        atexit.register(bstack11l1111ll_opy_)
        if not bstack1lll1l11l1l1_opy_:
            try:
                bstack1lll1l111l11_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack111ll1l1lll_opy_():
                    bstack1lll1l111l11_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack1lll1l111l11_opy_:
                    signal.signal(s, bstack1lll1l1ll1l1_opy_)
                bstack1lll1l11l1l1_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack1ll111_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡷ࡫ࡧࡪࡵࡷࡩࡷࠦࡳࡪࡩࡱࡥࡱࠦࡨࡢࡰࡧࡰࡪࡸࡳ࠻ࠢࠥ⍁") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack1lllll1l11l1_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack1ll111_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ⍂")
    try:
        if not bstack111l1l111_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack111l1l1l11_opy_ = {
            bstack1ll111_opy_ (u"ࠫࡺࡻࡩࡥࠩ⍃"): uuid,
            bstack1ll111_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ⍄"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"࡚࠭ࠨ⍅"),
            bstack1ll111_opy_ (u"ࠧࡵࡻࡳࡩࠬ⍆"): bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰ࠭⍇"),
            bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ⍈"): bstack1ll111_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ⍉"),
            bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ⍊"): bstack1ll111_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ⍋")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack1ll111_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ⍌")] = item
        store[bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ⍍")] = [uuid]
        if not _1111ll11ll_opy_.get(item.nodeid, None):
            _1111ll11ll_opy_[item.nodeid] = {bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⍎"): [], bstack1ll111_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⍏"): []}
        _1111ll11ll_opy_[item.nodeid][bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⍐")].append(bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫࡺࡻࡩࡥࠩ⍑")])
        _1111ll11ll_opy_[item.nodeid + bstack1ll111_opy_ (u"ࠬ࠳ࡳࡦࡶࡸࡴࠬ⍒")] = bstack111l1l1l11_opy_
        bstack1lll1l11llll_opy_(item, bstack111l1l1l11_opy_, bstack1ll111_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ⍓"))
    except Exception as err:
        print(bstack1ll111_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡲࡶࡰࡷࡩࡸࡺ࡟ࡴࡧࡷࡹࡵࡀࠠࡼࡿࠪ⍔"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.AFTER_EACH, bstack1lll1l1llll_opy_.PRE, item, bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⍕"))
        return # skip all existing operations
    try:
        global bstack1l1111l111_opy_
        bstack1lll1l1l_opy_ = 0
        if bstack1l1lll1l11_opy_ is True:
            bstack1lll1l1l_opy_ = int(os.environ.get(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ⍖")))
        if bstack11lllll11_opy_.bstack1l11111l_opy_() == bstack1ll111_opy_ (u"ࠥࡸࡷࡻࡥࠣ⍗"):
            if bstack11lllll11_opy_.bstack1ll1l1lll1_opy_() == bstack1ll111_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨ⍘"):
                bstack1lll1l111lll_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ⍙"), None)
                bstack1l11l1l1l1_opy_ = bstack1lll1l111lll_opy_ + bstack1ll111_opy_ (u"ࠨ࠭ࡵࡧࡶࡸࡨࡧࡳࡦࠤ⍚")
                driver = getattr(item, bstack1ll111_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ⍛"), None)
                bstack11lllll1l1_opy_ = getattr(item, bstack1ll111_opy_ (u"ࠨࡰࡤࡱࡪ࠭⍜"), None)
                bstack1ll11l11l_opy_ = getattr(item, bstack1ll111_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⍝"), None)
                PercySDK.screenshot(driver, bstack1l11l1l1l1_opy_, bstack11lllll1l1_opy_=bstack11lllll1l1_opy_, bstack1ll11l11l_opy_=bstack1ll11l11l_opy_, bstack1lllll111_opy_=bstack1lll1l1l_opy_)
        if not cli.bstack1ll1l1ll111_opy_(bstack1lll111ll1l_opy_):
            if getattr(item, bstack1ll111_opy_ (u"ࠪࡣࡦ࠷࠱ࡺࡡࡶࡸࡦࡸࡴࡦࡦࠪ⍞"), False):
                bstack1lll1111ll_opy_.bstack11lllllll_opy_(getattr(item, bstack1ll111_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ⍟"), None), bstack1l1111l111_opy_, logger, item)
        if not bstack111l1l111_opy_.on():
            return
        bstack111l1l1l11_opy_ = {
            bstack1ll111_opy_ (u"ࠬࡻࡵࡪࡦࠪ⍠"): uuid4().__str__(),
            bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⍡"): bstack1111l1lll1_opy_().isoformat() + bstack1ll111_opy_ (u"࡛ࠧࠩ⍢"),
            bstack1ll111_opy_ (u"ࠨࡶࡼࡴࡪ࠭⍣"): bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ⍤"),
            bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭⍥"): bstack1ll111_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ⍦"),
            bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨ⍧"): bstack1ll111_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ⍨")
        }
        _1111ll11ll_opy_[item.nodeid + bstack1ll111_opy_ (u"ࠧ࠮ࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⍩")] = bstack111l1l1l11_opy_
        bstack1lll1l11llll_opy_(item, bstack111l1l1l11_opy_, bstack1ll111_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⍪"))
    except Exception as err:
        print(bstack1ll111_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱ࠾ࠥࢁࡽࠨ⍫"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack1lllll1l1111_opy_(fixturedef.argname):
        store[bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡲࡵࡤࡶ࡮ࡨࡣ࡮ࡺࡥ࡮ࠩ⍬")] = request.node
    elif bstack1lllll1ll1l1_opy_(fixturedef.argname):
        store[bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ⍭")] = request.node
    if not bstack111l1l111_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.SETUP_FIXTURE, bstack1lll1l1llll_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.SETUP_FIXTURE, bstack1lll1l1llll_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.SETUP_FIXTURE, bstack1lll1l1llll_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.SETUP_FIXTURE, bstack1lll1l1llll_opy_.POST, fixturedef, request, outcome)
        return # skip all existing operations
    try:
        fixture = {
            bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⍮"): fixturedef.argname,
            bstack1ll111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⍯"): bstack111lll1111l_opy_(outcome),
            bstack1ll111_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ⍰"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⍱")]
        if not _1111ll11ll_opy_.get(current_test_item.nodeid, None):
            _1111ll11ll_opy_[current_test_item.nodeid] = {bstack1ll111_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⍲"): []}
        _1111ll11ll_opy_[current_test_item.nodeid][bstack1ll111_opy_ (u"ࠪࡪ࡮ࡾࡴࡶࡴࡨࡷࠬ⍳")].append(fixture)
    except Exception as err:
        logger.debug(bstack1ll111_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡸ࡫ࡴࡶࡲ࠽ࠤࢀࢃࠧ⍴"), str(err))
if bstack11l11l11l_opy_() and bstack111l1l111_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.STEP, bstack1lll1l1llll_opy_.PRE, request, step)
            return
        try:
            _1111ll11ll_opy_[request.node.nodeid][bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⍵")].bstack1l11l111l1_opy_(id(step))
        except Exception as err:
            print(bstack1ll111_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶ࠺ࠡࡽࢀࠫ⍶"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.STEP, bstack1lll1l1llll_opy_.POST, request, step, exception)
            return
        try:
            _1111ll11ll_opy_[request.node.nodeid][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⍷")].bstack111l1l1lll_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack1ll111_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡸࡺࡥࡱࡡࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠬ⍸"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.STEP, bstack1lll1l1llll_opy_.POST, request, step)
            return
        try:
            bstack111ll11ll1_opy_: bstack111ll1l1l1_opy_ = _1111ll11ll_opy_[request.node.nodeid][bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ⍹")]
            bstack111ll11ll1_opy_.bstack111l1l1lll_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack1ll111_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡳࡵࡧࡳࡣࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠧ⍺"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack1lll1l111l1l_opy_
        try:
            if not bstack111l1l111_opy_.on() or bstack1lll1l111l1l_opy_ != bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨ⍻"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.TEST, bstack1lll1l1llll_opy_.PRE, request, feature, scenario)
                return
            driver = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫ⍼"), None)
            if not _1111ll11ll_opy_.get(request.node.nodeid, None):
                _1111ll11ll_opy_[request.node.nodeid] = {}
            bstack111ll11ll1_opy_ = bstack111ll1l1l1_opy_.bstack1llll1l1llll_opy_(
                scenario, feature, request.node,
                name=bstack1lllll1ll1ll_opy_(request.node, scenario),
                started_at=bstack11ll1l111_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack1ll111_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠳ࡣࡶࡥࡸࡱࡧ࡫ࡲࠨ⍽"),
                tags=bstack1lllll1l1l11_opy_(feature, scenario),
                bstack111ll1ll11_opy_=bstack111l1l111_opy_.bstack111l1lll1l_opy_(driver) if driver and driver.session_id else {}
            )
            _1111ll11ll_opy_[request.node.nodeid][bstack1ll111_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⍾")] = bstack111ll11ll1_opy_
            bstack1lll1l1l1l1l_opy_(bstack111ll11ll1_opy_.uuid)
            bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⍿"), bstack111ll11ll1_opy_)
        except Exception as err:
            print(bstack1ll111_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵ࠺ࠡࡽࢀࠫ⎀"), str(err))
def bstack1lll1l1l1111_opy_(bstack111l1ll11l_opy_):
    if bstack111l1ll11l_opy_ in store[bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ⎁")]:
        store[bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⎂")].remove(bstack111l1ll11l_opy_)
def bstack1lll1l1l1l1l_opy_(test_uuid):
    store[bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⎃")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack111l1l111_opy_.bstack1lll1llllll1_opy_
def bstack1lll1l111ll1_opy_(item, call, report):
    logger.debug(bstack1ll111_opy_ (u"࠭ࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡶࡸࡦࡸࡴࠨ⎄"))
    global bstack1lll1l111l1l_opy_
    bstack11ll1l1lll_opy_ = bstack11ll1l111_opy_()
    if hasattr(report, bstack1ll111_opy_ (u"ࠧࡴࡶࡲࡴࠬ⎅")):
        bstack11ll1l1lll_opy_ = bstack11l11l111l1_opy_(report.stop)
    elif hasattr(report, bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡷࡺࠧ⎆")):
        bstack11ll1l1lll_opy_ = bstack11l11l111l1_opy_(report.start)
    try:
        if getattr(report, bstack1ll111_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⎇"), bstack1ll111_opy_ (u"ࠪࠫ⎈")) == bstack1ll111_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⎉"):
            logger.debug(bstack1ll111_opy_ (u"ࠬ࡮ࡡ࡯ࡦ࡯ࡩࡤࡵ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡵࡷࡥࡹ࡫ࠠ࠮ࠢࡾࢁ࠱ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠢ࠰ࠤࢀࢃࠧ⎊").format(getattr(report, bstack1ll111_opy_ (u"࠭ࡷࡩࡧࡱࠫ⎋"), bstack1ll111_opy_ (u"ࠧࠨ⎌")).__str__(), bstack1lll1l111l1l_opy_))
            if bstack1lll1l111l1l_opy_ == bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⎍"):
                _1111ll11ll_opy_[item.nodeid][bstack1ll111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⎎")] = bstack11ll1l1lll_opy_
                bstack1lll1l1l11ll_opy_(item, _1111ll11ll_opy_[item.nodeid], bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⎏"), report, call)
                store[bstack1ll111_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⎐")] = None
            elif bstack1lll1l111l1l_opy_ == bstack1ll111_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤ⎑"):
                bstack111ll11ll1_opy_ = _1111ll11ll_opy_[item.nodeid][bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⎒")]
                bstack111ll11ll1_opy_.set(hooks=_1111ll11ll_opy_[item.nodeid].get(bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⎓"), []))
                exception, bstack111ll11l1l_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack111ll11l1l_opy_ = [call.excinfo.exconly(), getattr(report, bstack1ll111_opy_ (u"ࠨ࡮ࡲࡲ࡬ࡸࡥࡱࡴࡷࡩࡽࡺࠧ⎔"), bstack1ll111_opy_ (u"ࠩࠪ⎕"))]
                bstack111ll11ll1_opy_.stop(time=bstack11ll1l1lll_opy_, result=Result(result=getattr(report, bstack1ll111_opy_ (u"ࠪࡳࡺࡺࡣࡰ࡯ࡨࠫ⎖"), bstack1ll111_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ⎗")), exception=exception, bstack111ll11l1l_opy_=bstack111ll11l1l_opy_))
                bstack111l1l111_opy_.bstack111ll1111l_opy_(bstack1ll111_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⎘"), _1111ll11ll_opy_[item.nodeid][bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⎙")])
        elif getattr(report, bstack1ll111_opy_ (u"ࠧࡸࡪࡨࡲࠬ⎚"), bstack1ll111_opy_ (u"ࠨࠩ⎛")) in [bstack1ll111_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⎜"), bstack1ll111_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ⎝")]:
            logger.debug(bstack1ll111_opy_ (u"ࠫ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡴࡶࡤࡸࡪࠦ࠭ࠡࡽࢀ࠰ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࠯ࠣࡿࢂ࠭⎞").format(getattr(report, bstack1ll111_opy_ (u"ࠬࡽࡨࡦࡰࠪ⎟"), bstack1ll111_opy_ (u"࠭ࠧ⎠")).__str__(), bstack1lll1l111l1l_opy_))
            bstack111ll111ll_opy_ = item.nodeid + bstack1ll111_opy_ (u"ࠧ࠮ࠩ⎡") + getattr(report, bstack1ll111_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⎢"), bstack1ll111_opy_ (u"ࠩࠪ⎣"))
            if getattr(report, bstack1ll111_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ⎤"), False):
                hook_type = bstack1ll111_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ⎥") if getattr(report, bstack1ll111_opy_ (u"ࠬࡽࡨࡦࡰࠪ⎦"), bstack1ll111_opy_ (u"࠭ࠧ⎧")) == bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⎨") else bstack1ll111_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬ⎩")
                _1111ll11ll_opy_[bstack111ll111ll_opy_] = {
                    bstack1ll111_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⎪"): uuid4().__str__(),
                    bstack1ll111_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⎫"): bstack11ll1l1lll_opy_,
                    bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ⎬"): hook_type
                }
            _1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⎭")] = bstack11ll1l1lll_opy_
            bstack1lll1l1l1111_opy_(_1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⎮")])
            bstack1lll1l11llll_opy_(item, _1111ll11ll_opy_[bstack111ll111ll_opy_], bstack1ll111_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ⎯"), report, call)
            if getattr(report, bstack1ll111_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⎰"), bstack1ll111_opy_ (u"ࠩࠪ⎱")) == bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩ⎲"):
                if getattr(report, bstack1ll111_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬ⎳"), bstack1ll111_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⎴")) == bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⎵"):
                    bstack111l1l1l11_opy_ = {
                        bstack1ll111_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⎶"): uuid4().__str__(),
                        bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬ⎷"): bstack11ll1l111_opy_(),
                        bstack1ll111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⎸"): bstack11ll1l111_opy_()
                    }
                    _1111ll11ll_opy_[item.nodeid] = {**_1111ll11ll_opy_[item.nodeid], **bstack111l1l1l11_opy_}
                    bstack1lll1l1l11ll_opy_(item, _1111ll11ll_opy_[item.nodeid], bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ⎹"))
                    bstack1lll1l1l11ll_opy_(item, _1111ll11ll_opy_[item.nodeid], bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⎺"), report, call)
    except Exception as err:
        print(bstack1ll111_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡼࡿࠪ⎻"), str(err))
def bstack1lll1l1ll1ll_opy_(test, bstack111l1l1l11_opy_, result=None, call=None, bstack1lll1lll11_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111ll11ll1_opy_ = {
        bstack1ll111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⎼"): bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⎽")],
        bstack1ll111_opy_ (u"ࠨࡶࡼࡴࡪ࠭⎾"): bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࠧ⎿"),
        bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨ⏀"): test.name,
        bstack1ll111_opy_ (u"ࠫࡧࡵࡤࡺࠩ⏁"): {
            bstack1ll111_opy_ (u"ࠬࡲࡡ࡯ࡩࠪ⏂"): bstack1ll111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭⏃"),
            bstack1ll111_opy_ (u"ࠧࡤࡱࡧࡩࠬ⏄"): inspect.getsource(test.obj)
        },
        bstack1ll111_opy_ (u"ࠨ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ⏅"): test.name,
        bstack1ll111_opy_ (u"ࠩࡶࡧࡴࡶࡥࠨ⏆"): test.name,
        bstack1ll111_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ⏇"): bstack1llll1111_opy_.bstack111l111l11_opy_(test),
        bstack1ll111_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ⏈"): file_path,
        bstack1ll111_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧ⏉"): file_path,
        bstack1ll111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⏊"): bstack1ll111_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⏋"),
        bstack1ll111_opy_ (u"ࠨࡸࡦࡣ࡫࡯࡬ࡦࡲࡤࡸ࡭࠭⏌"): file_path,
        bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭⏍"): bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ⏎")],
        bstack1ll111_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ⏏"): bstack1ll111_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ⏐"),
        bstack1ll111_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡘࡥࡳࡷࡱࡔࡦࡸࡡ࡮ࠩ⏑"): {
            bstack1ll111_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥ࡮ࡢ࡯ࡨࠫ⏒"): test.nodeid
        },
        bstack1ll111_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭⏓"): bstack111lllll1l1_opy_(test.own_markers)
    }
    if bstack1lll1lll11_opy_ in [bstack1ll111_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪ⏔"), bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ⏕")]:
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠫࡲ࡫ࡴࡢࠩ⏖")] = {
            bstack1ll111_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧ⏗"): bstack111l1l1l11_opy_.get(bstack1ll111_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨ⏘"), [])
        }
    if bstack1lll1lll11_opy_ == bstack1ll111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨ⏙"):
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⏚")] = bstack1ll111_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪ⏛")
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⏜")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⏝")]
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ⏞")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ⏟")]
    if result:
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⏠")] = result.outcome
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ⏡")] = result.duration * 1000
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⏢")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⏣")]
        if result.failed:
            bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ⏤")] = bstack111l1l111_opy_.bstack1llllll1l11_opy_(call.excinfo.typename)
            bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭⏥")] = bstack111l1l111_opy_.bstack1llll111l1l1_opy_(call.excinfo, result)
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⏦")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⏧")]
    if outcome:
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⏨")] = bstack111lll1111l_opy_(outcome)
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⏩")] = 0
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⏪")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⏫")]
        if bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⏬")] == bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⏭"):
            bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭⏮")] = bstack1ll111_opy_ (u"ࠨࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠩ⏯")  # bstack1lll1l1l11l1_opy_
            bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ⏰")] = [{bstack1ll111_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭⏱"): [bstack1ll111_opy_ (u"ࠫࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠨ⏲")]}]
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⏳")] = bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⏴")]
    return bstack111ll11ll1_opy_
def bstack1lll1l1l1l11_opy_(test, bstack111l1111l1_opy_, bstack1lll1lll11_opy_, result, call, outcome, bstack1lll1l11l11l_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⏵")]
    hook_name = bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⏶")]
    hook_data = {
        bstack1ll111_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⏷"): bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⏸")],
        bstack1ll111_opy_ (u"ࠫࡹࡿࡰࡦࠩ⏹"): bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⏺"),
        bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⏻"): bstack1ll111_opy_ (u"ࠧࡼࡿࠪ⏼").format(bstack1lllll1l11ll_opy_(hook_name)),
        bstack1ll111_opy_ (u"ࠨࡤࡲࡨࡾ࠭⏽"): {
            bstack1ll111_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ⏾"): bstack1ll111_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⏿"),
            bstack1ll111_opy_ (u"ࠫࡨࡵࡤࡦࠩ␀"): None
        },
        bstack1ll111_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫ␁"): test.name,
        bstack1ll111_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭␂"): bstack1llll1111_opy_.bstack111l111l11_opy_(test, hook_name),
        bstack1ll111_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ␃"): file_path,
        bstack1ll111_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ␄"): file_path,
        bstack1ll111_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ␅"): bstack1ll111_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ␆"),
        bstack1ll111_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩ␇"): file_path,
        bstack1ll111_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ␈"): bstack111l1111l1_opy_[bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ␉")],
        bstack1ll111_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ␊"): bstack1ll111_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪ␋") if bstack1lll1l111l1l_opy_ == bstack1ll111_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭␌") else bstack1ll111_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶࠪ␍"),
        bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ␎"): hook_type
    }
    bstack1l1llll1ll1_opy_ = bstack1111l1llll_opy_(_1111ll11ll_opy_.get(test.nodeid, None))
    if bstack1l1llll1ll1_opy_:
        hook_data[bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡪࡦࠪ␏")] = bstack1l1llll1ll1_opy_
    if result:
        hook_data[bstack1ll111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭␐")] = result.outcome
        hook_data[bstack1ll111_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨ␑")] = result.duration * 1000
        hook_data[bstack1ll111_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭␒")] = bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ␓")]
        if result.failed:
            hook_data[bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ␔")] = bstack111l1l111_opy_.bstack1llllll1l11_opy_(call.excinfo.typename)
            hook_data[bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ␕")] = bstack111l1l111_opy_.bstack1llll111l1l1_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack1ll111_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ␖")] = bstack111lll1111l_opy_(outcome)
        hook_data[bstack1ll111_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧ␗")] = 100
        hook_data[bstack1ll111_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ␘")] = bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭␙")]
        if hook_data[bstack1ll111_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ␚")] == bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ␛"):
            hook_data[bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ␜")] = bstack1ll111_opy_ (u"࡛ࠬ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷ࠭␝")  # bstack1lll1l1l11l1_opy_
            hook_data[bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧ␞")] = [{bstack1ll111_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪ␟"): [bstack1ll111_opy_ (u"ࠨࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠬ␠")]}]
    if bstack1lll1l11l11l_opy_:
        hook_data[bstack1ll111_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ␡")] = bstack1lll1l11l11l_opy_.result
        hook_data[bstack1ll111_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫ␢")] = bstack111ll1lll1l_opy_(bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ␣")], bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ␤")])
        hook_data[bstack1ll111_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ␥")] = bstack111l1111l1_opy_[bstack1ll111_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬ␦")]
        if hook_data[bstack1ll111_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ␧")] == bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ␨"):
            hook_data[bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩ␩")] = bstack111l1l111_opy_.bstack1llllll1l11_opy_(bstack1lll1l11l11l_opy_.exception_type)
            hook_data[bstack1ll111_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬ␪")] = [{bstack1ll111_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨ␫"): bstack111ll11l11l_opy_(bstack1lll1l11l11l_opy_.exception)}]
    return hook_data
def bstack1lll1l1l11ll_opy_(test, bstack111l1l1l11_opy_, bstack1lll1lll11_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack1ll111_opy_ (u"࠭ࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡥࡷࡧࡱࡸ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶࡨࡷࡹࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠥ࠳ࠠࡼࡿࠪ␬").format(bstack1lll1lll11_opy_))
    bstack111ll11ll1_opy_ = bstack1lll1l1ll1ll_opy_(test, bstack111l1l1l11_opy_, result, call, bstack1lll1lll11_opy_, outcome)
    driver = getattr(test, bstack1ll111_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ␭"), None)
    if bstack1lll1lll11_opy_ == bstack1ll111_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ␮") and driver:
        bstack111ll11ll1_opy_[bstack1ll111_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠨ␯")] = bstack111l1l111_opy_.bstack111l1lll1l_opy_(driver)
    if bstack1lll1lll11_opy_ == bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ␰"):
        bstack1lll1lll11_opy_ = bstack1ll111_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭␱")
    bstack111l111l1l_opy_ = {
        bstack1ll111_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ␲"): bstack1lll1lll11_opy_,
        bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ␳"): bstack111ll11ll1_opy_
    }
    bstack111l1l111_opy_.bstack1lll111l11_opy_(bstack111l111l1l_opy_)
    if bstack1lll1lll11_opy_ == bstack1ll111_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ␴"):
        threading.current_thread().bstackTestMeta = {bstack1ll111_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ␵"): bstack1ll111_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ␶")}
    elif bstack1lll1lll11_opy_ == bstack1ll111_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ␷"):
        threading.current_thread().bstackTestMeta = {bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ␸"): getattr(result, bstack1ll111_opy_ (u"ࠬࡵࡵࡵࡥࡲࡱࡪ࠭␹"), bstack1ll111_opy_ (u"࠭ࠧ␺"))}
def bstack1lll1l11llll_opy_(test, bstack111l1l1l11_opy_, bstack1lll1lll11_opy_, result=None, call=None, outcome=None, bstack1lll1l11l11l_opy_=None):
    logger.debug(bstack1ll111_opy_ (u"ࠧࡴࡧࡱࡨࡤ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡦࡸࡨࡲࡹࡀࠠࡂࡶࡷࡩࡲࡶࡴࡪࡰࡪࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢ࡫ࡳࡴࡱࠠࡥࡣࡷࡥ࠱ࠦࡥࡷࡧࡱࡸ࡙ࡿࡰࡦࠢ࠰ࠤࢀࢃࠧ␻").format(bstack1lll1lll11_opy_))
    hook_data = bstack1lll1l1l1l11_opy_(test, bstack111l1l1l11_opy_, bstack1lll1lll11_opy_, result, call, outcome, bstack1lll1l11l11l_opy_)
    bstack111l111l1l_opy_ = {
        bstack1ll111_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ␼"): bstack1lll1lll11_opy_,
        bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫ␽"): hook_data
    }
    bstack111l1l111_opy_.bstack1lll111l11_opy_(bstack111l111l1l_opy_)
def bstack1111l1llll_opy_(bstack111l1l1l11_opy_):
    if not bstack111l1l1l11_opy_:
        return None
    if bstack111l1l1l11_opy_.get(bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭␾"), None):
        return getattr(bstack111l1l1l11_opy_[bstack1ll111_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ␿")], bstack1ll111_opy_ (u"ࠬࡻࡵࡪࡦࠪ⑀"), None)
    return bstack111l1l1l11_opy_.get(bstack1ll111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⑁"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.LOG, bstack1lll1l1llll_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_.LOG, bstack1lll1l1llll_opy_.POST, request, caplog)
        return # skip all existing operations
    try:
        if not bstack111l1l111_opy_.on():
            return
        places = [bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭⑂"), bstack1ll111_opy_ (u"ࠨࡥࡤࡰࡱ࠭⑃"), bstack1ll111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ⑄")]
        logs = []
        for bstack1lll1ll11111_opy_ in places:
            records = caplog.get_records(bstack1lll1ll11111_opy_)
            bstack1lll1l11l111_opy_ = bstack1ll111_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⑅") if bstack1lll1ll11111_opy_ == bstack1ll111_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⑆") else bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ⑇")
            bstack1lll1l1lllll_opy_ = request.node.nodeid + (bstack1ll111_opy_ (u"࠭ࠧ⑈") if bstack1lll1ll11111_opy_ == bstack1ll111_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⑉") else bstack1ll111_opy_ (u"ࠨ࠯ࠪ⑊") + bstack1lll1ll11111_opy_)
            test_uuid = bstack1111l1llll_opy_(_1111ll11ll_opy_.get(bstack1lll1l1lllll_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack111llllll11_opy_(record.message):
                    continue
                logs.append({
                    bstack1ll111_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ⑋"): bstack11l1111ll11_opy_(record.created).isoformat() + bstack1ll111_opy_ (u"ࠪ࡞ࠬ⑌"),
                    bstack1ll111_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ⑍"): record.levelname,
                    bstack1ll111_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⑎"): record.message,
                    bstack1lll1l11l111_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack111l1l111_opy_.bstack11l1l1l111_opy_(logs)
    except Exception as err:
        print(bstack1ll111_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡥࡤࡱࡱࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡀࠠࡼࡿࠪ⑏"), str(err))
def bstack1lll1l1111_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1l1l1111_opy_
    bstack1l1111l1l1_opy_ = bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ⑐"), None) and bstack11111l1l1_opy_(
            threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ⑑"), None)
    bstack1l11111l1l_opy_ = getattr(driver, bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ⑒"), None) != None and getattr(driver, bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ⑓"), None) == True
    if sequence == bstack1ll111_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫ⑔") and driver != None:
      if not bstack1l1l1111_opy_ and bstack1l1l11l1l1l_opy_() and bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ⑕") in CONFIG and CONFIG[bstack1ll111_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭⑖")] == True and bstack111llll1ll_opy_.bstack11l1l1lll1_opy_(driver_command) and (bstack1l11111l1l_opy_ or bstack1l1111l1l1_opy_) and not bstack1l1llll11_opy_(args):
        try:
          bstack1l1l1111_opy_ = True
          logger.debug(bstack1ll111_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡻࡾࠩ⑗").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack1ll111_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡹࡣࡢࡰࠣࡿࢂ࠭⑘").format(str(err)))
        bstack1l1l1111_opy_ = False
    if sequence == bstack1ll111_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ⑙"):
        if driver_command == bstack1ll111_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠧ⑚"):
            bstack111l1l111_opy_.bstack1lll1lllll_opy_({
                bstack1ll111_opy_ (u"ࠫ࡮ࡳࡡࡨࡧࠪ⑛"): response[bstack1ll111_opy_ (u"ࠬࡼࡡ࡭ࡷࡨࠫ⑜")],
                bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⑝"): store[bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⑞")]
            })
def bstack11l1111ll_opy_():
    global bstack1ll111ll1l_opy_
    bstack1llll1ll1l_opy_.bstack1l1ll11ll_opy_()
    logging.shutdown()
    bstack111l1l111_opy_.bstack111l11l1ll_opy_()
    for driver in bstack1ll111ll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack1lll1l1ll1l1_opy_(*args):
    global bstack1ll111ll1l_opy_
    bstack111l1l111_opy_.bstack111l11l1ll_opy_()
    for driver in bstack1ll111ll1l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l111lll_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll11l1ll1_opy_(self, *args, **kwargs):
    bstack1ll1l1l1_opy_ = bstack1lll111111_opy_(self, *args, **kwargs)
    bstack11llllll_opy_ = getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩ⑟"), None)
    if bstack11llllll_opy_ and bstack11llllll_opy_.get(bstack1ll111_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ①"), bstack1ll111_opy_ (u"ࠪࠫ②")) == bstack1ll111_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ③"):
        bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
    return bstack1ll1l1l1_opy_
@measure(event_name=EVENTS.bstack11l11ll1l_opy_, stage=STAGE.bstack1lll11l111_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11ll11l1l1_opy_(framework_name):
    from bstack_utils.config import Config
    bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
    if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩ④")):
        return
    bstack11ll11l11l_opy_.bstack1lll111lll_opy_(bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ⑤"), True)
    global bstack1ll11lllll_opy_
    global bstack1l1111llll_opy_
    bstack1ll11lllll_opy_ = framework_name
    logger.info(bstack1l11l11ll_opy_.format(bstack1ll11lllll_opy_.split(bstack1ll111_opy_ (u"ࠧ࠮ࠩ⑥"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1l1l11l1l1l_opy_():
            Service.start = bstack11l1111ll1_opy_
            Service.stop = bstack1lll1lll1_opy_
            webdriver.Remote.get = bstack1ll1111111_opy_
            webdriver.Remote.__init__ = bstack1l1l1l1l1_opy_
            if not isinstance(os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑ࡛ࡗࡉࡘ࡚࡟ࡑࡃࡕࡅࡑࡒࡅࡍࠩ⑦")), str):
                return
            WebDriver.quit = bstack11lllll11l_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack111l1l111_opy_.on():
            webdriver.Remote.__init__ = bstack1ll11l1ll1_opy_
        bstack1l1111llll_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack1ll111_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧ⑧")):
        bstack1l1111llll_opy_ = eval(os.environ.get(bstack1ll111_opy_ (u"ࠪࡗࡊࡒࡅࡏࡋࡘࡑࡤࡕࡒࡠࡒࡏࡅ࡞࡝ࡒࡊࡉࡋࡘࡤࡏࡎࡔࡖࡄࡐࡑࡋࡄࠨ⑨")))
    if not bstack1l1111llll_opy_:
        bstack111111ll1_opy_(bstack1ll111_opy_ (u"ࠦࡕࡧࡣ࡬ࡣࡪࡩࡸࠦ࡮ࡰࡶࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠨ⑩"), bstack11l1lllll_opy_)
    if bstack11ll1ll11l_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack1ll111_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭⑪")) and callable(getattr(RemoteConnection, bstack1ll111_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ⑫"))):
                RemoteConnection._get_proxy_url = bstack1l111lll11_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack1l111lll11_opy_
        except Exception as e:
            logger.error(bstack1l111ll1_opy_.format(str(e)))
    if bstack1ll111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ⑬") in str(framework_name).lower():
        if not bstack1l1l11l1l1l_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1l1l1l11l_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l1ll11111_opy_
            Config.getoption = bstack1l1l1ll111_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack11l1111l1_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l1l11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack11lllll11l_opy_(self):
    global bstack1ll11lllll_opy_
    global bstack1ll1lll1ll_opy_
    global bstack111llll111_opy_
    try:
        if bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⑭") in bstack1ll11lllll_opy_ and self.session_id != None and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"ࠩࡷࡩࡸࡺࡓࡵࡣࡷࡹࡸ࠭⑮"), bstack1ll111_opy_ (u"ࠪࠫ⑯")) != bstack1ll111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⑰"):
            bstack1lll1ll1l_opy_ = bstack1ll111_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⑱") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⑲")
            bstack1ll1111lll_opy_(logger, True)
            if os.environ.get(bstack1ll111_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ⑳"), None):
                self.execute_script(
                    bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭⑴") + json.dumps(
                        os.environ.get(bstack1ll111_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⑵"))) + bstack1ll111_opy_ (u"ࠪࢁࢂ࠭⑶"))
            if self != None:
                bstack11ll1ll11_opy_(self, bstack1lll1ll1l_opy_, bstack1ll111_opy_ (u"ࠫ࠱ࠦࠧ⑷").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1ll1l1ll111_opy_(bstack1lll111ll1l_opy_):
            item = store.get(bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⑸"), None)
            if item is not None and bstack11111l1l1_opy_(threading.current_thread(), bstack1ll111_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ⑹"), None):
                bstack1lll1111ll_opy_.bstack11lllllll_opy_(self, bstack1l1111l111_opy_, logger, item)
        threading.current_thread().testStatus = bstack1ll111_opy_ (u"ࠧࠨ⑺")
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࠤ⑻") + str(e))
    bstack111llll111_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack11lll1l1l1_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1l1l1l1l1_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1ll1lll1ll_opy_
    global bstack11l1l1111l_opy_
    global bstack1l1lll1l11_opy_
    global bstack1ll11lllll_opy_
    global bstack1lll111111_opy_
    global bstack1ll111ll1l_opy_
    global bstack1ll1l111l_opy_
    global bstack1l1lllll_opy_
    global bstack1l1111l111_opy_
    CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ⑼")] = str(bstack1ll11lllll_opy_) + str(__version__)
    command_executor = bstack111111lll_opy_(bstack1ll1l111l_opy_, CONFIG)
    logger.debug(bstack1lll11l11l_opy_.format(command_executor))
    proxy = bstack1l11111ll1_opy_(CONFIG, proxy)
    bstack1lll1l1l_opy_ = 0
    try:
        if bstack1l1lll1l11_opy_ is True:
            bstack1lll1l1l_opy_ = int(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⑽")))
    except:
        bstack1lll1l1l_opy_ = 0
    bstack1l1l1llll_opy_ = bstack1l1l111ll_opy_(CONFIG, bstack1lll1l1l_opy_)
    logger.debug(bstack1l11l11l_opy_.format(str(bstack1l1l1llll_opy_)))
    bstack1l1111l111_opy_ = CONFIG.get(bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⑾"))[bstack1lll1l1l_opy_]
    if bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ⑿") in CONFIG and CONFIG[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ⒀")]:
        bstack11ll1l1l1l_opy_(bstack1l1l1llll_opy_, bstack1l1lllll_opy_)
    if bstack1llll111_opy_.bstack1llll111l_opy_(CONFIG, bstack1lll1l1l_opy_) and bstack1llll111_opy_.bstack1ll1l11111_opy_(bstack1l1l1llll_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1ll1l1ll111_opy_(bstack1lll111ll1l_opy_):
            bstack1llll111_opy_.set_capabilities(bstack1l1l1llll_opy_, CONFIG)
    if desired_capabilities:
        bstack1111llll1_opy_ = bstack111lll1ll1_opy_(desired_capabilities)
        bstack1111llll1_opy_[bstack1ll111_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ⒁")] = bstack11l1lll11l_opy_(CONFIG)
        bstack1ll111lll_opy_ = bstack1l1l111ll_opy_(bstack1111llll1_opy_)
        if bstack1ll111lll_opy_:
            bstack1l1l1llll_opy_ = update(bstack1ll111lll_opy_, bstack1l1l1llll_opy_)
        desired_capabilities = None
    if options:
        bstack1llll1ll11_opy_(options, bstack1l1l1llll_opy_)
    if not options:
        options = bstack1ll1l111l1_opy_(bstack1l1l1llll_opy_)
    if proxy and bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ⒂")):
        options.proxy(proxy)
    if options and bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨ⒃")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack111l111l_opy_() < version.parse(bstack1ll111_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ⒄")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack1l1l1llll_opy_)
    logger.info(bstack11111l1l_opy_)
    bstack1ll1lll11_opy_.end(EVENTS.bstack11l11ll1l_opy_.value, EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦ⒅"),
                               EVENTS.bstack11l11ll1l_opy_.value + bstack1ll111_opy_ (u"ࠧࡀࡥ࡯ࡦࠥ⒆"), True, None)
    try:
        if bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"࠭࠴࠯࠳࠳࠲࠵࠭⒇")):
            bstack1lll111111_opy_(self, command_executor=command_executor,
                      options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
        elif bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭⒈")):
            bstack1lll111111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities, options=options,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        elif bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠨ࠴࠱࠹࠸࠴࠰ࠨ⒉")):
            bstack1lll111111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive, file_detector=file_detector)
        else:
            bstack1lll111111_opy_(self, command_executor=command_executor,
                      desired_capabilities=desired_capabilities,
                      browser_profile=browser_profile, proxy=proxy,
                      keep_alive=keep_alive)
    except Exception as bstack11lll1111l_opy_:
        logger.error(bstack1l1l1lll_opy_.format(bstack1ll111_opy_ (u"ࠩࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠨ⒊"), str(bstack11lll1111l_opy_)))
        raise bstack11lll1111l_opy_
    try:
        bstack1lll11l11_opy_ = bstack1ll111_opy_ (u"ࠪࠫ⒋")
        if bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࡥ࠵ࠬ⒌")):
            bstack1lll11l11_opy_ = self.caps.get(bstack1ll111_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧ⒍"))
        else:
            bstack1lll11l11_opy_ = self.capabilities.get(bstack1ll111_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨ⒎"))
        if bstack1lll11l11_opy_:
            bstack1lll11l1l_opy_(bstack1lll11l11_opy_)
            if bstack111l111l_opy_() <= version.parse(bstack1ll111_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧ⒏")):
                self.command_executor._url = bstack1ll111_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ⒐") + bstack1ll1l111l_opy_ + bstack1ll111_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨ⒑")
            else:
                self.command_executor._url = bstack1ll111_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧ⒒") + bstack1lll11l11_opy_ + bstack1ll111_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧ⒓")
            logger.debug(bstack11l111l11_opy_.format(bstack1lll11l11_opy_))
        else:
            logger.debug(bstack11llll1l11_opy_.format(bstack1ll111_opy_ (u"ࠧࡕࡰࡵ࡫ࡰࡥࡱࠦࡈࡶࡤࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠨ⒔")))
    except Exception as e:
        logger.debug(bstack11llll1l11_opy_.format(e))
    bstack1ll1lll1ll_opy_ = self.session_id
    if bstack1ll111_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭⒕") in bstack1ll11lllll_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack1ll111_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫ⒖"), None)
        if item:
            bstack1lll1l1l111l_opy_ = getattr(item, bstack1ll111_opy_ (u"ࠨࡡࡷࡩࡸࡺ࡟ࡤࡣࡶࡩࡤࡹࡴࡢࡴࡷࡩࡩ࠭⒗"), False)
            if not getattr(item, bstack1ll111_opy_ (u"ࠩࡢࡨࡷ࡯ࡶࡦࡴࠪ⒘"), None) and bstack1lll1l1l111l_opy_:
                setattr(store[bstack1ll111_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡬ࡸࡪࡳࠧ⒙")], bstack1ll111_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ⒚"), self)
        bstack11llllll_opy_ = getattr(threading.current_thread(), bstack1ll111_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࡙࡫ࡳࡵࡏࡨࡸࡦ࠭⒛"), None)
        if bstack11llllll_opy_ and bstack11llllll_opy_.get(bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭⒜"), bstack1ll111_opy_ (u"ࠧࠨ⒝")) == bstack1ll111_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ⒞"):
            bstack111l1l111_opy_.bstack11l1llll11_opy_(self)
    bstack1ll111ll1l_opy_.append(self)
    if bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ⒟") in CONFIG and bstack1ll111_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ⒠") in CONFIG[bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⒡")][bstack1lll1l1l_opy_]:
        bstack11l1l1111l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ⒢")][bstack1lll1l1l_opy_][bstack1ll111_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⒣")]
    logger.debug(bstack1llll11l_opy_.format(bstack1ll1lll1ll_opy_))
@measure(event_name=EVENTS.bstack11lll11l1l_opy_, stage=STAGE.bstack11ll1lll1_opy_, bstack1l1lll11_opy_=bstack11l1l1111l_opy_)
def bstack1ll1111111_opy_(self, url):
    global bstack1l11llllll_opy_
    global CONFIG
    try:
        bstack1lll1l111_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack1l11ll11l_opy_.format(str(err)))
    try:
        bstack1l11llllll_opy_(self, url)
    except Exception as e:
        try:
            bstack1l111l1l_opy_ = str(e)
            if any(err_msg in bstack1l111l1l_opy_ for err_msg in bstack1111l1ll_opy_):
                bstack1lll1l111_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack1l11ll11l_opy_.format(str(err)))
        raise e
def bstack1l1l1ll1_opy_(item, when):
    global bstack1lllllllll_opy_
    try:
        bstack1lllllllll_opy_(item, when)
    except Exception as e:
        pass
def bstack11l1111l1_opy_(item, call, rep):
    global bstack111ll11l1_opy_
    global bstack1ll111ll1l_opy_
    name = bstack1ll111_opy_ (u"ࠧࠨ⒤")
    try:
        if rep.when == bstack1ll111_opy_ (u"ࠨࡥࡤࡰࡱ࠭⒥"):
            bstack1ll1lll1ll_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack1ll111_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ⒦"))
            try:
                if (str(skipSessionName).lower() != bstack1ll111_opy_ (u"ࠪࡸࡷࡻࡥࠨ⒧")):
                    name = str(rep.nodeid)
                    bstack1ll11l1l_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ⒨"), name, bstack1ll111_opy_ (u"ࠬ࠭⒩"), bstack1ll111_opy_ (u"࠭ࠧ⒪"), bstack1ll111_opy_ (u"ࠧࠨ⒫"), bstack1ll111_opy_ (u"ࠨࠩ⒬"))
                    os.environ[bstack1ll111_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⒭")] = name
                    for driver in bstack1ll111ll1l_opy_:
                        if bstack1ll1lll1ll_opy_ == driver.session_id:
                            driver.execute_script(bstack1ll11l1l_opy_)
            except Exception as e:
                logger.debug(bstack1ll111_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ⒮").format(str(e)))
            try:
                bstack1ll11111l1_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack1ll111_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⒯"):
                    status = bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ⒰") if rep.outcome.lower() == bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⒱") else bstack1ll111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ⒲")
                    reason = bstack1ll111_opy_ (u"ࠨࠩ⒳")
                    if status == bstack1ll111_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ⒴"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack1ll111_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨ⒵") if status == bstack1ll111_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫⒶ") else bstack1ll111_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫⒷ")
                    data = name + bstack1ll111_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨⒸ") if status == bstack1ll111_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧⒹ") else name + bstack1ll111_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫⒺ") + reason
                    bstack1l11l1l11_opy_ = bstack1l111l1l11_opy_(bstack1ll111_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫⒻ"), bstack1ll111_opy_ (u"ࠪࠫⒼ"), bstack1ll111_opy_ (u"ࠫࠬⒽ"), bstack1ll111_opy_ (u"ࠬ࠭Ⓘ"), level, data)
                    for driver in bstack1ll111ll1l_opy_:
                        if bstack1ll1lll1ll_opy_ == driver.session_id:
                            driver.execute_script(bstack1l11l1l11_opy_)
            except Exception as e:
                logger.debug(bstack1ll111_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪⒿ").format(str(e)))
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫⓀ").format(str(e)))
    bstack111ll11l1_opy_(item, call, rep)
notset = Notset()
def bstack1l1l1ll111_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack11l111ll11_opy_
    if str(name).lower() == bstack1ll111_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨⓁ"):
        return bstack1ll111_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣⓂ")
    else:
        return bstack11l111ll11_opy_(self, name, default, skip)
def bstack1l111lll11_opy_(self):
    global CONFIG
    global bstack11ll1l1ll1_opy_
    try:
        proxy = bstack1ll1ll111l_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack1ll111_opy_ (u"ࠪ࠲ࡵࡧࡣࠨⓃ")):
                proxies = bstack1l11ll1ll1_opy_(proxy, bstack111111lll_opy_())
                if len(proxies) > 0:
                    protocol, bstack11l111l1ll_opy_ = proxies.popitem()
                    if bstack1ll111_opy_ (u"ࠦ࠿࠵࠯ࠣⓄ") in bstack11l111l1ll_opy_:
                        return bstack11l111l1ll_opy_
                    else:
                        return bstack1ll111_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨⓅ") + bstack11l111l1ll_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack1ll111_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡳࡶࡴࡾࡹࠡࡷࡵࡰࠥࡀࠠࡼࡿࠥⓆ").format(str(e)))
    return bstack11ll1l1ll1_opy_(self)
def bstack11ll1ll11l_opy_():
    return (bstack1ll111_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪⓇ") in CONFIG or bstack1ll111_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬⓈ") in CONFIG) and bstack1ll1l1l1ll_opy_() and bstack111l111l_opy_() >= version.parse(
        bstack11l11l11ll_opy_)
def bstack11l1l11lll_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack11l1l1111l_opy_
    global bstack1l1lll1l11_opy_
    global bstack1ll11lllll_opy_
    CONFIG[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫⓉ")] = str(bstack1ll11lllll_opy_) + str(__version__)
    bstack1lll1l1l_opy_ = 0
    try:
        if bstack1l1lll1l11_opy_ is True:
            bstack1lll1l1l_opy_ = int(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪⓊ")))
    except:
        bstack1lll1l1l_opy_ = 0
    CONFIG[bstack1ll111_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥⓋ")] = True
    bstack1l1l1llll_opy_ = bstack1l1l111ll_opy_(CONFIG, bstack1lll1l1l_opy_)
    logger.debug(bstack1l11l11l_opy_.format(str(bstack1l1l1llll_opy_)))
    if CONFIG.get(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩⓌ")):
        bstack11ll1l1l1l_opy_(bstack1l1l1llll_opy_, bstack1l1lllll_opy_)
    if bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩⓍ") in CONFIG and bstack1ll111_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬⓎ") in CONFIG[bstack1ll111_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫⓏ")][bstack1lll1l1l_opy_]:
        bstack11l1l1111l_opy_ = CONFIG[bstack1ll111_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬⓐ")][bstack1lll1l1l_opy_][bstack1ll111_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨⓑ")]
    import urllib
    import json
    if bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨⓒ") in CONFIG and str(CONFIG[bstack1ll111_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩⓓ")]).lower() != bstack1ll111_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬⓔ"):
        bstack1l111ll1l1_opy_ = bstack1l1l11l1l1_opy_()
        bstack11l1ll11l1_opy_ = bstack1l111ll1l1_opy_ + urllib.parse.quote(json.dumps(bstack1l1l1llll_opy_))
    else:
        bstack11l1ll11l1_opy_ = bstack1ll111_opy_ (u"ࠧࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠩⓕ") + urllib.parse.quote(json.dumps(bstack1l1l1llll_opy_))
    browser = self.connect(bstack11l1ll11l1_opy_)
    return browser
def bstack11l1l1ll1l_opy_():
    global bstack1l1111llll_opy_
    global bstack1ll11lllll_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1ll111l1l_opy_
        if not bstack1l1l11l1l1l_opy_():
            global bstack1lll11l1l1_opy_
            if not bstack1lll11l1l1_opy_:
                from bstack_utils.helper import bstack1ll1l11l_opy_, bstack11l11llll1_opy_
                bstack1lll11l1l1_opy_ = bstack1ll1l11l_opy_()
                bstack11l11llll1_opy_(bstack1ll11lllll_opy_)
            BrowserType.connect = bstack1ll111l1l_opy_
            return
        BrowserType.launch = bstack11l1l11lll_opy_
        bstack1l1111llll_opy_ = True
    except Exception as e:
        pass
def bstack1lll1l11l1ll_opy_():
    global CONFIG
    global bstack1l11l1111l_opy_
    global bstack1ll1l111l_opy_
    global bstack1l1lllll_opy_
    global bstack1l1lll1l11_opy_
    global bstack111llll11l_opy_
    CONFIG = json.loads(os.environ.get(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍࠧⓖ")))
    bstack1l11l1111l_opy_ = eval(os.environ.get(bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪⓗ")))
    bstack1ll1l111l_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡋ࡙ࡇࡥࡕࡓࡎࠪⓘ"))
    bstack1l1l1111l_opy_(CONFIG, bstack1l11l1111l_opy_)
    bstack111llll11l_opy_ = bstack1llll1ll1l_opy_.configure_logger(CONFIG, bstack111llll11l_opy_)
    if cli.bstack11llll1111_opy_():
        bstack111lll1l1_opy_.invoke(bstack111llll1l_opy_.CONNECT, bstack1llllll1l1_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1ll111_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫⓙ"), bstack1ll111_opy_ (u"ࠬ࠶ࠧⓚ")))
        cli.bstack1lll11l111l_opy_(cli_context.platform_index)
        cli.bstack1lll1l111l1_opy_(bstack111111lll_opy_(bstack1ll1l111l_opy_, CONFIG), cli_context.platform_index, bstack1ll1l111l1_opy_)
        cli.bstack1lll111l1ll_opy_()
        logger.debug(bstack1ll111_opy_ (u"ࠨࡃࡍࡋࠣ࡭ࡸࠦࡡࡤࡶ࡬ࡺࡪࠦࡦࡰࡴࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࠧⓛ") + str(cli_context.platform_index) + bstack1ll111_opy_ (u"ࠢࠣⓜ"))
        return # skip all existing operations
    global bstack1lll111111_opy_
    global bstack111llll111_opy_
    global bstack1llll1l1l_opy_
    global bstack11ll11ll1l_opy_
    global bstack11l1l1l1ll_opy_
    global bstack1l11ll111l_opy_
    global bstack1111l1l1l_opy_
    global bstack1l11llllll_opy_
    global bstack11ll1l1ll1_opy_
    global bstack11l111ll11_opy_
    global bstack1lllllllll_opy_
    global bstack111ll11l1_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack1lll111111_opy_ = webdriver.Remote.__init__
        bstack111llll111_opy_ = WebDriver.quit
        bstack1111l1l1l_opy_ = WebDriver.close
        bstack1l11llllll_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack1ll111_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫⓝ") in CONFIG or bstack1ll111_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ⓞ") in CONFIG) and bstack1ll1l1l1ll_opy_():
        if bstack111l111l_opy_() < version.parse(bstack11l11l11ll_opy_):
            logger.error(bstack1l1l1l11ll_opy_.format(bstack111l111l_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack1ll111_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫⓟ")) and callable(getattr(RemoteConnection, bstack1ll111_opy_ (u"ࠫࡤ࡭ࡥࡵࡡࡳࡶࡴࡾࡹࡠࡷࡵࡰࠬⓠ"))):
                    bstack11ll1l1ll1_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack11ll1l1ll1_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack1l111ll1_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack11l111ll11_opy_ = Config.getoption
        from _pytest import runner
        bstack1lllllllll_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack11l1l1l11l_opy_)
    try:
        from pytest_bdd import reporting
        bstack111ll11l1_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡴࠦࡲࡶࡰࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡧࡶࡸࡸ࠭ⓡ"))
    bstack1l1lllll_opy_ = CONFIG.get(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪⓢ"), {}).get(bstack1ll111_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩⓣ"))
    bstack1l1lll1l11_opy_ = True
    bstack11ll11l1l1_opy_(bstack1l11l11l1_opy_)
if (bstack111l1lll111_opy_()):
    bstack1lll1l11l1ll_opy_()
@error_handler(class_method=False)
def bstack1lll1ll1111l_opy_(hook_name, event, bstack11lll1lll1l_opy_=None):
    if hook_name not in [bstack1ll111_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩⓤ"), bstack1ll111_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ⓥ"), bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩⓦ"), bstack1ll111_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭ⓧ"), bstack1ll111_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪⓨ"), bstack1ll111_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧⓩ"), bstack1ll111_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭⓪"), bstack1ll111_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪ⓫")]:
        return
    node = store[bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⓬")]
    if hook_name in [bstack1ll111_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ⓭"), bstack1ll111_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭⓮")]:
        node = store[bstack1ll111_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥ࡭ࡰࡦࡸࡰࡪࡥࡩࡵࡧࡰࠫ⓯")]
    elif hook_name in [bstack1ll111_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡩ࡬ࡢࡵࡶࠫ⓰"), bstack1ll111_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡦࡰࡦࡹࡳࠨ⓱")]:
        node = store[bstack1ll111_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡦࡰࡦࡹࡳࡠ࡫ࡷࡩࡲ࠭⓲")]
    hook_type = bstack1lllll11llll_opy_(hook_name)
    if event == bstack1ll111_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩ⓳"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_[hook_type], bstack1lll1l1llll_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack111l1111l1_opy_ = {
            bstack1ll111_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⓴"): uuid,
            bstack1ll111_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨ⓵"): bstack11ll1l111_opy_(),
            bstack1ll111_opy_ (u"ࠬࡺࡹࡱࡧࠪ⓶"): bstack1ll111_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ⓷"),
            bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⓸"): hook_type,
            bstack1ll111_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⓹"): hook_name
        }
        store[bstack1ll111_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭⓺")].append(uuid)
        bstack1lll1l1lll1l_opy_ = node.nodeid
        if hook_type == bstack1ll111_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ⓻"):
            if not _1111ll11ll_opy_.get(bstack1lll1l1lll1l_opy_, None):
                _1111ll11ll_opy_[bstack1lll1l1lll1l_opy_] = {bstack1ll111_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ⓼"): []}
            _1111ll11ll_opy_[bstack1lll1l1lll1l_opy_][bstack1ll111_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⓽")].append(bstack111l1111l1_opy_[bstack1ll111_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ⓾")])
        _1111ll11ll_opy_[bstack1lll1l1lll1l_opy_ + bstack1ll111_opy_ (u"ࠧ࠮ࠩ⓿") + hook_name] = bstack111l1111l1_opy_
        bstack1lll1l11llll_opy_(node, bstack111l1111l1_opy_, bstack1ll111_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ─"))
    elif event == bstack1ll111_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ━"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1lll1l1lll1_opy_[hook_type], bstack1lll1l1llll_opy_.POST, node, None, bstack11lll1lll1l_opy_)
            return
        bstack111ll111ll_opy_ = node.nodeid + bstack1ll111_opy_ (u"ࠪ࠱ࠬ│") + hook_name
        _1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ┃")] = bstack11ll1l111_opy_()
        bstack1lll1l1l1111_opy_(_1111ll11ll_opy_[bstack111ll111ll_opy_][bstack1ll111_opy_ (u"ࠬࡻࡵࡪࡦࠪ┄")])
        bstack1lll1l11llll_opy_(node, _1111ll11ll_opy_[bstack111ll111ll_opy_], bstack1ll111_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ┅"), bstack1lll1l11l11l_opy_=bstack11lll1lll1l_opy_)
def bstack1lll1l1l1lll_opy_():
    global bstack1lll1l111l1l_opy_
    if bstack11l11l11l_opy_():
        bstack1lll1l111l1l_opy_ = bstack1ll111_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠫ┆")
    else:
        bstack1lll1l111l1l_opy_ = bstack1ll111_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ┇")
@bstack111l1l111_opy_.bstack1lll1llllll1_opy_
def bstack1lll1l1ll11l_opy_():
    bstack1lll1l1l1lll_opy_()
    if cli.is_running():
        try:
            bstack111l1l11l1l_opy_(bstack1lll1ll1111l_opy_)
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࡹࠠࡱࡣࡷࡧ࡭ࡀࠠࡼࡿࠥ┈").format(e))
        return
    if bstack1ll1l1l1ll_opy_():
        bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
        bstack1ll111_opy_ (u"ࠪࠫࠬࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡋࡵࡲࠡࡲࡳࡴࠥࡃࠠ࠲࠮ࠣࡱࡴࡪ࡟ࡦࡺࡨࡧࡺࡺࡥࠡࡩࡨࡸࡸࠦࡵࡴࡧࡧࠤ࡫ࡵࡲࠡࡣ࠴࠵ࡾࠦࡣࡰ࡯ࡰࡥࡳࡪࡳ࠮ࡹࡵࡥࡵࡶࡩ࡯ࡩࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡈࡲࡶࠥࡶࡰࡱࠢࡁࠤ࠶࠲ࠠ࡮ࡱࡧࡣࡪࡾࡥࡤࡷࡷࡩࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡳࡷࡱࠤࡧ࡫ࡣࡢࡷࡶࡩࠥ࡯ࡴࠡ࡫ࡶࠤࡵࡧࡴࡤࡪࡨࡨࠥ࡯࡮ࠡࡣࠣࡨ࡮࡬ࡦࡦࡴࡨࡲࡹࠦࡰࡳࡱࡦࡩࡸࡹࠠࡪࡦࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡖ࡫ࡹࡸࠦࡷࡦࠢࡱࡩࡪࡪࠠࡵࡱࠣࡹࡸ࡫ࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࡒࡤࡸࡨ࡮ࠨࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡡ࡫ࡥࡳࡪ࡬ࡦࡴࠬࠤ࡫ࡵࡲࠡࡲࡳࡴࠥࡄࠠ࠲ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠫࠬ࠭┉")
        if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡲࡵࡤࡠࡥࡤࡰࡱ࡫ࡤࠨ┊")):
            if CONFIG.get(bstack1ll111_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ┋")) is not None and int(CONFIG[bstack1ll111_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭┌")]) > 1:
                bstack111llllll1_opy_(bstack1lll1l1111_opy_)
            return
        bstack111llllll1_opy_(bstack1lll1l1111_opy_)
    try:
        bstack111l1l11l1l_opy_(bstack1lll1ll1111l_opy_)
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡷࠥࡶࡡࡵࡥ࡫࠾ࠥࢁࡽࠣ┍").format(e))
bstack1lll1l1ll11l_opy_()