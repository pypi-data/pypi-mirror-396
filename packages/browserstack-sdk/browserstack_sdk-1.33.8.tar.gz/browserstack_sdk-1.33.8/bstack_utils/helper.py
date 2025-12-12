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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1l1l1l1ll_opy_, bstack1lll1ll111_opy_, bstack1ll1ll1ll_opy_,
                                    bstack11l1l11llll_opy_, bstack11l1l1111ll_opy_, bstack11l1l111l1l_opy_, bstack11l1l111ll1_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1lll11l1_opy_, bstack1l111ll1_opy_
from bstack_utils.proxy import bstack1l1l1ll11l_opy_, bstack1ll1ll111l_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1llll1ll1l_opy_
from bstack_utils.bstack1111l11ll_opy_ import bstack1lll1ll1l1_opy_
from browserstack_sdk._version import __version__
bstack11ll11l11l_opy_ = Config.bstack1l11l1l1l_opy_()
logger = bstack1llll1ll1l_opy_.get_logger(__name__, bstack1llll1ll1l_opy_.bstack1ll1l111lll_opy_())
def bstack11ll11ll1ll_opy_(config):
    return config[bstack1ll111_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭᭱")]
def bstack11l1lllllll_opy_(config):
    return config[bstack1ll111_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ᭲")]
def bstack1ll1l11l1_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111lll11ll1_opy_(obj):
    values = []
    bstack11l111111ll_opy_ = re.compile(bstack1ll111_opy_ (u"ࡸࠢ࡟ࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤࡢࡤࠬࠦࠥ᭳"), re.I)
    for key in obj.keys():
        if bstack11l111111ll_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111l1ll11ll_opy_(config):
    tags = []
    tags.extend(bstack111lll11ll1_opy_(os.environ))
    tags.extend(bstack111lll11ll1_opy_(config))
    return tags
def bstack111lllll1l1_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack11l111l1l11_opy_(bstack111lllll111_opy_):
    if not bstack111lllll111_opy_:
        return bstack1ll111_opy_ (u"ࠧࠨ᭴")
    return bstack1ll111_opy_ (u"ࠣࡽࢀࠤ࠭ࢁࡽࠪࠤ᭵").format(bstack111lllll111_opy_.name, bstack111lllll111_opy_.email)
def bstack11ll111l111_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111lll11l1l_opy_ = repo.common_dir
        info = {
            bstack1ll111_opy_ (u"ࠤࡶ࡬ࡦࠨ᭶"): repo.head.commit.hexsha,
            bstack1ll111_opy_ (u"ࠥࡷ࡭ࡵࡲࡵࡡࡶ࡬ࡦࠨ᭷"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1ll111_opy_ (u"ࠦࡧࡸࡡ࡯ࡥ࡫ࠦ᭸"): repo.active_branch.name,
            bstack1ll111_opy_ (u"ࠧࡺࡡࡨࠤ᭹"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡺࡥࡳࠤ᭺"): bstack11l111l1l11_opy_(repo.head.commit.committer),
            bstack1ll111_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࡢࡨࡦࡺࡥࠣ᭻"): repo.head.commit.committed_datetime.isoformat(),
            bstack1ll111_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࠣ᭼"): bstack11l111l1l11_opy_(repo.head.commit.author),
            bstack1ll111_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࡡࡧࡥࡹ࡫ࠢ᭽"): repo.head.commit.authored_datetime.isoformat(),
            bstack1ll111_opy_ (u"ࠥࡧࡴࡳ࡭ࡪࡶࡢࡱࡪࡹࡳࡢࡩࡨࠦ᭾"): repo.head.commit.message,
            bstack1ll111_opy_ (u"ࠦࡷࡵ࡯ࡵࠤ᭿"): repo.git.rev_parse(bstack1ll111_opy_ (u"ࠧ࠳࠭ࡴࡪࡲࡻ࠲ࡺ࡯ࡱ࡮ࡨࡺࡪࡲࠢᮀ")),
            bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰࡳࡳࡥࡧࡪࡶࡢࡨ࡮ࡸࠢᮁ"): bstack111lll11l1l_opy_,
            bstack1ll111_opy_ (u"ࠢࡸࡱࡵ࡯ࡹࡸࡥࡦࡡࡪ࡭ࡹࡥࡤࡪࡴࠥᮂ"): subprocess.check_output([bstack1ll111_opy_ (u"ࠣࡩ࡬ࡸࠧᮃ"), bstack1ll111_opy_ (u"ࠤࡵࡩࡻ࠳ࡰࡢࡴࡶࡩࠧᮄ"), bstack1ll111_opy_ (u"ࠥ࠱࠲࡭ࡩࡵ࠯ࡦࡳࡲࡳ࡯࡯࠯ࡧ࡭ࡷࠨᮅ")]).strip().decode(
                bstack1ll111_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᮆ")),
            bstack1ll111_opy_ (u"ࠧࡲࡡࡴࡶࡢࡸࡦ࡭ࠢᮇ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡹ࡟ࡴ࡫ࡱࡧࡪࡥ࡬ࡢࡵࡷࡣࡹࡧࡧࠣᮈ"): repo.git.rev_list(
                bstack1ll111_opy_ (u"ࠢࡼࡿ࠱࠲ࢀࢃࠢᮉ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack11l11l111ll_opy_ = []
        for remote in remotes:
            bstack111lll111l1_opy_ = {
                bstack1ll111_opy_ (u"ࠣࡰࡤࡱࡪࠨᮊ"): remote.name,
                bstack1ll111_opy_ (u"ࠤࡸࡶࡱࠨᮋ"): remote.url,
            }
            bstack11l11l111ll_opy_.append(bstack111lll111l1_opy_)
        bstack111ll111l11_opy_ = {
            bstack1ll111_opy_ (u"ࠥࡲࡦࡳࡥࠣᮌ"): bstack1ll111_opy_ (u"ࠦ࡬࡯ࡴࠣᮍ"),
            **info,
            bstack1ll111_opy_ (u"ࠧࡸࡥ࡮ࡱࡷࡩࡸࠨᮎ"): bstack11l11l111ll_opy_
        }
        bstack111ll111l11_opy_ = bstack111lll11lll_opy_(bstack111ll111l11_opy_)
        return bstack111ll111l11_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1ll111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡯ࡱࡷ࡯ࡥࡹ࡯࡮ࡨࠢࡊ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡥࡳࡴࡲࡶ࠿ࠦࡻࡾࠤᮏ").format(err))
        return {}
def bstack111ll1111ll_opy_(bstack11l11l11l11_opy_=None):
    bstack1ll111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡈࡧࡷࠤ࡬࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡷࡵ࡫ࡣࡪࡨ࡬ࡧࡦࡲ࡬ࡺࠢࡩࡳࡷࡳࡡࡵࡶࡨࡨࠥ࡬࡯ࡳࠢࡄࡍࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࡷࡶࡩࠥࡩࡡࡴࡧࡶࠤ࡫ࡵࡲࠡࡧࡤࡧ࡭ࠦࡦࡰ࡮ࡧࡩࡷࠦࡩ࡯ࠢࡷ࡬ࡪࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡩࡳࡱࡪࡥࡳࡵࠣࠬࡱ࡯ࡳࡵ࠮ࠣࡳࡵࡺࡩࡰࡰࡤࡰ࠮ࡀࠠࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡐࡲࡲࡪࡀࠠࡎࡱࡱࡳ࠲ࡸࡥࡱࡱࠣࡥࡵࡶࡲࡰࡣࡦ࡬࠱ࠦࡵࡴࡧࡶࠤࡨࡻࡲࡳࡧࡱࡸࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡ࡝ࡲࡷ࠳࡭ࡥࡵࡥࡺࡨ࠭࠯࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡇࡰࡴࡹࡿࠠ࡭࡫ࡶࡸࠥࡡ࡝࠻ࠢࡐࡹࡱࡺࡩ࠮ࡴࡨࡴࡴࠦࡡࡱࡲࡵࡳࡦࡩࡨࠡࡹ࡬ࡸ࡭ࠦ࡮ࡰࠢࡶࡳࡺࡸࡣࡦࡵࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࡪࠬࠡࡴࡨࡸࡺࡸ࡮ࡴࠢ࡞ࡡࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡒࡩࡴࡶࠣࡳ࡫ࠦࡰࡢࡶ࡫ࡷ࠿ࠦࡍࡶ࡮ࡷ࡭࠲ࡸࡥࡱࡱࠣࡥࡵࡶࡲࡰࡣࡦ࡬ࠥࡽࡩࡵࡪࠣࡷࡵ࡫ࡣࡪࡨ࡬ࡧࠥ࡬࡯࡭ࡦࡨࡶࡸࠦࡴࡰࠢࡤࡲࡦࡲࡹࡻࡧࠍࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡰ࡮ࡹࡴ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡨ࡮ࡩࡴࡴ࠮ࠣࡩࡦࡩࡨࠡࡥࡲࡲࡹࡧࡩ࡯࡫ࡱ࡫ࠥ࡭ࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡣࠣࡪࡴࡲࡤࡦࡴ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᮐ")
    if bstack11l11l11l11_opy_ is None:
        bstack11l11l11l11_opy_ = [os.getcwd()]
    elif isinstance(bstack11l11l11l11_opy_, list) and len(bstack11l11l11l11_opy_) == 0:
        return []
    results = []
    for folder in bstack11l11l11l11_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack1ll111_opy_ (u"ࠣࡈࡲࡰࡩ࡫ࡲࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡩࡽ࡯ࡳࡵ࠼ࠣࡿࢂࠨᮑ").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack1ll111_opy_ (u"ࠤࡳࡶࡎࡪࠢᮒ"): bstack1ll111_opy_ (u"ࠥࠦᮓ"),
                bstack1ll111_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥᮔ"): [],
                bstack1ll111_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡸࠨᮕ"): [],
                bstack1ll111_opy_ (u"ࠨࡰࡳࡆࡤࡸࡪࠨᮖ"): bstack1ll111_opy_ (u"ࠢࠣᮗ"),
                bstack1ll111_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡎࡧࡶࡷࡦ࡭ࡥࡴࠤᮘ"): [],
                bstack1ll111_opy_ (u"ࠤࡳࡶ࡙࡯ࡴ࡭ࡧࠥᮙ"): bstack1ll111_opy_ (u"ࠥࠦᮚ"),
                bstack1ll111_opy_ (u"ࠦࡵࡸࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠦᮛ"): bstack1ll111_opy_ (u"ࠧࠨᮜ"),
                bstack1ll111_opy_ (u"ࠨࡰࡳࡔࡤࡻࡉ࡯ࡦࡧࠤᮝ"): bstack1ll111_opy_ (u"ࠢࠣᮞ")
            }
            bstack111llll11ll_opy_ = repo.active_branch.name
            bstack111lll11l11_opy_ = repo.head.commit
            result[bstack1ll111_opy_ (u"ࠣࡲࡵࡍࡩࠨᮟ")] = bstack111lll11l11_opy_.hexsha
            bstack11l11111111_opy_ = _111ll111ll1_opy_(repo)
            logger.debug(bstack1ll111_opy_ (u"ࠤࡅࡥࡸ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠࡧࡱࡵࠤࡨࡵ࡭ࡱࡣࡵ࡭ࡸࡵ࡮࠻ࠢࠥᮠ") + str(bstack11l11111111_opy_) + bstack1ll111_opy_ (u"ࠥࠦᮡ"))
            if bstack11l11111111_opy_:
                try:
                    bstack11l111l1111_opy_ = repo.git.diff(bstack1ll111_opy_ (u"ࠦ࠲࠳࡮ࡢ࡯ࡨ࠱ࡴࡴ࡬ࡺࠤᮢ"), bstack1lll11ll11l_opy_ (u"ࠧࢁࡢࡢࡵࡨࡣࡧࡸࡡ࡯ࡥ࡫ࢁ࠳࠴࠮ࡼࡥࡸࡶࡷ࡫࡮ࡵࡡࡥࡶࡦࡴࡣࡩࡿࠥᮣ")).split(bstack1ll111_opy_ (u"࠭࡜࡯ࠩᮤ"))
                    logger.debug(bstack1ll111_opy_ (u"ࠢࡄࡪࡤࡲ࡬࡫ࡤࠡࡨ࡬ࡰࡪࡹࠠࡣࡧࡷࡻࡪ࡫࡮ࠡࡽࡥࡥࡸ࡫࡟ࡣࡴࡤࡲࡨ࡮ࡽࠡࡣࡱࡨࠥࢁࡣࡶࡴࡵࡩࡳࡺ࡟ࡣࡴࡤࡲࡨ࡮ࡽ࠻ࠢࠥᮥ") + str(bstack11l111l1111_opy_) + bstack1ll111_opy_ (u"ࠣࠤᮦ"))
                    result[bstack1ll111_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠣᮧ")] = [f.strip() for f in bstack11l111l1111_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack1lll11ll11l_opy_ (u"ࠥࡿࡧࡧࡳࡦࡡࡥࡶࡦࡴࡣࡩࡿ࠱࠲ࢀࡩࡵࡳࡴࡨࡲࡹࡥࡢࡳࡣࡱࡧ࡭ࢃࠢᮨ")))
                except Exception:
                    logger.debug(bstack1ll111_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡨࡧࡷࠤࡨ࡮ࡡ࡯ࡩࡨࡨࠥ࡬ࡩ࡭ࡧࡶࠤ࡫ࡸ࡯࡮ࠢࡥࡶࡦࡴࡣࡩࠢࡦࡳࡲࡶࡡࡳ࡫ࡶࡳࡳ࠴ࠠࡇࡣ࡯ࡰ࡮ࡴࡧࠡࡤࡤࡧࡰࠦࡴࡰࠢࡵࡩࡨ࡫࡮ࡵࠢࡦࡳࡲࡳࡩࡵࡵ࠱ࠦᮩ"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack1ll111_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧ᮪ࠦ")] = _111ll1llll1_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack1ll111_opy_ (u"ࠨࡦࡪ࡮ࡨࡷࡈ࡮ࡡ࡯ࡩࡨࡨ᮫ࠧ")] = _111ll1llll1_opy_(commits[:5])
            bstack111llll1111_opy_ = set()
            bstack11l111lll11_opy_ = []
            for commit in commits:
                logger.debug(bstack1ll111_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡨࡵ࡭࡮࡫ࡷ࠾ࠥࠨᮬ") + str(commit.message) + bstack1ll111_opy_ (u"ࠣࠤᮭ"))
                bstack111ll1ll111_opy_ = commit.author.name if commit.author else bstack1ll111_opy_ (u"ࠤࡘࡲࡰࡴ࡯ࡸࡰࠥᮮ")
                bstack111llll1111_opy_.add(bstack111ll1ll111_opy_)
                bstack11l111lll11_opy_.append({
                    bstack1ll111_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦᮯ"): commit.message.strip(),
                    bstack1ll111_opy_ (u"ࠦࡺࡹࡥࡳࠤ᮰"): bstack111ll1ll111_opy_
                })
            result[bstack1ll111_opy_ (u"ࠧࡧࡵࡵࡪࡲࡶࡸࠨ᮱")] = list(bstack111llll1111_opy_)
            result[bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡓࡥࡴࡵࡤ࡫ࡪࡹࠢ᮲")] = bstack11l111lll11_opy_
            result[bstack1ll111_opy_ (u"ࠢࡱࡴࡇࡥࡹ࡫ࠢ᮳")] = bstack111lll11l11_opy_.committed_datetime.strftime(bstack1ll111_opy_ (u"ࠣࠧ࡜࠱ࠪࡳ࠭ࠦࡦࠥ᮴"))
            if (not result[bstack1ll111_opy_ (u"ࠤࡳࡶ࡙࡯ࡴ࡭ࡧࠥ᮵")] or result[bstack1ll111_opy_ (u"ࠥࡴࡷ࡚ࡩࡵ࡮ࡨࠦ᮶")].strip() == bstack1ll111_opy_ (u"ࠦࠧ᮷")) and bstack111lll11l11_opy_.message:
                bstack11l111l1ll1_opy_ = bstack111lll11l11_opy_.message.strip().splitlines()
                result[bstack1ll111_opy_ (u"ࠧࡶࡲࡕ࡫ࡷࡰࡪࠨ᮸")] = bstack11l111l1ll1_opy_[0] if bstack11l111l1ll1_opy_ else bstack1ll111_opy_ (u"ࠨࠢ᮹")
                if len(bstack11l111l1ll1_opy_) > 2:
                    result[bstack1ll111_opy_ (u"ࠢࡱࡴࡇࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠢᮺ")] = bstack1ll111_opy_ (u"ࠨ࡞ࡱࠫᮻ").join(bstack11l111l1ll1_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack1ll111_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡲࡴࡺࡲࡡࡵ࡫ࡱ࡫ࠥࡍࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡃࡌࠤࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠠࠩࡨࡲࡰࡩ࡫ࡲ࠻ࠢࡾࢁ࠮ࡀࠠࡼࡿࠣ࠱ࠥࢁࡽࠣᮼ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _111ll11111l_opy_(result)
    ]
    return filtered_results
def _111ll11111l_opy_(result):
    bstack1ll111_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡌࡪࡲࡰࡦࡴࠣࡸࡴࠦࡣࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡣࠣ࡫࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡸࡻ࡬ࡵࠢ࡬ࡷࠥࡼࡡ࡭࡫ࡧࠤ࠭ࡴ࡯࡯࠯ࡨࡱࡵࡺࡹࠡࡨ࡬ࡰࡪࡹࡃࡩࡣࡱ࡫ࡪࡪࠠࡢࡰࡧࠤࡦࡻࡴࡩࡱࡵࡷ࠮࠴ࠊࠡࠢࠣࠤࠧࠨࠢᮽ")
    return (
        isinstance(result.get(bstack1ll111_opy_ (u"ࠦ࡫࡯࡬ࡦࡵࡆ࡬ࡦࡴࡧࡦࡦࠥᮾ"), None), list)
        and len(result[bstack1ll111_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦᮿ")]) > 0
        and isinstance(result.get(bstack1ll111_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡹࠢᯀ"), None), list)
        and len(result[bstack1ll111_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸࡳࠣᯁ")]) > 0
    )
def _111ll111ll1_opy_(repo):
    bstack1ll111_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡖࡵࡽࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡹ࡮ࡥࠡࡤࡤࡷࡪࠦࡢࡳࡣࡱࡧ࡭ࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡨ࡫ࡹࡩࡳࠦࡲࡦࡲࡲࠤࡼ࡯ࡴࡩࡱࡸࡸࠥ࡮ࡡࡳࡦࡦࡳࡩ࡫ࡤࠡࡰࡤࡱࡪࡹࠠࡢࡰࡧࠤࡼࡵࡲ࡬ࠢࡺ࡭ࡹ࡮ࠠࡢ࡮࡯ࠤ࡛ࡉࡓࠡࡲࡵࡳࡻ࡯ࡤࡦࡴࡶ࠲ࠏࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡸ࡭࡫ࠠࡥࡧࡩࡥࡺࡲࡴࠡࡤࡵࡥࡳࡩࡨࠡ࡫ࡩࠤࡵࡵࡳࡴ࡫ࡥࡰࡪ࠲ࠠࡦ࡮ࡶࡩࠥࡔ࡯࡯ࡧ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᯂ")
    try:
        try:
            origin = repo.remotes.origin
            bstack111ll1111l1_opy_ = origin.refs[bstack1ll111_opy_ (u"ࠩࡋࡉࡆࡊࠧᯃ")]
            target = bstack111ll1111l1_opy_.reference.name
            if target.startswith(bstack1ll111_opy_ (u"ࠪࡳࡷ࡯ࡧࡪࡰ࠲ࠫᯄ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack1ll111_opy_ (u"ࠫࡴࡸࡩࡨ࡫ࡱ࠳ࠬᯅ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111ll1llll1_opy_(commits):
    bstack1ll111_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡍࡥࡵࠢ࡯࡭ࡸࡺࠠࡰࡨࠣࡧ࡭ࡧ࡮ࡨࡧࡧࠤ࡫࡯࡬ࡦࡵࠣࡪࡷࡵ࡭ࠡࡣࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡨࡵ࡭࡮࡫ࡷࡷ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᯆ")
    bstack11l111l1111_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack111ll11ll1l_opy_ in diff:
                        if bstack111ll11ll1l_opy_.a_path:
                            bstack11l111l1111_opy_.add(bstack111ll11ll1l_opy_.a_path)
                        if bstack111ll11ll1l_opy_.b_path:
                            bstack11l111l1111_opy_.add(bstack111ll11ll1l_opy_.b_path)
    except Exception:
        pass
    return list(bstack11l111l1111_opy_)
def bstack111lll11lll_opy_(bstack111ll111l11_opy_):
    bstack11l1111lll1_opy_ = bstack111lllll1ll_opy_(bstack111ll111l11_opy_)
    if bstack11l1111lll1_opy_ and bstack11l1111lll1_opy_ > bstack11l1l11llll_opy_:
        bstack11l1111111l_opy_ = bstack11l1111lll1_opy_ - bstack11l1l11llll_opy_
        bstack111llll11l1_opy_ = bstack11l111l1lll_opy_(bstack111ll111l11_opy_[bstack1ll111_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠢᯇ")], bstack11l1111111l_opy_)
        bstack111ll111l11_opy_[bstack1ll111_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠣᯈ")] = bstack111llll11l1_opy_
        logger.info(bstack1ll111_opy_ (u"ࠣࡖ࡫ࡩࠥࡩ࡯࡮࡯࡬ࡸࠥ࡮ࡡࡴࠢࡥࡩࡪࡴࠠࡵࡴࡸࡲࡨࡧࡴࡦࡦ࠱ࠤࡘ࡯ࡺࡦࠢࡲࡪࠥࡩ࡯࡮࡯࡬ࡸࠥࡧࡦࡵࡧࡵࠤࡹࡸࡵ࡯ࡥࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤࢀࢃࠠࡌࡄࠥᯉ")
                    .format(bstack111lllll1ll_opy_(bstack111ll111l11_opy_) / 1024))
    return bstack111ll111l11_opy_
def bstack111lllll1ll_opy_(bstack1l1l111l_opy_):
    try:
        if bstack1l1l111l_opy_:
            bstack11l111111l1_opy_ = json.dumps(bstack1l1l111l_opy_)
            bstack111l1ll1ll1_opy_ = sys.getsizeof(bstack11l111111l1_opy_)
            return bstack111l1ll1ll1_opy_
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠤࡖࡳࡲ࡫ࡴࡩ࡫ࡱ࡫ࠥࡽࡥ࡯ࡶࠣࡻࡷࡵ࡮ࡨࠢࡺ࡬࡮ࡲࡥࠡࡥࡤࡰࡨࡻ࡬ࡢࡶ࡬ࡲ࡬ࠦࡳࡪࡼࡨࠤࡴ࡬ࠠࡋࡕࡒࡒࠥࡵࡢ࡫ࡧࡦࡸ࠿ࠦࡻࡾࠤᯊ").format(e))
    return -1
def bstack11l111l1lll_opy_(field, bstack11l111l1l1l_opy_):
    try:
        bstack111ll1ll11l_opy_ = len(bytes(bstack11l1l1111ll_opy_, bstack1ll111_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᯋ")))
        bstack111lllll11l_opy_ = bytes(field, bstack1ll111_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᯌ"))
        bstack111llll1l11_opy_ = len(bstack111lllll11l_opy_)
        bstack11l11l11111_opy_ = ceil(bstack111llll1l11_opy_ - bstack11l111l1l1l_opy_ - bstack111ll1ll11l_opy_)
        if bstack11l11l11111_opy_ > 0:
            bstack11l111l11ll_opy_ = bstack111lllll11l_opy_[:bstack11l11l11111_opy_].decode(bstack1ll111_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᯍ"), errors=bstack1ll111_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪ࠭ᯎ")) + bstack11l1l1111ll_opy_
            return bstack11l111l11ll_opy_
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡺࡲࡶࡰࡦࡥࡹ࡯࡮ࡨࠢࡩ࡭ࡪࡲࡤ࠭ࠢࡱࡳࡹ࡮ࡩ࡯ࡩࠣࡻࡦࡹࠠࡵࡴࡸࡲࡨࡧࡴࡦࡦࠣ࡬ࡪࡸࡥ࠻ࠢࡾࢁࠧᯏ").format(e))
    return field
def bstack1l1lll11l1_opy_():
    env = os.environ
    if (bstack1ll111_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡘࡖࡑࠨᯐ") in env and len(env[bstack1ll111_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢ࡙ࡗࡒࠢᯑ")]) > 0) or (
            bstack1ll111_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣࡍࡕࡍࡆࠤᯒ") in env and len(env[bstack1ll111_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤࡎࡏࡎࡇࠥᯓ")]) > 0):
        return {
            bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯔ"): bstack1ll111_opy_ (u"ࠨࡊࡦࡰ࡮࡭ࡳࡹࠢᯕ"),
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯖ"): env.get(bstack1ll111_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᯗ")),
            bstack1ll111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᯘ"): env.get(bstack1ll111_opy_ (u"ࠥࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᯙ")),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯚ"): env.get(bstack1ll111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᯛ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠨࡃࡊࠤᯜ")) == bstack1ll111_opy_ (u"ࠢࡵࡴࡸࡩࠧᯝ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡄࡋࠥᯞ"))):
        return {
            bstack1ll111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᯟ"): bstack1ll111_opy_ (u"ࠥࡇ࡮ࡸࡣ࡭ࡧࡆࡍࠧᯠ"),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᯡ"): env.get(bstack1ll111_opy_ (u"ࠧࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᯢ")),
            bstack1ll111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᯣ"): env.get(bstack1ll111_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡋࡑࡅࠦᯤ")),
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᯥ"): env.get(bstack1ll111_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑ᯦ࠧ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠥࡇࡎࠨᯧ")) == bstack1ll111_opy_ (u"ࠦࡹࡸࡵࡦࠤᯨ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࠧᯩ"))):
        return {
            bstack1ll111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᯪ"): bstack1ll111_opy_ (u"ࠢࡕࡴࡤࡺ࡮ࡹࠠࡄࡋࠥᯫ"),
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᯬ"): env.get(bstack1ll111_opy_ (u"ࠤࡗࡖࡆ࡜ࡉࡔࡡࡅ࡙ࡎࡒࡄࡠ࡙ࡈࡆࡤ࡛ࡒࡍࠤᯭ")),
            bstack1ll111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᯮ"): env.get(bstack1ll111_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᯯ")),
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᯰ"): env.get(bstack1ll111_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᯱ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠢࡄࡋ᯲ࠥ")) == bstack1ll111_opy_ (u"ࠣࡶࡵࡹࡪࠨ᯳") and env.get(bstack1ll111_opy_ (u"ࠤࡆࡍࡤࡔࡁࡎࡇࠥ᯴")) == bstack1ll111_opy_ (u"ࠥࡧࡴࡪࡥࡴࡪ࡬ࡴࠧ᯵"):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᯶"): bstack1ll111_opy_ (u"ࠧࡉ࡯ࡥࡧࡶ࡬࡮ࡶࠢ᯷"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᯸"): None,
            bstack1ll111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᯹"): None,
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᯺"): None
        }
    if env.get(bstack1ll111_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡈࡒࡂࡐࡆࡌࠧ᯻")) and env.get(bstack1ll111_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡃࡐࡏࡐࡍ࡙ࠨ᯼")):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᯽"): bstack1ll111_opy_ (u"ࠧࡈࡩࡵࡤࡸࡧࡰ࡫ࡴࠣ᯾"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᯿"): env.get(bstack1ll111_opy_ (u"ࠢࡃࡋࡗࡆ࡚ࡉࡋࡆࡖࡢࡋࡎ࡚࡟ࡉࡖࡗࡔࡤࡕࡒࡊࡉࡌࡒࠧᰀ")),
            bstack1ll111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᰁ"): None,
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰂ"): env.get(bstack1ll111_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᰃ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠦࡈࡏࠢᰄ")) == bstack1ll111_opy_ (u"ࠧࡺࡲࡶࡧࠥᰅ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠨࡄࡓࡑࡑࡉࠧᰆ"))):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰇ"): bstack1ll111_opy_ (u"ࠣࡆࡵࡳࡳ࡫ࠢᰈ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰉ"): env.get(bstack1ll111_opy_ (u"ࠥࡈࡗࡕࡎࡆࡡࡅ࡙ࡎࡒࡄࡠࡎࡌࡒࡐࠨᰊ")),
            bstack1ll111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰋ"): None,
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᰌ"): env.get(bstack1ll111_opy_ (u"ࠨࡄࡓࡑࡑࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᰍ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠢࡄࡋࠥᰎ")) == bstack1ll111_opy_ (u"ࠣࡶࡵࡹࡪࠨᰏ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࠧᰐ"))):
        return {
            bstack1ll111_opy_ (u"ࠥࡲࡦࡳࡥࠣᰑ"): bstack1ll111_opy_ (u"ࠦࡘ࡫࡭ࡢࡲ࡫ࡳࡷ࡫ࠢᰒ"),
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰓ"): env.get(bstack1ll111_opy_ (u"ࠨࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡒࡖࡌࡇࡎࡊ࡜ࡄࡘࡎࡕࡎࡠࡗࡕࡐࠧᰔ")),
            bstack1ll111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰕ"): env.get(bstack1ll111_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨᰖ")),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰗ"): env.get(bstack1ll111_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡊࡐࡄࡢࡍࡉࠨᰘ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠦࡈࡏࠢᰙ")) == bstack1ll111_opy_ (u"ࠧࡺࡲࡶࡧࠥᰚ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠨࡇࡊࡖࡏࡅࡇࡥࡃࡊࠤᰛ"))):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰜ"): bstack1ll111_opy_ (u"ࠣࡉ࡬ࡸࡑࡧࡢࠣᰝ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰞ"): env.get(bstack1ll111_opy_ (u"ࠥࡇࡎࡥࡊࡐࡄࡢ࡙ࡗࡒࠢᰟ")),
            bstack1ll111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰠ"): env.get(bstack1ll111_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᰡ")),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᰢ"): env.get(bstack1ll111_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡊࡆࠥᰣ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠣࡅࡌࠦᰤ")) == bstack1ll111_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᰥ") and bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࠨᰦ"))):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᰧ"): bstack1ll111_opy_ (u"ࠧࡈࡵࡪ࡮ࡧ࡯࡮ࡺࡥࠣᰨ"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᰩ"): env.get(bstack1ll111_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᰪ")),
            bstack1ll111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᰫ"): env.get(bstack1ll111_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡒࡁࡃࡇࡏࠦᰬ")) or env.get(bstack1ll111_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡐࡄࡑࡊࠨᰭ")),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᰮ"): env.get(bstack1ll111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᰯ"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠨࡔࡇࡡࡅ࡙ࡎࡒࡄࠣᰰ"))):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰱ"): bstack1ll111_opy_ (u"ࠣࡘ࡬ࡷࡺࡧ࡬ࠡࡕࡷࡹࡩ࡯࡯ࠡࡖࡨࡥࡲࠦࡓࡦࡴࡹ࡭ࡨ࡫ࡳࠣᰲ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰳ"): bstack1ll111_opy_ (u"ࠥࡿࢂࢁࡽࠣᰴ").format(env.get(bstack1ll111_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡈࡒ࡙ࡓࡊࡁࡕࡋࡒࡒࡘࡋࡒࡗࡇࡕ࡙ࡗࡏࠧᰵ")), env.get(bstack1ll111_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡓࡖࡔࡐࡅࡄࡖࡌࡈࠬᰶ"))),
            bstack1ll111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥ᰷ࠣ"): env.get(bstack1ll111_opy_ (u"ࠢࡔ࡛ࡖࡘࡊࡓ࡟ࡅࡇࡉࡍࡓࡏࡔࡊࡑࡑࡍࡉࠨ᰸")),
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᰹"): env.get(bstack1ll111_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤ᰺"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࠧ᰻"))):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᰼"): bstack1ll111_opy_ (u"ࠧࡇࡰࡱࡸࡨࡽࡴࡸࠢ᰽"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᰾"): bstack1ll111_opy_ (u"ࠢࡼࡿ࠲ࡴࡷࡵࡪࡦࡥࡷ࠳ࢀࢃ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂࠨ᰿").format(env.get(bstack1ll111_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢ࡙ࡗࡒࠧ᱀")), env.get(bstack1ll111_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡆࡉࡃࡐࡗࡑࡘࡤࡔࡁࡎࡇࠪ᱁")), env.get(bstack1ll111_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡖࡒࡐࡌࡈࡇ࡙ࡥࡓࡍࡗࡊࠫ᱂")), env.get(bstack1ll111_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨ᱃"))),
            bstack1ll111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᱄"): env.get(bstack1ll111_opy_ (u"ࠨࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥ᱅")),
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᱆"): env.get(bstack1ll111_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤ᱇"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠤࡄ࡞࡚ࡘࡅࡠࡊࡗࡘࡕࡥࡕࡔࡇࡕࡣࡆࡍࡅࡏࡖࠥ᱈")) and env.get(bstack1ll111_opy_ (u"ࠥࡘࡋࡥࡂࡖࡋࡏࡈࠧ᱉")):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᱊"): bstack1ll111_opy_ (u"ࠧࡇࡺࡶࡴࡨࠤࡈࡏࠢ᱋"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᱌"): bstack1ll111_opy_ (u"ࠢࡼࡿࡾࢁ࠴ࡥࡢࡶ࡫࡯ࡨ࠴ࡸࡥࡴࡷ࡯ࡸࡸࡅࡢࡶ࡫࡯ࡨࡎࡪ࠽ࡼࡿࠥᱍ").format(env.get(bstack1ll111_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡌࡏࡖࡐࡇࡅ࡙ࡏࡏࡏࡕࡈࡖ࡛ࡋࡒࡖࡔࡌࠫᱎ")), env.get(bstack1ll111_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡐࡓࡑࡍࡉࡈ࡚ࠧᱏ")), env.get(bstack1ll111_opy_ (u"ࠪࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠪ᱐"))),
            bstack1ll111_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᱑"): env.get(bstack1ll111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠧ᱒")),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᱓"): env.get(bstack1ll111_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢ᱔"))
        }
    if any([env.get(bstack1ll111_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᱕")), env.get(bstack1ll111_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡘࡅࡔࡑࡏ࡚ࡊࡊ࡟ࡔࡑࡘࡖࡈࡋ࡟ࡗࡇࡕࡗࡎࡕࡎࠣ᱖")), env.get(bstack1ll111_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡓࡐࡗࡕࡇࡊࡥࡖࡆࡔࡖࡍࡔࡔࠢ᱗"))]):
        return {
            bstack1ll111_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᱘"): bstack1ll111_opy_ (u"ࠧࡇࡗࡔࠢࡆࡳࡩ࡫ࡂࡶ࡫࡯ࡨࠧ᱙"),
            bstack1ll111_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᱚ"): env.get(bstack1ll111_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡔ࡚ࡈࡌࡊࡅࡢࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᱛ")),
            bstack1ll111_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᱜ"): env.get(bstack1ll111_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᱝ")),
            bstack1ll111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᱞ"): env.get(bstack1ll111_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᱟ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡒࡺࡳࡢࡦࡴࠥᱠ")):
        return {
            bstack1ll111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᱡ"): bstack1ll111_opy_ (u"ࠢࡃࡣࡰࡦࡴࡵࠢᱢ"),
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᱣ"): env.get(bstack1ll111_opy_ (u"ࠤࡥࡥࡲࡨ࡯ࡰࡡࡥࡹ࡮ࡲࡤࡓࡧࡶࡹࡱࡺࡳࡖࡴ࡯ࠦᱤ")),
            bstack1ll111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᱥ"): env.get(bstack1ll111_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡸ࡮࡯ࡳࡶࡍࡳࡧࡔࡡ࡮ࡧࠥᱦ")),
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱧ"): env.get(bstack1ll111_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡢࡶ࡫࡯ࡨࡓࡻ࡭ࡣࡧࡵࠦᱨ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࠣᱩ")) or env.get(bstack1ll111_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡐࡅࡎࡔ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡖࡘࡆࡘࡔࡆࡆࠥᱪ")):
        return {
            bstack1ll111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱫ"): bstack1ll111_opy_ (u"࡛ࠥࡪࡸࡣ࡬ࡧࡵࠦᱬ"),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᱭ"): env.get(bstack1ll111_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᱮ")),
            bstack1ll111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱯ"): bstack1ll111_opy_ (u"ࠢࡎࡣ࡬ࡲࠥࡖࡩࡱࡧ࡯࡭ࡳ࡫ࠢᱰ") if env.get(bstack1ll111_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࡡࡐࡅࡎࡔ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡖࡘࡆࡘࡔࡆࡆࠥᱱ")) else None,
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᱲ"): env.get(bstack1ll111_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡌࡏࡔࡠࡅࡒࡑࡒࡏࡔࠣᱳ"))
        }
    if any([env.get(bstack1ll111_opy_ (u"ࠦࡌࡉࡐࡠࡒࡕࡓࡏࡋࡃࡕࠤᱴ")), env.get(bstack1ll111_opy_ (u"ࠧࡍࡃࡍࡑࡘࡈࡤࡖࡒࡐࡌࡈࡇ࡙ࠨᱵ")), env.get(bstack1ll111_opy_ (u"ࠨࡇࡐࡑࡊࡐࡊࡥࡃࡍࡑࡘࡈࡤࡖࡒࡐࡌࡈࡇ࡙ࠨᱶ"))]):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᱷ"): bstack1ll111_opy_ (u"ࠣࡉࡲࡳ࡬ࡲࡥࠡࡅ࡯ࡳࡺࡪࠢᱸ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᱹ"): None,
            bstack1ll111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᱺ"): env.get(bstack1ll111_opy_ (u"ࠦࡕࡘࡏࡋࡇࡆࡘࡤࡏࡄࠣᱻ")),
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᱼ"): env.get(bstack1ll111_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡏࡄࠣᱽ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࠥ᱾")):
        return {
            bstack1ll111_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱿"): bstack1ll111_opy_ (u"ࠤࡖ࡬࡮ࡶࡰࡢࡤ࡯ࡩࠧᲀ"),
            bstack1ll111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲁ"): env.get(bstack1ll111_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᲂ")),
            bstack1ll111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲃ"): bstack1ll111_opy_ (u"ࠨࡊࡰࡤࠣࠧࢀࢃࠢᲄ").format(env.get(bstack1ll111_opy_ (u"ࠧࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡎࡔࡈ࡟ࡊࡆࠪᲅ"))) if env.get(bstack1ll111_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡏࡕࡂࡠࡋࡇࠦᲆ")) else None,
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᲇ"): env.get(bstack1ll111_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᲈ"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠦࡓࡋࡔࡍࡋࡉ࡝ࠧᲉ"))):
        return {
            bstack1ll111_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᲊ"): bstack1ll111_opy_ (u"ࠨࡎࡦࡶ࡯࡭࡫ࡿࠢ᲋"),
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ᲌"): env.get(bstack1ll111_opy_ (u"ࠣࡆࡈࡔࡑࡕ࡙ࡠࡗࡕࡐࠧ᲍")),
            bstack1ll111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᲎"): env.get(bstack1ll111_opy_ (u"ࠥࡗࡎ࡚ࡅࡠࡐࡄࡑࡊࠨ᲏")),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᲐ"): env.get(bstack1ll111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢᲑ"))
        }
    if bstack1l1l1111l1_opy_(env.get(bstack1ll111_opy_ (u"ࠨࡇࡊࡖࡋ࡙ࡇࡥࡁࡄࡖࡌࡓࡓ࡙ࠢᲒ"))):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᲓ"): bstack1ll111_opy_ (u"ࠣࡉ࡬ࡸࡍࡻࡢࠡࡃࡦࡸ࡮ࡵ࡮ࡴࠤᲔ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲕ"): bstack1ll111_opy_ (u"ࠥࡿࢂ࠵ࡻࡾ࠱ࡤࡧࡹ࡯࡯࡯ࡵ࠲ࡶࡺࡴࡳ࠰ࡽࢀࠦᲖ").format(env.get(bstack1ll111_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡘࡋࡒࡗࡇࡕࡣ࡚ࡘࡌࠨᲗ")), env.get(bstack1ll111_opy_ (u"ࠬࡍࡉࡕࡊࡘࡆࡤࡘࡅࡑࡑࡖࡍ࡙ࡕࡒ࡚ࠩᲘ")), env.get(bstack1ll111_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡒࡖࡐࡢࡍࡉ࠭Კ"))),
            bstack1ll111_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᲚ"): env.get(bstack1ll111_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠ࡙ࡒࡖࡐࡌࡌࡐ࡙ࠥᲛ")),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᲜ"): env.get(bstack1ll111_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢࡖ࡚ࡔ࡟ࡊࡆࠥᲝ"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠦࡈࡏࠢᲞ")) == bstack1ll111_opy_ (u"ࠧࡺࡲࡶࡧࠥᲟ") and env.get(bstack1ll111_opy_ (u"ࠨࡖࡆࡔࡆࡉࡑࠨᲠ")) == bstack1ll111_opy_ (u"ࠢ࠲ࠤᲡ"):
        return {
            bstack1ll111_opy_ (u"ࠣࡰࡤࡱࡪࠨᲢ"): bstack1ll111_opy_ (u"ࠤ࡙ࡩࡷࡩࡥ࡭ࠤᲣ"),
            bstack1ll111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲤ"): bstack1ll111_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࢀࢃࠢᲥ").format(env.get(bstack1ll111_opy_ (u"ࠬ࡜ࡅࡓࡅࡈࡐࡤ࡛ࡒࡍࠩᲦ"))),
            bstack1ll111_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᲧ"): None,
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲨ"): None,
        }
    if env.get(bstack1ll111_opy_ (u"ࠣࡖࡈࡅࡒࡉࡉࡕ࡛ࡢ࡚ࡊࡘࡓࡊࡑࡑࠦᲩ")):
        return {
            bstack1ll111_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᲪ"): bstack1ll111_opy_ (u"ࠥࡘࡪࡧ࡭ࡤ࡫ࡷࡽࠧᲫ"),
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲬ"): None,
            bstack1ll111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᲭ"): env.get(bstack1ll111_opy_ (u"ࠨࡔࡆࡃࡐࡇࡎ࡚࡙ࡠࡒࡕࡓࡏࡋࡃࡕࡡࡑࡅࡒࡋࠢᲮ")),
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᲯ"): env.get(bstack1ll111_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᲰ"))
        }
    if any([env.get(bstack1ll111_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࠧᲱ")), env.get(bstack1ll111_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡕࡓࡎࠥᲲ")), env.get(bstack1ll111_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠤᲳ")), env.get(bstack1ll111_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡖࡈࡅࡒࠨᲴ"))]):
        return {
            bstack1ll111_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᲵ"): bstack1ll111_opy_ (u"ࠢࡄࡱࡱࡧࡴࡻࡲࡴࡧࠥᲶ"),
            bstack1ll111_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᲷ"): None,
            bstack1ll111_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᲸ"): env.get(bstack1ll111_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᲹ")) or None,
            bstack1ll111_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᲺ"): env.get(bstack1ll111_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢ᲻"), 0)
        }
    if env.get(bstack1ll111_opy_ (u"ࠨࡇࡐࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦ᲼")):
        return {
            bstack1ll111_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᲽ"): bstack1ll111_opy_ (u"ࠣࡉࡲࡇࡉࠨᲾ"),
            bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲿ"): None,
            bstack1ll111_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᳀"): env.get(bstack1ll111_opy_ (u"ࠦࡌࡕ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᳁")),
            bstack1ll111_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᳂"): env.get(bstack1ll111_opy_ (u"ࠨࡇࡐࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡈࡕࡕࡏࡖࡈࡖࠧ᳃"))
        }
    if env.get(bstack1ll111_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᳄")):
        return {
            bstack1ll111_opy_ (u"ࠣࡰࡤࡱࡪࠨ᳅"): bstack1ll111_opy_ (u"ࠤࡆࡳࡩ࡫ࡆࡳࡧࡶ࡬ࠧ᳆"),
            bstack1ll111_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᳇"): env.get(bstack1ll111_opy_ (u"ࠦࡈࡌ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥ᳈")),
            bstack1ll111_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᳉"): env.get(bstack1ll111_opy_ (u"ࠨࡃࡇࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡓࡇࡍࡆࠤ᳊")),
            bstack1ll111_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᳋"): env.get(bstack1ll111_opy_ (u"ࠣࡅࡉࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᳌"))
        }
    return {bstack1ll111_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᳍"): None}
def get_host_info():
    return {
        bstack1ll111_opy_ (u"ࠥ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠧ᳎"): platform.node(),
        bstack1ll111_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨ᳏"): platform.system(),
        bstack1ll111_opy_ (u"ࠧࡺࡹࡱࡧࠥ᳐"): platform.machine(),
        bstack1ll111_opy_ (u"ࠨࡶࡦࡴࡶ࡭ࡴࡴࠢ᳑"): platform.version(),
        bstack1ll111_opy_ (u"ࠢࡢࡴࡦ࡬ࠧ᳒"): platform.architecture()[0]
    }
def bstack1ll1l1l1ll_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack11l1111llll_opy_():
    if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩ᳓")):
        return bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨ᳔")
    return bstack1ll111_opy_ (u"ࠪࡹࡳࡱ࡮ࡰࡹࡱࡣ࡬ࡸࡩࡥ᳕ࠩ")
def bstack111l1lll11l_opy_(driver):
    info = {
        bstack1ll111_opy_ (u"ࠫࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵ᳖ࠪ"): driver.capabilities,
        bstack1ll111_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥ᳗ࠩ"): driver.session_id,
        bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ᳘ࠧ"): driver.capabilities.get(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩ᳙ࠬ"), None),
        bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪ᳚"): driver.capabilities.get(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ᳛"), None),
        bstack1ll111_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ᳜ࠬ"): driver.capabilities.get(bstack1ll111_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧ᳝ࠪ"), None),
        bstack1ll111_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᳞"):driver.capabilities.get(bstack1ll111_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ᳟"), None),
    }
    if bstack11l1111llll_opy_() == bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭᳠"):
        if bstack11l111l1_opy_():
            info[bstack1ll111_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩ᳡")] = bstack1ll111_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨ᳢")
        elif driver.capabilities.get(bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶ᳣ࠫ"), {}).get(bstack1ll111_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨ᳤"), False):
            info[bstack1ll111_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹ᳥࠭")] = bstack1ll111_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧ᳦ࠪ")
        else:
            info[bstack1ll111_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨ᳧")] = bstack1ll111_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵࡧ᳨ࠪ")
    return info
def bstack11l111l1_opy_():
    if bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠩࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠨᳩ")):
        return True
    if bstack1l1l1111l1_opy_(os.environ.get(bstack1ll111_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫᳪ"), None)):
        return True
    return False
def bstack1l1l111111_opy_(bstack111llll1lll_opy_, url, data, config):
    headers = config.get(bstack1ll111_opy_ (u"ࠫ࡭࡫ࡡࡥࡧࡵࡷࠬᳫ"), None)
    proxies = bstack1l1l1ll11l_opy_(config, url)
    auth = config.get(bstack1ll111_opy_ (u"ࠬࡧࡵࡵࡪࠪᳬ"), None)
    response = requests.request(
            bstack111llll1lll_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack11ll1ll1l_opy_(bstack1ll111l11l_opy_, size):
    bstack11ll1l1ll_opy_ = []
    while len(bstack1ll111l11l_opy_) > size:
        bstack111ll111_opy_ = bstack1ll111l11l_opy_[:size]
        bstack11ll1l1ll_opy_.append(bstack111ll111_opy_)
        bstack1ll111l11l_opy_ = bstack1ll111l11l_opy_[size:]
    bstack11ll1l1ll_opy_.append(bstack1ll111l11l_opy_)
    return bstack11ll1l1ll_opy_
def bstack11l111ll11l_opy_(message, bstack111ll1l1l11_opy_=False):
    os.write(1, bytes(message, bstack1ll111_opy_ (u"࠭ࡵࡵࡨ࠰࠼᳭ࠬ")))
    os.write(1, bytes(bstack1ll111_opy_ (u"ࠧ࡝ࡰࠪᳮ"), bstack1ll111_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᳯ")))
    if bstack111ll1l1l11_opy_:
        with open(bstack1ll111_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠯ࡲ࠵࠶ࡿ࠭ࠨᳰ") + os.environ[bstack1ll111_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩᳱ")] + bstack1ll111_opy_ (u"ࠫ࠳ࡲ࡯ࡨࠩᳲ"), bstack1ll111_opy_ (u"ࠬࡧࠧᳳ")) as f:
            f.write(message + bstack1ll111_opy_ (u"࠭࡜࡯ࠩ᳴"))
def bstack1l1l11l1l1l_opy_():
    return os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᳵ")].lower() == bstack1ll111_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᳶ")
def bstack11ll1l111_opy_():
    return bstack1111l1lll1_opy_().replace(tzinfo=None).isoformat() + bstack1ll111_opy_ (u"ࠩ࡝ࠫ᳷")
def bstack111ll1lll1l_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1ll111_opy_ (u"ࠪ࡞ࠬ᳸"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1ll111_opy_ (u"ࠫ࡟࠭᳹")))).total_seconds() * 1000
def bstack11l11l111l1_opy_(timestamp):
    return bstack11l1111ll11_opy_(timestamp).isoformat() + bstack1ll111_opy_ (u"ࠬࡠࠧᳺ")
def bstack11l11l11l1l_opy_(bstack111lll1l1ll_opy_):
    date_format = bstack1ll111_opy_ (u"࡚࠭ࠥࠧࡰࠩࡩࠦࠥࡉ࠼ࠨࡑ࠿ࠫࡓ࠯ࠧࡩࠫ᳻")
    bstack111ll11llll_opy_ = datetime.datetime.strptime(bstack111lll1l1ll_opy_, date_format)
    return bstack111ll11llll_opy_.isoformat() + bstack1ll111_opy_ (u"࡛ࠧࠩ᳼")
def bstack111lll1111l_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1ll111_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ᳽")
    else:
        return bstack1ll111_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩ᳾")
def bstack1l1l1111l1_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1ll111_opy_ (u"ࠪࡸࡷࡻࡥࠨ᳿")
def bstack111lll1l1l1_opy_(val):
    return val.__str__().lower() == bstack1ll111_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪᴀ")
def error_handler(bstack11l111lll1l_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11l111lll1l_opy_ as e:
                print(bstack1ll111_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡻࡾࠢ࠰ࡂࠥࢁࡽ࠻ࠢࡾࢁࠧᴁ").format(func.__name__, bstack11l111lll1l_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11l11l11ll1_opy_(bstack11l1111l11l_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11l1111l11l_opy_(cls, *args, **kwargs)
            except bstack11l111lll1l_opy_ as e:
                print(bstack1ll111_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨᴂ").format(bstack11l1111l11l_opy_.__name__, bstack11l111lll1l_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11l11l11ll1_opy_
    else:
        return decorator
def bstack1ll1l1111_opy_(bstack11111111l1_opy_):
    if os.getenv(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᴃ")) is not None:
        return bstack1l1l1111l1_opy_(os.getenv(bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫᴄ")))
    if bstack1ll111_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᴅ") in bstack11111111l1_opy_ and bstack111lll1l1l1_opy_(bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᴆ")]):
        return False
    if bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᴇ") in bstack11111111l1_opy_ and bstack111lll1l1l1_opy_(bstack11111111l1_opy_[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᴈ")]):
        return False
    return True
def bstack11l11l11l_opy_():
    try:
        from pytest_bdd import reporting
        bstack111ll1l1l1l_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࠨᴉ"), None)
        return bstack111ll1l1l1l_opy_ is None or bstack111ll1l1l1l_opy_ == bstack1ll111_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᴊ")
    except Exception as e:
        return False
def bstack111111lll_opy_(hub_url, CONFIG):
    if bstack111l111l_opy_() <= version.parse(bstack1ll111_opy_ (u"ࠨ࠵࠱࠵࠸࠴࠰ࠨᴋ")):
        if hub_url:
            return bstack1ll111_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᴌ") + hub_url + bstack1ll111_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢᴍ")
        return bstack1lll1ll111_opy_
    if hub_url:
        return bstack1ll111_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨᴎ") + hub_url + bstack1ll111_opy_ (u"ࠧ࠵ࡷࡥ࠱࡫ࡹࡧࠨᴏ")
    return bstack1ll1ll1ll_opy_
def bstack111l1lll111_opy_():
    return isinstance(os.getenv(bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖ࡙ࡕࡇࡖࡘࡤࡖࡌࡖࡉࡌࡒࠬᴐ")), str)
def bstack1ll1111l11_opy_(url):
    return urlparse(url).hostname
def bstack1l1lll111_opy_(hostname):
    for bstack1ll11l111l_opy_ in bstack1l1l1l1ll_opy_:
        regex = re.compile(bstack1ll11l111l_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l111llll1_opy_(bstack11l1111l1l1_opy_, file_name, logger):
    bstack11lllll1l_opy_ = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠧࡿࠩᴑ")), bstack11l1111l1l1_opy_)
    try:
        if not os.path.exists(bstack11lllll1l_opy_):
            os.makedirs(bstack11lllll1l_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠨࢀࠪᴒ")), bstack11l1111l1l1_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1ll111_opy_ (u"ࠩࡺࠫᴓ")):
                pass
            with open(file_path, bstack1ll111_opy_ (u"ࠥࡻ࠰ࠨᴔ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1lll11l1_opy_.format(str(e)))
def bstack111lll1ll1l_opy_(file_name, key, value, logger):
    file_path = bstack11l111llll1_opy_(bstack1ll111_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᴕ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack11lll11ll_opy_ = json.load(open(file_path, bstack1ll111_opy_ (u"ࠬࡸࡢࠨᴖ")))
        else:
            bstack11lll11ll_opy_ = {}
        bstack11lll11ll_opy_[key] = value
        with open(file_path, bstack1ll111_opy_ (u"ࠨࡷࠬࠤᴗ")) as outfile:
            json.dump(bstack11lll11ll_opy_, outfile)
def bstack1111ll1l_opy_(file_name, logger):
    file_path = bstack11l111llll1_opy_(bstack1ll111_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᴘ"), file_name, logger)
    bstack11lll11ll_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1ll111_opy_ (u"ࠨࡴࠪᴙ")) as bstack11111ll11_opy_:
            bstack11lll11ll_opy_ = json.load(bstack11111ll11_opy_)
    return bstack11lll11ll_opy_
def bstack11lll1l1_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡩ࡫࡬ࡦࡶ࡬ࡲ࡬ࠦࡦࡪ࡮ࡨ࠾ࠥ࠭ᴚ") + file_path + bstack1ll111_opy_ (u"ࠪࠤࠬᴛ") + str(e))
def bstack111l111l_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1ll111_opy_ (u"ࠦࡁࡔࡏࡕࡕࡈࡘࡃࠨᴜ")
def bstack11l1lll11l_opy_(config):
    if bstack1ll111_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫᴝ") in config:
        del (config[bstack1ll111_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬᴞ")])
        return False
    if bstack111l111l_opy_() < version.parse(bstack1ll111_opy_ (u"ࠧ࠴࠰࠷࠲࠵࠭ᴟ")):
        return False
    if bstack111l111l_opy_() >= version.parse(bstack1ll111_opy_ (u"ࠨ࠶࠱࠵࠳࠻ࠧᴠ")):
        return True
    if bstack1ll111_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩᴡ") in config and config[bstack1ll111_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪᴢ")] is False:
        return False
    else:
        return True
def bstack11ll111ll1_opy_(args_list, bstack111l1llll11_opy_):
    index = -1
    for value in bstack111l1llll11_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1111l1l_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1111l1l_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111ll11l1l_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111ll11l1l_opy_ = bstack111ll11l1l_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1ll111_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫᴣ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1ll111_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᴤ"), exception=exception)
    def bstack1llllll1l11_opy_(self):
        if self.result != bstack1ll111_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᴥ"):
            return None
        if isinstance(self.exception_type, str) and bstack1ll111_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᴦ") in self.exception_type:
            return bstack1ll111_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤᴧ")
        return bstack1ll111_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᴨ")
    def bstack111ll1l11l1_opy_(self):
        if self.result != bstack1ll111_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᴩ"):
            return None
        if self.bstack111ll11l1l_opy_:
            return self.bstack111ll11l1l_opy_
        return bstack111ll11l11l_opy_(self.exception)
def bstack111ll11l11l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack111llllll11_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack11111l1l1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1l111l1l1_opy_(config, logger):
    try:
        import playwright
        bstack111llll111l_opy_ = playwright.__file__
        bstack111ll1lllll_opy_ = os.path.split(bstack111llll111l_opy_)
        bstack111ll11l1ll_opy_ = bstack111ll1lllll_opy_[0] + bstack1ll111_opy_ (u"ࠫ࠴ࡪࡲࡪࡸࡨࡶ࠴ࡶࡡࡤ࡭ࡤ࡫ࡪ࠵࡬ࡪࡤ࠲ࡧࡱ࡯࠯ࡤ࡮࡬࠲࡯ࡹࠧᴪ")
        os.environ[bstack1ll111_opy_ (u"ࠬࡍࡌࡐࡄࡄࡐࡤࡇࡇࡆࡐࡗࡣࡍ࡚ࡔࡑࡡࡓࡖࡔ࡞࡙ࠨᴫ")] = bstack1ll1ll111l_opy_(config)
        with open(bstack111ll11l1ll_opy_, bstack1ll111_opy_ (u"࠭ࡲࠨᴬ")) as f:
            bstack1l1ll1l11_opy_ = f.read()
            bstack111lll1l11l_opy_ = bstack1ll111_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭ᴭ")
            bstack11l1111l111_opy_ = bstack1l1ll1l11_opy_.find(bstack111lll1l11l_opy_)
            if bstack11l1111l111_opy_ == -1:
              process = subprocess.Popen(bstack1ll111_opy_ (u"ࠣࡰࡳࡱࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡧ࡭ࡱࡥࡥࡱ࠳ࡡࡨࡧࡱࡸࠧᴮ"), shell=True, cwd=bstack111ll1lllll_opy_[0])
              process.wait()
              bstack111ll111lll_opy_ = bstack1ll111_opy_ (u"ࠩࠥࡹࡸ࡫ࠠࡴࡶࡵ࡭ࡨࡺࠢ࠼ࠩᴯ")
              bstack11l1111l1ll_opy_ = bstack1ll111_opy_ (u"ࠥࠦࠧࠦ࡜ࠣࡷࡶࡩࠥࡹࡴࡳ࡫ࡦࡸࡡࠨ࠻ࠡࡥࡲࡲࡸࡺࠠࡼࠢࡥࡳࡴࡺࡳࡵࡴࡤࡴࠥࢃࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠫ࡬ࡲ࡯ࡣࡣ࡯࠱ࡦ࡭ࡥ࡯ࡶࠪ࠭ࡀࠦࡩࡧࠢࠫࡴࡷࡵࡣࡦࡵࡶ࠲ࡪࡴࡶ࠯ࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜࠭ࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠩࠫ࠾ࠤࠧࠨࠢᴰ")
              bstack111ll111l1l_opy_ = bstack1l1ll1l11_opy_.replace(bstack111ll111lll_opy_, bstack11l1111l1ll_opy_)
              with open(bstack111ll11l1ll_opy_, bstack1ll111_opy_ (u"ࠫࡼ࠭ᴱ")) as f:
                f.write(bstack111ll111l1l_opy_)
    except Exception as e:
        logger.error(bstack1l111ll1_opy_.format(str(e)))
def bstack1ll1l11ll_opy_():
  try:
    bstack11l1111ll1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠬࡵࡰࡵ࡫ࡰࡥࡱࡥࡨࡶࡤࡢࡹࡷࡲ࠮࡫ࡵࡲࡲࠬᴲ"))
    bstack111lll1ll11_opy_ = []
    if os.path.exists(bstack11l1111ll1l_opy_):
      with open(bstack11l1111ll1l_opy_) as f:
        bstack111lll1ll11_opy_ = json.load(f)
      os.remove(bstack11l1111ll1l_opy_)
    return bstack111lll1ll11_opy_
  except:
    pass
  return []
def bstack1lll11l1l_opy_(bstack1lll11l11_opy_):
  try:
    bstack111lll1ll11_opy_ = []
    bstack11l1111ll1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ࠭ᴳ"))
    if os.path.exists(bstack11l1111ll1l_opy_):
      with open(bstack11l1111ll1l_opy_) as f:
        bstack111lll1ll11_opy_ = json.load(f)
    bstack111lll1ll11_opy_.append(bstack1lll11l11_opy_)
    with open(bstack11l1111ll1l_opy_, bstack1ll111_opy_ (u"ࠧࡸࠩᴴ")) as f:
        json.dump(bstack111lll1ll11_opy_, f)
  except:
    pass
def bstack1ll1111lll_opy_(logger, bstack11l111l111l_opy_ = False):
  try:
    test_name = os.environ.get(bstack1ll111_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫᴵ"), bstack1ll111_opy_ (u"ࠩࠪᴶ"))
    if test_name == bstack1ll111_opy_ (u"ࠪࠫᴷ"):
        test_name = threading.current_thread().__dict__.get(bstack1ll111_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡆࡩࡪ࡟ࡵࡧࡶࡸࡤࡴࡡ࡮ࡧࠪᴸ"), bstack1ll111_opy_ (u"ࠬ࠭ᴹ"))
    bstack111l1lll1ll_opy_ = bstack1ll111_opy_ (u"࠭ࠬࠡࠩᴺ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack11l111l111l_opy_:
        bstack1lll1l1l_opy_ = os.environ.get(bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᴻ"), bstack1ll111_opy_ (u"ࠨ࠲ࠪᴼ"))
        bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᴽ"): test_name, bstack1ll111_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᴾ"): bstack111l1lll1ll_opy_, bstack1ll111_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪᴿ"): bstack1lll1l1l_opy_}
        bstack11l111ll1ll_opy_ = []
        bstack11l11111ll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡶࡰࡱࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫᵀ"))
        if os.path.exists(bstack11l11111ll1_opy_):
            with open(bstack11l11111ll1_opy_) as f:
                bstack11l111ll1ll_opy_ = json.load(f)
        bstack11l111ll1ll_opy_.append(bstack1l1ll11l11_opy_)
        with open(bstack11l11111ll1_opy_, bstack1ll111_opy_ (u"࠭ࡷࠨᵁ")) as f:
            json.dump(bstack11l111ll1ll_opy_, f)
    else:
        bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᵂ"): test_name, bstack1ll111_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᵃ"): bstack111l1lll1ll_opy_, bstack1ll111_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᵄ"): str(multiprocessing.current_process().name)}
        if bstack1ll111_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺࠧᵅ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l1ll11l11_opy_)
  except Exception as e:
      logger.warn(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡰࡺࡶࡨࡷࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠣᵆ").format(e))
def bstack1l1l111l11_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1ll111_opy_ (u"ࠬ࡬ࡩ࡭ࡧ࡯ࡳࡨࡱࠠ࡯ࡱࡷࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡷࡶ࡭ࡳ࡭ࠠࡣࡣࡶ࡭ࡨࠦࡦࡪ࡮ࡨࠤࡴࡶࡥࡳࡣࡷ࡭ࡴࡴࡳࠨᵇ"))
    try:
      bstack111llll1ll1_opy_ = []
      bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᵈ"): test_name, bstack1ll111_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᵉ"): error_message, bstack1ll111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᵊ"): index}
      bstack111l1lllll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᵋ"))
      if os.path.exists(bstack111l1lllll1_opy_):
          with open(bstack111l1lllll1_opy_) as f:
              bstack111llll1ll1_opy_ = json.load(f)
      bstack111llll1ll1_opy_.append(bstack1l1ll11l11_opy_)
      with open(bstack111l1lllll1_opy_, bstack1ll111_opy_ (u"ࠪࡻࠬᵌ")) as f:
          json.dump(bstack111llll1ll1_opy_, f)
    except Exception as e:
      logger.warn(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡲࡰࡤࡲࡸࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᵍ").format(e))
    return
  bstack111llll1ll1_opy_ = []
  bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᵎ"): test_name, bstack1ll111_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᵏ"): error_message, bstack1ll111_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᵐ"): index}
  bstack111l1lllll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll111_opy_ (u"ࠨࡴࡲࡦࡴࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩᵑ"))
  lock_file = bstack111l1lllll1_opy_ + bstack1ll111_opy_ (u"ࠩ࠱ࡰࡴࡩ࡫ࠨᵒ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111l1lllll1_opy_):
          with open(bstack111l1lllll1_opy_, bstack1ll111_opy_ (u"ࠪࡶࠬᵓ")) as f:
              content = f.read().strip()
              if content:
                  bstack111llll1ll1_opy_ = json.load(open(bstack111l1lllll1_opy_))
      bstack111llll1ll1_opy_.append(bstack1l1ll11l11_opy_)
      with open(bstack111l1lllll1_opy_, bstack1ll111_opy_ (u"ࠫࡼ࠭ᵔ")) as f:
          json.dump(bstack111llll1ll1_opy_, f)
  except Exception as e:
    logger.warn(bstack1ll111_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡳࡱࡥࡳࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡩ࡭ࡱ࡫ࠠ࡭ࡱࡦ࡯࡮ࡴࡧ࠻ࠢࡾࢁࠧᵕ").format(e))
def bstack11l11l1111_opy_(bstack1ll1lll1_opy_, name, logger):
  try:
    bstack1l1ll11l11_opy_ = {bstack1ll111_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᵖ"): name, bstack1ll111_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᵗ"): bstack1ll1lll1_opy_, bstack1ll111_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᵘ"): str(threading.current_thread()._name)}
    return bstack1l1ll11l11_opy_
  except Exception as e:
    logger.warn(bstack1ll111_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡰࡴࡨࠤࡧ࡫ࡨࡢࡸࡨࠤ࡫ࡻ࡮࡯ࡧ࡯ࠤࡩࡧࡴࡢ࠼ࠣࡿࢂࠨᵙ").format(e))
  return
def bstack111ll1l1lll_opy_():
    return platform.system() == bstack1ll111_opy_ (u"࡛ࠪ࡮ࡴࡤࡰࡹࡶࠫᵚ")
def bstack111llll11_opy_(bstack111lll1lll1_opy_, config, logger):
    bstack111lll11111_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111lll1lll1_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡧ࡫࡯ࡸࡪࡸࠠࡤࡱࡱࡪ࡮࡭ࠠ࡬ࡧࡼࡷࠥࡨࡹࠡࡴࡨ࡫ࡪࡾࠠ࡮ࡣࡷࡧ࡭ࡀࠠࡼࡿࠥᵛ").format(e))
    return bstack111lll11111_opy_
def bstack111ll11l111_opy_(bstack11l11111lll_opy_, bstack111ll11lll1_opy_):
    bstack111ll1lll11_opy_ = version.parse(bstack11l11111lll_opy_)
    bstack111llllllll_opy_ = version.parse(bstack111ll11lll1_opy_)
    if bstack111ll1lll11_opy_ > bstack111llllllll_opy_:
        return 1
    elif bstack111ll1lll11_opy_ < bstack111llllllll_opy_:
        return -1
    else:
        return 0
def bstack1111l1lll1_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11l1111ll11_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll111111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1l1l1ll1ll_opy_(options, framework, config, bstack1l11l111ll_opy_={}):
    if options is None:
        return
    if getattr(options, bstack1ll111_opy_ (u"ࠬ࡭ࡥࡵࠩᵜ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack11lll1l11l_opy_ = caps.get(bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᵝ"))
    bstack11l111l11l1_opy_ = True
    bstack1llll1l1l1_opy_ = os.environ[bstack1ll111_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᵞ")]
    bstack1ll111llll1_opy_ = config.get(bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᵟ"), False)
    if bstack1ll111llll1_opy_:
        bstack1ll1l1llll1_opy_ = config.get(bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᵠ"), {})
        bstack1ll1l1llll1_opy_[bstack1ll111_opy_ (u"ࠪࡥࡺࡺࡨࡕࡱ࡮ࡩࡳ࠭ᵡ")] = os.getenv(bstack1ll111_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᵢ"))
        bstack11ll111llll_opy_ = json.loads(os.getenv(bstack1ll111_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ᵣ"), bstack1ll111_opy_ (u"࠭ࡻࡾࠩᵤ"))).get(bstack1ll111_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᵥ"))
    if bstack111lll1l1l1_opy_(caps.get(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡶࡵࡨ࡛࠸ࡉࠧᵦ"))) or bstack111lll1l1l1_opy_(caps.get(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩࡤࡽ࠳ࡤࠩᵧ"))):
        bstack11l111l11l1_opy_ = False
    if bstack11l1lll11l_opy_({bstack1ll111_opy_ (u"ࠥࡹࡸ࡫ࡗ࠴ࡅࠥᵨ"): bstack11l111l11l1_opy_}):
        bstack11lll1l11l_opy_ = bstack11lll1l11l_opy_ or {}
        bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ᵩ")] = bstack111ll111111_opy_(framework)
        bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᵪ")] = bstack1l1l11l1l1l_opy_()
        bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᵫ")] = bstack1llll1l1l1_opy_
        bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩᵬ")] = bstack1l11l111ll_opy_
        if bstack1ll111llll1_opy_:
            bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᵭ")] = bstack1ll111llll1_opy_
            bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᵮ")] = bstack1ll1l1llll1_opy_
            bstack11lll1l11l_opy_[bstack1ll111_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᵯ")][bstack1ll111_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᵰ")] = bstack11ll111llll_opy_
        if getattr(options, bstack1ll111_opy_ (u"ࠬࡹࡥࡵࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸࡾ࠭ᵱ"), None):
            options.set_capability(bstack1ll111_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᵲ"), bstack11lll1l11l_opy_)
        else:
            options[bstack1ll111_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᵳ")] = bstack11lll1l11l_opy_
    else:
        if getattr(options, bstack1ll111_opy_ (u"ࠨࡵࡨࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡺࠩᵴ"), None):
            options.set_capability(bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᵵ"), bstack111ll111111_opy_(framework))
            options.set_capability(bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᵶ"), bstack1l1l11l1l1l_opy_())
            options.set_capability(bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᵷ"), bstack1llll1l1l1_opy_)
            options.set_capability(bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᵸ"), bstack1l11l111ll_opy_)
            if bstack1ll111llll1_opy_:
                options.set_capability(bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᵹ"), bstack1ll111llll1_opy_)
                options.set_capability(bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᵺ"), bstack1ll1l1llll1_opy_)
                options.set_capability(bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹ࠮ࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᵻ"), bstack11ll111llll_opy_)
        else:
            options[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᵼ")] = bstack111ll111111_opy_(framework)
            options[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᵽ")] = bstack1l1l11l1l1l_opy_()
            options[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᵾ")] = bstack1llll1l1l1_opy_
            options[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᵿ")] = bstack1l11l111ll_opy_
            if bstack1ll111llll1_opy_:
                options[bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᶀ")] = bstack1ll111llll1_opy_
                options[bstack1ll111_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᶁ")] = bstack1ll1l1llll1_opy_
                options[bstack1ll111_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᶂ")][bstack1ll111_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᶃ")] = bstack11ll111llll_opy_
    return options
def bstack111ll1l11ll_opy_(bstack111ll1ll1ll_opy_, framework):
    bstack1l11l111ll_opy_ = bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠥࡔࡑࡇ࡙ࡘࡔࡌࡋࡍ࡚࡟ࡑࡔࡒࡈ࡚ࡉࡔࡠࡏࡄࡔࠧᶄ"))
    if bstack111ll1ll1ll_opy_ and len(bstack111ll1ll1ll_opy_.split(bstack1ll111_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᶅ"))) > 1:
        ws_url = bstack111ll1ll1ll_opy_.split(bstack1ll111_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᶆ"))[0]
        if bstack1ll111_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩᶇ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack11l11111l11_opy_ = json.loads(urllib.parse.unquote(bstack111ll1ll1ll_opy_.split(bstack1ll111_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᶈ"))[1]))
            bstack11l11111l11_opy_ = bstack11l11111l11_opy_ or {}
            bstack1llll1l1l1_opy_ = os.environ[bstack1ll111_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᶉ")]
            bstack11l11111l11_opy_[bstack1ll111_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪᶊ")] = str(framework) + str(__version__)
            bstack11l11111l11_opy_[bstack1ll111_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᶋ")] = bstack1l1l11l1l1l_opy_()
            bstack11l11111l11_opy_[bstack1ll111_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᶌ")] = bstack1llll1l1l1_opy_
            bstack11l11111l11_opy_[bstack1ll111_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ᶍ")] = bstack1l11l111ll_opy_
            bstack111ll1ll1ll_opy_ = bstack111ll1ll1ll_opy_.split(bstack1ll111_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᶎ"))[0] + bstack1ll111_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᶏ") + urllib.parse.quote(json.dumps(bstack11l11111l11_opy_))
    return bstack111ll1ll1ll_opy_
def bstack1ll1l11l_opy_():
    global bstack1lll11l1l1_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1lll11l1l1_opy_ = BrowserType.connect
    return bstack1lll11l1l1_opy_
def bstack11l11llll1_opy_(framework_name):
    global bstack1ll11lllll_opy_
    bstack1ll11lllll_opy_ = framework_name
    return framework_name
def bstack1ll111l1l_opy_(self, *args, **kwargs):
    global bstack1lll11l1l1_opy_
    try:
        global bstack1ll11lllll_opy_
        if bstack1ll111_opy_ (u"ࠨࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸࠬᶐ") in kwargs:
            kwargs[bstack1ll111_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭ᶑ")] = bstack111ll1l11ll_opy_(
                kwargs.get(bstack1ll111_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᶒ"), None),
                bstack1ll11lllll_opy_
            )
    except Exception as e:
        logger.error(bstack1ll111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡫࡮ࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫࡙ࠥࡄࡌࠢࡦࡥࡵࡹ࠺ࠡࡽࢀࠦᶓ").format(str(e)))
    return bstack1lll11l1l1_opy_(self, *args, **kwargs)
def bstack111llllll1l_opy_(bstack111lll1l111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1l1l1ll11l_opy_(bstack111lll1l111_opy_, bstack1ll111_opy_ (u"ࠧࠨᶔ"))
        if proxies and proxies.get(bstack1ll111_opy_ (u"ࠨࡨࡵࡶࡳࡷࠧᶕ")):
            parsed_url = urlparse(proxies.get(bstack1ll111_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᶖ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1ll111_opy_ (u"ࠨࡲࡵࡳࡽࡿࡈࡰࡵࡷࠫᶗ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1ll111_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡱࡵࡸࠬᶘ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1ll111_opy_ (u"ࠪࡴࡷࡵࡸࡺࡗࡶࡩࡷ࠭ᶙ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1ll111_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧᶚ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11lll11lll_opy_(bstack111lll1l111_opy_):
    bstack11l111lllll_opy_ = {
        bstack11l1l111ll1_opy_[bstack111lll1llll_opy_]: bstack111lll1l111_opy_[bstack111lll1llll_opy_]
        for bstack111lll1llll_opy_ in bstack111lll1l111_opy_
        if bstack111lll1llll_opy_ in bstack11l1l111ll1_opy_
    }
    bstack11l111lllll_opy_[bstack1ll111_opy_ (u"ࠧࡶࡲࡰࡺࡼࡗࡪࡺࡴࡪࡰࡪࡷࠧᶛ")] = bstack111llllll1l_opy_(bstack111lll1l111_opy_, bstack11ll11l11l_opy_.get_property(bstack1ll111_opy_ (u"ࠨࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࠨᶜ")))
    bstack111l1lll1l1_opy_ = [element.lower() for element in bstack11l1l111l1l_opy_]
    bstack111l1llll1l_opy_(bstack11l111lllll_opy_, bstack111l1lll1l1_opy_)
    return bstack11l111lllll_opy_
def bstack111l1llll1l_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1ll111_opy_ (u"ࠢࠫࠬ࠭࠮ࠧᶝ")
    for value in d.values():
        if isinstance(value, dict):
            bstack111l1llll1l_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack111l1llll1l_opy_(item, keys)
def bstack1l1ll11l1ll_opy_():
    bstack111lll111ll_opy_ = [os.environ.get(bstack1ll111_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡋࡏࡉࡘࡥࡄࡊࡔࠥᶞ")), os.path.join(os.path.expanduser(bstack1ll111_opy_ (u"ࠤࢁࠦᶟ")), bstack1ll111_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᶠ")), os.path.join(bstack1ll111_opy_ (u"ࠫ࠴ࡺ࡭ࡱࠩᶡ"), bstack1ll111_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬᶢ"))]
    for path in bstack111lll111ll_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack1ll111_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࠬࠨᶣ") + str(path) + bstack1ll111_opy_ (u"ࠢࠨࠢࡨࡼ࡮ࡹࡴࡴ࠰ࠥᶤ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack1ll111_opy_ (u"ࠣࡉ࡬ࡺ࡮ࡴࡧࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲࡸࠦࡦࡰࡴࠣࠫࠧᶥ") + str(path) + bstack1ll111_opy_ (u"ࠤࠪࠦᶦ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack1ll111_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࠩࠥᶧ") + str(path) + bstack1ll111_opy_ (u"ࠦࠬࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡩࡣࡶࠤࡹ࡮ࡥࠡࡴࡨࡵࡺ࡯ࡲࡦࡦࠣࡴࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳ࠯ࠤᶨ"))
            else:
                logger.debug(bstack1ll111_opy_ (u"ࠧࡉࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩࠥ࠭ࠢᶩ") + str(path) + bstack1ll111_opy_ (u"ࠨࠧࠡࡹ࡬ࡸ࡭ࠦࡷࡳ࡫ࡷࡩࠥࡶࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯࠰ࠥᶪ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack1ll111_opy_ (u"ࠢࡐࡲࡨࡶࡦࡺࡩࡰࡰࠣࡷࡺࡩࡣࡦࡧࡧࡩࡩࠦࡦࡰࡴࠣࠫࠧᶫ") + str(path) + bstack1ll111_opy_ (u"ࠣࠩ࠱ࠦᶬ"))
            return path
        except Exception as e:
            logger.debug(bstack1ll111_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡸࡴࠥ࡬ࡩ࡭ࡧࠣࠫࢀࡶࡡࡵࡪࢀࠫ࠿ࠦࠢᶭ") + str(e) + bstack1ll111_opy_ (u"ࠥࠦᶮ"))
    logger.debug(bstack1ll111_opy_ (u"ࠦࡆࡲ࡬ࠡࡲࡤࡸ࡭ࡹࠠࡧࡣ࡬ࡰࡪࡪ࠮ࠣᶯ"))
    return None
@measure(event_name=EVENTS.bstack11l11llllll_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack1lll11l1ll1_opy_(binary_path, bstack1ll1l1l111l_opy_, bs_config):
    logger.debug(bstack1ll111_opy_ (u"ࠧࡉࡵࡳࡴࡨࡲࡹࠦࡃࡍࡋࠣࡔࡦࡺࡨࠡࡨࡲࡹࡳࡪ࠺ࠡࡽࢀࠦᶰ").format(binary_path))
    bstack111ll1l1111_opy_ = bstack1ll111_opy_ (u"࠭ࠧᶱ")
    bstack111ll1l1ll1_opy_ = {
        bstack1ll111_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᶲ"): __version__,
        bstack1ll111_opy_ (u"ࠣࡱࡶࠦᶳ"): platform.system(),
        bstack1ll111_opy_ (u"ࠤࡲࡷࡤࡧࡲࡤࡪࠥᶴ"): platform.machine(),
        bstack1ll111_opy_ (u"ࠥࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠣᶵ"): bstack1ll111_opy_ (u"ࠫ࠵࠭ᶶ"),
        bstack1ll111_opy_ (u"ࠧࡹࡤ࡬ࡡ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠦᶷ"): bstack1ll111_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ᶸ")
    }
    bstack11l11111l1l_opy_(bstack111ll1l1ll1_opy_)
    try:
        if binary_path:
            if bstack111ll1l1lll_opy_():
                bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"ࠧࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᶹ")] = subprocess.check_output([binary_path, bstack1ll111_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤᶺ")]).strip().decode(bstack1ll111_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᶻ"))
            else:
                bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"ࠪࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨᶼ")] = subprocess.check_output([binary_path, bstack1ll111_opy_ (u"ࠦࡻ࡫ࡲࡴ࡫ࡲࡲࠧᶽ")], stderr=subprocess.DEVNULL).strip().decode(bstack1ll111_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᶾ"))
        response = requests.request(
            bstack1ll111_opy_ (u"࠭ࡇࡆࡖࠪᶿ"),
            url=bstack1lll1ll1l1_opy_(bstack11l1l1111l1_opy_),
            headers=None,
            auth=(bs_config[bstack1ll111_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ᷀")], bs_config[bstack1ll111_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ᷁")]),
            json=None,
            params=bstack111ll1l1ll1_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack1ll111_opy_ (u"ࠩࡸࡶࡱ᷂࠭") in data.keys() and bstack1ll111_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡧࡣࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ᷃") in data.keys():
            logger.debug(bstack1ll111_opy_ (u"ࠦࡓ࡫ࡥࡥࠢࡷࡳࠥࡻࡰࡥࡣࡷࡩࠥࡨࡩ࡯ࡣࡵࡽ࠱ࠦࡣࡶࡴࡵࡩࡳࡺࠠࡣ࡫ࡱࡥࡷࡿࠠࡷࡧࡵࡷ࡮ࡵ࡮࠻ࠢࡾࢁࠧ᷄").format(bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"ࠬࡩ࡬ࡪࡡࡹࡩࡷࡹࡩࡰࡰࠪ᷅")]))
            if bstack1ll111_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤ࡛ࡒࡍࠩ᷆") in os.environ:
                logger.debug(bstack1ll111_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡥ࡭ࡳࡧࡲࡺࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡦࡹࠠࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡕࡓࡎࠣ࡭ࡸࠦࡳࡦࡶࠥ᷇"))
                data[bstack1ll111_opy_ (u"ࠨࡷࡵࡰࠬ᷈")] = os.environ[bstack1ll111_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡗࡕࡐࠬ᷉")]
            bstack111l1ll1l11_opy_ = bstack111lllllll1_opy_(data[bstack1ll111_opy_ (u"ࠪࡹࡷࡲ᷊ࠧ")], bstack1ll1l1l111l_opy_)
            bstack111ll1l1111_opy_ = os.path.join(bstack1ll1l1l111l_opy_, bstack111l1ll1l11_opy_)
            os.chmod(bstack111ll1l1111_opy_, 0o777) # bstack111l1ll1l1l_opy_ permission
            return bstack111ll1l1111_opy_
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠ࡯ࡧࡺࠤࡘࡊࡋࠡࡽࢀࠦ᷋").format(e))
    return binary_path
def bstack11l11111l1l_opy_(bstack111ll1l1ll1_opy_):
    try:
        if bstack1ll111_opy_ (u"ࠬࡲࡩ࡯ࡷࡻࠫ᷌") not in bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"࠭࡯ࡴࠩ᷍")].lower():
            return
        if os.path.exists(bstack1ll111_opy_ (u"ࠢ࠰ࡧࡷࡧ࠴ࡵࡳ࠮ࡴࡨࡰࡪࡧࡳࡦࠤ᷎")):
            with open(bstack1ll111_opy_ (u"ࠣ࠱ࡨࡸࡨ࠵࡯ࡴ࠯ࡵࡩࡱ࡫ࡡࡴࡧ᷏ࠥ"), bstack1ll111_opy_ (u"ࠤࡵ᷐ࠦ")) as f:
                bstack111ll1ll1l1_opy_ = {}
                for line in f:
                    if bstack1ll111_opy_ (u"ࠥࡁࠧ᷑") in line:
                        key, value = line.rstrip().split(bstack1ll111_opy_ (u"ࠦࡂࠨ᷒"), 1)
                        bstack111ll1ll1l1_opy_[key] = value.strip(bstack1ll111_opy_ (u"ࠬࠨ࡜ࠨࠩᷓ"))
                bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"࠭ࡤࡪࡵࡷࡶࡴ࠭ᷔ")] = bstack111ll1ll1l1_opy_.get(bstack1ll111_opy_ (u"ࠢࡊࡆࠥᷕ"), bstack1ll111_opy_ (u"ࠣࠤᷖ"))
        elif os.path.exists(bstack1ll111_opy_ (u"ࠤ࠲ࡩࡹࡩ࠯ࡢ࡮ࡳ࡭ࡳ࡫࠭ࡳࡧ࡯ࡩࡦࡹࡥࠣᷗ")):
            bstack111ll1l1ll1_opy_[bstack1ll111_opy_ (u"ࠪࡨ࡮ࡹࡴࡳࡱࠪᷘ")] = bstack1ll111_opy_ (u"ࠫࡦࡲࡰࡪࡰࡨࠫᷙ")
    except Exception as e:
        logger.debug(bstack1ll111_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡩࡨࡸࠥࡪࡩࡴࡶࡵࡳࠥࡵࡦࠡ࡮࡬ࡲࡺࡾࠢᷚ") + e)
@measure(event_name=EVENTS.bstack11l1l1l1l11_opy_, stage=STAGE.bstack11ll1lll1_opy_)
def bstack111lllllll1_opy_(bstack111l1ll1lll_opy_, bstack11l111ll111_opy_):
    logger.debug(bstack1ll111_opy_ (u"ࠨࡄࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡘࡊࡋࠡࡤ࡬ࡲࡦࡸࡹࠡࡨࡵࡳࡲࡀࠠࠣᷛ") + str(bstack111l1ll1lll_opy_) + bstack1ll111_opy_ (u"ࠢࠣᷜ"))
    zip_path = os.path.join(bstack11l111ll111_opy_, bstack1ll111_opy_ (u"ࠣࡦࡲࡻࡳࡲ࡯ࡢࡦࡨࡨࡤ࡬ࡩ࡭ࡧ࠱ࡾ࡮ࡶࠢᷝ"))
    bstack111l1ll1l11_opy_ = bstack1ll111_opy_ (u"ࠩࠪᷞ")
    with requests.get(bstack111l1ll1lll_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack1ll111_opy_ (u"ࠥࡻࡧࠨᷟ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack1ll111_opy_ (u"ࠦࡋ࡯࡬ࡦࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽ࠳ࠨᷠ"))
    with zipfile.ZipFile(zip_path, bstack1ll111_opy_ (u"ࠬࡸࠧᷡ")) as zip_ref:
        bstack11l11l1111l_opy_ = zip_ref.namelist()
        if len(bstack11l11l1111l_opy_) > 0:
            bstack111l1ll1l11_opy_ = bstack11l11l1111l_opy_[0] # bstack111ll1l111l_opy_ bstack11l1l1lllll_opy_ will be bstack111l1llllll_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11l111ll111_opy_)
        logger.debug(bstack1ll111_opy_ (u"ࠨࡆࡪ࡮ࡨࡷࠥࡹࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭࡮ࡼࠤࡪࡾࡴࡳࡣࡦࡸࡪࡪࠠࡵࡱࠣࠫࠧᷢ") + str(bstack11l111ll111_opy_) + bstack1ll111_opy_ (u"ࠢࠨࠤᷣ"))
    os.remove(zip_path)
    return bstack111l1ll1l11_opy_
def get_cli_dir():
    bstack111ll11ll11_opy_ = bstack1l1ll11l1ll_opy_()
    if bstack111ll11ll11_opy_:
        bstack1ll1l1l111l_opy_ = os.path.join(bstack111ll11ll11_opy_, bstack1ll111_opy_ (u"ࠣࡥ࡯࡭ࠧᷤ"))
        if not os.path.exists(bstack1ll1l1l111l_opy_):
            os.makedirs(bstack1ll1l1l111l_opy_, mode=0o777, exist_ok=True)
        return bstack1ll1l1l111l_opy_
    else:
        raise FileNotFoundError(bstack1ll111_opy_ (u"ࠤࡑࡳࠥࡽࡲࡪࡶࡤࡦࡱ࡫ࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡥࡻࡧࡩ࡭ࡣࡥࡰࡪࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡔࡆࡎࠤࡧ࡯࡮ࡢࡴࡼ࠲ࠧᷥ"))
def bstack1lll111111l_opy_(bstack1ll1l1l111l_opy_):
    bstack1ll111_opy_ (u"ࠥࠦࠧࡍࡥࡵࠢࡷ࡬ࡪࠦࡰࡢࡶ࡫ࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡘࡊࡋࠡࡤ࡬ࡲࡦࡸࡹࠡ࡫ࡱࠤࡦࠦࡷࡳ࡫ࡷࡥࡧࡲࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼ࠲ࠧࠨࠢᷦ")
    bstack111ll11l1l1_opy_ = [
        os.path.join(bstack1ll1l1l111l_opy_, f)
        for f in os.listdir(bstack1ll1l1l111l_opy_)
        if os.path.isfile(os.path.join(bstack1ll1l1l111l_opy_, f)) and f.startswith(bstack1ll111_opy_ (u"ࠦࡧ࡯࡮ࡢࡴࡼ࠱ࠧᷧ"))
    ]
    if len(bstack111ll11l1l1_opy_) > 0:
        return max(bstack111ll11l1l1_opy_, key=os.path.getmtime) # get bstack111llll1l1l_opy_ binary
    return bstack1ll111_opy_ (u"ࠧࠨᷨ")
def bstack11ll111l11l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l1llllllll_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1l1llllllll_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1l111l1l1l_opy_(data, keys, default=None):
    bstack1ll111_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡓࡢࡨࡨࡰࡾࠦࡧࡦࡶࠣࡥࠥࡴࡥࡴࡶࡨࡨࠥࡼࡡ࡭ࡷࡨࠤ࡫ࡸ࡯࡮ࠢࡤࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹࠡࡱࡵࠤࡱ࡯ࡳࡵ࠰ࠍࠤࠥࠦࠠ࠻ࡲࡤࡶࡦࡳࠠࡥࡣࡷࡥ࠿ࠦࡔࡩࡧࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡰࡴࠣࡰ࡮ࡹࡴࠡࡶࡲࠤࡹࡸࡡࡷࡧࡵࡷࡪ࠴ࠊࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡰ࡫ࡹࡴ࠼ࠣࡅࠥࡲࡩࡴࡶࠣࡳ࡫ࠦ࡫ࡦࡻࡶ࠳࡮ࡴࡤࡪࡥࡨࡷࠥࡸࡥࡱࡴࡨࡷࡪࡴࡴࡪࡰࡪࠤࡹ࡮ࡥࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡩ࡫ࡦࡢࡷ࡯ࡸ࠿ࠦࡖࡢ࡮ࡸࡩࠥࡺ࡯ࠡࡴࡨࡸࡺࡸ࡮ࠡ࡫ࡩࠤࡹ࡮ࡥࠡࡲࡤࡸ࡭ࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺ࠮ࠋࠢࠣࠤࠥࡀࡲࡦࡶࡸࡶࡳࡀࠠࡕࡪࡨࠤࡻࡧ࡬ࡶࡧࠣࡥࡹࠦࡴࡩࡧࠣࡲࡪࡹࡴࡦࡦࠣࡴࡦࡺࡨ࠭ࠢࡲࡶࠥࡪࡥࡧࡣࡸࡰࡹࠦࡩࡧࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᷩ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default
def bstack11ll1l11ll_opy_(bstack11l111ll1l1_opy_, key, value):
    bstack1ll111_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡔࡶࡲࡶࡪࠦࡃࡍࡋࠣࡩࡳࡼࡩࡳࡱࡱࡱࡪࡴࡴࠡࡸࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠤࡲࡧࡰࡱ࡫ࡱ࡫ࠥ࡯࡮ࠡࡶ࡫ࡩࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼ࠲ࠏࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡦࡰ࡮ࡥࡥ࡯ࡸࡢࡺࡦࡸࡳࡠ࡯ࡤࡴ࠿ࠦࡄࡪࡥࡷ࡭ࡴࡴࡡࡳࡻࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥ࡫࡮ࡷ࡫ࡵࡳࡳࡳࡥ࡯ࡶࠣࡺࡦࡸࡩࡢࡤ࡯ࡩࠥࡳࡡࡱࡲ࡬ࡲ࡬ࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡ࡭ࡨࡽ࠿ࠦࡋࡦࡻࠣࡪࡷࡵ࡭ࠡࡅࡏࡍࡤࡉࡁࡑࡕࡢࡘࡔࡥࡃࡐࡐࡉࡍࡌࠐࠠࠡࠢࠣࠤࠥࠦࠠࡷࡣ࡯ࡹࡪࡀࠠࡗࡣ࡯ࡹࡪࠦࡦࡳࡱࡰࠤࡨࡵ࡭࡮ࡣࡱࡨࠥࡲࡩ࡯ࡧࠣࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠐࠠࠡࠢࠣࠦࠧࠨᷪ")
    if key in bstack1ll1l1ll1l_opy_:
        bstack1l1ll1l11l_opy_ = bstack1ll1l1ll1l_opy_[key]
        if isinstance(bstack1l1ll1l11l_opy_, list):
            for env_name in bstack1l1ll1l11l_opy_:
                bstack11l111ll1l1_opy_[env_name] = value
        else:
            bstack11l111ll1l1_opy_[bstack1l1ll1l11l_opy_] = value