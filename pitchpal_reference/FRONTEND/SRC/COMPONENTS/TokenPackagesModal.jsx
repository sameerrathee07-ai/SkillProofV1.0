import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useApi } from "../hooks/useApi";
import { api } from "../lib/api";
import { Icon } from "../components/Icons";
import { LOW_BALANCE_THRESHOLD, pitchesAffordable } from "../data/config";

const ONE_TIME = "one_time";
const SUBSCRIPTION = "subscription";

/**
 * Best guess at a local currency from the browser locale.
 *
 * The guess is only a request: /tokens/catalog validates the code and echoes
 * back the currency it actually priced in, so an unsupported region quietly
 * lands on the default instead of showing nothing.
 */
const REGION_CURRENCY = {
  IN: "INR", US: "USD", GB: "GBP", SG: "SGD",
  DE: "EUR", FR: "EUR", ES: "EUR", IT: "EUR", NL: "EUR",
  IE: "EUR", AT: "EUR", PT: "EUR", FI: "EUR", BE: "EUR",
};

function guessCurrency() {
  const tag = (typeof navigator !== "undefined" && navigator.language) || "";
  const region = tag.split("-")[1]?.toUpperCase();
  return REGION_CURRENCY[region] || "INR";
}

/**
 * Cheapest tokens per unit of money, among the packs on offer.
 *
 * A ranking, not a price: it compares two numbers the server sent and never
 * produces an amount anyone is charged.
 */
function bestValuePlanId(plans) {
  if (!plans?.length) return null;
  return plans.reduce((best, p) =>
    p.amount_minor / p.tokens < best.amount_minor / best.tokens ? p : best
  ).id;
}

/**
 * The pack a founder's own usage points at: enough tokens to cover roughly a
 * month at the rate they have been spending this week. Falls back to the
 * largest pack when even that is not enough.
 */
function suggestedPlanId(plans, tokensThisWeek) {
  if (!plans?.length || !tokensThisWeek) return null;
  const projectedMonth = tokensThisWeek * 4;
  const covers = plans.find((p) => p.tokens >= projectedMonth);
  return (covers || plans[plans.length - 1]).id;
}

export default function TokenPackagesModal({ isOpen, onClose }) {
  const { tokenBalance, refreshBalance } = useAuth();

  const [currency, setCurrency] = useState(guessCurrency);
  const [activeTab, setActiveTab] = useState(ONE_TIME);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [promoInput, setPromoInput] = useState("");
  const [appliedCode, setAppliedCode] = useState("");
  const [method, setMethod] = useState("upi");
  const [purchaseError, setPurchaseError] = useState("");
  const [processing, setProcessing] = useState(false);
  const modalRef = useRef(null);

  // Prices, plans, methods and promo codes all come from the server.
  const catalogReq = useApi(() => api.tokens.catalog(currency), [currency]);
  const catalog = catalogReq.data;

  // Usage drives the "based on your usage" suggestion. A failure here costs a
  // hint, not the modal, so its error is deliberately ignored.
  const usageReq = useApi(() => api.tokens.usage(), []);
  const tokensThisWeek = useMemo(
    () => (usageReq.data || []).reduce((sum, d) => sum + (d.tokens || 0), 0),
    [usageReq.data]
  );

  const plans = useMemo(() => {
    if (!catalog) return [];
    return activeTab === ONE_TIME ? catalog.one_time : catalog.subscriptions;
  }, [catalog, activeTab]);

  const oneTimePlans = catalog?.one_time || [];
  const bestValueId = useMemo(() => bestValuePlanId(oneTimePlans), [oneTimePlans]);
  const suggestedId = useMemo(
    () => suggestedPlanId(oneTimePlans, tokensThisWeek),
    [oneTimePlans, tokensThisWeek]
  );

  // Pick a default once the catalogue lands, and again whenever the tab changes,
  // since plan ids do not carry across tabs.
  useEffect(() => {
    if (!plans.length) return;
    if (plans.some((p) => p.id === selectedPlan)) return;
    const preferred =
      (activeTab === ONE_TIME && tokenBalance <= LOW_BALANCE_THRESHOLD && suggestedId) ||
      plans.find((p) => p.popular)?.id ||
      plans[0].id;
    setSelectedPlan(preferred);
  }, [plans, selectedPlan, activeTab, suggestedId, tokenBalance]);

  // The only place a total comes from. The client sends the plan and the code;
  // the server decides what the code is worth and what is owed.
  const quoteReq = useApi(
    () =>
      selectedPlan
        ? api.tokens.quote(selectedPlan, { currency, promoCode: appliedCode })
        : Promise.resolve(null),
    [selectedPlan, currency, appliedCode]
  );
  const quote = quoteReq.data;

  const eligibleIds = useMemo(
    () => new Set((quote?.eligible_methods || []).map((m) => m.id)),
    [quote]
  );

  // Keep the selected method payable: switching to a cheaper plan can drop EMI.
  useEffect(() => {
    if (!quote || eligibleIds.has(method)) return;
    setMethod(quote.eligible_methods[0]?.id || "upi");
  }, [quote, eligibleIds, method]);

  useEffect(() => {
    const onKeyDown = (e) => { if (e.key === "Escape") onClose(); };
    if (isOpen) {
      document.addEventListener("keydown", onKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  useEffect(() => { if (isOpen) modalRef.current?.focus(); }, [isOpen]);

  const applyPromo = useCallback(() => {
    setPurchaseError("");
    setAppliedCode(promoInput.trim().toUpperCase());
  }, [promoInput]);

  const clearPromo = useCallback(() => {
    setAppliedCode("");
    setPromoInput("");
  }, []);

  const handlePurchase = useCallback(async () => {
    if (!selectedPlan) return;
    setProcessing(true);
    setPurchaseError("");
    try {
      await api.tokens.purchase(selectedPlan);
      // Only reachable once a gateway confirms payment server-side. Re-read the
      // balance rather than adding the pack's tokens locally.
      await refreshBalance();
      onClose();
    } catch (err) {
      // Show what the server said, including "payments are not available yet".
      setPurchaseError(err.message || "Could not complete that purchase.");
    } finally {
      setProcessing(false);
    }
  }, [selectedPlan, refreshBalance, onClose]);

  if (!isOpen) return null;

  const promoAccepted = Boolean(quote?.promo_code);
  const promoError = quote?.promo_error || "";
  const lowBalance = tokenBalance <= LOW_BALANCE_THRESHOLD;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal" ref={modalRef} tabIndex={-1} onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2 id="modal-title" className="modal-title">Top up your tokens</h2>
          <div className="modal-head-right">
            {catalog?.currencies?.length > 1 && (
              <label className="currency-select">
                <span className="sr-only">Currency</span>
                <select
                  value={catalog.currency.code}
                  onChange={(e) => setCurrency(e.target.value)}
                  aria-label="Currency"
                >
                  {catalog.currencies.map((c) => (
                    <option key={c.code} value={c.code}>{c.symbol} {c.code}</option>
                  ))}
                </select>
              </label>
            )}
            <button className="modal-close" onClick={onClose} aria-label="Close">
              <Icon name="x" size={20} />
            </button>
          </div>
        </header>

        {purchaseError && (
          <div className="modal-error" role="alert">
            <Icon name="alertCircle" size={18} />
            <span>{purchaseError}</span>
          </div>
        )}

        <div className="modal-body">
          {lowBalance && (
            <div className="tp-nudge">
              <Icon name="coin" size={16} />
              <span>
                {tokenBalance <= 0
                  ? "You are out of tokens. Pick a pack to carry on pitching."
                  : `${tokenBalance} tokens left — under one full pitch. Top up in one step.`}
              </span>
            </div>
          )}

          {catalogReq.loading ? (
            <div className="packages-list" aria-hidden="true">
              {[0, 1, 2].map((i) => (
                <div key={i} className="package-row">
                  <div className="db-skeleton db-skeleton-title" />
                  <div className="db-skeleton db-skeleton-line" />
                </div>
              ))}
            </div>
          ) : catalogReq.error ? (
            <div className="tp-unavailable" role="alert">
              <Icon name="alertCircle" size={20} />
              <p>Could not load pricing. {catalogReq.error.message}</p>
              <button className="btn btn-ghost btn-sm" onClick={catalogReq.reload}>
                <Icon name="refresh" size={14} /> Try again
              </button>
            </div>
          ) : (
            <>
              <div className="tabs" role="tablist">
                {[
                  [ONE_TIME, "One-time packs"],
                  [SUBSCRIPTION, "Monthly plans"],
                ].map(([tab, label]) => (
                  <button
                    key={tab}
                    role="tab"
                    aria-selected={activeTab === tab}
                    className={`tab ${activeTab === tab ? "active" : ""}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {label}
                  </button>
                ))}
              </div>

              <div className="packages-list" role="radiogroup" aria-label="Token plans">
                {plans.map((plan) => {
                  const tags = [];
                  if (plan.popular) tags.push(plan.badge || "Most popular");
                  else if (plan.badge) tags.push(plan.badge);
                  if (activeTab === ONE_TIME && plan.id === bestValueId) tags.push("Lowest per token");
                  if (activeTab === ONE_TIME && plan.id === suggestedId) tags.push("Matches your usage");

                  return (
                    <label
                      key={plan.id}
                      className={`package-row ${selectedPlan === plan.id ? "selected" : ""} ${plan.popular ? "popular" : ""}`}
                    >
                      <input
                        type="radio"
                        name="token-plan"
                        value={plan.id}
                        checked={selectedPlan === plan.id}
                        onChange={() => setSelectedPlan(plan.id)}
                        className="package-radio"
                      />
                      <div className="package-info">
                        <div className="package-header">
                          <h3 className="package-name">{plan.name}</h3>
                          <div className="package-tokens">
                            <span className="tokens-count">{plan.tokens}</span>
                            <span className="tokens-label">
                              {plan.interval ? `tokens / ${plan.interval}` : "tokens"}
                            </span>
                          </div>
                        </div>
                        <p className="package-desc">{plan.description}</p>
                        {tags.length > 0 && (
                          <div className="package-tags">
                            {tags.map((t) => (
                              <span key={t} className={`package-badge ${plan.popular && t === tags[0] ? "is-popular" : ""}`}>
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="package-price">
                        <span className="final-price">{plan.amount_display}</span>
                        {plan.interval && <span className="interval">/{plan.interval}</span>}
                      </div>
                    </label>
                  );
                })}
              </div>

              {/* Promo codes are validated server-side; this only carries the
                  code there and shows the verdict that comes back. */}
              <div className="promo-section">
                {promoAccepted ? (
                  <div className="promo-applied">
                    <span>{quote.promo_code} applied — {quote.promo_description}</span>
                    <button type="button" className="promo-remove" onClick={clearPromo} aria-label="Remove code">
                      <Icon name="x" size={14} />
                    </button>
                  </div>
                ) : (
                  <div className="promo-input">
                    <input
                      type="text"
                      placeholder="Promo code"
                      value={promoInput}
                      onChange={(e) => setPromoInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); applyPromo(); } }}
                      className="promo-input-field"
                      aria-label="Promo code"
                      aria-invalid={Boolean(promoError)}
                    />
                    <button className="btn btn-ghost btn-sm" onClick={applyPromo} disabled={!promoInput.trim()}>
                      Apply
                    </button>
                  </div>
                )}
                {promoError && <span className="promo-error" role="alert">{promoError}</span>}
                {!promoAccepted && !promoError && catalog.promotions.length > 0 && (
                  <ul className="promo-hints">
                    {catalog.promotions.map((p) => (
                      <li key={p.code}>
                        <b>{p.active ? p.code : "Soon"}</b> {p.description}
                        {p.expires_on && <i> · until {p.expires_on}</i>}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="payment-methods">
                <h4 className="section-label">Payment method</h4>
                <div className="payment-method-grid">
                  {catalog.payment_methods.map((m) => {
                    const allowed = !quote || eligibleIds.has(m.id);
                    return (
                      <button
                        key={m.id}
                        type="button"
                        className={`payment-method ${method === m.id ? "selected" : ""} ${allowed ? "" : "disabled"}`}
                        onClick={() => allowed && setMethod(m.id)}
                        disabled={!allowed}
                        title={allowed ? m.description : `Needs an order over ₹${m.min_amount_inr}`}
                      >
                        <div className="payment-method-icon"><Icon name={m.icon} size={20} /></div>
                        <span className="payment-method-name">{m.name}</span>
                      </button>
                    );
                  })}
                </div>
                <p className="payment-method-note">
                  {method === "emi"
                    ? `EMI over ${catalog.emi_tenures.join(", ")} months.`
                    : catalog.payment_methods.find((m) => m.id === method)?.description}
                </p>
              </div>

              {/* Every figure below is quoted by the server. */}
              <div className="package-summary">
                {quoteReq.loading || !quote ? (
                  <div className="db-skeleton db-skeleton-block" aria-hidden="true" />
                ) : (
                  <>
                    <div className="summary-row">
                      <span>Current balance</span>
                      <span><strong>{tokenBalance}</strong> tokens</span>
                    </div>
                    <div className="summary-row">
                      <span>Tokens added</span>
                      <span><strong>+{quote.tokens}</strong>{quote.tokens ? ` → ${quote.balance_after}` : ""}</span>
                    </div>
                    <div className="summary-row">
                      <span>Full pitches you could run</span>
                      <span>
                        <strong>{quote.pitches_after}</strong>
                        <span className="summary-muted"> (from {pitchesAffordable(tokenBalance)})</span>
                      </span>
                    </div>
                    {quote.discount_minor > 0 && (
                      <>
                        <div className="summary-row">
                          <span>List price</span>
                          <span className="original-price">{quote.list_display}</span>
                        </div>
                        <div className="summary-row discount">
                          <span>Discount {quote.promo_code ? `(${quote.promo_code})` : ""}</span>
                          <span>−{quote.discount_display}</span>
                        </div>
                      </>
                    )}
                    <div className="summary-row total">
                      <span>Total</span>
                      <span><strong>{quote.total_display}</strong></span>
                    </div>
                  </>
                )}
              </div>

              <p className="tp-rate">
                {catalog.tokens_per_message} tokens per answer · {catalog.tokens_per_pitch} for a full
                {" "}5-step pitch.
              </p>
            </>
          )}
        </div>

        <footer className="modal-footer">
          <button className="btn btn-ghost btn-block" onClick={onClose} disabled={processing}>
            Cancel
          </button>
          <button
            className="btn btn-primary-dark btn-block"
            onClick={handlePurchase}
            disabled={processing || !quote || quoteReq.loading}
          >
            {processing ? (
              <><span className="spinner" aria-hidden="true" /> Processing</>
            ) : (
              <>Proceed to pay{quote ? ` — ${quote.total_display}` : ""}</>
            )}
          </button>
        </footer>

        <p className="modal-note">
          A payment provider is not connected yet, so checkout will decline. Prices,
          discounts and balances are all confirmed by the server.
        </p>
      </div>
    </div>
  );
}
