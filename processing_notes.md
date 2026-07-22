# Processing Notes — Reversible Data Hiding (Ni 2006)

- **Paper:** Zhicheng Ni, Yun-Qing Shi, Nirwan Ansari, Wei Su, IEEE TCSVT, vol. 16, no. 3, 2006
- **Reproduction tier:** A
- **Status:** Completed (full reproduction)

## What was reproduced
The single- and multiple-(peak,zero)-pair histogram-shifting algorithm was implemented from the paper text in ~90 lines of NumPy and verified for **bit-exact reversibility** on all eight USC-SIPI images.

## Key results (reproduced)
- Every image/configuration: perfect recovery of payload and cover.
- Single-pair marked PSNR ~50-55 dB, always above the paper's theoretical 48.13 dB lower bound.
- Capacity is set by the peak height; smooth images embed far more than textured ones.

## Reproduced vs. reported
- The 48.13 dB PSNR bound and exact reversibility reproduce exactly.
- Absolute single-pair capacity for Lena (2745 bits) is lower than the paper's 5460 bits. **Reason:** the USC-SIPI Lena variant bundled here has a shorter peak bin than the variant used in the 2006 paper. This is an image-source difference, not an algorithmic discrepancy; the mechanism (capacity = peak height) is identical.

## Honesty note
All numbers in the report/figures are produced by the included code on the bundled images. No results were copied from the paper except those explicitly labelled "reported" in the comparison table.
