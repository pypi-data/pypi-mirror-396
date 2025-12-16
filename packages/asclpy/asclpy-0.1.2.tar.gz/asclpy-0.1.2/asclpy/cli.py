"""
Command-line interface for asclpy.
"""

import click

from .loader import get_default_registry, load_tuning


@click.group()
@click.version_option()
def cli():
    """asclpy - Ableton Scala tuning file parser and library."""
    pass


@cli.command()
@click.option("--compact", is_flag=True, help="Omit descriptions and warnings")
def list(compact: bool):
    """List all available tunings with their documentation and validation warnings."""
    registry = get_default_registry()

    click.echo(click.style("\n📚 Available Tunings\n", fg="cyan", bold=True))

    for name in registry.list():
        try:
            tuning = registry.load(name)
            data = tuning._midi_mapper.data

            # Display tuning name
            click.echo(click.style(f"\n{name}", fg="green", bold=True))

            # Display description if available (unless compact)
            if not compact and data.description:
                click.echo(f"  {data.description}")

            # Display basic info
            click.echo(f"  Notes per octave: {data.notes_per_octave}")

            # Display reference pitch if available
            if data.reference_pitch:
                ref = data.reference_pitch
                click.echo(
                    f"  Reference: octave {ref.octave}, index {ref.note_index}, {ref.frequency} Hz"
                )

            # Display note range if available
            if data.note_range:
                nr = data.note_range
                if nr.min_freq is not None:
                    max_display = f"{nr.max_freq} Hz" if nr.max_freq else "unlimited"
                    click.echo(f"  Range: {nr.min_freq} Hz - {max_display}")
                elif nr.min_octave is not None:
                    max_octave_display = (
                        str(nr.max_octave) if nr.max_octave is not None else "unlimited"
                    )
                    max_index_display = (
                        str(nr.max_index) if nr.max_index is not None else ""
                    )
                    if nr.max_octave is not None:
                        click.echo(
                            f"  Range: octave {nr.min_octave}.{nr.min_index} - {max_octave_display}.{max_index_display}"
                        )
                    else:
                        click.echo(
                            f"  Range: octave {nr.min_octave}.{nr.min_index} - unlimited"
                        )

            # Display validation warnings if any (unless compact)
            if (
                not compact
                and hasattr(data, "validation_warnings")
                and data.validation_warnings
            ):
                click.echo(click.style("  ⚠️  Warnings:", fg="yellow"))
                for warning in data.validation_warnings:
                    click.echo(click.style(f"     • {warning}", fg="yellow"))

        except Exception as e:
            click.echo(click.style(f"  ❌ Error loading tuning: {e}", fg="red"))

    click.echo(f"\nTotal tunings: {len(registry.list())}\n")


@cli.command()
@click.argument("tuning")
@click.option("--min-midi", default=0, help="Minimum MIDI note number (default: 0)")
@click.option("--max-midi", default=127, help="Maximum MIDI note number (default: 127)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "csv", "json"], case_sensitive=False),
    default="table",
    help="Output format",
)
def table(tuning: str, min_midi: int, max_midi: int, output_format: str):
    """
    Print a MIDI note to frequency table for a given tuning.

    TUNING can be a tuning name (e.g., '12_tet_edo') or path to an .ascl file.
    """
    try:
        t = load_tuning(tuning)
    except (KeyError, FileNotFoundError) as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        return

    data = t._midi_mapper.data

    # Get valid MIDI range for this tuning
    valid_min, valid_max = t.get_valid_midi_range()

    # Clamp to valid range
    min_midi = max(min_midi, valid_min)
    max_midi = min(max_midi, valid_max)

    if output_format == "json":
        import json

        result = {
            "tuning": tuning,
            "description": data.description,
            "notes_per_octave": data.notes_per_octave,
            "valid_range": {"min": valid_min, "max": valid_max},
            "midi_to_freq": {},
        }

        for midi in range(min_midi, max_midi + 1):
            if t.is_midi_valid(midi):
                result["midi_to_freq"][midi] = round(t.midi_to_freq(midi), 6)

        click.echo(json.dumps(result, indent=2))

    elif output_format == "csv":
        click.echo("midi,note,frequency")
        for midi in range(min_midi, max_midi + 1):
            if t.is_midi_valid(midi):
                freq = t.midi_to_freq(midi)
                note_name = (
                    t.get_note_name(midi % data.notes_per_octave)
                    or f"#{midi % data.notes_per_octave}"
                )
                octave = midi // 12 - 2  # MIDI octave
                click.echo(f"{midi},{note_name}{octave},{freq:.6f}")

    else:  # table format
        # Header
        click.echo()
        click.echo(click.style(f"🎵 {tuning.upper()}", fg="cyan", bold=True))
        if data.description:
            click.echo(f"   {data.description}")
        click.echo(f"   {data.notes_per_octave} notes per octave")
        click.echo(f"   Valid MIDI range: {valid_min}-{valid_max}")
        click.echo()
        header = f"{'MIDI':<6} {'Note':<8} {'Octave':<8} {'Frequency (Hz)':<20}"
        click.echo(header)
        click.echo("-" * len(header))

        # Table rows
        for midi in range(min_midi, max_midi + 1):
            if t.is_midi_valid(midi):
                freq = t.midi_to_freq(midi)
                note_name = t.get_note_name(midi % data.notes_per_octave)

                if note_name:
                    note_display = note_name
                else:
                    note_display = f"#{midi % data.notes_per_octave}"

                # Calculate octave (MIDI octave system)
                octave = midi // 12 - 2

                # Color code by frequency range
                if freq < 100:
                    color = "blue"
                elif freq < 1000:
                    color = "green"
                elif freq < 5000:
                    color = "yellow"
                else:
                    color = "red"

                line = f"{midi:<6} {note_display:<8} {octave:<8} {freq:<20.6f}"
                click.echo(click.style(line, fg=color))

        click.echo()


if __name__ == "__main__":
    cli()
