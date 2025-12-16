"""
Higgsfield motion presets registry.

Contains all 120 motion presets available in the Higgsfield API.
Motion IDs are UUIDs that control camera and subject movement.
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# Motion Presets
# ---------------------------------------------------------------------------

HIGGSFIELD_MOTIONS = {
    # Camera movements
    "360_orbit": "ea035f68-b350-40f1-b7f4-7dff999fdd67",
    "3d_rotation": "2bae49e6-ffe7-42a8-a73f-d44632c4acaa",
    "arc_left": "c5881721-05b1-47d9-94d6-0203863114e1",
    "arc_right": "a85cb3f2-f2be-4ee2-b3b9-808fc6a81acc",
    "bullet_time": "22d7c60a-b76f-4082-9928-d2a42357759a",
    "crane_down": "b26dcbe5-e784-4893-b8a3-2bd4f848e90a",
    "crane_over_the_head": "0d736605-3a09-4a39-bcfe-b556fba7dd22",
    "crane_up": "68af9add-43ea-4261-a706-16b640fdcff9",
    "crash_zoom_in": "3ec247ed-063d-476d-8266-48829c2eced6",
    "crash_zoom_out": "3f7a86be-c78f-4c5d-8dbf-7395a3fbeea1",
    "dolly_in": "81ca2cd2-05db-4222-9ba0-a32e5185adfb",
    "dolly_left": "71f0f8bc-0e5d-4d32-b34f-bd74a5e3cba8",
    "dolly_out": "12ac8798-5370-4801-91a6-f1acb425fc4a",
    "dolly_right": "15ddc007-4723-42c1-8446-2af69af4879f",
    "dolly_zoom_in": "f0ca4e62-f65d-4a6d-83c1-ecbaa4d492ba",
    "dolly_zoom_out": "2df82f5f-064a-4a7e-8b59-24ac446cb1df",
    "double_dolly": "bd133fba-ed35-433b-9cb2-87b1f5bb1139",
    "dutch_angle": "915d6b95-6b9c-4a09-a0df-7ecd69c9bf64",
    "earth_zoom_out": "46fa79e3-efce-41e8-95bc-1dc5a1a30795",
    "eyes_in": "0c5d9955-706e-4b21-b499-39f1b5e5ea0e",
    "fisheye": "ec365c4d-c130-48b3-923d-4b4359d96095",
    "fpv_drone": "7673d9e0-208c-4cf8-8b72-fce5b0e92ecb",
    "handheld": "5be9d262-82d7-4a74-babf-ee8fefd5c3c3",
    "head_tracking": "d38d2084-dde6-4c16-90d2-19603bceb901",
    "hyperlapse": "aebcaa0d-525d-4a74-b497-26da8f81957b",
    "jib_down": "2ce412eb-2e66-4d73-9c9c-d1fba4c8a494",
    "jib_up": "cc5d4b42-f05d-41ef-9f51-c4b28f3fd2d2",
    "lazy_susan": "ce9dc38e-d6da-4368-9742-f73b559d802e",
    "object_pov": "b29cff3b-2494-4f3f-a74c-70ceee7b1ccf",
    "overhead": "40245735-2670-4572-b46e-854151281f55",
    "snorricam": "984834d9-72a7-4074-97c2-f98d265a49de",
    "static": "fa3ddb7c-53ee-4383-aa17-97ae65f180e5",
    "super_dolly_in": "3a24a20d-b494-4e8a-9b5f-4ef05ee5073d",
    "super_dolly_out": "679c128d-a109-4267-8007-12f653f6346d",
    "through_object_in": "ebf152b3-f794-4d5c-886f-ff61ec6498bc",
    "through_object_out": "ea0d11ac-b4e2-4ea7-89c2-a4a44a62dc79",
    "tilt_down": "ff67b0eb-a621-45a0-b92d-ce2549250149",
    "tilt_up": "2c9af101-fe7a-4299-91f3-e44431a0576f",
    "whip_pan": "25c72c28-7857-4aa0-af92-ba5380f0e67d",
    "wiggle": "8a660d27-dfe9-4bb1-8ad0-c6603e79fc95",
    "yoyo_zoom": "bd639dee-00a3-407b-b539-f4516ce9d214",
    "zoom_in": "fbcbec5b-30f8-4b17-ba6e-8e8d5b265562",
    "zoom_out": "263600e4-45c0-4c13-9579-40a9278af37c",

    # General / Default
    "general": "31177282-bde3-4870-b283-1135ca0a201a",

    # Actions and effects
    "action_run": "dc8d7d9c-ae0c-45fc-b780-7d470b171b45",
    "agent_reveal": "65b0a5a3-953d-471c-86d5-967ab44d0dab",
    "angel_wings": "d21ff628-0d91-40b2-8508-cd5a0ce375d4",
    "baseball_kick": "ab0fa3d8-fcbe-4a6a-96bb-eae7a0e2c2cb",
    "basketball_dunks": "1b4c1b9a-898b-451c-bff8-7288382ccaf2",
    "black_tears": "161d2898-f7ed-43f5-8daa-1175bcc69ba9",
    "bloom_mouth": "4a79cff8-ef78-42ca-aed9-3fb9acaed4ad",
    "boxing": "4ac80533-015b-49c1-a2eb-891603823883",
    "buckle_up": "a652ae99-c21b-4bdf-965c-e4a6d07fb262",
    "building_explosion": "cb8cfb5a-245d-4d96-92d7-7e0791967d75",
    "car_chasing": "b98810ad-e51d-4680-a800-cd6fc8037bc4",
    "car_explosion": "0235b1a9-428a-4df5-aa5a-93b6dba41834",
    "car_grip": "b3fd6f79-dd5e-48f7-b5b4-5c2f1655822c",
    "catwalk": "0e339850-d8f1-4c9d-be3a-97fc2cdb628e",
    "clone_explosion": "fd6272d6-7b7c-4c4e-9afd-c5c98aaa1b5c",
    "datamosh": "e3112849-0c04-4af2-be93-ccbb0f8f4cd5",
    "diamond": "81d6b1c4-dd8a-4130-9c01-fe85bf80babc",
    "dirty_lens": "29168a2c-04db-4ad1-8e19-f2a24371d413",
    "disintegration": "97ffe32a-ab9a-4067-9cf9-9adc30c2656f",
    "downhill_pov": "381fcf9a-ca91-4eac-a3c4-43d4302d6404",
    "duplicate": "1d21b411-b706-4233-ad83-7599290ac51f",
    "face_punch": "d6772bfc-272d-4396-a972-deecb09b17cb",
    "fire_breathe": "eeb51fed-dfdc-4b99-804a-6ae8f550e95d",
    "floating_fish": "ca339f47-c2a5-4f3f-a1fb-4f12344cd5da",
    "flood": "6597fc71-86dc-4f65-90c2-11330022cd1c",
    "floral_eyes": "f0426395-607f-4753-83e3-85ee2151a840",
    "flying": "1d5ee550-a8b2-4200-8909-4ca7795911dc",
    "focus_change": "797e27b5-2e6e-4b9a-a3c1-d437e9d386fc",
    "freezing": "9390496c-0547-4a70-98a7-31ad27d334cd",
    "garden_bloom": "60049b87-68f5-4c34-b833-e2ef3b9d807d",
    "glam": "a2046ff7-26fc-4d97-aab7-54bbb55fca97",
    "glowing_fish": "cb3d5fee-d874-41cf-b0aa-c1092af79da0",
    "glowshift": "f2db4c02-4d29-4401-a26e-0cf8ae14b9b3",
    "head_explosion": "92141609-85f7-4c8a-866e-9a542c164fe9",
    "head_off": "d57404a2-5d6f-4bce-b9d5-1242666cae02",
    "incline": "cff69c3b-0178-4f72-bae5-e301ccb97f28",
    "innerlight": "7c01086d-92a1-43f8-a69b-63ce07d4f19d",
    "invisible": "6fdc8fa8-6373-4a5e-aeac-4aa84c8cfd4b",
    "jelly_drift": "c5b339cd-9f1c-44fe-91a1-464cf83f3749",
    "kiss": "83a8902b-4531-4893-9ee8-044b2d92b758",
    "lens_crack": "080dd954-0d90-4346-8fef-83aebfe63ce5",
    "lens_flare": "e98b3fee-79e8-4d87-881c-8ddd03ca738e",
    "levitation": "0a5a48d7-6716-41a4-9a9f-7ad9229c879b",
    "low_shutter": "790ca797-703e-44c1-8d77-53080ea3c6a3",
    "medusa_gorgona": "473fd7e0-18f5-467f-a146-3b6cbfddf46a",
    "melting": "eb3b0cd9-f924-410c-94c7-9e1850ed04c7",
    "moonwalk_left": "70f3014c-ee77-4c33-83b9-7f7e68726aa9",
    "moonwalk_right": "cf8c7490-7bc0-433d-860c-d1be982a520a",
    "morphskin": "8968b3f5-8d71-432a-a579-2d1aeae21439",
    "mouth_in": "21bbd0c4-ca4f-4ea3-82a8-607437d63e8e",
    "paint_splash": "aa8d80db-ca0e-4535-952f-6fa040f2306b",
    "paparazzi": "556ab276-23b1-4604-a501-2513a71e2eea",
    "powder_explosion": "7aa6fbad-55eb-4930-bf75-cc9a2f0b3b5b",
    "push_to_glass": "30a02896-cdda-469d-9ed9-52cbba1c04a8",
    "rap_flex": "c3dbf04b-2ba5-4986-ab4f-872a9d71826f",
    "robo_arm": "153afe86-20f1-45d3-99ea-106c37f94506",
    "roll_transition": "c718443d-fc3c-4a79-bccf-6c98b56737ec",
    "sand_storm": "ba778a3b-e6ff-4563-9253-a8ae4e04b1a7",
    "set_on_fire": "3f003f41-dbdc-41d9-94a8-de3942ebeb67",
    "skateboard_glide": "26864aa2-010c-458c-bdf5-963babc756d2",
    "skateboard_ollie": "023bf31f-23d2-4432-90be-cab4ae332e59",
    "skate_cruise": "2bf184fb-47a3-41ba-93ac-846b9307b1bd",
    "ski_carving": "9015dd00-4325-4679-b3da-bb25cd948899",
    "skin_surge": "8c8f12b1-732f-4faf-8b2b-6029b964afd3",
    "ski_powder": "e65a92e6-7a9e-43ce-8d35-6f6a16bfe716",
    "snowboard_carving": "f933ee1b-329e-41e9-8aad-5a1f60ecd6f5",
    "snowboard_powder": "f6fdf448-6309-497b-85ee-79517a9ff097",
    "soul_jump": "87d67a56-8d80-42db-8e1c-ebc3d2483cbd",
    "super_8mm": "b604bd5f-22eb-4920-ad7e-47306805d7c6",
    "tentacles": "20a5fdc3-c92b-4134-900c-4f47bbb0edb7",
    "thunder_god": "27169770-288b-4ee7-b3ab-bb2bcf0e136b",
    "timelapse_human": "9463e9ef-3242-46bf-b1ec-41eec6b2d6bf",
    "timelapse_landscape": "130b5a9d-522f-467b-bb22-a9109c1710c1",
    "turning_metal": "3e735d99-34f6-469c-83fb-ba608f299424",
    "vhs": "2b7c1db3-862a-4373-8435-ae4464ae5892",
    "wind_to_face": "e8027924-b97d-43c3-9676-3c0f16da6c5f",
}


# ---------------------------------------------------------------------------
# Motion Categories
# ---------------------------------------------------------------------------

CAMERA_MOTIONS = [
    "360_orbit", "3d_rotation", "arc_left", "arc_right", "bullet_time",
    "crane_down", "crane_over_the_head", "crane_up", "crash_zoom_in",
    "crash_zoom_out", "dolly_in", "dolly_left", "dolly_out", "dolly_right",
    "dolly_zoom_in", "dolly_zoom_out", "double_dolly", "dutch_angle",
    "earth_zoom_out", "eyes_in", "fisheye", "fpv_drone", "handheld",
    "head_tracking", "hyperlapse", "jib_down", "jib_up", "lazy_susan",
    "object_pov", "overhead", "snorricam", "static", "super_dolly_in",
    "super_dolly_out", "through_object_in", "through_object_out",
    "tilt_down", "tilt_up", "whip_pan", "wiggle", "yoyo_zoom",
    "zoom_in", "zoom_out",
]

EFFECT_MOTIONS = [
    "agent_reveal", "angel_wings", "black_tears", "bloom_mouth",
    "clone_explosion", "datamosh", "diamond", "dirty_lens",
    "disintegration", "fire_breathe", "floating_fish", "flood",
    "floral_eyes", "flying", "focus_change", "freezing", "garden_bloom",
    "glam", "glowing_fish", "glowshift", "head_explosion", "head_off",
    "incline", "innerlight", "invisible", "jelly_drift", "lens_crack",
    "lens_flare", "levitation", "low_shutter", "medusa_gorgona", "melting",
    "morphskin", "paint_splash", "paparazzi", "powder_explosion",
    "push_to_glass", "roll_transition", "sand_storm", "set_on_fire",
    "skin_surge", "soul_jump", "super_8mm", "tentacles", "thunder_god",
    "timelapse_human", "timelapse_landscape", "turning_metal", "vhs",
    "wind_to_face",
]

ACTION_MOTIONS = [
    "action_run", "baseball_kick", "basketball_dunks", "boxing",
    "buckle_up", "building_explosion", "car_chasing", "car_explosion",
    "car_grip", "catwalk", "downhill_pov", "duplicate", "face_punch",
    "kiss", "moonwalk_left", "moonwalk_right", "mouth_in", "rap_flex",
    "robo_arm", "skateboard_glide", "skateboard_ollie", "skate_cruise",
    "ski_carving", "ski_powder", "snowboard_carving", "snowboard_powder",
]


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def list_motions() -> list[str]:
    """Return list of all available motion preset names."""
    return sorted(HIGGSFIELD_MOTIONS.keys())


def get_motion_id(name: str) -> Optional[str]:
    """
    Get motion UUID by name.

    Args:
        name: Motion preset name (e.g., "zoom_in", "dolly_out")

    Returns:
        UUID string or None if not found.
    """
    return HIGGSFIELD_MOTIONS.get(name)


def is_valid_motion(name: str) -> bool:
    """Check if a motion name is valid."""
    return name in HIGGSFIELD_MOTIONS


def get_motions_by_category(category: str) -> list[str]:
    """
    Get motion names by category.

    Args:
        category: One of "camera", "effect", "action"

    Returns:
        List of motion names in that category.
    """
    categories = {
        "camera": CAMERA_MOTIONS,
        "effect": EFFECT_MOTIONS,
        "action": ACTION_MOTIONS,
    }
    return categories.get(category, [])
