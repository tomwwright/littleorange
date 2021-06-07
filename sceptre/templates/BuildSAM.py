
"""
1.1.3 AWS SAM Build Integration Library

This script expects to be called from `template_path` of a Sceptre Stack Config.
It invokes the AWS SAM integration library to build the project and return the resulting template.
"""

from littleorange_build_sam import sam

def sceptre_handler(sceptre_user_data):
  template = sam.build_sam(sceptre_user_data)
  return template
