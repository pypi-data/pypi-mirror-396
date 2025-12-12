import setuptools as st

from datetime import datetime

# Setting up
st.setup(
    name="duppla_aws",
    version=f"{datetime.now():%Y.%m.%d.%H.%M}",
    author="duppla",
    author_email="<>",
    description="Custom implementation for the AWS resources",
    long_description_content_type="text/markdown",
    long_description="A custom implementation for AWS resources using boto3 (for our corporate needs)",
    packages=st.find_packages(),
    package_data={"duppla_aws": ["py.typed"]},
    install_requires=[
        "pydantic>=2.7.0,<3.0.0",
        "pydantic_extra_types",
        "boto3>=1.37.4",
        # "types-boto3[full]", should be an aditional (optional) dependency just for the stubs
    ],
    keywords=["python", "aws", "duppla"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
