import os
import os.path
import glob
import re
import hashlib
import shutil
import json

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import Headers
from starlette.staticfiles import (
    StaticFiles as StarletteStaticFiles,
    NotModifiedResponse,
)
from nomad.config.models.plugins import APIEntryPoint
from nomad.config import config


def is_quoted(value: str) -> bool:
    """Returns whether the given string is surrounded by quotes."""
    return len(value) >= 2 and value[0] == '"' and value[-1] == '"'


def generate_config():
    """Generates the config.js contents. Note that the output needs to be sorted to produce stable ETags."""
    from nomad.config import config

    include_filter = {
        'keycloak': {
            'realm_name': '*',
            'client_id': '*',
            'public_server_url': '*',
        },
        'meta': {
            'description': '*',
            'footer_links': '*',
        },
        'services': '*',
        'ui': {'unit_systems': '*', 'north_base': '*'},
        'north': {'enabled': '*'},
        'temporal': {'enabled': '*'},
    }

    def filter_config(data, filter):
        if filter == '*':
            return data
        if not filter:
            return None
        if isinstance(data, dict):
            next = {}
            for key in filter:
                if key in data:
                    next_data = data.get(key)
                    if next_data is not None:
                        next[key] = filter_config(next_data, filter[key])
            return next
        if data == filter:
            return data
        return None

    config_data = filter_config(config.dict(), include_filter)

    # Add a filtered list of unit systems
    unit_systems = []
    for key, value in config.ui.unit_systems.filtered_items():
        unit_system = value.dict()
        unit_system.update({'id': key})
        unit_systems.append(unit_system)
    config_data['ui']['unit_systems'] = {
        'items': unit_systems,
        'selected': config.ui.unit_systems.selected,
    }
    config_js_string = (
        f'window.nomadConfig = {json.dumps(config_data, sort_keys=True)};'
    )

    return config_js_string


def generate_metainfo():
    """Generates the metainfo.js content. Note that the output needs to be sorted to
    produce stable ETags."""
    from nomad.datamodel import all_metainfo_packages

    definition_dict = {}

    # Get all metainfo packages serialized as dict
    env = all_metainfo_packages().m_to_dict(with_meta=True, with_def_id=True)

    def get_definition_id(path: str):
        """Convert '/packages/<package-index>/section_definitions/<section-index>' into
        'metainfo/<package-name>/section_definitions/<index>' This is the format that the
        Graph API response uses.

        TODO: The Graph API format should be updated to use the qualified name +
        definition id
        """
        if path.startswith('/packages/'):
            path_parts = path[1:].split('/', 2)
            package_name = env[path_parts[0]][int(path_parts[1])].get('name')

            if package_name:
                path = f'/{package_name}/{"/".join(path_parts[2:])}'

            return f'metainfo{path}'

        return path

    def minify(definition):
        defcopy = definition.copy()

        # TODO: these are dropped for now, but some may be needed in the GUI.
        defcopy.pop('categories', None)
        defcopy.pop('extends_base_section', None)
        defcopy.pop('attributes', None)
        defcopy.pop('m_def_id', None)
        defcopy.pop('definition_id', None)
        defcopy.pop('m_parent_index', None)
        defcopy.pop('m_parent_sub_section', None)

        # Get valid ids for base sections
        if base_sections := defcopy.get('base_sections'):
            defcopy['base_sections'] = [
                get_definition_id(path) for path in base_sections
            ]

        # Get valid ids for sub sections
        if sub_section := defcopy.get('sub_section'):
            defcopy['sub_section'] = get_definition_id(sub_section)

        # Get valid ids's for references
        if type_info := defcopy.get('type'):
            if type_info.get('type_kind') == 'reference':
                type_info['type_data'] = get_definition_id(type_info['type_data'])

        # Minify quantities
        if quantities := defcopy.pop('quantities', None):
            minified_quantities = []
            for quantity in quantities:
                # Skip parser-specific definitions: these should be deprecated
                if quantity['name'].startswith('x_'):
                    continue
                minified_quantities.append(minify(quantity))
            if minified_quantities:
                defcopy['quantities'] = minified_quantities

        # Minify sub sections
        if sub_sections := defcopy.pop('sub_sections', None):
            minified_sub_sections = []
            for sub_section in sub_sections:
                # Skip parser-specific definitions: these should be deprecated
                if sub_section['name'].startswith('x_'):
                    continue
                minified_sub_sections.append(minify(sub_section))
            if minified_sub_sections:
                defcopy['sub_sections'] = minified_sub_sections

        return defcopy

    # Loop through packages
    packages = env.get('packages', [])
    for package in packages:
        package_name = package['name']
        definitions = package.get('section_definitions', [])

        # Loop through all definitions in the package and store a minified version in the
        # definition_dict
        for i_definition, definition in enumerate(definitions):
            # Skip parser-specific definitions: these should be deprecated
            if definition['name'].startswith('x_'):
                continue

            # Minify definition and store under a key based on package name and index.
            # TODO: we should start using a more stable identitifer here.
            minified = minify(definition)
            definition_dict[
                f'metainfo/{package_name}/section_definitions/{i_definition}'
            ] = minified

    return f'window.nomadMetainfo = {json.dumps(definition_dict, sort_keys=True)};'


class GUIAPIEntryPoint(APIEntryPoint):
    def load(self):
        config_js_string = generate_config()
        metainfo_string = generate_metainfo()
        config_etag = hashlib.md5(
            config_js_string.encode(), usedforsecurity=False
        ).hexdigest()
        metainfo_etag = hashlib.md5(
            metainfo_string.encode(), usedforsecurity=False
        ).hexdigest()

        class GUIFiles(StarletteStaticFiles):
            etag_re = r'^(W/)?"?([^"]*)"?$'

            def is_not_modified(
                self, response_headers: Headers, request_headers: Headers
            ) -> bool:
                try:
                    if_none_match = request_headers['if-none-match']
                    match = re.match(self.etag_re, if_none_match)
                    if match:
                        if_none_match = match.group(2)
                    etag = response_headers['etag']

                    if is_quoted(etag):
                        etag = etag[1:-1]

                    if if_none_match == etag:
                        return True
                except KeyError:
                    pass

                return super().is_not_modified(response_headers, request_headers)

            async def get_response(self, path: str, scope):
                """This method is called when serving dynamically created files."""
                if path == 'metainfo.js':
                    response = PlainTextResponse(
                        metainfo_string,
                        media_type='application/javascript',
                        headers={'etag': metainfo_etag},
                    )
                elif path == 'config.js':
                    response = PlainTextResponse(
                        config_js_string,
                        media_type='application/javascript',
                        headers={'etag': config_etag},
                    )
                else:
                    response = await super().get_response(path, scope)

                request_headers = Headers(scope=scope)
                if self.is_not_modified(response.headers, request_headers):
                    return NotModifiedResponse(response.headers)

                return response

        root_path = f'{config.services.api_base_path}/{self.prefix}'

        # Create a copy of the static gui build that has the default base path replaced
        # with the configured base path
        static_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'static')
        )

        run_gui_folder = os.path.join(config.fs.working_directory, 'run', 'gui')
        if not os.path.exists(run_gui_folder):
            os.makedirs(run_gui_folder)

        shutil.rmtree(run_gui_folder, ignore_errors=True)
        shutil.copytree(static_folder, run_gui_folder, dirs_exist_ok=True)

        source_file_globs = [
            '**/*.json',
            '**/*.html',
            '**/*.js',
            '**/*.js.map',
            '**/*.css',
        ]
        for source_file_glob in source_file_globs:
            source_files = glob.glob(
                os.path.join(run_gui_folder, source_file_glob), recursive=True
            )
            for source_file in source_files:
                with open(source_file, 'rt') as f:
                    file_data = f.read()
                file_data = file_data.replace('/prefix-to-replace', root_path)
                with open(source_file, 'wt') as f:
                    f.write(file_data)

        # Create the app and mount the static files
        app = FastAPI(
            root_path=root_path, title=self.name, description=self.description
        )
        app.mount('/', GUIFiles(directory=run_gui_folder), name='static')

        # Return the index.html for all routes that do not match a file to make the react
        # SPA work
        @app.exception_handler(404)
        async def custom_404_handler(_, __):
            return FileResponse(os.path.join(run_gui_folder, 'index.html'))

        @app.middleware('http')
        async def add_header(request: Request, call_next):
            """This middleware adds Cache-Control headers and ensures that the proper
            Etags are set. Note that the etags that starlette produces do not follow the
            RFC, because they are not wrapped in double quotes as the RFC specifies. Nginx
            considers them weak etags and will strip these if gzip is enabled. For more
            info see: https://github.com/Kludex/starlette/issues/2298
            """
            response = await call_next(request)
            path = request.scope['path']

            # Ensure etag is quoted
            etag = response.headers.get('etag')
            if etag and not is_quoted(etag):
                etag = f'"{etag}"'
                response.headers['etag'] = etag

            # 1. HTML code are always revalidated. This ensures that the user always gets
            # the latest version of the GUI
            if path.endswith('.html') or path == '/':
                response.headers['Cache-Control'] = 'no-cache, must-revalidate'
            # 2. Dynamically generated files are cached for 1 week. TODO: for some reason
            # the ETags change and we need to use time-based caching. Ideally these files
            # would only use ETag-based caching.
            elif etag == f'"{config_etag}"' or etag == f'"{metainfo_etag}"':
                response.headers['Cache-Control'] = (
                    f'max-age={60 * 60 * 24 * 7}, must-revalidate'
                )
            # 3. All other static assets are cached aggressively: react production builds
            # include a hash in the filename, and thus the same version can be cached
            # forever without revalidation.
            else:
                response.headers['Cache-Control'] = (
                    f'max-age={60 * 60 * 24 * 365}, immutable'
                )

            return response

        # Allow the GUI to be used from any origin
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        return app


gui_api = GUIAPIEntryPoint(
    name='The NOMAD GUI',
    description='The NOMAD graphical user interface. This API serves the static files from the production build of the GUI.',
    prefix='gui/v2',
)
