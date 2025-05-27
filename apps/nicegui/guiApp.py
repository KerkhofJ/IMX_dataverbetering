import zipfile
import shutil
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from fastapi.responses import FileResponse
from nicegui import native, ui, events, run, app, context

from imxInsights import __version__ as insights_version
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum
from imxTools.insights.diff_and_population import write_diff_output_files, write_population_output_files

client_states = {}

def zip_output_folder(output_path: Path, destination_dir: Path | None = None) -> Path:
    if destination_dir is None:
        destination_dir = output_path.parent
    zip_name = f'{output_path.name}.zip'
    zip_path = destination_dir / zip_name
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in output_path.rglob('*'):
            if file.is_file():
                zipf.write(file, file.relative_to(output_path))
    return zip_path

def find_situations_in_xml(xml_file_path: Path) -> list[str]:
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        found_situations = []
        for enum_name in ImxSituationEnum.__members__:
            if root.find(f".//{{*}}{enum_name}") is not None:
                found_situations.append(enum_name)
        return found_situations
    except Exception as e:
        print(f"⚠️ Error parsing XML: {e}")
        return []

def handle_upload(e, label, situation_element, state):
    client_id = context.client.id
    base_dir = Path(f'temp_uploads/{client_id}')
    base_dir.mkdir(parents=True, exist_ok=True)

    save_path = base_dir / f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{e.name}'
    with open(save_path, 'wb') as f:
        f.write(e.content.read())

    state['uploaded_files'][label] = save_path
    state['file_extensions'][label] = save_path.suffix.lower()
    state['temp_files'].append(str(save_path))

    if state['file_extensions'][label] == '.xml':
        situations = find_situations_in_xml(save_path)
        if situations:
            situation_element.options = situations
            situation_element.props(remove='disable')
            if len(situations) == 1:
                situation_element.value = situations[0]
                ui.notify(f'🧠 Auto-detected situation: {situations[0]}', type='info')
            else:
                situation_element.value = ''
                ui.notify(f'🧠 Multiple situations found: {", ".join(situations)}', type='info')
        else:
            situation_element.options = []
            situation_element.value = ''
            situation_element.props(remove='disable')
            ui.notify('❓ No known situation elements found in XML.', type='warning')
    else:
        situation_element.options = []
        situation_element.value = ''
        situation_element.props('disable')

    ui.notify(f'📁 {label.upper()} uploaded: {save_path.name} 🎉', type='info')


def reset_situation(label: str, situation_element, state):
    state['uploaded_files'].pop(label, None)
    state['file_extensions'][label] = None
    situation_element.value = ''
    situation_element.props('disable')
    ui.notify(f'🗑️ {label.upper()} file removed. Situation reset.', type='warning')

def get_situation_enum(value: str | None):
    return ImxSituationEnum(value) if value else None

@app.on_startup
def setup_dark_mode():
    dark_mode = ui.dark_mode()
    dark_mode.enable()
    def toggle_dark_light():
        dark_mode.toggle()
        toggle_button.text = '🔦 Flashbang Mode' if dark_mode.value else '🌙 Dark Mode'
    global toggle_button
    toggle_button = ui.button(
        '🔦 Flashbang Mode' if dark_mode.value else '🌙 Dark Mode',
        color=None,
        on_click=toggle_dark_light
    ).classes('absolute top-4 right-4 border-0 outline-none ring-0 shadow-none')

@app.on_disconnect
def cleanup_user_temp_files():
    client_id = context.client.id
    state = client_states.pop(client_id, None)
    base_dirs = [
        Path(f'temp_uploads/{client_id}'),
        Path(f'output_population/{client_id}'),
        Path(f'work/{client_id}'),
        Path(f'zips/{client_id}')
    ]
    if state:
        for tab_state in state.values():
            for path_str in tab_state.get('temp_files', []):
                try:
                    path = Path(path_str)
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    elif path.is_file():
                        path.unlink(missing_ok=True)
                except Exception as e:
                    print(f'⚠️ Error deleting {path_str}: {e}')
    for folder in base_dirs:
        try:
            shutil.rmtree(folder, ignore_errors=True)
        except Exception as e:
            print(f'⚠️ Error deleting folder {folder}: {e}')

@app.on_shutdown
def cleanup_temp_files():
    print("🧹 Global cleanup on shutdown...")
    try:
        shutil.rmtree('temp_uploads', ignore_errors=True)
        shutil.rmtree('output_diff', ignore_errors=True)
        shutil.rmtree('output_population', ignore_errors=True)
        shutil.rmtree('work', ignore_errors=True)
        shutil.rmtree('zips', ignore_errors=True)
        for zip_file in Path('.').glob('*.zip'):
            zip_file.unlink()
    except Exception as e:
        print(f'Error cleaning up files: {e}')

@ui.page('/')
def main_page():
    client_id = context.client.id
    if client_id not in client_states:
        client_states[client_id] = {}

    def init_tab_state(tab_key: str):
        if tab_key not in client_states[client_id]:
            client_states[client_id][tab_key] = {
                'uploaded_files': {},
                'file_extensions': {},
                'temp_files': []
            }
        return client_states[client_id][tab_key]

    with ui.dialog() as spinner_dialog, ui.card().classes('p-8 items-center'):
        ui.spinner(size='lg').props('color=primary')
        ui.label('⏳ Processing, please wait... 🛠️').classes('mt-4')

    with ui.column().classes('items-center justify-center mt-6 w-full'):
        ui.label('IMX comparison').classes('text-3xl font-bold')

    with ui.tabs() as tabs:
        diff_tab = ui.tab('🔍 Diff')
        pop_tab = ui.tab('📊 Population')

    with ui.tab_panels(tabs, value=diff_tab).classes('w-full h-screen overflow-hidden'):
        with ui.tab_panel(diff_tab):
            state = init_tab_state('diff')
            ui.markdown('''### 🔍 Compare IMX Containers and generate a diff report.''')
            upload_t1 = ui.upload(label='📤 Upload T1 IMX or ZIP', auto_upload=True, on_upload=lambda e: handle_upload(e, 't1', t1_situation, state)).classes('w-full')
            t1_situation = ui.select(list(ImxSituationEnum.__members__), label='🧾 T1 Situation').props('disable').classes('w-full')
            upload_t1.on('removed', lambda e: reset_situation('t1', t1_situation, state))
            upload_t2 = ui.upload(label='📤 Upload T2 IMX or ZIP', auto_upload=True, on_upload=lambda e: handle_upload(e, 't2', t2_situation, state)).classes('w-full')
            t2_situation = ui.select(list(ImxSituationEnum.__members__), label='🧾 T2 Situation').props('disable').classes('w-full')
            upload_t2.on('removed', lambda e: reset_situation('t2', t2_situation, state))

            with ui.row():
                geojson = ui.checkbox('🗺️ Generate GeoJSON')
                to_wgs = ui.checkbox('🌐 Use WGS84 (EPSG:4326)').bind_visibility_from(geojson, 'value')
            version_checkbox = ui.checkbox('🆚 Compare across IMX versions', value=False)

            async def run_diff():
                if 't1' not in state['uploaded_files'] or 't2' not in state['uploaded_files']:
                    ui.notify('⚠️ Both T1 and T2 files must be uploaded!', type='negative')
                    return
                errors = []
                if state['file_extensions'].get('t1') == '.xml' and not t1_situation.value:
                    errors.append('T1 situation must be selected for XML files.')
                if state['file_extensions'].get('t2') == '.xml' and not t2_situation.value:
                    errors.append('T2 situation must be selected for XML files.')
                if errors:
                    for err in errors:
                        ui.notify(f'⚠️ {err}', type='negative')
                    return
                spinner_dialog.open()
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_dir = Path(f'work/{client_id}/diff_{timestamp}')
                    zip_dir = Path(f'zips/{client_id}')
                    base_dir.mkdir(parents=True, exist_ok=True)
                    zip_dir.mkdir(parents=True, exist_ok=True)
                    await run.cpu_bound(
                        write_diff_output_files,
                        state['uploaded_files']['t1'],
                        state['uploaded_files']['t2'],
                        base_dir,
                        get_situation_enum(t1_situation.value),
                        get_situation_enum(t2_situation.value),
                        geojson.value,
                        to_wgs.value,
                        version_checkbox.value,
                    )
                    zip_path = zip_output_folder(base_dir, zip_dir)
                    state['temp_files'].extend([str(zip_path), str(base_dir)])
                    ui.download(zip_path)
                    ui.notify('✅ Diff completed! Downloading ZIP... 📦', type='positive')
                except Exception as e:
                    ui.notify(f'💥 Error during diff: {e}', type='negative')
                finally:
                    spinner_dialog.close()

            ui.button('🧪 Create and download diff report', on_click=run_diff).classes('mt-4 w-full')

        with ui.tab_panel(pop_tab):
            state = init_tab_state('population')
            ui.markdown('''### 📊 Generate a population report from a IMX container.''')
            imx_situation = ui.select([], label='📋 IMX Situation').classes('w-full')
            ui.upload(label='📤 Upload IMX or ZIP', on_upload=lambda e: handle_upload(e, 'imx', imx_situation, state)).classes('w-full')

            with ui.row():
                geojson_p = ui.checkbox('🗺️ Generate GeoJSON')
                to_wgs_p = ui.checkbox('🌐 Use WGS84 (EPSG:4326)').bind_visibility_from(geojson_p, 'value')

            async def run_population():
                if 'imx' not in state['uploaded_files']:
                    ui.notify('⚠️ IMX file must be uploaded!', type='negative')
                    return
                if state['file_extensions'].get('imx') == '.xml' and not imx_situation.value:
                    ui.notify('⚠️ Situation must be selected for XML files!', type='negative')
                    return
                spinner_dialog.open()
                try:
                    output_path = Path(f'output_population/{client_id}')
                    output_path.mkdir(parents=True, exist_ok=True)
                    await run.cpu_bound(
                        write_population_output_files,
                        state['uploaded_files']['imx'],
                        output_path,
                        get_situation_enum(imx_situation.value),
                        geojson_p.value,
                        to_wgs_p.value,
                    )
                    zip_path = zip_output_folder(output_path)
                    state['temp_files'].extend([str(zip_path), str(output_path)])
                    ui.download(zip_path)
                    ui.notify('✅ Population report completed! Downloading ZIP... 📦', type='positive')
                except Exception as e:
                    ui.notify(f'💥 Error during population: {e}', type='negative')
                finally:
                    spinner_dialog.close()

            ui.button('🧪 Create and download population report', on_click=run_population).classes('mt-4 w-full')

    with ui.column().classes('items-center justify-center mt-6 w-full'):
        ui.label(f'⚙️ Powered by ImxInsights 🚀v{insights_version}').classes('text-1xl font-bold')
        ui.link('🌐 Visit on PyPI', target='https://pypi.org/project/imxInsights/').classes('text-1xl font-bold text-blue-500 underline')

ui.run(reload=True, port=native.find_open_port(), title="🚆 IMX Diff GUI", dark=True, fastapi_docs=True)
