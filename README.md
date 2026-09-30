# Artifacts for "Position: Attested ≠ True — The Robustness of Verified ML Cannot Be Self-Certified"

Anonymized artifact repository for the SaTML 2027 submission. Contents follow the Open Science section of the paper.

| item | paper | folder | notes |
|---|---|---|---|
| (i) machine-readable Table I with verification status and the two corrections of Appendix H | Section III, Appendix H | `table1/table1.csv`, `table1/table1.json` | |
| (ii) seasoning price T* of eq. (3), regime boundary N* of eq. (4), table of Appendix E | Section VI-C, Appendix E | `scripts/seasoning_price.py` | reproduces the Appendix E table to two decimals |
| (ii) randomized check of Lemma 1 (retained fraction = mean rho over the cheapest mass 1-eps, over rho_bar; hence >= rho_min/rho_bar), worked case, Fig. 4 data | Appendix D | `scripts/estimation_error_check.py` | 20,000 random instances, no departure from the equality and no violation of the corollary; equality on the right exactly when the cheapest class carries mass >= 1-eps; worked case 0.048 |
| (ii) Figs. 1-4 of the paper | Section VI, Appendix D | `scripts/figures.py`, `figures/` | the PDFs in the paper are produced by this script (`python3 scripts/figures.py <output dir>`), PNG previews in `figures/` |
| (iii) enumeration reproducing the three counts of the illustrative audit of Appendix J (8, 63 and 0 of 128) | Appendix J | `scripts/audit_enumeration.py` | a reconstruction from the description in Appendix J under the assumptions stated there (withholding free; a withholding is profitable if the verdict is strictly better than on the complete honest submission); not a record of the original enumeration |
| (iv) model behind Appendix G and Fig. 5 (capacity frontier) | Appendix G | — | not released; see Open Science (iv) |
| (v) quotations with page numbers behind the readings of Section V and the leaderboard passage of Section IV-B | Sections V, IV-B | `quotes/quotes_section_V.md` | |
| bibliography check | LLM usage considerations | `hallucinator/hallucinator-report.txt` | output of hallucinator-cli 0.2.3 on the paper's reference list: 46 entries verified; 19 reported NOT FOUND because the databases timed out and 1 skipped as a web page, each of these 20 verified separately against a bibliographic database or the source page; 1 author mismatch where the database record lists one of the three authors |

## Running

    python3 scripts/seasoning_price.py          # Appendix E table, N*, regime readings
    python3 scripts/estimation_error_check.py   # Lemma 1 check + fig4_data.csv
    python3 scripts/audit_enumeration.py        # Appendix J counts: 8, 63, 0 of 128
    python3 scripts/figures.py                  # needs matplotlib; writes figures/fig1..fig4

Python 3.8 or later. Only `figures.py` needs a third-party package (matplotlib). Everything runs in seconds on commodity hardware.

## Anonymity

The files contain no author names, affiliations, institutional paths, account handles, e-mail addresses or blockchain addresses.

## Provenance of the scripts

`seasoning_price.py`, `estimation_error_check.py`, `audit_enumeration.py` and `figures.py` were drafted with LLM assistance during the preparation of the submission and checked against the closed-form expressions of the paper (Appendix E table to two decimals; worked case 0.048; the 2^3 count of the fail-open audit). The LLM usage considerations section of the paper states this.
