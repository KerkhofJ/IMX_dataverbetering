
from pathlib import Path

from imxCli.revision.process_revision import process_imx_revisions
from imxCli.utils.helpers import clear_directory


def test_process(issue_list: str, imx_12_xml_file: str, output_path: str):
    clear_directory(Path(output_path))

    df = process_imx_revisions(imx_12_xml_file, issue_list, output_path)
    filtered_df = df[df['verbeteren']]
    unique_statuses = filtered_df['status'].unique().tolist()
    assert len(unique_statuses) == 1 and unique_statuses[0] == 'processed', 'should all be processed'
