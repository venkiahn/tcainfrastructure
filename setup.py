import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="techchallengeapp",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "techchallengeapp"},
    packages=setuptools.find_packages(where="techchallengeapp"),

    install_requires=[
        "aws-cdk.core==1.130.0",
        "aws-cdk.ec2==1.130.0",
        "aws-cdk.ecs==1.130.0",
        "aws-cdk.rds==1.130.0",
        "aws-cdk.elasticloadbalancingv2==1.13.0",
        "aws-cdk.ecr==1.13.0"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
