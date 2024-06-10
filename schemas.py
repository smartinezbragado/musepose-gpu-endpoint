from pydantic import BaseModel, field_validator


class AnimationPayload(BaseModel):
    id: str
    audio_file: str
    output_path: str
    reference_image: str
    reference_video: str | None = None
    motion_sequence: str | None = None

    seed: int = 1
    image_clip_duration: float = 5
    lower_vram: bool = False

    watermark: bool = True
    watermark_path: str
    watermark_width: float = 100
    watermark_offset: float = 20

    remove_background: bool = False

    @field_validator('watermark_width', 'watermark_offset')
    def validate_positive_values(cls, v, info):
        if v <= 0:
            raise ValueError(f'{info.field_name} must be greater than 0')
        return v

    @field_validator('watermark', 'remove_background')
    def validate_boolean_values(cls, v, info):
        if not isinstance(v, bool):
            raise ValueError(f'{info.field_name} must be a boolean')
        return v