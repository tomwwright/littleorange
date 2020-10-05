import logging
import subprocess


def sceptre_handler(sceptre_user_data):

  formatter = logging.Formatter("[%(asctime)s] AWS SAM Template [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.getLogger(__name__)
  logger.handlers = [handler]
  logger.setLevel(logging.INFO)

  logger.info(f"Building AWS SAM Project...")

  if "SAMProject" not in sceptre_user_data:
    raise Exception("SAMProject not provided in Sceptre user data!")

  project = sceptre_user_data["SAMProject"]
  command = f"make Build{project}"

  logger.info(f"Building '{project}' with command '{command}'")

  try:
    process = subprocess.run(command, capture_output=True, shell=True, text=True)
    if process.returncode != 0:
      raise Exception(f'Command failed with error code {process.returncode}')

    with open(f"sceptre/templates/SAM/{project}/template.cfn.yaml", "r") as f:
      return f.read()
  except Exception as e:
    logger.error("Error occurred during AWS SAM build", exc_info=e)
    if process:
      logger.error(f"Process standard output stream:\n{process.stdout}")
      logger.error(f"Process standard error stream:\n{process.stderr}")
