# filename: beatstoch/generator.py
import random
import math
from typing import List, Tuple, Optional

import numpy as np
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

# General MIDI drum note numbers (GM Standard)
DRUMS = {
    # Kicks
    "kick": 36,  # Bass Drum 1
    "kick_acoustic": 35,  # Acoustic Bass Drum
    # Snares
    "snare": 38,  # Acoustic Snare
    "snare_electric": 40,  # Electric Snare
    "side_stick": 37,  # Side Stick / Rimshot
    "clap": 39,  # Hand Clap
    # Hi-hats
    "closed_hat": 42,  # Closed Hi-Hat
    "pedal_hat": 44,  # Pedal Hi-Hat
    "open_hat": 46,  # Open Hi-Hat
    # Cymbals
    "crash": 49,  # Crash Cymbal 1
    "crash2": 57,  # Crash Cymbal 2
    "ride": 51,  # Ride Cymbal 1
    "ride_bell": 53,  # Ride Bell
    "ride2": 59,  # Ride Cymbal 2
    "splash": 55,  # Splash Cymbal
    "china": 52,  # Chinese Cymbal
    # Toms
    "tom_low": 41,  # Low Floor Tom
    "tom_floor_high": 43,  # High Floor Tom
    "tom_mid": 45,  # Low Tom
    "tom_mid_low": 47,  # Low-Mid Tom
    "tom_mid_high": 48,  # Hi-Mid Tom
    "tom_high": 50,  # High Tom
    # Percussion
    "tambourine": 54,  # Tambourine
    "cowbell": 56,  # Cowbell
    "bongo_high": 60,  # Hi Bongo
    "bongo_low": 61,  # Low Bongo
    "conga_mute": 62,  # Mute Hi Conga
    "conga_high": 63,  # Open Hi Conga
    "conga_low": 64,  # Low Conga
    "claves": 75,  # Claves
    "woodblock_high": 76,  # Hi Wood Block
    "woodblock_low": 77,  # Low Wood Block
}

# Psychoacoustic constants based on research
GOLDEN_RATIO = 1.618033988749
GROOVE_TIMING_MS = (20, 30)  # Human-preferred microtiming range
PREDICTABILITY_RATIO = 0.85  # 85% predictable, 15% surprise
FRACTAL_DEPTH = 3  # Fractal recursion depth for natural complexity

# Humanize constants
GHOST_NOTE_VELOCITY_RANGE = (25, 50)  # Subtle ghost notes
GHOST_NOTE_PROBABILITY = 0.35  # Chance of ghost note on eligible positions
TIMING_HUMANIZE_MS = (-15, 15)  # Timing variation range in ms


def _triangular(mean: float, spread: float) -> float:
    return np.random.triangular(-spread, 0.0, spread) + mean


def _clip_velocity(val: float, lo: int = 1, hi: int = 127) -> int:
    return max(lo, min(hi, int(round(val))))


def _fibonacci_probabilities(steps: int, base_prob: float = 0.3) -> List[float]:
    """Generate probabilities using Fibonacci sequence for natural rhythm patterns."""
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    probs = []

    for i in range(steps):
        # Use Fibonacci ratios for probability modulation
        fib_idx = i % len(fib)
        fib_ratio = fib[fib_idx] / fib[(fib_idx + 1) % len(fib)]
        prob = base_prob * (0.5 + 0.5 * fib_ratio)
        probs.append(min(1.0, prob))

    return probs


def _golden_ratio_timing(steps: int, bpm: float) -> List[float]:
    """Generate timing offsets based on golden ratio for pleasing rhythm."""
    base_timing = 60.0 / bpm  # seconds per beat
    offsets = []

    for i in range(steps):
        # Golden ratio creates pleasing mathematical relationships
        golden_offset = (i * GOLDEN_RATIO) % 1.0
        # Convert to milliseconds for microtiming
        ms_offset = golden_offset * base_timing * 1000
        # Keep within human-preferred groove range
        clamped_offset = max(GROOVE_TIMING_MS[0], min(GROOVE_TIMING_MS[1], ms_offset))
        offsets.append(clamped_offset / 1000.0)  # Convert back to seconds

    return offsets


def _fractal_pattern(length: int, complexity: float) -> List[float]:
    """Generate fractal-based pattern for natural complexity."""
    # Use depth based on length to ensure we get the right number of items
    depth = max(1, int(math.log2(length)) + 1)

    pattern = []
    for _ in range(length):
        # Each position gets a fractal-influenced value
        base_val = random.random()
        detail = sum(random.random() * (0.5 ** (d + 1)) for d in range(depth))
        pattern.append((base_val + detail * complexity) / (1 + complexity))

    return [min(1.0, max(0.0, p)) for p in pattern]


def _natural_velocity_curve(steps: int, base_velocity: Tuple[int, int]) -> List[int]:
    """Generate natural velocity variation using sine wave curves."""
    lo, hi = base_velocity
    velocities = []

    for i in range(steps):
        # Use multiple sine waves for natural variation
        primary = math.sin(i * 0.5) * 0.3  # Main curve
        secondary = math.sin(i * 0.23) * 0.15  # Secondary variation
        tertiary = math.sin(i * 0.77) * 0.1  # High frequency detail

        # Combine waves for natural feel
        combined = primary + secondary + tertiary
        normalized = (combined + 1.0) / 2.0  # Normalize to 0-1

        # Apply to velocity range
        velocity = lo + (hi - lo) * normalized
        velocities.append(_clip_velocity(velocity, lo, hi))

    return velocities


def _psychoacoustic_balance(
    probs: List[float], predictability: float = PREDICTABILITY_RATIO
) -> List[float]:
    """Balance predictability vs surprise for optimal human preference."""
    balanced = []

    for prob in probs:
        # Add controlled randomness while maintaining overall predictability
        if random.random() < predictability:
            # Use original probability (predictable)
            balanced.append(prob)
        else:
            # Add surprise element within reasonable bounds
            surprise_factor = random.uniform(0.1, 0.4)
            if random.random() < 0.5:
                # Increase probability for syncopation
                balanced.append(min(1.0, prob * (1 + surprise_factor)))
            else:
                # Decrease probability for rests
                balanced.append(max(0.0, prob * (1 - surprise_factor)))

    return balanced


def _generate_ghost_notes(
    steps_per_bar: int,
    steps_per_beat: int,
    meter: Tuple[int, int],
    humanize_amount: float = 0.5,
) -> List[Tuple[int, int]]:
    """Generate ghost note positions and velocities for humanization.

    Returns list of (step_position, velocity) tuples for ghost notes.
    Ghost notes typically fall on upbeats and subdivisions.
    """
    ghost_notes = []
    beats_per_bar = meter[0]

    for step in range(steps_per_bar):
        beat_position = step % steps_per_beat
        beat_num = step // steps_per_beat

        # Ghost notes on weak subdivisions (not on main beats)
        is_main_beat = beat_position == 0
        is_backbeat = (beat_num % 2 == 1) and is_main_beat

        # Skip main beats and backbeats - those get real hits
        if is_main_beat:
            continue

        # Higher probability for certain subdivisions based on meter
        ghost_prob = GHOST_NOTE_PROBABILITY * humanize_amount

        # 16th note ghost positions (between 8ths) are more common
        if steps_per_beat >= 4:
            if beat_position in (1, 3):  # "e" and "a" in "1 e & a"
                ghost_prob *= 1.3
            elif beat_position == 2:  # "&" position
                ghost_prob *= 0.8

        if random.random() < ghost_prob:
            # Velocity varies with position - later subdivisions slightly softer
            vel_range = GHOST_NOTE_VELOCITY_RANGE
            position_factor = 1.0 - (beat_position / steps_per_beat) * 0.2
            vel = random.randint(
                int(vel_range[0] * position_factor), int(vel_range[1] * position_factor)
            )
            ghost_notes.append((step, max(1, vel)))

    return ghost_notes


def _humanize_timing(
    base_tick: int, ticks_per_beat: int, humanize_amount: float
) -> int:
    """Add human-like timing variation to a tick position."""
    # Convert humanize range to ticks
    ms_range = TIMING_HUMANIZE_MS
    # Assuming ~120 BPM as reference (500ms per beat)
    ticks_per_ms = ticks_per_beat / 500.0

    max_offset_ticks = int(ms_range[1] * ticks_per_ms * humanize_amount)
    if max_offset_ticks > 0:
        offset = random.randint(-max_offset_ticks, max_offset_ticks)
        return max(0, base_tick + offset)
    return base_tick


def _get_meter_accents(
    meter: Tuple[int, int], steps_per_bar: int, steps_per_beat: int
) -> List[float]:
    """Get accent pattern based on time signature for natural phrasing."""
    beats_per_bar = meter[0]
    accents = []

    for step in range(steps_per_bar):
        beat_num = step // steps_per_beat
        beat_position = step % steps_per_beat

        if beat_position == 0:  # On the beat
            if meter == (3, 4):
                # Waltz feel: strong-weak-weak
                if beat_num == 0:
                    accents.append(1.0)
                else:
                    accents.append(0.7)
            elif meter == (2, 4):
                # March feel: strong-weak
                if beat_num == 0:
                    accents.append(1.0)
                else:
                    accents.append(0.75)
            else:  # 4/4
                # Standard: strong-weak-medium-weak
                if beat_num == 0:
                    accents.append(1.0)
                elif beat_num == 2:
                    accents.append(0.85)
                else:
                    accents.append(0.7)
        else:
            # Off-beat positions get progressively softer
            accents.append(0.5 - (beat_position / steps_per_beat) * 0.2)

    return accents


def generate_stochastic_pattern(
    bpm: float,
    bars: int = 4,
    meter: Tuple[int, int] = (4, 4),
    steps_per_beat: int = 4,
    swing: float = 0.12,
    intensity: float = 0.9,
    seed: int = 42,
    style: str = "house",
    groove_intensity: float = 0.7,
    humanize: float = 0.0,  # 0.0 = off, 1.0 = full humanization
    predictability: float = 0.85,  # 0.0 = chaotic, 1.0 = fully predictable
) -> MidiFile:
    random.seed(seed)
    np.random.seed(seed)

    beats_per_bar = meter[0]
    steps_per_bar = beats_per_bar * steps_per_beat

    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message("program_change", program=0, time=0))
    tempo = bpm2tempo(bpm)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    # Helper to create crash on beat 1 of every N bars
    def _crash_pattern(steps: int, every_n_bars: int = 4) -> List[float]:
        probs = [0.0] * steps
        # Crash on first beat
        probs[0] = 0.95 if every_n_bars <= 4 else 0.8
        return probs

    # Helper to create ride pattern (8ths or quarters)
    def _ride_pattern(steps: int, density: str = "eighth") -> List[float]:
        probs = []
        for i in range(steps):
            if density == "quarter" and i % steps_per_beat == 0:
                probs.append(0.85)
            elif density == "eighth" and i % (steps_per_beat // 2) == 0:
                probs.append(0.80)
            else:
                probs.append(0.0)
        return probs

    # Generate psychoacoustic patterns for each style
    if style == "house":
        # House: Four-on-the-floor with driving hats and sparse crashes
        kick_base = _fibonacci_probabilities(steps_per_bar, 0.25)
        kick_probs = [
            0.98 if (i % steps_per_beat == 0) else p * 0.2
            for i, p in enumerate(kick_base)
        ]

        snare_base = _fibonacci_probabilities(steps_per_bar, 0.2)
        snare_probs = [
            0.95 if (i % (2 * steps_per_beat) == steps_per_beat) else p * 0.15
            for i, p in enumerate(snare_base)
        ]

        # Clap layered with snare
        clap_probs = [
            0.70 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.0
            for i in range(steps_per_bar)
        ]

        hat_fractal = _fractal_pattern(steps_per_bar, 0.6)
        hat_probs = [
            p * 0.9 if (i % (steps_per_beat // 2) != 0) else p * 0.7
            for i, p in enumerate(hat_fractal)
        ]

        instruments = [
            ("kick", kick_probs, (100, 127), 0.002, _natural_velocity_curve),
            ("snare", snare_probs, (95, 120), 0.003, _natural_velocity_curve),
            ("clap", clap_probs, (80, 105), 0.002, _natural_velocity_curve),
            ("closed_hat", hat_probs, (65, 100), 0.001, _natural_velocity_curve),
            (
                "open_hat",
                _fractal_pattern(steps_per_bar, 0.4),
                (75, 100),
                0.004,
                _natural_velocity_curve,
            ),
            (
                "crash",
                _crash_pattern(steps_per_bar, 4),
                (90, 115),
                0.002,
                _natural_velocity_curve,
            ),
        ]

    elif style == "breaks":
        # Breaks: Syncopated with ghost notes and complex hats
        kick_fractal = _fractal_pattern(steps_per_bar, 0.7)
        kick_probs = [
            0.90 if i in (0, 6, 8, 14) else p * 0.4 for i, p in enumerate(kick_fractal)
        ]

        snare_fractal = _fractal_pattern(steps_per_bar, 0.5)
        snare_probs = [
            0.92 if i in (4, 12) else p * 0.35 for i, p in enumerate(snare_fractal)
        ]

        hat_probs = _fractal_pattern(steps_per_bar, 0.8)

        instruments = [
            ("kick", kick_probs, (95, 125), 0.003, _natural_velocity_curve),
            ("snare", snare_probs, (95, 125), 0.004, _natural_velocity_curve),
            ("closed_hat", hat_probs, (60, 100), 0.002, _natural_velocity_curve),
            (
                "open_hat",
                _fractal_pattern(steps_per_bar, 0.6),
                (75, 105),
                0.005,
                _natural_velocity_curve,
            ),
            (
                "crash",
                _crash_pattern(steps_per_bar, 8),
                (85, 110),
                0.003,
                _natural_velocity_curve,
            ),
        ]

    elif style == "rock":
        # Rock: Strong backbeat, driving 8th note hats, crash accents
        kick_probs = [0.0] * steps_per_bar
        # Kick on 1 and 3 (and sometimes the "and" of 2)
        for i in range(steps_per_bar):
            if i == 0:  # Beat 1
                kick_probs[i] = 0.98
            elif i == 2 * steps_per_beat:  # Beat 3
                kick_probs[i] = 0.95
            elif i == steps_per_beat + steps_per_beat // 2:  # "and" of 2
                kick_probs[i] = 0.45
            else:
                kick_probs[i] = 0.08

        # Snare on 2 and 4
        snare_probs = [
            0.98 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.05
            for i in range(steps_per_bar)
        ]

        # Driving 8th note hats
        hat_probs = [
            0.90 if (i % (steps_per_beat // 2) == 0) else 0.15
            for i in range(steps_per_bar)
        ]

        # Open hat on upbeats occasionally
        open_hat_probs = [
            0.40 if (i % steps_per_beat == steps_per_beat // 2) else 0.0
            for i in range(steps_per_bar)
        ]

        instruments = [
            ("kick", kick_probs, (100, 127), 0.003, _natural_velocity_curve),
            ("snare", snare_probs, (100, 127), 0.004, _natural_velocity_curve),
            ("closed_hat", hat_probs, (70, 100), 0.002, _natural_velocity_curve),
            ("open_hat", open_hat_probs, (75, 105), 0.003, _natural_velocity_curve),
            (
                "crash",
                _crash_pattern(steps_per_bar, 4),
                (95, 120),
                0.002,
                _natural_velocity_curve,
            ),
            (
                "ride_bell",
                [0.30 if i == 0 else 0.0 for i in range(steps_per_bar)],
                (80, 100),
                0.002,
                _natural_velocity_curve,
            ),
        ]

    elif style == "blues":
        # Blues: Shuffle feel, ride cymbal, laid back snare
        # Shuffle: emphasis on 1, skip 2, hit 3 (triplet feel approximated with 16ths)
        kick_probs = [0.0] * steps_per_bar
        for i in range(steps_per_bar):
            if i % steps_per_beat == 0:  # On the beat
                kick_probs[i] = 0.85
            elif i % steps_per_beat == 3:  # Shuffle "and" (approximating triplet)
                kick_probs[i] = 0.50

        # Snare on 2 and 4, with ghost notes
        snare_probs = [0.0] * steps_per_bar
        for i in range(steps_per_bar):
            if i % (2 * steps_per_beat) == steps_per_beat:  # Beats 2 and 4
                snare_probs[i] = 0.95
            elif i % steps_per_beat in (1, 3):  # Ghost positions
                snare_probs[i] = 0.25

        # Ride cymbal shuffle pattern
        ride_probs = [0.0] * steps_per_bar
        for i in range(steps_per_bar):
            if i % steps_per_beat == 0:  # On beat
                ride_probs[i] = 0.90
            elif i % steps_per_beat == 3:  # Shuffle
                ride_probs[i] = 0.75

        # Hi-hat on 2 and 4 with foot
        pedal_hat_probs = [
            0.70 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.0
            for i in range(steps_per_bar)
        ]

        instruments = [
            ("kick", kick_probs, (85, 115), 0.004, _natural_velocity_curve),
            ("snare", snare_probs, (70, 110), 0.005, _natural_velocity_curve),
            ("ride", ride_probs, (75, 100), 0.003, _natural_velocity_curve),
            ("pedal_hat", pedal_hat_probs, (60, 85), 0.002, _natural_velocity_curve),
            (
                "crash",
                _crash_pattern(steps_per_bar, 8),
                (80, 105),
                0.003,
                _natural_velocity_curve,
            ),
        ]

    elif style == "indie":
        # Indie: Driving but loose, tom accents, minimal cymbals
        kick_probs = [0.0] * steps_per_bar
        for i in range(steps_per_bar):
            if i == 0:  # Beat 1
                kick_probs[i] = 0.95
            elif i == 2 * steps_per_beat:  # Beat 3
                kick_probs[i] = 0.90
            elif i == 3 * steps_per_beat:  # Beat 4
                kick_probs[i] = 0.40
            else:
                kick_probs[i] = _fractal_pattern(1, 0.3)[0] * 0.15

        # Snare on 2 and 4, occasional rimshot
        snare_probs = [
            0.95 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.0
            for i in range(steps_per_bar)
        ]

        side_stick_probs = [
            0.30 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.0
            for i in range(steps_per_bar)
        ]

        # Sparse, driving hats
        hat_probs = [
            0.85 if (i % (steps_per_beat // 2) == 0) else 0.10
            for i in range(steps_per_bar)
        ]

        # Floor tom accent on beat 4 sometimes
        tom_probs = [
            0.35 if i == 3 * steps_per_beat else 0.0 for i in range(steps_per_bar)
        ]

        instruments = [
            ("kick", kick_probs, (95, 120), 0.004, _natural_velocity_curve),
            ("snare", snare_probs, (90, 120), 0.005, _natural_velocity_curve),
            ("side_stick", side_stick_probs, (70, 95), 0.003, _natural_velocity_curve),
            ("closed_hat", hat_probs, (65, 95), 0.003, _natural_velocity_curve),
            ("tom_low", tom_probs, (80, 110), 0.004, _natural_velocity_curve),
            (
                "crash",
                _crash_pattern(steps_per_bar, 8),
                (85, 110),
                0.003,
                _natural_velocity_curve,
            ),
        ]

    elif style == "jazz":
        # Jazz: Ride pattern, kick/snare comping, brush feel
        # Ride: classic jazz ride pattern (1, 2-and, 3, 4-and)
        ride_probs = [0.0] * steps_per_bar
        for i in range(steps_per_bar):
            beat_pos = i % steps_per_beat
            beat_num = i // steps_per_beat
            if beat_pos == 0:  # On beats
                ride_probs[i] = 0.90
            elif beat_pos == steps_per_beat // 2 and beat_num in (
                1,
                3,
            ):  # "and" of 2 and 4
                ride_probs[i] = 0.75

        # Sparse, comping kick
        kick_probs = _fractal_pattern(steps_per_bar, 0.4)
        kick_probs = [
            p * 0.5 if i % steps_per_beat != 0 else p * 0.3
            for i, p in enumerate(kick_probs)
        ]

        # Comping snare (cross-stick feel)
        snare_probs = _fractal_pattern(steps_per_bar, 0.35)
        snare_probs = [p * 0.4 for p in snare_probs]

        # Hi-hat on 2 and 4
        pedal_hat_probs = [
            0.85 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.0
            for i in range(steps_per_bar)
        ]

        instruments = [
            ("kick", kick_probs, (60, 95), 0.006, _natural_velocity_curve),
            ("side_stick", snare_probs, (55, 85), 0.005, _natural_velocity_curve),
            ("ride", ride_probs, (70, 100), 0.003, _natural_velocity_curve),
            ("pedal_hat", pedal_hat_probs, (60, 80), 0.002, _natural_velocity_curve),
        ]

    else:
        # Generic: Balanced backbeat with natural variation
        kick_fib = _fibonacci_probabilities(steps_per_bar, 0.22)
        kick_probs = [
            0.95 if (i % steps_per_beat == 0) else p * 0.25
            for i, p in enumerate(kick_fib)
        ]

        snare_fib = _fibonacci_probabilities(steps_per_bar, 0.18)
        snare_probs = [
            0.90 if (i % (2 * steps_per_beat) == steps_per_beat) else p * 0.25
            for i, p in enumerate(snare_fib)
        ]

        hat_fractal = _fractal_pattern(steps_per_bar, 0.5)
        hat_probs = [p * 0.8 for p in hat_fractal]

        instruments = [
            ("kick", kick_probs, (90, 120), 0.002, _natural_velocity_curve),
            ("snare", snare_probs, (90, 120), 0.003, _natural_velocity_curve),
            ("closed_hat", hat_probs, (65, 100), 0.001, _natural_velocity_curve),
            (
                "crash",
                _crash_pattern(steps_per_bar, 4),
                (85, 110),
                0.002,
                _natural_velocity_curve,
            ),
        ]

    # Apply psychoacoustic balancing and intensity scaling
    for idx, (name, probs, vel_rng, jitter, vel_func) in enumerate(instruments):
        # Balance predictability vs surprise
        balanced_probs = _psychoacoustic_balance(probs, predictability)
        # Apply intensity and groove effects
        scaled_probs = [
            max(0.0, min(1.0, p * intensity * (0.8 + 0.4 * groove_intensity)))
            for p in balanced_probs
        ]
        instruments[idx] = (name, scaled_probs, vel_rng, jitter, vel_func)

    def _step_to_ticks(step_idx: int, jitter_sec: float, golden_offset: float) -> int:
        base_beats = step_idx / steps_per_beat
        base_ticks = int(round(mid.ticks_per_beat * base_beats))

        # Apply swing
        if steps_per_beat % 2 == 0:
            eighth_step = steps_per_beat // 2
            if (step_idx % eighth_step) == (eighth_step - 1):
                swing_ticks = int(round(mid.ticks_per_beat * (0.5 * swing)))
                base_ticks += swing_ticks

        # Apply golden ratio microtiming for groove
        groove_ticks = int(round(mid.ticks_per_beat * golden_offset))
        base_ticks += groove_ticks

        # Apply traditional jitter
        sec_per_beat = tempo / 1_000_000.0
        ticks_per_sec = mid.ticks_per_beat / sec_per_beat
        jitter_ticks = int(round(jitter_sec * ticks_per_sec))
        return base_ticks + jitter_ticks

    events: List[Tuple[int, str, int]] = []
    # Generate golden ratio timing offsets for the entire pattern
    golden_offsets = _golden_ratio_timing(steps_per_bar * bars, bpm)

    # Get meter-aware accent pattern
    meter_accents = _get_meter_accents(meter, steps_per_bar, steps_per_beat)

    # Generate ghost note pattern if humanize is enabled
    ghost_notes_pattern = []
    if humanize > 0:
        ghost_notes_pattern = _generate_ghost_notes(
            steps_per_bar, steps_per_beat, meter, humanize
        )

    for bar in range(bars):
        bar_offset_steps = bar * steps_per_bar
        for name, probs, vel_rng, jitter, vel_func in instruments:
            lo, hi = vel_rng
            # Generate natural velocity curve for this instrument
            vel_curve = vel_func(steps_per_bar, vel_rng)

            for s in range(steps_per_bar):
                if random.random() < probs[s]:
                    # Apply meter accent to velocity
                    accent = meter_accents[s] if s < len(meter_accents) else 1.0
                    vel = _clip_velocity(vel_curve[s] * intensity * accent, lo, hi)

                    # Use golden ratio timing for psychoacoustic groove
                    offset_idx = (bar_offset_steps + s) % len(golden_offsets)
                    golden_offset = golden_offsets[offset_idx] * groove_intensity

                    jitter_sec = _triangular(0.0, jitter)
                    abs_step = bar_offset_steps + s
                    tick = _step_to_ticks(abs_step, jitter_sec, golden_offset)

                    # Apply humanize timing variation
                    if humanize > 0:
                        tick = _humanize_timing(tick, mid.ticks_per_beat, humanize)

                    events.append((tick, name, vel))

        # Add ghost notes for snare (most common ghost note instrument)
        if humanize > 0 and ghost_notes_pattern:
            for ghost_step, ghost_vel in ghost_notes_pattern:
                # Regenerate ghost notes each bar with some variation
                if random.random() < 0.7:  # Don't repeat every bar exactly
                    abs_step = bar_offset_steps + ghost_step
                    tick = _step_to_ticks(abs_step, 0, 0)
                    tick = _humanize_timing(tick, mid.ticks_per_beat, humanize)
                    events.append((tick, "snare", ghost_vel))

    events.sort(key=lambda x: x[0])

    last_tick = 0
    for tick, name, vel in events:
        delta = tick - last_tick
        note = DRUMS.get(name, DRUMS["closed_hat"])
        track.append(
            Message("note_on", channel=9, note=note, velocity=vel, time=max(0, delta))
        )
        track.append(Message("note_off", channel=9, note=note, velocity=0, time=60))
        last_tick = tick + 60

    return mid


from .bpm import fetch_bpm_from_bpmdatabase


def generate_from_song(
    song_title: str,
    artist: Optional[str] = None,
    bars: int = 8,
    style: str = "house",
    meter: Tuple[int, int] = (4, 4),
    steps_per_beat: int = 4,
    swing: float = 0.10,
    intensity: float = 0.9,
    groove_intensity: float = 0.7,
    humanize: float = 0.0,
    predictability: float = 0.85,
    seed: Optional[int] = None,
    fallback_bpm: Optional[float] = None,
    verbose: bool = False,
) -> Tuple[MidiFile, float]:
    bpm = fetch_bpm_from_bpmdatabase(song_title, artist, verbose=verbose)
    if bpm is None:
        if fallback_bpm is None:
            raise RuntimeError("BPM lookup failed and no fallback BPM provided.")
        bpm = fallback_bpm

    if seed is None:
        seed_str = f"{song_title}|{artist or ''}|{int(bpm)}"
        seed = abs(hash(seed_str)) % (2**31)

    mid = generate_stochastic_pattern(
        bpm=bpm,
        bars=bars,
        meter=meter,
        steps_per_beat=steps_per_beat,
        swing=swing,
        intensity=intensity,
        groove_intensity=groove_intensity,
        humanize=humanize,
        predictability=predictability,
        seed=seed,
        style=style,
    )
    return mid, bpm
