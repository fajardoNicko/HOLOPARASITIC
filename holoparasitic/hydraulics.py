r"""
hydraulics.py  (Person B) — steady-state xylem flow as a sparse linear system.

Kirchhoff's current law on the conductance-weighted graph gives, at every free
node i,

        sum_j g_ij (psi_i - psi_j)  +  h_i (psi_i - psi_parasite)  =  0
        \_______ network flow _______/   \____ haustorial sink ____/

which is the linear system  A psi = b  with A = L_ff + diag(h_f)  (L = graph
Laplacian of conductances). The haustorium enters exactly as the brief's leak
equation  Q_parasite = K_h (psi_host - psi_parasite): a conductance K_h tying a
host node to a fixed parasite reservoir psi_parasite.

Boundary conditions (Dirichlet):
    root node      psi = PSI_SOURCE   (water supply at the stem base)
    terminal nodes psi = PSI_LEAF     (transpirational pull at the leaves)

A vessel whose tension exceeds the cavitation limit (psi < PSI_CAVITATION)
embolises and is removed from the conducting network — this is the physical
event that couples K_h to the topological collapse studied by percolation.py.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

import config
from . import network


class HydraulicSolver:
    """Pre-factorises the conductance Laplacian once; re-solves cheaply for any
    set of haustoria (used by the K_h sweep)."""

    def __init__(self, G):
        self.G = G
        self.W, self.nodes = network.conductance_csr(G)
        self.index = {n: i for i, n in enumerate(self.nodes)}
        deg = np.asarray(self.W.sum(axis=1)).ravel()
        self.L = (sp.diags(deg) - self.W).tocsr()

        self.root = next(n for n, d in G.nodes(data=True) if d["kind"] == "root")
        self.terminals = [n for n, d in G.nodes(data=True)
                          if d["kind"] == "terminal"]
        # incident conductance of every node (diagonal of the Laplacian) — used
        # to scale haustorial leak to the host vessel's own caliber.
        self.node_conductance = np.asarray(self.W.sum(axis=1)).ravel()

    # ------------------------------------------------------------------ solve
    def solve(self, haustoria=None, k_h=config.K_H_DEFAULT, relative=True,
              psi_source=config.PSI_SOURCE, psi_leaf=config.PSI_LEAF,
              psi_parasite=config.PSI_PARASITE):
        """Return psi (array aligned with self.nodes).

        haustoria : iterable of node ids carrying a haustorial sink (or a
                    {node: K_h} dict for per-haustorium strengths).
        relative  : if True (default), K_h is a DIMENSIONLESS multiple of the
                    host node's own incident conductance, so a haustorium taps a
                    vessel in proportion to its caliber. This keeps sensitivity
                    uniform across generations — without it, sinks on thin
                    terminal vessels embolise instantly and collapse occurs at
                    rho ~ 0 (giving meaningless negative p_c).
        """
        N = len(self.nodes)
        psi = np.zeros(N)

        fixed = {self.root: psi_source}
        for t in self.terminals:
            fixed.setdefault(t, psi_leaf)

        h = np.zeros(N)
        if haustoria is not None:
            items = haustoria.items() if isinstance(haustoria, dict) \
                else ((n, k_h) for n in haustoria)
            for n, k in items:
                i = self.index[n]
                h[i] += k * self.node_conductance[i] if relative else k

        is_fixed = np.zeros(N, bool)
        fixed_idx = np.fromiter((self.index[n] for n in fixed), int, len(fixed))
        fixed_val = np.fromiter(fixed.values(), float, len(fixed))
        is_fixed[fixed_idx] = True
        psi[fixed_idx] = fixed_val

        free = np.where(~is_fixed)[0]
        if free.size == 0:
            return psi

        Lff = self.L[free][:, free]
        Lfd = self.L[free][:, fixed_idx]
        # tiny grounding term keeps A non-singular if a sub-component detaches
        A = (Lff + sp.diags(h[free] + 1e-12)).tocsc()
        b = -Lfd.dot(fixed_val) + h[free] * psi_parasite

        psi[free] = spla.spsolve(A, b)
        return psi

    # ------------------------------------------------------------- diagnostics
    def embolized_nodes(self, psi, threshold=config.PSI_CAVITATION):
        """Node ids whose tension passes the cavitation limit (psi < threshold).
        Root/terminal Dirichlet nodes are never reported as embolised."""
        protected = {self.root, *self.terminals}
        out = []
        for i, p in enumerate(psi):
            n = self.nodes[i]
            if p < threshold and n not in protected:
                out.append(n)
        return out

    def edge_flows(self, psi):
        """Volumetric flow Q_uv = g_uv (psi_u - psi_v) on every edge."""
        flows = {}
        for u, v, d in self.G.edges(data=True):
            flows[(u, v)] = d["conductance"] * (psi[self.index[u]]
                                                - psi[self.index[v]])
        return flows


def baseline_potentials(G):
    """Healthy host: solve with no haustoria. Returns (solver, psi)."""
    s = HydraulicSolver(G)
    return s, s.solve(haustoria=None)


if __name__ == "__main__":
    from . import network as net
    G = net.generate()
    s, psi = baseline_potentials(G)
    print(f"baseline psi range: [{psi.min():.3f}, {psi.max():.3f}] MPa")
    h = list(G.nodes)[:50]
    psi2 = s.solve(haustoria=h, k_h=1.0)
    print(f"with 50 haustoria (K_h=1.0): {len(s.embolized_nodes(psi2))} embolised")
