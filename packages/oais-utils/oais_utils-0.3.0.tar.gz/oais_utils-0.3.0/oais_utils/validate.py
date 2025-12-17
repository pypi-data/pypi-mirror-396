import json
import logging
import os
from zlib import adler32

import bagit
import jsonschema
from fs import open_fs

import oais_utils


def check_folder_exists(path):
    """
    Check if the provided path resolves to a folder
    """
    logging.info(f"Verifying if folder {path} exists.")
    if not os.path.exists(path):
        raise Exception(f"Directory {path} does not exist.")
    return True


def validate_bagit(path, is_dry=False):
    """
    Run BagIt validation against the provided folder.
    If dry_run is set, the bag is considered a "lightweight" one i.e.
    file missing errors won't fail the validation
    """

    bag = bagit.Bag(path)
    try:
        bag.validate()
    except bagit.BagValidationError as e:
        for d in e.details:
            if isinstance(d, bagit.FileMissing):
                # If FileisMissing error occurs and is a dry run file, then return True
                if not is_dry:
                    raise Exception(
                        "%s exists in manifest but was not found on filesystem"
                    ) % (d.path)
                else:
                    return True
    except Exception as e:
        raise Exception(f"Bag validation error: {str(e)}")
    return True


def verify_directory_structure(path, dirlist):
    """
    Given a list of relative paths, check if they exist in the given folder
    """
    logging.info("Verifying directory structure")
    for directory in dirlist:
        dir_path = os.path.join(path, directory)
        logging.info(f"Checking if {dir_path} exists")
        if not os.path.exists(dir_path):
            raise Exception(f"Directory {dir_path} does not exist.")
        else:
            logging.info("\tSuccessful")
            return True


def validate_sip_manifest(sip_json, schema="v1"):
    """
    Validate the sip_json against the JSON schema with the given name
    """
    logging.info("Validating sip.json")

    # JSON schema against which we validate our instance
    json_schema = oais_utils.schemas()[schema]

    # Validates the sip JSON against the schema
    try:
        jsonschema.validate(instance=sip_json, schema=json_schema)

        logging.info(f"\tValidated successfully against the {schema}")
        return True

    except Exception as e:
        logging.info(f"Sip validation failed: {str(e)}")


def validate_contents(path, sip_json={}):
    """
    Validates if the files mentioned in the SIP manifest exist in the contents folder.
    If sip JSON is not provided, then it is retrieved using the get_manifest function.
    """
    logging.info("Validate contents folder")

    if sip_json == {}:
        sip_json = get_manifest(path)

    is_dry = sip_json["audit"][0]["tool"]["params"]["dry_run"]

    if not is_dry:
        try:
            content_files = sip_json["contentFiles"]
            for file in content_files:
                bagpath = file["bagpath"]
                downloaded = file["downloaded"]
                if downloaded:
                    full_bagpath = os.path.join(path, bagpath)
                    if os.path.exists(full_bagpath):
                        logging.info(f"\tFile in path: {bagpath} exists")
                    else:
                        raise Exception(f"File in path: {bagpath} does not exist")
            return True
        except Exception as e:
            raise Exception(f"Error with the contentFiles: {str(e)}")
    else:
        logging.info("This is a dry_run bag. Searching for fetch.txt...")
        # Check if fetch.txt is actually there
        if os.path.isfile(os.path.join(path, "fetch.txt")):
            logging.info("\tSuccessful")
        else:
            raise Exception(f"\tfetch.txt was not found inside {path}")
        return True


def get_manifest(path, sip_manifest_path="data/meta/sip.json"):
    """
    Retrieve the SIP manifest and read it as JSON
    from the provided path
    """
    logging.info("Retrieving Sip.json...")
    sip_location = os.path.join(path, sip_manifest_path)
    try:
        with open(sip_location) as json_file:
            sip_json = json.load(json_file)
            return sip_json
    except Exception as e:
        logging.warning(f"Get manifest exception: {str(e)}")


# Validate data according to SIP specification
def validate_sip(path, schema="v1", logginglevel=50):
    """
    Validate the provided folder as a CERN SIP:
    - Checks the directory structure
    - Validate the sip.json (manifest file) against the JSON schema
    - Validate the SIP folder as a BagIt
    - Checks if every file mentioned in the manifest is provided
    """
    logging.basicConfig(level=logginglevel, format="%(message)s")

    # Expected directory structure of the SIP
    dirlist = ["data", "data/content", "data/meta"]

    try:
        check_folder_exists(path)

        # Check directory structure
        verify_directory_structure(path, dirlist)

        # Gets the sip.json from the content/meta folder
        sip_json = get_manifest(path)

        # Check if provided sip.json validates against the schema
        validate_sip_manifest(sip_json, schema)

        # Check if the SIP package is a "lightweight" one,
        # (no content files included)
        is_dry = sip_json["audit"][0]["tool"]["params"]["dry_run"]

        # Check if the SIP is a valid BagIt
        validate_bagit(path, is_dry)

        # Check if every file mentioned in the manifest is there
        validate_contents(path, sip_json)

        return True

    except Exception as e:
        logging.error(f"Validation failed with error: {str(e)}")

        return False


def _adler32sum(filepath):
    """
    Compute adler32 of given file
    """
    BLOCKSIZE = 256 * 1024 * 1024
    asum = 1
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BLOCKSIZE)
            if not data:
                break
            asum = adler32(data, asum)
    return hex(asum)[2:10].zfill(8).lower()


def compute_hash(filename, alg="md5"):
    """
    Compute hash of a given file
    """
    if alg == "adler32":
        computedhash = _adler32sum(filename)
    else:
        my_fs = open_fs("/")
        computedhash = my_fs.hash(filename, alg)

    return computedhash
