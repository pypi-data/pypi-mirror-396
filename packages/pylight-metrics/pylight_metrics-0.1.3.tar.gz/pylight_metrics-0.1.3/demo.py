import time
from pylight_metrics import fast_timer, count_calls, increment, LockFreeMetricsAggregator

# 1. Initialize the Engine
agg = LockFreeMetricsAggregator()

print("--- 1. Testing Timer (Latency) ---")
@fast_timer("database.query")
def query_db():
    time.sleep(0.1)

query_db()
print("Executed query_db() (Should take ~0.1s)")

print("\n--- 2. Testing Counter (Events) ---")
@count_calls("login.attempt")
def login():
    pass

login()
login()
print("Executed login() 2 times.")

print("\n--- 3. Testing Manual Increment ---")
increment("login.failure", 1, tags={"reason": "bad_password"})
print("Incremented login.failure by 1.")

# FORCE FLUSH (Move data from buffer to storage)
agg.flush()

print("\n--- 4. FINAL OUTPUT (What users will see) ---")

print("\n[Prometheus Format]")
print(agg.export_prometheus())

print("\n[CSV Format]")
print(agg.export_csv())
