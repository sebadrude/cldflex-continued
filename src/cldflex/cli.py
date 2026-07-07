"""Console script for cldflex."""
import logging
import sys
from pathlib import Path

import click
from writio import load

from cldflex.flex2csv import convert as flex2csv_convert
from cldflex.lift2csv import convert as lift2csv_convert

log = logging.getLogger(__name__)


def _load_config(config_file, input_file=None):
    """Load a config. Explicit --conf wins; otherwise look for cldflex.yaml in
    the current directory, then beside the input file (so a config can travel
    next to the .lift export). Returns None if nothing is found."""
    if config_file:
        return load(config_file)
    if Path("cldflex.yaml").is_file():
        return load("cldflex.yaml")
    if input_file is not None:
        beside = Path(input_file).parent / "cldflex.yaml"
        if beside.is_file():
            log.info(f"Using config {beside.resolve()}")
            return load(beside)
    return None


def _apply_lang_overrides(conf, gloss_lgs, obj_lg):
    """Merge CLI language overrides into the (possibly empty) config dict.
    --gloss-lgs is a comma-separated, ordered keep-list (first = primary)."""
    conf = dict(conf) if conf else {}
    if gloss_lgs:
        conf["gloss_lgs"] = [part.strip() for part in gloss_lgs.split(",") if part.strip()]
    if obj_lg:
        conf["obj_lg"] = obj_lg
    return conf


@click.group()
def main():
    pass  # pragma: no cover


@main.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-c",
    "--conf",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option("-d", "--cldf", "cldf", default=False, is_flag=True)
@click.option(
    "--gloss-lgs",
    "gloss_lgs",
    default=None,
    help="Comma-separated analysis languages to keep; the first is primary "
    "(drives sense names/descriptions). Overrides config. Example: --gloss-lgs pt,en",
)
@click.option(
    "--obj-lg",
    "obj_lg",
    default=None,
    help="Object (vernacular) language code. Overrides config.",
)
def dictionary(filename, config_file, cldf, output_dir, gloss_lgs, obj_lg):
    if not output_dir:
        output_dir = Path(filename.parents[0])
    conf = _apply_lang_overrides(
        _load_config(config_file, filename), gloss_lgs, obj_lg
    )
    lift2csv_convert(
        filename,
        conf=conf,
        cldf=cldf,
        output_dir=output_dir,
        cldf_mode="dictionary",
    )


@main.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-c",
    "--conf",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option("-d", "--cldf", "cldf", default=False, is_flag=True)
# --rich previously also declared "-d", colliding with --cldf and making click
# emit a UserWarning and the -d short flag ambiguous. Give it its own short
# flag "-r". See bug #2.
@click.option("-r", "--rich", "rich", default=False, is_flag=True)
@click.option(
    "--gloss-lgs",
    "gloss_lgs",
    default=None,
    help="Comma-separated analysis languages to keep; the first is primary "
    "(drives sense names/descriptions). Overrides config. Example: --gloss-lgs pt,en",
)
@click.option(
    "--obj-lg",
    "obj_lg",
    default=None,
    help="Object (vernacular) language code. Overrides config.",
)
def wordlist(filename, config_file, cldf, output_dir, rich, gloss_lgs, obj_lg):
    if not output_dir:
        output_dir = Path(filename.parents[0])
    if rich:
        cldf_mode = "rich"
    else:
        cldf_mode = "wordlist"
    conf = _apply_lang_overrides(
        _load_config(config_file, filename), gloss_lgs, obj_lg
    )
    lift2csv_convert(
        filename,
        conf=conf,
        cldf=cldf,
        output_dir=output_dir,
        cldf_mode=cldf_mode,
    )


@main.command()
@click.argument("filename", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-c",
    "--conf",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(exists=True, path_type=Path),
    default=".",
)
@click.option(
    "-l",
    "--lexicon",
    "lexicon_file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option(
    "-a",
    "--audio",
    "audio_folder",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option("-d", "--cldf", "cldf", default=False, is_flag=True)
def corpus(filename, config_file, lexicon_file, audio_folder, cldf, output_dir):
    conf = _load_config(config_file)
    if not output_dir:
        output_dir = Path(".")
    flex2csv_convert(
        filename,
        conf=conf,
        lexicon_file=lexicon_file,
        cldf=cldf,
        output_dir=output_dir,
        audio_folder=audio_folder,
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
