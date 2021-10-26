import json
import hashlib
import os
import sys
import shutil
from typing import Callable, Optional, TypedDict
from zipfile import ZipFile

from pass_dict import pass_dict


PK_PASS_NAME = "Generic"
OPENSSL_APP = "openssl"

SUPPORTED_ASSET_FILES = [
    "icon.png",
    "icon@2x.png",
    "background.png",
    "background@2x.png",
    "logo.png",
    "logo@2x.png",
    "footer.png",
    "footer@2x.png",
    "strip.png",
    "strip@2x.png",
    "thumbnail.png",
    "thumbnail@2x.png",
]


def with_clean_up(func: Callable):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)
        finally:
            generated_files = [
                "pass.json",
                "manifest.json",
                "passcertificate.pem",
                "passkey.pem",
                "signature",
            ]

            for asset_file in SUPPORTED_ASSET_FILES + generated_files:
                if os.path.exists(asset_file):
                    os.remove(asset_file)
    return wrapper


@with_clean_up
def main():
    arguments = parse_arguments()

    pass_type_identifier = arguments["pass_type_identifier"]
    if pass_type_identifier is "":
        raise Exception("pass type identifier is empty")

    team_identifier = arguments["team_identifier"]
    if team_identifier is "":
        raise Exception("team identifier is empty")

    pass_dict_copy = create_pass_dict(
        pass_type_identifier=pass_type_identifier,
        team_identifier=team_identifier,
    )
    pass_dict_json = json.dumps(pass_dict_copy, indent=2)
    with open("pass.json", "w") as f:
        f.write(pass_dict_json)

    create_manifest_json(asset_path=f"{PK_PASS_NAME}.pass")

    certificate_password = arguments["certificate_password"]
    certificate_path = arguments["certificate_path"]

    #  Create pass certificate
    os_code = os.system(f"{OPENSSL_APP} pkcs12 -in {certificate_path} -clcerts -nokeys -out passcertificate.pem -passin pass:{certificate_password}")
    if os_code != 0:
        raise Exception("could not create pass certificate")

    key_password = arguments["key_password"]
    # Create pass key
    os_code = os.system(f"{OPENSSL_APP} pkcs12 -in {certificate_path} -nocerts -out passkey.pem -passin pass:{certificate_password} -passout pass:{key_password}")
    if os_code != 0:
        raise Exception("could not create pass key")

    wwdr_path = arguments["wwdr_path"]
    # Create signature
    os_code = os.system(f"{OPENSSL_APP} smime -binary -sign -certfile {wwdr_path} -signer passcertificate.pem -inkey passkey.pem -in manifest.json -out signature -outform DER -passin pass:{key_password}")
    if os_code != 0:
        raise Exception("could not create signature")

    asset_files_to_delete = [
        "passkey.pem",
        "passcertificate.pem",
        "signature",
        "pass.json",
    ]
    asset_files = [
        "signature",
        "pass.json",
        "manifest.json",
    ]

    for (_, _, filenames) in os.walk(f"{PK_PASS_NAME}.pass"):
        for filename in filenames:
            if filename in SUPPORTED_ASSET_FILES:
                shutil.copy2(f"{PK_PASS_NAME}.pass/{filename}", filename)
                asset_files_to_delete.append(filename)
                asset_files.append(filename)

    with ZipFile(f"{PK_PASS_NAME}.pkpass", "w") as zip_file:
        for asset_file in asset_files:
            zip_file.write(asset_file)

    os_code = os.system(f"open {PK_PASS_NAME}.pkpass")
    if os_code != 0:
        raise Exception("could not open pkpass")


class Arguments(TypedDict):
    certificate_password: str
    key_password: str
    pass_type_identifier: str
    team_identifier: str
    certificate_path: str
    wwdr_path: str

def parse_arguments() -> "Arguments":
    certificate_password: Optional[str] = None
    key_password: Optional[str] = None
    pass_type_identifier: Optional[str] = None
    team_identifier: Optional[str] = None
    certificate_path: Optional[str] = None
    wwdr_path: Optional[str] = None

    skip_next_value = False
    for index, arg in enumerate(sys.argv[1:]):
        if skip_next_value:
            skip_next_value = False
            continue

        next_value_is_getable = index + 1 < len(sys.argv[index:])
        next_value_index = index + 2
        match arg:
            case "--certificate-password":
                if next_value_is_getable:
                    certificate_password = sys.argv[next_value_index]
                    skip_next_value = True
            case "--pass-key-password":
                if next_value_is_getable:
                    key_password = sys.argv[next_value_index]
                    skip_next_value = True
            case "--pass-type-identifier":
                if next_value_is_getable:
                    pass_type_identifier = sys.argv[next_value_index]
                    skip_next_value = True
            case "--team-identifier":
                if next_value_is_getable:
                    team_identifier = sys.argv[next_value_index]
                    skip_next_value = True
            case "--certificate-path":
                if next_value_is_getable:
                    certificate_path = sys.argv[next_value_index]
                    skip_next_value = True
            case "--wwdr-path":
                if next_value_is_getable:
                    wwdr_path = sys.argv[next_value_index]
                    skip_next_value = True

    if certificate_password is None:
        certificate_password = input("what is the password of the provided certificate?\n")

    if key_password is None:
        key_password = input("provide a password for your passkey.pem\n")

    if pass_type_identifier is None:
        pass_type_identifier = input("provide a pass type identifier\n")

    if team_identifier is None:
        team_identifier = input("provide a team identifier\n")

    if certificate_path is None:
        certificate_path = input("provide the path to your certificate\n")

    if wwdr_path is None:
        wwdr_path = input("provide the path to your WWDR certificate\n")

    return {
        "certificate_password": certificate_password,
        "key_password": key_password,
        "pass_type_identifier": pass_type_identifier,
        "team_identifier": team_identifier,
        "certificate_path": certificate_path,
        "wwdr_path": wwdr_path,
    }


def create_manifest_json(asset_path: str):
    with open("pass.json", "r") as f:
        pass_json = f.read()

    hashed_pass_json = hashlib.sha1(pass_json.encode('utf-8')).hexdigest()

    manifest_dict = {"pass.json": hashed_pass_json}

    for (_, _, filenames) in os.walk(asset_path):
        for filename in filenames:
            if filename in SUPPORTED_ASSET_FILES:
                manifest_dict[filename] = hashlib.sha1(
                    open(f"{asset_path}/{filename}", "rb").read()
                ).hexdigest()

    with open(f"manifest.json", "w") as f:
        f.write(json.dumps(manifest_dict, indent=4))


def create_pass_dict(pass_type_identifier: str, team_identifier: str):
    pass_dict_copy = pass_dict.copy()
    pass_dict_copy["passTypeIdentifier"] = pass_type_identifier
    pass_dict_copy["teamIdentifier"] = team_identifier
    return pass_dict_copy


main()
