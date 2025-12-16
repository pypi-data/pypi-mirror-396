from bluer_ugv.README.swallow.consts import swallow_assets2
from bluer_ugv.README.arzhang.consts import arzhang_assets, arzhang_assets2
from bluer_ugv.README.rangin.consts import rangin_mechanical_design

dict_of_ugvs = {
    "swallow": {
        "order": 1,
        "items": [
            f"{swallow_assets2}/20250701_2206342_1.gif",
            f"{swallow_assets2}/20250913_203635~2_1.gif",
        ],
    },
    "arzhang": {
        "order": 2,
        "items": [
            f"{arzhang_assets2}/20251209_111322.jpg",
        ],
    },
    "arzhang2": {
        "order": 3,
        "items": [
            f"{arzhang_assets2}/20251210_154513.jpg",
        ],
    },
    "arzhang3": {
        "order": 4,
        "items": sorted(
            [
                f"{arzhang_assets}/20251107_175506.jpg",
                f"{arzhang_assets2}/20251128_175614.jpg",
                f"{arzhang_assets2}/20251202_100317.jpg",
                f"{arzhang_assets2}/20251202_101031.jpg",
                f"{arzhang_assets2}/20251128_113314.jpg",
                f"{arzhang_assets2}/20251128_151952.jpg",
                f"{arzhang_assets2}/20251128_155616.jpg",
                f"{arzhang_assets2}/20251130_140103.jpg",
                f"{arzhang_assets2}/20251203_112602.jpg",
                f"{arzhang_assets2}/20251210_154654.jpg",
            ]
        ),
    },
    "rangin": {
        "order": 5,
        "items": [
            f"{rangin_mechanical_design}/robot.png",
        ],
    },
}
