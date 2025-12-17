#!/usr/bin/env python3
"""Quick test of position aggregation with actual positions.json data"""

import json
import sys
sys.path.insert(0, '/home/typeshit/stock_cli')

from src.streamlit_app import aggregate_positions_by_symbol

# Load actual positions
with open('/home/typeshit/stock_cli/positions.json', 'r') as f:
    positions = json.load(f)

print(f"Total positions in file: {len(positions)}")
print("\nPositions by symbol:")
symbol_counts = {}
for pos in positions:
    symbol = pos['symbol']
    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

for symbol, count in symbol_counts.items():
    print(f"  {symbol}: {count} position(s)")

# Aggregate
aggregated = aggregate_positions_by_symbol(positions)

print(f"\n{'='*60}")
print(f"After aggregation: {len(aggregated)} unique stocks")
print(f"{'='*60}\n")

for symbol, data in sorted(aggregated.items()):
    print(f"{symbol}:")
    print(f"  Total Quantity: {data['quantity']:.8f}")
    print(f"  Weighted Avg Price: ${data['purchase_price']:.2f}")
    print(f"  Total Cost: ${data['total_cost']:.2f}")
    print(f"  From {len(data['positions'])} position(s)")
    print()
