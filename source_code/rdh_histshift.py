"""
Reproduction of:  Z. Ni, Y.-Q. Shi, N. Ansari, W. Su,
"Reversible Data Hiding," IEEE TCSVT vol. 16(3), pp. 354-362, 2006.

Histogram-shifting reversible data hiding with one or multiple
(peak, zero) point pairs. Fully reversible: extract() recovers the
embedded bits and restores the original image exactly (verified by
bit-exact comparison in run_experiment.py).

For clarity the reproduction selects zero points that are genuinely
empty histogram bins (no side-information / overhead needed), which is
the standard demonstration case in the paper for natural images.
"""
import numpy as np


def _select_pairs(hist, n_pairs):
    """Choose n_pairs (peak, zero) grayscale values. Peaks = tallest bins;
    each zero = nearest empty bin (guarantees loss-free recovery)."""
    order = [int(v) for v in np.argsort(hist)[::-1] if hist[v] > 0]
    empties = [v for v in range(256) if hist[v] == 0]
    pairs, used_zero = [], set()
    for P in order:
        cand = [z for z in empties if z not in used_zero]
        if not cand:
            break
        Z = min(cand, key=lambda z: abs(z - P))
        used_zero.add(Z)
        pairs.append((P, Z))
        if len(pairs) >= n_pairs:
            break
    return pairs


def embed(img, bits, n_pairs=1):
    img = img.astype(np.uint8)
    hist = np.bincount(img.ravel(), minlength=256)
    pairs = _select_pairs(hist, n_pairs)
    cur = img.copy().astype(np.int16)
    bits = np.asarray(bits, dtype=np.uint8)
    ptr = 0
    used = []
    for (P, Z) in pairs:
        d = 1 if Z > P else -1
        slot = P + d
        flat = cur.ravel()
        if d == 1:
            region = (flat > P) & (flat < Z)
        else:
            region = (flat < P) & (flat > Z)
        flat[region] += d
        # embed into peak
        peak_idx = np.flatnonzero(flat == P)
        take = min(len(peak_idx), len(bits) - ptr)
        chunk = bits[ptr:ptr + take]
        sel = peak_idx[:take]
        flat[sel[chunk == 1]] = slot
        cur = flat.reshape(cur.shape)
        ptr += take
        used.append((int(P), int(Z), int(d), int(take)))
        if ptr >= len(bits):
            break
    info = {"pairs": used, "n_embedded": int(ptr), "shape": list(img.shape)}
    return cur.astype(np.uint8), info


def extract(marked, info):
    cur = marked.astype(np.int16)
    rev_bits = []
    for (P, Z, d, take) in reversed(info["pairs"]):
        slot = P + d
        flat = cur.ravel()
        idx = np.sort(np.flatnonzero((flat == P) | (flat == slot)))
        b = (flat[idx] == slot).astype(np.uint8)
        rev_bits.append(b[:take] if take <= len(b) else b)
        # collapse slot back to peak
        flat[flat == slot] = P
        # un-shift region
        if d == 1:
            region = (flat > slot) & (flat <= Z)
        else:
            region = (flat < slot) & (flat >= Z)
        flat[region] -= d
        cur = flat.reshape(cur.shape)
    bits = np.concatenate(list(reversed(rev_bits))) if rev_bits else np.array([], np.uint8)
    return bits[:info["n_embedded"]].astype(np.uint8), cur.astype(np.uint8)


def capacity(img, n_pairs=1):
    hist = np.bincount(img.astype(np.uint8).ravel(), minlength=256)
    pairs = _select_pairs(hist, n_pairs)
    return int(sum(hist[P] for (P, Z) in pairs))
