# kdenlive-api

Python client library for the Kdenlive JSON-RPC WebSocket API.

## Installation

```bash
pip install kdenlive-api
```

Or with uv:

```bash
uv add kdenlive-api
```

## Requirements

- Python 3.11+
- Kdenlive with RPC server enabled (requires kdenlive-websocket fork)

## Quick Start

```python
import asyncio
from kdenlive_api import KdenliveClient

async def main():
    async with KdenliveClient() as client:
        # Get project info
        info = await client.project.get_info()
        print(f"Project: {info.name}")
        print(f"Resolution: {info.width}x{info.height}")
        print(f"FPS: {info.fps}")

        # List clips in bin
        clips = await client.bin.list_clips()
        for clip in clips:
            print(f"  - {clip.name}")

        # Get timeline info
        timeline = await client.timeline.get_info()
        print(f"Timeline duration: {timeline.duration} frames")

asyncio.run(main())
```

## Examples

The [`examples/`](./examples/) directory contains 15 ready-to-use scripts solving common video editing problems:

| Script | Problem Solved |
|--------|----------------|
| [01_batch_import_organize.py](./examples/01_batch_import_organize.py) | Import and auto-organize files by type |
| [02_quick_rough_cut.py](./examples/02_quick_rough_cut.py) | Add clips to timeline in order |
| [03_auto_transitions.py](./examples/03_auto_transitions.py) | Add transitions between all clips |
| [04_batch_color_grade.py](./examples/04_batch_color_grade.py) | Apply consistent color correction |
| [05_add_fade_effects.py](./examples/05_add_fade_effects.py) | Add fade-in/fade-out effects |
| [06_trim_silence.py](./examples/06_trim_silence.py) | Trim dead air from clips |
| [07_track_setup.py](./examples/07_track_setup.py) | Create organized track structure |
| [08_multi_format_export.py](./examples/08_multi_format_export.py) | Export for multiple platforms |
| [09_scene_splitter.py](./examples/09_scene_splitter.py) | Split clips at intervals |
| [10_cleanup_timeline.py](./examples/10_cleanup_timeline.py) | Remove tiny leftover clips |
| [11_backup_project.py](./examples/11_backup_project.py) | Auto-save with timestamps |
| [12_apply_preset_effects.py](./examples/12_apply_preset_effects.py) | Apply saved effect presets |
| [13_audio_ducking_setup.py](./examples/13_audio_ducking_setup.py) | Lower music during speech |
| [14_marker_based_export.py](./examples/14_marker_based_export.py) | Export by guide markers |
| [15_project_template.py](./examples/15_project_template.py) | Create projects from templates |

All scripts accept command-line arguments. Run with `--help` for usage:

```bash
python examples/01_batch_import_organize.py --help
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KDENLIVE_WS_URL` | WebSocket URL | `ws://localhost:9876` |
| `KDENLIVE_AUTH_TOKEN` | Bearer token for authentication | None |

### Programmatic Configuration

```python
from kdenlive_api import KdenliveClient

# Custom URL
client = KdenliveClient(url="ws://192.168.1.100:9876")

# With authentication
client = KdenliveClient(auth_token="your-secret-token")

# Both
client = KdenliveClient(
    url="ws://192.168.1.100:9876",
    auth_token="your-secret-token"
)
```

## API Namespaces

The client provides access to Kdenlive functionality through typed API namespaces:

### Project (`client.project`)

```python
# Get project information
info = await client.project.get_info()

# Open a project
await client.project.open("/path/to/project.kdenlive")

# Save project
await client.project.save()
await client.project.save("/path/to/new-project.kdenlive")

# Create new project
await client.project.new(profile="atsc_1080p_25")

# Close project
await client.project.close(save_changes=True)

# Undo/Redo
await client.project.undo()
await client.project.redo()
```

### Timeline (`client.timeline`)

```python
# Get timeline info
info = await client.timeline.get_info()

# Get all tracks
tracks = await client.timeline.get_tracks()

# Get clips (all or by track)
clips = await client.timeline.get_clips()
clips = await client.timeline.get_clips(track_id=0)

# Insert clip from bin
clip_id = await client.timeline.insert_clip(
    bin_clip_id="abc123",
    track_id=0,
    position=100  # frames
)

# Move clip
await client.timeline.move_clip(clip_id=1, track_id=1, position=200)

# Delete clip
await client.timeline.delete_clip(clip_id=1)

# Split clip
parts = await client.timeline.split_clip(clip_id=1, position=50)

# Resize/trim clip
await client.timeline.resize_clip(clip_id=1, in_point=10, out_point=100)

# Track management
track_id = await client.timeline.add_track("video", name="V3")
await client.timeline.delete_track(track_id=2)

# Playhead
await client.timeline.seek(position=500)
position = await client.timeline.get_position()
```

### Bin (`client.bin`)

```python
# List clips and folders
clips = await client.bin.list_clips()
clips = await client.bin.list_clips(folder_id="folder123")
folders = await client.bin.list_folders()

# Get clip details
info = await client.bin.get_clip_info(clip_id="abc123")

# Import media
clip_id = await client.bin.import_clip("/path/to/video.mp4")
clip_ids = await client.bin.import_clips([
    "/path/to/video1.mp4",
    "/path/to/video2.mp4"
], folder_id="folder123")

# Organize
folder_id = await client.bin.create_folder("Footage", parent_id=None)
await client.bin.rename_item(item_id="abc123", name="New Name")
await client.bin.move_item(item_id="abc123", target_folder_id="folder123")
await client.bin.delete_clip(clip_id="abc123")

# Markers
marker_id = await client.bin.add_clip_marker(
    clip_id="abc123",
    position=100,
    comment="Important moment"
)
await client.bin.delete_clip_marker(clip_id="abc123", marker_id=0)
```

### Effects (`client.effects`)

```python
# List available effects
effects = await client.effects.list_available()

# Get effect details
info = await client.effects.get_info(effect_id="blur")

# Apply effect to clip
instance_id = await client.effects.add(effect_id="blur", clip_id=1)

# Get effects on a clip
clip_effects = await client.effects.get_clip_effects(clip_id=1)

# Modify effect parameters
await client.effects.set_property(
    clip_id=1,
    effect_id="effect123",
    property_name="radius",
    value=10.5
)

# Enable/disable effects
await client.effects.enable(clip_id=1, effect_id="effect123")
await client.effects.disable(clip_id=1, effect_id="effect123")

# Remove effect
await client.effects.remove(clip_id=1, effect_id="effect123")

# Keyframes
keyframes = await client.effects.get_keyframes(
    clip_id=1,
    effect_id="effect123",
    property_name="radius"
)

await client.effects.set_keyframe(
    clip_id=1,
    effect_id="effect123",
    property_name="radius",
    position=50,
    value=20.0
)

await client.effects.delete_keyframe(
    clip_id=1,
    effect_id="effect123",
    property_name="radius",
    position=50
)
```

### Render (`client.render`)

```python
# Get available presets
presets = await client.render.get_presets()

# Start render
job = await client.render.start(
    preset_name="MP4-H264",
    output_path="/path/to/output.mp4"
)

# Monitor progress
status = await client.render.get_status(job_id=job.job_id)
print(f"Progress: {status.progress}%")

# Get all jobs
jobs = await client.render.get_jobs()
active = await client.render.get_active_job()

# Stop render
await client.render.stop(job_id=job.job_id)
```

### Assets (`client.asset`)

```python
# Browse categories
categories = await client.asset.list_categories()

# Search
results = await client.asset.search("blur")

# Get effects by category
effects = await client.asset.get_effects_by_category("Color")

# Favorites
favorites = await client.asset.get_favorites()
await client.asset.add_favorite(asset_id="blur")
await client.asset.remove_favorite(asset_id="blur")

# Presets
presets = await client.asset.get_presets(effect_id="blur")
await client.asset.save_preset(effect_id="blur", preset_name="My Blur")
```

### Transitions (`client.transition`)

```python
# List available transitions
transitions = await client.transition.list()

# Add transition between clips
info = await client.transition.add(
    transition_type="dissolve",
    from_clip_id=1,
    to_clip_id=2
)

# Remove transition
await client.transition.remove(transition_id=info.id)
```

### Compositions (`client.composition`)

```python
# List compositions
compositions = await client.composition.list()

# Add composition
info = await client.composition.add(
    composition_type="composite",
    track=0,
    position=100
)

# Remove composition
await client.composition.remove(composition_id=info.id)
```

## Notifications

Subscribe to real-time notifications from Kdenlive:

```python
async def handle_notification(method: str, params: dict):
    if method == "render.progress":
        print(f"Render progress: {params['progress']}%")
    elif method == "timeline.changed":
        print("Timeline was modified")

client = KdenliveClient()
client.on_notification(handle_notification)
await client.connect()
```

## Error Handling

```python
from kdenlive_api import (
    KdenliveError,
    ConnectionError,
    ProjectNotOpenError,
    ClipNotFoundError,
    ValidationError,
)

try:
    await client.project.get_info()
except ConnectionError:
    print("Cannot connect to Kdenlive")
except ProjectNotOpenError:
    print("No project is open")
except ClipNotFoundError as e:
    print(f"Clip not found: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except KdenliveError as e:
    print(f"Kdenlive error: {e}")
```

## Type Safety

All API responses are typed using Pydantic models:

```python
from kdenlive_api import ProjectInfo, ClipInfo, TimelineClip

info: ProjectInfo = await client.project.get_info()
print(info.width)  # IDE autocomplete works!
```

## License

MIT License - see LICENSE file for details.
