#!/usr/bin/env python3
"""
Basic example: Compose a Matt prompt and interpret an architecture response.

This demonstrates the core organ interface without requiring LLM calls.
"""

import sys
import os

# Add parent directory to path so we can import organ
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import organ


def main():
    print("=" * 60)
    print("Matt Persona Organ — Basic Architecture Review")
    print("=" * 60)

    # Define the work state
    state = {
        "variant": "v1",
        "knowledge_text": """
Current system:
- Request throughput: 10k req/s (peak)
- Database latency: 150ms avg
- Single availability zone
- Cache hit rate: 70%
- Query log shows database at 95% CPU during peak
""",
        "directive": "Assess scalability for 10x growth to 100k req/s",
        "capabilities_summary": "Can analyze system metrics, design improvements, review trade-offs",
    }

    context = {
        "platform_identity": "DataFlow Advisory — AI-powered discovery engine for enterprise knowledge work",
    }

    # Compose the prompt
    print("\n1. COMPOSING PROMPT (v1_general_session variant)")
    print("-" * 60)

    composed = organ.compose(state, context)
    print(f"Model: {composed['model']}")
    print(f"\nPrompt (first 300 chars):\n{composed['prompt'][:300]}...")

    # Simulate a Matt response
    print("\n2. SIMULATING MATT'S RESPONSE")
    print("-" * 60)

    fake_response = """
Architecture scalability assessment:

**Current Bottlenecks:**
1. Database query latency at 150ms — single database, no read replicas
2. Cache hit rate at 70% — need distributed cache cluster
3. Single AZ deployment — no geographic redundancy
4. CPU maxing out at peak load suggests vertical scaling limits

**Capacity Requirements:**
- 10x growth: 10k → 100k req/s
- Database needs to handle 100k queries/s with <50ms latency
- Network bandwidth: estimate 100Mbps sustained

**Recommended Architecture Changes:**
1. Multi-database with read replicas (PostgreSQL Streaming Replication)
2. Distributed cache layer (Redis Cluster with 3 nodes)
3. Multi-AZ deployment across AWS regions
4. API rate limiting and circuit breakers

**Trade-offs:**
- Complexity increases significantly but resilience improves
- Cost increase ~2-3x but throughput capacity increases 10x
- Implementation timeline: 4-6 months

**Confidence Level:** High. These are proven patterns at this scale.
"""

    print(fake_response)

    # Interpret the response
    print("\n3. INTERPRETING RESPONSE")
    print("-" * 60)

    interpreted = organ.interpret(state, context, fake_response)
    print(f"Confidence (self_metric): {interpreted['self_metric']}/10")
    print(f"Rationale: {interpreted['rationale']}")
    print(f"\nFull rationale: {interpreted['output'][:200]}...")


if __name__ == "__main__":
    main()
