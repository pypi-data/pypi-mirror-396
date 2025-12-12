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
bstack1ll111_opy_ (u"ࠥࠦࠧࠐࡐࡺࡶࡨࡷࡹࠦࡴࡦࡵࡷࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡪࡨࡰࡵ࡫ࡲࠡࡷࡶ࡭ࡳ࡭ࠠࡥ࡫ࡵࡩࡨࡺࠠࡱࡻࡷࡩࡸࡺࠠࡩࡱࡲ࡯ࡸ࠴ࠊࠣࠤࠥၝ")
import pytest
import io
import os
from contextlib import redirect_stdout, redirect_stderr
import subprocess
import sys
def bstack1111l111ll_opy_(bstack1111l111l1_opy_=None, bstack11111llll1_opy_=None):
    bstack1ll111_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡈࡵ࡬࡭ࡧࡦࡸࠥࡶࡹࡵࡧࡶࡸࠥࡺࡥࡴࡶࡶࠤࡺࡹࡩ࡯ࡩࠣࡴࡾࡺࡥࡴࡶࠪࡷࠥ࡯࡮ࡵࡧࡵࡲࡦࡲࠠࡂࡒࡌࡷ࠳ࠐࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡸࡪࡹࡴࡠࡣࡵ࡫ࡸࠦࠨ࡭࡫ࡶࡸ࠱ࠦ࡯ࡱࡶ࡬ࡳࡳࡧ࡬ࠪ࠼ࠣࡇࡴࡳࡰ࡭ࡧࡷࡩࠥࡲࡩࡴࡶࠣࡳ࡫ࠦࡰࡺࡶࡨࡷࡹࠦࡡࡳࡩࡸࡱࡪࡴࡴࡴࠢ࡬ࡲࡨࡲࡵࡥ࡫ࡱ࡫ࠥࡶࡡࡵࡪࡶࠤࡦࡴࡤࠡࡨ࡯ࡥ࡬ࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡖࡤ࡯ࡪࡹࠠࡱࡴࡨࡧࡪࡪࡥ࡯ࡥࡨࠤࡴࡼࡥࡳࠢࡷࡩࡸࡺ࡟ࡱࡣࡷ࡬ࡸࠦࡩࡧࠢࡥࡳࡹ࡮ࠠࡢࡴࡨࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡶࡨࡷࡹࡥࡰࡢࡶ࡫ࡷࠥ࠮࡬ࡪࡵࡷࠤࡴࡸࠠࡴࡶࡵ࠰ࠥࡵࡰࡵ࡫ࡲࡲࡦࡲࠩ࠻ࠢࡗࡩࡸࡺࠠࡧ࡫࡯ࡩ࠭ࡹࠩ࠰ࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠬ࡮࡫ࡳࠪࠢࡷࡳࠥࡩ࡯࡭࡮ࡨࡧࡹࠦࡦࡳࡱࡰ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡃࡢࡰࠣࡦࡪࠦࡡࠡࡵ࡬ࡲ࡬ࡲࡥࠡࡲࡤࡸ࡭ࠦࡳࡵࡴ࡬ࡲ࡬ࠦ࡯ࡳࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡴࡦࡺࡨࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡎ࡭࡮ࡰࡴࡨࡨࠥ࡯ࡦࠡࡶࡨࡷࡹࡥࡡࡳࡩࡶࠤ࡮ࡹࠠࡱࡴࡲࡺ࡮ࡪࡥࡥ࠰ࠍࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡨ࡮ࡩࡴ࠻ࠢࡆࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡲࡦࡵࡸࡰࡹࡹࠠࡸ࡫ࡷ࡬ࠥࡱࡥࡺࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡸࡻࡣࡤࡧࡶࡷࠥ࠮ࡢࡰࡱ࡯࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡩ࡯ࡶࡰࡷࠤ࠭࡯࡮ࡵࠫࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡲࡴࡪࡥࡪࡦࡶࠤ࠭ࡲࡩࡴࡶࠬࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳࠡࠪ࡯࡭ࡸࡺࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡧࡵࡶࡴࡸࠠࠩࡵࡷࡶ࠮ࠐࠠࠡࠢࠣࠦࠧࠨၞ")
    try:
        bstack1111l11l1l_opy_ = os.getenv(bstack1ll111_opy_ (u"ࠧࡖ࡙ࡕࡇࡖࡘࡤࡉࡕࡓࡔࡈࡒ࡙ࡥࡔࡆࡕࡗࠦၟ")) is not None
        if bstack1111l111l1_opy_ is not None:
            args = list(bstack1111l111l1_opy_)
        elif bstack11111llll1_opy_ is not None:
            if isinstance(bstack11111llll1_opy_, str):
                args = [bstack11111llll1_opy_]
            elif isinstance(bstack11111llll1_opy_, list):
                args = list(bstack11111llll1_opy_)
            else:
                args = [bstack1ll111_opy_ (u"ࠨ࠮ࠣၠ")]
        else:
            args = [bstack1ll111_opy_ (u"ࠢ࠯ࠤၡ")]
        if bstack1111l11l1l_opy_:
            return _11111lll1l_opy_(args)
        bstack11111lllll_opy_ = args + [
            bstack1ll111_opy_ (u"ࠣ࠯࠰ࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡴࡴ࡬ࡺࠤၢ"),
            bstack1ll111_opy_ (u"ࠤ࠰࠱ࡶࡻࡩࡦࡶࠥၣ")
        ]
        class bstack11111ll1ll_opy_:
            bstack1ll111_opy_ (u"ࠥࠦࠧࡖࡹࡵࡧࡶࡸࠥࡶ࡬ࡶࡩ࡬ࡲࠥࡺࡨࡢࡶࠣࡧࡦࡶࡴࡶࡴࡨࡷࠥࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤࠡࡶࡨࡷࡹࠦࡩࡵࡧࡰࡷ࠳ࠨࠢࠣၤ")
            def __init__(self):
                self.bstack1111l1111l_opy_ = []
                self.test_files = set()
                self.bstack1111l11l11_opy_ = None
            def pytest_collection_finish(self, session):
                bstack1ll111_opy_ (u"ࠦࠧࠨࡈࡰࡱ࡮ࠤࡨࡧ࡬࡭ࡧࡧࠤࡦ࡬ࡴࡦࡴࠣࡧࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠠࡪࡵࠣࡪ࡮ࡴࡩࡴࡪࡨࡨ࠳ࠨࠢࠣၥ")
                try:
                    for item in session.items:
                        nodeid = item.nodeid
                        self.bstack1111l1111l_opy_.append(nodeid)
                        if bstack1ll111_opy_ (u"ࠧࡀ࠺ࠣၦ") in nodeid:
                            file_path = nodeid.split(bstack1ll111_opy_ (u"ࠨ࠺࠻ࠤၧ"), 1)[0]
                            if file_path.endswith(bstack1ll111_opy_ (u"ࠧ࠯ࡲࡼࠫၨ")):
                                self.test_files.add(file_path)
                except Exception as e:
                    self.bstack1111l11l11_opy_ = str(e)
        collector = bstack11111ll1ll_opy_()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            exit_code = pytest.main(bstack11111lllll_opy_, plugins=[collector])
        if collector.bstack1111l11l11_opy_:
            return {bstack1ll111_opy_ (u"ࠣࡵࡸࡧࡨ࡫ࡳࡴࠤၩ"): False, bstack1ll111_opy_ (u"ࠤࡦࡳࡺࡴࡴࠣၪ"): 0, bstack1ll111_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࡶࠦၫ"): [], bstack1ll111_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡩ࡭ࡱ࡫ࡳࠣၬ"): [], bstack1ll111_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦၭ"): bstack1ll111_opy_ (u"ࠨࡃࡰ࡮࡯ࡩࡨࡺࡩࡰࡰࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨၮ").format(collector.bstack1111l11l11_opy_)}
        return {
            bstack1ll111_opy_ (u"ࠢࡴࡷࡦࡧࡪࡹࡳࠣၯ"): True,
            bstack1ll111_opy_ (u"ࠣࡥࡲࡹࡳࡺࠢၰ"): len(collector.bstack1111l1111l_opy_),
            bstack1ll111_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࡵࠥၱ"): collector.bstack1111l1111l_opy_,
            bstack1ll111_opy_ (u"ࠥࡸࡪࡹࡴࡠࡨ࡬ࡰࡪࡹࠢၲ"): sorted(collector.test_files),
            bstack1ll111_opy_ (u"ࠦࡪࡾࡩࡵࡡࡦࡳࡩ࡫ࠢၳ"): exit_code
        }
    except Exception as e:
        return {bstack1ll111_opy_ (u"ࠧࡹࡵࡤࡥࡨࡷࡸࠨၴ"): False, bstack1ll111_opy_ (u"ࠨࡣࡰࡷࡱࡸࠧၵ"): 0, bstack1ll111_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࡳࠣၶ"): [], bstack1ll111_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡷࠧၷ"): [], bstack1ll111_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣၸ"): bstack1ll111_opy_ (u"࡙ࠥࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡦࡴࡵࡳࡷࠦࡩ࡯ࠢࡷࡩࡸࡺࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡱࡱ࠾ࠥࢁࡽࠣၹ").format(e)}
def _11111lll1l_opy_(args):
    bstack1ll111_opy_ (u"ࠦࠧࠨࡉࡴࡱ࡯ࡥࡹ࡫ࡤࠡࡥࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠥ࡫ࡸࡦࡥࡸࡸࡪࡪࠠࡪࡰࠣࡥࠥࡹࡥࡱࡣࡵࡥࡹ࡫ࠠࡑࡻࡷ࡬ࡴࡴࠠࡱࡴࡲࡧࡪࡹࡳࠡࡶࡲࠤࡦࡼ࡯ࡪࡦࠣࡲࡪࡹࡴࡦࡦࠣࡴࡾࡺࡥࡴࡶࠣ࡭ࡸࡹࡵࡦࡵ࠱ࠦࠧࠨၺ")
    bstack11111lll11_opy_ = [sys.executable, bstack1ll111_opy_ (u"ࠧ࠳࡭ࠣၻ"), bstack1ll111_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨၼ"), bstack1ll111_opy_ (u"ࠢ࠮࠯ࡦࡳࡱࡲࡥࡤࡶ࠰ࡳࡳࡲࡹࠣၽ"), bstack1ll111_opy_ (u"ࠣ࠯࠰ࡵࡺ࡯ࡥࡵࠤၾ")]
    bstack11111ll1l1_opy_ = [a for a in args if a not in (bstack1ll111_opy_ (u"ࠤ࠰࠱ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡵ࡮࡭ࡻࠥၿ"), bstack1ll111_opy_ (u"ࠥ࠱࠲ࡷࡵࡪࡧࡷࠦႀ"), bstack1ll111_opy_ (u"ࠦ࠲ࡷࠢႁ"))]
    cmd = bstack11111lll11_opy_ + bstack11111ll1l1_opy_
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        stdout = proc.stdout.splitlines()
        bstack1111l1111l_opy_ = []
        test_files = set()
        for line in stdout:
            line = line.strip()
            if not line or bstack1ll111_opy_ (u"ࠧࠦࡣࡰ࡮࡯ࡩࡨࡺࡥࡥࠤႂ") in line.lower():
                continue
            if bstack1ll111_opy_ (u"ࠨ࠺࠻ࠤႃ") in line:
                bstack1111l1111l_opy_.append(line)
                file_path = line.split(bstack1ll111_opy_ (u"ࠢ࠻࠼ࠥႄ"), 1)[0]
                if file_path.endswith(bstack1ll111_opy_ (u"ࠨ࠰ࡳࡽࠬႅ")):
                    test_files.add(file_path)
        success = proc.returncode in (0, 5)
        return {
            bstack1ll111_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵࠥႆ"): success,
            bstack1ll111_opy_ (u"ࠥࡧࡴࡻ࡮ࡵࠤႇ"): len(bstack1111l1111l_opy_),
            bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࡷࠧႈ"): bstack1111l1111l_opy_,
            bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴࠤႉ"): sorted(test_files),
            bstack1ll111_opy_ (u"ࠨࡥࡹ࡫ࡷࡣࡨࡵࡤࡦࠤႊ"): proc.returncode,
            bstack1ll111_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨႋ"): None if success else bstack1ll111_opy_ (u"ࠣࡕࡸࡦࡵࡸ࡯ࡤࡧࡶࡷࠥࡩ࡯࡭࡮ࡨࡧࡹ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥࠢࠫࡩࡽ࡯ࡴࠡࡽࢀ࠭ࠧႌ").format(proc.returncode)
        }
    except Exception as e:
        return {bstack1ll111_opy_ (u"ࠤࡶࡹࡨࡩࡥࡴࡵႍࠥ"): False, bstack1ll111_opy_ (u"ࠥࡧࡴࡻ࡮ࡵࠤႎ"): 0, bstack1ll111_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࡷࠧႏ"): [], bstack1ll111_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡲࡥࡴࠤ႐"): [], bstack1ll111_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ႑"): bstack1ll111_opy_ (u"ࠢࡔࡷࡥࡴࡷࡵࡣࡦࡵࡶࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠦ႒").format(e)}