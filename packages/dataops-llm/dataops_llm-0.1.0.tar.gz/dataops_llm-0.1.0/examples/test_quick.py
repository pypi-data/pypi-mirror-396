"""Quick test of DataOps LLM Engine."""

import pandas as pd
from dataops_llm import process

print("=" * 60)
print("DataOps LLM Engine - Quick Test")
print("=" * 60)

# Create sample data
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Bob", "Alice"],
    "age": [25, 30, 35, 30, 25],
    "city": ["NYC", "LA", "Chicago", "LA", "NYC"]
})

print("\nOriginal Data:")
print(df)
print(f"\nShape: {df.shape}")

# Process with natural language
print("\n" + "=" * 60)
print("Processing: 'Remove duplicate rows and sort by age'")
print("=" * 60)

result = process(
    file_path=df,
    instruction="Remove duplicate rows and sort by age",
    return_code=True  # Show the generated code
)

print(f"\nSuccess: {result.success}")
print(f"Execution time: {result.execution_time:.2f}s")

if result.success:
    print("\n" + "-" * 60)
    print("RESULT:")
    print("-" * 60)
    print(result.dataframe)
    print(f"\nNew Shape: {result.dataframe.shape}")

    print("\n" + "-" * 60)
    print("REPORT:")
    print("-" * 60)
    print(result.report)

    if result.generated_code:
        print("\n" + "-" * 60)
        print("GENERATED CODE:")
        print("-" * 60)
        print(result.generated_code)

    if result.warnings:
        print("\n" + "-" * 60)
        print("WARNINGS:")
        print("-" * 60)
        for warning in result.warnings:
            print(f"  [Warning] {warning}")
else:
    print("\n" + "-" * 60)
    print("FAILED:")
    print("-" * 60)
    print(result.report)

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
