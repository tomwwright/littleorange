from littleorange_build_sam import sam


def sceptre_handler(sceptre_user_data):
  template = sam.build_sam(sceptre_user_data)
  return template
