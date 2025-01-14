import kshell_utilities as ksutil
import numpy as np

def main():
    Ne22_v2 = ksutil.loadtxt(path="Ne22_v2/", load_and_save_to_file=False)
    Ne22_v4 = ksutil.loadtxt(path="Ne22_v4/", load_and_save_to_file=False)
    V50_v2 = ksutil.loadtxt(path="V50_v2/", load_and_save_to_file=False)
    V50_v4 = ksutil.loadtxt(path="V50_v4/", load_and_save_to_file=False)

    assert np.all(Ne22_v2.levels == Ne22_v4.levels)
    assert np.all(Ne22_v2.transitions_BE1 == Ne22_v4.transitions_BE1)
    assert np.all(Ne22_v2.transitions_BM1 == Ne22_v4.transitions_BM1)
    assert np.all(Ne22_v2.transitions_BE2 == Ne22_v4.transitions_BE2)

    assert np.all(V50_v2.levels == V50_v4.levels)
    assert np.all(V50_v2.transitions_BE1 == V50_v4.transitions_BE1)
    assert np.all(V50_v2.transitions_BM1 == V50_v4.transitions_BM1)
    assert np.all(V50_v2.transitions_BE2 == V50_v4.transitions_BE2)


if __name__ == "__main__":
    main()