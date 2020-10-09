import boto3
import logging
from samtranslator.public.translator import ManagedPolicyLoader
from samtranslator.translator.transform import transform
import subprocess
import yaml


def initialise_logger():
  formatter = logging.Formatter("[%(asctime)s] AWS SAM Template [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.getLogger(__name__)
  logger.handlers = [handler]
  logger.setLevel(logging.INFO)

  return logger


def apply_sam_translate(template_string, logger):

  iam = boto3.client("iam")
  template = yaml.load(template_string, Loader=yaml.FullLoader)
  template = transform(template, {}, ManagedPolicyLoader(iam))
  return yaml.dump(template)


def build_project(project, logger):

  command = f"make Build{project}"

  logger.info(f"Building '{project}' with command '{command}'")

  process = subprocess.run(command, capture_output=True, shell=True, text=True)
  if process.returncode != 0:
    logger.error(f"Process standard output stream:\n{process.stdout}")
    logger.error(f"Process standard error stream:\n{process.stderr}")
    raise Exception(f'Command failed with error code {process.returncode}')

  with open(f"sceptre/templates/SAM/{project}/template.cfn.yaml", "r") as f:
    return f.read()


def build_sam(parameters):

  logger = initialise_logger()

  if "SAMProject" not in parameters:
    raise Exception("SAMProject not provided in parameters!")

  logger.info(f"Building AWS SAM Project...")

  project = parameters["SAMProject"]
  applySAMTranslate = parameters.get("ApplySAMTranslate", False)

  try:
    template = build_project(project, logger)
    if applySAMTranslate:
      template = apply_sam_translate(template, logger)
    return template
  except Exception as e:
    logger.error("Error occurred during AWS SAM build", exc_info=e)
