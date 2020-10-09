import setuptools

setuptools.setup(
    name='littleorange-build-sam',
    version='0.1',
    description='Provides Python modules for integrating building SAM projects with Sceptre',
    packages=setuptools.find_packages(),
    entry_points={
        'sceptre.resolvers': [
            'BuildSAM = littleorange_build_sam.resolver:BuildSAM',
        ],
    }
)
