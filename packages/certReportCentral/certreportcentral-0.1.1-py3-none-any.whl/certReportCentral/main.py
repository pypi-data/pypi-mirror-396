#!/usr/bin/python3
import requests
import json
import argparse
import os
import sqlite3
from pathlib import Path
import time
import re

version = "0.1"

cert_central_api = os.getenv('CERT_CENTRAL_API')

def query_cert_central(payload):
    headers = {"X-API-KEY": cert_central_api}
    response = requests.post("https://certcentral.org/api/process_hash",headers=headers ,json=payload)
    response.raise_for_status()
    response = response.json()
    print(response['message'])

def is_valid_sha256(input_str):
    sha256_regex = re.compile(r'^[a-fA-F0-9]{64}$')
    return bool(sha256_regex.match(input_str))

def create_tag_string(tags):
    if len(tags) == 0:
        return ""
    elif len(tags) == 1:
        return tags[0]
    else:
        tag_string = ", ".join(tags[:-1])
        tag_string += " and " + tags[-1]
        return tag_string

def query_malwarebazaar(filehash):
    query = {"query": "post-data", "query": "get_info", "hash": filehash}
    data_request = requests.post("https://mb-api.abuse.ch/api/v1/", data=query)
    data_request.raise_for_status()
    json_string = data_request.text
    json_python_value = json.loads(json_string)
    return json_python_value

def query_virustotal(filehash):
    try:
        api_key = os.getenv('VT_API_KEY')
        if api_key == None:
            raise KeyError
    except KeyError:
        print('''Please set your VirusTotal API key by running the doing the following:
        On Linux:
        echo "VT_API_KEY=your_api_key_here" >> ~/.bashrc
        source ~/.bashrc

        On Windows:
        setx VT_API_KEY "your_api_key"

        On MacOS:
        echo "export VT_API_KEY=your_api_key_here" >> ~/.zprofile
        source ~/.zprofile
        ''')
        exit()
    headers = {"accept": "application/json", "x-apikey": api_key}
    item_id = {"id": filehash}
    data_request = requests.get("https://www.virustotal.com/api/v3/files/" + filehash, headers=headers)
    try:
        data_request.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if data_request.status_code == 401:
            print("API request was forbidden. Check to confirm your API key is correct.")
            exit()
        elif data_request.status_code == 404:
            print("The file hash was not found in VirusTotal's database.")
            exit()
        else:
            print("An error occurred while querying VirusTotal: " + str(e))
            exit()
    json_python_value = data_request.json()
    return json_python_value


def process_virustotal_data(json_python_value, filehash, user_supplied_tag):
    try:

        signature_info = json_python_value.get("data", {}).get("attributes", {}).get("signature_info")
        if signature_info:
            signers = json_python_value["data"]["attributes"]["signature_info"]["signers"]
            signer_list = signers.split(";")
            subject_cn = signer_list[0]
            issuer_cn = signer_list[1]
            signer_details = json_python_value["data"]["attributes"]["signature_info"]["signers details"][0]
            cert_status = signer_details["status"]
            serial_number = signer_details["serial number"]
            thumbprint = signer_details["thumbprint"]
            valid_from = signer_details["valid from"]
            valid_to = signer_details["valid to"]
            malware_config = json_python_value.get("data", {}).get("attributes", {}).get("malware_config")
            if malware_config:
                for family in json_python_value["data"]["attributes"]["malware_config"]["families"]:
                    if user_supplied_tag is None:
                        user_supplied_tag = family["family"]
            
            payload = {
                "hash": filehash,
                "subject_cn": subject_cn,
                "issuer_cn": issuer_cn,
                "serial_number": serial_number,
                "thumbprint": thumbprint,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "user_tag": user_supplied_tag,
            }
            return payload
    except KeyError:
        payload = None
        return payload
        print("Certificate is not valid.")
    else:
        payload = None
        return payload
        print("No signature information found in VirusTotal.")
        

def process_malwarebazaar_data(json_python_value, filehash, user_supplied_tag):
    if json_python_value["data"][0]["code_sign"]:
        subject_cn = json_python_value["data"][0]["code_sign"][0]["subject_cn"]
        issuer_cn = json_python_value["data"][0]["code_sign"][0]["issuer_cn"]
        serial_number = json_python_value["data"][0]["code_sign"][0]["serial_number"]
        thumbprint = json_python_value["data"][0]["code_sign"][0]["thumbprint"]
        valid_from = json_python_value["data"][0]["code_sign"][0]["valid_from"]
        valid_until = json_python_value["data"][0]["code_sign"][0]["valid_to"]

        payload = {
            "hash": filehash,
            "subject_cn": subject_cn,
            "issuer_cn": issuer_cn,
            "serial_number": serial_number,
            "thumbprint": thumbprint,
            "valid_from": valid_from,
            "valid_to": valid_until,
            "user_tag": user_supplied_tag,
        }
        return payload
    else:
        payload = None
        print("No signature information found in MalwareBazaar.")
        return payload
        


def main():
    parser = argparse.ArgumentParser(description = "Pull data pertaining to filehash by specifying hash associated with the malware and choosing a provider (defaults to MalwareBazaar).")
    parser.add_argument("-#","--hash", help="Specify hash of file to query.")
    parser.add_argument("-s", "--service", default="malwarebazaar", choices=["MB", "malwarebazaar", "VT", "virustotal"],
                        help="Select the service to query (default: malwarebazaar).")
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('-t', '--tag', help="Tag the malware as a specific family")
    parser.add_argument('-r', '--read', help="Read a list of hashes from a file. Each hash should be on its own line and malware family can be specifiied by adding a tab and the family name after the hash.")
    args = parser.parse_args()

    if not cert_central_api:
                print('''Please set your certCentral API key by running the doing the following:
        On Linux:
        echo "CERT_CENTRAL_API=your_api_key_here" >> ~/.bashrc
        source ~/.bashrc

        On Windows:
        setx CERT_CENTRAL_API "your_api_key"

        On MacOS:
        echo "export CERT_CENTRAL_API=your_api_key_here" >> ~/.zprofile
        source ~/.zprofile
        ''')


    if args.read:
        request_count = 0
        with open(args.read, "r") as f:
            hashes = f.readlines()
        for hash in hashes:

            start_time = time.time()
            if request_count >= 3:
                elapsed_time = time.time() - start_time
                if elapsed_time < 60:
                    time.sleep(60 - elapsed_time)
                request_count = 0
                start_time = time.time()
            hash, tag = hash.strip().split('\t')
            args.hash = hash
            args.tag = tag
            if not is_valid_sha256(args.hash):
                print("The hash is not a valid SHA256 hash: " + args.hash)
                continue

            request_count += 1
            args.hash = hash.strip()
            if args.service == "virustotal" or args.service == "VT":
                json_python_value = query_virustotal(args.hash)
                payload = process_virustotal_data(json_python_value, args.hash, args.tag)
                if payload is None:
                    continue
                query_cert_central(payload)
            else:  # Default to MalwareBazaar
                json_python_value = query_malwarebazaar(args.hash)
                if json_python_value["query_status"] == "hash_not_found":
                    print("The hash was not found in MalwareBazaar's database.")
                    continue
                payload = process_malwarebazaar_data(json_python_value, args.hash, args.tag)
                if payload is None:
                    continue
                query_cert_central(payload)


    elif args.hash:
        if args.service == "virustotal" or args.service == "VT":
            if not is_valid_sha256(args.hash):
                print("The hash is not a valid SHA256 hash.")
                exit()
            json_python_value = query_virustotal(args.hash)
            payload = process_virustotal_data(json_python_value, args.hash, args.tag)
        else:  # Default to MalwareBazaar
            json_python_value = query_malwarebazaar(args.hash)
            if json_python_value["query_status"] == "hash_not_found":
                print("The hash was not found in MalwareBazaar's database.")
                exit()
            payload = process_malwarebazaar_data(json_python_value, args.hash, args.tag)
        query_cert_central(payload)
    elif not args.hash:
         parser.error("the following arguments are required: --hash/-#")

            
if __name__=="__main__":
    main()
