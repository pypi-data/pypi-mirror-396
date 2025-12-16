import logging
from pathlib import Path

from moviepy import VideoFileClip

logger = logging.getLogger(__name__)


def webm_to_mp4_moviepy(input_path: str | Path, output_path: str | Path | None = None):
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".mp4")
    else:
        output_path = Path(output_path)

    with VideoFileClip(str(input_path)) as clip:
        clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
        )

    return output_path


def create_evidence_clip(
    video_path: str | Path,
    timestamps: list[float],
    output_path: str | Path,
) -> Path:
    """
    Create single evidence clip from video based on action timestamps.

    Args:
        video_path: Path to the full video file
        timestamps: Action's start time (seconds from run start). i.e. len(timestamps) = len(steps)
        output_path: Path to save evidence clip

    Returns:
        Path to evidence clip
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    clip = VideoFileClip(str(video_path))

    # Pass / Fail evidence: last 2 actions
    start_time = clip.duration - timestamps[-2] if len(timestamps) >= 2 else 0
    evidence_clip = clip.subclipped(max(0, start_time), clip.duration)

    evidence_clip.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
    )
    evidence_clip.close()
    clip.close()
    return output_path
