import numpy as np
import matplotlib.colorbar

# numpy fix
np.int = int

# colorbar fix
if not hasattr(matplotlib.colorbar.Colorbar, "set_clim"):
    def _set_clim(self, vmin=None, vmax=None):
        if hasattr(self, "mappable"):
            self.mappable.set_clim(vmin=vmin, vmax=vmax)
    matplotlib.colorbar.Colorbar.set_clim = _set_clim

from neurodynex.hopfield_network import network, pattern_tools, plot_tools


def build(size):
    net = network.HopfieldNetwork(size * size)
    fac = pattern_tools.PatternFactory(size, size)
    return net, fac


def make_patterns(fac):
    base = fac.create_checkerboard()
    pats = [base] + fac.create_random_pattern_list(3, 0.5)
    return base, pats


def show_patterns(pats):
    plot_tools.plot_pattern_list(pats)
    M = pattern_tools.compute_overlap_matrix(pats)
    plot_tools.plot_overlap_matrix(M)


def run_sim(net, base, flips=4):
    noisy = pattern_tools.flip_n(base, flips)
    net.set_state_from_pattern(noisy)
    states = net.run_with_monitoring(4)
    return noisy, states


def show_dynamics(states, pats):
    shape = pats[0].shape
    seq = pattern_tools.reshape_patterns(states, shape)
    plot_tools.plot_state_sequence_and_overlap(seq, pats, 0, suptitle="Network Dynamics")


def main():
    n = 5
    net, fac = build(n)
    base, pats = make_patterns(fac)
    net.store_patterns(pats)
    show_patterns(pats)
    noisy, states = run_sim(net, base, 4)
    show_dynamics(states, pats)


if __name__ == "__main__":
    main()
