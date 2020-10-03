import logging
import subprocess


def sceptre_handler(sceptre_user_data):

  logging.basicConfig(format='[%(asctime)s] AWS SAM Template [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  logger = logging.getLogger(__name__)

  logger.info(f"Building AWS SAM Project...")

  if "SAMProject" not in sceptre_user_data:
    raise Exception("SAMProject not provided in Sceptre user data!")

  project = sceptre_user_data["SAMProject"]
  command = f"make Build{project}"

  logger.info(f"Building '{project}' with command '{command}'")

  package_process = subprocess.run(command.split(" "))
  if package_process.returncode != 0:
    raise Exception(f'Command failed with error code {package_process.returncode}')

  with open(f"sceptre/templates/SAM/{project}/template.cfn.yaml", "r") as f:
    return f.read()
