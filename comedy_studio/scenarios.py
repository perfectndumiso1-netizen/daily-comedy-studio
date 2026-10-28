"""Small, original, offline scenario library and recent-concept rotation."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "meeting-mute", "category": "work-life", "title": "The Unmute Olympics",
        "hook": "Remote meeting. Camera on. Mic off.", "actor": "person", "room": "office", "prop": "laptop",
        "scenes": [
            {"caption": "I had the perfect answer ready.", "description": "A confident worker waits on a video call."},
            {"caption": "I give a powerful speech to the little mute icon.", "description": "The worker enthusiastically talks at a laptop with its microphone muted."},
            {"caption": "Everyone nods. I assume they agree.", "description": "The grid of coworkers appears to nod silently."},
            {"caption": "Then someone types: 'Your cat is presenting.'", "description": "A cat has walked across the keyboard and taken over the meeting."},
        ],
    },
    {
        "id": "fridge-mystery", "category": "everyday-life", "title": "The Fridge Detective",
        "hook": "I opened the fridge for one thing.", "actor": "person", "room": "kitchen", "prop": "fridge",
        "scenes": [
            {"caption": "I came in for the milk. Case closed.", "description": "A sleepy midnight snack seeker opens the refrigerator."},
            {"caption": "One leftover container looks suspicious.", "description": "A mysterious food container catches the person's eye."},
            {"caption": "I inspect it like a crime scene.", "description": "The person investigates leftovers with exaggerated seriousness."},
            {"caption": "The milk is in my hand. Detective work: flawless.", "description": "They realize they were holding the milk the whole time."},
        ],
    },
    {
        "id": "laundry-chair", "category": "relatable-life", "title": "The Chair of Decisions",
        "hook": "Laundry has three stages.", "actor": "person", "room": "bedroom", "prop": "laundry",
        "scenes": [
            {"caption": "Clean clothes go in the closet.", "description": "A person folds a neat stack of laundry."},
            {"caption": "Worn clothes go in the hamper.", "description": "The person sorts clothes with determined focus."},
            {"caption": "The almost-clean ones go on The Chair.", "description": "A chair slowly disappears beneath a mountain of clothes."},
            {"caption": "The chair is now a wardrobe with legs.", "description": "The clothes mountain looks suspiciously like furniture."},
        ],
    },
    {
        "id": "dog-walk", "category": "funny-animals", "title": "A Very Important Walk",
        "hook": "The dog asked for a walk.", "actor": "dog", "room": "park", "prop": "leash",
        "scenes": [
            {"caption": "I grab the leash. The dog is thrilled.", "description": "An excited dog sees its leash and springs into action."},
            {"caption": "We reach the end of the driveway.", "description": "The dog and owner set off on their great adventure."},
            {"caption": "The dog finds one excellent leaf.", "description": "The dog spots a leaf and sits down to investigate."},
            {"caption": "Walk complete. The leaf has been inspected.", "description": "The dog proudly turns around after its one-leaf expedition."},
        ],
    },
    {
        "id": "family-photo", "category": "family-life", "title": "The Family Photo",
        "hook": "Just one nice family photo.", "actor": "person", "room": "living-room", "prop": "camera",
        "scenes": [
            {"caption": "Everyone says, 'We'll be ready in a second.'", "description": "A family gathers for a supposedly quick photo."},
            {"caption": "One blink. One snack. One mysterious shoe.", "description": "The family photo attempt immediately becomes chaotic."},
            {"caption": "I set the timer and sprint into place.", "description": "The photographer races to join the group."},
            {"caption": "Perfect shot: only the dog is looking.", "description": "The dog is the only family member posing for the camera."},
        ],
    },
    {
        "id": "online-shopping", "category": "everyday-life", "title": "The Tiny Parcel",
        "hook": "My package said 'small box.'",
        "actor": "person", "room": "doorstep", "prop": "box",
        "scenes": [
            {"caption": "The delivery alert says: 'Arriving today.'", "description": "A person eagerly checks the delivery notification."},
            {"caption": "A box arrives with its own postcode.", "description": "An enormous parcel appears on a tiny doorstep."},
            {"caption": "I open it. More boxes. A lot more boxes.", "description": "The package contains a ridiculous sequence of smaller boxes."},
            {"caption": "At the bottom: one very confident teaspoon.", "description": "A tiny spoon sits at the bottom of the huge package."},
        ],
    },
    {
        "id": "plant-talk", "category": "unexpected", "title": "The Plant Parent",
        "hook": "I started talking to my plant.", "actor": "person", "room": "living-room", "prop": "plant",
        "scenes": [
            {"caption": "I tell the plant it is doing great.", "description": "A person gives a houseplant a motivational pep talk."},
            {"caption": "I bring it water and a tiny blanket.", "description": "The plant receives wildly attentive care."},
            {"caption": "My roommate asks how the plant is doing.", "description": "A roommate notices the plant's dramatic makeover."},
            {"caption": "I say, 'It has been quiet since the meeting.'", "description": "The person reports a plant's imaginary office gossip."},
        ],
    },
    {
        "id": "gym-mat", "category": "relatable-life", "title": "The Workout Mat",
        "hook": "Today I finally exercised.", "actor": "person", "room": "living-room", "prop": "mat",
        "scenes": [
            {"caption": "I roll out the mat. Big fitness energy.", "description": "A person prepares for a serious workout."},
            {"caption": "I do one impressive stretch.", "description": "The person completes a single ambitious stretch."},
            {"caption": "The floor is surprisingly comfortable.", "description": "The person pauses on the mat and looks cozy."},
            {"caption": "Workout complete. I have warmed the mat.", "description": "They proudly rate their floor-based fitness session."},
        ],
    },
    {
        "id": "cat-box", "category": "funny-animals", "title": "The Premium Cat Bed",
        "hook": "I bought my cat a luxury bed.", "actor": "cat", "room": "living-room", "prop": "box",
        "scenes": [
            {"caption": "Soft fabric. Perfect size. Very fancy.", "description": "A plush designer cat bed arrives."},
            {"caption": "The cat inspects the expensive bed.", "description": "A cat considers a luxurious new bed."},
            {"caption": "The cat chooses the shipping box.", "description": "The cat climbs into a plain cardboard box."},
            {"caption": "Five stars. The box is clearly premium.", "description": "The cat is delighted by the cardboard box."},
        ],
    },
    {
        "id": "text-autocorrect", "category": "relationships", "title": "Autocorrect Has Plans",
        "hook": "I texted: 'See you soon.'",
        "actor": "person", "room": "cafe", "prop": "phone",
        "scenes": [
            {"caption": "A sweet message to my partner.", "description": "A person types a loving message on their phone."},
            {"caption": "Autocorrect makes one tiny change.", "description": "The phone suggests an unexpected autocorrect."},
            {"caption": "I send: 'See you spoon.'", "description": "The person notices the curious message they sent."},
            {"caption": "They reply: 'Already setting the table.'", "description": "Their partner turns the typo into a dinner plan."},
        ],
    },
    {
        "id": "umbrella", "category": "absurd-situations", "title": "The Inside-Out Umbrella",
        "hook": "The forecast said a light breeze.",
        "actor": "person", "room": "street", "prop": "umbrella",
        "scenes": [
            {"caption": "I bring my tiny travel umbrella.", "description": "A confident person opens a compact umbrella."},
            {"caption": "The wind turns it into modern art.", "description": "A gust flips the umbrella inside out."},
            {"caption": "I pretend this was the design.", "description": "The person tries to look sophisticated under the broken umbrella."},
            {"caption": "A stranger asks where they can buy one.", "description": "A passerby admires the accidental umbrella sculpture."},
        ],
    },
    {
        "id": "sleep-alarm", "category": "relationships", "title": "The Sleepy Alarm",
        "hook": "I set five alarms for tomorrow.", "actor": "person", "room": "bedroom", "prop": "phone",
        "scenes": [
            {"caption": "The first alarm rings. I bravely snooze.", "description": "A sleepy person taps snooze on a phone."},
            {"caption": "The second alarm rings. Also snooze.", "description": "The snooze button receives another decisive tap."},
            {"caption": "The third alarm rings. I negotiate.", "description": "The person bargains with their alarm clock."},
            {"caption": "The phone gives up and sets an alarm for lunch.", "description": "A sleepy person and their phone have reached a compromise."},
        ],
    },
]


def choose_scenario(history_path: str | Path, category: str | None = None,
                    seed: int | None = None, recent_limit: int = 6) -> tuple[dict[str, Any], dict[str, Any]]:
    """Choose randomly while avoiding recent IDs; return concept and updated history."""
    path = Path(history_path)
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(history, dict) or not isinstance(history.get("recent", []), list):
            history = {"recent": []}
    except (OSError, json.JSONDecodeError):
        history = {"recent": []}
    recent = [str(x) for x in history.get("recent", [])]
    pool = [item for item in SCENARIOS if category in (None, "random", item["category"])]
    if not pool:
        raise ValueError(f"Unknown category: {category}. Use one of: {', '.join(available_categories())}, random")
    unused = [item for item in pool if item["id"] not in recent]
    # If a narrow category is exhausted, allow its concepts again instead of failing.
    selected = random.Random(seed).choice(unused or pool)
    updated = {"recent": ([selected["id"]] + [item for item in recent if item != selected["id"]])[:recent_limit]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    return selected, updated


def available_categories() -> list[str]:
    return sorted({item["category"] for item in SCENARIOS})
