import click
from LabelManager import LabelManager
from UtilLabelMe import UtilLabelMe

@click.group("cli")
@click.pass_context
def cli(ctx):
    ctx.obj = UtilLabelMe()

@cli.command("search")
@click.pass_context
@click.argument("category")
@click.option("-p", "--path", help="Path to the 'All-Dataset' folder")
@click.option("-h", "--hide", is_flag=True, show_default=True, default=False, help="Hide the names of images that contain the label")
def search(ctx, category, path, hide):
    util = ctx.obj
    if path is None:
        (names, count) = util.search_label(category)
    else:
        (names, count) = util.search_label(category, path)
    click.echo(f"Searching for '{category}':")
    if not hide:
        click.echo(click.style("Files", fg="green") + click.style(f": {names}", fg="white"))
    click.echo(click.style("Image count", fg="green") + click.style(f": {len(names)}", fg="white"))
    click.echo(click.style("Label count", fg="green") + click.style(f": {count}", fg="white"))
    click.pause()
@cli.command("listlabels")
@click.pass_context
@click.option("-p", "--path", help="Path to the 'All-Dataset' folder")
def listlabels(ctx, path):
    util = ctx.obj
    if path is None:
        counter = util.check_labels()[0]
    else:
        counter = util.check_labels(path=path)[0]
    for key, value in counter.items():
        click.echo(click.style(f"{key}", fg="green", bold=True) + click.style(f": {value}", fg="white"))
    click.pause()

@cli.command("show")
@click.pass_context
@click.option("-p", "--path", help="Path to the 'All-Dataset' folder")
@click.option("-h", "--hide", is_flag=True, show_default=False, default=True, help="Disable labeling on images")
@click.argument("dataset")
@click.argument("name")
def show(ctx, path, hide, dataset, name):
    util = ctx.obj
    if path is None:
        util.image_processing(dataset, name, labeling=hide)
    else:
        util.image_processing(dataset, name, path=path, labeling=hide)

@cli.command("convert")
@click.pass_context
@click.option("-p", "--path", help="Path to the 'All-Dataset' folder")
@click.argument("dataset")
def show(ctx, path, dataset):
    util = ctx.obj
    if path is None:
        util.convert(dataset)
    else:
        util.convert(dataset, path=path)

@cli.command("alter")
@click.pass_context
@click.option("-p", "--path", help="Path to the 'All-Dataset' folder")
@click.argument("targetlabel")
@click.argument("newname")
def alter(ctx, path, targetlabel, newname):
    util = ctx.obj
    if path is None:
        util.alter_label(targetlabel, newname)
    else:
        util.alter_label(targetlabel, newname, path=path)

def main():
    try:
        cli(prog_name="cli")
    except Exception as e:
        click.echo(e)

if __name__ == '__main__':
    main()
