with open(r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'BatteryFault_001' in line:
            print(f'Found at line {i}: {repr(line)}')
            if i < len(lines) - 5:
                print("Context:")
                for j in range(max(0, i-2), min(len(lines), i+5)):
                    print(f'  {j}: {repr(lines[j])}')