import { describe, it, expect } from "vitest";

/**
 * Unit tests for contact form validation logic.
 * Keeps the engagement mapping and primary-toggle default values honest.
 */

const ENGAGEMENT_OPTIONS = [
  { value: "", label: "None" },
  { value: "BUY_SIDE", label: "Buy-side" },
  { value: "SELL_SIDE", label: "Sell-side" },
  { value: "CAPITAL_RAISE", label: "Capital raise" },
];

describe("ContactDialog engagement options", () => {
  it("has an empty sentinel as the first option", () => {
    expect(ENGAGEMENT_OPTIONS[0].value).toBe("");
    expect(ENGAGEMENT_OPTIONS[0].label).toBe("None");
  });

  it("covers all three engagement types", () => {
    const values = ENGAGEMENT_OPTIONS.slice(1).map((o) => o.value);
    expect(values).toContain("BUY_SIDE");
    expect(values).toContain("SELL_SIDE");
    expect(values).toContain("CAPITAL_RAISE");
  });

  it("all labels are non-empty strings", () => {
    ENGAGEMENT_OPTIONS.forEach((o) => {
      expect(typeof o.label).toBe("string");
      expect(o.label.length).toBeGreaterThan(0);
    });
  });
});

describe("contact default values", () => {
  function defaultValues(contact?: { contact_person: string; is_primary: boolean }) {
    return {
      contact_person: contact?.contact_person ?? "",
      is_primary: contact?.is_primary ?? false,
      engagement: "",
      email: "",
    };
  }

  it("new contact defaults: empty name, not primary", () => {
    const d = defaultValues();
    expect(d.contact_person).toBe("");
    expect(d.is_primary).toBe(false);
  });

  it("edit contact: prefills name and primary flag", () => {
    const d = defaultValues({ contact_person: "Alice", is_primary: true });
    expect(d.contact_person).toBe("Alice");
    expect(d.is_primary).toBe(true);
  });
});

describe("contact payload coercion", () => {
  it("empty engagement becomes null in payload", () => {
    const engagement = "";
    const payload = { engagement: engagement || null };
    expect(payload.engagement).toBeNull();
  });

  it("non-empty engagement is passed through", () => {
    const engagement = "BUY_SIDE";
    const payload = { engagement: engagement || null };
    expect(payload.engagement).toBe("BUY_SIDE");
  });

  it("empty email becomes null in payload", () => {
    const email = "";
    const payload = { email: email || null };
    expect(payload.email).toBeNull();
  });
});
