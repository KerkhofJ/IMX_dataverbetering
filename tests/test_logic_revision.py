from imxTools.revision.process_revision import process_imx_revisions
from imxTools.revision.revision_enums import RevisionColumns


def test_process(issue_list: str, imx_12_xml_file: str, clean_output_path: str):
    df = process_imx_revisions(imx_12_xml_file, issue_list, clean_output_path)
    filtered_df = df[df[RevisionColumns.ProcessingStatus.name]]
    unique_statuses = filtered_df["status"].unique().tolist()
    assert len(unique_statuses) == 1 and unique_statuses[0] == "processed", (
        "should all be processed"
    )
