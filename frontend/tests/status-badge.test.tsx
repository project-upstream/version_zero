import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { cadenceStateFromSchedule, StatusBadge } from "@/components/features/status-badge";

describe("StatusBadge", () => {
  it("renders a human label for a status enum", () => {
    render(<StatusBadge status="NOT_CONTACTED" />);
    expect(screen.getByText("Not contacted")).toBeInTheDocument();
  });

  it("renders Responded", () => {
    render(<StatusBadge status="RESPONDED" />);
    expect(screen.getByText("Responded")).toBeInTheDocument();
  });
});

describe("cadenceStateFromSchedule", () => {
  it("maps AWAITING_INITIAL to needs_initial", () => {
    expect(
      cadenceStateFromSchedule({ scheduleStatus: "AWAITING_INITIAL", daysRemaining: null }),
    ).toBe("needs_initial");
  });

  it("maps negative days_remaining to overdue", () => {
    expect(
      cadenceStateFromSchedule({ scheduleStatus: "ACTIVE", daysRemaining: -2 }),
    ).toBe("overdue");
  });

  it("maps small positive days_remaining to due_soon", () => {
    expect(
      cadenceStateFromSchedule({ scheduleStatus: "ACTIVE", daysRemaining: 3 }),
    ).toBe("due_soon");
  });

  it("maps far-out days_remaining to upcoming", () => {
    expect(
      cadenceStateFromSchedule({ scheduleStatus: "ACTIVE", daysRemaining: 30 }),
    ).toBe("upcoming");
  });
});
