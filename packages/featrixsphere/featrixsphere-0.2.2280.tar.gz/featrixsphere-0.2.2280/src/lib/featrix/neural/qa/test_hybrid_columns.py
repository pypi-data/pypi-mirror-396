#!/usr/bin/env python3
"""
QA Test: Hybrid Column Detection & Encoding

Tests the hybrid column detection and encoding system with both strategies:
1. MERGE strategy: Addresses and coordinates combined into single encoders
2. RELATIONSHIP strategy: Entity attributes kept separate but marked as related

Tests include:
- Unit tests for HybridColumnDetector
- Unit tests for hybrid encoders
- Integration test: Full training workflow with hybrid columns
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import shutil
import torch

# Paths
test_dir = Path(__file__).parent
neural_dir = test_dir.parent
featrix_dir = neural_dir.parent
lib_dir = featrix_dir.parent
src_dir = lib_dir.parent

# Clear Python bytecode cache
print("🧹 Clearing Python bytecode cache...")
pycache_count = 0
for pycache_dir in lib_dir.rglob("__pycache__"):
    try:
        shutil.rmtree(pycache_dir)
        pycache_count += 1
    except Exception:
        pass

import importlib
importlib.invalidate_caches()
print(f"✅ Cleared {pycache_count} __pycache__ dirs")
print()

sys.path.insert(0, str(lib_dir))
sys.path.insert(0, str(src_dir))

from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.hybrid_column_detector import HybridColumnDetector
from featrix.neural.gpu_utils import set_backend_cpu as set_device_cpu

# Force CPU mode for testing
set_device_cpu()

print("=" * 80)
print("🧪 HYBRID COLUMN DETECTION & ENCODING - QA TEST")
print("=" * 80)
print(f"Started: {datetime.now()}")
print()


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def create_address_dataset():
    """Create test dataset with shipping and billing addresses."""
    np.random.seed(42)
    n = 100
    
    cities = ['Boston', 'Seattle', 'Denver', 'Austin', 'Portland', 'Miami', 'Chicago', 'Phoenix']
    states = ['MA', 'WA', 'CO', 'TX', 'OR', 'FL', 'IL', 'AZ']
    streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr', 'Elm St', 'Cedar Ln', 'Birch Way']
    
    data = {
        'order_id': range(1, n + 1),
        'shipping_addr1': [f"{np.random.randint(100, 999)} {np.random.choice(streets)}" for _ in range(n)],
        'shipping_city': np.random.choice(cities, n),
        'shipping_state': np.random.choice(states, n),
        'shipping_zip': [f"{np.random.randint(10000, 99999)}" for _ in range(n)],
        'billing_addr1': [f"{np.random.randint(100, 999)} {np.random.choice(streets)}" for _ in range(n)],
        'billing_city': np.random.choice(cities, n),
        'billing_state': np.random.choice(states, n),
        'amount': np.random.uniform(50, 500, n).round(2),
        'item_count': np.random.randint(1, 10, n),
        'is_express': np.random.choice(['yes', 'no'], n)
    }
    return pd.DataFrame(data)


def create_coordinates_dataset():
    """Create test dataset with HQ and office coordinates."""
    np.random.seed(42)
    n = 100
    
    # Major US cities coordinates
    cities = [
        ('Boston', 42.3601, -71.0589),
        ('Seattle', 47.6062, -122.3321),
        ('Denver', 37.7749, -104.9903),
        ('Austin', 30.2672, -97.7431),
        ('Chicago', 41.8781, -87.6298),
    ]
    
    data = {
        'company_id': range(1, n + 1),
        'company_name': [f"Company_{i}" for i in range(n)],
        'hq_lat': [cities[i % len(cities)][1] + np.random.uniform(-0.1, 0.1) for i in range(n)],
        'hq_long': [cities[i % len(cities)][2] + np.random.uniform(-0.1, 0.1) for i in range(n)],
        'office_lat': [cities[(i + 1) % len(cities)][1] + np.random.uniform(-0.1, 0.1) for i in range(n)],
        'office_long': [cities[(i + 1) % len(cities)][2] + np.random.uniform(-0.1, 0.1) for i in range(n)],
        'revenue': np.random.randint(100000, 10000000, n),
        'employee_count': np.random.randint(10, 1000, n),
        'industry': np.random.choice(['tech', 'finance', 'retail', 'manufacturing'], n)
    }
    return pd.DataFrame(data)


def create_entity_dataset():
    """Create test dataset with customer and product entity attributes."""
    np.random.seed(42)
    n = 150
    
    data = {
        'transaction_id': range(1, n + 1),
        'customer_id': np.random.randint(100, 200, n),
        'customer_name': [f"Customer_{i}" for i in np.random.randint(100, 200, n)],
        'customer_type': np.random.choice(['enterprise', 'smb', 'startup'], n),
        'customer_since': pd.date_range('2020-01-01', periods=n, freq='2D').astype(str),
        'product_id': np.random.randint(500, 600, n),
        'product_name': [f"Product_{i}" for i in np.random.randint(500, 600, n)],
        'product_category': np.random.choice(['hardware', 'software', 'service'], n),
        'quantity': np.random.randint(1, 50, n),
        'unit_price': np.random.uniform(10, 500, n).round(2),
        'total_amount': [0.0] * n  # Will be calculated
    }
    # Calculate total_amount
    df = pd.DataFrame(data)
    df['total_amount'] = (df['quantity'] * df['unit_price']).round(2)
    return df


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_unit_hybrid_detection():
    """Unit test: Hybrid column detector pattern matching."""
    print("\n" + "="*80)
    print("TEST 1: Unit Test - Hybrid Column Detection")
    print("="*80)
    
    detector = HybridColumnDetector(use_llm=False)
    
    # Test 1A: Address detection
    print("\n1A: Testing address pattern detection...")
    df_addr = create_address_dataset()
    col_types = {col: 'string' for col in df_addr.columns if 'addr' in col or 'city' in col or 'state' in col}
    col_types.update({col: 'scalar' for col in df_addr.columns if col in ['amount', 'item_count', 'order_id']})
    col_types['is_express'] = 'set'
    
    groups = detector.detect(df_addr, col_types)
    
    addr_groups = {k: v for k, v in groups.items() if v.get('type') == 'address'}
    print(f"   Found {len(addr_groups)} address groups")
    
    # Should detect shipping and billing addresses
    assert len(addr_groups) >= 2, f"Expected at least 2 address groups, found {len(addr_groups)}"
    
    # Check for shipping and billing prefixes
    prefixes = {g['prefix'] for g in addr_groups.values()}
    assert 'shipping' in prefixes, f"Missing 'shipping' prefix, found: {prefixes}"
    assert 'billing' in prefixes, f"Missing 'billing' prefix, found: {prefixes}"
    
    # Verify strategy is MERGE
    for group_name, group_info in addr_groups.items():
        assert group_info['strategy'] == 'merge', f"Address group should use MERGE strategy, got {group_info['strategy']}"
        print(f"   ✅ {group_name}: {group_info['columns']} (prefix={group_info['prefix']})")
    
    # Test 1B: Coordinate detection
    print("\n1B: Testing coordinate pattern detection...")
    df_coord = create_coordinates_dataset()
    col_types_coord = {}
    for col in df_coord.columns:
        if 'lat' in col or 'long' in col:
            col_types_coord[col] = 'scalar'
        elif col in ['revenue', 'employee_count', 'company_id']:
            col_types_coord[col] = 'scalar'
        else:
            col_types_coord[col] = 'string'
    
    groups_coord = detector.detect(df_coord, col_types_coord)
    
    coord_groups = {k: v for k, v in groups_coord.items() if v.get('type') == 'coordinates'}
    print(f"   Found {len(coord_groups)} coordinate groups")
    
    # Should detect hq and office coordinate pairs
    assert len(coord_groups) >= 2, f"Expected at least 2 coordinate groups, found {len(coord_groups)}"
    
    # Verify strategy is MERGE
    for group_name, group_info in coord_groups.items():
        assert group_info['strategy'] == 'merge', f"Coordinate group should use MERGE strategy"
        assert len(group_info['columns']) == 2, f"Coordinate group should have exactly 2 columns"
        print(f"   ✅ {group_name}: {group_info['columns']} (prefix={group_info['prefix']})")
    
    # Test 1C: Entity detection
    print("\n1C: Testing entity pattern detection...")
    df_entity = create_entity_dataset()
    col_types_entity = {}
    for col in df_entity.columns:
        if 'id' in col or 'quantity' in col or 'price' in col or 'amount' in col:
            col_types_entity[col] = 'scalar'
        elif 'since' in col:
            col_types_entity[col] = 'timestamp'
        else:
            col_types_entity[col] = 'set'  # customer_type, product_category, names
    
    groups_entity = detector.detect(df_entity, col_types_entity)
    
    entity_groups = {k: v for k, v in groups_entity.items() if v.get('type') == 'entity'}
    print(f"   Found {len(entity_groups)} entity groups")
    
    # Should detect customer and product entity groups
    assert len(entity_groups) >= 2, f"Expected at least 2 entity groups, found {len(entity_groups)}"
    
    # Verify strategy is RELATIONSHIP
    prefixes_entity = set()
    for group_name, group_info in entity_groups.items():
        assert group_info['strategy'] == 'relationship', f"Entity group should use RELATIONSHIP strategy"
        prefixes_entity.add(group_info['prefix'])
        print(f"   ✅ {group_name}: {group_info['columns']} (prefix={group_info['prefix']})")
    
    # Check for customer and product prefixes
    assert 'customer' in prefixes_entity, f"Missing 'customer' prefix, found: {prefixes_entity}"
    assert 'product' in prefixes_entity, f"Missing 'product' prefix, found: {prefixes_entity}"
    
    print("\n✅ All unit tests passed!")
    return True


def test_unit_input_dataset_integration():
    """Unit test: Integration with FeatrixInputDataSet."""
    print("\n" + "="*80)
    print("TEST 2: Unit Test - FeatrixInputDataSet Integration")
    print("="*80)
    
    # Test with address dataset
    print("\n2A: Testing FeatrixInputDataSet with addresses...")
    df_addr = create_address_dataset()
    
    dataset = FeatrixInputDataSet(
        df=df_addr,
        enable_hybrid_detection=True,
        hybrid_detection_use_llm=False
    )
    
    assert hasattr(dataset, 'hybrid_groups'), "FeatrixInputDataSet should have hybrid_groups attribute"
    assert dataset.hybrid_groups is not None, "hybrid_groups should not be None"
    print(f"   ✅ Detected {len(dataset.hybrid_groups)} hybrid groups")
    
    # Verify groups were detected
    assert len(dataset.hybrid_groups) > 0, "Should detect at least one hybrid group"
    
    for group_name, group_info in dataset.hybrid_groups.items():
        print(f"   {group_name}:")
        print(f"      Type: {group_info.get('type')}")
        print(f"      Strategy: {group_info.get('strategy')}")
        print(f"      Columns: {group_info.get('columns')}")
    
    # Test with hybrid detection disabled
    print("\n2B: Testing with hybrid detection disabled...")
    dataset_no_hybrid = FeatrixInputDataSet(
        df=df_addr,
        enable_hybrid_detection=False
    )
    
    assert dataset_no_hybrid.hybrid_groups == {}, "Should have empty hybrid_groups when disabled"
    print("   ✅ hybrid_groups is empty when detection disabled")
    
    print("\n✅ Integration tests passed!")
    return True


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_integration_full_training():
    """Integration test: Full training workflow with hybrid columns."""
    print("\n" + "="*80)
    print("TEST 3: Integration Test - Full Training with Hybrid Columns")
    print("="*80)
    
    # Use address dataset (most interesting for hybrid encoding)
    df = create_address_dataset()
    print(f"\nDataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    
    # Split into train/val
    train_df = df.iloc[:80].copy()
    val_df = df.iloc[80:].copy()
    
    print("\nCreating training dataset...")
    train_dataset = FeatrixInputDataSet(
        df=train_df,
        enable_hybrid_detection=True,
        hybrid_detection_use_llm=False
    )
    
    print(f"✅ Train dataset created")
    print(f"   Hybrid groups: {len(train_dataset.hybrid_groups)}")
    for group_name, group_info in train_dataset.hybrid_groups.items():
        print(f"   - {group_name}: {group_info['type']} ({group_info['strategy']}) - {group_info['columns']}")
    
    print("\nCreating validation dataset...")
    val_dataset = FeatrixInputDataSet(
        df=val_df,
        enable_hybrid_detection=True,
        hybrid_detection_use_llm=False
    )
    print(f"✅ Validation dataset created")
    
    # Create embedding space (this will pass hybrid groups to encoder)
    print("\nCreating embedding space with hybrid columns...")
    try:
        es = EmbeddingSpace(
            train_input_data=train_dataset,
            val_input_data=val_dataset,
            d_model=64,  # Small for testing
            output_debug_label="hybrid_test"
        )
        print("✅ Embedding space created")
        
        # Verify hybrid groups were passed to encoder
        if hasattr(es, 'encoder') and hasattr(es.encoder, 'joint_encoder'):
            joint_encoder = es.encoder.joint_encoder
            if hasattr(joint_encoder, 'hybrid_groups'):
                print(f"✅ Joint encoder received {len(joint_encoder.hybrid_groups)} hybrid groups")
                
                # Check if RELATIONSHIP groups have group embeddings
                relationship_groups = {
                    k: v for k, v in joint_encoder.hybrid_groups.items() 
                    if v.get('strategy') == 'relationship'
                }
                if relationship_groups and hasattr(joint_encoder, 'group_embeddings'):
                    if joint_encoder.group_embeddings is not None:
                        print(f"✅ Group embeddings created for RELATIONSHIP strategy")
                        print(f"   Shape: {joint_encoder.group_embeddings.shape}")
            else:
                print("⚠️  Joint encoder doesn't have hybrid_groups attribute (old version?)")
        
        # Quick training test (just 2 epochs to verify it works)
        print("\nRunning quick training test (2 epochs)...")
        try:
            es.train(n_epochs=2, output_dir=None)
            print("✅ Training completed successfully!")
            print(f"   Final training loss: {es.training_losses[-1]:.4f}")
            print(f"   Final validation loss: {es.validation_losses[-1]:.4f}")
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Embedding space creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Integration test passed!")
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all QA tests for hybrid columns."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    all_passed = True
    
    # Test 1: Unit tests for detection
    try:
        passed = test_unit_hybrid_detection()
        results['tests'].append({
            'name': 'Unit Test - Hybrid Detection',
            'passed': passed,
            'error': None
        })
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['tests'].append({
            'name': 'Unit Test - Hybrid Detection',
            'passed': False,
            'error': str(e)
        })
        all_passed = False
    
    # Test 2: Unit tests for integration
    try:
        passed = test_unit_input_dataset_integration()
        results['tests'].append({
            'name': 'Unit Test - Input Dataset Integration',
            'passed': passed,
            'error': None
        })
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['tests'].append({
            'name': 'Unit Test - Input Dataset Integration',
            'passed': False,
            'error': str(e)
        })
        all_passed = False
    
    # Test 3: Integration test with full training
    try:
        passed = test_integration_full_training()
        results['tests'].append({
            'name': 'Integration Test - Full Training',
            'passed': passed,
            'error': None
        })
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results['tests'].append({
            'name': 'Integration Test - Full Training',
            'passed': False,
            'error': str(e)
        })
        all_passed = False
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for t in results['tests'] if t['passed'])
    total_count = len(results['tests'])
    
    for test in results['tests']:
        status = "✅ PASSED" if test['passed'] else "❌ FAILED"
        print(f"{status}: {test['name']}")
        if test['error']:
            print(f"   Error: {test['error']}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    # Save results
    results_file = test_dir / "hybrid_columns_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

