import { describe, it, expect } from "vitest";

/**
 * Unit tests for mandate list display logic (status labels, stat formatting).
 * Pure functions kept in sync with the mandates page rendering.
 */

const TYPE_LABELS: Record<string, string> = {
  SELL_SIDE: "Sell-side",
  BUY_SIDE: "Buy-side",
  CAPITAL_RAISE: "Capital raise",
};

function statusLabel(status: string): string {
  return status.replace("_", " ").toLowerCase();
}

function respondedPctLabel(rate: number): string {
  return `${Math.round(rate * 100)}%`;
}

describe("mandate type labels", () => {
  it("maps all three engagement types", () => {
    expect(TYPE_LABELS.SELL_SIDE).toBe("Sell-side");
    expect(TYPE_LABELS.BUY_SIDE).toBe("Buy-side");
    expect(TYPE_LABELS.CAPITAL_RAISE).toBe("Capital raise");
  });
});

describe("mandate status label", () => {
  it("humanizes enum values", () => {
    expect(statusLabel("ACTIVE")).toBe("active");
    expect(statusLabel("ON_HOLD")).toBe("on hold");
    expect(statusLabel("TERMINATED")).toBe("terminated");
  });
});

describe("responded pct formatting", () => {
  it("renders a rounded percentage", () => {
    expect(respondedPctLabel(0)).toBe("0%");
    expect(respondedPctLabel(0.3125)).toBe("31%");
    expect(respondedPctLabel(1)).toBe("100%");
  });
});
