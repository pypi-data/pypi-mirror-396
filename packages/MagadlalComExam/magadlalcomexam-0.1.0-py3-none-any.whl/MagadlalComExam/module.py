
# MagadlalComExam.py

import base64
import gzip
import json
import requests
import platform
import subprocess
import re
import ast

__all__ = ['submit_solution']

#=====================================================================

def __get_mac_address():
  """
  Returns Mac Address(es) of the computer.

  :return: str: The Mac address(es) found, separated by a comma (str).
  :raises: RuntimeError: If the Mac Address cannot be determined.
  """
  try:
    system_name = platform.system()
    if system_name == "Windows":
      command = "getmac"
      pattern = r"[0-9a-fA-F]{2}[-][0-9a-fA-F]{2}[-][0-9a-fA-F]{2}[-][0-9a-fA-F]{2}[-][0-9a-fA-F]{2}[-][0-9a-fA-F]{2}"
    elif system_name in ["Linux", "Darwin"]:  # Linux or macOS
      command = "ifconfig"
      pattern = r"[0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}"
    else:
      raise RuntimeError(f"Unsupported operating system: {system_name}")
    result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
    addr_info = result.stdout
    mac_addresses = re.findall(pattern, addr_info)
    n_mac_addr = len(mac_addresses)
    if n_mac_addr == 0:
      raise RuntimeError("No Mac Address found using system command output.")
    if n_mac_addr > 1:
      return ",".join(mac_addresses)
    else:
      return mac_addresses[0]
  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Error executing command '{command}': {e.stderr.strip()}")
  except FileNotFoundError:
    raise RuntimeError(f"Command '{command}' not found. Please ensure it is installed and in your PATH.")
  except Exception as e:
    raise RuntimeError(f"It could not determine your computer's Mac Address. Details: {e}")

#=====================================================================

def __interface(query=None):
  """
  Send Request and Receive Response

  :param query: dict, query parameters (equivalent to R's list)
  :return: dict, server response that is formatted as JSON object
  :raises: Exception: For HTTP errors or JSON decoding errors.
  """
  if query is None:
    query = {}

  url = "https://www.magadlal.com/exam/python"
  # url = "http://localhost/www/magadlal.com/exam/python"

  query['sender'] = "my-script"
  query['mac'] = __get_mac_address()
  try:
    response = requests.post(
      url=url, 
      data=query
    )
  except requests.exceptions.RequestException as e:
    raise Exception(f"Request failed: {e}")
  if response.status_code != 200:
    raise Exception(f"HTTP status code: {response.status_code}")
  try:
    result = response.json()
  except json.JSONDecodeError:
    raise Exception(response.text)
  return result

#=====================================================================

def __as_gzjson_b64(data):
  json_data = json.dumps(data).encode('utf-8')
  compressed_data = gzip.compress(json_data)
  b64_data = base64.b64encode(compressed_data)
  return b64_data.decode('utf-8')

#=====================================================================

def __exec(code: str):
  tree = ast.parse(code)
  last = tree.body[-1]
  tree.body[-1] = ast.Assign(
    targets=[ast.Name(id="__result__", ctx=ast.Store())],
    value=last.value
  )
  ast.fix_missing_locations(tree)
  scope = {}
  exec(compile(tree, "<string>", "exec"), scope)
  return scope.get("__result__")

#=====================================================================

def submit_solution(uid, expr):
  """
  Check and Submit a Solution.

  :param uid: int, the unique identification number.
  :param expr: str, a multiline Python code string which is a solution.
  :return: str, server response message or an error message.
  """
  try:
    response = __interface(query={"operation": "verify", "uid": uid})
    if response.get("message") != "VERIFIED":
      return response.get("message", "Verification failed with unknown error.")
    result = __exec(expr)
    b64_gz_json = __as_gzjson_b64(result)
    response = __interface(query={
      "operation": "submit",
      "uid": uid,
      "solution": expr,
      "b64_gz_json": b64_gz_json
    })
    return response.get("message")      
  except Exception as e:
    return str(e)
