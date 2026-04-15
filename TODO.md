# Optimization Fixes TODO

## Status: In Progress

### 1. [x] Robust CSV parser (csv_service.py)

### 2. [x] API fixes (optimize.py)

### 3. [x] Schema (product.py)

### 4. [x] Pipeline/cap expand/packing perf (optimization/packing_engine.py)

### 5. [x] Packing engine (packing_engine.py)

### 6. [x] GA optimizer (genetic_optimizer.py)
   - Heuristic fitness (99% packs saved)
   - Dynamic pop/gens, early stop
   - Tuned constants

### 7. [ ] Minor: constants.py, shipment_service.py

### 8. [ ] Test: docker-compose up, API calls
   - Malformed CSV, large inputs
   - Perf timings

**Next Step:** Implement CSV parser fixes.
