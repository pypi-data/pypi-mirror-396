import click


@click.command(
    help='Compress folder into a zip file that can be used to create an upload'
)
@click.argument('PATH', nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    '--upload-name',
    help='Optional name for the upload of a single file. Will be ignored on directories.',
)
@click.option(
    '--ignore-path-prefix',
    is_flag=True,
    default=False,
    help='Ignores common path prefixes when creating an upload.',
)
@click.pass_context
def compress_upload(
    ctx,
    path,
    upload_name: str,
    ignore_path_prefix: bool,
):
    import os
    import zipfile

    paths = path
    prefix = os.path.commonprefix(paths)
    print(paths)
    if not os.path.isdir(prefix):
        prefix = os.path.dirname(prefix)
    file_paths = []
    zip_paths = []

    def add_file(file):
        _, ext = os.path.splitext(file)
        if ext in ['.zip', '.tar', 'tgz', 'tar.gz']:
            zip_paths.append(file)
        else:
            file_paths.append(file)

    for file_path in paths:
        if os.path.isfile(file_path):
            add_file(file_path)

        elif os.path.isdir(file_path):
            for dirpath, _, filenames in os.walk(file_path):
                for filename in filenames:
                    add_file(os.path.join(dirpath, filename))

    click.echo(f'create temporary zipfile from {len(file_paths)} files')
    with zipfile.ZipFile(upload_name, 'w') as zip_file:
        for file_path in file_paths:
            if file_path.startswith(prefix) and ignore_path_prefix:
                arcname = file_path[len(prefix) :]
            else:
                arcname = file_path
            zip_file.write(file_path, arcname=arcname)


if __name__ == '__main__':
    compress_upload()
