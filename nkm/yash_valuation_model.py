"""
Yash Highvoltage Ltd - Forward Estimate & Valuation Model
=========================================================

ILLUSTRATIVE SCENARIO MODEL - NOT INVESTMENT ADVICE.

This script builds a reproducible, assumption-driven forward estimate and
valuation for Yash Highvoltage Ltd (an Indian SME stock). It produces three
forward scenarios (Bear / Base / Bull) for FY27-FY30, target prices under a
range of exit P/E multiples, a reverse-DCF of what today's price implies, a
sensitivity grid, and an "overvaluation bridge".

Every number below is a function of the explicitly stated ASSUMPTIONS block.
Change the assumptions and the entire model re-derives. Nothing here is a
forecast, a recommendation, or a guarantee. FY = year ending 31 March.
All currency figures are INR crore unless stated otherwise (EPS / price in Rs).

Standard library only - no third-party dependencies. Runs with `python yash_valuation_model.py`.
"""

from dataclasses import dataclass, field
from typing import Dict, List

# =====================================================================
# ============================ ASSUMPTIONS ============================
# =====================================================================
# Everything that drives the model lives here and is meant to be edited.

# ---- Market / current state (HARD INPUTS) ----
CURRENT_PRICE        = 735.0     # Rs per share
MARKET_CAP_CR        = 2102.0    # Rs crore
SHARES_OUT_CR        = MARKET_CAP_CR / CURRENT_PRICE   # ~2.86 crore shares
COST_OF_EQUITY       = 0.13      # 13% discount rate (SME risk premium)
TAX_RATE             = 0.25      # 25%

# ---- FY26 actuals (the launch pad; HARD INPUTS) ----
FY26 = {
    "revenue":  235.2,
    "ebitda":   60.4,    # 25.7% margin
    "pat":      37.3,
    "eps":      13.08,
    "units":    7272,
}

# ---- Trailing valuation multiples (HARD INPUTS) ----
TRAILING_PE      = 54.0
TRAILING_PB      = 11.4
TRAILING_EVEBITDA = 30.0
PEER_NORMAL_PE   = 30.0   # Shilchar / TARIL-level "peer-normal" multiple

# ---- Forward scenario definitions (FY27..FY30) ----
# Each scenario specifies, per year:
#   rev_growth : YoY revenue growth rate
#   ebitda_mgn : EBITDA margin
#   da_cr      : depreciation & amortisation (Rs cr) - rises as Rs153cr plant
#                is commissioned and depreciated
#   interest_cr: net interest expense (Rs cr) - near net-debt-free today; some
#                drawdown to part-fund capex in slower-equity scenarios
#   dilution   : NET new shares issued (crore) versus FY26 base, cumulative,
#                from the pending ~Rs100-150cr equity raise. Bull = least
#                dilution (raise at higher price -> fewer shares); Bear = most.
#
# Years are ordered FY27, FY28, FY29, FY30.

YEARS = ["FY27", "FY28", "FY29", "FY30"]

SCENARIOS = {
    # ---------------------------------------------------------------
    # BEAR: growth normalises ~20-25%, margins 23-24%, plant ramp
    # delayed, more dilution (equity raised at a lower price).
    # ---------------------------------------------------------------
    "Bear": {
        "rev_growth": [0.30, 0.18, 0.14, 0.12],   # FY27 ~306cr (below guidance), -> ~430cr FY30
        "ebitda_mgn": [0.235, 0.235, 0.240, 0.240],
        "da_cr":      [9.0, 14.0, 18.0, 19.0],
        "interest_cr":[3.0, 5.0, 6.0, 6.0],        # debt-funds part of capex
        "dilution":   [0.45, 0.45, 0.45, 0.45],    # ~Rs150cr raise at a low price
    },
    # ---------------------------------------------------------------
    # BASE: management mid-guidance. FY27 ~Rs380cr (mid of 360-400),
    # ~25% margins, some slippage in plant ramp; lands ~Rs520cr FY30.
    # ---------------------------------------------------------------
    "Base": {
        "rev_growth": [0.615, 0.16, 0.12, 0.10],   # FY27 ->~380cr (mid guide) -> ~520cr FY30
        "ebitda_mgn": [0.245, 0.250, 0.255, 0.255],
        "da_cr":      [9.0, 15.0, 19.0, 20.0],
        "interest_cr":[2.5, 3.5, 4.0, 4.0],
        "dilution":   [0.32, 0.32, 0.32, 0.32],    # ~Rs125cr raise, mid price
    },
    # ---------------------------------------------------------------
    # BULL: encodes the higher-realisation + margin-expansion thesis.
    # 550 kV + export mix lifts EBITDA margin toward 27-28%; revenue
    # reaches the Rs 550-700cr ambition by FY30 (~Rs660cr here).
    # Least dilution (raise placed at a high price -> fewer shares).
    # ---------------------------------------------------------------
    "Bull": {
        "rev_growth": [0.70, 0.24, 0.20, 0.15],    # FY27 ~400cr -> FY30 ~660cr
        "ebitda_mgn": [0.250, 0.265, 0.275, 0.280],# margin lift from mix
        "da_cr":      [9.0, 15.0, 19.0, 20.0],
        "interest_cr":[1.5, 1.5, 1.0, 0.5],        # stays ~net-debt-free
        "dilution":   [0.22, 0.22, 0.22, 0.22],    # ~Rs100cr raise at high price
    },
}

# ---- Exit-multiple grid for target prices ----
EXIT_PE_GRID = [25.0, 35.0, 45.0]
TARGET_YEARS = ["FY28", "FY30"]   # apply exit multiples to these forward EPS

# =====================================================================
# ========================= MODEL MACHINERY ==========================
# =====================================================================

@dataclass
class YearResult:
    year: str
    revenue: float
    growth: float
    ebitda: float
    margin: float
    da: float
    interest: float
    pbt: float
    tax: float
    pat: float
    shares: float
    eps: float


def project_scenario(name: str, cfg: Dict) -> List[YearResult]:
    """Build a FY27..FY30 P&L projection for one scenario from the assumptions."""
    results: List[YearResult] = []
    prev_rev = FY26["revenue"]
    base_shares = SHARES_OUT_CR
    for i, yr in enumerate(YEARS):
        g = cfg["rev_growth"][i]
        rev = prev_rev * (1.0 + g)
        mgn = cfg["ebitda_mgn"][i]
        ebitda = rev * mgn
        da = cfg["da_cr"][i]
        interest = cfg["interest_cr"][i]
        pbt = ebitda - da - interest
        tax = pbt * TAX_RATE if pbt > 0 else 0.0
        pat = pbt - tax
        shares = base_shares + cfg["dilution"][i]
        eps = (pat / shares) if shares > 0 else 0.0
        results.append(YearResult(
            year=yr, revenue=rev, growth=g, ebitda=ebitda, margin=mgn,
            da=da, interest=interest, pbt=pbt, tax=tax, pat=pat,
            shares=shares, eps=eps,
        ))
        prev_rev = rev
    return results


def get_year(results: List[YearResult], year: str) -> YearResult:
    for r in results:
        if r.year == year:
            return r
    raise KeyError(year)


def discount_to_present(future_value: float, years: float, rate: float) -> float:
    return future_value / ((1.0 + rate) ** years)


# Years from "now" (FY26 close = valuation date) to the end of each FY.
# We treat FY27 as ~1 year out, FY28 ~2y, FY29 ~3y, FY30 ~4y.
YEARS_OUT = {"FY27": 1.0, "FY28": 2.0, "FY29": 3.0, "FY30": 4.0}


# =====================================================================
# ============================= PRINTING =============================
# =====================================================================

def hr(char="=", width=78):
    print(char * width)


def banner(title):
    hr()
    print(title)
    hr()


def print_scenario_table(name: str, results: List[YearResult]):
    print()
    print(f"  SCENARIO: {name.upper()}")
    print("  " + "-" * 74)
    hdr = (f"  {'Year':<6}{'Revenue':>9}{'Grw%':>7}{'EBITDA':>9}{'Mgn%':>7}"
           f"{'PAT':>9}{'Shares':>9}{'EPS':>8}")
    print(hdr)
    print("  " + "-" * 74)
    # FY26 actual reference row
    print(f"  {'FY26':<6}{FY26['revenue']:>9.1f}{'--':>7}{FY26['ebitda']:>9.1f}"
          f"{25.7:>7.1f}{FY26['pat']:>9.1f}{SHARES_OUT_CR:>9.2f}{FY26['eps']:>8.2f}")
    for r in results:
        print(f"  {r.year:<6}{r.revenue:>9.1f}{r.growth*100:>7.1f}"
              f"{r.ebitda:>9.1f}{r.margin*100:>7.1f}{r.pat:>9.1f}"
              f"{r.shares:>9.2f}{r.eps:>8.2f}")
    print("  " + "-" * 74)
    fy30 = get_year(results, "FY30")
    cagr_rev = (fy30.revenue / FY26["revenue"]) ** (1/4) - 1
    cagr_pat = (fy30.pat / FY26["pat"]) ** (1/4) - 1
    print(f"  Implied FY26->FY30 CAGR:  revenue {cagr_rev*100:5.1f}%   "
          f"PAT {cagr_pat*100:5.1f}%")


def print_target_price_table(projections: Dict[str, List[YearResult]]):
    banner("TARGET PRICES: exit P/E applied to forward EPS, discounted to today @ 13%")
    print()
    print("  Method: Target(exit yr) = forward EPS x exit P/E.")
    print("          PV = Target / (1.13 ^ years_out).  Compare PV to Rs 735.")
    print()
    for ty in TARGET_YEARS:
        yrs_out = YEARS_OUT[ty]
        print(f"  --- Exit year {ty}  (discounted {yrs_out:.0f}y @ 13%) ---")
        hdr = f"  {'Scenario':<10}{'EPS':>8}"
        for pe in EXIT_PE_GRID:
            hdr += f"{('PV@'+str(int(pe))+'x'):>12}"
        hdr += f"{'  (upside vs 735 at each PE)':<2}"
        print(hdr)
        print("  " + "-" * 70)
        for sc, res in projections.items():
            yr = get_year(res, ty)
            row = f"  {sc:<10}{yr.eps:>8.2f}"
            ups = []
            for pe in EXIT_PE_GRID:
                target = yr.eps * pe
                pv = discount_to_present(target, yrs_out, COST_OF_EQUITY)
                row += f"{pv:>12.0f}"
                ups.append((pv / CURRENT_PRICE - 1) * 100)
            print(row)
            up_str = "   ".join(f"{int(pe)}x:{u:+5.0f}%" for pe, u in zip(EXIT_PE_GRID, ups))
            print(f"  {'':<18}{up_str}")
        print()


def reverse_dcf(projections: Dict[str, List[YearResult]]):
    banner("REVERSE-DCF / IMPLIED EXPECTATIONS: what must you believe to justify Rs 735?")
    print()
    print("  Q: At today's Rs 735, what FY26->FY30 EPS CAGR is required for a")
    print("     given exit P/E, such that the discounted target equals Rs 735?")
    print()
    print("  Solve:  735 = EPS_FY30 * exitPE / 1.13^4")
    print("     =>   EPS_FY30 = 735 * 1.13^4 / exitPE")
    print("     =>   required EPS CAGR = (EPS_FY30 / EPS_FY26)^(1/4) - 1")
    print(f"     (EPS_FY26 = {FY26['eps']:.2f}; note dilution makes the *EPS* CAGR")
    print("      bar even higher than the PAT CAGR bar.)")
    print()
    df4 = (1 + COST_OF_EQUITY) ** 4
    print(f"  {'Exit P/E':<10}{'Req EPS_FY30':>14}{'Req EPS CAGR':>16}"
          f"{'Implied FY30 PAT*':>20}")
    print("  " + "-" * 60)
    for pe in [25.0, 30.0, 35.0, 45.0, 54.0]:
        req_eps = CURRENT_PRICE * df4 / pe
        req_cagr = (req_eps / FY26["eps"]) ** (1/4) - 1
        # Implied PAT if shares ~ base + ~0.3cr mid dilution, just to size it
        implied_pat = req_eps * (SHARES_OUT_CR + 0.30)
        print(f"  {pe:<10.0f}{req_eps:>14.2f}{req_cagr*100:>15.1f}%"
              f"{implied_pat:>20.0f}")
    print("  " + "-" * 60)
    print("  *Implied FY30 PAT assumes ~0.30cr net dilution; for scale only.")
    print()
    print("  Cross-check against the scenarios' actual FY30 EPS:")
    print(f"  {'Scenario':<10}{'FY30 EPS':>10}{'FY30 PAT':>10}{'PAT CAGR':>11}"
          f"{'EPS CAGR':>11}")
    print("  " + "-" * 54)
    for sc, res in projections.items():
        fy30 = get_year(res, "FY30")
        pat_cagr = (fy30.pat / FY26["pat"]) ** (1/4) - 1
        eps_cagr = (fy30.eps / FY26["eps"]) ** (1/4) - 1
        print(f"  {sc:<10}{fy30.eps:>10.2f}{fy30.pat:>10.1f}"
              f"{pat_cagr*100:>10.1f}%{eps_cagr*100:>10.1f}%")
    print()
    # What exit PE does today's price imply if we ACCEPT each scenario's FY30 EPS?
    print("  Flip it: GRANT each scenario's FY30 EPS - what exit P/E must the")
    print("  market be assigning today (so that discounted target = 735)?")
    print(f"  {'Scenario':<10}{'FY30 EPS':>10}{'Implied exit P/E*':>20}")
    print("  " + "-" * 42)
    for sc, res in projections.items():
        fy30 = get_year(res, "FY30")
        implied_pe = CURRENT_PRICE * df4 / fy30.eps
        print(f"  {sc:<10}{fy30.eps:>10.2f}{implied_pe:>20.1f}")
    print("  " + "-" * 42)
    print("  *i.e. the FY30 P/E you must STILL be willing to pay in 4 years to")
    print("   merely earn the 13% cost of equity from Rs 735. Compare to peer-")
    print(f"   normal ~{PEER_NORMAL_PE:.0f}x. If this >> 30x, growth+rerating are both priced in.")


def sensitivity_grid(projections: Dict[str, List[YearResult]]):
    banner("SENSITIVITY GRID: target price & upside vs Rs 735  (FY30 EPS x exit P/E)")
    print()
    print("  Cells = present value today (discounted 4y @ 13%) and (upside%).")
    print()
    hdr = f"  {'FY30 EPS':<22}"
    for pe in EXIT_PE_GRID:
        hdr += f"{('exit '+str(int(pe))+'x'):>16}"
    print(hdr)
    print("  " + "-" * 70)
    for sc, res in projections.items():
        fy30 = get_year(res, "FY30")
        label = f"{sc} (EPS {fy30.eps:.1f})"
        row = f"  {label:<22}"
        for pe in EXIT_PE_GRID:
            target = fy30.eps * pe
            pv = discount_to_present(target, 4.0, COST_OF_EQUITY)
            up = (pv / CURRENT_PRICE - 1) * 100
            cell = f"{pv:.0f} ({up:+.0f}%)"
            row += f"{cell:>16}"
        print(row)
    print("  " + "-" * 70)
    print("  Read: a cell above Rs 735 with a positive % = upside under that")
    print("  (EPS, exit-multiple) pair; below = downside. PV already nets out")
    print("  4 years of 13% required return, so 0% = 'merely earns cost of equity'.")


def overvaluation_bridge(projections: Dict[str, List[YearResult]]):
    banner("OVERVALUATION BRIDGE: today's ~54x P/E vs peer-normal ~30x")
    print()
    print(f"  Trailing P/E today          : {TRAILING_PE:.0f}x  (price {CURRENT_PRICE:.0f}, "
          f"FY26 EPS {FY26['eps']:.2f})")
    print(f"  Peer-normal P/E (Shilchar/TARIL): {PEER_NORMAL_PE:.0f}x")
    print()
    # Decompose price into earnings component vs multiple-premium component.
    price_at_peer_pe = PEER_NORMAL_PE * FY26["eps"]
    multiple_premium = CURRENT_PRICE - price_at_peer_pe
    print("  Decomposition of the Rs 735 price on TRAILING FY26 earnings:")
    print("  " + "-" * 58)
    print(f"  Price justified by FY26 EPS @ peer-normal 30x : Rs {price_at_peer_pe:>7.0f}")
    print(f"  Multiple premium (54x vs 30x) on same earnings: Rs {multiple_premium:>7.0f}")
    print(f"  {'':47}{'-'*10}")
    print(f"  Total price                                   : Rs {CURRENT_PRICE:>7.0f}")
    pct_premium = multiple_premium / CURRENT_PRICE * 100
    print()
    print(f"  => {pct_premium:.0f}% of today's price is pure multiple premium over a")
    print(f"     peer-normal 30x on TODAY'S earnings. The market is paying that")
    print(f"     premium in anticipation of the forward growth/margin story.")
    print()
    # How much forward earnings growth "absorbs" the premium at peer-normal exit?
    print("  Alternative view - does forward growth 'earn back' the premium?")
    print("  At a peer-normal 30x EXIT on each scenario's FY30 EPS, PV today is:")
    print("  " + "-" * 58)
    df4 = (1 + COST_OF_EQUITY) ** 4
    for sc, res in projections.items():
        fy30 = get_year(res, "FY30")
        pv = discount_to_present(fy30.eps * PEER_NORMAL_PE, 4.0, COST_OF_EQUITY)
        up = (pv / CURRENT_PRICE - 1) * 100
        verdict = "justifies >=735" if pv >= CURRENT_PRICE else "below 735"
        print(f"  {sc:<6} FY30 EPS {fy30.eps:6.2f}  -> PV @30x = Rs {pv:6.0f}  "
              f"({up:+5.0f}%)  {verdict}")
    print("  " + "-" * 58)
    print("  Interpretation: if you assume the multiple NORMALISES to ~30x by")
    print("  FY30 (the bull/bear debate's real crux), only the strongest growth")
    print("  path keeps you whole. Holding 45-54x forever is the unspoken assumption.")


def print_assumptions_recap():
    banner("ASSUMPTIONS RECAP (editable at top of script)")
    print(f"  Current price Rs {CURRENT_PRICE:.0f} | Mkt cap Rs {MARKET_CAP_CR:.0f}cr | "
          f"Shares {SHARES_OUT_CR:.2f}cr | Ke {COST_OF_EQUITY*100:.0f}% | Tax {TAX_RATE*100:.0f}%")
    print(f"  FY26 actuals: Rev {FY26['revenue']:.1f} | EBITDA {FY26['ebitda']:.1f} "
          f"(25.7%) | PAT {FY26['pat']:.1f} | EPS {FY26['eps']:.2f}")
    print(f"  Trailing: P/E {TRAILING_PE:.0f}x | P/B {TRAILING_PB:.1f}x | "
          f"EV/EBITDA {TRAILING_EVEBITDA:.0f}x | peer-normal P/E {PEER_NORMAL_PE:.0f}x")
    print()
    print("  Scenario drivers (FY27->FY30):")
    for sc, cfg in SCENARIOS.items():
        g = "/".join(f"{x*100:.0f}" for x in cfg["rev_growth"])
        m = "/".join(f"{x*100:.1f}" for x in cfg["ebitda_mgn"])
        print(f"    {sc:<5}: rev growth% {g}  | EBITDA mgn% {m}  | "
              f"net dilution {cfg['dilution'][-1]:.2f}cr shares")
    print()
    print("  BULL THESIS ENCODED: EBITDA margin rises 25.0% -> 28.0% as the 550 kV")
    print("  greenfield plant + 20%+ export mix lift per-unit realisation; revenue")
    print("  reaches the Rs 550-700cr ambition (~Rs660cr FY30). Least dilution,")
    print("  near net-debt-free. BASE = management mid-guidance w/ ramp slippage.")
    print("  BEAR = growth normalises ~20-25%, margins 23.5-24%, ramp delayed, more dilution.")


def main():
    print()
    banner("YASH HIGHVOLTAGE LTD - ILLUSTRATIVE FORWARD VALUATION MODEL")
    print("  *** ILLUSTRATIVE SCENARIO MODEL - NOT INVESTMENT ADVICE ***")
    print("  All outputs are functions of the editable ASSUMPTIONS block and are")
    print("  scenarios, not forecasts, recommendations, or guarantees.")
    print(f"  FY = year ending 31 March. INR crore unless noted. Ke = {COST_OF_EQUITY*100:.0f}%.")
    print()

    print_assumptions_recap()

    # Build all projections
    projections = {sc: project_scenario(sc, cfg) for sc, cfg in SCENARIOS.items()}

    banner("FORWARD SCENARIOS (FY27-FY30): year-by-year P&L")
    for sc, res in projections.items():
        print_scenario_table(sc, res)

    print()
    print_target_price_table(projections)
    reverse_dcf(projections)
    print()
    sensitivity_grid(projections)
    print()
    overvaluation_bridge(projections)

    print()
    banner("DISCLAIMER")
    print("  This is an ILLUSTRATIVE, ASSUMPTION-DRIVEN scenario model built for")
    print("  analysis only. It is NOT investment advice, NOT a recommendation, and")
    print("  NOT a guarantee of any outcome. Every figure depends entirely on the")
    print("  assumptions at the top of this script and on management guidance that")
    print("  may not be realised. Do your own due diligence / consult a registered")
    print("  adviser before any investment decision.")
    print()


if __name__ == "__main__":
    main()
