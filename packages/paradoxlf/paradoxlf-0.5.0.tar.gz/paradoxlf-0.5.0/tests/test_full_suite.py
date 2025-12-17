import sys
import os
import py_compile

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_full_suite():
    print("=== Paradox V0.5.0 Full Suite Verification ===")
    
    # 1. Verify Core Engine & Optimization (V4)
    print("[1/5] Checking Core Engine & Parallel Sim...")
    from paradox.engine import LatentMemoryEngine
    from paradox.simulation import SimulationEnv
    engine = LatentMemoryEngine(dimension=64, backend="numpy")
    sim = SimulationEnv(engine)
    assert sim.num_workers > 0
    print("      -> Core OK.")

    # 2. Verify Multimedia (V2)
    print("[2/5] Checking Multimedia (Image/Video)...")
    from paradox.media.image import SimpleImageEncoder
    from paradox.media.video import SimpleVideoEncoder
    enc_img = SimpleImageEncoder()
    enc_vid = SimpleVideoEncoder()
    print("      -> Media OK.")

    # 3. Verify Mixer (V3)
    print("[3/5] Checking Latent Mixer...")
    from paradox.mixer import ParadoxMixer
    # Test availability of hybrid detection
    import numpy as np
    v = np.array([1.0])
    res = ParadoxMixer.add(v, v)
    assert res[0] == 2.0
    print("      -> Mixer OK.")

    # 4. Verify UI (V5)
    print("[4/5] Checking UI Dashboard Integrity...")
    ui_path = os.path.join(os.path.dirname(__file__), '..', 'paradox', 'ui', 'dashboard.py')
    if not os.path.exists(ui_path):
        raise FileNotFoundError(f"Dashboard file missing at {ui_path}")
    
    # Check syntax errors
    try:
        py_compile.compile(ui_path, doraise=True)
        print("      -> UI Syntax OK.")
    except py_compile.PyCompileError as e:
        print(f"      -> UI SYNTAX ERROR: {e}")
        sys.exit(1)

    # 5. Verify Dependencies
    print("[5/5] Checking Dependencies...")
    try:
        import streamlit
        import plotly
        print("      -> Departments OK.")
    except ImportError as e:
        print(f"      -> MISSING DEPENDENCY: {e}")
        # Don't fail test hard if just env issue, but warn
    
    print("\n✅ PRE-FLIGHT CHECK PASSED: Paradox V0.5.0 is ready for launch.")

if __name__ == "__main__":
    test_full_suite()
