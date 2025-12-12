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
import os
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll11llll1_opy_ import bstack1ll1ll1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll11l_opy_ import (
    bstack1llll1l1111_opy_,
    bstack1lllll11l11_opy_,
    bstack1lllll11111_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1ll1lllllll_opy_ import bstack1ll11lll1ll_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11111l1l_opy_
from bstack_utils.helper import bstack1l1l11l1l1l_opy_
import threading
import os
import urllib.parse
class bstack1ll1ll1l111_opy_(bstack1ll1ll1l1l1_opy_):
    def __init__(self, bstack1ll1l11111l_opy_):
        super().__init__()
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1llll11ll11_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11lll11ll_opy_)
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1llll11ll11_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11llll1l1_opy_)
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1l1ll_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11lll11l1_opy_)
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1lllll1111l_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11lllllll_opy_)
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.bstack1llll11ll11_opy_, bstack1lllll11l11_opy_.PRE), self.bstack1l11lll1ll1_opy_)
        bstack1ll11lll1ll_opy_.bstack1l1llll111l_opy_((bstack1llll1l1111_opy_.QUIT, bstack1lllll11l11_opy_.PRE), self.on_close)
        self.bstack1ll1l11111l_opy_ = bstack1ll1l11111l_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l11lll11ll_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        bstack1l11llllll1_opy_: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠤ࡯ࡥࡺࡴࡣࡩࠤፐ"):
            return
        if not bstack1l1l11l1l1l_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢ࡯ࡥࡺࡴࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠮ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠢፑ"))
            return
        def wrapped(bstack1l11llllll1_opy_, launch, *args, **kwargs):
            response = self.bstack1l11llll11l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1ll111_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪፒ"): True}).encode(bstack1ll111_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦፓ")))
            if response is not None and response.capabilities:
                if not bstack1l1l11l1l1l_opy_():
                    browser = launch(bstack1l11llllll1_opy_)
                    return browser
                bstack1l1l1111111_opy_ = json.loads(response.capabilities.decode(bstack1ll111_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧፔ")))
                if not bstack1l1l1111111_opy_: # empty caps bstack1l11lll111l_opy_ bstack1l11lll1l11_opy_ bstack1l11llll111_opy_ bstack1ll1llll11l_opy_ or error in processing
                    return
                bstack1l11llll1ll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l1111111_opy_))
                f.bstack1llll11l11l_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11lll1111_opy_, bstack1l11llll1ll_opy_)
                f.bstack1llll11l11l_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11lll1l1l_opy_, bstack1l1l1111111_opy_)
                browser = bstack1l11llllll1_opy_.connect(bstack1l11llll1ll_opy_)
                return browser
        return wrapped
    def bstack1l11lll11l1_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠢࡥ࡫ࡶࡴࡦࡺࡣࡩࠤፕ"):
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡔࡨࡸࡺࡸ࡮ࡪࡰࡪࠤ࡮ࡴࠠࡥ࡫ࡶࡴࡦࡺࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠮ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠢፖ"))
            return
        if not bstack1l1l11l1l1l_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack1ll111_opy_ (u"ࠩࡳࡥࡷࡧ࡭ࡴࠩፗ"), {}).get(bstack1ll111_opy_ (u"ࠪࡦࡸࡖࡡࡳࡣࡰࡷࠬፘ")):
                    bstack1l11lll1lll_opy_ = args[0][bstack1ll111_opy_ (u"ࠦࡵࡧࡲࡢ࡯ࡶࠦፙ")][bstack1ll111_opy_ (u"ࠧࡨࡳࡑࡣࡵࡥࡲࡹࠢፚ")]
                    session_id = bstack1l11lll1lll_opy_.get(bstack1ll111_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴࡉࡥࠤ፛"))
                    f.bstack1llll11l11l_opy_(instance, bstack1ll11lll1ll_opy_.bstack1l11ll1lll1_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡤࡪࡵࡳࡥࡹࡩࡨࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࠥ፜"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l11lll1ll1_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        bstack1l11llllll1_opy_: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠣࡥࡲࡲࡳ࡫ࡣࡵࠤ፝"):
            return
        if not bstack1l1l11l1l1l_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡥࡲࡲࡳ࡫ࡣࡵࠢࡰࡩࡹ࡮࡯ࡥ࠮ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠢ፞"))
            return
        def wrapped(bstack1l11llllll1_opy_, connect, *args, **kwargs):
            response = self.bstack1l11llll11l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1ll111_opy_ (u"ࠪ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩ፟"): True}).encode(bstack1ll111_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥ፠")))
            if response is not None and response.capabilities:
                bstack1l1l1111111_opy_ = json.loads(response.capabilities.decode(bstack1ll111_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ፡")))
                if not bstack1l1l1111111_opy_:
                    return
                bstack1l11llll1ll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l1111111_opy_))
                if bstack1l1l1111111_opy_.get(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ።")):
                    browser = bstack1l11llllll1_opy_.bstack1l11lllll11_opy_(bstack1l11llll1ll_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11llll1ll_opy_
                    return connect(bstack1l11llllll1_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11llll1l1_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        bstack1l1ll1l1l1l_opy_: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠢ࡯ࡧࡺࡣࡵࡧࡧࡦࠤ፣"):
            return
        if not bstack1l1l11l1l1l_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠣࡔࡨࡸࡺࡸ࡮ࡪࡰࡪࠤ࡮ࡴࠠ࡯ࡧࡺࡣࡵࡧࡧࡦࠢࡰࡩࡹ࡮࡯ࡥ࠮ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠢ፤"))
            return
        def wrapped(bstack1l1ll1l1l1l_opy_, bstack1l11ll1llll_opy_, *args, **kwargs):
            contexts = bstack1l1ll1l1l1l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1ll111_opy_ (u"ࠤࡤࡦࡴࡻࡴ࠻ࡤ࡯ࡥࡳࡱࠢ፥") in page.url:
                                return page
                            else:
                                return bstack1l11ll1llll_opy_(bstack1l1ll1l1l1l_opy_)
                    else:
                        return bstack1l11ll1llll_opy_(bstack1l1ll1l1l1l_opy_)
        return wrapped
    def bstack1l11llll11l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack1ll111_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲࡠ࡫ࡱ࡭ࡹࡀࠠࠣ፦") + str(req) + bstack1ll111_opy_ (u"ࠦࠧ፧"))
        try:
            r = self.bstack1lll1l11lll_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1ll111_opy_ (u"ࠧࡸࡥࡤࡧ࡬ࡺࡪࡪࠠࡧࡴࡲࡱࠥࡹࡥࡳࡸࡨࡶ࠿ࠦࡳࡶࡥࡦࡩࡸࡹ࠽ࠣ፨") + str(r.success) + bstack1ll111_opy_ (u"ࠨࠢ፩"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll111_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧ፪") + str(e) + bstack1ll111_opy_ (u"ࠣࠤ፫"))
            traceback.print_exc()
            raise e
    def bstack1l11lllllll_opy_(
        self,
        f: bstack1ll11lll1ll_opy_,
        Connection: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠤࡢࡷࡪࡴࡤࡠ࡯ࡨࡷࡸࡧࡧࡦࡡࡷࡳࡤࡹࡥࡳࡸࡨࡶࠧ፬"):
            return
        if not bstack1l1l11l1l1l_opy_():
            return
        def wrapped(Connection, bstack1l11lllll1l_opy_, *args, **kwargs):
            return bstack1l11lllll1l_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll11lll1ll_opy_,
        bstack1l11llllll1_opy_: object,
        exec: Tuple[bstack1lllll11111_opy_, str],
        bstack1llll11ll1l_opy_: Tuple[bstack1llll1l1111_opy_, bstack1lllll11l11_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll111_opy_ (u"ࠥࡧࡱࡵࡳࡦࠤ፭"):
            return
        if not bstack1l1l11l1l1l_opy_():
            self.logger.debug(bstack1ll111_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡧࡱࡵࡳࡦࠢࡰࡩࡹ࡮࡯ࡥ࠮ࠣࡲࡴࡺࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠢ፮"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped