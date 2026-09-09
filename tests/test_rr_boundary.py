from master_engine.engine import MasterEngine

def test_rr_boundary_float_tolerance():
    # 1.8 / 1.2 can be represented just below 1.5 in binary floating point.
    rr=1.8/1.2
    assert not (rr + 1e-9 < MasterEngine(min_rr=1.5).min_rr)
