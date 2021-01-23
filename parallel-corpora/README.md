# Parallel Corpora
This directory contains the parallel corpora for 12 Indian minority languages considered 'no (or very-low) resource languages' with Hindi. The corpus was made using the translation of the New Testament (27 book of the Bible) that was manually translated and published under an open licence. These were then proramatically individually sentence (verse) aligned with an open licenced version of the Hindi Bible (Hindi IRV). The version of these translation that was used to create the corpora is included here.

## Heuristics
This corpora was aligned automatically using the script [`build_parallel_corpora.py`](). It uses the fact that these translation were based off of the Hindi Bible and that the minority languages are related to Hindi. Thus, we assume that the verses numbers are a reference to the same semantic sentence in all languages. There are, however, cases where the verse numbers are different for this we use a simple metric based on the Levenshtein distance of the tokens above a pre-determined threshold as a heuristic to identify similar sentences. We will continue to make improvements to the output but in the meanwhile if you find an issue please create it on this [repo]()

## Statistics
Here are some general observations \
- List of minority languages represented: \
  1. Baghlayani (BGH)
  2. Bhadrawahi (BHD)
  3. Bilaspuri (KFS)
  4. Chambeali (CDH)
  5. Dogri (DGO)
  6. Gaddi (GBK)
  7. Haryanvi (BGC)
  8. Kangri (XNR)
  9. Kulvi Outer Seraji (OSJ)
  10. Kuvli (KFX)
  11. Mandeali (MJL)
  12. Pahari Mahasui (BFZ)

- Counts \
  - Number of words and lines in each minority language files \
    1. Baghlayani (BGH): words=187537 and lines=7273
    2. Bhadrawahi (BHD): words=179425 and lines=7261
    3. Bilaspuri (KFS): words=200060 and lines=7265
    4. Chambeali (CDH): words=225632 and lines=7200
    5. Dogri (DGO): words=188668 and lines=7276
    6. Gaddi (GBK): words=201460 and lines=7275
    7. Haryanvi (BGC): words=204008 and lines=7238
    8. Kangri (XNR): words=205253 and lines=7256
    9. Kulvi Outer Seraji (OSJ): words=200696 and lines=7243
    10. Kulvi (KFX): words=188619 and lines=7250
    11. Mandeali (MJL): words=221826 and lines=7216
    12. Pahari Mahasui (BFZ): words=184428 and lines=7263

