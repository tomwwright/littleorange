import setuptools

setuptools.setup(
    name='littleorange-sceptre-resolvers',
    version='0.1',
    description='Contains Sceptre Custom Resolvers',
    packages=setuptools.find_packages(),
    entry_points={
        'sceptre.resolvers': [
            'Command = littleorange_sceptre_resolvers.command:Command',
            'UploadS3 = littleorange_sceptre_resolvers.upload_s3:UploadS3'
        ],
    }
)
