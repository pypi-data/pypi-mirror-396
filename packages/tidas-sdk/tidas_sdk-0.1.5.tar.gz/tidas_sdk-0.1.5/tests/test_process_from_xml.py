from pathlib import Path

from tidas_sdk import TidasProcess, create_process_from_xml


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<processDataSet xmlns="http://lca.jrc.it/ILCD/Process"
                xmlns:common="http://lca.jrc.it/ILCD/Common"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                version="1.1"
                locations="../ILCDLocations.xml"
                xsi:schemaLocation="http://lca.jrc.it/ILCD/Process ../../schemas/ILCD_ProcessDataSet.xsd">
  <processInformation>
    <dataSetInformation>
      <common:UUID>123e4567-e89b-12d3-a456-426614174000</common:UUID>
      <name>
        <baseName xml:lang="en">Sample Process</baseName>
      </name>
    </dataSetInformation>
    <quantitativeReference type="Reference flow(s)">
      <referenceToReferenceFlow>1</referenceToReferenceFlow>
      <functionalUnitOrOther xml:lang="en">1 kg of output</functionalUnitOrOther>
    </quantitativeReference>
  </processInformation>
  <administrativeInformation>
    <dataEntryBy>
      <common:timeStamp>2024-01-01T00:00:00Z</common:timeStamp>
    </dataEntryBy>
    <publicationAndOwnership/>
  </administrativeInformation>
</processDataSet>
"""


def _write_xml(tmp_path: Path) -> Path:
    xml_path = tmp_path / "process.xml"
    xml_path.write_text(SAMPLE_XML, encoding="utf-8")
    return xml_path


def test_tidas_process_from_xml(tmp_path: Path) -> None:
    xml_path = _write_xml(tmp_path)

    process = TidasProcess.from_xml(xml_path)
    dataset = process.to_json()

    info = dataset["processDataSet"]["processInformation"]
    assert info["dataSetInformation"]["common:UUID"] == "123e4567-e89b-12d3-a456-426614174000"
    assert info["dataSetInformation"]["name"]["baseName"][0]["#text"] == "Sample Process"
    assert info["quantitativeReference"]["@type"] == "Reference flow(s)"
    assert info["quantitativeReference"]["functionalUnitOrOther"][0]["#text"] == "1 kg of output"

    xml_output = process.to_xml()
    assert "<processDataSet" in xml_output
    assert "<baseName" in xml_output


def test_factory_create_process_from_xml(tmp_path: Path) -> None:
    xml_path = _write_xml(tmp_path)
    process = create_process_from_xml(xml_path)
    dataset = process.to_json()
    assert dataset["processDataSet"]["processInformation"]["dataSetInformation"]["name"]["baseName"][0]["#text"] == "Sample Process"
