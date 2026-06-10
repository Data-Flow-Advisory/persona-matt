#!/usr/bin/env python3
"""
A/B test both variants of Matt's architecture approach.

Demonstrates how to run both v1 (general) and v2 (deep-dive) variants
and compare their confidence scores.
"""

import sys
import os

# Add parent directory to path so we can import organ and select_organ
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import organ
import select_organ


def main():
    print("=" * 60)
    print("Matt Persona Organ — A/B Testing Variants")
    print("=" * 60)

    # Shared context and baseline state
    context = {
        "platform_identity": "DataFlow Advisory — AI-powered discovery engine",
    }

    shared_state = {
        "knowledge_text": """
Current database:
- PostgreSQL single instance on AWS RDS
- 1TB dataset
- 10k queries/second at peak
- 150ms average latency
- Query logs show sequential scans on large tables
- No read replicas currently
""",
        "directive": "Design database architecture for 100k queries/second",
        "capabilities_summary": "Can review system metrics, propose architectures, analyze trade-offs",
    }

    # Run V1 (general-purpose variant)
    print("\n" + "=" * 60)
    print("VARIANT V1 (General Architecture Session)")
    print("=" * 60)

    state_v1 = {**shared_state, "variant": "v1"}
    composed_v1 = organ.compose(state_v1, context)
    print(f"\nModel: {composed_v1['model']}")
    print(f"Template: genome/v1_general_session.txt")

    # Simulate V1 response
    response_v1 = """
Database architecture review:

For scaling from 10k to 100k queries/second, the current single-instance PostgreSQL approach won't work. Here's what I'd recommend:

**Core Issues:**
- Single instance is a bottleneck
- Sequential scans suggest missing indexes
- No read replica strategy limits scaling
- 150ms latency indicates insufficient caching

**Solution:**
Use PostgreSQL with streaming replication for read replicas. This lets us distribute read traffic across multiple servers while keeping writes centralized. Deploy a Redis cluster in front for frequently accessed data.

**Why This Approach:**
- Proven at scale with companies like Airbnb and Stripe
- Keeps same database technology (less retraining)
- Supports both read and write scaling
- Manageable operational complexity

**Next Steps:**
1. Profile queries to find the slowest ones
2. Add appropriate indexes
3. Set up read replicas
4. Implement caching layer
"""

    interpreted_v1 = organ.interpret(state_v1, context, response_v1)
    print(f"\nV1 Confidence: {interpreted_v1['self_metric']}/10")
    print(f"V1 Rationale: {interpreted_v1['rationale']}")

    # Run V2 (architecture deep-dive variant)
    print("\n" + "=" * 60)
    print("VARIANT V2 (Architecture Deep-Dive)")
    print("=" * 60)

    state_v2 = {**shared_state, "variant": "v2"}
    composed_v2 = organ.compose(state_v2, context)
    print(f"\nModel: {composed_v2['model']}")
    print(f"Template: genome/v2_architecture_deep_dive.txt")

    # Simulate V2 response (more quantified, more technical)
    response_v2 = """
Database Architecture Deep-Dive:

**Current State Analysis:**
- Throughput: 10k req/s current, need 100k req/s (10x)
- Latency: 150ms avg (target: <50ms)
- Storage: 1TB dataset
- Query pattern: sequential scans dominant → missing indexes

**Failure Modes:**
- Single point of failure: Primary database crash = total outage
- CPU saturation: Already at 95% during peak
- Memory constraints: Large sequential scans evict cache
- Write bottleneck: All writes serialized on primary

**Scaling Path Analysis:**
- 10x throughput requires both horizontal (replicas) and vertical (optimize queries) scaling
- Read replicas can handle read traffic (estimate 70% of load)
- Write traffic still bottlenecked on primary

**Alternative Architectures Evaluated:**
1. PostgreSQL Streaming Replication (chosen)
   - Pros: familiar, proven, single consistency model
   - Cons: writes still centralized, operational complexity
2. Sharded PostgreSQL
   - Pros: horizontal write scaling
   - Cons: application changes required, operational nightmare
3. NoSQL (MongoDB)
   - Pros: horizontal scaling built-in
   - Cons: loses ACID guarantees, data model mismatch
4. Managed service (Aurora)
   - Pros: operational simplicity
   - Cons: vendor lock-in, cost, limited customization

**Recommendation: PostgreSQL with Streaming Replication**

**Technical Implementation:**
1. Add read replicas (minimum 3 for HA)
2. Implement query routing (read vs write)
3. Add distributed caching (Redis 3-node cluster)
4. Query optimization:
   - Index missing columns from WHERE clauses
   - Analyze explain plans for sequential scans
   - Partition large tables if needed
5. Monitoring:
   - Alert on replication lag (>1s)
   - Query latency percentiles (p99 < 100ms)
   - CPU/memory utilization on all nodes

**Trade-off Analysis:**
- Complexity: Medium (operational burden increases)
- Cost: 2-3x increase due to additional instances
- Latency improvement: 150ms → ~40-50ms with optimization
- Resilience: Much better (HA via replicas)
- Time to implement: 4-6 weeks

**Risk Mitigation:**
- Test failover scenario before production
- Implement connection pooling (PgBouncer)
- Set replication timeout conservatively
- Monitor replication lag continuously

**Confidence:** 9/10. This is a well-established pattern for this scale.
"""

    interpreted_v2 = organ.interpret(state_v2, context, response_v2)
    print(f"\nV2 Confidence: {interpreted_v2['self_metric']}/10")
    print(f"V2 Rationale: {interpreted_v2['rationale']}")

    # Compare the variants
    print("\n" + "=" * 60)
    print("VARIANT COMPARISON")
    print("=" * 60)

    comparison = select_organ.select_best_variant(interpreted_v1, interpreted_v2)
    print(f"\nSelected: Variant {comparison['selected'].upper()}")
    print(f"Confidence Delta: {comparison['delta']:.1f} points")
    print(f"Comparison Rationale: {comparison['rationale']}")

    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    if comparison["delta"] > 3:
        print(f"V{comparison['selected'].upper()} is significantly better for this task.")
        print("Use it for this directive.")
    elif comparison["delta"] > 1:
        print(f"V{comparison['selected'].upper()} is slightly better.")
        print("Both are usable; context determines choice.")
    else:
        print("Variants are essentially equivalent.")
        print("Choose based on available resources or preference.")


if __name__ == "__main__":
    main()
