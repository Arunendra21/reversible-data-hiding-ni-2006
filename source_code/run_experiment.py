"""Run the Ni-2006 histogram-shifting RDH reproduction on the USC-SIPI
grayscale test set. Produces figures/ and outputs/metrics.json."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_toolkit"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rdh_toolkit as tk
import rdh_histshift as R

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
OUT = os.path.join(HERE, "..", "outputs")
os.makedirs(FIG, exist_ok=True); os.makedirs(OUT, exist_ok=True)

imgs = tk.load_all_std()
results = {}

for name, img in imgs.items():
    row = {}
    for npairs in [1, 3, 5]:
        cap = R.capacity(img, npairs)
        bits = tk.random_payload(cap, seed=hash(name) % 9999)
        marked, info = R.embed(img, bits, npairs)
        rbits, rimg = R.extract(marked, info)
        row[npairs] = {
            "capacity_bits": int(info["n_embedded"]),
            "bpp": round(tk.bpp(info["n_embedded"], img), 5),
            "psnr": round(tk.psnr(img, marked), 3),
            "ssim": round(tk.ssim(img, marked), 5),
            "reversible": bool(np.array_equal(rimg, img)
                               and np.array_equal(rbits, bits[:info["n_embedded"]])),
        }
    results[name] = row

json.dump(results, open(os.path.join(OUT, "metrics.json"), "w"), indent=2)

# --- Figure 1: Lena original vs marked (single pair) ---
lena = imgs["lena"]
cap = R.capacity(lena, 1)
marked, info = R.embed(lena, tk.random_payload(cap), 1)
fig, ax = plt.subplots(1, 2, figsize=(8, 4.2))
ax[0].imshow(lena, cmap="gray", vmin=0, vmax=255); ax[0].set_title("Original Lena"); ax[0].axis("off")
ax[1].imshow(marked, cmap="gray", vmin=0, vmax=255)
ax[1].set_title(f"Marked (PSNR={tk.psnr(lena,marked):.2f} dB)"); ax[1].axis("off")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig1_lena_orig_marked.png"), dpi=130); plt.close()

# --- Figure 2: histograms before/after ---
fig, ax = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
ax[0].bar(range(256), np.bincount(lena.ravel(), minlength=256), color="#1f4e79", width=1)
ax[0].set_title("Histogram of original Lena"); ax[0].set_xlabel("gray level")
ax[1].bar(range(256), np.bincount(marked.ravel(), minlength=256), color="#c0504d", width=1)
ax[1].set_title("Histogram after embedding"); ax[1].set_xlabel("gray level")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig2_histograms.png"), dpi=130); plt.close()

# --- Figure 3: rate-distortion (capacity vs PSNR) as pairs grow ---
fig, ax = plt.subplots(figsize=(6.2, 4.2))
for name in ["lena", "baboon", "airplane", "peppers"]:
    img = imgs[name]
    xs, ys = [], []
    for npairs in range(1, 13):
        cap = R.capacity(img, npairs)
        if cap == 0: break
        marked, info = R.embed(img, tk.random_payload(cap), npairs)
        xs.append(tk.bpp(info["n_embedded"], img)); ys.append(tk.psnr(img, marked))
    ax.plot(xs, ys, "-o", ms=3, label=name)
ax.axhline(48.13, ls="--", color="gray", lw=1, label="theoretical PSNR bound 48.13 dB")
ax.set_xlabel("Embedding rate (bpp)"); ax.set_ylabel("PSNR (dB)")
ax.set_title("Rate-distortion: multiple (peak,zero) pairs"); ax.legend(fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig3_rate_distortion.png"), dpi=130); plt.close()

# --- Figure 4: capacity bar chart across images ---
fig, ax = plt.subplots(figsize=(7.5, 4))
names = list(results.keys())
caps1 = [results[n][1]["capacity_bits"] for n in names]
caps5 = [results[n][5]["capacity_bits"] for n in names]
x = np.arange(len(names))
ax.bar(x - 0.2, caps1, 0.4, label="1 pair", color="#1f4e79")
ax.bar(x + 0.2, caps5, 0.4, label="5 pairs", color="#70ad47")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right")
ax.set_ylabel("Pure payload (bits)"); ax.set_title("Embedding capacity per image"); ax.legend()
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig4_capacity.png"), dpi=130); plt.close()

print("Done. Metrics for lena:", json.dumps(results["lena"], indent=1))
print("All reversible:", all(results[n][p]["reversible"] for n in results for p in results[n]))
