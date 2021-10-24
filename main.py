import json

from pass_dict import pass_dict

CERTIFICATE_PASSWORD = "password"
KEY_PASSWORD = "password"
WWDR_PATH = "Apple Worldwide Developer Relations Certification Authority.pem"
CERTIFICATE_PATH = "certificates.p12"
PASS_TYPE_IDENTIFIER = "com.apple.application-password"
TEAM_IDENTIFIER = "2V9Z6R8X2R"
PK_PASS_NAME = "Generic"


def main():
    pass_dict_copy = create_pass_dict(
        pass_type_identifier=PASS_TYPE_IDENTIFIER,
        team_identifier=TEAM_IDENTIFIER,
    )
    pass_dict_json = json.dumps(pass_dict_copy, indent=4)
    with open(f"{PK_PASS_NAME}.pass/pass.json", "w") as f:
        f.write(pass_dict_json)

    print(pass_dict_json)


    create_manifest_json(asset_path=f"{PK_PASS_NAME}.pass")

def create_manifest_json(asset_path: str):
    pass

def create_pass_dict(pass_type_identifier: str, team_identifier: str):
    pass_dict_copy = pass_dict.copy()
    pass_dict_copy["passTypeIdentifier"] = pass_type_identifier
    pass_dict_copy["teamIdentifier"] = team_identifier
    return pass_dict_copy


main()
