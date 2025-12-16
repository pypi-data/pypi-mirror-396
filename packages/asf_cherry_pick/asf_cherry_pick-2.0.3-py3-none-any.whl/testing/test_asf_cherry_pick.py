#!/usr/bin/env python3

from pathlib import Path
import asf_cherry_pick.asf_cherry_pick as acp
import asf_search as asf

def read_asf_credential() -> tuple[str, str]:
    credentials = Path(__file__).parent.absolute() / "credentials.txt"
    login, pwd = credentials.read_text().split()
    return login, pwd


safe_name = "S1A_IW_SLC__1SSV_20141006T003957_20141006T004022_002702_00304C_7C77"

def test_catalog_search():
    product = asf.granule_search(safe_name)
    product_dict = product.geojson()
    url = product_dict["features"][0]["properties"]["url"]
    assert url == "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SSV_20141006T003957_20141006T004022_002702_00304C_7C77.zip"

def test_download_manifest():
    url = "https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SSV_20141006T003957_20141006T004022_002702_00304C_7C77.zip"
    test_dir = Path(__file__).parent.absolute()
    p = test_dir.parent / "test_asf"
    try:
        login, passwd = read_asf_credential()
    except FileNotFoundError as e:
        assert False, str(e)
    full_safe_name = safe_name + ".SAFE"
    p.mkdir(parents=True, exist_ok=True)
    asf_picker = acp.AsfCherryPick()
    asf_picker.connect(login, passwd)
    asf_picker.cherry_pick((url, p, "manifest.safe"))
    target = p / full_safe_name / "manifest.safe"
    assert target.exists()
