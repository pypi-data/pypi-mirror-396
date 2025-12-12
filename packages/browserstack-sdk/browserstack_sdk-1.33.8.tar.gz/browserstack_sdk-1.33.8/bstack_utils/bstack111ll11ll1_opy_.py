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
from uuid import uuid4
from bstack_utils.helper import bstack11ll1l111_opy_, bstack111ll1lll1l_opy_
from bstack_utils.bstack11ll11ll1_opy_ import bstack1lllll1l1lll_opy_
class bstack111l1l11l1_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll1l1l1ll_opy_=None, bstack1llll1l1lll1_opy_=True, bstack1l111l111l1_opy_=None, bstack1lll1lll11_opy_=None, result=None, duration=None, bstack111l1l111l_opy_=None, meta={}):
        self.bstack111l1l111l_opy_ = bstack111l1l111l_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1llll1l1lll1_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll1l1l1ll_opy_ = bstack1llll1l1l1ll_opy_
        self.bstack1l111l111l1_opy_ = bstack1l111l111l1_opy_
        self.bstack1lll1lll11_opy_ = bstack1lll1lll11_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l11llll_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111ll11l11_opy_(self, meta):
        self.meta = meta
    def bstack111ll1l111_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll1l11lll_opy_(self):
        bstack1llll1l111l1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1ll111_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ₼"): bstack1llll1l111l1_opy_,
            bstack1ll111_opy_ (u"ࠩ࡯ࡳࡨࡧࡴࡪࡱࡱࠫ₽"): bstack1llll1l111l1_opy_,
            bstack1ll111_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨ₾"): bstack1llll1l111l1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1ll111_opy_ (u"࡚ࠦࡴࡥࡹࡲࡨࡧࡹ࡫ࡤࠡࡣࡵ࡫ࡺࡳࡥ࡯ࡶ࠽ࠤࠧ₿") + key)
            setattr(self, key, val)
    def bstack1llll1l111ll_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⃀"): self.name,
            bstack1ll111_opy_ (u"࠭ࡢࡰࡦࡼࠫ⃁"): {
                bstack1ll111_opy_ (u"ࠧ࡭ࡣࡱ࡫ࠬ⃂"): bstack1ll111_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ⃃"),
                bstack1ll111_opy_ (u"ࠩࡦࡳࡩ࡫ࠧ⃄"): self.code
            },
            bstack1ll111_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ⃅"): self.scope,
            bstack1ll111_opy_ (u"ࠫࡹࡧࡧࡴࠩ⃆"): self.tags,
            bstack1ll111_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ⃇"): self.framework,
            bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⃈"): self.started_at
        }
    def bstack1llll1l1ll11_opy_(self):
        return {
         bstack1ll111_opy_ (u"ࠧ࡮ࡧࡷࡥࠬ⃉"): self.meta
        }
    def bstack1llll1ll1111_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡓࡧࡵࡹࡳࡖࡡࡳࡣࡰࠫ⃊"): {
                bstack1ll111_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪ࠭⃋"): self.bstack1llll1l1l1ll_opy_
            }
        }
    def bstack1llll1l1l11l_opy_(self, bstack1llll1l11l11_opy_, details):
        step = next(filter(lambda st: st[bstack1ll111_opy_ (u"ࠪ࡭ࡩ࠭⃌")] == bstack1llll1l11l11_opy_, self.meta[bstack1ll111_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃍")]), None)
        step.update(details)
    def bstack1l11l111l1_opy_(self, bstack1llll1l11l11_opy_):
        step = next(filter(lambda st: st[bstack1ll111_opy_ (u"ࠬ࡯ࡤࠨ⃎")] == bstack1llll1l11l11_opy_, self.meta[bstack1ll111_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⃏")]), None)
        step.update({
            bstack1ll111_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ⃐"): bstack11ll1l111_opy_()
        })
    def bstack111l1l1lll_opy_(self, bstack1llll1l11l11_opy_, result, duration=None):
        bstack1l111l111l1_opy_ = bstack11ll1l111_opy_()
        if bstack1llll1l11l11_opy_ is not None and self.meta.get(bstack1ll111_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⃑")):
            step = next(filter(lambda st: st[bstack1ll111_opy_ (u"ࠩ࡬ࡨ⃒ࠬ")] == bstack1llll1l11l11_opy_, self.meta[bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴ⃓ࠩ")]), None)
            step.update({
                bstack1ll111_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⃔"): bstack1l111l111l1_opy_,
                bstack1ll111_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧ⃕"): duration if duration else bstack111ll1lll1l_opy_(step[bstack1ll111_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ⃖")], bstack1l111l111l1_opy_),
                bstack1ll111_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ⃗"): result.result,
                bstack1ll111_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦ⃘ࠩ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1l11111_opy_):
        if self.meta.get(bstack1ll111_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ⃙")):
            self.meta[bstack1ll111_opy_ (u"ࠪࡷࡹ࡫ࡰࡴ⃚ࠩ")].append(bstack1llll1l11111_opy_)
        else:
            self.meta[bstack1ll111_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ⃛")] = [ bstack1llll1l11111_opy_ ]
    def bstack1llll1l11l1l_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠬࡻࡵࡪࡦࠪ⃜"): self.bstack111l11llll_opy_(),
            bstack1ll111_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⃝"): bstack1ll111_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⃞"),
            **self.bstack1llll1l111ll_opy_(),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll1l1ll11_opy_()
        }
    def bstack1llll1l1111l_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1ll111_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭⃟"): self.bstack1l111l111l1_opy_,
            bstack1ll111_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⃠"): self.duration,
            bstack1ll111_opy_ (u"ࠪࡶࡪࡹࡵ࡭ࡶࠪ⃡"): self.result.result
        }
        if data[bstack1ll111_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⃢")] == bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ⃣"):
            data[bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫࡟ࡵࡻࡳࡩࠬ⃤")] = self.result.bstack1llllll1l11_opy_()
            data[bstack1ll111_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨ⃥")] = [{bstack1ll111_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨ⃦ࠫ"): self.result.bstack111ll1l11l1_opy_()}]
        return data
    def bstack1llll1l1ll1l_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⃧"): self.bstack111l11llll_opy_(),
            **self.bstack1llll1l111ll_opy_(),
            **self.bstack1llll1l11lll_opy_(),
            **self.bstack1llll1l1111l_opy_(),
            **self.bstack1llll1l1ll11_opy_()
        }
    def bstack1111lll1l1_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1ll111_opy_ (u"ࠪࡗࡹࡧࡲࡵࡧࡧ⃨ࠫ") in event:
            return self.bstack1llll1l11l1l_opy_()
        elif bstack1ll111_opy_ (u"ࠫࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭⃩") in event:
            return self.bstack1llll1l1ll1l_opy_()
    def bstack111l1l11ll_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l111l111l1_opy_ = time if time else bstack11ll1l111_opy_()
        self.duration = duration if duration else bstack111ll1lll1l_opy_(self.started_at, self.bstack1l111l111l1_opy_)
        if result:
            self.result = result
class bstack111ll1l1l1_opy_(bstack111l1l11l1_opy_):
    def __init__(self, hooks=[], bstack111ll1ll11_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111ll1ll11_opy_ = bstack111ll1ll11_opy_
        super().__init__(*args, **kwargs, bstack1lll1lll11_opy_=bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶ⃪ࠪ"))
    @classmethod
    def bstack1llll1l1llll_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1ll111_opy_ (u"࠭ࡩࡥ⃫ࠩ"): id(step),
                bstack1ll111_opy_ (u"ࠧࡵࡧࡻࡸ⃬ࠬ"): step.name,
                bstack1ll111_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥ⃭ࠩ"): step.keyword,
            })
        return bstack111ll1l1l1_opy_(
            **kwargs,
            meta={
                bstack1ll111_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧ⃮ࠪ"): {
                    bstack1ll111_opy_ (u"ࠪࡲࡦࡳࡥࠨ⃯"): feature.name,
                    bstack1ll111_opy_ (u"ࠫࡵࡧࡴࡩࠩ⃰"): feature.filename,
                    bstack1ll111_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪ⃱"): feature.description
                },
                bstack1ll111_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨ⃲"): {
                    bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ⃳"): scenario.name
                },
                bstack1ll111_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ⃴"): steps,
                bstack1ll111_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫ⃵"): bstack1lllll1l1lll_opy_(test)
            }
        )
    def bstack1llll1l1l111_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ⃶"): self.hooks
        }
    def bstack1llll1l11ll1_opy_(self):
        if self.bstack111ll1ll11_opy_:
            return {
                bstack1ll111_opy_ (u"ࠫ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠪ⃷"): self.bstack111ll1ll11_opy_
            }
        return {}
    def bstack1llll1l1ll1l_opy_(self):
        return {
            **super().bstack1llll1l1ll1l_opy_(),
            **self.bstack1llll1l1l111_opy_()
        }
    def bstack1llll1l11l1l_opy_(self):
        return {
            **super().bstack1llll1l11l1l_opy_(),
            **self.bstack1llll1l11ll1_opy_()
        }
    def bstack111l1l11ll_opy_(self):
        return bstack1ll111_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ⃸")
class bstack111l1ll1ll_opy_(bstack111l1l11l1_opy_):
    def __init__(self, hook_type, *args,bstack111ll1ll11_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1l1llll1ll1_opy_ = None
        self.bstack111ll1ll11_opy_ = bstack111ll1ll11_opy_
        super().__init__(*args, **kwargs, bstack1lll1lll11_opy_=bstack1ll111_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ⃹"))
    def bstack1111ll111l_opy_(self):
        return self.hook_type
    def bstack1llll1l1l1l1_opy_(self):
        return {
            bstack1ll111_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪ⃺"): self.hook_type
        }
    def bstack1llll1l1ll1l_opy_(self):
        return {
            **super().bstack1llll1l1ll1l_opy_(),
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack1llll1l11l1l_opy_(self):
        return {
            **super().bstack1llll1l11l1l_opy_(),
            bstack1ll111_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢ࡭ࡩ࠭⃻"): self.bstack1l1llll1ll1_opy_,
            **self.bstack1llll1l1l1l1_opy_()
        }
    def bstack111l1l11ll_opy_(self):
        return bstack1ll111_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫ⃼")
    def bstack111ll1ll1l_opy_(self, bstack1l1llll1ll1_opy_):
        self.bstack1l1llll1ll1_opy_ = bstack1l1llll1ll1_opy_