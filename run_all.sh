#!/bin/bash

echo "================================"
echo "UAF Dirac Agent - Full Validation"
echo "================================"

echo -e "\n[1/2] Running validation tests..."
python test_validation.py

echo -e "\n[2/2] Running simulation scenarios..."
python test_simulation.py

echo -e "\n================================"
echo "All tests completed!"
echo "================================"
