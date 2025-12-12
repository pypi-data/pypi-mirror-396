import math
from pathlib import Path

import pytest
from pycivil.EXAStructural.codes import Code
from pycivil.EXAStructural.materials import Concrete, ConcreteSteel
from pycivil.EXAStructural.templateRCRect import RCTemplRectEC2


# --------------------
# BY-HAND TEST CASE #3
# --------------------
def test_symmetrical_uncracked_NM_001(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2018")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C25/30")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(600)
    rcSection.setDimW(300)

    # Longitudinal rebars
    lineMTRebars = rcSection.addSteelArea("LINE-MT", dist=50, d=20, nb=4, sd=40)
    lineMBRebars = rcSection.addSteelArea("LINE-MB", dist=50, d=20, nb=4, sd=40)

    # Geometrical properties
    assert pytest.approx(rcSection.calConcreteArea()) == 180000
    assert pytest.approx(rcSection.calSteelArea(), rel=1e-3) == 2513
    assert pytest.approx(rcSection.calIdealArea(), rel=1e-3) == 217699
    assert pytest.approx(rcSection.calProp_Ihx(), rel=1e-3) == 7.755e09
    assert pytest.approx(
        [rcSection.calBarycenterOfConcrete().x, rcSection.calBarycenterOfConcrete().y]
    ) == [0.0, 0.0]
    assert pytest.approx(
        [rcSection.calBarycenterOfSteel().x, rcSection.calBarycenterOfSteel().y]
    ) == [0.0, 0.0]
    assert pytest.approx(
        [rcSection.calBarycenter().x, rcSection.calBarycenter().y]
    ) == [0.0, 0.0]

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0 * KN, 0.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [0, 0, None]
    for i in rcSection.getConcrStress():
        assert pytest.approx(i, rel=1e-3) == 0
    for i in rcSection.getSteelStress():
        assert pytest.approx(i, rel=1e-3) == 0

    sigmac, sigmas, xi = rcSection.solverSLS_NM(1000 * KN, 0.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [4.593, 68.895, math.inf]
    for i in rcSection.getConcrStress():
        assert pytest.approx(i, rel=1e-3) == 4.593
    for i in rcSection.getSteelStress():
        assert pytest.approx(i, rel=1e-3) == 68.895

    sigmac, sigmas, xi = rcSection.solverSLS_NM(-1000 * KN, 0.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [-4.593, -68.895, math.inf]
    for i in rcSection.getConcrStress():
        assert pytest.approx(i, rel=1e-3) == -4.593
    for i in rcSection.getSteelStress():
        assert pytest.approx(i, rel=1e-3) == -68.895

    sigmac, sigmas, xi = rcSection.solverSLS_NM(-100 * KN, 0.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [
        -0.4593,
        -68.895 / 10,
        math.inf,
    ]
    for i in rcSection.getConcrStress():
        assert pytest.approx(i, rel=1e-3) == -0.4593
    for i in rcSection.getSteelStress():
        assert pytest.approx(i, rel=1e-3) == -6.8895

    sigmac, sigmas, xi = rcSection.solverSLS_NM(+100 * KN, 0.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [+0.4593, +6.8895, math.inf]
    for i in rcSection.getConcrStress():
        assert pytest.approx(i, rel=1e-3) == +0.4593
    for i in rcSection.getSteelStress():
        assert pytest.approx(i, rel=1e-3) == +6.8895

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0.0 * KN, 150.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [-5.803, 72.53, 300]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == +5.803
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-3) == -5.803
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = +72.53
        if idx in lineMTRebars:
            stressExpected = -72.53
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-3) == stressExpected

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0.0 * KN, -150.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [-5.803, +72.53, 300]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == -5.803
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-3) == +5.803
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = -72.53
        if idx in lineMTRebars:
            stressExpected = +72.53
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-3) == stressExpected

    # Neutral axis is measured from bottom to top of section
    sigmac, sigmas, xi = rcSection.solverSLS_NM(
        -1000.0 * KN, +150.0 * KNm, uncracked=True
    )
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-10.396, +3.635, 537.45]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-2) == +1.210
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == -10.396
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = +3.635
        if idx in lineMTRebars:
            stressExpected = -141.425
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-2) == stressExpected

    sigmac, sigmas, xi = rcSection.solverSLS_NM(
        -1000.0 * KN, -150.0 * KNm, uncracked=True
    )
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-10.396, +3.635, 62.65]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-2) == -10.396
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == +1.210
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = -141.425
        if idx in lineMTRebars:
            stressExpected = +3.635
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-2) == stressExpected

    sigmac, sigmas, xi = rcSection.solverSLS_NM(
        +1000.0 * KN, +150.0 * KNm, uncracked=True
    )
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-1.210, +141.425, 62.55]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-2) == 10.396
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == -1.210
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = +141.425
        if idx in lineMTRebars:
            stressExpected = -3.635
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-2) == stressExpected

    sigmac, sigmas, xi = rcSection.solverSLS_NM(
        +1000.0 * KN, -150.0 * KNm, uncracked=True
    )
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-1.210, +141.425, 537.45]
    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-2) == -1.210
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == 10.396
    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineMBRebars:
            stressExpected = -3.635
        if idx in lineMTRebars:
            stressExpected = +141.425
        print(
            f"Steel stress calculated: {i:.5f} equal to expected: {stressExpected:.5f}"
        )
        assert pytest.approx(i, rel=1e-2) == stressExpected


# ----------------------
# BY-HAND TEST CASE #2.2
# ----------------------
def test_uncracked_NM_002(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2008")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C32/40")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(1200)
    rcSection.setDimW(800)

    # Longitudinal rebars
    # Aggregates diameter maximum 25mm
    lineRebars01 = rcSection.addSteelArea("LINE-MT", dist=76, d=24, nb=10, sd=49)
    lineRebars02 = rcSection.addSteelArea("LINE-MT", dist=1016, d=24, nb=10, sd=49)
    lineRebars03 = rcSection.addSteelArea("LINE-MT", dist=1070, d=24, nb=10, sd=49)
    lineRebars04 = rcSection.addSteelArea("LINE-MT", dist=1124, d=24, nb=10, sd=49)

    # Geometrical properties
    assert pytest.approx(rcSection.calConcreteArea(), rel=1e-6) == 960.00e03
    assert pytest.approx(rcSection.calSteelArea(), rel=1e-3) == 18.09e03
    assert pytest.approx(rcSection.calIdealArea(), rel=1e-3) == 1.23135e06
    assert pytest.approx(
        [rcSection.calBarycenterOfConcrete().x, rcSection.calBarycenterOfConcrete().y]
    ) == [0.0, 0.0]
    assert pytest.approx(
        [rcSection.calBarycenterOfSteel().x, rcSection.calBarycenterOfSteel().y],
        rel=1e-2,
        abs=1e-3,
    ) == [0.0, -220.89]
    assert pytest.approx(
        [rcSection.calBarycenter().x, rcSection.calBarycenter().y], rel=1e-2, abs=1
    ) == [0.0, -49.39]
    assert (
        pytest.approx(rcSection.calProp_Ihx(barycenter=True), rel=1e-3, abs=1e-3)
        == 176.24e09
    )

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0 * KN, 2400.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-8.84, +96.97, 649.39]

    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == +7.4988
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-3) == -8.840

    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineRebars01:
            stressExpected = -117.11
        if idx in lineRebars02:
            stressExpected = +74.91
        if idx in lineRebars03:
            stressExpected = +85.94
        if idx in lineRebars04:
            stressExpected = +96.97
        assert pytest.approx(i, rel=1e-2) == stressExpected


# ----------------------
# BY-HAND TEST CASE #2.2
# ----------------------
def test_uncracked_NM_003(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2008")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C32/40")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(1200)
    rcSection.setDimW(800)

    # Longitudinal rebars
    # Aggregates diameter maximum 25mm
    lineRebars01 = rcSection.addSteelArea("LINE-MT", dist=76, d=24, nb=10, sd=49)
    lineRebars02 = rcSection.addSteelArea("LINE-MT", dist=130, d=24, nb=10, sd=49)
    lineRebars03 = rcSection.addSteelArea("LINE-MT", dist=184, d=24, nb=10, sd=49)
    lineRebars04 = rcSection.addSteelArea("LINE-MT", dist=1124, d=24, nb=10, sd=49)

    # Geometrical properties
    assert pytest.approx(rcSection.calConcreteArea(), rel=1e-6) == 960.00e03
    assert pytest.approx(rcSection.calSteelArea(), rel=1e-3) == 18.09e03
    assert pytest.approx(rcSection.calIdealArea(), rel=1e-3) == 1.23135e06
    assert pytest.approx(
        [rcSection.calBarycenterOfConcrete().x, rcSection.calBarycenterOfConcrete().y]
    ) == [0.0, 0.0]
    assert pytest.approx(
        [rcSection.calBarycenterOfSteel().x, rcSection.calBarycenterOfSteel().y],
        rel=1e-2,
        abs=1e-3,
    ) == [0.0, +220.89]
    assert pytest.approx(
        [rcSection.calBarycenter().x, rcSection.calBarycenter().y], rel=1e-2, abs=1
    ) == [0.0, +49.39]
    assert (
        pytest.approx(rcSection.calProp_Ihx(barycenter=True), rel=1e-3, abs=1e-3)
        == 176.24e09
    )

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0 * KN, -2400.0 * KNm, uncracked=True)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-8.84, +96.97, 550.61]

    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == -8.840
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-3) == +7.4988

    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineRebars04:
            stressExpected = -117.11
        if idx in lineRebars03:
            stressExpected = +74.91
        if idx in lineRebars02:
            stressExpected = +85.94
        if idx in lineRebars01:
            stressExpected = +96.97
        assert pytest.approx(i, rel=1e-2) == stressExpected


# ----------------------
# BY-HAND TEST CASE #2.5
# ----------------------
def test_cracked_stretched_NM_004(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2008")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C32/40")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(1200)
    rcSection.setDimW(800)

    # Longitudinal rebars
    # Aggregates diameter maximum 25mm
    lineRebars01 = rcSection.addSteelArea("LINE-MT", dist=76, d=24, nb=10, sd=49)
    lineRebars02 = rcSection.addSteelArea("LINE-MT", dist=1016, d=24, nb=10, sd=49)
    lineRebars03 = rcSection.addSteelArea("LINE-MT", dist=1070, d=24, nb=10, sd=49)
    lineRebars04 = rcSection.addSteelArea("LINE-MT", dist=1124, d=24, nb=10, sd=49)

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(+3619 * KN, 0.0 * KNm, uncracked=False)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [0.0, +376.27, 1666.0]

    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == 0.0
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-3) == 0.0

    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineRebars01:
            stressExpected = 376.27
        if idx in lineRebars02:
            stressExpected = 153.86
        if idx in lineRebars03:
            stressExpected = 141.05
        if idx in lineRebars04:
            stressExpected = 128.27
        assert pytest.approx(i, rel=1e-2) == stressExpected


# ----------------------
# BY-HAND TEST CASE #2.6
# ----------------------
def test_cracked_compressed_NM_005(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2008")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C32/40")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(1200)
    rcSection.setDimW(800)

    # Longitudinal rebars
    # Aggregates diameter maximum 25mm
    lineRebars01 = rcSection.addSteelArea("LINE-MT", dist=76, d=24, nb=10, sd=49)
    lineRebars02 = rcSection.addSteelArea("LINE-MT", dist=1016, d=24, nb=10, sd=49)
    lineRebars03 = rcSection.addSteelArea("LINE-MT", dist=1070, d=24, nb=10, sd=49)
    lineRebars04 = rcSection.addSteelArea("LINE-MT", dist=1124, d=24, nb=10, sd=49)

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(-3619 * KN, 0.0 * KNm, uncracked=False)
    assert pytest.approx([sigmac, sigmas, xi], rel=1e-2) == [-3.599, -36.92, 3557.496]

    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == -2.385
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == -3.599

    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineRebars01:
            stressExpected = -52.84
        if idx in lineRebars02:
            stressExpected = -38.56
        if idx in lineRebars03:
            stressExpected = -37.74
        if idx in lineRebars04:
            stressExpected = -36.92
        assert pytest.approx(i, rel=1e-2) == stressExpected


# ----------------------
# BY-HAND TEST CASE #2.1
# ----------------------
def test_cracked_bending_NM_006(tmp_path: Path):
    # Setting code for check
    code = Code("NTC2008")

    concrete = Concrete(descr="My concrete")
    concrete.setByCode(code, "C32/40")

    # Setting code for check
    steel = ConcreteSteel(descr="My steel")
    steel.setByCode(code, "B450C")

    # Build checkable structural system
    rcSection = RCTemplRectEC2(1, "Template RC Section")

    # Concrete dimension
    rcSection.setDimH(1200)
    rcSection.setDimW(800)

    # Longitudinal rebars
    # Aggregates diameter maximum 25mm
    lineRebars01 = rcSection.addSteelArea("LINE-MT", dist=76, d=24, nb=10, sd=49)
    lineRebars02 = rcSection.addSteelArea("LINE-MT", dist=1016, d=24, nb=10, sd=49)
    lineRebars03 = rcSection.addSteelArea("LINE-MT", dist=1070, d=24, nb=10, sd=49)
    lineRebars04 = rcSection.addSteelArea("LINE-MT", dist=1124, d=24, nb=10, sd=49)

    # Setting units
    KN = 1000
    KNm = 1000 * 1000

    sigmac, sigmas, xi = rcSection.solverSLS_NM(0.0 * KN, 2400.0 * KNm, uncracked=False)

    assert pytest.approx([sigmac, sigmas, xi], rel=1e-3) == [-10.31, +207.10, 480.51]

    for idx, i in enumerate(rcSection.getConcrStress()):
        if idx < 2:
            # BL and BR
            assert pytest.approx(i, rel=1e-3) == 0.0
        else:
            # TL and TR
            assert pytest.approx(i, rel=1e-2) == -10.31

    for idx, i in enumerate(rcSection.getSteelStress()):
        stressExpected = 0
        if idx in lineRebars01:
            stressExpected = -130.19
        if idx in lineRebars02:
            stressExpected = +172.34
        if idx in lineRebars03:
            stressExpected = +189.72
        if idx in lineRebars04:
            stressExpected = +207.10
        assert pytest.approx(i, rel=1e-2) == stressExpected
