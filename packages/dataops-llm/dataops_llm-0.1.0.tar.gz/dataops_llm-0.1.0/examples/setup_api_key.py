"""Quick setup script to configure your API key."""

import os
from pathlib import Path

print("=" * 60)
print("DataOps LLM Engine - API Key Setup")
print("=" * 60)

# Check if .env exists
env_path = Path(".env")

if not env_path.exists():
    print("\n❌ .env file not found!")
    print("Creating .env from template...")

    # Copy from example
    if Path(".env.example").exists():
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file")
    else:
        print("❌ .env.example not found!")
        exit(1)

print("\n" + "=" * 60)
print("API Key Options:")
print("=" * 60)
print("\n1. OpenAI (GPT-4)")
print("   - Website: https://platform.openai.com/api-keys")
print("   - Key format: sk-proj-...")
print("   - Cost: ~$0.10 per operation")
print("\n2. Anthropic (Claude)")
print("   - Website: https://console.anthropic.com/settings/keys")
print("   - Key format: sk-ant-api03-...")
print("   - Cost: ~$0.05 per operation")
print("\n3. Google (Gemini)")
print("   - Website: https://makersuite.google.com/app/apikey")
print("   - Key format: varies")
print("   - Cost: FREE TIER AVAILABLE!")

print("\n" + "=" * 60)

# Get user input
choice = input("\nWhich provider? (1/2/3): ").strip()

if choice == "1":
    model = "gpt-4"
    print("\n📝 Go to: https://platform.openai.com/api-keys")
elif choice == "2":
    model = "claude-3-5-sonnet-20241022"
    print("\n📝 Go to: https://console.anthropic.com/settings/keys")
elif choice == "3":
    model = "gemini-pro"
    print("\n📝 Go to: https://makersuite.google.com/app/apikey")
else:
    print("❌ Invalid choice")
    exit(1)

api_key = input("\nPaste your API key here: ").strip()

if not api_key:
    print("❌ No API key provided!")
    exit(1)

# Update .env file
print("\n📝 Updating .env file...")

with open(".env", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("LITELLM_API_KEY="):
        new_lines.append(f"LITELLM_API_KEY={api_key}\n")
    elif line.startswith("LITELLM_MODEL="):
        new_lines.append(f"LITELLM_MODEL={model}\n")
    else:
        new_lines.append(line)

with open(".env", "w") as f:
    f.writelines(new_lines)

print("✅ Configuration saved!")
print("\n" + "=" * 60)
print("Setup Complete!")
print("=" * 60)
print("\n✅ Your API key has been configured")
print(f"✅ Model set to: {model}")
print("\n🚀 You're ready to go! Run:")
print("   python test_quick.py")
print("\n" + "=" * 60)
