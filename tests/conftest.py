import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, pytest
@pytest.fixture
def prices():
    rng=np.random.default_rng(7); n=500; idx=pd.date_range("2024-01-01",periods=n,freq="h",tz="UTC"); close=2000+np.cumsum(rng.normal(.08,2,n)); op=np.r_[close[0],close[:-1]]; spread=rng.uniform(.5,3,n)
    return pd.DataFrame({"open":op,"high":np.maximum(op,close)+spread,"low":np.minimum(op,close)-spread,"close":close,"volume":rng.integers(100,1000,n)},index=idx)

