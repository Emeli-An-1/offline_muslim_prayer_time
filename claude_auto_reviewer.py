import os
import anthropic
from tqdm import tqdm
from rich.console import Console
from datetime import datetime

console = Console()

# API Key al
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# --- AI REVIEW PROMPT ---
REVIEW_PROMPT = """
You are a senior Python Flet framework developer.
Analyze the following Python code and:
1. Detect syntax, import, or logic errors.
2. Fix any design or layout issues related to Flet framework.
3. Simplify or optimize the code while preserving its logic.
4. Remove redundant or unused imports.
5. Return the corrected full file code.

Output format strictly as follows:
### Summary
(Short explanation of what was fixed)
### Fixed Code
(Provide the corrected full code below)
"""

def review_file(file_path, output_dir):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Claude API çağrısı
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": REVIEW_PROMPT + "\n\nHere is the file content:\n\n" + code}
            ]
        )

        result = response.content[0].text

        # Kaydet
        file_name = os.path.basename(file_path)
        output_file = os.path.join(output_dir, f"{file_name}_review.txt")

        with open(output_file, "w", encoding="utf-8") as out:
            out.write(result)

        console.print(f"[green]✅ Reviewed:[/green] {file_path}")

    except Exception as e:
        console.print(f"[red]❌ Error reviewing {file_path}: {e}[/red]")


def main():
    base_dir = "."
    output_dir = os.path.join("ai_reviews", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(output_dir, exist_ok=True)

    # .py dosyalarını topla (venv, build, vs hariç)
    python_files = []
    for root, _, files in os.walk(base_dir):
        if any(skip in root for skip in ["venv", "build", "__pycache__", "dist", "ai_reviews"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    console.print(f"[yellow]🔍 Total files to review:[/yellow] {len(python_files)}")

    for path in tqdm(python_files, desc="Reviewing files"):
        review_file(path, output_dir)

    console.print(f"\n[bold green]✅ Review completed![/bold green]")
    console.print(f"Reports saved in: [cyan]{output_dir}[/cyan]")


if __name__ == "__main__":
    main()
