from bdgs.algorithms.adithya_rajesh.adithya_rajesh import AdithyaRajesh
from bdgs.algorithms.chang_chen.chang_chen import ChangChen
from bdgs.algorithms.eid_schwenker.eid_schwenker import EidSchwenker
from bdgs.algorithms.gupta_jaafar.gupta_jaafar import GuptaJaafar
from bdgs.algorithms.islam_hossain_andersson.islam_hossain_andersson import IslamHossainAndersson
from bdgs.algorithms.joshi_kumar.joshi_kumar import JoshiKumar
from bdgs.algorithms.maung.maung import Maung
from bdgs.algorithms.mohanty_rambhatla.mohanty_rambhatla import MohantyRambhatla
from bdgs.algorithms.mohmmad_dadi.mohmmad_dadi import MohmmadDadi
from bdgs.algorithms.murthy_jadon.murthy_jadon import MurthyJadon
from bdgs.algorithms.naidoo_omlin.naidoo_omlin import NaidooOmlin
from bdgs.algorithms.nguyen_huynh.nguyen_huynh import NguyenHuynh
from bdgs.algorithms.oyedotun_khashman.oyedotun_khashman import OyedotunKhashman
from bdgs.algorithms.pinto_borges.pinto_borges import PintoBorges
from bdgs.algorithms.zhuang_yang.zhuang_yang import ZhuangYang
from bdgs.data.algorithm import ALGORITHM

ALGORITHM_FUNCTIONS = {
    ALGORITHM.MURTHY_JADON: MurthyJadon(),
    ALGORITHM.MAUNG: Maung(),
    ALGORITHM.ADITHYA_RAJESH: AdithyaRajesh(),
    ALGORITHM.EID_SCHWENKER: EidSchwenker(),
    ALGORITHM.ISLAM_HOSSAIN_ANDERSSON: IslamHossainAndersson(),
    ALGORITHM.PINTO_BORGES: PintoBorges(),
    ALGORITHM.MOHMMAD_DADI: MohmmadDadi(),
    ALGORITHM.GUPTA_JAAFAR: GuptaJaafar(),
    ALGORITHM.MOHANTY_RAMBHATLA: MohantyRambhatla(),
    ALGORITHM.ZHUANG_YANG: ZhuangYang(),
    ALGORITHM.CHANG_CHEN: ChangChen(),
    ALGORITHM.NAIDOO_OMLIN: NaidooOmlin(),
    ALGORITHM.JOSHI_KUMAR: JoshiKumar(),
    ALGORITHM.NGUYEN_HUYNH: NguyenHuynh(),
    ALGORITHM.OYEDOTUN_KHASHMAN: OyedotunKhashman(),
}
