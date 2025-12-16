from fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any
import asyncio
import json
import base64
from pathlib import Path
import os
import sys
import io
from PIL import Image


def resize_image_bytes(image_data: bytes, scale: float) -> bytes:
    """Resize image bytes by a scale factor."""
    if scale >= 1.0 or scale <= 0.0:
        return image_data

    try:
        with Image.open(io.BytesIO(image_data)) as img:
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            output = io.BytesIO()
            resized_img.save(output, format="PNG")
            return output.getvalue()
    except Exception:
        return image_data


# Try to import droidrun, if not found, add parent directory to sys.path
try:
    import droidrun
except ImportError:
    # This assumes droidrun-mcp is a sibling of droidrun
    # We are in droidrun_mcp/server.py, so we need to go up 2 levels to find the sibling 'droidrun' folder
    sys.path.append(str(Path(__file__).resolve().parents[2] / "droidrun"))

try:
    from .runner import DroidRunner
except ImportError:
    from runner import DroidRunner

# ... (rest of the file)

def main():
    mcp.run()

if __name__ == "__main__":
    main()

mcp = FastMCP("DroidRun")

# Initialize DroidRunner
# We assume config.yaml is in the droidrun package or current working dir
# For now, let's point to the one in the sibling directory if possible, or expect it in CWD
runner = DroidRunner()


@mcp.tool()
async def execute_task(
    instruction: str, apk_path: Optional[str] = None, ctx: Context = None
) -> Dict[str, Any]:
    """
    Execute a natural language task on the connected Android device.

    Args:
        instruction: The task description (e.g., "Open Settings and toggle Wi-Fi").
        apk_path: Optional path to an APK to install. ONLY use this if the user explicitly asks to install/test a specific app file. NOT required for general device control.
    """

    def progress_callback(event: Dict[str, Any]):
        if ctx:
            # Log info to MCP console/client
            if event.get("type") == "status":
                ctx.info(f"Status: {event.get('message')}")
            elif event.get("type") == "event":
                # can choose to be verbose or concise
                details = event.get("details", "")
                # extract a meaningful message if possible in this meaningless life
                ctx.info(f"Event: {event.get('event_type')}")

    result = await runner.run(
        instruction=instruction, apk_path=apk_path, progress_callback=progress_callback
    )

    return {
        "session_id": result.session_id,
        "last_output": result.last_output,
        "success": result.success,
    }


@mcp.tool()
def get_trajectory(session_id: str) -> Dict[str, Any]:
    """
    Retrieve the full trajectory JSON for a given session.

    Args:
        session_id: The session ID returned by execute_task.
    """
    # Locate trajectory file
    # it is important to know where DroidRun saves trajectories.
    # By default it's in the configured trajectory_path.
    #  try to resolve it relative to the runner's config.

    base_path = Path(runner.config.logging.trajectory_path)
    trajectory_file = base_path / session_id / "trajectory.json"

    if not trajectory_file.exists():
        return {"error": f"Trajectory not found for session {session_id}"}

    try:
        with open(trajectory_file, "r") as f:
            return {"trajectory": json.load(f)}
    except Exception as e:
        return {"error": f"Failed to read trajectory: {str(e)}"}


@mcp.tool()
def get_screenshots(
    session_id: str,
    start_step: int = 0,
    end_step: int = -1,
    max_screenshots: int = 5,
    scale: float = 0.25,
) -> List[Dict[str, Any]]:
    """
    Retrieve screenshots for a session.

    Args:
        session_id: The session ID.
        start_step: Optional start step index.
        end_step: Optional end step index (-1 for all).
        max_screenshots: Maximum number of screenshots to return (default: 5).
        scale: Scaling factor for images (default: 0.25). Set to 1.0 for full size.
    """
    base_path = Path(runner.config.logging.trajectory_path)
    screenshots_dir = base_path / session_id / "screenshots"

    if not screenshots_dir.exists():
        return []

    images = []
    # List all png files
    files = sorted(list(screenshots_dir.glob("*.png")))

    count = 0
    for file_path in files:
        if count >= max_screenshots:
            break

        # Extract step number from filename if possible, or just use index
        # Filename format usually: step_{n}.png or similar
        try:
            # Simple heuristic: try to parse step number
            stem = file_path.stem
            if "step_" in stem:
                step_num = int(stem.split("step_")[1])
            else:
                # Try parsing as integer (for example 0000.png)
                try:
                    step_num = int(stem)
                except ValueError:
                    step_num = 0  # Fallback

            if step_num < start_step:
                continue
            if end_step != -1 and step_num > end_step:
                continue

            with open(file_path, "rb") as img_file:
                raw_data = img_file.read()
                resized_data = resize_image_bytes(raw_data, scale)
                b64_data = base64.b64encode(resized_data).decode("utf-8")

            images.append(
                {"step": step_num, "filename": file_path.name, "data": b64_data}
            )
            count += 1
        except Exception:
            continue

    return images


@mcp.tool()
def get_single_screenshot(session_id: str, step: int, scale: float = 0.25) -> str:
    """
    Retrieve a single screenshot as base64 string.

    Args:
        session_id: The session ID.
        step: The step number.
        scale: Scaling factor for images (default: 0.25). Set to 1.0 for full size.
    """
    base_path = Path(runner.config.logging.trajectory_path)
    screenshots_dir = base_path / session_id / "screenshots"

    # Try to find the file
    # It might be named differently depending on DroidRun version
    # first check *step_{step}.png
    matches = list(screenshots_dir.glob(f"*step_{step}.png"))

    if not matches:
        # check zero-padded {step:04d}.png (e.g. 0000.png)
        matches = list(screenshots_dir.glob(f"{step:04d}.png"))

    if not matches:
        # check {step}.png onl
        matches = list(screenshots_dir.glob(f"{step}.png"))

    if not matches:
        return "Error: Screenshot not found"

    file_path = matches[0]

    try:
        with open(file_path, "rb") as img_file:
            raw_data = img_file.read()
            resized_data = resize_image_bytes(raw_data, scale)
            return base64.b64encode(resized_data).decode("utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"


def main():
    mcp.run()

if __name__ == "__main__":
    main()
