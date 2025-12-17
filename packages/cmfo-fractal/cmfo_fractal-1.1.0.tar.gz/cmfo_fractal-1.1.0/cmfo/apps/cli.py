"""
CMFO Interactive Suite
======================

The central hub for running CMFO applications and demos.
"""

import sys
import os
import time
from .. import verify
from ..bridges import analyze_dispersion_relation, analyze_gate_entropy, landauer_cost, analyze_level_spacings
from .neuron import FractalNeuron
import numpy as np

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Colors.HEADER + Colors.BOLD)
    print("      CMFO FRACTAL SUITE v1.0.0      ")
    print("=====================================")
    print("   The Geometry of Intelligence      ")
    print(Colors.ENDC)

def run_ai_demo():
    print(Colors.OKCYAN + "\n[APP] FRACTAL NEURON STUDIO" + Colors.ENDC)
    print("Training a generic Fractal Neuron on XOR Logic...")
    
    inputs = [[0.1, 0.1], [0.1, 0.9], [0.9, 0.1], [0.9, 0.9]]
    labels = [0, 1, 1, 0]
    
    neuron = FractalNeuron(input_dim=2)
    print("Initial Weights (Phi-Aligned):", neuron.weights)
    
    # Quick Viz Loop
    best_acc = 0
    symbols = ['-', '\\', '|', '/']
    
    for i in range(50):
        # Spinner
        sys.stdout.write(f"\rTraining Epoch {i+1}/50... {symbols[i%4]}")
        sys.stdout.flush()
        
        # Perturb
        old_w = neuron.weights.copy()
        neuron.weights += np.random.uniform(-0.2, 0.2, 2)
        
        correct = 0
        for x, y in zip(inputs, labels):
            if neuron.predict(x) == y: correct += 1
        acc = correct/4.0
        
        if acc >= best_acc:
            best_acc = acc
        else:
            neuron.weights = old_w
            
        time.sleep(0.05) 
        
    print(f"\n\n{Colors.OKGREEN}Best Accuracy Achieved: {best_acc*100}%{Colors.ENDC}")
    print("Weights:", neuron.weights)
    input("\nPress Enter to return...")

def run_physics_lab():
    print(Colors.OKCYAN + "\n[APP] FRACTAL PHYSICS LAB" + Colors.ENDC)
    print("Analyzing 7D Manifold Properties...\n")
    
    # Relativity
    print("1. RUNNING RELATIVITY CHECK...")
    res = analyze_dispersion_relation()[-1]
    print(f"   Delta-Gamma at {res['v_c']:.2f}c: {res['divergence']:.4f}")
    
    # Thermo
    print("\n2. RUNNING THERMODYNAMICS CHECK...")
    loss = analyze_gate_entropy("Rhombus_Process")
    print(f"   Rhombus Entropy Loss: {loss['entropy_loss_bits']} bits (Reversible)")
    
    # Chaos
    print("\n3. RUNNING QUANTUM CHAOS CHECK...")
    stats = analyze_level_spacings(max_n=3)
    print(f"   Spectral Variance: {stats['variance']:.4f} ({stats['regime']})")
    
    input("\nPress Enter to return...")

def main_menu():
    while True:
        print_header()
        print("1. Launch Fractal Neuron AI (Demo)")
        print("2. Run Physics & Topology Lab (Analysis)")
        print("3. Run Full System Verification (Test Suite)")
        print("4. Exit")
        
        choice = input(f"\n{Colors.OKBLUE}Select Application [1-4]: {Colors.ENDC}")
        
        if choice == '1':
            run_ai_demo()
        elif choice == '2':
            run_physics_lab()
        elif choice == '3':
            verify.run(json_output=False)
            input("\nPress Enter to return...")
        elif choice == '4':
            print("Exiting CMFO Suite.")
            sys.exit(0)
            
if __name__ == "__main__":
    main_menu()
