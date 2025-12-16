import logging
import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass

from droidrun import DroidAgent, ResultEvent
from droidrun.config_manager import DroidrunConfig
from async_adbutils import adb
from droidrun.cli.main import _setup_portal, get_portal_version, ensure_package_config



@dataclass
class RunResult:
    session_id: str
    last_output: str
    success: bool


class DroidRunner:
    def __init__(self, config_path: str = "config.yaml"):
        ensure_package_config(verbose=False)
        self.config = DroidrunConfig.from_yaml(config_path)
        # Ensure logging is configured but don't force console output if not needed
        # We might want to suppress standard logging if we are just streaming events
        self.logger = logging.getLogger("droidrun")

        # Configure trajectory path
        # Priority: Env Var > Default (droidrun-mcp/trajectories)
        env_path = os.environ.get("DROIDRUN_TRAJECTORY_PATH")
        if env_path:
            self.config.logging.trajectory_path = str(Path(env_path).resolve())
        else:
            # Default to ~/.droidrun-mcp/trajectories
            default_path = Path.home() / ".droidrun-mcp" / "trajectories"
            self.config.logging.trajectory_path = str(default_path.resolve())

        # Force enable trajectory saving for MCP
        # it is needed to support get_trajectory and get_screenshots tools
        self.config.logging.save_trajectory = "all"

    async def run(
        self,
        instruction: str,
        apk_path: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        device_serial: Optional[str] = None,
    ) -> RunResult:
        """
        Execute a task on the device.

        Args:
            instruction: The natural language command.
            apk_path: Optional path to an APK to install before running.
            progress_callback: A callback function that receives event dictionaries.
            device_serial: Optional serial number of the device to use.
        """

        serial = device_serial or self.config.device.serial
        if serial:
            self.config.device.serial = serial

        try:
            device_obj = await adb.device(self.config.device.serial)
            if not device_obj:
                # If no specific serial, try to find first connected
                devices = await adb.list()
                if devices:
                    device_obj = devices[0]
                    self.config.device.serial = device_obj.serial
                else:
                    return RunResult(
                        session_id="",
                        last_output="No device connected",
                        success=False,
                    )

            portal_version = await get_portal_version(device_obj)
            if not portal_version:
                await _setup_portal(
                    path=None, device=self.config.device.serial, debug=False
                )

            if apk_path:
                if progress_callback:
                    progress_callback(
                        {"type": "setup", "message": f"Installing APK: {apk_path}"}
                    )
                await device_obj.install(
                    apk_path, uninstall=True, flags=["-g"], silent=True
                )

        except Exception as e:
            return RunResult(
                session_id="",
                last_output=f"Device setup failed: {str(e)}",
                success=False,
            )

        agent = DroidAgent(goal=instruction, config=self.config, timeout=1000)

        if progress_callback:
            progress_callback(
                {"type": "status", "message": "Starting agent execution..."}
            )

        try:
            handler = agent.run()

            async for event in handler.stream_events():
                # Map internal events to simplified MCP events
                # can be refined based on what's useful for the client
                event_data = {
                    "type": "event",
                    "event_type": event.__class__.__name__,
                    "details": str(event),
                }

                # Extract more specific info if possible
                if hasattr(event, "step_number"):
                    event_data["step"] = event.step_number

                if progress_callback:
                    progress_callback(event_data)

            result: ResultEvent = await handler

            # Ensure all artifacts are written to disk
            if hasattr(agent, "trajectory_writer") and agent.trajectory_writer:
                await agent.trajectory_writer.stop()

            # Session ID is the trajectory folder name.
            # DroidAgent -> trajectory -> base_path / goal_timestamp_uuid
            if (
                hasattr(agent, "trajectory")
                and agent.trajectory
                and agent.trajectory.trajectory_folder
            ):
                trajectory_path = agent.trajectory.trajectory_folder
                session_id = trajectory_path.name
            else:
                session_id = "unknown"

            return RunResult(
                session_id=session_id,
                last_output=result.reason or "No output",
                success=result.success,
            )

        except Exception as e:
            return RunResult(
                session_id="",
                last_output=f"Execution failed: {str(e)}",
                success=False,
            )
