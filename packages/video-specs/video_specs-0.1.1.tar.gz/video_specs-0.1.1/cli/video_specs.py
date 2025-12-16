#!/usr/bin/env python3
"""
Video Specifications Tool - Outil interactif pour capturer les caractéristiques d'une vidéo
"""
import json

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import click
import rich_click as click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

from cli.const import LOGO
from cli.utils import banner, success_banner
from helpers.to_html import to_html
from helpers.to_xml import to_xml
from helpers.to_text_blocks import to_text_blocks

# Configuration rich-click pour un menu d'aide élégant
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.ERRORS_SUGGESTION = "Essayez 'video-specs --help' pour plus d'informations."
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_SWITCH = "bold green"

console = Console()


class VideoSpecs:
    """Classe pour gérer les spécifications vidéo"""

    def __init__(self):
        self.specs = {
            "technical": {},
            "setting_atmosphere": {},
            "camera_visuals": {},
            "scene_content": {},
            "characters": [],
            "dialogs": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0"
            }
        }

    def collect_technical_specs(self):
        """Collecte les spécifications techniques"""
        console.clear()
        console.print(LOGO)
        console.input("Appuyez sur Entrée pour continuer...")
        banner("Technical Specifications")

        aspect_ratios = ["16:9", "9:16", "4:3", "1:1", "2.35:1", "2.39:1", "21:9", "18:9"]
        resolutions = ["4K (3840×2160)", "2K (2048×1080)", "1080p", "720p", "480p", "360p"]
        frame_rates = ["15", "24", "25", "30", "60", "120"]

        # Aspect Ratio
        console.print("\n[yellow3]Ratios disponibles:[/yellow3]", ", ".join(aspect_ratios))
        aspect_ratio = Prompt.ask(
            "Aspect Ratio",
            default="9:16"
        )

        # Resolution
        console.print("\n[yellow3]Résolutions disponibles:[/yellow3]", ", ".join(resolutions))
        resolution = Prompt.ask(
            "Resolution",
            default="4K"
        )

        # Duration
        duration = Prompt.ask(
            "Duration (format HH:MM:SS)",
            default="00:00:15"
        )

        # Frame Rate
        console.print("\n[yellow3]Frame rates disponibles:[/yellow3]", ", ".join(frame_rates))
        frame_rate = Prompt.ask(
            "Frame Rate (fps)",
            default="25"
        )

        self.specs["technical"] = {
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration": duration,
            "frame_rate": f"{frame_rate} fps"
        }

    def collect_setting_atmosphere(self):
        """Collecte les paramètres de décor et atmosphère"""
        banner("Setting & Atmosphere")
        times_of_day = ["morning", "afternoon", "evening", "night", "midnight", "dawn", "dusk", "golden hour"]
        seasons = ["spring", "summer", "autumn", "winter"]
        weathers = ["sunny", "cloudy", "rainy", "stormy", "snowy", "foggy", "overcast"]
        location_types = ["indoor", "outdoor", "urban", "rural", "nature", "studio", "mixed"]
        lighting_styles = ["natural", "dramatic", "soft", "hard", "low-key", "high-key", "neon", "cinematic"]

        console.print("\n[yellow3]Times of day:[/yellow3]", ", ".join(times_of_day))
        time_of_day = Prompt.ask("Time of Day", default="afternoon")

        console.print("\n[yellow3]Seasons:[/yellow3]", ", ".join(seasons))
        season = Prompt.ask("Season", default="summer")

        console.print("\n[yellow3]Weather:[/yellow3]", ", ".join(weathers))
        weather = Prompt.ask("Weather", default="sunny")

        console.print("\n[yellow3]Location types:[/yellow3]", ", ".join(location_types))
        location_type = Prompt.ask("Location Type", default="outdoor")

        location_description = Prompt.ask(
            "Location Description",
            default="A beautiful park with trees"
        )

        console.print("\n[yellow3]Lighting styles:[/yellow3]", ", ".join(lighting_styles))
        lighting_style = Prompt.ask("Lighting Style", default="natural")

        self.specs["setting_atmosphere"] = {
            "time_of_day": time_of_day,
            "season": season,
            "weather": weather,
            "location_type": location_type,
            "location_description": location_description,
            "lighting_style": lighting_style
        }

    def collect_camera_visuals(self):
        """Collecte les paramètres de caméra et visuels"""
        banner("Camera & Visuals")

        shot_types = ["close-up", "medium shot", "wide shot", "extreme close-up", "full shot", "over-the-shoulder", "POV", "establishing shot"]
        camera_movements = ["static", "pan", "tilt", "dolly", "tracking", "handheld", "crane", "steadicam", "drone"]
        focus_types = ["shallow depth of field", "deep focus", "rack focus", "soft focus", "selective focus"]
        lens_choices = ["wide-angle", "telephoto", "standard", "fisheye", "macro", "anamorphic"]
        color_palettes = ["warm", "cool", "monochrome", "vibrant", "desaturated", "pastel", "neon", "earth tones"]

        console.print("\n[yellow3]Shot types:[/yellow3]", ", ".join(shot_types[:5]), "...")
        shot_type = Prompt.ask("Shot Type", default="medium shot")

        console.print("\n[yellow3]Camera movements:[/yellow3]", ", ".join(camera_movements[:5]), "...")
        camera_movement = Prompt.ask("Camera Movement", default="static")

        console.print("\n[yellow3]Focus types:[/yellow3]", ", ".join(focus_types[:3]), "...")
        focus = Prompt.ask("Focus", default="shallow depth of field")

        console.print("\n[yellow3]Lens choices:[/yellow3]", ", ".join(lens_choices))
        lens_choice = Prompt.ask("Lens Choice", default="standard")

        console.print("\n[yellow3]Color palettes:[/yellow3]", ", ".join(color_palettes[:5]), "...")
        color_palette = Prompt.ask("Color Palette", default="neutral")

        self.specs["camera_visuals"] = {
            "shot_type": shot_type,
            "camera_movement": camera_movement,
            "focus": focus,
            "lens_choice": lens_choice,
            "color_palette": color_palette
        }

    def collect_scene_content(self):
        """Collecte le contenu de la scène"""
        banner("Scene Content")

        crowd_densities = ["empty", "sparse", "moderate", "crowded", "packed"]
        moods = ["happy", "sad", "tense", "peaceful", "energetic", "melancholic", "mysterious", "dramatic", "romantic"]

        console.print("\n[yellow3]Crowd densities:[/yellow3]", ", ".join(crowd_densities))
        crowd_density = Prompt.ask("Crowd Density", default="moderate")

        subject_count = Prompt.ask("Subject Count", default="1")

        console.print("\n[yellow3]Moods/Tones:[/yellow3]", ", ".join(moods[:5]), "...")
        mood = Prompt.ask("Mood / Tone", default="peaceful")

        action_description = Prompt.ask(
            "Action Description",
            default="A person walking through the park"
        )

        self.specs["scene_content"] = {
            "crowd_density": crowd_density,
            "subject_count": int(subject_count),
            "mood_tone": mood,
            "action_description": action_description
        }

    def collect_characters(self):
        """Collecte les informations sur les personnages"""
        banner("Characters")

        roles = ["protagonist", "antagonist", "supporting", "extra", "narrator", "sidekick"]

        count = 1
        while count > 0:
            console.print(f"\n[cyan]Personnage #{len(self.specs['characters']) + 1}[/cyan]")

            name = Prompt.ask("Name", default=f"Character {len(self.specs['characters']) + 1}")

            console.print("\n[yellow3]Roles disponibles:[/yellow3]", ", ".join(roles))
            role = Prompt.ask("Role", default="protagonist")

            age = Prompt.ask("Age", default="30")

            costume = Prompt.ask(
                "Costume",
                default="Casual clothes"
            )

            physical_appearance = Prompt.ask(
                "Physical Appearance",
                default="Average height, brown hair"
            )

            character = {
                "name": name,
                "role": role,
                "age": age,
                "costume": costume,
                "physical_appearance": physical_appearance
            }

            self.specs["characters"].append(character)

            # Demander si on ajoute un autre personnage
            add_more = Confirm.ask(
                "\n[green]Ajouter un autre personnage ?[/green]",
                default=False
            )

            if not add_more:
                count -= 1

    def collect_dialogs(self):
        """Collecte les dialogues"""
        banner("Dialogs")

        if not self.specs["characters"]:
            console.print("[yellow]Aucun personnage défini. Impossible d'ajouter des dialogues sans personnages.[/yellow]")
            return

        character_names = [c["name"] for c in self.specs["characters"]]
        
        # Demander si on veut ajouter des dialogues
        if not Confirm.ask("\n[green]Voulez-vous ajouter des dialogues ?[/green]", default=True):
            return

        while True:
            console.print(f"\n[cyan]Ligne de dialogue #{len(self.specs['dialogs']) + 1}[/cyan]")

            console.print("\n[yellow3]Personnages disponibles:[/yellow3]", ", ".join(character_names))
            character_id = Prompt.ask(
                "Personnage",
                choices=character_names
            )

            emotion = Prompt.ask("Émotion", default="neutral")
            
            content = Prompt.ask("Contenu")

            line = {
                "character": character_id,
                "emotion": emotion,
                "content": content
            }

            self.specs["dialogs"].append(line)

            if not Confirm.ask("\n[green]Ajouter une autre ligne ?[/green]", default=True):
                break

    def to_json(self) -> str:
        """Exporte en JSON formaté"""
        return json.dumps(self.specs, indent=2, ensure_ascii=True)

    def to_xml(self) -> str:
        """Exporte en XML formaté"""
        return to_xml(self.specs)

    def to_html(self) -> str:
        """Exporte en HTML formaté"""
        return to_html(self.specs)

    def to_text_blocks(self) -> str:
        """Exporte en blocs de texte narratif"""
        return to_text_blocks(self.specs)

    def display_summary(self):
        """Affiche un résumé des spécifications collectées"""
        console.clear()
        success_banner("Collecte terminée !")
        console.input()
        console.clear()


        # Table technique
        table = Table(
            title="📹 Technical Specs", 
            box=box.SIMPLE, 
            show_header=False
        )
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="white")
        for key, value in self.specs["technical"].items():
            table.add_row(key.replace("_", " ").title(), str(value))
        console.print(Align.center(table))

        # Table characters
        if self.specs["characters"]:
            console.print()
            char_table = Table(title="👥 Characters", box=box.SIMPLE)
            char_table.add_column("Name", style="magenta")
            char_table.add_column("Role", style="yellow3")
            char_table.add_column("Age", style="cyan")
            for char in self.specs["characters"]:
                char_table.add_row(char["name"], char["role"], char["age"])
            console.print(Align.center(char_table))

        # Table dialogs
        if self.specs["dialogs"]:
            console.print()
            dialog_table = Table(title="💬 Dialogs", box=box.SIMPLE)
            dialog_table.add_column("Character", style="magenta")
            dialog_table.add_column("Emotion", style="yellow3")
            dialog_table.add_column("Content", style="white")
            for line in self.specs["dialogs"]:
                dialog_table.add_row(line["character"], line["emotion"], line["content"])
            console.print(Align.center(dialog_table))


@click.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="📁 Fichier de sortie (extension: .json, .xml, .html, .txt)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "xml", "html", "text-blocks"], case_sensitive=False),
    help="📋 Format de sortie (détecté automatiquement depuis l'extension si non spécifié)"
)
@click.option(
    "--interactive/--no-interactive", "-i/-n",
    default=True,
    help="🖱️  Mode interactif (par défaut) ou non-interactif"
)
def main(output, format, interactive):
    """
    Video Specifications Tool

    Outil interactif pour capturer toutes les caractéristiques d'une vidéo.

    Catégories disponibles:
    • Technical (aspect ratio, resolution, duration, frame rate)
    • Setting & Atmosphere (time, season, weather, location)
    • Camera & Visuals (shot type, movement, focus, lens)
    • Scene Content (crowd, subjects, mood, action)
    • Characters (illimité, avec nom, rôle, âge, costume, apparence)

    Formats d'export:
    • JSON (données structurées)
    • XML (format standard)
    • HTML (visualisation élégante)
    • TEXT-BLOCKS (blocs narratifs)

    Exemples d'utilisation:

        Mode interactif (par défaut)
        video-specs

        Sauvegarder en JSON:
        video-specs -o video.json

        Sauvegarder en XML:
        video-specs -o specs.xml

        Sauvegarder en HTML (avec visualisation):
        video-specs -o report.html
    """
    console.clear()
    console.print(LOGO)

    if not interactive:
        console.print("Mode non-interactif non encore implémenté")
        return

    # Collecte des données
    video = VideoSpecs()

    try:
        video.collect_technical_specs()
        video.collect_setting_atmosphere()
        video.collect_camera_visuals()
        video.collect_scene_content()
        video.collect_characters()
        video.collect_dialogs()

        # Afficher le résumé
        video.display_summary()

        # Déterminer le format de sortie
        if output:
            output_path = Path(output)
            if not format:
                # Détecter depuis l'extension
                ext = output_path.suffix.lower()
                if ext == ".json":
                    format = "json"
                elif ext == ".xml":
                    format = "xml"
                elif ext == ".html":
                    format = "html"
                elif ext == ".txt":
                    format = "text-blocks"
                else:
                    format = "json"  # Par défaut
        else:
            # Demander le format si pas de fichier de sortie
            console.clear()
            format = Prompt.ask(
                "Format de sortie",
                choices=["json", "xml", "html", "text-blocks"],
                default="json"
            )

        # Générer la sortie
        console.print(f"\n[cyan]Génération du fichier {format.upper()}...[/cyan]")

        if format == "json":
            output_data = video.to_json()
        elif format == "xml":
            output_data = video.to_xml()
        elif format == "html":
            output_data = video.to_html()
        elif format == "text-blocks":
            output_data = video.to_text_blocks()

        # Sauvegarder ou afficher
        if output:
            output_path.write_text(output_data, encoding="utf-8")
            console.print(f"\n[green]✓ Fichier sauvegardé:[/green] {output_path}")
        else:
            console.print("\n" + "=" * 80)
            console.print(output_data)
            console.print("=" * 80)

            # Proposer de sauvegarder
            if Confirm.ask("\n[yellow3]Sauvegarder dans un fichier ?[/yellow3]", default=True):
                default_name = f"video_specs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
                filename = Prompt.ask("Nom du fichier", default=default_name)
                Path(filename).write_text(output_data, encoding="utf-8")
                console.print(f"[green]✓ Fichier sauvegardé:[/green] {filename}")

    except KeyboardInterrupt:
        console.print("\n[yellow3]Annulé par l'utilisateur[/yellow3]")
        return


if __name__ == "__main__":
    main()