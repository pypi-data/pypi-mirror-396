"""Debug script to test run_command with TypeScript slow script."""

from cli.commands import run_command

if __name__ == "__main__":
    # Call run_command without API key (no_analysis will be True implicitly)
    success = run_command(
        script_path="/Users/luftig-personal/Software/projects/aiprofile/aiprofile-cli/examples/typescript/slow_script.js",
        script_args=[],
        duration=10,  # 10 seconds
        no_analysis=True,  # Skip AI analysis (no API key needed)
        api_key=None,
        web_url=None,
    )
