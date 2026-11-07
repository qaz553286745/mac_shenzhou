#ifndef HASEE_LILU_LOG_RETRY_HPP
#define HASEE_LILU_LOG_RETRY_HPP

// One thread-call owns this state. No retry work runs in a panic/interrupt handler.
struct LiluLogRetryState {
	static constexpr unsigned MaxAttempts = 12;
	static constexpr unsigned TargetSnapshots = 3;
	static constexpr unsigned IntervalSeconds = 3;
	unsigned attempts {0};
	unsigned saved {0};
	bool pending() const { return attempts < MaxAttempts && saved < TargetSnapshots; }
	unsigned slot() const { return saved % 2; }
	void completed(bool success) { ++attempts; if (success) ++saved; }
};
#endif
